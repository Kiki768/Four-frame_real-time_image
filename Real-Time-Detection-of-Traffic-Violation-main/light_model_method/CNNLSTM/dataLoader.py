import argparse
import datetime
import logging
import sys
from pathlib import Path
from tqdm import tqdm
import numpy as np
import cv2 as cv
import os
from PIL import Image
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import torch
from torch.autograd import Variable
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
from torchvision import transforms
import torch.nn as nn
from CNNLSTM import *
import re
from torch.nn.utils.rnn import pad_sequence,pack_padded_sequence,pack_sequence,pad_packed_sequence


train_batch_size = 1
test_batch_size = 32
num_workers = 0
train_size_rate = 0.9
image_shape = (3, 224, 224)



#將資料集存成左邊資料夾

class Dataset(Dataset):
    def __init__(self, data_path, window , step, training=True):
        # 初始化参数
        self.training = training
        data_label = []
        labels = os.listdir(data_path)
        for label in labels:
            image_list_names = os.listdir(os.path.join(data_path, label))
            for image_list_name in image_list_names:
                cut_image_path = os.path.join(data_path, label, image_list_name)
                cut_image_list_names = os.listdir(cut_image_path)
                # print(cut_image_path)
                cut_image_list_names.sort(key = lambda x:int(x[:-4]))
                count = 0
                cut_image_list = []
                for num in range(0, len(cut_image_list_names)):
                    frame_path = os.path.join(cut_image_path, cut_image_list_names[num])
                    cut_image_list.append(frame_path)

                data_label.append((cut_image_list, label))
            self.data_label = data_label
        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.data_label)
        

    def __getitem__(self, idx):
        data_path, label = self.data_label[idx]
        data = []
        for frame_path in data_path:
            frame = Image.open(frame_path).convert('RGB')
            frame = self.transform(frame)
            data.append(frame)
        if label == 'rn':
            label = 0
        if label == 'rr':
            label = 1
        return torch.stack(data), torch.tensor(label)
    
    
def collate_fn(batch):
    sequences = [x[0] for x in batch]
    labels = [x[1] for x in batch]
    seq_len = [len(s) for s in sequences]
    # print(sequences[0].shape)
    sequences = pad_sequence(sequences, batch_first=True)
    # torch.stack(sequences)
    labels = torch.tensor(labels)
    return sequences, labels, seq_len


def make_train_dataloader(data_path, window = 30, step = 1):
    dataset = Dataset(data_path, window, step, True)
    train_size = int(len(dataset) * train_size_rate)
    valid_size = len(dataset) - train_size
    train_dataset, valid_dataset = torch.utils.data.random_split(dataset, [train_size, valid_size])
    train_loader = DataLoader(train_dataset, batch_size=train_batch_size, shuffle=True, num_workers=num_workers, collate_fn= collate_fn)
    valid_loader = DataLoader(valid_dataset, batch_size=train_batch_size, shuffle=True, num_workers=num_workers, collate_fn= collate_fn)
    return train_loader, valid_loader



