<?php

namespace App\Controllers;


class LiveFeedController extends BaseController
{

    public function violation_history()
    {
        return view('history/history');
    }

    public function index()
    {
        return view('live/index'); 
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
    // 資料夾名稱設定為 'error'
    $video_name = 'C:\\Users\\vicky\\Desktop\\PJ74\\Real-Time-Detection-of-Traffic-Violation-main\\RT_DTV_website\\public\\python\\error';  

    // 設定 main.py 的路徑
    $python = 'C:\\Users\\vicky\\anaconda3\\envs\\pj11\\python.exe';
    $script = 'C:\\Users\\vicky\\Desktop\\PJ74\\Real-Time-Detection-of-Traffic-Violation-main\\RT_DTV_website\\public\\python\\main.py';

    // 設定 log 文件儲存路徑
    $logDir = WRITEPATH . 'logs';
    if (!is_dir($logDir)) {
        mkdir($logDir, 0775, true);
    }
    $logFile = $logDir . DIRECTORY_SEPARATOR . uniqid('task_') . '.log';

    // 設定工作目錄為 main.py 所在的資料夾
    $workingDir = 'C:\\Users\\vicky\\Desktop\\PJ74\\Real-Time-Detection-of-Traffic-Violation-main\\RT_DTV_website\\public\\python';

    // 執行命令，並設置工作目錄
    $cmd = 'start "" ' .  escapeshellarg($python) . ' '
         . escapeshellarg($script) . ' '
         . '--name ' . escapeshellarg($video_name)  // 傳遞資料夾名稱 'error'
         . ' >> ' . escapeshellarg($logFile) . ' 2>&1 &';

    exec($cmd);

    return $this->response->setJSON(['taskId' => uniqid('task_')]);
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


    public function stop()
    {
        $storage = WRITEPATH.'detection';
        $pidFile = $storage.DIRECTORY_SEPARATOR.'detector.pid';
        $lockFile= $storage.DIRECTORY_SEPARATOR.'detector.lock';

        $pid = file_exists($pidFile) ? trim(@file_get_contents($pidFile)) : '';
        if ($pid !== '') {
            // /T 連同子程序一併殺掉（cmd.exe -> python.exe）
            exec('taskkill /PID '.((int)$pid).' /F /T');
        }
        @unlink($pidFile);
        @unlink($lockFile); // 以防卡住

        return $this->response->setJSON(['ok'=>true,'msg'=>'Stopped.'.($pid? " PID $pid":' (no pid)')]);
    }


    

}
