<?= $this->extend('template') ?>

<?php
    foreach($row as $i)
    {
        $videoUrl[$i['road']][] = base_url($i['video_path']);
        $road_option[] = $i['road'];
    }
    $road_option = array_unique($road_option);
    // print_r($road_option);
?>

<?= $this->section('content') ?>

    <select name="roadSelect" id="roadSelect" class = "form-select form-select-focus"  style = "width: 50% ; display:inline-block">
        <option value="">請選擇路口</option>
        <?php 
            foreach ($road_option as $road)
                echo '<option value='.$road.' required>'.$road.'</option>'
        ?>
    </select><br><br>

    <div class = "only-one-video-container" >
        <video class = "video" type="video/mp4" autoplay muted></video>
        <div class = "red-dot"></div>
    </div>
    <h3 hidden id = "show_violation_car" style = "color: red">違規車ID:<h3><h3 id = "detect_result"></h3>
    <script>
        const videos = <?php echo json_encode($videoUrl);?>;
        const video_element = document.querySelectorAll('.video')[0];
        const red_dot = document.getElementsByClassName('red-dot')[0];
        const detect_result = document.getElementById('detect_result');
        const road_select = document.getElementById('roadSelect');
        const show_violation_car = document.getElementById('show_violation_car');


        // console.log(videos);
        // console.log(video_element);
        // console.log(lengths);
        
        function initial_video(road)
        {
            if(road === "")
            {
                road_name = "";
                lengths = 0;
                current = 0;
                video_element.src = "";
                show_violation_car.hidden = true; 
                return
            }
            road_name = road;
            lengths = videos[road_name].length;
            current = 0;
            video_element.src = videos[road_name][0];
            show_violation_car.hidden = false;
        }
        
        function auto_play(current)
        {
            video_element.src = videos[road_name][current];     
        }

        //  初始化 WebSocket 連線
        ip = "localhost:6789/";
        socket = new WebSocket("ws://" + ip);

        socket.onopen = () => {
            console.log("WebSocket 已連線");
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("接收到事件通知:", data);

            // 根據事件名稱顯示紅點
            if (data.event === "violation_car") {
                show_red_dot(); 
                detect_result.innerText = data.car_id;
            }
        };

        socket.onclose = () => {
            console.log("WebSocket 已關閉");
        };

        socket.onerror = (error) => {
            console.error("WebSocket 錯誤:", error);
        };

        //新增事件監聽器--選單顯示影片
        road_select.addEventListener('change', ()=>{
            console.log(road_select.value);
            initial_video(road_select.value);
        });
        
        // 新增事件監聽器--當影片播完播下一部影片
        video_element.addEventListener('ended', ()=>{
            current = (current + 1) % lengths;
            auto_play(current);
            console.log(current);
        });
        
        // 新增事件監聽器--當影片開始播放時，向後端發送啟動訊號
        video_element.addEventListener('play', () => {
            if (socket.readyState === WebSocket.OPEN) {
                console.log("影片開始播放，向後端發送啟動訊號");
                const video_path = video_element.src;
                const message = JSON.stringify({
                    action: "start_auto",
                    path: video_path,
                });

                socket.send(message);
            }
            
        });

        function show_red_dot() 
        {
            red_dot.style.display = 'block';
            red_dot.style.opacity = '1';
            setTimeout(() => {
                hide_red_dot();
            }, 3000);
        }

        function hide_red_dot() 
        {
            red_dot.style.opacity = '0';
            setTimeout(() => {
                red_dot.style.display = 'none';
            }, 300);
        }
        

    </script>

    
<?= $this->endSection() ?>
