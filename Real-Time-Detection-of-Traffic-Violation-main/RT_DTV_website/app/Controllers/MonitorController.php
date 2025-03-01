<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use CodeIgniter\HTTP\ResponseInterface;
use App\Models\AutoVideoModel;
use App\Models\VideoModel;
use App\Models\ViolatingCarModel;



class MonitorController extends BaseController
{
    public function index()
    {
        $autoVideoModel = new AutoVideoModel();
        $autoVideoModel->truncate();
        $folder = FCPATH . 'auto_videos';
        if (is_dir($folder)) 
        {
            // 讀取資料夾中的檔案
            $road_folder = scandir($folder);
            // 過濾掉 '.' 和 '..'
            $road_folder = array_diff($road_folder, ['.', '..']);
        }
        else 
            return "資料夾不存在。";
        foreach($road_folder as $key => $value)
        {
            $road_folder[$key] = $folder . '\\' . $road_folder[$key];
            $files = scandir($road_folder[$key]);
            $files = array_diff($files, ['.', '..']);
            foreach($files as $i)
            {
                $datePart = substr($i, 0, 8);
                $date = substr($datePart, 0, 4) . '-' . substr($datePart, 4, 2) . '-' . substr($datePart, 6, 2);
                $video_data = [
                    'videoname'=> $i,
                    'road'=> $value,
                    'is_run' => 1,
                    'date'=> $date,
                    'video_path'=> 'auto_videos/' . $value . '/'.$i
                ];
                $autoVideoModel->save($video_data);
            }

        }
        $data = ["row" => $autoVideoModel->findAll()];
        # 這邊讀完影片之後
        return view("monitors/index", $data);
    }

    public function only_one_screen()
    {

        $autoVideoModel = new AutoVideoModel();
        $autoVideoModel->truncate();
        $folder = FCPATH . 'auto_videos';
        if (is_dir($folder)) 
        {
            // 讀取資料夾中的檔案
            $road_folder = scandir($folder);
            // 過濾掉 '.' 和 '..'
            $road_folder = array_diff($road_folder, ['.', '..']);
        }
        else 
            return "資料夾不存在。";
        foreach($road_folder as $key => $value)
        {
            $road_folder[$key] = $folder . '\\' . $road_folder[$key];
            $files = scandir($road_folder[$key]);
            $files = array_diff($files, ['.', '..']);
            foreach($files as $i)
            {
                $datePart = substr($i, 0, 8);
                $date = substr($datePart, 0, 4) . '-' . substr($datePart, 4, 2) . '-' . substr($datePart, 6, 2);
                $video_data = [
                    'videoname'=> $i,
                    'road'=> $value,
                    'is_run' => 0,
                    'date'=> $date,
                    'video_path'=> 'auto_videos/' . $value . '/'.$i
                ];
                $autoVideoModel->save($video_data);
            }

        }
        $data = ["row" => $autoVideoModel->findAll()];
        # 這邊讀完影片之後
        return view("monitors/only_one_screen", $data);
    }

    public function save_violation_car($data)
    {
        $violationVideoModel = new ViolatingCarModel();
        $videoModel = new VideoModel();
        $car_ids = $data['car_id'];
        $video_name = $data['video_name'];
        $datePart = substr($video_name, 0, 8);
        $date = substr($datePart, 0, 4) . '-' . substr($datePart, 4, 2) . '-' . substr($datePart, 6, 2);
        $video = $videoModel -> where('videoname', $video_name . '.mp4') -> first();
        $img_folder = 'only_one_screen_result/result/' . $video_name;

        foreach($car_ids as $car_id)
        {
            $violation_car_data = [
                "license_plate" => $car_id,
                "date" => $date,
                "road" => $video['road'],
                "video_path" => $video['video_path'],
                "img_path" => $img_folder . '/car' . strval($car_id) . '.jpg'
            ];
            $exist_data = $violationVideoModel->where('img_path', $violation_car_data['img_path'])->first();
            if(!$exist_data)
                $violationVideoModel->save($violation_car_data);
        }

        return $this->response->setStatusCode(200);

    }

    public function save_violation_car_auto($data)
    {
        
        $violationVideoModel = new ViolatingCarModel();
        $car_ids = $data['car_id'];
        $video_name = $data['video_name'];
        $split_road = explode("\\", $data['video_path']);
        $road = $split_road[count($split_road) -2];
        $img_folder = 'only_one_screen_result/result/' . $video_name;

        foreach($car_ids as $car_id)
        {
            $violation_car_data = [
                "license_plate" => $car_id,
                "date" => "monitor",
                "road" => $road,
                "video_path" => 'auto_videos/' . $road . '/'.$video_name,
                "img_path" => $img_folder . '/car' . strval($car_id) . '.jpg'
            ];
            $exist_data = $violationVideoModel->where('img_path', $violation_car_data['img_path'])->first();
            if(!$exist_data)
                $violationVideoModel->save($violation_car_data);
        }
        
        return $this->response->setStatusCode(200);
    }

    public function get_violation_car_data()
    {
        $data = $this->request->getJSON(true); // 接收 JSON 資料
        if($data['auto'] == 0)
            $this->save_violation_car($data);
        else
            $this->save_violation_car_auto($data);
    }

}