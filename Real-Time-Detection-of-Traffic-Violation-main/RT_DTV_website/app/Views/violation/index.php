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
    margin: 20px auto; /* 自動水平置中 */
    border-collapse: collapse;
}
table th, table td {
    padding: 8px 12px;
    border: 1px solid #ccc;
    text-align: left;
}
.button-container { margin: 10px; }
.muted { color: #888; font-size: 12px; }
img { max-width: 800px; height: auto; }
.controls { margin: 8px 0 16px 0; }
.controls button { margin: 0 6px; }
</style>

<div class="center-container">
    <h2>違規車輛取締結果</h2>

    <!-- 影像顯示區 -->
    <div class="violation-container">
        <img id="violationImage" src="" data-id="" data-index="-1" alt="violation">
        <p id="noViolationMsg" style="display:none; color: gray; font-size: 30px; margin: 24px 0 32px 0;">
            目前無違規車輛
        </p>
    </div>

    <p id="lastUpdatedTime" class="muted"></p>

    <div class="controls">
        <button id="prevBtn">⬅️ 上一張</button>
        <button id="nextBtn">➡️ 下一張</button>
    </div>

    <!-- 按鈕功能 -->
    <div class="button-container">
        <button id="deleteBtn">刪除</button>
        <button id="saveBtn">儲存</button>
    </div>

    <!-- 違規資訊表格 -->
    <div id="violationDetails" style="display:none;">
        <table>
            <tr><th>違規時間</th><td id="violationTime">(尚未擷取)</td></tr>
            <tr><th>違規車牌</th><td contenteditable="true" id="licensePlate">CCC-0123</td></tr>
            <tr><th>違規車種</th><td contenteditable="true" id="carType">汽車</td></tr>
            <tr><th>車主姓名</th><td contenteditable="true" id="carOwner">(依車牌查出)</td></tr>
            <tr><th>車主地址</th><td contenteditable="true" id="carAddress">(依車牌查出)</td></tr>
        </table>
        <p class="muted" id="imgPath"></p>
    </div>
</div>
<?= $this->endSection() ?>

<?= $this->section('script') ?>
<script>
  // 從 PHP 傳進來的資料庫資料（ViolationController::index 丟的 $violations）
  // 欄位：id, license_plate, vehicle_type, violation_time, owner_name, owner_address, image_rel_path, created_at
  const violations = <?= json_encode($violations ?? [], JSON_UNESCAPED_UNICODE) ?>;

  // 後端 API 位址
  const URL_DELETE = "<?= site_url('violation/delete') ?>"; // GET ?id=123
  const URL_SAVE   = "<?= site_url('violation/save') ?>";   // POST JSON {id, owner, address}

  // 如果專案有開 CSRF，可以把 Token 帶上（沒開不影響）
  const CSRF_HEADER = 'X-CSRF-TOKEN';
  const CSRF_TOKEN  = '<?= csrf_hash() ?>';

  const imgEl    = document.getElementById('violationImage');
  const noMsgEl  = document.getElementById('noViolationMsg');
  const details  = document.getElementById('violationDetails');
  const lastTime = document.getElementById('lastUpdatedTime');

  const timeEl   = document.getElementById('violationTime');
  const plateEl  = document.getElementById('licensePlate');
  const typeEl   = document.getElementById('carType');
  const ownerEl  = document.getElementById('carOwner');
  const addrEl   = document.getElementById('carAddress');
  const pathEl   = document.getElementById('imgPath');

  const prevBtn  = document.getElementById('prevBtn');
  const nextBtn  = document.getElementById('nextBtn');
  const delBtn   = document.getElementById('deleteBtn');
  const saveBtn  = document.getElementById('saveBtn');

  const URL_DISMISS = "<?= site_url('violation/dismiss') ?>";

    function show(index) {
        if (!violations || violations.length === 0) {
        imgEl.style.display = 'none';
        details.style.display = 'none';
        noMsgEl.style.display = 'block';
        lastTime.textContent = '';
        imgEl.dataset.index = -1;
        imgEl.dataset.id = '';
        setControlsEnabled(false);        // 沒資料：停用按鈕
        return;
        }
        // 有資料的情況下
        const i = ((index % violations.length) + violations.length) % violations.length; // 正規化 index
        const v = violations[i];

        // 圖片
        if (v.image_rel_path) {
        imgEl.src = "<?= base_url() ?>/" + v.image_rel_path;
        } else {
        imgEl.removeAttribute('src');
        }
        imgEl.dataset.index = i;
        imgEl.dataset.id = v.id;

        // 資訊
        timeEl.textContent  = v.violation_time || v.created_at || '';
        plateEl.textContent = v.license_plate || '';
        typeEl.textContent  = v.vehicle_type   || '';
        ownerEl.textContent = v.owner_name     || '(依車牌查出)';
        addrEl.textContent  = v.owner_address  || '(依車牌查出)';
        pathEl.textContent  = v.image_rel_path ? `路徑：${v.image_rel_path}` : '';

        details.style.display = 'block';
        noMsgEl.style.display = 'none';
        imgEl.style.display = 'inline-block';

        lastTime.textContent = '最後更新：' + new Date().toLocaleString();
        setControlsEnabled(true);           // 有資料：啟用按鈕
    }
    //在沒有違規圖片時不要有按鈕
    function setControlsEnabled(enabled) {
        const btns = [prevBtn, nextBtn, delBtn, saveBtn];
        btns.forEach(b => {
            b.style.display = enabled ? 'inline-block' : 'none';
        });
    }


  function currentIndex() {
    return parseInt(imgEl.dataset.index || '-1', 10);
  }

  // 切換上一張/下一張
  prevBtn.addEventListener('click', () => {
    const idx = currentIndex();
    if (idx >= 0) show(idx - 1);
  });
  nextBtn.addEventListener('click', () => {
    const idx = currentIndex();
    if (idx >= 0) show(idx + 1);
  });

    // 刪除
    delBtn.addEventListener('click', async () => {
        const idx = currentIndex();
        if (idx < 0) return;
        const v = violations[idx];

        if (!confirm(`這筆只會從待處理清單移除（不刪資料）\n#${v.id} ${v.license_plate || ''}`)) return;

        try {
            await fetch(URL_DISMISS, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', [CSRF_HEADER]: CSRF_TOKEN},
            body: JSON.stringify({ id: v.id }),
            });
        } catch (e) {
            // 即使失敗也先把畫面移除，避免卡住
            console.warn('dismiss API error:', e);
        }

        // 前端畫面移除
        violations.splice(idx, 1);
        if (violations.length === 0) {
            show(-1);
        } else {
            show(idx >= violations.length ? violations.length - 1 : idx);
        }
        alert('已從待處理清單移除');
    });


  // 儲存（更新姓名/地址到資料庫）
    saveBtn.addEventListener('click', async () => {
        const idx = currentIndex();
        if (idx < 0) return;
        const v = violations[idx];

        const payload = {
            id: v.id,
            owner:  ownerEl.textContent.trim(),
            address: addrEl.textContent.trim(),
        };

        try {
            const res = await fetch(URL_SAVE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                [CSRF_HEADER]: CSRF_TOKEN, // 如果專案有開 CSRF 就會用到
            },
            body: JSON.stringify(payload),
            });
            const json = await res.json();
            if (json.success) {
            // 更新本地快取
            v.owner_name    = payload.owner;
            v.owner_address = payload.address;

            // 從 violations 移除這筆
            violations.splice(idx, 1);

            // 顯示下一張或空畫面
            if (violations.length === 0) {
                show(-1);
            } else {
                show(idx >= violations.length ? violations.length - 1 : idx);
            }

            alert('已更新並移除當前圖片');
            } else {
            alert('更新失敗：' + (json.error || ''));
            }
        } catch (e) {
            alert('更新請求失敗：' + e.message);
        }
    });


  // 初始化顯示第一張
  show(0);
</script>
<?= $this->endSection() ?>
