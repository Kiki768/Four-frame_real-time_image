<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use CodeIgniter\HTTP\ResponseInterface;
use App\Models\VideoModel;
use App\Models\RoadModel;

class UploadController extends BaseController
{
    public function index()
    {
        $RoadModel = new RoadModel();
        $data = ["row" => $RoadModel->select('road_name')->groupBy('road_name')->findAll()];
        return view('uploads/index', $data);
    }
    #多部影片還沒寫
    public function upload()
    {
        $VideoModel = new VideoModel();
        $RoadModel = new RoadModel();

        $files = $this->request->getFile('my_file');
        $road = $this->request->getVar('road'); //路口名
        $videoname = $files->getName();//影片名
        $datePart = substr($videoname, 0, 8);
        $date = substr($datePart, 0, 4) . '-' . substr($datePart, 4, 2) . '-' . substr($datePart, 6, 2);
        $path = 'videos/';//影片存的路徑
        $is_run = 0;
        
        $result = $VideoModel->where('videoname',$videoname)->first();
        if($road == NULL)
        {
            return redirect()->back()->with('error', '未選擇路口');
        }
  
        if(empty($result))
        {
            $video_data=[
                'videoname'=> $videoname,
                'road'=> $road,
                'is_run' => $is_run,
                'date'=> $date,
                'video_path'=> $path . $videoname
            ];
            print_r($files);
            $files->move(ROOTPATH . 'public/videos/' , $videoname);
            $VideoModel->save($video_data);
            $existingRecord = $RoadModel->where('road_name', $road)
                             ->where('date', $date)
                             ->first();

            if ($existingRecord == FALSE) {
            // 如果不存在，執行插入操作
            $data = [
                'road_name' => $road,
                'date' => $date,
            ];
            $RoadModel->save($data);
            }
            // echo ROOTPATH . 'public/videos/' . $videoname;
            echo '成功上傳';
            
            return redirect()->to('UploadController');
        }
        else
        {
            //echo ROOTPATH . 'public/videos/' . $videoname;
            //echo '已經上傳';
            return redirect()->back()->with('error', $videoname.'已經上傳');
           
            // return view('uploads/index');
        }
    }
}
