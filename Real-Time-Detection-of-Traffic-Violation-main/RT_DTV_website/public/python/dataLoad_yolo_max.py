import numpy as np
import torch
import pandas as pd
import torch.nn as nn
import torch.utils
import torch.utils.data
from torchvision import datasets
from torchvision import transforms
from torch.nn.utils.rnn import pad_sequence
import os
from tqdm import tqdm
from PIL import Image
from torchvision import transforms
from torch.utils.data import DataLoader, Dataset
import sys

import config_max

# You can modify hyperparemeter
train_batch_size = config_max.train_batch_size
# train_batch_size = 8
test_batch_size = config_max.test_batch_size
window_size = config_max.window_size
# window_size = 30
step = config_max.step # 改成 5 時 train accuracy 在 0.5~0.6 以下
num_workers = config_max.num_workers
train_size_rate = config_max.train_size_rate   # Split dataset into train and validation 8:2

# Image transform for train and test
data_transforms = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
test_transforms = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Make dataset and dataloader
def make_train_dataloader(img_path, label_path):
    # 每次用 __getitem__ 碰一次 dataset，會回傳的一筆資料，包含 img_list_tensor、labels_tensor、img_list_name
    # img_list_tensor 的形狀為 (window_size, C, H, W)
    dataset = Dataset_car_list(img_path = img_path, label_path = label_path, transform = data_transforms)
    train_size = int(len(dataset) * train_size_rate)
    valid_size = len(dataset) - train_size
    train_dataset = torch.utils.data.Subset(dataset, range(0, train_size))
    valid_dataset = torch.utils.data.Subset(dataset, range(train_size, len(dataset)))
    # train_dataset, valid_dataset = torch.utils.data.random_split(dataset, [train_size, valid_size])
    # 每碰一次 train_loader 也是會回傳 img_list_tensor_batch 、 labels_tensor_batch 、 img_list_name_batch ，只是多了一個維度，用 batch 的數量組合在一起
    # 例如 img_list_tensor_batch 的形狀為 (batch_size, window_size, C, H, W)
    train_loader = DataLoader(train_dataset, batch_size=train_batch_size, shuffle=True, num_workers=num_workers, collate_fn=collate_fn)
    valid_loader = DataLoader(valid_dataset, batch_size=train_batch_size, shuffle=False, num_workers=num_workers, collate_fn=collate_fn)

    return train_loader, valid_loader

def make_test_dataloader(data_path):
    datasets = Dataset_car_list(img_path = data_path, transform = data_transforms, mode = "test")
    test_loader = DataLoader(datasets, batch_size=test_batch_size, shuffle=False, num_workers=num_workers, collate_fn=collate_fn_test)
    return test_loader

