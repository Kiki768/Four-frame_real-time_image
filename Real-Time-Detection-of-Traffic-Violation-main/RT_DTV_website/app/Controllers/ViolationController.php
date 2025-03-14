<?php

namespace App\Controllers;

class ViolationController extends BaseController
{
    public function index()
    {
        return view('violation/index'); // 導向違規管理頁面
    }
}
