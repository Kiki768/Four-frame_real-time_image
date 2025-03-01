<?= $this->extend('template') ?>

<?= $this->section('content') ?>
    <h2>四格即時影像</h2>
    <!-- 影片四宮格 -->
    <div class="grid-container">
        <video id="video1" autoplay muted loop></video>
        <video id="video2" autoplay muted loop></video>
        <video id="video3" autoplay muted loop></video>
        <video id="video4" autoplay muted loop></video>
    </div>

    <script>
        let videos = <?= json_encode($videos) ?>; // 從後端獲取影片清單
        let videoElements = [
            document.getElementById("video1"),
            document.getElementById("video2"),
            document.getElementById("video3"),
            document.getElementById("video4")
        ];

        function getRandomVideo(exclude = []) {
            let availableVideos = videos.filter(v => !exclude.includes(v)); // 避免選擇已經使用的影片
            return availableVideos[Math.floor(Math.random() * availableVideos.length)];
        }

        function updateVideos() {
            let usedVideos = [];
            videoElements.forEach(video => {
                let newVideo = getRandomVideo(usedVideos);
                usedVideos.push(newVideo);
                video.src = newVideo;
            });
        }

        // 初始化影片
        updateVideos();

        // 每 5 秒更換其中一部影片
        setInterval(() => {
            let randomIndex = Math.floor(Math.random() * videoElements.length);
            let newVideo = getRandomVideo([videoElements[randomIndex].src]);
            videoElements[randomIndex].src = newVideo;
        }, 5000);
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
