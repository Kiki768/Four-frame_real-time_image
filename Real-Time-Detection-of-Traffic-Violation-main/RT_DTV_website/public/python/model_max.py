# 定義了一個名為 MyModel 的深度學習模型，結合了卷積神經網絡（CNN）和 Transformer 架構。

import numpy as np
import torch # PyTorch 核心庫，用於張量操作和神經網絡構建
import torch.nn.functional as F
import torch.nn as nn # 神經網絡模塊，如層、損失函數等
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence
from torchvision import datasets # 用於圖像資料集和預處理
from torchvision import models
from torchvision import transforms
from torch.utils.data.sampler import SubsetRandomSampler
from torchsummary import summary # 用於印出模型結構摘要
import os
import sys
import math

from ResNet_max import ResNet, ResidualBlock # 從 ResNet-max.py 文件中導入自定義的 ResNet 模型和殘差塊（ResidualBlock）。

import config_max

device = torch.device('cuda:0') # 將模型運行的設備設置為 GPU（如果可用）
# device = torch.device('cpu')

model_check = 0

open_conf_matrix = 0 # 我先把 conf_matrix 的部分都先關閉，將此參數設定為 1 能開啟

class PositionalEncoding(nn.Module):
    # d_embed：嵌入向量的維度（例如 512）
    # max_pos：能夠支援的最大序列長度，預設 5120
    def __init__(self, d_embed, max_pos=5120):
        super(PositionalEncoding, self).__init__()
        self.d_embed = d_embed
        self.max_pos = max_pos

        # pe (Position Encoding) 用來存放 (位置 × 維度) 的位置編碼值
        # 形狀為 (max_pos, d_embed)，內容全為零，例如：
        # [[0., 0., ..., 0.,] 共有 d_embed (512) 個 0
        #   ...
        # [0., 0., ..., 0.,] 共有 max_pos (5120) 列]
        pe = torch.zeros(max_pos, d_embed)
        # position 建立 [0, 1, 2, ..., max_pos-1] 的位置索引向量並擴展維度，形狀為 (max_pos, 1)
        # [[    0.],
        #  [    1.],
        #  [    2.],
        #  [    3.],
        #  ...
        #  [5120.]]
        position = torch.arange(0, max_pos, dtype=torch.float).unsqueeze(1)
        # torch.arange(0, d_embed, 2) 建立一個 tensor，從 0 開始，每隔 2 一個數字（只取偶數維度 0, 2, 4, ...），也就是公式的 2i
        # shape 是 (d_embed // 2)
        # .float() 將整數轉為浮點數
        # -math.log(10000.0) 為 -log_e(10000)，以 e 為底
        # 使用 torch.exp() 後，會變成 e^(2i*(-log_e(10000))/d_embed)
        # 負號移出後變成 1/e^(2i*log_e(10000)/d_embed)
        # log_e(10000) 取出後變成 1/10000^(2i/d_embed)
        div_term = torch.exp(torch.arange(0, d_embed, 2).float() * (-math.log(10000.0) / d_embed))
        # pe(pos, 2i) = sin(pos/10000^(2i/d_embed))
        # pe(pos, 2i+1) = cos(pos/10000^(2i/d_embed))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        # print(f"pe = {pe[:8]}")
        # print(f"pe.shape = {pe.shape}")
        # sys.exit(0)
        pe = pe.unsqueeze(0).transpose(0, 1)  # 調整形狀，變為 (max_pos, 1, d_embed)
        self.register_buffer('pe', pe)  # 註冊為 buffer，不會被訓練

    def forward(self, seq_len, bsz=None):
        # bsz: batch size
        # 這裡取出前 seq_len 長度的「最大長度 max_pos」的時間編碼矩陣
        pos_encoding = self.pe[:seq_len, :]
        if bsz is not None:
            # 把原本的單一序列位置編碼複製到每個batch上
            # expand(seq_len, bsz, embed_dim)
            # 變成一個三維張量：
            # 序列長度（seq_len）
            # batch數（bsz）
            # 每個位置的特徵維度（embed_dim）
            # -1 的意思是：「在這個維度上，保留原來的大小，不改變」。
            # pos_encoding 的 shape 是 (seq_len, d_model)
            # expand(seq_len, bsz, -1) 要求變成 (seq_len, bsz, d_model)
            # 這裡PyTorch會隱式地把原來的pos_encoding視為(seq_len, 1, d_model)，然後在batch_size維度上虛擬複製出 bsz 份。
            pos_encoding = pos_encoding.expand(seq_len, bsz, -1)
        return pos_encoding

