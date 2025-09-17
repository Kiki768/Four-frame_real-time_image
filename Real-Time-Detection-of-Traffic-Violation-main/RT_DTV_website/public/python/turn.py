import cv2 as cv
import numpy as np
import torch
import os
import csv
from tqdm import tqdm
from turn_model import make_test_dataloader

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#存car_img
def save_carimg(frame_info, id, output_folder, save):
    if save:
        for frame, info in frame_info.items():
            img = info["car_imgs"]
            carimg_folder_path = os.path.join(output_folder , 'carimg', f"{id}")
            os.makedirs(carimg_folder_path, exist_ok=True)
            carimg_path = os.path.join(carimg_folder_path, f"car{id}_{frame}.jpg")
            cv.imwrite(carimg_path, img)
            
#存turn_info的軌跡圖片
def save_trackimg(img, id, output_folder, save):
    if save:
        #格式：./"args.name"_output/turn_info/"filename"/track_"id".jpg
        turn_info_folder_path = os.path.join(output_folder , 'turn_info')
        track_img_path = os.path.join(turn_info_folder_path, f"track_{id}.jpg")
        cv.imwrite(track_img_path, img)
        
#存turn_info的車輛轉彎方向csv檔(記錄車輛是直走、右轉還是左轉）       
def save_turn_info(results, car_id, output_folder, filename, save):
    if save:
        turn_info_folder_path = os.path.join(output_folder , 'turn_info')
        csv_path = os.path.join(turn_info_folder_path, "turn_predict.csv")
        with open(csv_path, mode='a', newline='') as csvfile:
            df = csv.writer(csvfile)
            if os.stat(csv_path).st_size == 0:  # 檢查檔案是否為空
                df.writerow(['video_name', 'car_id', 'predict_turn'])
            for turn, id in zip(results, car_id):
                df.writerow([filename, id, turn])
        

# 畫軌跡
def draw(track_info, output_folder, save):      
    car_id= []
    imgs = []
    
    for id, frame_info in track_info.items():
        if not frame_info:
            # print(f"[警告] 車輛 {id} 的 frame_info 為空，跳過")
            print(f"[Warning] Car {id} has empty frame_info, skipping")
            continue
        points = []  # 用來儲存每幀車輛的座標點
        start_coor = frame_info[list(frame_info.keys())[0]]['bboxes']  # 取得第一幀的車輛邊界框座標 (x1, y1, x2, y2)
        end_coor = frame_info[list(frame_info.keys())[-1]]['bboxes']  # 取得最後一幀的車輛邊界框座標 (x1, y1, x2, y2)
        frame_num = 0
        for _, info in frame_info.items():
            frame_num = frame_num + 1  
            bbox = info["bboxes"]  
            points.append([bbox[0], bbox[1]]) # 儲存該幀的左上角座標 (x1, y1)
        
        # 取得第一幀和最後一幀的座標
        x1 = int(start_coor[0])  # 取第一幀邊界框的 x1
        y1 = int(start_coor[1])  # 取第一幀邊界框的 y1
        x2 = int(end_coor[0])  # 取最後一幀邊界框的 x1
        y2 = int(end_coor[1])  # 取最後一幀邊界框的 y1

        # 計算起始點和結束點之間的 pixel 距離的平方
        dis = (y2 - y1)**2 + (x2 - x1)**2  # 以 pixel 為單位，距離的平方
        # if frame_num > 35 and (y2 - y1) < 0 and dis > 10000:
        # dis > 10000 相當於剛出現的位置與消失的位置，直線距離在 100 pixel 內，過濾掉路邊停車等沒有在動的車
        if frame_num > 35 and (y2 - y1) < 0 and dis > 10000:
        # if (y2 - y1) < 0:
            # if frame_num <= 35: print(f"car {id}'s frame_num {frame_num} <= 35")
            # if dis <= 10000: print(f"car {id}'s moving distance {np.sqrt(dis)} pixel <= 100 pixel")
            img = np.zeros((540,960,3), np.uint8)
            points = np.array(points)
            points = points.astype(np.int32).reshape((-1, 1, 2))
            cv.polylines(img, [points], isClosed=False, color=(255, 255, 255), thickness=1)
            cv.circle(img, (points[0][0][0], points[0][0][1]), 1, (255,0,0))
            cv.circle(img, (points[-1][0][0], points[-1][0][1]), 1, (0,255,0))
            car_id.append(id)
            imgs.append(img)
            # 存turn_info的軌跡圖片
            save_trackimg(img, id, output_folder, save[2])
            # 存car_img
            save_carimg(frame_info, id, output_folder, save[1])
                
                
        else:
            continue 
    return car_id, imgs
  

class_names = ['left', 'right', 'straight'] 

def turn_predict(model, track_info, output_folder, filename, save, turn):
    turn_car = []
    results = []
    turn_way = []
    car_id, track_imgs = draw(track_info, output_folder, save)
    if not car_id:
        return turn_car, turn_way
    else:
        # 將 track_imgs 轉換為批次(每次4張影像)的 PyTorch Tensor 資料集的 DataLoader
        test_loader = make_test_dataloader(track_imgs)
        # 將模型切換到評估模式
        model.eval()
        # 禁用梯度計算，以減少記憶體使用並加速推論，不需更新權重
        with torch.no_grad():
            # 使用 for 迴圈逐批次讀取 test_loader 中的影像資料。
            for images in tqdm(test_loader, desc="Predicting", disable=True):
                # 每次處理 4 張影像（大小為批次大小），並將影像移到 GPU（cuda:0）上進行計算
                images = images.to(device)
                # 取得模型評估的結果，這裡的模型使用 ResNet
                outputs = model(images)
                # 使用 torch.max(outputs, 1) 找到每張影像分數最高的類別索引
                _, predicted = torch.max(outputs, 1)
                # 使用 .cpu().numpy() 將 Tensor 從 GPU 移回 CPU，並轉為 NumPy 陣列以進行處理
                # 將類別索引轉換為對應的類別名稱 class_names[p]，並存入 results
                results.extend([class_names[p] for p in predicted.cpu().numpy()])
        
        # turn 為 command line 輸入的 --turn，左轉路口為l,右轉路口為r,不指定則為n
        for label, id in zip(results, car_id): 
            if turn == 'n' and label in ['left', 'right']:
                turn_way.append(label)
                turn_car.append(id)
            if turn == 'l' and label == 'left':
                turn_way.append(label)
                turn_car.append(id)
            if turn == 'r' and label == 'right':
                turn_way.append(label)
                turn_car.append(id)
        save_turn_info(results, car_id, output_folder, filename, save[2]) #存turn_info的車輛轉彎方向csv檔(記錄車輛是直走、右轉還是左轉） 
        return turn_car, turn_way




