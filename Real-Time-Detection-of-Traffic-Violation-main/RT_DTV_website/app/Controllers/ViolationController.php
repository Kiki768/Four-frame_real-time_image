<?php

namespace App\Controllers;

class ViolationController extends BaseController
{
    public function index()
    {
        $folderPath = 'public/videos/result/';
        $violations = [];

        if (is_dir($folderPath))
        {
            $files = scandir($folderPath);
            foreach($files as $file)
            {
                if(pathinfo($file, PATHINFO_EXTENSION) === 'jpg')
                {
                    $violations[] = 
                    [
                        'image' => base_url($folderPath . $file),
                        'violation_time' => date("Y-m-d H:i:s", filemtime($folderPath . $file)), // 以檔案修改時間作為違規時間
                        'license_plate' => strtoupper(substr($file, 0, 7)), // 假設檔名前 7 碼為車牌
                        'violation_type' => '未打方向燈',
                        'owner_name' => '(依車牌查出)',
                        'owner_address' => '(依車牌查出)',
                    ];
                }
            }
        }
        $data = ['violations' => $violations];
        return view('violation/index'); // 導向違規管理頁面
    }
    public function get_violation_images()
    {
        $imageDir = FCPATH . 'videos/result/'; // 確保路徑正確
        $imageFiles = [];

        if (is_dir($imageDir)) {
            $files = scandir($imageDir);
            foreach ($files as $file) {
                if (pathinfo($file, PATHINFO_EXTENSION) === "jpg") {
                    $imageFiles[] = "videos/result/" . $file;
                }
            }
        }

        return $this->response->setJSON($imageFiles);
    }
}
