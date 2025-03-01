<?php

namespace App\Controllers;

class LiveFeedController extends BaseController
{
    public function index()
    {
        $videoPath = base_url('videos'); // 指向public/videos
        $files = glob(FCPATH . 'videos/*.mp4');
        $videos = [];

        foreach($files as $file)
        {
            $videos[] = $videoPath . '/' . basename($file);
        }
        return view('live/index', ['videos' => $videos]); // 讓它載入 live/index.php
    }
}


