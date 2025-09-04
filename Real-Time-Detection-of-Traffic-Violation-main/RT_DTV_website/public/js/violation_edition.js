const baseUrl = window.location.origin;
let imageElement;
let images = [];
let index = 0;


document.addEventListener("DOMContentLoaded", function () {
    //     const refreshBtn = document.getElementById("refreshBtn");
    //     if (refreshBtn) {
    //         refreshBtn.addEventListener("click", function () {
    //             location.reload(); // 重新整理頁面
    //         });
    //     }

    updateLastRefreshTime();

    setInterval(() => {
        location.reload();
        updateLastRefreshTime();
    }, 300000);

    function updateLastRefreshTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        const timeDisplay = document.getElementById("lastUpdatedTime");
        if (timeDisplay) {
            timeDisplay.textContent = "上次自動更新時間：" + timeStr;
        }
    }

    fetch(baseUrl + "/get_violation_images")
        .then(response => response.json())
        .then(data => {
            images = data;
            const img = document.getElementById("violationImage");
            const msg = document.getElementById("noViolationMsg");
            const details = document.getElementById("violationDetails");
            if (images.length === 0) {
                console.warn("⚠️ 沒有違規圖片可顯示！");
                if (msg) msg.style.display = "block";
                if (img) img.style.display = "none";
                if (details) details.style.display = "none";
                // if (refreshBtn) refreshBtn.style.display = "inline-block"; // 顯示按鈕
                return;
            } else {
                if (msg) msg.style.display = "none";
                if (img) img.style.display = "block";
                if (details) details.style.display = "block"
                // if (refreshBtn) refreshBtn.style.display = "none";
            }

            updateImage(); // 載入第一張圖片

            document.getElementById("prevBtn").addEventListener("click", function () {
                index = (index - 1 + images.length) % images.length;
                updateImage();
            });

            document.getElementById("nextBtn").addEventListener("click", function () {
                index = (index + 1) % images.length;
                updateImage();
            });


        })
        .catch(error => console.error("❌ 無法獲取違規圖片列表:", error));
});


function deleteViolation() {
    imageElement = document.getElementById("violationImage");
    let filename = imageElement.getAttribute("data-filename"); // 取得目前顯示的圖片檔名
    console.log("🔍 當前圖片檔名為：", filename);

    if (!filename) {
        alert("⚠️ 沒有可刪除的違規記錄！");
        return;
    }
    if (confirm("確定要刪除此違規記錄？")) {
        fetch(baseUrl + "/ViolationController/delete_violation?file=" + filename, { method: "DELETE" })
            .then(response => response.text())
            .then(text => {
                console.log("🔥 伺服器回應內容：", text);
                try {
                    const data = JSON.parse(text);
                    if (data.success) {
                        alert("✅ 違規記錄已刪除！");
                        location.reload(); // 重新整理畫面，更新違規列表
                    } else {
                        alert("❌ 刪除失敗：" + data.error);
                    }
                }
                catch (e) {
                    alert("⚠️ 回傳格式錯誤，內容如下：\n" + text);
                }
            });
    }
}

function updateImage() {
    console.log("updateImg print")
    imageElement = document.getElementById("violationImage");
    const filename = images[index].split("/").pop();
    imageElement.src = baseUrl + "/" + images[index];
    imageElement.setAttribute("data-filename", filename);

    //imageElement.onload = extractTimestamp;

    //console.log("載入圖片：", images[index]);
    console.log("📝 檔名已設定：", filename)

}

function saveViolation() {
    const imageElement = document.getElementById("violationImage");
    let violationData = {
        filename: imageElement.getAttribute("data-filename"),
        time: document.getElementById("violationTime").innerText,
        plate: document.getElementById("licensePlate").innerText,
        type: document.getElementById("carType").innerText,
        owner: document.getElementById("carOwner").innerText,
        address: document.getElementById("carAddress").innerText,
    };

    fetch(baseUrl + "/ViolationController/save_violation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(violationData)
    })

        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("✅ 已儲存並移除！");
                location.reload(); // 重新整理畫面，更新違規列表
            } else {
                alert("❌ 儲存失敗：" + data.error);
            }
        });
}

function fetchImageListAndUpdate() {
    fetch(baseUrl + "/get_violation_images")
        .then(response => response.json())
        .then(data => {
            images = data;
            if (images.length === 0) {
                alert("🚫 所有違規圖片都已儲存！");
                const imageElement = document.getElementById("violationImage");
                imageElement.src = "";
                imageElement.removeAttribute("data-filename");
                return;
            }

            // 避免 index 超出新資料長度
            index = index % images.length;
            updateImage();
        })
        .catch(error => {
            console.error("❌ 無法重新載入違規圖片清單:", error);
        });
}

