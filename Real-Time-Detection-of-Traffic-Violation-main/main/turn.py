import cv2 as cv
import numpy as np
import torch
import os
import csv
from tqdm import tqdm
from turn_model import make_test_dataloader
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
        

#畫軌跡
def draw(track_info, output_folder, save):      
    car_id= []
    imgs = []
    
    for id, frame_info in track_info.items():
        points = []
        start_coor = frame_info[list(frame_info.keys())[0]]['bboxes']
        end_coor = frame_info[list(frame_info.keys())[-1]]['bboxes']
        frame_num = 0
        for _, info in frame_info.items():
            frame_num = frame_num + 1  
            bbox = info["bboxes"]  
            points.append([bbox[0], bbox[1]]) 
        x1 = int(start_coor[0])
        y1 = int(start_coor[1])
        x2 = int(end_coor[0])
        y2 = int(end_coor[1])
        dis = (y2 - y1)**2 + (x2 - x1)**2 
        if frame_num > 35 and (y2 - y1) < 0 and dis > 10000:
                img = np.zeros((540,960,3), np.uint8)
                points = np.array(points)
                points = points.astype(np.int32).reshape((-1, 1, 2))
                cv.polylines(img, [points], isClosed=False, color=(255, 255, 255), thickness=1)
                cv.circle(img, (points[0][0][0], points[0][0][1]), 1, (255,0,0))
                cv.circle(img, (points[-1][0][0], points[-1][0][1]), 1, (0,255,0))
                car_id.append(id)
                imgs.append(img)
                #存turn_info的軌跡圖片
                save_trackimg(img, id, output_folder, save[2])
                #存car_img
                save_carimg(frame_info, id, output_folder, save[1])
                
                
        else:
            continue 
    return car_id, imgs
  

class_names = ['left', 'right', 'straight'] 

def turn_predict(model, track_info, output_folder, filename, save, turn):
    turn_car = []
    results = []
    car_id, track_imgs = draw(track_info, output_folder, save)
    if not car_id:
        return turn_car
    else:
        test_loader = make_test_dataloader(track_imgs)
        model.eval()
        with torch.no_grad():
            for images in tqdm(test_loader, desc="Predicting", disable=True):
                images = images.to("cuda:0")
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                results.extend([class_names[p] for p in predicted.cpu().numpy()])
        
        for label, id in zip(results, car_id): 
            if turn == 'n' and label in ['left', 'right']:     
                turn_car.append(id)
            if turn == 'l' and label == 'left':
                turn_car.append(id)
            if turn == 'r' and label == 'right':
                turn_car.append(id)
        save_turn_info(results, car_id, output_folder, filename, save[2]) #存turn_info的車輛轉彎方向csv檔(記錄車輛是直走、右轉還是左轉） 
        return turn_car




