<?= $this->extend('template') ?>

<?= $this->section('content') ?>
    <h2>四格即時影像</h2>
    <div class="grid-container">
        <video id="video1" autoplay muted></video>
        <video id="video2" autoplay muted></video>
        <video id="video3" autoplay muted></video>
        <video id="video4" autoplay muted></video>
    </div>

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
            height: 100%;
            object-fit: cover; /* 讓影片填滿框架 */
            display: block;
            background: black; /* 防止影片載入前背景透明 */
        }
    </style>

    <script>
        async function loadVideos() {
            try {
                console.log("發送 API 請求: /LiveFeedController/api");
                const response = await fetch('/LiveFeedController/api'); // 向後端請求影片來源
                const data = await response.json();
                console.log("API 回傳的影片清單:", data);

                const videoMappings = {
                    video1: data.folder1 || [],
                    video2: data.folder2 || [],
                    video3: data.folder3 || [],
                    video4: data.folder4 || []
                };

                Object.keys(videoMappings).forEach(videoId => { // 遍歷 四個 <video> 元素 (video1~video4)
                    const videoElement = document.getElementById(videoId);
                    if (!videoElement) {
                        console.error(`找不到 <video> 標籤: ${videoId}`);
                        return;
                    }
                    if (videoMappings[videoId].length === 0) {
                        console.warn(`影片 ${videoId} 沒有可播放的內容`);
                        return;
                    }

                    console.log(`設定 ${videoId} 播放來源:`, videoMappings[videoId]); 
                    setupVideoLoop(videoElement, videoMappings[videoId]); //若有可播放的影片，則呼叫 setupVideoLoop() 來播放影片。 
                });

            } catch (error) {
                console.error("無法載入影片:", error);
            }
        }

        function setupVideoLoop(videoElement, sources) { // 設定 <video> 迴圈播放
            if (sources.length === 0) {
                console.warn(`影片 ${videoElement.id} 沒有來源，無法播放`);
                return;
            }

            let index = 0;
            console.log(`設定 ${videoElement.id} 播放來源:`, sources);

            videoElement.src = sources[index];
            videoElement.load(); 
            videoElement.play().then(() => {
                console.log(`${videoElement.id} 開始播放`);
            }).catch(error => console.warn(`影片 ${videoElement.id} 無法自動播放:`, error));

            videoElement.addEventListener("ended", () => {
                index = (index + 1) % sources.length; // index = (index + 1) % sources.length 讓索引回到開頭
                console.log(`影片 ${videoElement.id} 切換到: ${sources[index]}`);
                videoElement.src = sources[index];
                videoElement.load(); // 重新載入影片
                videoElement.play().catch(error => console.warn(`影片 ${videoElement.id} 無法播放下一個:`, error));
            });

            videoElement.addEventListener("loadeddata", () => { // 影片載入完成後自動播放
                console.log(`影片 ${videoElement.id} 已準備好播放: ${videoElement.src}`);
                videoElement.play().catch(error => console.warn(`影片 ${videoElement.id} 無法開始播放:`, error));
            });
        }

        document.addEventListener("DOMContentLoaded", () => {
            console.log("DOMContentLoaded 事件觸發，執行 loadVideos()");
            loadVideos();
        });
    </script>
<?= $this->endSection() ?>