class Dataset_car_list(Dataset):
    def __init__(self, img_path, label_path = None, transform = None, mode = 'train'):
        if mode == 'train':
            # image_files = [
            #     window_list = [
            #         [video_name, frame, img_path, label],
            #         (共 window_size 筆資料)
            #     ], (沒有 car_id 的資料，所有 window_list 串成 image_files，共有所有 car 的數量 * 每輛車分成的 window_list 數量)
            # ]
            image_files = split_images_to_car_list(img_path, label_path)
        elif mode == 'test':
            # image_files = [
                # car_list_i =  [
                    # [video_name, frame, img_path, label], ... (frame_list，包含此幀的相關資料)
                    # (共有此資料夾內的所有 car_img，因此可能有接近 200 幀的資料在一個 car_list_i 內)
                # ], (有許多 car_list_i，數量等同於 test 資料夾內的影片資料夾數量，也因此每個資料夾內只能放僅限一個 car_id 的車輛截圖組)
            # ]
            image_files = car_list_from_folder(img_path)
        self.image_files = image_files
        self.transform = transform
        self.mode = mode

    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx):
        try:
            # idx 決定是哪個 window_list 或者哪個 car_list_i
            img_list = []
            labels = []
            img_list_name = self.image_files[idx][0][0]

    # img_len 在 train 時就是 window_size，在 test 時就是 car_list_i 內的影像數量
            img_len = len(self.image_files[idx])
            for i in range(img_len):
                img_path = self.image_files[idx][i][2]
                label = self.image_files[idx][i][3]
                img = Image.open(img_path).convert('RGB')
                if self.transform:  # 對影像進行 preprocess
                    img = self.transform(img)
                img_list.append(img)
                labels.append(label)
            img_list_tensor = torch.stack(img_list)
            labels_tensor = torch.tensor(labels)
            if self.mode == 'train':
                # 回傳一筆資料
                return img_list_tensor, labels_tensor, img_list_name
            elif self.mode == 'test':
                return img_list_tensor, labels_tensor, img_list_name
            
        except Exception as e:
        # 找出是哪個 car folder 出錯
            folder_hint = self.image_files[idx][0][2].split(os.sep)
            folder_name = folder_hint[-2] if len(folder_hint) > 2 else "未知資料夾"
            print(f"[❌ IndexError] 讀取第 {idx} 筆 self.image_files 時出錯！來自資料夾：{folder_name}")
            print(f"[🐞 DEBUG] img_list_name: {img_list_name}")
            print(f"[🐞 DEBUG] 錯誤訊息：{e}")
            raise e  # 繼續丟出例外讓主程式知道


