<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use CodeIgniter\HTTP\ResponseInterface;
use App\Models\VideoModel;
use App\Models\RoadModel;
use App\Models\ViolatingCarModel;

class CheckController extends BaseController
{
    public function index()
    {
        session();
        return view('checks/index');
    }
    public function folder_to_database()
    {

        $VideoModel = new VideoModel();
        $RoadModel = new RoadModel();

        $folder = FCPATH . 'videos';
        if (is_dir($folder)) {
            // 讀取資料夾中的檔案
            $files = scandir($folder);
            // 過濾掉 '.' 和 '..'
            $files = array_diff($files, ['.', '..']);
        } else {
            return "資料夾不存在。";
        }
        print_r($files);
        $letters = ['A', 'B', 'C', 'D'];
        foreach($files as $i)
        {
            $random_road = array_rand($letters);
            $road = $letters[$random_road];
            $datePart = substr($i, 0, 8);
            $date = substr($datePart, 0, 4) . '-' . substr($datePart, 4, 2) . '-' . substr($datePart, 6, 2);

            $video_data = [
                'videoname'=> $i,
                'road'=> $road,
                'is_run' => 0,
                'date'=> $date,
                'video_path'=> 'videos/' . $i
            ];
            $road_data = [
                'road_name'=> $road,
                'date'=> $date,
            ];
            
            $existingRecord = $RoadModel->where('road_name', $road)
                             ->where('date', $date)
                             ->first();
            $existingVideo = $VideoModel->where('videoname', $i)->first();

            if ($existingVideo == FALSE) {
                // 如果不存在，執行插入操作
                $VideoModel->save($video_data);
                if ($existingRecord == FALSE) {
                    // 如果不存在，執行插入操作
                        $RoadModel->save($road_data);
                    }
            }


        }  
    }
    public function is_run()
    {
        $violatingCarModel = new ViolatingCarModel();
        $VideoModel = new VideoModel();
        $video_data = [
            'is_run' => 0,
        ];
        $VideoModel->set($video_data)->where('is_run', 1)->update();

        $first = $violatingCarModel->orderBy('id', 'ASC')->first();
        print_r($first);
        $firstId = $first['id'];
        $violatingCarModel->where('id !=', $firstId)->delete();

    }

    public function delete_video()
    {
        $VideoModel = new VideoModel();
        $VideoModel->where('videoname', '');
    }

    # 不要亂用
    public function delete_user()
    {
        $userModel = new UserModel();

        
        print_r($userModel->findAll());

    }

    public function delete_violation_car()
    {
        $violatingCarModel = new ViolatingCarModel();
        print_r($violatingCarModel->findAll());
        $violatingCarModel->where('img_path !=', '')->delete();
    }
}
