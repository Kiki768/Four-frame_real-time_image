<?= $this->extend('template') ?>
<?= $this->section('content') ?>

<h2 style="color:black;">交通科技執法轉彎車輛違規判斷</h2>


<!-- 四格影片區塊 -->
<div class="video-wrapper" style="width: 140%; max-width: 1200px; margin: 0 auto;">
    <div class="grid-container">
        <div class="video-cell">
            <video id="video1A" muted playsinline></video>
            <video id="video1B" muted playsinline style="display:none;"></video>
        </div>
        <div class="video-cell">
            <video id="video2A" muted playsinline></video>
            <video id="video2B" muted playsinline style="display:none;"></video>
        </div>
        <div class="video-cell">
            <video id="video3A" muted playsinline></video>
            <video id="video3B" muted playsinline style="display:none;"></video>
        </div>
        <div class="video-cell">
            <video id="video4A" muted playsinline></video>
            <video id="video4B" muted playsinline style="display:none;"></video>
        </div>
    </div>
</div>


<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, 1fr);
        gap: 10px;
    }
        .video-cell {
        position: relative;
        width: 100%;
        aspect-ratio: 16 / 9;
    }

    .video-cell video {
        position: absolute;
        width: 100%;
        height: 100%;
        object-fit: cover;
        background: black;
    }
</style>
<?= $this->endSection() ?>

<?= $this->section('script') ?>
<script>
console.log("✅ JavaScript 載入了");
    async function loadVideos() {
        try {
            const response = await fetch('/LiveFeedController/api');
            const data = await response.json();
            console.log("📦 API 回傳資料：", data);

            const videoMap = {
                1: data.folder1 || [],
                2: data.folder2 || [],
                3: data.folder3 || [],
                4: data.folder4 || []
            };

            for (let i = 1; i <= 4; i++) {
                const sources = videoMap[i];
                if (sources.length === 0) {
                    console.warn(`video${i} 無影片來源`);
                    continue;
                }

                setupDualVideoLoop(`video${i}A`, `video${i}B`, sources);
            }   

        } catch (err) {
            console.error("❌ 載入影片清單失敗：", err);
        }
    }

    function setupDualVideoLoop(idA, idB, sources) {
        const videoA = document.getElementById(idA);
        const videoB = document.getElementById(idB);
        let index = 0;
        let active = videoA;
        let standby = videoB;

        function preloadAndSwap() {
            standby.src = sources[index];
            standby.load();

            standby.onloadeddata = () => {
                standby.play();
                standby.style.display = "block";
                active.pause();
                active.style.display = "none";

                // 交換 active/standby
                [active, standby] = [standby, active];
                index = (index + 1) % sources.length;

                active.onended = () => preloadAndSwap();
            };
        }

        // 初始化第一段影片
        active.src = sources[index];
        active.load();
        active.play();
        index = (index + 1) % sources.length;
        active.onended = () => preloadAndSwap();
    }

    document.addEventListener("DOMContentLoaded", () => {
        console.log("DOMContentLoaded 事件觸發，執行 loadVideos()");
        loadVideos();

        fetch('/LiveFeedController/start_detection', {
            method: 'POST'
        })
        .then(res => res.json())
        .then(data => {
            console.log("🎯 自動啟動偵測回傳：", data);
            if (data.success) {
                console.log("🚗 偵測已自動啟動！");
            } else {
                console.log("❌ 偵測啟動失敗：" + data.error);
            }
        })
        .catch(err => {
            console.error("❌ 自動偵測發生錯誤：", err);
            console.log("❌ 自動偵測發生錯誤：" + err);
        });
    });
</script>
<?= $this->endSection() ?>
