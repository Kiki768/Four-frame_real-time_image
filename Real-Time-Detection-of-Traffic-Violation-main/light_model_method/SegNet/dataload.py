import numpy as np
import torch
import torch.nn as nn
from torchvision import datasets
from torchvision import transforms
from torch.utils.data.sampler import SubsetRandomSampler
import os
from PIL import Image
import torch
from torchvision import datasets
from torchvision import transforms
from torch.utils.data import DataLoader
import cv2 as cv

train_batch_size = 16
test_batch_size = 16
num_workers = 0
train_size_rate = 0.8 

# Make dataset and dataloader(Don't need to adjust)
def make_train_dataloader(dataset):

    train_size = int(len(dataset) * train_size_rate)
    valid_size = len(dataset) - train_size
    train_dataset, valid_dataset = torch.utils.data.random_split(dataset, [train_size, valid_size])
    
    train_loader = DataLoader(train_dataset, batch_size=train_batch_size, shuffle=True, num_workers=num_workers)
    valid_loader = DataLoader(valid_dataset, batch_size=train_batch_size, shuffle=True, num_workers=num_workers)

    return train_loader, valid_loader


def load_test_data(data_path, transform=None):
    imgs = []
    img_srcs = []
    img_names = []
    path_list = os.listdir(data_path)
    path_list.sort()
    for file_name in path_list:
        img_path = os.path.join(data_path, file_name)
        img_names.append(file_name)
        
        img = cv.imread(img_path)
        img = cv.resize(img, (224, 224))
        
        img_src = img
        img_src = cv.cvtColor(img_src, cv.COLOR_BGR2RGB)
        img_srcs.append(img_src)
        
        img = img/255.0 
        img = torch.Tensor(img)
        img = img.permute(2, 0, 1)  
        if transform:
            img = transform(img)
        imgs.append(img)
    return [imgs, img_srcs, img_names]




