from collections import defaultdict
import torch
import cv2
import os
import websockets
import asyncio
import json
import requests
from ultralytics import YOLO
import numpy as np
from turn import turn_predict
from light import light_predict
from turn_model import *

base_path = os.path.join(os.getcwd(), "python")
weight_path = os.path.join(base_path, "weight")
# device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = YOLO(os.path.join(weight_path, "yolov8n.pt"))
model.to("cpu")

turn_model = ResNet(ResidualBlock, [3,4,6,3])
# turn_model.load_state_dict(torch.load(os.path.join(weight_path, "turn.pth"), map_location="cpu"))
turn_model.load_state_dict(torch.load(r"C:\third\Project\Real-Time-Detection-of-Traffic-Violation-main\RT_DTV_website\public\python\weight\turn.pth", map_location="cpu"))

turn_model = turn_model.to("cpu")

light_model = YOLO(r"C:\third\Project\Real-Time-Detection-of-Traffic-Violation-main\RT_DTV_website\public\python\weight\light.pt")
# light_model = YOLO(os.path.join(weight_path, "light.pt"))
light_model = light_model.to("cpu")



async def car_track(video_path, output_folder, websocket = None, auto = 1):



    ##################################
    filename = os.path.basename(video_path)[:-4]
    print(filename)
    car_info = defaultdict(dict)
    buffer = []
    #目前檢測到的未離開畫面的車輛
    record_cars = set()
    frame_num = 0
    # 紀錄影片是否播放完畢
    video_finished = 0

    # 資料儲存格式
    # car_info : {
    #     car_id -> {
    #         frame_num -> {
    #             ori_imgs, 
    #             car_imgs, 
    #             bbboxes
    #         }
    #     }
    # }

    # 參數設定
    buffer_size = 16
    check_interval = 30
    ip = "localhost:8080"                    
    #########################

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error reading video file: {video_path}")
        return

    #output_video的width, height, fps設定
    width, height, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    
    output_video_path = output_folder + "/video_output/" + filename + "_output.mp4"
    print(output_video_path)

    video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    while True:
        success, frame = cap.read()
        if success:
            frame_num += 1
            #yoloV8啟動
            results = model.track(frame, persist=True, tracker='bytetrack.yaml', classes = [2,7], verbose=False)
            #要先確認影片中是否有偵測到物件
            if results[0].boxes.id is not None:
                #boxes為這一幀所有bounding box資訊（中心座標以及w,h)的集合
                #track_ids為這一幀所有id的集合
                
                boxes = results[0].boxes.xywh.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()

                #將預測結果寫入影片（就是那些框框）
                annotated_frame = results[0].plot()
                cv2.putText(annotated_frame, str(frame_num), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255))
                video_writer.write(annotated_frame)

                #紀錄目前的車輛
                current_cars = set(track_ids)
                # print(current_cars, buffer)
                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    #計算bounding box左上角及右下角座標以供opencv截圖
                    x1 = int(x - w / 2)
                    y1 = int(y - h / 2)
                    x2 = int(x1 + w)
                    y2 = int(y1 + h)
                    if x1 - 10 > 0:
                        x1 -= 10
                    else:
                        x1 = 0
                    if frame.shape[1] - x2 - 10 > 0:
                        x2 += 10
                    else:
                        x2 = frame.shape[1] - 1
                    
                    roi = frame[y1:y2, x1:x2]
                    roi = cv2.resize(roi, (224, 224))

                    #將boxes和car_imgs中的資料放入car_info
                    car_info[track_id][frame_num] = {
                        "ori_imgs" :frame,  
                        "car_imgs" : roi,
                        "bboxes" : (x,y,w,h)
                    }
                #每10幀偵測一次
                if frame_num%check_interval == 0:
                    disappeared_cars = record_cars - current_cars
                    record_cars = current_cars
                else:
                    disappeared_cars = set()
                #將結束的車輛進入buffer
                if disappeared_cars:
                    for car_id in disappeared_cars:
                        buffer.append(car_id)
        else:
            for car_id in record_cars:
                buffer.append(car_id)
            record_cars.clear()
            video_finished = 1
        if len(buffer) >= buffer_size:
            #執行轉彎判斷及違規判斷
            print("執行轉彎判斷的車輛:", buffer[-buffer_size:])
            turn_info = {key: car_info[key] for key in buffer[-buffer_size:]}
            turn_cars = turn_predict(turn_model, turn_info)
            print("轉彎的車輛", turn_cars)
            if turn_cars:
                light_info = {key: car_info[key] for key in turn_cars}
                light_cars = light_predict(light_model, light_info, output_folder, filename)
                if light_cars :
                    event_data = {
                        "event": "violation_car",
                        "car_id": light_cars,
                        "video_name": filename,
                        "video_path": video_path,
                        "auto": auto  
                    }
                    # 傳送訊息給前端網頁(實時偵測系統)
                    await websocket.send(json.dumps(event_data))
                    # 傳送訊息給PHP後端(get_violation_car_data)
                    response = requests.post(os.path.join(ip,"get_violation_car_data"), json = event_data)
                print("沒有打方向燈的車輛:", light_cars)
            else:
                print("沒有打方向燈的車輛: none")
            print("")
            # 移除buffer
            del buffer[-buffer_size:]

        if len(buffer) == 0 and video_finished == 1:
            break
        elif len(buffer) < buffer_size and video_finished == 1:
            print("執行檢測的車輛:", buffer)
            turn_info = {key: car_info[key] for key in buffer}
            turn_cars = turn_predict(turn_model, turn_info)
            print("轉彎的車輛", turn_cars)
            if turn_cars:
                light_info = {key: car_info[key] for key in turn_cars}
                light_cars = light_predict(light_model, light_info, output_folder, filename)

                if light_cars :
                    event_data = {
                        "event": "violation_car",
                        "car_id": light_cars,
                        "video_name": filename,
                        "video_path": video_path,
                        "auto": auto    
                    }
                    # 傳送訊息給前端網頁(實時偵測系統)
                    await websocket.send(json.dumps(event_data))
                    # 傳送訊息給PHP後端(get_violation_car_data)
                    response = requests.post(f"http://{ip}/get_violation_car_data", json=event_data)# response = requests.post(os.path.join(ip,"get_violation_car_data"), json = event_data)
                print("沒有打方向燈的車輛:", light_cars)
            else:
                print("沒有打方向燈的車輛: none")
            buffer.clear()
            break

    model.predictor.trackers[0].reset()
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()
    print(list(car_info.keys()))
    print(len(car_info))        