def split_images_to_car_list(img_folder, label_path):
    car_list = []
    combined_label = []
    for label_file in os.listdir(label_path):
        if label_file.endswith(".csv"):
            file_path = os.path.join(label_path, label_file)
            # print(file_path)
            df = pd.read_csv(file_path)
            combined_label.append(df)
    combined_label_df = pd.concat(combined_label, ignore_index=True)
    # 將所有 label 的 csv 檔案的資訊合併成一個 DataFrame 並重新索引
    # 例如，假設 combined_label 為：
    # [
    #      ID   Name
    #   0   1  Alice
    #   1   2    Bob
    #   ,
    #      ID     Name
    #   0   7  Charlie
    #   1   8   David
    # ]
    # 合併後的 combined_label_df 為：
    #        ID   Name
    #    0   1   Alice
    #    1   2     Bob
    #    2   7  Charlie
    #    3   8   David
    print(combined_label_df)
    
    combined_label_df = check_files_and_count_labels_and_turn_light(data_path, combined_label_df)
    
    # iterrows() 逐行讀取 combined_label_df 的 DataFrame，每一行代表一輛車的資訊
    for index, row in combined_label_df.iterrows():
        windows_list = []
        name = row["filename"]
        car_id = row["carid"]
        begin_frame = row["begin"]
        end_frame = row["end"]
        # row.to_list() 會將 row 轉換為 [name, car_id, begin_frame, end_frame, frame_1, frame_2, ..., frame_n]
        tmp_car_list = row.to_list()
        
        # # 每行 (每個 car_id) 分成數個 window，串接到一個 windows_list 下
        # for start in range(begin_frame, end_frame - window_size, step):
        #     window_list = []
        #     for i in range(window_size):
        #         img_path = os.path.join(img_folder,name ,"car" + str(car_id) + "_" + str(start + i) +".jpg")
        #         # 每個 window 包含以下欄位 [filename, 當前的 frame_num, img_path, 當前 frame 的車燈亮暗標記值 (-1,0,1)]
        #         # 也就是 [video_name, frame, img_path, label]
        #         # tmp_car_list 這個 row 的欄位轉為 list，而編號為 start+i 的 frame 本應在 tmp_car_list[start+i-1]，但開頭要跳過四個欄位 (filename,carid,begin,end)，所以加四後變為 tmp_car_list[start + i + 3]
        #         window_list.append([row['filename'], start + i, img_path, int(tmp_car_list[start + i + 3])])
        #     windows_list.append(window_list)
        # # windows_list = [[[row['filename'], start + i, 'path', int(tmp_car_list[start + i + 3]) ] for i in range(window_size)] for start in range(begin_frame, end_frame - window_size, step)]
        # # car_list.extend(windows_list) 是將 windows_list 內的所有元素加入 car_list，而不是把 windows_list 當作一個整體加入
        # # 所以並沒有像 windows_list 那樣區分不同的 carid，而是把所有的 window 都串在同一個 list 內
        # car_list.extend(windows_list)
        
        # 我稍微修改，取消無意義的 windows_list，直接將 window 接到 car_list 下面
        # for start in range(begin_frame, end_frame - window_size, step):
        #     window_list = []
        #     for i in range(window_size):
        #         img_path = os.path.join(img_folder,name ,"car" + str(car_id) + "_" + str(start + i) +".jpg")
        #         window_list.append([row['filename'], start + i, img_path, int(tmp_car_list[start + i + 3])])
        #     car_list.append(window_list)
        
        valid_frames = []
        # 掃描該車的所有 frame，挑出合法的（label ≠ -1 且圖片存在）
        for frame in range(begin_frame, end_frame):
            label = int(tmp_car_list[frame + 3])
            if label != -1:
                img_path = os.path.join(img_folder, name, f"car{car_id}_{frame}.jpg")
                if os.path.exists(img_path):
                    valid_frames.append([name, frame, img_path, label])

        # 用滑動視窗方式將合法 frame 分組
        for start in range(0, len(valid_frames) - window_size + 1, step):
            window = valid_frames[start : start + window_size]
            if len(window) == window_size:
                car_list.append(window)
                
    # print(car_list[2][0])
    # print(len(car_list),len(car_list[2]))
    # car_list 架構：
    # 一個三維的 list，包含所有 car (car_id) 的 window_list
    # 每個 window list 包含數量固定為 window_size 組的資料
    # 每筆資料包含 4 個欄位：[filename, 當前的 frame_num, img_path, 當前 frame 的車燈亮暗標記值 (-1,0,1)]
    
    # car_list = [
    #     window_list, window_list, ..., window_list # 數量為 (所有 csv 檔案的 row 數量 (每輛車) ) * (每輛車分割成的 window_list 數量)
    #     不含 windows_list，因為 car_list 就是很多 windows_list【合併】(不是串接)
    # ] 
    # window_list = [
        # 固定有 window_size 筆資料
        # [filename, 當前的 frame_num, img_path, 當前 frame 的車燈亮暗標記值 (-1,0,1)], [filename, 當前的 frame_num, img_path, 當前 frame 的車燈亮暗標記值 (-1,0,1)], ... # 共有 window_size 組資料
    # ]
    # car_list = [
    #    window_list = [
    #        [filename, 當前的 frame_num, img_path, 當前 frame 的車燈亮暗標記值 (-1,0,1)], ... (window_size 組)
    #    ], ..., (將 carimg 以 window_size 和 step 分組，不分 carid 都串接在 car_list 之下)
    # ]
    return car_list

def car_list_from_folder(directory):
    car_list = []
    for video_name in os.listdir(directory):
        video_path = os.path.join(directory, video_name)
        car_list_i = []
        for img in os.listdir(video_path):
            if not img.lower().endswith('.jpg'):  # 確保副檔名為 .jpg（忽略大小寫）
                continue  # 跳過非 .jpg 的檔案
            # 以底線 "_" 分割檔名，例如 "car12_001.jpg" 會變成 ["car12", "001.jpg"]
            tmp_img = img.split('_')
            # carid = int(tmp_img[0][4:]) # 假設檔名格式為 "car12_001.jpg"，則 `car12[4:]` 取得 "12" 並轉為整數
            # 從檔名取得影像的幀編號 (frame number)，去掉副檔名 ".jpg"  
            # 例如 "car12_001.jpg" → `tmp_img[1] = "001.jpg"` → `[:-4]` 去掉 ".jpg" → 轉為整數 `1`
            frame = int(tmp_img[1][:-4])
            label = -1
            img_path = os.path.join(video_path, img)
            frame_list = [video_name, frame, img_path, label]
            car_list_i.append(frame_list)
        car_list.append(car_list_i)
    # car_list = [
        # car_list_i =  [
            # [video_name, frame, img_path, label], ... (frame_list，包含此幀的相關資料)
        # ], (有許多 car_list_i，數量等同於 test 資料夾內的影片資料夾數量，也因此每個資料夾內只能放僅限一個 car_id 的車輛截圖組)
    # ]
    return car_list

