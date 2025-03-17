<?= $this->extend('template') ?>

<?= $this->section('content') ?>
    <h2>違規管理</h2>
    <p>這裡可以管理所有違規車輛資料。</p>

    <!-- 影像顯示區 -->
    <div class="violation-container">
    <img id="violationImage" src="" alt="違規影像" style="width: 100%; max-width: 800px; height: auto;">
    <p><strong>擷取時間：</strong> <span id="timestamp"></span></p>
    <button id="prevBtn">⬅️ 上一張</button>
    <button id="nextBtn">➡️ 下一張</button>
    </div>

    <!-- 按鈕功能 -->
    <div class="button-container">
        <!--<button onclick="editViolation()">修改</button> -->
        <button onclick="deleteViolation()">刪除</button>
        <button onclick="saveViolation()">儲存</button>
    </div>

    <!-- 違規資訊表格 -->
    <table>
        <tr><th>違規時間</th><td id="violationTime">(尚未擷取)</td></tr>
        <tr><th>違規車牌</th><td contenteditable="true" id="licensePlate">CCC-0123</td></tr>
        <tr><th>違規車種</th><td contenteditable="true">汽車</td></tr>
        <tr><th>車主姓名</th><td contenteditable="true">(依車牌查出)</td></tr>
        <tr><th>車主地址</th><td contenteditable="true">(依車牌查出)</td></tr>
    </table>
<?= $this->endSection() ?>

<?= $this->section('script') ?>
<script src="https://cdn.jsdelivr.net/npm/tesseract.js@4"></script>
<script src="<?= base_url('js/violation_edition.js') ?>"></script>  <!-- 引入外部 JS -->
<?= $this->endSection() ?>
