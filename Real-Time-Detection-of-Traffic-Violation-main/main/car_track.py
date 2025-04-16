from collections import defaultdict
import torch
import cv2
import os
from ultralytics import YOLO
import numpy as np
import csv
from turn import turn_predict
from light import light_predict
from turn_model import *

current_dir = os.path.dirname((os.path.abspath(__file__)))
weight = os.path.join(current_dir, "weight")

model = YOLO(os.path.join(weight, "yolov8n.pt"))
model.to('cuda')

turn_model = ResNet(ResidualBlock, [3,4,6,3])
turn_model.load_state_dict(torch.load(os.path.join(weight, "turn.pth"), map_location='cuda:0'))
turn_model = turn_model.to('cuda')


light_model = YOLO(os.path.join(weight, "light.pt"))
light_model = light_model.to('cuda')


def car_track(video_path, output_folder, save, turn):

    ##################################
    filename = os.path.basename(video_path)[:-4]
    print("影片：", filename)
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
    #########################

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error reading video file: {video_path}")
        return

    #output_video的width, height, fps設定
    width, height, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    
    if save[0]:
        output_video_path = os.path.join(output_folder ,f"{filename}_output.webm")
        video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'VP80'), fps, (width, height))


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
                
                if save[0]:
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
            turn_cars = turn_predict(turn_model, turn_info, output_folder, filename, save, turn)
            print("轉彎的車輛", turn_cars)
            light_info = {key: car_info[key] for key in turn_cars}
            light_cars = light_predict(light_model, light_info, output_folder, filename, save)
            print("沒打方向燈的車輛:", light_cars)
            print("")
            for key in buffer[-buffer_size:]:
                if key in car_info:
                    del car_info[key]
            # 移除buffer
            del buffer[-buffer_size:]

        if len(buffer) == 0 and video_finished == 1:
            break
        elif len(buffer) < buffer_size and video_finished == 1:
            print("執行檢測的車輛:", buffer)
            turn_info = {key: car_info[key] for key in buffer}
            turn_cars = turn_predict(turn_model, turn_info, output_folder, filename, save, turn)
            print("轉彎的車輛", turn_cars)
            light_info = {key: car_info[key] for key in turn_cars}
            light_cars = light_predict(light_model, light_info, output_folder, filename, save)
            print("沒打方向燈的車輛:", light_cars)
            for key in buffer:
                if key in car_info:
                    del car_info[key]
            buffer.clear()
            break

    model.predictor.trackers[0].reset()
    cap.release()
    if save[0]:
        video_writer.release()
    cv2.destroyAllWindows()
    #print(list(car_info.keys()))
    #print(len(car_info))        



