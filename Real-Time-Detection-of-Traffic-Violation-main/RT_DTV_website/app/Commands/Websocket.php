<?php

namespace App\Commands;

use CodeIgniter\CLI\BaseCommand;
use CodeIgniter\CLI\CLI;

class Websocket extends BaseCommand
{
    protected $group = 'WebSocket';
    protected $name = 'websocket:start';
    protected $description = '啟動 WebSocket 伺服器';

    public function run(array $params)
    {
        $python_path = 'C:\Users\vicky\anaconda3\envs\pj11\python.exe'; // 這邊填入PYTHON環境執行黨
        $command =  $python_path . ' ' . FCPATH . 'python/car_track.py';  // 指向 Python 腳本
        $output = shell_exec($command);

        CLI::write("WebSocket 伺服器啟動: " . $output, 'green');

    }
}