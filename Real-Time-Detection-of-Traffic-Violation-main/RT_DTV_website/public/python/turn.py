import cv2 as cv
import numpy as np
import torch
from tqdm import tqdm
from turn_model import make_test_dataloader

def draw(track_info, save):      
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
                if save:
                    cv.imwrite('C:\\CCCProject\\ccc\\' + str(id) + '.jpg', img)
                car_id.append(id)
                imgs.append(img)
        else:
            continue 
    return car_id, imgs
  

class_names = ['left', 'right', 'straight'] 

def turn_predict(model, track_info, save = 0):
    turn_car = []
    # 存轉彎結果，還沒寫
    results = []
    model.eval()
    car_id, track_imgs = draw(track_info, save)
    test_loader = make_test_dataloader(track_imgs)
    with torch.no_grad():
        for images in tqdm(test_loader, desc="Predicting", disable=True):
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            images = images.to(device)

            # images = images.to("cuda:0")
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            results.extend([class_names[p] for p in predicted.cpu().numpy()])
    for turn, id in zip(results, car_id):
        if turn == 'left' or turn == 'right':
            turn_car.append(id)
    return turn_car






