<?= $this->extend('template') ?>
<?= $this->section('content') ?>

    <div class = check-container>
        <form action="/CheckController/folder_to_database" method="post">
            <input type="submit" value="將檔案寫入資料庫" class = "btn btn-secondary">
        </form>
        </br>
        <form action="/CheckController/is_run" method="post">
            <input type="submit" value="將影片變成沒有跑過" class = "btn btn-secondary">
        </form>
        </br>
        <form action="/CheckController/delete_violation_car" method="post">
            <input type="submit" value="刪除違規車資料庫" class = "btn btn-secondary">
        </form>
        
    </div>
<?= $this->endSection() ?>
