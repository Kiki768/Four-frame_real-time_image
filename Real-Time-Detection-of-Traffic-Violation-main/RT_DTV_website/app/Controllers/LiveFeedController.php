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
    // 先記錄請求到達
    log_message('info', 'start_detection method called');

    // 資料夾名稱設定為 'error'
    $video_name = 'C:\\Users\\vicky\\Desktop\\PJ74\\Real-Time-Detection-of-Traffic-Violation-main\\RT_DTV_website\\public\\python\\error';  
    $python = 'C:\\Users\\vicky\\anaconda3\\envs\\pj11\\python.exe';
    $script = 'C:\\Users\\vicky\\Desktop\\PJ74\\Real-Time-Detection-of-Traffic-Violation-main\\RT_DTV_website\\public\\python\\main.py';
    $workingDir = 'C:\\Users\\vicky\\Desktop\\PJ74\\Real-Time-Detection-of-Traffic-Violation-main\\RT_DTV_website\\public\\python';

    // 設定 log 文件儲存路徑
    $logDir = WRITEPATH . 'logs';
    if (!is_dir($logDir)) {
        mkdir($logDir, 0775, true);
    }

    $taskId  = uniqid('task_');
    $logFile = $logDir . DIRECTORY_SEPARATOR . $taskId . '.log';
    $errFile = $logDir . DIRECTORY_SEPARATOR . $taskId . '.err.log';

    $cmd = 'cmd /c "cd /d ' . escapeshellarg($workingDir) . ' && '
     . 'start "" /b '
     . escapeshellarg($python) . ' '
     . escapeshellarg($script) . ' --name ' . escapeshellarg($video_name) . ' '
     . '1>>' . escapeshellarg($logFile) . ' 2>>' . escapeshellarg($errFile) . '"';

// 非阻塞
pclose(popen($cmd, 'r'));

return $this->response->setJSON([
  'success' => true,
  'taskId'  => $taskId,
  'logFile' => basename($logFile),
  'errFile' => basename($errFile),
]);
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
