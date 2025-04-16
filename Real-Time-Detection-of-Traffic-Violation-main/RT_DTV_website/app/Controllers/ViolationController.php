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

    public function delete_violation()
    {
        $filename = $this->request->getGet('file');  // 取得前端傳來的檔案名稱
        $filePath = FCPATH . 'videos/result/' . $filename;  // 檔案路徑

        //echo "the path of delete is：" . $filePath . "<br>";

        if (file_exists($filePath)) {
            unlink($filePath);  // 刪除檔案
            return $this->response->setJSON(['success' => true]);
        } 
        else {
            return $this->response->setJSON(['success' => false, 'error' => '找不到檔案']);
        }
    }
    public function save_violation()
    {
        try {
            $data = $this->request->getJSON(true);

            if (!$data || !isset($data['filename'])) {
                return $this->response->setJSON(['success' => false, 'error' => '缺少檔名']);
            }

            $filename = $data['filename'];
            $sourceImage = 'videos/result/' . $filename;  // 相對路徑給 <img>
            $imagePath = FCPATH . $sourceImage;           // 絕對路徑給 unlink()
            $targetDir = FCPATH . 'videos/result/confirm/';
            $targetImagePath = $targetDir . $filename;
            $targetHTML = $targetDir . pathinfo($filename, PATHINFO_FILENAME) . '.html';

            copy($imagePath, $targetImagePath); //把圖片複製到confirm
            $imgUrl = base_url('videos/result/confirm/' . $filename);

            // HTML 內容
            $html = "
            <!DOCTYPE html>
            <html lang='zh-TW'>
            <head>
                <meta charset='UTF-8'>
                <title>違規紀錄 - {$data['plate']}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    img { width: 600px; height: auto; }
                    .info { margin-top: 20px; line-height: 1.8; }
                </style>
            </head>
            <body>
                <h2>違規紀錄</h2>
                
                <img src='" . $imgUrl . "' alt='違規圖片'>
                <div class='info'>
                    <strong>違規時間：</strong> {$data['time']}<br>
                    <strong>違規車牌：</strong> {$data['plate']}<br>
                    <strong>違規車種：</strong> {$data['type']}<br>
                    <strong>車主姓名：</strong> {$data['owner']}<br>
                    <strong>車主地址：</strong> {$data['address']}<br>
                </div>
            </body>
            </html>
            ";
            // echo $imgUrl; exit;

            file_put_contents($targetHTML, $html);

            // 刪除原始圖片
            unlink($imagePath);

            return $this->response->setJSON(['success' => true]);

        } catch (\Throwable $e) {
            return $this->response->setJSON([
                'success' => false,
                'error' => '伺服器錯誤：' . $e->getMessage()
            ]);
        }
    }


}
