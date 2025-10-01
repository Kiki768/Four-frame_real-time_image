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

from model_max import MyModel
import config_max

device = config_max.device

# 當前檔案所在的資料夾
current_dir = os.path.dirname((os.path.abspath(__file__)))
# 設定 "weight" 資料夾的路徑，這個資料夾應該與當前檔案位於同一目錄下
weight = os.path.join(current_dir, "weight")

# weight 儲存在 main/weight/ 資料夾內的 yolov8n.pt
# 載入 YOLO 模型，路徑指向 "weight" 資料夾內的 "yolov8n.pt" 權重檔案
# n 代表 nano，小型、速度最快，適合資源有限的設備。其他還有 s,m,l,x，主要差別在模型的深度與寬度
# model = YOLO(os.path.join(weight, "yolov8n.pt"))
model = YOLO(os.path.join(weight, "yolo11m.pt"))
# 將模型移動到 GPU（如果可用），使用 'cuda' 表示在支持 CUDA 的顯示卡上執行
model.to(device)

# ResNet 是一種深度卷積神經網絡架構，通過引入殘差塊（Residual Block）解決了深層網絡中的梯度消失問題，使得模型可以在更深的結構中進行有效的訓練。
# [3,4,6,3] 代表有四層，每層的殘差塊數量
turn_model = ResNet(ResidualBlock, [3,4,6,3])
turn_model.load_state_dict(torch.load(os.path.join(weight, "turn.pth"), map_location='cuda:0'))
turn_model = turn_model.to(device)


# light_model = YOLO(os.path.join(weight, "light.pt"))
# light_model = light_model.to('cuda')
light_model = YOLO(os.path.join(weight, "yolo_light_train2_best.pt"))
light_model = light_model.to(device)

weight_path = config_max.weight_path
num_layers = config_max.num_layers
classnum = config_max.classnum
nhead = config_max.nhead
dropout_rate = config_max.dropout_rate
transformer_model = MyModel(num_layers, classnum, nhead, dropout_rate)
transformer_model.load_state_dict(torch.load(weight_path))
transformer_model = transformer_model.to(device)