class MyModel(nn.Module): # 定義一個繼承自 nn.Module 的類 MyModel，這是 PyTorch 中所有神經網絡模型的基類
    # 初始化函數
    def __init__(self, num_layers, output_size, nhead, dropout_rate=0.4, embed_dim=512, max_seq_len=5120):
        # num_layers: Transformer 編碼器的層數
        # output_size：輸出類別數。
        # nhead：Transformer 的多頭注意力機制（multi-head attention）的頭數量。
        # dropout_rate：Dropout 機率，默認為 0.4。
        super(MyModel, self).__init__()
        # 使用 ResNet 模型的卷積層作為特徵提取器，並移除最後一層（通常是全連接層 fc）
        # list(...children())：將 ResNet 的所有層轉換成一個列表
        encoder = list(ResNet(ResidualBlock, [3,4,6,3]).children())[:-1]
        self.encoder  = nn.Sequential(*encoder)
        hidden_size = 512
        
        # 定義一個線性層，將 ResNet 輸出的特徵維度映射到 Transformer 的輸入維度
        self.linear = nn.Linear(hidden_size,hidden_size)
        
        # 初始化 Positional Encoding
        self.pos_encoder = PositionalEncoding(embed_dim, max_seq_len)
        
        if open_conf_matrix:
            self.attention_weights = []  # 新增：存儲注意力權重
        
        transformer_encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_size, nhead=nhead, dropout=dropout_rate, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(transformer_encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(hidden_size, output_size)
        
        self.classify = nn.Linear(hidden_size, output_size)
    
    def forward(self, img_list, true_length=None):
        global model_check
        # 獲取輸入張量的形狀：batch_size 是批次大小，seq_len 是序列長度 (window_size)，
        # c 是通道數（例如 RGB 圖像的通道數為 3），h 和 w 分別是圖像的高度和寬度。
        batch_size, seq_len, c, h, w = img_list.shape
        
        if model_check:
            print('\n======== model_check ========\n')
            print(f'img_list shape: {img_list.shape}') # torch.Size([16, 8, 3, 224, 224])
            
        # 使用 view 方法將 img_list 的形狀從 (batch_size, seq_len, c, h, w) 轉換為 (batch_size * seq_len, c, h, w)
        # 這樣做的目的是將批次中的每個序列展開成獨立的圖像，以便可以將它們輸入到 ResNet 的卷積層中
         # 例如，如果 batch_size = 4 且 seq_len = 5，則展平後的形狀為 (20, c, h, w)，表示 20 張獨立的圖像
        img_list = img_list.view(batch_size*seq_len, c, h, w)
        
        if model_check:
            print(f'img_list.view shape: {img_list.shape}') # torch.Size([128, 3, 224, 224])
            
        # 通過 ResNet 的卷積層提取特徵
        # 獲得的資料形狀為 (batch_size * seq_len, hidden_size, 1, 1)
        img_list = self.encoder(img_list)
        
        if model_check:
            print(f'img_list encoder shape: {img_list.shape}') # torch.Size([128, 512, 1, 1])
            
        # 使用 view 方法將特徵張量的形狀從 (batch_size * seq_len, hidden_size) 轉換為 (batch_size, seq_len, hidden_size)
        # 這樣做的目的是將展平的圖像重新組合成原始的批次和序列結構，以便後續輸入到 Transformer 中。
        # 例如，如果 batch_size = 4 且 seq_len = 5，則形狀變為 (4, 5, hidden_size)。
        img_list = img_list.view(batch_size, seq_len, -1)
        
        if model_check:
            print(f'img_list encoder view shape: {img_list.shape}') # torch.Size([16, 8, 512])
            print(f'img_list[0,3] : {img_list[0,3]}\n')
            
        img_list = img_list + self.pos_encoder(seq_len, batch_size).transpose(0, 1)
        
        if model_check:
            print(f'self.pos_encoder(seq_len, batch_size).transpose(0, 1) shape: {self.pos_encoder(seq_len, batch_size).transpose(0, 1).shape}') # torch.Size([16, 8, 512])
            print(f'position_encoding[0,3] : {self.pos_encoder(5, 1).transpose(0, 1)[0,3]}')
            print(f'img_list[0,3] + position_encoding[0,3] : {img_list[0,3]}\n')
        
        # 將重組後的特徵張量輸入到 Transformer 編碼器（self.transformer_encoder）中。
        # Transformer 編碼器會對序列中的每個時間步進行處理
        transformer_output = self.transformer_encoder(img_list)
        
        if model_check:
            print(f'transformer_encoder_output shape: {transformer_output.shape}') # torch.Size([16, 8, 512])
        
        # 捕獲自注意力權重（假設使用 PyTorch 的 Transformer）
        if open_conf_matrix:
            for layer in self.transformer_encoder.layers:
                #self.attention_weights.append(layer.self_attn.attn)
                attn_output, attn_weights = layer.self_attn(
                transformer_output, transformer_output, transformer_output, need_weights=True)
                self.attention_weights.append(attn_weights)  # 存儲注意力權重
                transformer_output = attn_output  # 更新 transformer_output，作為下一層的輸入
        # 將 Transformer 的輸出通過全連接層（self.fc）進行分類。
        # 輸出形狀為 (batch_size, seq_len (window_size), output_size)，其中 output_size 是類別數
        output = self.fc(transformer_output)
        
        if model_check:
            print(f'fc_output shape: {output.shape}') # torch.Size([16, 8, 2])
            print('\n======== end of model_check ========\n')
            
        # global model_check
        # if model_check:
        #     print(f"\nmodel_forward_output_shape: {output.shape}")
        #     model_check = 0
        return output

 
    def load_weights(self, weights_path):
        '''
        # 加載預訓練的權重文件
        # torch.load 會將文件中的權重加載為一個字典，其中鍵是層的名稱，值是對應的權重張量
        weights = torch.load(weights_path)
        # print("Loaded weights layer names:")
        # print(*weights.keys(), sep="\n")
        # os._exit(0)
        # 每層的名稱存在 model_layer_name.txt 檔案內
        
        # 獲取當前模型 encoder 部分的狀態字典（state_dict）。
        # state_dict 是一個字典，包含了模型的所有可學習參數（權重和偏置）。
        model_weights = self.encoder.state_dict()
        
        # 刪除加載的權重字典中的 'fc.weight' 和 'fc.bias'。
        # 這是因為這些權重對應於全連接層（fc），而當前模型的結構可能與加載的權重不完全一致。
        # 如果保留這些權重，可能會導致形狀不匹配的錯誤。
        del weights['fc.weight']
        del weights['fc.bias']
        
        # 創建一個新的權重字典，用於存儲與當前模型 encoder 部分對應的權重
        new_weights = {}
        
        # 手動對應名稱
        # 遍歷加載的權重字典和當前模型 encoder 的狀態字典。
        # 這裡假設加載的權重和當前模型的層名稱是一一對應的。
        # key 是加載權重字典中的層名稱，new_key 是當前模型 encoder 的層名稱。
        for key, new_key in zip(weights.keys(), model_weights.keys()):
            new_weights[new_key] = weights[key]
        self.encoder.load_state_dict(new_weights)
        
        '''
        
        # 改成這樣，將權重完整的載入，再進行 test.py 或繼續訓練 (於 train.py 載入權重繼續訓練模型)
        
        state_dict = torch.load(weights_path, map_location=device)
        self.load_state_dict(state_dict)
