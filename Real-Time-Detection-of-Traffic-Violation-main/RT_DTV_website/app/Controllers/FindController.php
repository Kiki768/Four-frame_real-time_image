<?php
namespace App\Controllers;

use App\Controllers\BaseController;
use Config\Database;

class FindController extends BaseController
{
    // 查詢首頁：只需要提供 ABCD 路口選單
    public function index()
    {
        $roads = ['A','B','C','D'];     // 固定 ABCD
        return view('finds/index', ['roads' => $roads]);
    }

    // 依 路口 + 日期 查詢 violation_reports
    public function find_license_plate()
    {
        $road = $this->request->getVar('road_name');    // 'A' | 'B' | 'C' | 'D' | 'show_all_car'
        $date = $this->request->getVar('date');         // YYYY-MM-DD (可選)

        if ($road === null || $road === '') {
            return redirect()->back()->with('error', '未選擇路口');
        }

        $db = Database::connect();
        $builder = $db->table('violation_reports')
            ->select('id, license_plate, road, image_rel_path, status, reviewed_at, created_at');

        if ($road !== 'show_all_car') {
            $builder->where('road', $road);
        }
        if (!empty($date)) {
            // 以建立時間的日期來篩
            $builder->where('DATE(created_at)', $date);
        }

        $rows = $builder->orderBy('created_at', 'DESC')->get()->getResultArray();

        return view('finds/road_result', [
            'data'  => $rows,
            'roads' => ['A','B','C','D']  // 讓結果頁也能換路口
        ]);
    }

    // 顯示所有（依路口過濾）—給你原本 monitor 頁邏輯的替代
    public function find_car_with_monitor()
    {
        $db = Database::connect();
        $rows = $db->table('violation_reports')
            ->select('id, license_plate, road, image_rel_path, status, reviewed_at, created_at') // ← 加上這些
            ->orderBy('created_at','DESC')
            ->get()->getResultArray();

        // （如果這頁也用到一樣的 view，就傳 $roads；否則可不傳）
        return view('finds/monitor_result', [
            'data'  => $rows,
            'roads' => ['A','B','C','D'],
        ]);
    }
}
