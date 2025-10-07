<?= $this->extend('template') ?>
<?= $this->section('content') ?>
    <div class="img-container">
        <img src="pictures/tutorial_1.png" alt="tutorial">
        <img src="pictures/tutorial_2.png" alt="tutorial">
        <img src="pictures/tutorial_3.png" alt="tutorial">
    </div> 

    <style>
    .img-container {
        text-align: center; /* 圖片整體置中 */
    }
    .img-container img {
        width: 80%;
        max-width: 3000px; /* 最大寬度 300px */
        height: auto;
        margin: 10px;
        border-radius: 8px;
    }
    </style>


<?= $this->endSection() ?>

