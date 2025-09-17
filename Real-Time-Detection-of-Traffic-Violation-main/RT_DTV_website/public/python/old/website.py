from ultralytics import YOLO
import os
import time
import argparse
import asyncio
import websockets
import json
from car_track_website import car_track

# 這個檔案是網頁用
WEBSOCKET_PORT = 6789
base_path = os.getcwd()  # 獲取當前工作目錄
auto = -1                # 自動偵測或手動執行

async def website(websocket):    
    while True:
        
        # 等待來自前端的啟動訊號
        print("等待前端開始播放訊號...")
        message = await websocket.recv()
        data = json.loads(message)
        print(data)
        if (data["action"] != "start") and (data["action"] != "start_auto"):
            print("收到無效的啟動訊號")
            continue

        print("接收到啟動訊號，開始處理影片...")

        #處理收到的啟動訊號
        split_data = data["path"].split('/')
        if data["action"] == "start":
            input_folder = os.path.join(base_path, split_data[-2])
            auto = 0
        else:
            input_folder = os.path.join(base_path, split_data[-3], split_data[-2])
            auto = 1
        video_path = os.path.join(base_path, split_data[-3], split_data[-2], split_data[-1])
        filename = split_data[-1]
        print(input_folder, video_path)

        
        start_time = time.time()

        #output_folder
        output_folder = os.path.join(base_path, "only_one_screen_result")
        video_output_folder = output_folder + '/videoOutput'
        turn_info_folder = output_folder + '/turn_info'
        light_info_folder = output_folder + '/light_info'
        carimg_folder = output_folder + '/carimg'
        result_folder = output_folder + '/result'



        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if not os.path.exists(video_output_folder):
            os.makedirs(video_output_folder)

        if not os.path.exists(turn_info_folder):
            os.makedirs(turn_info_folder)

        if not os.path.exists(light_info_folder):
            os.makedirs(light_info_folder)

        if not os.path.exists(carimg_folder):
            os.makedirs(carimg_folder)

        if not os.path.exists(result_folder):
            os.makedirs(result_folder)




        if filename.endswith(".mp4"):
            #合成video_path
            video_path = os.path.join(input_folder, filename)
            await car_track(video_path, output_folder, websocket, auto)


        end_time = time.time()
        duration_seconds = end_time - start_time

        print("Time：", duration_seconds, "秒")  


async def main():

    server = await websockets.serve(website, "0.0.0.0", WEBSOCKET_PORT)
    print(f"WebSocket Server 正在啟動，監聽埠號 {WEBSOCKET_PORT}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
