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

from model import *
from dataload import make_train_dataloader

#清空這隻程式的GPU(之後可以試試看)
#torch.cuda.empty_cache()
os.environ["CUDA_VISIBLE_DEVICES"] = "1,2,4,5,6"

#segnet中我們看的指標不是accuracy，而是miou，miou越接近1代表模型越準確
#這是因為accuracy是去看每一個像素有沒有被預測成功，但我們背景佔多數，所以不準

# training parameters
epochs = 5
learning_rate = 0.001
num_classes = 2 #背景也是一個class

image_shape = (3, 224, 224)

torch.cuda.set_device(0)
device = torch.device("cuda:0")

base_path = os.path.dirname(os.path.abspath(__file__))
weight_path = os.path.join(base_path, "weights", "weight.pth")
pre_weight_path = os.path.join(base_path, "weights", "pre_weight.pth")
image_path = os.path.join(base_path, "image", "train")
label_path = os.path.join(base_path, "label", "train")


#資料不平衡的權重，使用data_balance.py可以求得
CATE_WEIGHT = [0.5178204126629256, 14.528855825550663]
PRE_TRAINING = pre_weight_path

# Define network
model = SegNet(3, num_classes).cuda()
model.load_weights(PRE_TRAINING)
model = torch.nn.DataParallel(model, device_ids=[0,1,2,3]).cuda()


train_data = MyDataset(image_path, label_path)


train_loader, valid_loader = make_train_dataloader(train_data)
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)
criterion = nn.CrossEntropyLoss(weight=torch.from_numpy(np.array(CATE_WEIGHT)).float()).to(device)

# train
train_loss_list = list()
valid_loss_list = list()
train_accuracy_list = list()
valid_accuracy_list = list()
train_miou_list = list()
valid_miou_list = list()

best = 100
best_model_wts = copy.deepcopy(model.state_dict())

for epoch in range(epochs):
    print(f'\nEpoch: {epoch+1}/{epochs}')
    print('-' * len(f'Epoch: {epoch+1}/{epochs}'))
    train_loss, valid_loss = 0.0, 0.0
    train_correct, valid_correct = 0, 0
    train_accuracy, valid_accuracy = 0.0, 0.0
    train_pixels, valid_pixels = 0, 0
    train_miou = []
    valid_miou = []

    model.train()
    for data, target in tqdm(train_loader, desc="Training"):

        data, target = data.to(device), target.to(device)
        # forward + backward + optimize
        output  = model(data)
        _, preds = torch.max(output, 1)
        

        loss = criterion(output, target.long())
        optimizer.zero_grad()   # zero the parameter gradients
        loss.backward()
        optimizer.step()

        train_loss += loss.item() * data.size(0)
        train_correct += torch.sum(preds == target)
        train_pixels += target.numel()
        #計算miou
        for i in range(data.size(0)):  # 遍歷batch中的每個樣本
            pred = output[i]   
            label = target[i].cpu().numpy()
            pred = torch.squeeze(pred)
            pred = pred.argmax(dim=0).cpu().numpy()
            intersection = []
            union = []
            iou = 0.0
            for j in range(1, num_classes):
                intersection.append(np.sum((pred == j) & (label == j)))
                union.append(np.sum(pred == j) + np.sum(label == j) - intersection[j-1])
                iou += intersection[j-1]/union[j-1]
            train_miou.append(iou)      
                    
    train_loss /= len(train_loader.dataset)
    train_loss_list.append(train_loss)
    train_accuracy = float(train_correct) / train_pixels
    train_accuracy_list.append((train_accuracy))
    train_miou_list.append(np.mean(train_miou))

    model.eval()
    
    #valid
    with torch.no_grad():
        for data, target in tqdm(valid_loader, desc="Validation"):
            data, target = data.to(device), target.to(device)

            output = model(data)
            loss = criterion(output, target.long())
            loss = loss.cuda()
            _, preds = torch.max(output, 1)
            valid_loss += loss.item() * data.size(0)
            valid_correct += torch.sum(preds == target)
            valid_pixels += target.numel()
            #計算miou
            for i in range(data.size(0)): 
                pred = output[i]
                label = target[i].cpu().numpy()
                pred = torch.squeeze(pred)
                pred = pred.argmax(dim=0).cpu().numpy()
                intersection = []
                union = []
                iou = 0.0
                for j in range(1, num_classes):
                    intersection.append(np.sum((pred == j) & (label == j)))
                    union.append(np.sum(pred == j) + np.sum(label == j) - intersection[j-1])
                    iou += intersection[j-1]/union[j-1]
                valid_miou.append(iou)
             
               
        valid_loss /= len(valid_loader.dataset)
        valid_loss_list.append(valid_loss)
        valid_accuracy = float(valid_correct) / valid_pixels
        valid_accuracy_list.append((valid_accuracy))
        valid_miou_list.append(np.mean(valid_miou))
        
        
    # print loss and accuracy in one epoch
    print(f'Training loss: {train_loss:.4f}, validation loss: {valid_loss:.4f}')
    print(f'Training accuracy: {train_accuracy:.4f}, validation accuracy: {valid_accuracy:.4f}')
    print(f'Training miou: {np.mean(train_miou):.4f}, validation miou: {np.mean(valid_miou):.4f}')

    # record best weight so far
    if valid_loss < best :
        best = valid_loss
        best_model_wts = copy.deepcopy(model.state_dict())
# save the best weight
torch.save(best_model_wts, weight_path)

# plot the loss curve for training and validation
print("\nFinished Training")
pd.DataFrame({
    "train-loss": train_loss_list,
    "valid-loss": valid_loss_list
}).plot()
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.xlim(1,epoch+1)
plt.xlabel("Epoch"),plt.ylabel("Loss")
plt.savefig(os.path.join(base_path, "result", "Loss_curve"))

# plot the accuracy curve for training and validation
pd.DataFrame({
    "train-accuracy": train_accuracy_list,
    "valid-accuracy": valid_accuracy_list
}).plot()
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.xlim(1,epoch+1)
plt.xlabel("Epoch"),plt.ylabel("Accuracy")
plt.savefig(os.path.join(base_path, "result", "Training_accuracy"))

# plot the miou curve for training and validation
pd.DataFrame({
    "train-miou": train_miou_list,
    "valid-miou": valid_miou_list
}).plot()
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.xlim(1,epoch+1)
plt.xlabel("Epoch"),plt.ylabel("IOU")
plt.savefig(os.path.join(base_path, "result", "mIOU"))