def car_track(video_path, output_folder, save, turn):

    ##################################
    # 取得 video 的名稱，並去除 .mp4 的副檔名
    filename = os.path.basename(video_path)[:-4]
    # print("影片：", filename)
    print("\nvideo: ", filename)
    
    # defaultdict 是 Python 的 collections 模組中的一個類別，它是對標準字典（dict）的擴充。defaultdict 會為每個新鍵提供一個默認值，而不會引發 KeyError 異常。
    # dict 是 defaultdict 的默認工廠函數，這表示如果某個鍵不存在，會自動創建並返回一個新的空字典（{}）
    car_info = defaultdict(dict)
    buffer = []
    # 目前檢測到的未離開畫面的車輛
    # 當使用 set() 初始化時，它會創建一個空的集合
    record_cars = set()
    # 紀錄成功讀取到當前影片的多少個 frame
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

    # 使用 OpenCV 的 VideoCapture 類別來開啟指定路徑的影片檔案
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error reading video file: {video_path}")
        return

    # output_video 的 width, height, fps 設定
    # 跟 input_video 一樣
    width, height, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    
    # --save 的第一個數字，決定是否要儲存 YOLO 的影片
    if save[0]:
        output_video_path = os.path.join(output_folder ,f"{filename}_output.webm")
        video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'VP80'), fps, (width, height))
        # video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    orig_frame_h, orig_frame_w = 536, 960

    while True:
        success, frame = cap.read()
        if success:
            
            if frame_num == 0:
                orig_frame_h, orig_frame_w, _ = frame.shape
            
            frame_num += 1
            # yoloV8 啟動
            # persist=True 表示在多幀間持續追蹤目標
            # YOLO 支持使用 BoT-SORT 跟 ByteTrack 追蹤演算法，可以用 tracker='botsort.yaml' 或 'bytetrack.yaml' 來指定
            # classes = [2,7] 指定要追蹤的目標類別，這通常與模型的分類標籤對應，COCO dataset 內的分類，2和7分別是 car 跟 truck，3是motorcycle沒有偵測
            # verbose=False 關閉詳細輸出，減少追蹤過程中顯示的訊息。
            # results 會是只有一個元素的列表，results[0] 包含此幀中的所有偵測到的物件資訊，例如邊界框、類別、信心分數等
            results = model.track(frame, persist=True, tracker='bytetrack.yaml', classes = [2,7], verbose=False)
            # 要先確認影片中的此幀內是否有偵測到物件
            if results[0].boxes.id is not None:
                
                # boxes為這一幀所有 bounding box 資訊（中心座標以及w,h)的集合
                # track_ids為這一幀所有id的集合
                # cpu()：將儲存在 GPU 上的張量（tensor）移動到 CPU。
                boxes = results[0].boxes.xywh.cpu()
                # 將 bbox 的追蹤 ID 轉換為 int 並移動到 cpu 並將 ID 張量 tensor 轉換為 Python 的 list，方便後續處理或輸出。
                # 這樣，track_ids 會是每個 bboxes 的追蹤 ID 的列表。
                track_ids = results[0].boxes.id.int().cpu().tolist()
                
                if save[0]: # --save 的第一個數字，決定是否要儲存 YOLO 影像
                    # 將預測結果寫入影片（就是那些框框、偵測結果），繪製到輸入的影像上
                    annotated_frame = results[0].plot()
                    # 使用 opencv 在幀上繪製文字，文字內容為 str(frame_num)，文字在影像上的左上角座標 org=（x=20, y=40），cv2.FONT_HERSHEY_SIMPLEX 為 opencv 的簡單字體，fontScale=1 為字體縮放比例，color=(0, 255, 255) 是 BGR 格式，代表黃色
                    cv2.putText(annotated_frame, str(frame_num), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255))
                    # video_writer 是由 cv2.VideoWriter 創建的影片寫入物件，將這個帶有 YOLO 偵測結果的 frame 寫入新的影片內
                    video_writer.write(annotated_frame)

                # 紀錄目前的車輛
                # 將原本是 list 的 track_ids 轉為 set 放入 current_cars
                current_cars = set(track_ids)
                # print(current_cars, buffer)
                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    # 計算 bounding box 左上角 及 右下角 座標以供opencv截圖
                    x1 = int(x - w / 2)
                    y1 = int(y - h / 2)
                    # x2 = int(x + w / 2)
                    # y2 = int(y + h / 2)
                    x2 = int(x1 + w)
                    y2 = int(y1 + h)
                    
                    # 沿 x 軸方向左右移動 10 pixel
                    if x1 - 10 > 0:
                        x1 -= 10
                    else:
                        x1 = 0
                    if frame.shape[1] - x2 - 10 > 0:
                        x2 += 10
                    else:
                        x2 = frame.shape[1] - 1
                    
                    # 截取目標區域（ROI, Region of Interest）
                    roi = frame[y1:y2, x1:x2]
                    # 並將該區域調整為固定尺寸 (224, 224)，以便進行後續處理（如物體分類或特徵提取）。
                    roi = cv2.resize(roi, (224, 224))

                    # 將boxes和car_imgs中的資料放入car_info
                    # car_info = defaultdict(dict)，是個嵌套字典
                    car_info[track_id][frame_num] = {
                        "ori_imgs" :frame,  
                        "car_imgs" : roi,
                        "bboxes" : (x,y,w,h)
                    }
                # 每10幀偵測一次，check_interval=30
                # 定期檢測消失的車輛，record_cars 為上次偵測到的車輛的 ID 集合，current_cars 為這次偵測到的車輛的 ID 集合
                if frame_num%check_interval == 0:
                    disappeared_cars = record_cars - current_cars
                    record_cars = current_cars
                else:
                    # 在非檢查幀的期間，初始化空集合，不進入之後的 if 內
                    disappeared_cars = set()
                # 將結束的車輛進入buffer
                if disappeared_cars: # 如果有消失的車輛
                    for car_id in disappeared_cars:
                        # 將消失的車輛加入到 buffer 內，只有在 check_interval 的整數倍的幀內才會做
                        buffer.append(car_id)
        
        # 如果 frame 讀取失敗，當作影片播放完畢，將所有剩下的 car 都放入 buffer 內 (當作消失)
        else:
            for car_id in record_cars:
                buffer.append(car_id)
            record_cars.clear()
            video_finished = 1
            
        # 在 buffer 溢出後才處理
        if len(buffer) >= buffer_size:
            # 執行轉彎判斷及違規判斷
            # buffer[-buffer_size:] 會擷取 buffer 最後的 buffer_size 個元素
            # 例如 buffer=[1,2,3,4], buffer_size=2, buffer[-buffer_size:]=[3,4]
            
            # print("執行轉彎判斷的車輛:", sorted(buffer[-buffer_size:]))
            print("Cars performing turn detection: ", sorted(buffer[-buffer_size:]))
            
            # buffer 儲存的是 track_id 也就是 car_id 也就是 key
            # turn_info 會依據 buffer 內儲存的 car_id，從 car_info 字典內複製相應的 car_id 的資訊
            turn_info = {key: car_info[key] for key in buffer[-buffer_size:]}
            turn_cars, turn_way = turn_predict(turn_model, turn_info, output_folder, filename, save, turn, orig_frame_h, orig_frame_w)
            
            # print("轉彎的車輛", turn_cars)
            print("Turning cars: ", turn_cars)
            
            # 將有轉彎的車輛的 car_info 製成 light_info
            light_info = {key: car_info[key] for key in turn_cars}
            # 沒有判斷方向燈是否錯打？例如車輛左轉，卻打右轉燈？
            light_cars = light_predict(light_model, light_info, output_folder, filename, save, transformer_model, turn_way)
            
            # print("沒打方向燈的車輛:", light_cars)
            print("Cars without turn signals: ", light_cars)
            
            print("")
            # buffer 內的車輛都處理好了，所以要從 car_info 內移除
            for key in buffer[-buffer_size:]:
                if key in car_info:
                    del car_info[key]
            # 移除 buffer
            # 因為 buffer 內的車輛都已經從畫面中消失，並且判斷完是否轉彎與打燈了
            del buffer[-buffer_size:]

        # 影片結束後，處理剩下的車輛，並 break 出無窮迴圈
        if len(buffer) == 0 and video_finished == 1:
            break
        elif len(buffer) < buffer_size and video_finished == 1:
            
            # print("執行檢測的車輛:", sorted(buffer))
            print("Cars performing turn detection: ", sorted(buffer))
            
            turn_info = {key: car_info[key] for key in buffer}
            turn_cars, turn_way = turn_predict(turn_model, turn_info, output_folder, filename, save, turn, orig_frame_h, orig_frame_w)
            
            # print("轉彎的車輛", turn_cars)
            print("Turning cars: ", turn_cars)
            
            light_info = {key: car_info[key] for key in turn_cars}
            light_cars = light_predict(light_model, light_info, output_folder, filename, save, transformer_model, turn_way)
            
            # print("沒打方向燈的車輛:", light_cars)
            print("Cars without turn signals: ", light_cars)
            
            for key in buffer:
                if key in car_info:
                    del car_info[key]
            buffer.clear()
            break

    # 重置 YOLO 預設的唯一一個的追蹤器的狀態，清除之前的追蹤資訊，以便開始下一段影片的物件追蹤
    model.predictor.trackers[0].reset()
    # 釋放讀入影片的相關資源，使得 cap 無法再使用
    cap.release()
    # 如果有儲存 YOLO 的輸出影像，就會有 video_writer 寫出影像，也要釋放資源
    if save[0]:
        video_writer.release()
    # 關閉所有由 opencv 創建的視窗
    cv2.destroyAllWindows()
    #print(list(car_info.keys()))
    #print(len(car_info))        



