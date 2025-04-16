<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use CodeIgniter\HTTP\ResponseInterface;
use App\Models\UserModel;


class LoginController extends BaseController
{

    public function index()
    {
        return view('logins/index');
    }

    public function choose_action()
    {
        $action = $this->request->getVar('action');
        if($action == "註冊")
            return view('logins/register');
        else
            return view('logins/login');
        // print_r($action);
    }

    public function login_process()
    {
        $userModel = new UserModel();
        
        $username = $this->request->getVar('username');
        $password = $this->request->getVar('password');
        $hash_password = 1;
        // echo $username.'_'.$password;
        $user = $userModel->where('username', $username)->first();
        // echo $user['username'];
        if($user)
        {

            // password_verify($password, $user['password']
            if($password == $user['password'])
            {
                session()->set('loggedIn', true);
                session()->set('username', $user['username']);
                session()->set('authority', $user['authority']);
                return redirect()->to('Home');
            }
            else
            {
                return redirect()->back()->with('error', '密碼錯誤');
            }
        }
        else
        {
            return redirect()->back()->with('error', '帳號不存在');
        }
    }

    public function register_process()
    {   
        
        $userModel = new UserModel();
        $user_data = [
            'username'=> $this->request->getVar('usr_name'),
            'password' => $this->request->getVar('password'),
            'email' => $this->request->getVar('email_name'),
            'authority' => 1,
        ];
        $userModel->save($user_data);
        return redirect()->back()->with('error', '註冊成功，請重新登入');
    }

    public function logout()
    {
        session()->destroy();
        return redirect()->to('/');
    }



    public function login()
    {   
        return view('logins/login');
    }

}
