<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>即時車輛偵測違規系統</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            display: flex;
        }

        #sidebar {
            width: 200px;
            background-color: #2c2c2c;
            color: white;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
            overflow-y: auto;
            transition: transform 0.3s ease;
        }

        #sidebar.collapsed {
            transform: translateX(-100%);
        }

        #sidebar h2 {
            text-align: center;
            padding: 10px 0;
            border-bottom: 1px solid #444;
        }

        #sidebar a {
            display: block;
            padding: 10px 20px;
            color: white;
            text-decoration: none;
        }

        #sidebar a:hover {
            background-color: #575757;
        }

        #toggleSidebarBtn {
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 1001;
            background-color: #2c2c2c;
            color: white;
            border: none;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 16px;
            border-radius: 4px;
        }

        .main-content {
            margin-left: 200px;
            padding: 20px;
            width: 100%;
            transition: margin-left 0.3s ease;
        }

        #sidebar.collapsed ~ .main-content {
            margin-left: 0;
        }
    </style>
</head>
<body>

    <div id="sidebar">
        <h2>RT-DTV</h2>
        <a href="/Home">首頁</a>
        <a href="/UploadController">上傳影片</a>
        <a href="/RunController">手動偵測</a>
        <a href="/MonitorController/only_one_screen">自動偵測</a>
        <a href="/FindController/find_car_with_monitor">搜尋違規車</a>
        <a href="/LiveFeedController">四格即時影像</a>
        <a href="/ViolationController">違規輸出管理</a>
        <a href="/LiveFeedController/violation_history">違規單歷史紀錄</a>
        <a href="/LoginController/logout" class = "logout">登出</a>
    </div>

    <button id="toggleSidebarBtn">☰</button>

    <div class="main-content">
        <?= $this->renderSection('content') ?>
    </div>

    <?= $this->renderSection('script') ?>

    <script>
        document.getElementById('toggleSidebarBtn').addEventListener('click', function () {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });
    </script>
</body>
</html>
