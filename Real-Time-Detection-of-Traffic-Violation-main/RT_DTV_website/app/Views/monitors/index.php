<?= $this->extend('template') ?>

<?php
    foreach($row as $i)
        $videoUrl[$i['road']][] = base_url($i['video_path']);
?>



<?= $this->section('content') ?>

    <div class = "cut-video-container">
        <video name = "A" class = "video" width="640" height="360" type="video/mp4" autoplay muted></video>
        <video name = "B" class = "video" width="640" height="360" type="video/mp4" autoplay muted></video>
        <video name = "C" class = "video" width="640" height="360" type="video/mp4" autoplay muted></video>
        <video name = "D" class = "video" width="640" height="360" type="video/mp4" autoplay muted></video>
        <div class = "red-dot"></div>
        <div class = "red-dot" style = "left:950px;"></div>
        <div class = "red-dot" style = "top:500px;"></div>
        <div class = "red-dot" style = "top:500px; left:950px;"></div>
    </div>
    <!-- <h1>我還沒寫好即時偵測，目前只有顯示</h1> -->
    <script>
        $(document).ready(function() {
            console.log("Hello World!");

        })
        const videos = <?php echo json_encode($videoUrl);?>;
        const video_elements = document.querySelectorAll('.video');
        const red_dot = document.getElementsByClassName('red-dot');
        
        let current = [0,0,0,0];
        const lengths = Object.values(videos).map(arr => arr.length);

        console.log(videos);
        console.log(video_elements);
        console.log(lengths);

        function initial_video()
        {
            video_elements.forEach((video) => {
                video.src = videos[video.getAttribute('name')][0];
            });
        }
        
        function auto_play(video, video_i, index)
        {
            console.log(video);
            console.log(video_i);
            video.src = videos[video.getAttribute('name')][index[video_i]];
            // show_red_dot(video_i);
            if(video_i == 0 && index[0] == 1)
            {
                console.log('ccc');
                setTimeout(() => {
                    show_red_dot(video_i);
                }, 3000);
            }            
        }
        
        initial_video();

        video_elements.forEach((video, i) => {
            video.addEventListener('ended', ()=>{
                current[i] = (current[i] + 1) % lengths[i];
                auto_play(video, i, current);
                console.log(current);
            });
        });

        function show_red_dot(index) 
        {
            red_dot[index].style.display = 'block';
            red_dot[index].style.opacity = '1';
            setTimeout(() => {
                hide_red_dot(index);
            }, 3000);
        }

        function hide_red_dot(index) 
        {
            red_dot[index].style.opacity = '0';
            setTimeout(() => {
                red_dot[index].style.display = 'none';
            }, 300);
        }

    </script>
<?= $this->endSection() ?>
