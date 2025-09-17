from collections import defaultdict
#import tensorflow as tf
import cv2
import os
from ultralytics import YOLO
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import torch
import shutil
from screenshot import make_violation_image
import sys
from test_new import light_process
from config_max import threshold

# 存波型圖
def save_wave_img(light_box_num_list, id,  output_folder, save, frame_num_list):
    if save:
        light_info_folder_path = os.path.join(output_folder , 'light_info')
        wave_img_path = os.path.join(light_info_folder_path, f"wave_{id}.jpg")
        
        # plt.plot(light_box_num_list)
        # plt.title(f"light Information")
        # plt.xlabel('Index')
        # plt.ylabel('light')
        
        # plt.plot(frame_num_list, light_box_num_list)  # 設定 x 軸為 frame_num
        plt.plot(range(1, len(light_box_num_list) + 1), light_box_num_list)
        plt.title(f"Light Information")
        plt.xlabel('Frame Number')  # 更改 x 軸標籤
        plt.ylabel('Light')
        plt.savefig(wave_img_path)
        plt.cla()  

# 將方向燈的預測結果儲存到 light_info 資料夾內的 light_predict.csv 檔案
def save_light_info(is_light, car_id, output_folder, filename, save):
    if save:
        light_info_folder_path = os.path.join(output_folder , 'light_info')
        csv_path = os.path.join(light_info_folder_path, "light_predict.csv")
        # 追加模式 ('a') 開啟或創建 light_predict.csv 檔案
        with open(csv_path, mode='a', newline='') as csvfile:
            df = csv.writer(csvfile)
            if os.stat(csv_path).st_size == 0:  # 檢查檔案是否為空
                # 若為空，先寫入表頭（video_name, car_id, predict_light）
                df.writerow(['video_name', 'car_id', 'predict_light'])
            # 寫成車燈標記
            df.writerow([filename, car_id, is_light])

def light_predict(model, light_info, output_folder, filename, save, transformer_model, turn_way):
    violation_path = os.path.join(output_folder, 'violation')
    result = []
    # light_info 由有轉彎的車輛的 car_info 製成 
    if not light_info:
        return result
    
    else:
        
        for (car_id, frame_info), turn in zip(light_info.items(), turn_way):
            violation_imgs = []
            violation_bboxes = []
            car_imgs = [info["car_imgs"] for _, info in sorted(frame_info.items())]
            light_box_num_list = light_process(filename, car_id, car_imgs, model, transformer_model, output_folder, turn)
            light = is_light(light_box_num_list)
            save_light_info(light, car_id, output_folder, filename, save[3])
            # 如果這輛轉彎車，沒有打方向燈的話
            if light == 0:
                
                frame_keys = sorted(frame_info.keys())
                frame_num = len(frame_keys)
                target_indices = [int(0.4 * frame_num), int(0.6 * frame_num), int(0.8 * frame_num)]

                violation_imgs = []
                violation_bboxes = []

                for idx in target_indices:
                    frame_key = frame_keys[idx]
                    info = frame_info[frame_key]
                    violation_imgs.append(info["ori_imgs"])
                    violation_bboxes.append(info["bboxes"])
                
                # 車牌號碼(沒有偵測，只是個定值)
                license_plate = 'ccc-0001'
                make_violation_image(violation_imgs, violation_bboxes, car_id, license_plate, violation_path)
                result.append(car_id)
            frame_num_list = list(frame_info.keys())
            save_wave_img(light_box_num_list, car_id,  output_folder, save[3], frame_num_list)
        
        return result  

# 違規回傳 0，合法回傳 1
def is_light(num_list):
    
    total = len(num_list)

    if total == 0:
        return 1  # 跳過，當作合法，不討論是否違規
    
    if num_list.count(1) / total > threshold:
        return 1
    else:
        return 0
