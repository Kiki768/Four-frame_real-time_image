<?= $this->extend('template') ?>
<style>
    .button-container {
    display: flex;
    justify-content: center; /* 水平置中 */
    align-items: center;     /* 垂直置中 */
    flex-direction: row;     /* 按鈕水平排列 */
    text-align:center;
}
</style>

<?php
    $videoUrl = base_url($video_path);
?>

<?= $this->section('content') ?>
    <div class = run-container>
        <div id="videoContainer">
        <video width="640" height="360" controls>
            <source src="<?=  $videoUrl ?>" type="video/mp4">
        </video>
        </div>
        <input type="button" name="click" value="執行程式" class="btn btn-secondary" onclick = "click_button('<?= $videoUrl ?>')" >

        <div id="loadingMessage" style="display:none;">程式執行中，請稍後...</div>
        <div id="responseMessage"></div>
        <div id="result"></div>
    </div>

    <script>

        // 自動依照 http/https 選 ws/wss，主機用當前頁面的 host
        const WS_PORT = 8081; // 你的 websocket:start 預設就是 6789
        const proto = location.protocol === 'https:' ? 'wss' : 'ws';
        const host  = location.hostname || '127.0.0.1';
        const wsURL = `${proto}://${host}:${WS_PORT}/`;

        const loadingEl  = document.getElementById('loadingMessage');
        const respEl     = document.getElementById('responseMessage');

        let socket = new WebSocket(wsURL);

        socket.onopen = () => {
            console.log("WebSocket 已連線");
        };

        socket.onmessage = (event) => {
            $('#loadingMessage').text("程式執行完畢");
            const data = JSON.parse(event.data);
            console.log("接收到事件通知:", data);
            $('#responseMessage').text("偵測到違規車編號 : " + data["car_id"]);
            

        };

        socket.onclose = () => {
            console.log("WebSocket 已關閉");
        };

        socket.onerror = (error) => {
            console.error("WebSocket 錯誤:", error);
        };
        function click_button(video_path)
        {
            console.log(video_path);
            $('#loadingMessage').text("程式執行中，請稍後...");
            $('#responseMessage').text("");
            $('#loadingMessage').show();
            if (socket.readyState === WebSocket.OPEN) {
                console.log("影片開始播放，向後端發送啟動訊號");
                const message = JSON.stringify({
                    action: "start",
                    path: video_path,
                });

                socket.send(message);
            }
        }
    </script>
<?= $this->endSection() ?>
