<?= $this->extend('template') ?>

<?= $this->section('content') ?>

    <!-- 影片四宮格 -->
    <div class="grid-container">
        <video id="video1" autoplay muted loop></video>
        <video id="video2" autoplay muted loop></video>
        <video id="video3" autoplay muted loop></video>
        <video id="video4" autoplay muted loop></video>
    </div>

    <script>
        let videos = <?= json_encode($videos) ?>; // 後端傳來的影片資料
        let videoElements = [
            document.getElementById("video1"),
            document.getElementById("video2"),
            document.getElementById("video3"),
            document.getElementById("video4")
        ];

        let intersections = Object.keys(videos); // 取得四個路口的名稱
        let currentIndex = [0, 0, 0, 0]; // 各路口的影片索引

        function playNextVideo(videoIndex) {
            let intersection = intersections[videoIndex]; // 取得對應的路口
            let videoList = videos[intersection]; // 取得該路口的影片列表
            let player = videoElements[videoIndex];

            if (videoList.length > 0) {
                player.src = videoList[currentIndex[videoIndex]]; // 設定影片
                player.load();
                player.play();

                // 設定影片播放完後換下一部
                player.onended = function () {
                    currentIndex[videoIndex] = (currentIndex[videoIndex] + 1) % videoList.length;
                    playNextVideo(videoIndex);
                };
            }
        }

        // 初始化播放四個路口的影片
        for (let i = 0; i < videoElements.length; i++) {
            playNextVideo(i);
        }
    </script>

    <style>
        .grid-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(2, 1fr);
            gap: 10px;
            width: 80%;
            max-width: 800px;
            margin: 20px auto;
        }
        video {
            width: 100%;
            height: auto;
            object-fit: cover;
        }
    </style>

<?= $this->endSection() ?>
