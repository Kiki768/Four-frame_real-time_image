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
        try {
            $filename = $this->request->getGet('file');  // 取得前端傳來的檔案名稱
            $filePath = FCPATH . 'videos/result/' . $filename;  // 檔案路徑

            // 建立刪除備份資料夾
            $deleteBackupDir = FCPATH . 'videos/result/deleted/';
            if (!is_dir($deleteBackupDir)) {
                mkdir($deleteBackupDir, 0777, true);
            }    
            // 備份圖片到 deleted 資料夾
            $backupImagePath = $deleteBackupDir . $filename;
            copy($filePath, $backupImagePath);
            // 記錄到歷史紀錄（只記錄在 history.php 頁面）
            $this->addToHistory($filename, '刪除');
            unlink($filePath); // 刪除檔案

            return $this->response->setJSON(['success' => true, 'message' => '檔案已刪除並備份']);

        } catch (\Throwable $e) {
            return $this->response->setJSON([
                'success' => false,
                'error' => '刪除操作失敗：' . $e->getMessage()
            ]);
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

            if (!is_dir($targetDir)) {
                mkdir($targetDir, 0777, true);
            }

            copy($imagePath, $targetImagePath); //把圖片複製到confirm
            $this->addToHistory($filename, '儲存');

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

    private function addToHistory($filename, $action)
    {
        $logPath = WRITEPATH . 'logs/violation_history.csv';
        $timestamp = date('Y-m-d H:i:s');
        
        // 確保 logs 目錄存在
        $logDir = WRITEPATH . 'logs/';
        if (!is_dir($logDir)) {
            mkdir($logDir, 0755, true);
        }

        // 寫入 CSV 格式：圖片名稱,操作,時間
        $logEntry = "$filename,$action,$timestamp\n";
        
        // 以附加模式寫入檔案
        file_put_contents($logPath, $logEntry, FILE_APPEND | LOCK_EX);
        
        // 寫入除錯訊息到日誌檔
        log_message('info', "違規處理歷史紀錄已新增：檔案={$filename}, 操作={$action}, 時間={$timestamp}");
    }


}
