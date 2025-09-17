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
    
    img_tensors = [test_transforms(img) for img in images]
    batch = torch.stack(img_tensors).unsqueeze(0).to(device)  # shape: (1, seq_len, 3, 224, 224)
    
    model.eval() # 切換模型為評估模式
    predictions = [] # 預測類別名稱列表
    # img_list_names = [] # 對應的序列名稱
    check = 0
    with torch.no_grad():# 禁用梯度計算，也不進行反向傳播     
        true_len = len(images)
        outputs = model(batch, true_len)
        _, predicted = torch.max(outputs, 2)
        predictions.append([class_names[p] for p in predicted[0][:true_len]])
    return predictions

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