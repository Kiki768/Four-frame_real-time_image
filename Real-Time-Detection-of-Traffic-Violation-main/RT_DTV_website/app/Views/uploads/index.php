<?= $this->extend('template') ?>
<?= $this->section('content') ?>
    <style>
        .upload-container {
            display: grid;
            /*text-align:center;*/
            justify-content: center; /* 垂直居中 */
        }
    </style>
    <div class = upload-container >
    <form method="post" enctype="multipart/form-data" action="/UploadController/upload">
        <!-- 限制上傳檔案的最大值 -->
        <!-- <input type="hidden" name="MAX_FILE_SIZE" value="2097152"> -->
         <!-- 錯誤訊息 -->
        <?php if (session()->getFlashdata('error')): ?>
            <div style="color: red;">
                <?= session()->getFlashdata('error') ?>
            </div>
            <br>
        <?php endif; ?>

        <input type="file" name="my_file" accept = "video/mp4" multiple class = "form-control"required style = "display:inline-block" > <!--上傳多檔案 + 指定mp4-->
        <br><br>
        <select name="road_original" id="road_original" class = "form-select form-select-focus"  style = "width: 50% ; display:inline-block">
            <option value="">請選擇路口</option>
            <?php 
                foreach($row as $i) 
                    echo '<option value='.$i['road_name'].' required>'.$i['road_name'].'</option>'
            ?>
        </select><br><br>
        <label for="road_append" >新增路口名稱:</label>
        <input type="text" name="road_append" id = "road_append" placeholder="填寫路口名稱" style = "border-radius: 0.375rem; border: 1px solid #ced4da;"><br><br>
        <input name="road" type="hidden" required><br>
        <input type="submit" value="Upload" onclick = postData() class = "btn btn-secondary" >
        </form>
    </div>




<script>
    function postData()
    {
        var s = document.getElementsByTagName('select');
        var btn = document.getElementsByTagName('input');
        btn[2].value = s[0].value;
        if(btn[1].value !== "")
        {
            btn[2].value = btn[1].value;
        }
        console.log(btn[1], btn[2]);
    }
</script>
<?= $this->endSection() ?>




