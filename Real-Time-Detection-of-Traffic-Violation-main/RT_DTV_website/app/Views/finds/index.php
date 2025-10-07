<?= $this->extend('template') ?>
<?= $this->section('content') ?>

<div class="find-container">
  <!-- 錯誤訊息 -->
  <?php if (session()->getFlashdata('error')): ?>
      <div style="color:red;">
          <?= session()->getFlashdata('error') ?>
      </div>
      <br>
  <?php endif; ?>

  <form method="get" action="<?= site_url('find/find_license_plate') ?>">
      <label>路口：</label>
      <select name="road_name" id="roadSelect" class="form-select" style="width:50%" required>
          <option value="" selected hidden></option>  <!-- 預設空白 -->
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="C">C</option>
          <option value="D">D</option>
          <option value="show_all_car">顯示所有路口車輛</option>
      </select>

      <label style="margin-left:10px;">日期：</label>
      <input type="date" name="date" class="form-control" style="width:200px;display:inline-block;">

      <button type="submit" class="btn btn-secondary" style="margin-left:10px;">查詢</button>
  </form>
</div>

<?= $this->endSection() ?>
