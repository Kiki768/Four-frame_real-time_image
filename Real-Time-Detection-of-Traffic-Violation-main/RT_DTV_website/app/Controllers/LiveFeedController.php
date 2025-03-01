<?php

namespace App\Controllers;

class LiveFeedController extends BaseController
{
    public function index()
    {
        return view('live/index'); // 讓它載入 live/index.php
    }
}


