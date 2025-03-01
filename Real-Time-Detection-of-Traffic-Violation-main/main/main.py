from ultralytics import YOLO
import os
import time
import pandas as pd
import argparse
from car_track import car_track

def make_sub_dir(output_folder, save_paths):
    #依照save去創建turn_info_folder, car_img_folder, light_info_folder
    for name, flag in save_paths:
        if flag:
            os.makedirs(os.path.join(output_folder, name), exist_ok=True)
    #創建violation(存違規照片的目錄)
    os.makedirs(os.path.join(output_folder, "violation"), exist_ok=True)
    #刪除上一次偵測的csv檔案
    turn_csv_path = os.path.join(output_folder, "turn_info", "turn_predict.csv")
    if os.path.exists(turn_csv_path):
        os.remove(turn_csv_path)
    light_csv_path = os.path.join(output_folder, "light_info", "light_predict.csv")
    if os.path.exists(light_csv_path):
        os.remove(light_csv_path)

def parse_save(value):
    try:
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
    
def parse_turn(value):
    try:
        if value not in ['n', 'l', 'r']:
            raise ValueError("Turn value must be one of 'n', 'l', 'r'")
        
        return value
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid value for --turn: {e}")
    

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    '--name', 
    type=str, 
    default="demo_video", 
    help="Name of the folder containing the video files"
)
parser.add_argument(
    '--save', 
    type=parse_save, 
    default="1,0,1,0", 
    help="A comma-separated list of 4 integers to specify saving options:\n - The 1st number: Save YOLO output video (1: yes, 0: no)\n- The 2nd number: Save vehicle images (1: yes, 0: no)\n- The 3rd number: Save vehicle trajectories(image) and turn model predictions(csv file) (1: yes, 0: no)\n- The 4th number: Save wave graphs (1: yes, 0: no)\nExample: --save 1,0,1,0"
)

parser.add_argument(
    '--turn', 
    type=parse_turn, 
    default="n", 
    help="Use 'l' for left turn, 'r' for right turn, default is 'n' if not specified."
    #左轉路口為l,右轉路口為r,不指定則為n
)


args = parser.parse_args()


start_time = time.time()
input_folder = args.name
#檢查input_folder是否存在
try:
    if not os.path.exists(input_folder):
        raise ValueError(f"The folder {input_folder} doesn't exist.")
except ValueError as e:
    raise argparse.ArgumentTypeError(f"Invalid value for --name: {e}")

#創建output目錄
current_dir =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_folder_name = os.path.basename(input_folder)
all_output_folder = os.path.join(current_dir, "output", input_folder_name) #存所有結果的資料夾
os.makedirs(all_output_folder, exist_ok=True)
save_paths = [
    ("carimg", args.save[1]),
    ("turn_info", args.save[2]),
    ("light_info", args.save[3]),
]



for filename in os.listdir(input_folder):
    if filename.endswith(".mp4"):
        #創建目錄
        output_folder = os.path.join(all_output_folder,filename[:-4])
        os.makedirs(output_folder, exist_ok=True)
        make_sub_dir(output_folder, save_paths)
        #合成video_path
        video_path = os.path.join(input_folder, filename)
        car_track(video_path, output_folder, args.save, args.turn)
        

        



end_time = time.time()
duration_seconds = end_time - start_time

print("Time：", duration_seconds, "秒")  