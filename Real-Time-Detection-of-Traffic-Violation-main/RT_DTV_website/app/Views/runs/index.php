<?= $this->extend('template') ?>
<?= $this->section('content') ?>
    <style>
        .run-container {
            display: grid;
            text-align:center;
            justify-content: center; /* 垂直居中 */
        }
    </style>
    <div class = run-container>
        <?php if (session()->getFlashdata('error')): ?>
            <div style="color: red;">
                <?= session()->getFlashdata('error') ?>
            </div>
            <br>
        <?php endif; ?>
        <form action="/RunController/run" method="post">
            <select name="videoSelect" class = "form-select form-select-focus"  style = "width: 50% ; display:inline-block">
                <option value="">請選擇影片</option>
                <?php 
                    foreach($row as $i) 
                        echo '<option value='.$i['videoname'].' required>'.$i['videoname'].'</option>'
                ?>
            </select><br><br>
            <input name="videoname" type="hidden" required><br>
            <input type="submit" value="Choose"  onclick = postData() class = "btn btn-secondary">
        </form>
    </div>
    <script>
        function postData()
        {
            var s = document.getElementsByTagName('select');
            var btn = document.getElementsByTagName('input');
            btn[0].value = s[0].value;
        }
    </script>
<?= $this->endSection() ?>
