<?= $this->extend('template') ?>

<?= $this->section('content') ?>
<h2 style="color:black;">四格即時影像</h2>


<!-- 影片區塊 -->
<div class="video-wrapper" style="width: 80%; max-width: 800px; margin: 0 auto;">
    <div class="grid-container">
        <video id="video1" autoplay muted></video>
        <video id="video2" autoplay muted></video>
        <video id="video3" autoplay muted></video>
        <video id="video4" autoplay muted></video>
    </div>
</div>

<!-- 將這個按鈕移到外層（不會擋影片） -->
<div style="width: 80%; max-width: 800px; margin: 20px auto 0;">
    <button id="startDetectionBtn" style="
        padding: 10px 15px;
        font-size: 16px;
    ">開始偵測</button>
</div>


<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, 1fr);
        gap: 10px;
    }
    video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        background: black;
    }
</style>



<script>
    console.log("✅ JavaScript 載入了");

    async function loadVideos() {
        try {
            console.log("發送 API 請求: /LiveFeedController/api");
            const response = await fetch('/LiveFeedController/api');
            const data = await response.json();
            console.log("API 回傳的影片清單:", data);

            const videoMappings = {
                video1: data.folder1 || [],
                video2: data.folder2 || [],
                video3: data.folder3 || [],
                video4: data.folder4 || []
            };

            Object.keys(videoMappings).forEach(videoId => {
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
                setupVideoLoop(videoElement, videoMappings[videoId]);
            });

        } catch (error) {
            console.error("無法載入影片:", error);
        }
    }

    function setupVideoLoop(videoElement, sources) {
        if (sources.length === 0) {
            console.warn(`影片 ${videoElement.id} 沒有來源，無法播放`);
            return;
        }

        let index = 0;
        console.log(`設定 ${videoElement.id} 播放來源:`, sources);

        videoElement.src = sources[index];
        videoElement.load();
        videoElement.play().then(() => {
            console.log(`▶️ ${videoElement.id} 開始播放`);
        }).catch(error => console.warn(`影片 ${videoElement.id} 無法自動播放:`, error));

        videoElement.addEventListener("ended", () => {
            index = (index + 1) % sources.length;
            console.log(`影片 ${videoElement.id} 切換到: ${sources[index]}`);
            videoElement.src = sources[index];
            videoElement.load();
            videoElement.play().catch(error => console.warn(`影片 ${videoElement.id} 無法播放下一個:`, error));
        });

        videoElement.addEventListener("loadeddata", () => {
            console.log(`影片 ${videoElement.id} 已準備好播放: ${videoElement.src}`);
            videoElement.play().catch(error => console.warn(`影片 ${videoElement.id} 無法開始播放:`, error));
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        console.log("DOMContentLoaded 事件觸發，執行 loadVideos()");
        loadVideos();
    });

    document.getElementById('startDetectionBtn').addEventListener('click', async () => {
    console.log("🔘 [開始偵測] 按鈕被點擊");

    const confirmStart = confirm("確定要啟動違規偵測嗎？");

    if (confirmStart) {
        console.log("✅ 使用者確認啟動，準備送出 fetch POST 請求");

        try {
            const res = await fetch('/LiveFeedController/start_detection', {
                method: 'POST'
            });

            const data = await res.json();
            console.log("🎯 後端回傳資料：", data);

            if (data.success) {
                alert("🚗 偵測啟動成功！");
            } else {
                alert("❌ 偵測啟動失敗：" + data.error);
            }
        } catch (err) {
            console.error("❌ 發生錯誤：", err);
            alert("❌ 發生錯誤：" + err);
        }
    } else {
        console.log("❎ 使用者取消啟動");
    }
});

</script>

<?= $this->endSection() ?>
