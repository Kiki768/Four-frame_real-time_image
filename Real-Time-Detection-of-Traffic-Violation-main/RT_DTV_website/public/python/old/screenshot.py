import cv2
import pandas as pd
import csv
import os
import numpy as np
from collections import defaultdict


#畫bounding_box框框，return畫上bounding box的圖
def draw_rectangle(img, x, y, w, h):
    x1 = int(x - w / 2)
    y1 = int(y - h / 2)
    x2 = int(x1 + w)
    y2 = int(y1 + h)
    left_up = (x1, y1)
    right_down = (x2, y2)
    cv2.rectangle(img,left_up, right_down, (0, 0, 255), 3)
    return img


#在左上角繪製數字，回傳加上數字的照片
def draw_text(img, 
              text, 
              font = cv2.FONT_HERSHEY_PLAIN, 
              pos = (0,0), 
              font_scale = 3, 
              fone_thickness = 3,
              text_color = (0,0,255),
              text_color_bg = (255, 255, 255)):
    x, y = pos
    size , _ = cv2.getTextSize(text, font, font_scale, fone_thickness)
    text_w , text_h = size
    cv2.rectangle(img, pos, (x + text_w, y + text_h ), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, fone_thickness)
    return img 

#輸入四個圖片並合併
def merge_picture(imgs):
    top = cv2.vconcat([imgs[0], imgs[2]])
    bottom = cv2.vconcat([imgs[1], imgs[3]])
    result = cv2.hconcat([top, bottom])
    return result

#儲存合併後的圖片至/home/ai113/code2/result/v?/
def save_img(violation_image, car_id, output_folder):
    output_path = os.path.join(output_folder, "car"+str(car_id)+".jpg")
    cv2.imwrite(output_path, violation_image)
    # print("the result is saved in " + output_path)

#放大圖片
def big_img(img, x, y, w, h, imgx, imgy): 
    #尋找放大倍率(因為放大的話長寬要同比例，不然放大圖片會變扁)
    scale = min(imgx / w, imgy / h)
    w = int(imgx / scale)
    h = int(imgy / scale)
    #print(w, h, imgx, imgy)
    #設定放大為 
    x1 = int(x - h)
    y1 = int(y - w)
    x2 = int(x + h)
    y2 = int(y + w)
    #print(x, x1, x2, y, y1, y2)
    #檢查邊界(還沒做)
    '''
    if x1 < 0:
        print('x1 out of range in big img')
    if x2 > imgx:
        print('x2 out of range in big img')
    if y1 < 0:
        print('y1 out of range in big img')
    if y2 > imgy:
        print('y2 out of range in big img')
    '''
    img = img[y1:y2, x1:x2]
    return img

#從video的turn_data.csv取得某部轉彎車輛的資料
#影片在車輛偵測就轉成一張張圖片存進frame中了
def make_violation_image(four_imgs, four_bboxs, car_id, license_plate, output_folder):

    imgs = []
    #處理前三張照片，取整個過程中40%, 60%, 80%的幀數訊息
    for i in range(3):
        x, y, w, h = four_bboxs[i]
        #畫矩形
        img = draw_rectangle(four_imgs[i], x, y, w, h)
        #加數字
        img = draw_text(img, f'{i+1}')
        #將畫好的圖片加進去
        imgs.append(img)
    
    #處理第四張圖(60%)
    x, y, w, h = four_bboxs[1]
    fourth_img = four_imgs[1]
    #放大第四張圖片
    img4_x, img4_y, img4_channels = fourth_img.shape
    big_fourth_img = big_img(fourth_img, x, y, w, h, img4_x, img4_y)
    if not np.any(big_fourth_img):
        big_fourth_img = imgs[0]
        big_fourth_img = draw_text(big_fourth_img, 'List is empty')
        print("List is empty")
    else:
        big_fourth_img = cv2.resize(big_fourth_img, (img4_y,img4_x), interpolation= cv2.INTER_LINEAR)
    imgs.append(big_fourth_img)

    #合併四張圖
    violation_image = merge_picture(imgs)

    #儲存
    save_img(violation_image, car_id, output_folder)
    
     
    
