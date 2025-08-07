<?= $this->extend('template') ?>

<?= $this->section('content') ?>
<h2>違規處理歷史紀錄</h2>
<table border="1" cellpadding="8" cellspacing="0">
    <thead>
        <tr>
            <th>編號</th>
            <th>操作</th>
            <th>時間</th>
        </tr>
    </thead>
    <tbody id="historyTable">
        <!-- 這邊等下用 JavaScript 動態塞資料 -->
    </tbody>
</table>
<?= $this->endSection() ?>

<?= $this->section('script') ?>
<script>
    document.addEventListener('DOMContentLoaded', loadHistory);

    async function loadHistory() {
        const response = await fetch('/LiveFeedController/get_history');
        const data = await response.json();

        const tbody = document.getElementById('historyTable');
        tbody.innerHTML = '';

        data.forEach(entry => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${entry.video_name}</td>
                <td>${entry.action}</td>
                <td>${entry.timestamp}</td>
            `;
            tbody.appendChild(tr);
        });
    }
</script>
<?= $this->endSection() ?>
