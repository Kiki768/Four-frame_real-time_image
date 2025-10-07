<?= $this->extend('template') ?>
<?= $this->section('content') ?>

<style>
  .table-grid { border-collapse: collapse; width: 100%; }
  .table-grid th, .table-grid td { border: 1px solid #333; padding: 8px 10px; vertical-align: middle; }
  .table-grid th { background: #f5f5f5; text-align: left; }
  .status-saved { color:#1b8a5a; font-weight:700; }
  .status-dismissed { color:#c92a2a; font-weight:700; }
  .status-pending { color:#555; font-weight:700; }
</style>

<select id="roadSelect" class="form-select" style="width:50%;display:inline-block">
  <option value="" selected disabled>請選擇路口</option>
  <?php foreach (($roads ?? []) as $r): ?>
    <option value="<?= esc($r) ?>"><?= esc($r) ?></option>
  <?php endforeach; ?>
  <option value="show_all_car">顯示所有路口車輛</option>
</select>

<div id="results" hidden>
  <h3 style="margin:16px 0 8px;">違規車輛</h3>

  <table id="violation_table" class="table-grid">
    <thead>
      <tr>
        <th style="width:120px;">操作</th>
        <th style="width:110px;">編號(car id)</th>
        <th style="width:260px;">檔名</th>
        <th>車牌號碼</th>
        <th style="width:140px;">日期</th>
        <th style="width:80px;">路口</th>
        <th style="width:80px;">違規照片</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach (($data ?? []) as $row): ?>
        <?php
          $rel   = $row['image_rel_path'] ?? '';
          $parts = explode('/', $rel);
          $videoDir = count($parts) >= 3 ? $parts[count($parts)-3] : '';
          $carId = '';
          if (preg_match('/car(\d+)\.\w+$/', $rel, $m)) $carId = $m[1];

          $status = $row['status'] ?? 'pending';
          $statusHtml = $status === 'saved'
              ? '<span class="status-saved">儲存</span>'
              : ($status === 'dismissed'
                  ? '<span class="status-dismissed">刪除</span>'
                  : '<span class="status-pending">待處理</span>');

          $dateRaw = ($status === 'pending')
              ? ($row['created_at'] ?? '')
              : ($row['reviewed_at'] ?? ($row['created_at'] ?? ''));
          $date = substr($dateRaw, 0, 10);
        ?>
        <tr data-road="<?= esc($row['road'] ?? '') ?>">
          <td><?= $statusHtml ?></td>
          <td><?= esc($carId) ?></td>
          <td><?= esc($videoDir) ?></td>
          <td><?= esc($row['license_plate']) ?></td>
          <td><?= esc($date) ?></td>
          <td><?= esc($row['road']) ?></td>
          <td>
            <?php if (!empty($rel)): ?>
              <a href="<?= base_url($rel) ?>" download>
                <img src="<?= base_url('download.ico') ?>" style="width:20px;height:auto;">
              </a>
            <?php endif; ?>
          </td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</div>

<script>
  const roadSelect = document.getElementById('roadSelect');
  const results    = document.getElementById('results');
  const tableRows  = document.querySelectorAll('#violation_table tbody tr');

  results.hidden = true;
  tableRows.forEach(tr => tr.style.display = 'none');

  roadSelect.addEventListener('change', () => {
    const val = roadSelect.value;
    if (!val) {
      results.hidden = true;
      tableRows.forEach(tr => tr.style.display = 'none');
      return;
    }
    results.hidden = false;

    tableRows.forEach(tr => {
      const r = tr.getAttribute('data-road') || '';
      tr.style.display = (val === 'show_all_car' || r === val) ? '' : 'none';
    });
  });
</script>

<?= $this->endSection() ?>
