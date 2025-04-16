<!DOCTYPE html>
<html lang="zh_TW">
<head>
    <meta charset="UTF-8">
    <title>即時車輛偵測違規系統</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            text-align: center;
        }

        form {
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 10px;
            background-color: #f9f9f9;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        input[type="text"], input[type="email"], input[type="password"] {
            width: 500px;   /*調整輸入框的寬度*/
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }

        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #45a049;
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        .login_btn {
            display: inline-block;
            align-items: center;
            margin-top: 10px;
            padding: 10px 20px;
            background-color: #008CBA;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }

        .login_btn:hover {
            background-color: #007bb5;
        }
    </style>
</head>
<body>
    <form action="/LoginController/register_process" method="POST">
        <h2>註冊帳號</h2>
        <label for="usr_name">使用者名稱:</label>
        <input type="text" id="usr_name" name="usr_name" required><br>
        
        <label for="email_name">電子郵件帳號:</label>
        <input type="email" id="email_name" name="email_name" required><br>
        
        <label for="password">密碼:</label>
        <input type="password" id="password" name="password" required><br>
        
        <label for="double_check_pssword">再次確認密碼:</label>
        <input type="password" id="double_check_psswd" name="double_check_psswd" required><br>
        
        <input type="submit" value="註冊帳號">
        <a href="<?= base_url('LoginController/login') ?>" class="login-btn">已經有帳號？登入</a>
    </form>
</body>
</html>
