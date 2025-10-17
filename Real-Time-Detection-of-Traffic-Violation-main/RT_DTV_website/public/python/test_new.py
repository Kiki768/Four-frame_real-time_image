import os
import cv2
from ultralytics import YOLO
import re
import pandas as pd
from tqdm import tqdm
import sys
from PIL import Image
from test_max_transformer import transformer

def light_process(filename, car_id, car_imgs, model, transformer_model, output_folder, turn):

    draw_bbox = 1
    
    # print(f"[DEBUG] 車輛 {car_id} 的轉向為: {turn}")
    print(f"[DEBUG] Car {car_id} turn direction: {turn}")

    if draw_bbox:
        # print(f"繪製帶有 bbox 的畫面")
        print(f"Drawing frame with bbox")

    # 路徑設定
    # INPUT_DIR = "../transformer/data/test_police"
    # INPUT_DIR = "../transformer/data/test_light_way"
    # OUTPUT_DIR = os.path.expanduser("~/output/light_position/test_light_way")
    WEIGHTS_PATH = os.path.expanduser("~/turn_signal_position_detection/runs/detect/yolo_light_train2/weights/best.pt")
    # OUTPUT_WITH_BOX_DIR = os.path.expanduser("~/output/with_bbox/")
    OUTPUT_WITH_BOX_DIR = os.path.expanduser("../output/with_bbox/")

    # print(f'INPUT_DIR: {INPUT_DIR}')
    # print(f'OUTPUT_DIR: {OUTPUT_DIR}')
    # print(f'WEIGHTS_PATH: {WEIGHTS_PATH}')
    # print(f'OUTPUT_WITH_BOX_DIR: {OUTPUT_WITH_BOX_DIR}')

    # 建立輸出資料夾（如果還沒存在）
    # os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_WITH_BOX_DIR, exist_ok=True)

    # os.makedirs(OUTPUT_WITH_BOX, exist_ok=True)
    # os.makedirs(OUTPUT_ONLY_BOX, exist_ok=True)

    # 載入模型
    # model = YOLO(WEIGHTS_PATH)
    if model is None:
        model = YOLO(WEIGHTS_PATH)

    # 類別名稱
    class_names = ['l', 'r']

    # 讀取 input 資料夾內所有圖片
    # image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # # 遍歷每個子資料夾
    # car_folders = [f for f in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, f))]

    bbox_num = 0

    # xlsx_file = os.path.join('../transformer', '警方的未使用方向燈舉發資料.xlsx')
    # xlsx_file = os.path.expanduser("~/transformer/警方的未使用方向燈舉發資料.xlsx")
    # df = pd.read_excel(xlsx_file)
    
    ###======= 以下為新增的 ======###
    
    no_bbox = 0
    
    # output_folder = os.path.join(OUTPUT_DIR, filename)
    output_with_bbox_folder = os.path.join(OUTPUT_WITH_BOX_DIR, filename)
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_with_bbox_folder, exist_ok=True)
    
    # row_match = df[df['影片名稱'] == filename]

    # if row_match.empty:
    #     print(f"[警告] 找不到影片名稱: {filename}")
    #     return
    
    # turn = row_match.iloc[0]['轉向']
    
    frame_num = 0
    
    light_box_num_list = []  # 儲存每張圖的亮燈狀態 (0 或 1)
    
    cropped_imgs = []
    
    for img in car_imgs:

        results = model(img, verbose=False)[0]

        if len(results.boxes) == 0:
            # print(f"no bbox: {filename}/{img_name}")
            no_bbox += 1
            continue
        else:
            frame_num += 1
        
        # 之前是用 bbox 與圖片中心的歐式距離排序，拿最接近圖片中心的一個或兩個 bbox 當作左右方向燈
        # 用 x_center 分辨左右
        boxes_with_center = []
        for box in results.boxes:
            x_center = box.xywh[0][0].item()
            boxes_with_center.append((x_center, box))

        boxes_with_center.sort(key=lambda x: x[0])
        
        if len(boxes_with_center) == 1:
            light_assignments = [(turn, boxes_with_center[0][1])]
        else:
            light_assignments = [
                ('left', boxes_with_center[0][1]),
                ('right', boxes_with_center[-1][1])
            ]

        if draw_bbox:
            img_with_boxes = img.copy()

        car_str = None
        frame_str = None
        # cropped_imgs = []

        for light_type, box in light_assignments:
            if light_type != turn:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            h, w, _ = img.shape
            x1, x2 = max(0, min(x1, w)), max(0, min(x2, w))
            y1, y2 = max(0, min(y1, h)), max(0, min(y2, h))
            cropped = img[y1:y2, x1:x2]
            
            # Convert BGR to RGB and then to PIL Image for transformer
            cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            cropped_pil = Image.fromarray(cropped_rgb)
            cropped_imgs.append(cropped_pil)

            # output_path = os.path.join(output_folder, f"car{car_id}_{frame_num}.jpg")
            # cv2.imwrite(output_path, cropped)

            #####======== 繪製帶有 bbox 的畫面 ========#####

            if draw_bbox:
                # 顏色依照左右可自定
                color = (0, 0, 255) if light_type == 'l' else (255, 0, 0)
                cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), color, 2)  # 框線粗細為 2 像素
                cv2.putText(img_with_boxes, light_type.upper(), (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                # img_with_boxes：目標圖片。
                # light_type.upper()：顯示的文字內容，會將 'l' 或 'r' 轉成 'L' 或 'R'。
                # (x1, y1 - 5)：文字的位置，比框的左上角高一點（避免重疊）。
                # cv2.FONT_HERSHEY_SIMPLEX：使用的字體。
                # 0.5：字體大小。
                # color：文字顏色（同 bbox 顏色）。
                # 2：文字線條粗細。

        # if draw_bbox and car_str is not None and frame_str is not None:
        if draw_bbox:
            output_with_box_path = os.path.join(output_with_bbox_folder, f"car{car_id}_{frame_num}.jpg")
            cv2.imwrite(output_with_box_path, img_with_boxes)

    print(f"✔ light_process() saved, no_bbox_count: {no_bbox}")
    light_box_num_list = transformer(transformer_model, cropped_imgs, filename, car_id, output_folder)
    #light_box_num_list = transformer(transformer_model, car_imgs, filename, car_id, output_folder)
    '''
    # Draw bbox with colors based on light_box_num_list values
    if draw_bbox:
        OUTPUT_WITH_BOX_LIGHT_DIR = os.path.expanduser("../output/with_bbox_light")
        output_with_bbox_light_folder = os.path.join(OUTPUT_WITH_BOX_LIGHT_DIR, filename)
        os.makedirs(output_with_bbox_light_folder, exist_ok=True)
        
        # Reset counter and process images again with colored bboxes
        frame_num = 0
        img_index = 0
        
        for img in car_imgs:
            results = model(img, verbose=False)[0]
            
            if len(results.boxes) == 0:
                continue
            else:
                frame_num += 1
            
            # Skip if we don't have a corresponding light_box_num_list value
            if img_index >= len(light_box_num_list):
                break
                
            # 之前是用 bbox 與圖片中心的歐式距離排序，拿最接近圖片中心的一個或兩個 bbox 當作左右方向燈
            # 用 x_center 分辨左右
            boxes_with_center = []
            for box in results.boxes:
                x_center = box.xywh[0][0].item()
                boxes_with_center.append((x_center, box))
            
            boxes_with_center.sort(key=lambda x: x[0])
            
            if len(boxes_with_center) == 1:
                light_assignments = [(turn, boxes_with_center[0][1])]
            else:
                light_assignments = [
                    ('left', boxes_with_center[0][1]),
                    ('right', boxes_with_center[-1][1])
                ]
            
            img_with_colored_boxes = img.copy()
            
            for light_type, box in light_assignments:
                if light_type != turn:
                    continue
                
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                h, w, _ = img.shape
                x1, x2 = max(0, min(x1, w)), max(0, min(x2, w))
                y1, y2 = max(0, min(y1, h)), max(0, min(y2, h))
                
                # Choose color based on light_box_num_list value
                # 0 = blue (255, 0, 0), 1 = yellow (0, 255, 255)
                light_value = light_box_num_list[img_index]
                color = (255, 0, 0) if light_value == 0 else (0, 255, 255)
                
                cv2.rectangle(img_with_colored_boxes, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img_with_colored_boxes, f"{light_type.upper()}_{light_value}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Save image with colored bbox
            output_with_colored_box_path = os.path.join(output_with_bbox_light_folder, f"car{car_id}_{frame_num}.jpg")
            cv2.imwrite(output_with_colored_box_path, img_with_colored_boxes)
            img_index += 1
    '''
    return light_box_num_list
    