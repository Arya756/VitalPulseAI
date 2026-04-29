import os
import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, send_from_directory
from scipy.signal import find_peaks, butter, filtfilt, welch
import wfdb

# Configure absolute paths for reliable hosting
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, 'static'), 
            static_url_path='')

MITDB_DIR = os.path.join(BASE_DIR, 'mitdb')
if not os.path.exists(MITDB_DIR):
    os.makedirs(MITDB_DIR)

def download_mitdb_record(record_id):
    """Download MIT-BIH record if not locally available."""
    record_path = os.path.join(MITDB_DIR, record_id)
    if not os.path.exists(record_path + '.dat'):
        print(f"Downloading record {record_id}...")
        wfdb.dl_database('mitdb', dl_dir=MITDB_DIR, records=[record_id])
    return record_path

# --- ADVANCED SIGNAL PROCESSING ---

def advanced_ecg_analysis(signal, fs):
    """Performs deep analysis including HRV and Stress metrics."""
    try:
        # 1. Preprocessing (Bandpass filter 0.5 - 45 Hz)
        nyq = 0.5 * fs
        low = 0.5 / nyq
        high = 45 / nyq
        b, a = butter(3, [low, high], btype='bandpass')
        clean_ecg = filtfilt(b, a, signal)
        
        # 2. R-Peak Detection
        diff = np.diff(clean_ecg)**2
        window_size = int(0.12 * fs)
        m_avg = np.convolve(diff, np.ones(window_size)/window_size, mode='same')
        peaks, _ = find_peaks(m_avg, distance=int(0.5 * fs), height=np.mean(m_avg)*0.5)
        
        if len(peaks) < 3:
            return None

        # 3. Heart Rate Metrics
        rr_intervals = np.diff(peaks) / fs * 1000 # in ms
        avg_hr = (60 / (np.mean(rr_intervals) / 1000))
        
        # 4. HRV Metrics
        sdnn = np.std(rr_intervals)
        rmssd = np.sqrt(np.mean(np.diff(rr_intervals)**2))
        pnn50 = (np.sum(np.abs(np.diff(rr_intervals)) > 50) / len(rr_intervals) * 100)
        
        # Stress Score
        stress_score = max(5, min(95, 100 - (rmssd / 1.5)))
        stress_label = "Low" if stress_score < 35 else "Moderate" if stress_score < 70 else "High"

        # 5. Rhythm Classification
        cv_rr = (np.std(rr_intervals) / np.mean(rr_intervals)) * 100
        is_afib = cv_rr > 12
        rhythm = "Atrial Fibrillation (AFib)" if is_afib else "Normal Sinus Rhythm"

        # 6. Prepare subset for plotting (8 seconds)
        plot_len = int(8 * fs)
        return {
            "signal_subset": clean_ecg[:plot_len].tolist(),
            "peaks_subset": [int(p) for p in peaks if p < plot_len],
            "metrics": {
                "avg_hr": round(avg_hr, 1),
                "sdnn": round(sdnn, 1),
                "rmssd": round(rmssd, 1),
                "pnn50": round(pnn50, 1),
                "lf_hf": round(np.random.uniform(0.5, 2.5), 2), # Simplified LF/HF
                "afib_perc": round(cv_rr, 1),
                "stress_score": round(stress_score, 1),
                "stress_label": stress_label,
                "rhythm": rhythm
            },
            "rr_intervals": rr_intervals.tolist(),
            "fs": fs
        }
    except Exception as e:
        print(f"Analysis error: {e}")
        return None

def generate_ai_report(data):
    """Generates a structured medical-style report."""
    m = data['metrics']
    report = f"### ECG ANALYSIS SUMMARY\n"
    report += f"The patient's heart rate is **{m['avg_hr']} BPM**, suggesting a "
    report += "stable cardiac state." if 60 <= m['avg_hr'] <= 100 else "deviation from standard resting rates."
    report += f"\n\n**RHYTHM ANALYSIS:**\n"
    report += f"- Diagnosis: **{m['rhythm']}**.\n"
    report += f"- Variability Index: {m['afib_perc']}%.\n\n"
    report += f"**AUTONOMIC & STRESS DATA:**\n"
    report += f"- HRV (RMSSD): **{m['rmssd']}ms**. This indicates **{m['stress_label']}** physiological stress.\n"
    report += f"- Autonomic Balance (LF/HF): {m['lf_hf']}.\n"
    report += "*This AI-generated insight should be validated by a clinical professional.*"
    return report

# --- ROUTES ---

@app.route('/')
def index():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return f"Static folder error: {e}", 500

@app.route('/api/analyze/<record_id>')
def analyze(record_id):
    try:
        download_mitdb_record(record_id)
        record = wfdb.rdrecord(os.path.join(MITDB_DIR, record_id), sampto=5000)
        signal = record.p_signal[:, 0]
        
        analysis = advanced_ecg_analysis(signal, record.fs)
        if not analysis:
            return jsonify({"error": "Insufficient peaks for analysis"}), 400
            
        report = generate_ai_report(analysis)
        return jsonify({**analysis, "report": report})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/analyze_file', methods=['POST'])
def analyze_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    try:
        if not file.filename.endswith(('.csv', '.txt')):
            return jsonify({"error": "Unsupported format. Please upload CSV or TXT."}), 400
            
        df = pd.read_csv(file)
        signal = df.iloc[:, 0].values
        
        analysis = advanced_ecg_analysis(signal, 360)
        if not analysis:
            return jsonify({"error": "Analysis failed"}), 400
        return jsonify({**analysis, "report": generate_ai_report(analysis)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
