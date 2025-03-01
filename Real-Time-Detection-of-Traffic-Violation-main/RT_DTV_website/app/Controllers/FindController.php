<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use CodeIgniter\HTTP\ResponseInterface;
use App\Models\RoadModel;
use App\Models\ViolatingCarModel;

class FindController extends BaseController
{
    public function index()
    {
        $roadModel = new RoadModel();
        $data = ["row" => $roadModel->findAll()];
        return view("finds/index", $data);
    }
    public function find_license_plate()
    {
        $violatingCarModel = new ViolatingCarModel();
        if($this->request->getVar('road_name') != ''){
            $road_name = $this->request->getVar('road_name');
            $date = $this->request->getVar('date');
            $data = $violatingCarModel->where('date', $date)->where('road', $road_name)->findAll();
            return view('finds/road_result', ['data' => $data]);
        }
        else{
            return redirect()->back()->with('error', '未選擇路口');
        }
    }

    public function find_car_with_monitor()
    {
        $violatingCarModel = new ViolatingCarModel();
        $data = $violatingCarModel->findAll();
        $find_road = $violatingCarModel->distinct()->select('road')->findAll();
        $road = array_column($find_road, 'road');
        foreach($data as $i)
        {
            $violation_car[$i['road']][] = $i;
        }
        return view('finds/monitor_result', ['data' => $data, 'road' => $road]);
    }
}
