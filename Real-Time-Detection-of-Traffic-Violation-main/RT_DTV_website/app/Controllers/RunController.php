<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use CodeIgniter\HTTP\ResponseInterface;
use App\Models\VideoModel;
use App\Models\ViolatingCarModel;


class RunController extends BaseController
{
    public function index()
    {
        $videoModel = new VideoModel();
        $data = ["row" => $videoModel->where("is_run", 0)->findAll()];
        return view("runs/index", $data);
    }
    public function run()
    {
        $videoModel = new VideoModel();
        $videoname = $this->request->getVar('videoname');
        if($videoname == NULL)
        {
            return redirect()->back()->with('error', '未選擇影片');
        }
        $video_row = $videoModel->where('videoname', $videoname)->first();
        $video_path = $video_row['video_path'];
        return view("runs/show_video", ['video_path' => $video_path]);
    }
    public function run_program()
    {
        $videoModel = new VideoModel();
        $postData = $this->request->getPost();
        $video_name = explode("/", $postData["video_path"])[1];

        $video_row = $videoModel->where('videoname', $video_name)->first();
        
        # 檢查is_run(not)
        // $task_id = "task_670f11a663587";
        if($video_row['is_run'] == 0)
        {
            $data = ["is_run" => 1];
            $videoModel->update($video_row, $data);

            $task_id = uniqid('task_');
            exec("C:\Users\96285\anaconda3\\envs\ml\python.exe C:\CCCProject\ccc_method\ccc_for_website.py --name $video_name > tmp/$task_id.log");
            echo json_encode(['taskId' => $task_id]);
        }
        else
        {
            echo json_encode(['taskId' => "not run"]);
        }
    }
    public function check_result()
    {
        $task_id = $_GET['taskId'];
        // 检查输出文件是否存在
        $log_file = "tmp/$task_id.log";
        if (file_exists($log_file)) 
        {
            // 读取命令的输出
            $lines = file($log_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
            if (!empty($lines)) 
            {
                // 获取最后一行内容
                $last_line = array_pop($lines);
                if ($last_line == 'finish')
                {
                    $second_last_line = $lines[count($lines) - 1];
                    echo json_encode(['status' => 'finished', 'output' => $second_last_line]);
                }
                else
                {
                    echo json_encode(['status' => 'not finished', 'output' => $last_line]);
                }
            } 
            else 
            {
                // 文件存在，但没有内容
                echo json_encode(['status' => 'not finished']);
            }
            // 返回输出
        } 
        else 
        {
            // 输出文件不存在，说明命令仍在执行
            echo json_encode(['status' => 'not finished']);
        }
    }

    public function save_violating()
    {
        $videoModel = new VideoModel();
        $violatingCarModel = new ViolatingCarModel();



        $postData = $this->request->getPost();
        //print_r($postData);

        // $video_name = explode("/", "videos/20230110_083521_4417_A.mp4")[1];
        $video_name = explode("/", $postData["video_path"])[1];
        $video_row = $videoModel->where('videoname', $video_name)->first();
        // $output = "[11]";
        $output = $postData["output"];
        $violating_cars = explode(',', trim($output, '[]'));
        //print_r($violating_cars);
        for ($i = 0; $i < count($violating_cars); $i++) 
        {
            $count = $violatingCarModel->countAll() + 1;
            $license_plate = 'CCC-' . str_pad($count, 4, '0', STR_PAD_LEFT);
            $v_car = $violating_cars[$i];
            $source = "C:\CCCProject\ccc_method\output_for_website\\" . substr($video_name, 0, -4) . "\\result\\car" . $v_car .".jpg";
            $destination = "C:\CCCProject\RT_DTV\public\\violating_cars\\". $license_plate .".jpg";
            system("move $source $destination", $return_var);
            $img_path = "violating_cars/" . $license_plate .".jpg";
            $violating_data = [
                'license_plate' => $license_plate,
                'date' => $video_row['date'],
                'road' => $video_row['road'],
                'video_path' => $video_row['video_path'],
                'img_path' => $img_path,
            ];
            // print_r($violating_data);
        }

        $violatingCarModel->save($violating_data);

    }
}
