import argparse
import datetime
import logging
import sys
from pathlib import Path
import numpy as np
import copy
from tqdm import tqdm
import os
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import torch
from torch.autograd import Variable
from torch.utils.data import DataLoader
import torch.nn as nn
import pickle
from dataload import *
from model import *


def test(SegNet):

    #model = model.to(device)
    base_path = os.path.dirname(os.path.abspath(__file__))
    pre_weight_path = os.path.join(base_path, "weights", "pre_weight.pth")
    SegNet.load_weights(pre_weight_path)
    SegNet.load_state_dict(torch.load(WEIGHTS,  map_location='cuda:3'),False)
    SegNet.eval()

    test = load_test_data(SAMPLES)
    test_data = test[0]
    img_srcs = test[1]
    img_names = test[2]
    
    with torch.no_grad():
        for (image, image_src, image_name) in zip(tqdm(test_data, desc="Testing"), img_srcs, img_names):
        
            image = torch.unsqueeze(image, dim=0)
            output = SegNet(image)

            output = torch.squeeze(output)
            output = output.argmax(dim=0)
            output_np = cv.resize(np.uint8(output), (224, 224))

            image_seg = np.zeros((224, 224, 3))
            image_seg = np.uint8(image_seg)
            colors = COLORS

            for c in range(CLASS_NUM):
                image_seg[:, :, 0] += np.uint8((output_np == c)) * np.uint8(colors[c][0])
                image_seg[:, :, 1] += np.uint8((output_np == c)) * np.uint8(colors[c][1])
                image_seg[:, :, 2] += np.uint8((output_np == c)) * np.uint8(colors[c][2])

            image_seg = Image.fromarray(np.uint8(image_seg))
            old_image = Image.fromarray(np.uint8(image_src))

            image = Image.blend(old_image, image_seg, 0.8)

            # 将背景或空類別
            image_np = np.array(image)
            image_np[output_np == 0] = image_src[output_np == 0]
            image = Image.fromarray(image_np)
            image.save(os.path.join(OUTPUTS,image_name))
            print(image_name + " is done!")


#測試的資料夾格式為底下全都是圖片，沒有其它子資料夾
parser = argparse.ArgumentParser()
parser.add_argument("--samples", type=str, default="", help="測試的資料夾路徑")
parser.add_argument("--colors", type=int, default=[[0, 0, 0], [0, 0, 255]], help="遮罩的颜色")
parser.add_argument("--outputs", type=str, default="", help="保存结果資料夾的路徑")
opt = parser.parse_args()

base_path = os.path.dirname((os.path.abspath(__file__)))
WEIGHTS = os.path.join(base_path, "weights", "weight.pth")



CLASS_NUM = 2
SAMPLES = opt.samples
#檢查SAMPLES是否存在
try:
    if not os.path.exists(SAMPLES):
        raise ValueError(f"The folder {SAMPLES} doesn't exist.")
except ValueError as e:
    raise argparse.ArgumentTypeError(f"Invalid value for --name: {e}")


OUTPUTS = opt.outputs
os.makedirs(OUTPUTS , exist_ok=True)
COLORS = opt.colors

SegNet = SegNet(3, CLASS_NUM)
test(SegNet)
