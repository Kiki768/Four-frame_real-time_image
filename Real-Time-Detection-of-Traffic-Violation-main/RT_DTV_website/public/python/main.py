from ultralytics import YOLO
import os
import time
import pandas as pd
import argparse  # 用於解析 command line 引數
from car_track import car_track
import shutil

# import torch
# print(torch.cuda.is_available())  # 如果是 False，表示 PyTorch 沒有 CUDA 支援
# print(torch.version.cuda)  # 檢查 CUDA 版本
# print(torch.backends.cudnn.enabled)  # 檢查 cuDNN 是否可用

# os._exit(0)

def make_sub_dir(output_folder, save_paths):
    #依照 --save 去創建 turn_info_folder, car_img_folder, light_info_folder
    for name, flag in save_paths:
        if flag:
            os.makedirs(os.path.join(output_folder, name), exist_ok=True)
    # 創建violation(存違規照片的目錄)
    os.makedirs(os.path.join(output_folder, "violation"), exist_ok=True)
    # 刪除上一次偵測的csv檔案
    # os.path.join(path, *paths) 聰明地連接一個或多個路徑段，回傳值是 path 和 *paths 的所有成員的串聯
    turn_csv_path = os.path.join(output_folder, "turn_info", "turn_predict.csv")
    if os.path.exists(turn_csv_path):
        os.remove(turn_csv_path)
    light_csv_path = os.path.join(output_folder, "light_info", "light_predict.csv")
    if os.path.exists(light_csv_path):
        os.remove(light_csv_path)


# parse_save 是用來定義 argparse 模組中 --save 的 type 參數，用於解析和驗證命令行參數的輸入值。
def parse_save(value):
    try:
        # 例如，"1,0,1,0" 轉換為 [1, 0, 1, 0]
        numbers = [int(x) for x in value.split(",")]
        # 檢查長度是否為 4
        if len(numbers) != 4:
            raise ValueError("The list must contain exactly 4 numbers.")
        # 檢查每個數字是否在 [0, 1] 範圍內
        if any(n < 0 or n > 1 for n in numbers):
            raise ValueError("Each number must be in the range [0, 1].")
        
        return numbers
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid value for --save: {e}")


# parse_turn 是用來定義 argparse 模組中 --turn 的 type 參數，用於解析和驗證命令行參數的輸入值。
def parse_turn(value):
    try:
        if value not in ['n', 'l', 'r']:
            raise ValueError("Turn value must be one of 'n', 'l', 'r'")
        
        return value
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid value for --turn: {e}")
    
# ArgumentParser 用來定義和處理 command line 引數。它會幫忙從 command line 中獲取參數，並自動生成幫助訊息。
# formatter_class 是 ArgumentParser 的一個選項，用來控制輸出的幫助訊息的格式。
# RawTextHelpFormatter 是指定輸出的幫助訊息 (help) 遵循原始格式 (遵循原始字串內的空格、換行等排版)
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

# 定義引數 --name，type 代表之後接的引數是字串，會設定 args.name 的值，如果使用 --name 則會將 args.name 的值預設為 demo_video
parser.add_argument(
    '--name', 
    type=str, 
    default="demo_video", 
    help="Name of the folder containing the video files"
)
parser.add_argument(
    '--save', 
    type=parse_save, 
    default="0,0,0,0", 
    help="A comma-separated list of 4 integers to specify saving options:\n - \
    The 1st number: Save YOLO output video (1: yes, 0: no)\n-\
    The 2nd number: Save vehicle images (1: yes, 0: no)\n-\
    The 3rd number: Save vehicle trajectories(image) and turn model predictions(csv file) (1: yes, 0: no)\n-\
    The 4th number: Save wave graphs (1: yes, 0: no)\n\
    Example: --save 1,0,1,0"
)

parser.add_argument(
    '--turn', 
    type=parse_turn, 
    default="n", 
    help="Use 'l' for left turn, 'r' for right turn, default is 'n' if not specified."
    #左轉路口為l,右轉路口為r,不指定則為n
)

# 解析 command line 參數並將結果存儲到 args 中
args = parser.parse_args()

# 獲取當前時間，記錄為程式開始執行的時間
start_time = time.time()

# 取得從命令行參數 --name 指定的輸入資料夾名稱
input_folder = args.name

#檢查input_folder是否存在
try:
    # 如果資料夾不存在，則拋出 ValueError 異常
    if not os.path.exists(input_folder):
        # raise 拋出例外，引發 ValueError，並包含此字串
        raise ValueError(f"The folder {input_folder} doesn't exist.")
except ValueError as e:
    # 再次拋出例外，用 argparse 的例外
    raise argparse.ArgumentTypeError(f"Invalid value for --name: {e}")

# 創建output目錄
# 當前檔案的資料夾的上層資料夾，用 __file__ 取得絕對路徑，而 dirname 取得上層的資料夾
current_dir =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 取得輸入資料夾的名稱（從輸入資料夾的完整路徑中提取最後的資料夾名稱）
input_folder_name = os.path.basename(input_folder)

# 在目前目錄下建立存放所有結果的資料夾路徑，路徑結構為 "current_dir/output/input_folder_name"
all_output_folder = os.path.join(current_dir, "output", input_folder_name) # 存所有結果的資料夾

# all_output_folder = os.path.join("E:/College_Project", "output", input_folder_name) # 存所有結果的資料夾

# 建立存放結果的資料夾，若資料夾已存在則不拋出例外
os.makedirs(all_output_folder, exist_ok=True)

# 定義存放各類結果的子資料夾名稱與相關參數的對應關係
# save_paths 是一個列表，其中每個元素是一個包含資料夾名稱和對應參數的元組
save_paths = [
    ("carimg", args.save[1]),
    ("turn_info", args.save[2]),
    ("light_info", args.save[3]),
]



for filename in os.listdir(input_folder):
    # 檢查檔案是否以 ".mp4" 結尾
    if filename.endswith(".mp4"):
        # 創建目錄
        # 輸出目錄的路徑為 "all_output_folder/影片資料夾名稱/影片檔案名稱（去掉.mp4的部分）"
        output_folder = os.path.join(all_output_folder,filename[:-4])
        # os.makedirs(output_folder, exist_ok=True)
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)  # 刪除已存在的資料夾及其內容
        os.makedirs(output_folder)
        # 依據 --save 參數的設定，建立相應的子資料夾
        make_sub_dir(output_folder, save_paths)
        # 合成video_path
        video_path = os.path.join(input_folder, filename)
        # 引用在 main/car_track.py 內的 car_track 函數
        car_track(video_path, output_folder, args.save, args.turn)
        

        



end_time = time.time()
duration_seconds = end_time - start_time

# print("Time：", duration_seconds, "秒")  
print("Time: ", duration_seconds, " seconds")  