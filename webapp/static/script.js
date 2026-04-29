// Chart Global Instances
let ecgChart, hrChart, poincareChart, rhythmPie, stressPie;

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    setupEventListeners();
    updateTime();
});

function updateTime() {
    const now = new Date();
    document.getElementById('timestamp').innerText = now.toLocaleString();
}

function initCharts() {
    const ctxEcg = document.getElementById('ecgChart').getContext('2d');
    const ctxHr = document.getElementById('hrChart').getContext('2d');
    const ctxPoincare = document.getElementById('poincareChart').getContext('2d');
    const ctxRhythm = document.getElementById('rhythmPie').getContext('2d');
    const ctxStress = document.getElementById('stressPie').getContext('2d');

    // Main ECG Signal Chart
    ecgChart = new Chart(ctxEcg, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Clean ECG', data: [], borderColor: '#E11D48', borderWidth: 1.5, pointRadius: 0, fill: false }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: false }, y: { grid: { color: '#f0f0f0' } } }, plugins: { legend: { display: false } } }
    });

    // HR Trend Chart
    hrChart = new Chart(ctxHr, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'BPM', data: [], borderColor: '#E11D48', backgroundColor: 'rgba(225, 29, 72, 0.1)', fill: true, tension: 0.4 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    // Poincaré Plot
    poincareChart = new Chart(ctxPoincare, {
        type: 'scatter',
        data: { datasets: [{ label: 'RR Intervals', data: [], backgroundColor: '#E11D48' }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { title: { display: true, text: 'RR[n] ms' } }, y: { title: { display: true, text: 'RR[n+1] ms' } } } }
    });

    // Rhythm Pie
    rhythmPie = new Chart(ctxRhythm, {
        type: 'doughnut',
        data: { labels: ['Normal', 'Abnormal'], datasets: [{ data: [100, 0], backgroundColor: ['#10B981', '#EF4444'] }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '70%' }
    });

    // Stress Pie
    stressPie = new Chart(ctxStress, {
        type: 'pie',
        data: { labels: ['Low', 'Med', 'High'], datasets: [{ data: [80, 15, 5], backgroundColor: ['#10B981', '#F59E0B', '#EF4444'] }] },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function setupEventListeners() {
    document.getElementById('analyzeBtn').addEventListener('click', () => {
        const recordId = document.getElementById('recordSelect').value;
        fetchAnalysis(`/api/analyze/${recordId}`);
    });

    document.getElementById('fileInput').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setStatus('Uploading & Analyzing...');
        fetch('/api/analyze_file', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => handleResponse(data))
            .catch(err => setStatus('Error: ' + err.message));
    });
}

function setStatus(msg) {
    document.getElementById('status').innerText = msg;
}

function fetchAnalysis(url) {
    setStatus('Analyzing...');
    fetch(url)
        .then(res => res.json())
        .then(data => handleResponse(data))
        .catch(err => setStatus('Error: ' + err.message));
}

function handleResponse(data) {
    if (data.error) {
        setStatus('Error: ' + data.error);
        return;
    }

    setStatus('Analysis Complete');
    
    // Update Record Label
    document.getElementById('currentRecord').innerText = data.metrics.rhythm.includes('AFib') ? 'Warning (AFib)' : 'Stable';

    // Update Metrics
    document.getElementById('avgHr').innerText = data.metrics.avg_hr + ' BPM';
    document.getElementById('sdnn').innerText = data.metrics.sdnn + ' ms';
    document.getElementById('rmssd').innerText = data.metrics.rmssd + ' ms';
    document.getElementById('pnn50').innerText = data.metrics.pnn50 + '%';
    document.getElementById('lfHf').innerText = data.metrics.lf_hf;
    document.getElementById('afib').innerText = data.metrics.afib_perc + '%';
    document.getElementById('stressVal').innerText = data.metrics.stress_score + '% ' + data.metrics.stress_label.toUpperCase();
    
    // Update ECG Chart
    ecgChart.data.labels = data.signal_subset.map((_, i) => i);
    ecgChart.data.datasets[0].data = data.signal_subset;
    ecgChart.update();

    // Update HR Trend (Simulate a trend from RR intervals)
    const hrTrend = data.rr_intervals.map(rr => Math.round(60000 / rr));
    hrChart.data.labels = hrTrend.map((_, i) => i);
    hrChart.data.datasets[0].data = hrTrend;
    hrChart.update();

    // Update Poincaré
    const poincareData = [];
    for(let i=0; i < data.rr_intervals.length - 1; i++) {
        poincareData.push({ x: data.rr_intervals[i], y: data.rr_intervals[i+1] });
    }
    poincareChart.data.datasets[0].data = poincareData;
    poincareChart.update();

    // Update Pies
    const isAfib = data.metrics.afib_perc > 12;
    rhythmPie.data.datasets[0].data = isAfib ? [15, 85] : [95, 5];
    rhythmPie.update();

    const stress = data.metrics.stress_score;
    stressPie.data.datasets[0].data = [Math.max(0, 100-stress), stress/2, stress/2];
    stressPie.update();

    // Update AI Report
    document.getElementById('aiReport').innerHTML = formatMarkdown(data.report);
}

function formatMarkdown(text) {
    // Enhanced converter for the markdown used in the backend report
    return text
        .replace(/### (.*?)\n/g, '<h4>$1</h4>') // Headings
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
        .replace(/\n- (.*?)(?=\n|$)/g, '<br>• $1') // Bullet points
        .replace(/\n\n/g, '<br><br>') // Double newlines
        .replace(/\n(?!\<br\>|•|\<h4\>)/g, ' '); // Remove single newlines that aren't breaks
}
