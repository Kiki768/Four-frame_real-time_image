import torch
import os

threshold = 0.15

draw_bbox = 0
test_max_transformer_debug_msg = 0

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# epochs = 50
epochs = 10
learning_rate = 1e-4
betas = (0.9, 0.999) 
# num_layers = 5
num_layers = 4
classnum = 2 
# nhead = 8
nhead = 16
dropout_rate = 0.1
open_conf_matrix = 0
train_batch_size = 64
test_batch_size = 1
window_size = 8
# step = 2
step = 1
num_workers = 0
train_size_rate = 0.8

base_path = os.path.dirname(os.path.abspath(__file__))
# train_data_path = os.path.join(base_path, "data", "train")
train_data_path = os.path.join(base_path, "light_position", "train")
# train_label_path = os.path.join(base_path, "label")
train_label_path = os.path.join(base_path, "label_yolo")
weight_path = os.path.expanduser("weight/transformer_yolo_weight.pth")
# weight_path = os.path.join(base_path, "weights", "20250527_yolo", "weight.pth")
# weight_path = os.path.join(base_path, "weights", "weight.pth")
file_path = os.path.join(base_path, "result", "training_log.csv")
xlsx_path = os.path.join(base_path, "總標記資料集.xlsx")