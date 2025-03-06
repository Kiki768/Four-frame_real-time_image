<?php

namespace App\Controllers;

class LiveFeedController extends BaseController
{
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
}
