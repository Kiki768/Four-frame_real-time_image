<?php namespace App\Controllers;

class Health extends BaseController {
    public function index() {
        return $this->response->setJSON(['ok' => true, 'time' => time()]);
    }
}
