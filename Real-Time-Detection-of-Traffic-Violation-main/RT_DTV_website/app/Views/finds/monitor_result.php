<?= $this->extend('template') ?>


<?= $this->section('content') ?>
    <select name="roadSelect" id="roadSelect" class = "form-select form-select-focus"  style = "width: 50% ; display:inline-block">
        <option value="">請選擇路口</option>
        <?php 
            foreach ($road as $i)
                echo '<option value='.$i.' required>'.$i.'</option>'
        ?>
        <option value="show_all_car">顯示所有路口車輛</option>
    </select><br><br>

    <div class = find-container>
            <h3 id = "no_violatation_car" hidden>沒有違規車。</h3>
            <table id = "violation_table" class = "find-table table-bordered" hidden>
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
                        <tr name = "<?= $row['road'];?>">
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
    </div>
<!-- 
    <div class = "only-one-video-container" >
        <video name = "test" class = "video" type="video/mp4" autoplay muted></video>
        <div class = "red-dot"></div>
    </div> -->
    <script>
        const violation_car = <?php echo json_encode($data);?>;
        const table = document.getElementById('violation_table');
        const table_body_rows = document.querySelectorAll('#violation_table tbody tr');
        const road_select = document.getElementById('roadSelect');
        const no_car = document.getElementById('no_violatation_car');
        const car_num = violation_car.length;


        //新增事件監聽器--選單顯示表格
        road_select.addEventListener('change', ()=>{
            console.log(road_select.value);
            set_table(road_select.value);
        });

        function set_table(road)
        {
            no_car.hidden = true;
            if(road === "")
            {
                table.hidden = true;
                return
            }
            else if(road === "show_all_car")
            {
                table.hidden = false;
                for(let i = 0; i < car_num; i++) 
                    table_body_rows[i].hidden = false;
                if(car_num == 0)
                {
                    no_car.hidden = false;
                    table.hidden = true;
                }

            }
            else
            {
                table.hidden = false;
                for(let i = 0; i < car_num; i++)
                {
                    if(table_body_rows[i].getAttribute('name') === road)
                        table_body_rows[i].hidden = false;
                    else
                        table_body_rows[i].hidden = true;
                }
            }
        }

    </script>

    
<?= $this->endSection() ?>
