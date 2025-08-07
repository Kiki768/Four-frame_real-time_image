<?php

namespace App\Controllers;


class LiveFeedController extends BaseController
{

    public function violation_history()
    {
        return view('history/history');
    }

    // 🔥 讓 http://localhost:8080/LiveFeedController 顯示前端畫面
    public function index()
    {
        return view('live/index'); // 載入 Views/live/index.php
    }

    // 🔥 提供影片 API (http://localhost:8080/LiveFeedController/api)
    public function api()
    {
        $folders = ['folder1', 'folder2', 'folder3', 'folder4'];
        $basePath = FCPATH . 'videos/';

        $videoData = [];

        foreach ($folders as $folder) {
            $folderPath = $basePath . $folder;
            if (is_dir($folderPath)) {
                $files = array_diff(scandir($folderPath), ['.', '..']);
                $videoFiles = [];

                foreach ($files as $file) {
                    if (preg_match('/\.(mp4|webm|ogg)$/i', $file)) {
                        $videoFiles[] = site_url('videos/' . $folder . '/' . $file);
                    }
                }

                usort($videoFiles, 'strnatcasecmp');

                $videoData[$folder] = $videoFiles;
            }
        }

        return $this->response->setJSON($videoData);
    }

    public function start_detection()
    {
        try {
            $pythonPath = 'C:\\Users\\vicky\\anaconda3\\envs\\pj11\\python.exe';
            $scriptPath = realpath(FCPATH . '../public/python/car_track_website.py'); 


            if (!$scriptPath) {
                throw new \Exception('找不到 Python 腳本 car_track_website.py');
            }

            // 設定 log 輸出路徑
            $logPath = realpath(FCPATH . '../writable/logs/car_track_log.txt');
            $command = "start /B \"\" \"$pythonPath\" \"$scriptPath\" > \"$logPath\" 2>&1";  // 在背景執行並輸出 log

            // 使用 shell_exec 執行指令
            shell_exec("cmd /c $command");

            // 回傳成功訊息
            return $this->response->setJSON([
                'success' => true,
                'message' => 'car_track_website.py 已在背景啟動',
                'command' => $command
            ]);

        } catch (\Throwable $e) {
            // 如果有錯誤，回傳錯誤訊息
            return $this->response->setJSON([
                'success' => false,
                'error' => $e->getMessage()
            ]);
        }
    }

    public function get_history()
    {
        $logPath = WRITEPATH . 'logs/violation_history.csv';
        $history = [];

        if (file_exists($logPath)) {
            $rows = file($logPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
            foreach ($rows as $row) {
                $parts = str_getcsv($row);
                if (count($parts) === 3) {
                    $history[] = [
                        'video_name' => $parts[0],
                        'action' => $parts[1],
                        'timestamp' => $parts[2],
                    ];
                }
            }
        }

        return $this->response->setJSON($history);
    }


}

