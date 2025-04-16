<?= $this->extend('template') ?>
<?= $this->section('content') ?>

    <div class = find-container>
         <!-- 顯示錯誤訊息 -->
         <?php if (session()->getFlashdata('error')): ?>
            <div style="color: red;">
                <?= session()->getFlashdata('error') ?>
            </div>
            <br>
        <?php endif; ?>
        <form action="FindController/find_license_plate" method="post">
            <select name="videoSelect" class = "form-select form-select-focus"  style = "width: 100% ; display:inline-block">
                <option value="">請選擇路口及時間</option>
                <?php 
                    foreach($row as $i) 
                        echo '<option value='.$i['road_name'].'/'.$i['date'].' required>'.$i['road_name'].'---'.$i['date'].'</option>'
                ?>
            </select><br><br>
            <input name="road_name" type="hidden" required><br>
            <input name="date" type="hidden" required><br>
            <input type="submit" value="Choose"  onclick = postData() class = "btn btn-secondary">
            
        </form>

    </div>
    <script>
    function postData()
    {
        var s = document.getElementsByTagName('select');
        var arr = s[0].value.split('/');
        var btn = document.getElementsByTagName('input');
        btn[0].value = arr[0];
        btn[1].value = arr[1];
    }
</script>
<?= $this->endSection() ?>
