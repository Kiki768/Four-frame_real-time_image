document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_violation_images")
        .then(response => response.json())
        .then(images => {
            if (images.length === 0) {
                console.warn("⚠️ 沒有違規圖片可顯示！");
                return;
            }
            let index = 0;
            const imageElement = document.getElementById("violationImage");

            function updateImage() {
                imageElement.src = images[index];
                imageElement.onload = extractTimestamp;
            }

            document.getElementById("prevBtn").addEventListener("click", function () {
                index = (index - 1 + images.length) % images.length;
                updateImage();
            });

            document.getElementById("nextBtn").addEventListener("click", function () {
                index = (index + 1) % images.length;
                updateImage();
            });

            updateImage(); // 載入第一張圖片
        })
        .catch(error => console.error("❌ 無法獲取違規圖片列表:", error));
});


function deleteViolation() {
    if (confirm("確定要刪除此違規記錄？")) {
        document.querySelector(".violation-container").style.display = "none";
    }
}

function saveViolation() {
    let violationData = {
        time: document.getElementById("violationTime").innerText,
        plate: document.getElementById("licensePlate").innerText,
    };
    console.log("儲存資料:", violationData);
    alert("違規資料已儲存");
}
