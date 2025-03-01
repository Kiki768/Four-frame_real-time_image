import cv2 as cv
import numpy as np
import os 

# for 資料不平衡

base_path = os.path.dirname(os.path.abspath(__file__))
label_path = os.path.join(base_path, "label", "train")
path_list = os.listdir(label_path)
CLASS_NUM = 2
SUM = [[] for i in range(CLASS_NUM)]
SUM_ = 0

#紀錄每張label背景和遮罩的像素數
for path in path_list:
    input_path = os.path.join(base_path, "label", "train", path)
    img = cv.imread(input_path, 0) #灰度
    img_np = np.array(img)
    SUM[0].append(np.sum((img_np == 0)))#背景
    SUM[1].append(np.sum((img_np != 0)))#遮罩

for index, iter in enumerate(SUM):
    print("類別{}的数量：".format(index), sum(iter))

#所有像素數量
for iter in SUM:
    SUM_ += sum(iter)

median = 1/CLASS_NUM

for index, iter in enumerate(SUM):
    print("weight_{}:".format(index), median/(sum(iter)/SUM_))