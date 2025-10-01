import torch
import pandas as pd
from model_max import MyModel
from dataLoad_max import make_test_dataloader

import os
from tqdm import tqdm # 用於進度條顯示
import pickle

from sklearn.metrics import confusion_matrix  # 導入混淆矩陣
import matplotlib.pyplot as plt  # 導入 matplotlib 用於繪圖
import seaborn as sns  # 用於美化混淆矩陣的顯示

import numpy as np
import sys

import config_max

from dataLoad_max import test_transforms

# class_names = ['none_light', "light"]
class_names = [0, 1]

device = config_max.device

def predict_test_data(model, images):
    """
    將輸入的影像序列分割成不重疊的 window_size 大小的窗口進行預測
    這樣可以保持與訓練時相同的輸入格式，提升模型準確度
    
    Args:
        model: 訓練好的模型
        images: 一輛車的所有影像幀列表 (通常為 ~200 幀)
    
    Returns:
        list: 包含每幀預測結果的列表 [[pred1, pred2, ..., predN]]
    
    處理流程:
        1. 將 ~200 幀分割成多個不重疊的 8 幀窗口
        2. 每個窗口分別送入模型預測
        3. 將所有窗口的預測結果組合成完整序列
        4. 最後不足 8 幀的部分也會組成一個窗口進行預測
    """
    window_size = config_max.window_size  # 通常為 8
    model.eval() # 切換模型為評估模式
    all_predictions = [] # 儲存所有窗口的預測結果
    
    print(f"Processing {len(images)} frames with window_size={window_size}")
    
    with torch.no_grad(): # 禁用梯度計算，也不進行反向傳播
        # 將影像序列分割成不重疊的窗口 (step = window_size)
        num_windows = (len(images) + window_size - 1) // window_size  # 計算總窗口數
        
        for window_idx in range(num_windows):
            start = window_idx * window_size
            end = min(start + window_size, len(images))
            window_images = images[start:end]
            
            if config_max.test_max_transformer_debug_msg:
                print(f"Processing window {window_idx + 1}/{num_windows}: frames {start+1}-{end}")
            
            # 對當前窗口進行預處理
            img_tensors = [test_transforms(img) for img in window_images]
            batch = torch.stack(img_tensors).unsqueeze(0).to(device)  # shape: (1, window_len, 3, 224, 224)
            
            # 對當前窗口進行預測
            true_len = len(window_images)
            outputs = model(batch, true_len)
            _, predicted = torch.max(outputs, 2)
            
            # 收集當前窗口的預測結果
            window_predictions = [class_names[p] for p in predicted[0][:true_len]]
            all_predictions.extend(window_predictions)
            
            if config_max.test_max_transformer_debug_msg:
                print(f"Window predictions: {window_predictions}")
    
    print(f"Total predictions: {len(all_predictions)} frames")
    return [all_predictions]  # 保持原本的返回格式 (list of list)

def transformer(model, imgs, filename, car_id, output_folder):

    # device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    # base_path = os.path.expanduser('~/output/')
    # test_data_path = os.path.join(base_path, "data", "test")
    # test_label_path = os.path.join(base_path, "label")
    # weight_path = os.path.join(base_path, "weights", "weight.pth")
    # save_name = test_data_path.split('\\')[-2] + '_' + test_data_path.split('\\')[-1]
    # save_name = test_data_path.split('/')[-2] + '_' + test_data_path.split('/')[-1]
    # save_folder = os.path.join(base_path, filename)
    save_folder = os.path.join(output_folder)
    
    os.makedirs(save_folder, exist_ok=True)

    # weight_path = config_max.weight_path

    # load model and use weights we saved before
    # MyModel(num_layers, output_size, nhead, dropout_rate=0.4)
    # num_layers = config_max.num_layers
    # classnum = config_max.classnum
    # nhead = config_max.nhead
    # dropout_rate = config_max.dropout_rate
    # model = MyModel(5, 2, 8, 0.1)
    # print(f"MyModel(num_layers={num_layers}, classnum={classnum}, nhead={nhead}, dropout_rate={dropout_rate})")
    # model = MyModel(num_layers, classnum, nhead, dropout_rate)
    # print(f"model load weight from {weight_path}")
    # model.load_state_dict(torch.load(weight_path))
    # model = model.to(device)

    # make dataloader for test data
    # test_loader = make_test_dataloader(test_data_path)

    # predictions, img_list_name = predict_test_data(model, test_loader)
    
    predictions = predict_test_data(model, imgs)
    
    save_path = os.path.join(save_folder, filename + ".csv")
    combined_data = []
    begin = 1
    end = len(predictions[0])

    # 將 frame 從 1 開始編號
    columns = [f"frame_{i}" for i in range(1,end + 1)]

    # 構建結果
    result = pd.DataFrame({
        "filename": [filename],
        "carid": [car_id],
        "begin": [begin],
        "end": [end],
        **{col: [val] for col, val in zip(columns, predictions[0])}
    })

    combined_data.append(result)

    # 合併所有結果
    output_data = pd.concat(combined_data, ignore_index=True)

    # 儲存至檔案
    # print(save_path)
    output_data.to_csv(save_path, index=False)
    
    print(f'save the {filename} waves csv file in {save_folder}')
    
    return predictions[0]