<?php

namespace App\Controllers;

use Config\Database;

class ViolationController extends BaseController
{
    // 首頁：只撈「待處理(pending)」的違規紀錄
    public function index()
    {
        $db = Database::connect();
        $violations = $db->query("
            SELECT id, license_plate, vehicle_type,
                   violation_time, owner_name, owner_address,
                   image_rel_path, created_at
            FROM violation_reports
            WHERE status = 'pending'
            ORDER BY created_at DESC
            LIMIT 50
        ")->getResultArray();

        return view('violation/index', ['violations' => $violations]);
    }

    // 儲存：更新姓名/地址，並將狀態改成 saved
    public function save_violation()
    {
        $data = $this->request->getJSON(true);
        if (!$data || empty($data['id'])) {
            return $this->response->setJSON([
                'success' => false,
                'error'   => '缺少 id'
            ]);
        }

        $db = Database::connect();
        $ok = $db->table('violation_reports')
            ->where('id', (int)$data['id'])
            ->update([
                'owner_name'    => $data['owner']   ?? null,
                'owner_address' => $data['address'] ?? null,
                'status'        => 'saved',
                'reviewed_at'   => date('Y-m-d H:i:s'),
            ]);

        return $this->response->setJSON(['success' => (bool)$ok]);
    }

    // 刪除：不刪資料，只把狀態改成 dismissed
    public function dismiss()
    {
        $data = $this->request->getJSON(true);
        if (!$data || empty($data['id'])) {
            return $this->response->setJSON([
                'success' => false,
                'error'   => '缺少 id'
            ]);
        }

        $db = Database::connect();
        $ok = $db->table('violation_reports')
            ->where('id', (int)$data['id'])
            ->update([
                'status'      => 'dismissed',
                'reviewed_at' => date('Y-m-d H:i:s'),
            ]);

        return $this->response->setJSON(['success' => (bool)$ok]);
    }

    // 違規管理紀錄用
    public function history()
    {
        $db = \Config\Database::connect();
        $rows = $db->query("
            SELECT id, license_plate, image_rel_path,
                status, reviewed_at
            FROM violation_reports
            WHERE status IN ('saved','dismissed')
            ORDER BY reviewed_at DESC
            LIMIT 100
        ")->getResultArray();

        // 轉換成跟前端需求一樣的格式
        $history = [];
        foreach ($rows as $row) {
            $history[] = [
                'video_name' => basename($row['image_rel_path'] ?? ''), // car2.jpg
                'action'     => ($row['status'] === 'saved' ? '儲存' : '刪除'),
                'timestamp'  => $row['reviewed_at'],
            ];
        }

        return $this->response->setJSON($history);
    }

}
