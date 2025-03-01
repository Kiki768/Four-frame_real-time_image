<?= $this->extend('template') ?>
<?= $this->section('content') ?>

    <div class = find-container>
        
        
        <?php if (isset($data) && !empty($data)): ?>
            <table class = "find-table table-bordered">
                <caption>違規車輛</caption>
                <thead>
                    <tr>
                        <th>車牌號碼</th>
                        <th>日期</th>
                        <th>路口</th>
                        <th>違規照片</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach($data as $row): ?>
                        <tr>
                            <td><?= $row['license_plate']; ?></td>
                            <td><?= $row['date']; ?></td>
                            <td><?= $row['road']; ?></td>
                            <td>
                                <?php if (!empty($row['img_path'])): ?>
                                    <a href= "<?= base_url($row['img_path']) ?>" download >
                                        <img src= "<?= base_url('download.ico') ?>" rel="download"  style = "width: 20px; height: auto;">
                                    </a>
                                <?php else: ?>
                                    <img src= "<?= base_url('download.ico') ?>" rel="download"  style = "width: 20px; height: auto;">
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>

            <?php else: ?>
                <h3>沒有違規車。</h3>
            <?php endif; ?>
    </div>


<?= $this->endSection() ?>