def collate_fn(batch):
    sequences = [x[0] for x in batch]
    labels = [x[1] for x in batch]
    image_list_name = [x[2] for x in batch]
    seq_len = [len(s) for s in sequences]

    seq_len = torch.tensor(seq_len)
    sequences = torch.stack(sequences)
    labels = torch.stack(labels)
    return sequences, labels, seq_len, image_list_name

def collate_fn_test(batch):
    # 用於將 samples 組合成一個 batch
    # 它會把 Dataset_car_list.__getitem__ 回傳的單筆資料轉換成批次張量 (batch tensor)，讓模型可以一次處理多筆資料，提高運算效率。
    # batch = [
    #     [img_list_tensor, labels_tensor, img_list_name],
    #     共 batch_size 筆
    # ]
    # sequences 是一個 list，包含 batch_size 筆 img_list_tensor
    sequences = [x[0] for x in batch]
    # labels 是一個 list，包含 batch_size 筆 labels_tensor
    labels = [x[1] for x in batch]
    # image_list_name 是一個 list，包含 batch_size 筆 img_list_name
    image_list_name = [x[2] for x in batch]
    # 為每個 img_list_tensor 的 len，應該是 frames 數量，
    seq_len = [len(s) for s in sequences]
    seq_len = torch.tensor(seq_len)
    sequences = torch.stack(sequences)
    labels = torch.stack(labels)
    return sequences, labels, seq_len, image_list_name

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_path, "data", "train")
# label_path = os.path.join(base_path, "label")
# train_loader, _ = make_train_dataloader(data_path, label_path)
# print(len(train_loader))
# # test_loader = make_test_dataloader(data_path)
# for data, target, seq_len, image_list_name in tqdm(train_loader, desc="Training"):
#     print(data.shape)
#     print(target.shape)
#     print(seq_len)
#     print(image_list_name)

