import argparse
import datetime
import logging
import sys
from pathlib import Path
import numpy as np
from tqdm import tqdm
import cv2 as cv
import os
import copy
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import torch
from torch.autograd import Variable
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
from torchvision import transforms
import torch.nn as nn
from CNNLSTM import CNNLSTM
from dataloader import *


image_shape = (3, 224, 224)
num_classes = 2
latent_dim =  512
lstm_layers =  5
hidden_dim =  1024
bidirectional =  True
attention = True

window = 30
step = 1

epochs = 30
learning_rate = 0.0001


base_path = os.path.dirname(os.path.abspath(__file__))
weight_path = os.path.join(base_path, "weights", "weight.pth")
segnet_weight_path = os.path.join(base_path, "weights", "segnet_weight.pth")
data_path = os.path.join(base_path, "data")



torch.cuda.set_device(0)
device = torch.device("cuda:0")

model = CNNLSTM(
    num_classes = num_classes,
    latent_dim = latent_dim,
    lstm_layers = lstm_layers,
    hidden_dim = hidden_dim,
    bidirectional = bidirectional,
    attention = attention,
).cuda()

model.load_weights(segnet_weight_path)


optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
criterion = nn.CrossEntropyLoss().to(device)


train_loader, valid_loader = make_train_dataloader(data_path, window, step)


# train
train_loss_list = list()
valid_loss_list = list()
train_accuracy_list = list()
valid_accuracy_list = list()
best = 100
best_model_wts = copy.deepcopy(model.state_dict())


for epoch in range(epochs):
    print(f'\nEpoch: {epoch+1}/{epochs}')
    print('-' * len(f'Epoch: {epoch+1}/{epochs}'))
    train_loss, valid_loss = 0.0, 0.0
    train_correct, valid_correct = 0, 0
    train_accuracy, valid_accuracy = 0.0, 0.0

    model.train()
    for data, target, true_len in tqdm(train_loader, desc="Training"):
        
        # print(data.shape)
        data, target = data.to(device), target.to(device)
        # Reset LSTM hidden state
        model.lstm.reset_hidden_state()

        # forward + backward + optimize
        output  = model(data, true_len)
        _, preds = torch.max(output.data, 1)

        loss = criterion(output, target)
        optimizer.zero_grad()   # zero the parameter gradients
        loss.backward()
        optimizer.step()

        train_loss += loss.item() * data.size(0)
        train_correct += torch.sum(preds == target.data)
    train_loss /= len(train_loader.dataset)
    train_loss_list.append(train_loss)
    train_accuracy = float(train_correct) / len(train_loader.dataset)
    train_accuracy_list.append((train_accuracy))


    model.eval()
    with torch.no_grad():
        for data, target, true_len in tqdm(valid_loader, desc="Validation"):
            data, target = data.to(device), target.to(device)

            output = model(data, true_len)
            loss = criterion(output, target)
            _, preds = torch.max(output.data, 1)
            # print(preds, target)
            valid_loss += loss.item() * data.size(0)
            valid_correct += torch.sum(preds == target.data)
        valid_loss /= len(valid_loader.dataset)
        valid_loss_list.append(valid_loss)
        valid_accuracy = float(valid_correct) / len(valid_loader.dataset)
        valid_accuracy_list.append((valid_accuracy))
    # print loss and accuracy in one epoch
    print(f'Training loss: {train_loss:.4f}, validation loss: {valid_loss:.4f}')
    print(f'Training accuracy: {train_accuracy:.4f}, validation accuracy: {valid_accuracy:.4f}')

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