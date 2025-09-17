from collections import defaultdict
import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO

from turn import turn_predict          # (model, track_info, output_folder, filename, save, turn) -> (turn_car_ids, turn_way)
from light import light_predict        # (model, light_info, output_folder, filename, save, transformer_model, turn_way) -> [violation_car_ids]
from turn_model import ResNet, ResidualBlock
from model_max import MyModel
import config_max

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
current_dir = os.path.dirname((os.path.abspath(__file__)))
weight = os.path.join(current_dir, "weight")
model = YOLO(os.path.join(weight, "yolo11m.pt"))
model.to(device)

turn_model = ResNet(ResidualBlock, [3,4,6,3])
turn_model.load_state_dict(torch.load(os.path.join(weight, "turn.pth"), map_location=device))
turn_model = turn_model.to(device)

light_model = YOLO(os.path.join(weight, "yolo_light_train2_best.pt"))
light_model = light_model.to(device)

weight_path = config_max.weight_path
num_layers = config_max.num_layers
classnum = config_max.classnum
nhead = config_max.nhead
dropout_rate = config_max.dropout_rate

transformer_model = MyModel(num_layers, classnum, nhead, dropout_rate)
transformer_model.load_state_dict(torch.load(weight_path, map_location=device))
transformer_model = transformer_model.to(device)



# ----------------------
# 小工具
# ----------------------

def _safe_pad_box(x1, y1, x2, y2, W, H, pad=10):
    # 把邊界處理的部分提出來
    x1 = max(0, x1 - pad)
    y1 = max(0, y1 - pad)
    x2 = min(W - 1, x2 + pad)
    y2 = min(H - 1, y2 + pad)
    return x1, y1, x2, y2

# ----------------------
# 主流程
# ----------------------
def car_track(video_path, output_folder, save, turn):

    save = [0, 0, 0, 0]
    filename = os.path.basename(video_path)[:-4]
    print("video：", filename)

    cur_dir = os.path.dirname(os.path.abspath(__file__))              # website/public/python
    violation_path = os.path.abspath(os.path.join(cur_dir, "..", "videos", "result"))
    os.makedirs(violation_path, exist_ok=True)

    car_info = defaultdict(dict)
    buffer = []
    record_cars = set()
    frame_num = 0
    video_finished = 0

    buffer_size = 16
    check_interval = 30


    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[Error] Cannot open video: {video_path}")
        return

    # 不輸出影片
    # if save[0]:
    #     output_video_path = os.path.join(output_folder ,f"{filename}_output.webm")
    #     video_writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'VP80'), fps, (width, height))

    while True:
        success, frame = cap.read()
        if not success:
            for cid in record_cars:
                buffer.append(cid)
            record_cars.clear()
            video_finished = True   
        else:
            frame_num += 1
            results = model.track(frame, persist=True, tracker='bytetrack.yaml', classes=[2,7], verbose=False)

            if results and results[0].boxes.id is not None:
                boxes_xywh = results[0].boxes.xywh.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                current_cars = set(track_ids)

                H, W = frame.shape[0], frame.shape[1]   # ← 用 frame 取代 W/H 變數
                for (x, y, w, h), tid in zip(boxes_xywh, track_ids):
                    x1 = int(x - w / 2); y1 = int(y - h / 2)
                    x2 = int(x1 + w);    y2 = int(y1 + h)
                    x1, y1, x2, y2 = _safe_pad_box(x1, y1, x2, y2, W, H, pad=10)

                    roi = frame[y1:y2, x1:x2]
                    try:
                        roi = cv2.resize(roi, (224, 224))
                    except Exception:
                        continue

                    car_info[tid][frame_num] = {
                        "ori_imgs": frame,
                        "car_imgs": roi,
                        "bboxes": (float(x), float(y), float(w), float(h)),
                    }

                if frame_num % check_interval == 0:
                    disappeared = record_cars - current_cars
                    record_cars = current_cars
                else:
                    disappeared = set()

                if disappeared:
                    buffer.extend(list(disappeared))


        # 批次處理：buffer 滿了
        if len(buffer) >= buffer_size:
            # 執行轉彎判斷及違規判斷
            # buffer[-buffer_size:] 會擷取 buffer 最後的 buffer_size 個元素
            # 例如 buffer=[1,2,3,4], buffer_size=2, buffer[-buffer_size:]=[3,4]
            
            # print("執行轉彎判斷的車輛:", sorted(buffer[-buffer_size:]))
            print("Cars performing turn detection: ", sorted(buffer[-buffer_size:]))
            
            # buffer 儲存的是 track_id 也就是 car_id 也就是 key
            # turn_info 會依據 buffer 內儲存的 car_id，從 car_info 字典內複製相應的 car_id 的資訊
            turn_info = {key: car_info[key] for key in buffer[-buffer_size:]}
            turn_cars, turn_way = turn_predict(turn_model, turn_info, violation_path, filename, save, turn)
            
            # print("轉彎的車輛", turn_cars)
            print("Turning cars: ", turn_cars)
            
            # 將有轉彎的車輛的 car_info 製成 light_info
            light_info = {key: car_info[key] for key in turn_cars}
            # 沒有判斷方向燈是否錯打？例如車輛左轉，卻打右轉燈？
            light_cars = light_predict(light_model, light_info, violation_path, filename, save, transformer_model, turn_way)
            
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
            turn_cars, turn_way = turn_predict(turn_model, turn_info, output_folder, filename, save, turn)
            
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
    # 關閉所有由 opencv 創建的視窗
    cv2.destroyAllWindows()