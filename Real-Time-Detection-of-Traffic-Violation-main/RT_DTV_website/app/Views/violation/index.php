<?= $this->extend('template') ?>

<?= $this->section('content') ?>
<style>
.center-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding-top: 20px;
    text-align: center;
}
table {
    margin-top: 20px;
    border-collapse: collapse;
}

table th,
table td {
    padding: 8px 12px;
    border: 1px solid #ccc;
    text-align: left;
}

.button-container {
    margin: 10px;
}
</style>


<div class="center-container">
    <h2>違規車輛取締結果</h2> 

    <!-- 影像顯示區 -->
    <div class="violation-container">
        <img id="violationImage" src="" data-filename="" style="width: 800px; height: auto;">
        <p id="noViolationMsg" style="display: none; color: gray; font-size: 30px; margin: 24px 0 32px 0;">目前無違規車輛</p>
    </div>
    <p id="lastUpdatedTime" style="font-size: 14px; color: #888; margin-top: 20px;"></p>
    <!-- <button id="refreshBtn" style="
        display: none;
        padding: 10px 20px;
        font-size: 16px;
        background-color:rgb(37, 159, 78);
        color: white;
        border: none;
        border-radius: 5px;
        margin-top: 20px;
        cursor: pointer;
    "> 重新整理</button> -->

    <div id="violationDetails">  
        <p><strong>擷取時間：</strong> <span id="timestamp"></span></p>
        <button id="prevBtn">⬅️ 上一張</button>
        <button id="nextBtn">➡️ 下一張</button>
    

        <!-- 按鈕功能 -->
        <div class="button-container">
            <button onclick="deleteViolation()">刪除</button>
            <button onclick="saveViolation()">儲存</button>
        </div>

    <!-- 違規資訊表格 -->
        <table>
            <tr><th>違規時間</th><td id="violationTime">(尚未擷取)</td></tr>
            <tr><th>違規車牌</th><td contenteditable="true" id="licensePlate">CCC-0123</td></tr>
            <tr><th>違規車種</th><td contenteditable="true" id="carType">汽車</td></tr>
            <tr><th>車主姓名</th><td contenteditable="true" id="carOwner"(依車牌查出)</td></tr>
            <tr><th>車主地址</th><td contenteditable="true" id="carAddress">(依車牌查出)</td></tr>
        </table>
    </div>
<?= $this->endSection() ?>

<?= $this->section('script') ?>
<!-- <script>
    const baseUrl = "<?= base_url() ?>";

</script> -->
<script src="https://cdn.jsdelivr.net/npm/tesseract.js@4"></script>
<script src="<?= base_url('js/violation_edition.js') ?>"></script>

<?= $this->endSection() ?>
