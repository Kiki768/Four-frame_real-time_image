import torch
import torch.nn as nn
from PIL import Image
import cv2 as cv
from torchvision import transforms


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride = 1, downsample = None):
        super(ResidualBlock, self).__init__()#呼叫父類別的constructor
        #兩個捲積層(3*3,padding = 1)，第二層的stride = 1
        self.conv1 = nn.Sequential(
                        nn.Conv2d(in_channels, out_channels, kernel_size = 3, stride = stride, padding = 1),
                        nn.BatchNorm2d(out_channels),
                        nn.ReLU())
        self.conv2 = nn.Sequential(
                        nn.Conv2d(out_channels, out_channels, kernel_size = 3, stride = 1, padding = 1),
                        nn.BatchNorm2d(out_channels))
        self.downsample = downsample
        self.relu = nn.ReLU()
        self.out_channels = out_channels
        
    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.conv2(out)
        if self.downsample:
            residual = self.downsample(x)
        out += residual
        out = self.relu(out)
        return out
    

class ResNet(nn.Module):
    # block 為 residualBlock
    # num_classes 記得改成我們的類別
    def __init__(self, block, layers, num_classes = 10):
        super(ResNet, self).__init__()
        self.inplanes = 64
        #第一層
        self.conv1 = nn.Sequential(
                        nn.Conv2d(3, 64, kernel_size = 7, stride = 2, padding = 3),
                        nn.BatchNorm2d(64),
                        nn.ReLU())
        self.maxpool = nn.MaxPool2d(kernel_size = 3, stride = 2, padding = 1)
        #每一層可以選擇要使用的block(目前只有residualBlock)
        self.layer0 = self._make_layer(block, 64, layers[0], stride = 1)
        self.layer1 = self._make_layer(block, 128, layers[1], stride = 2)
        self.layer2 = self._make_layer(block, 256, layers[2], stride = 2)
        self.layer3 = self._make_layer(block, 512, layers[3], stride = 2)
        self.avgpool = nn.AvgPool2d(7, stride=1)
        self.fc = nn.Linear(512, num_classes)
    
    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes:
            
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes, kernel_size=1, stride=stride),
                nn.BatchNorm2d(planes),
            )
        layers = []
        
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)
    
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.maxpool(x)
        x = self.layer0(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)

        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x

#dataloader

# 一個影像的預處理管道，transforms.Compose 將多個轉換操作組合起來，生成適合深度學習模型輸入的格式
test_transforms = transforms.Compose([
    # 影像調整為指定大小 (224, 224)
    transforms.Resize((224,224)),
    # 將影像從 PIL 格式轉換為 PyTorch 的 Tensor 格式
    transforms.ToTensor(),
    #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 將一組影像，轉換為 RGB、轉為 PIL、調整大小並轉為 PyTorch 的 Tensor
# 組合成一組轉換後的影像的 list 後，再轉換為 PyTorch 的 DataLoader 格式，供模型進行推論測試
# 設定每批次取出 4 張影像進行處理
def make_test_dataloader(imgs):
    # images 用於儲存轉換後的影像
    images = []
    for item in imgs:
        # 使用 OpenCV 的 cv.cvtColor 將影像從 BGR 格式轉換為 RGB 格式。
        # 再使用 PIL 的 Image.fromarray 方法將陣列轉換為 PIL 影像格式 
        img = Image.fromarray(cv.cvtColor(item, cv.COLOR_BGR2RGB))
        # 調整影像大小，並轉換影像為 PyTorch 的 Tensor 格式
        img = test_transforms(img)
        # 將轉換後的影像加入到 images 這個 list 裡面
        images.append(img)
    # 將 images 列表中的 Tensor 格式影像堆疊成一個新的 PyTorch Tensor (testData)
    testData = torch.stack(images)
    # 使用 PyTorch 的 DataLoader 將 testData 包裝成批次的資料載入器 (test_loader)
    # 指定 batch_size=4，表示每次取出 4 張影像進行處理。
    test_loader = torch.utils.data.DataLoader(dataset=testData, batch_size=4)
    # print('test_loader:', len(test_loader))
    return test_loader




