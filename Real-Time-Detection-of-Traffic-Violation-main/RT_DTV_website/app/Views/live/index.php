<?= $this->extend('template') ?>

<?= $this->section('content') ?>
    <!-- <h2>四格即時影像</h2> -->
    <!-- 影片四宮格 -->
    <div class="grid-container"> 
        <video id="video1" autoplay muted loop src="/videos/video1.mp4"></video>
        <video id="video2" autoplay muted loop src="/videos/video2.mp4"></video>
        <video id="video3" autoplay muted loop src="/videos/video3.mp4"></video>
        <video id="video4" autoplay muted loop src="/videos/video4.mp4"></video>
    </div>

    <style>
        .grid-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(2, 1fr);
            gap: 10px;
            width: 80%;
            max-width: 800px;
            margin: 20px auto;
        }
        video {
            width: 100%;
            height: auto;
            object-fit: cover;
        }
    </style>
<?= $this->endSection() ?>