def check_files_and_count_labels_and_turn_light(base_dir, combined_label_df, xlsx_path=config_max.xlsx_path):
    window_size = config_max.window_size
    step = config_max.step

    # 讀取 xlsx 標記檔
    sheets = pd.read_excel(xlsx_path, sheet_name=None)
    mark_dfs = []
    for name, sheet in sheets.items():
        mark_dfs.append(sheet)
    mark_df = pd.concat(mark_dfs, ignore_index=True)

    # # 建立每個轉向類別的統計
    # stats = {
    #     'r': {'light': 0, 'no_light': 0, 'repeat_light': 0, 'repeat_no_light': 0},
    #     'l': {'light': 0, 'no_light': 0, 'repeat_light': 0, 'repeat_no_light': 0},
    #     'other': {'light': 0, 'no_light': 0, 'repeat_light': 0, 'repeat_no_light': 0}
    # }
    # 統計表：key = turn_value，value = {'light', 'no_light', 'repeat_light', 'repeat_no_light'}
    stats = {}
    
    # other_turns = []  # 收集其他轉向種類
    
    abnormal_turn_records = []  # 額外收集 turn 為 nan, s, n 的車
    
    turn_list = [] 

    for idx, row in combined_label_df.iterrows():
        filename = row['filename']
        carid = row['carid']
        begin = row['begin']
        end = row['end']

        # 找出對應的標記
        matched_rows = mark_df[(mark_df['video_name'] == filename) & (mark_df['car_id'] == carid)]
        if matched_rows.empty:
            print(f"警告：找不到 video_name = {filename}，car_id = {carid} 的標記資料")
            continue

        matched_row = matched_rows.iloc[0]
        
        # 決定這輛車的轉向種類
        turn_value_raw = matched_row['turn']
        if pd.isna(turn_value_raw):
            turn_value = 'nan'
        else:
            turn_value = str(turn_value_raw).strip().lower()
            
        # ✅ 如果 turn 不是 l/r/s，改拿 predict_turn
        if turn_value not in ['l', 'r', 's']:
            predict_turn_raw = matched_row.get('predict_turn', None)
            if pd.isna(predict_turn_raw):
                turn_value = 'nan'
            else:
                turn_value = str(predict_turn_raw).strip().lower()
            
        if turn_value in ['nan', 's', 'n']:
            abnormal_turn_records.append((filename, carid, turn_value))
            
        turn_list.append(turn_value)
            
        # 如果這個 turn_value 還沒出現過，初始化
        if turn_value not in stats:
            stats[turn_value] = {'light': 0, 'no_light': 0, 'repeat_light': 0, 'repeat_no_light': 0}
        

        # 先檢查所有影像是否存在
        for frame_num in range(begin, end + 1):
            img_path = os.path.join(base_dir, filename, f"car{carid}_{frame_num}.jpg")
            if not os.path.exists(img_path):
                print(f"檔案 {img_path} 不存在")
                sys.exit(0)
            
        # 計算不重複的 light / no_light
        for frame_num in range(begin, end + 1):
            frame_col = f'frame_{frame_num}'
            if frame_col in row:
                value = row[frame_col]
                if value == 1:
                    stats[turn_value]['light'] += 1
                elif value == 0:
                    stats[turn_value]['no_light'] += 1
                # -1 或 NaN 忽略
            
        # 計算有重複的 repeat_light / repeat_no_light
        frame_num_total = end - begin + 1
        if frame_num_total >= window_size:
            for start in range(begin, end - window_size + 2, step):
                for offset in range(window_size):
                    current_frame = start + offset
                    frame_col = f'frame_{current_frame}'
                    if frame_col in row:
                        value = row[frame_col]
                        if value == 1:
                            stats[turn_value]['repeat_light'] += 1
                        elif value == 0:
                            stats[turn_value]['repeat_no_light'] += 1
                        # -1 或 NaN 忽略
                        
    # 將 turn_list 寫回 combined_label_df，新增欄位 turn
    combined_label_df['turn'] = turn_list
    print("新增欄位 turn")

    print("\n===== 各轉向類別統計結果 =====")
    for turn, result in stats.items():
        print(f"\n轉向類別：【{turn}】")
        print(f"  light 幀數 = {result['light']}")
        print(f"  no_light 幀數 = {result['no_light']}")
        print(f"  repeat_light 幀數 = {result['repeat_light']}")
        print(f"  repeat_no_light 幀數 = {result['repeat_no_light']}")
        print(f"  total 原始幀數 = {result['light'] + result['no_light']}")
        print(f"  total 重複幀數 = {result['repeat_light'] + result['repeat_no_light']}")

    if abnormal_turn_records:
        print("\n===== 所有 turn 為 nan/s/n 的車輛資料 =====")
        for idx, (filename, carid, turn_value) in enumerate(abnormal_turn_records):
            print(f"{idx+1}. filename = {filename}, carid = {carid}, turn = {turn_value}")
            
        # 移除轉向為 nan/s/n 的列，並重排索引
        combined_label_df = combined_label_df[~combined_label_df['turn'].isin(['nan', 's', 'n'])].reset_index(drop=True)
        print("已移除所有 turn 為 nan/s/n 的標註資料")
    else:
        print("\n沒有 turn 為 nan、s 或 n 的資料")
    print("\n訓練與驗證資料皆存在且統計完畢！")
    output_csv_path = "combine_with_turn.csv" 
    combined_label_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 已儲存含轉向標記的新檔案：{output_csv_path}")
    print("\combined_label_df:")
    print(f"{combined_label_df}")
    # sys.exit(0)
    return combined_label_df