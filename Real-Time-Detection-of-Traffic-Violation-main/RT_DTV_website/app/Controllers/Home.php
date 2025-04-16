<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use CodeIgniter\HTTP\ResponseInterface;
use App\Models\VideoModel;
use App\Models\RoadModel;

class Home extends BaseController
{
    public function index(): string
    {
        return view('home');
    }
}
