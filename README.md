# VitalPulse AI: Advanced ECG Phased Monitoring

VitalPulse AI is a comprehensive clinical dashboard designed for the automated analysis of single-lead ECG signals. Developed for the Global Hackathon, this project solves three critical cardiac monitoring challenges through a narrative, phase-based diagnostic flow.

## 🚀 The Dashboard Flow

The application is structured into three distinct analytical phases, mirroring the core requirements of the medical monitoring challenge:

### **Phase 01: Heart Rate Detection**
*   **Challenge:** Accurate R-Peak detection from noisy single-lead signals.
*   **Solution:** Implements a robust Pan-Tompkins inspired derivative filtering algorithm.
*   **Metric:** Real-time Average Heart Rate (BPM) detection.

### **Phase 02: Rhythm & AFib Analysis**
*   **Challenge:** Identifying irregular rhythms and life-threatening Atrial Fibrillation.
*   **Solution:** Analysis of R-R Interval variability (Coefficient of Variation) to detect chaotic rhythms.
*   **Metric:** Automated AFib Probability and Rhythm Classification.

### **Phase 03: Holistic Stress Assessment**
*   **Challenge:** Measuring physiological stress through Heart Rate Variability (HRV).
*   **Solution:** Advanced time-domain feature extraction (SDNN, RMSSD, pNN50) and frequency-domain estimation (LF/HF).
*   **Metric:** Poincaré Plot visualization and a proprietary Stress Scoring engine.

### **Phase ✨: AI Insights**
*   **Outcome:** A structured clinical report summarizing the patient's cardiac health, generated through heuristic AI interpretation.

## 🛠️ Tech Stack
- **Backend:** Python (Flask)
- **Signal Processing:** SciPy, WFDB, NumPy, Pandas
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript (Chart.js)
- **Typography:** Plus Jakarta Sans

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "Global hackathon"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   cd webapp
   python3 app.py
   ```
4. **Access the Dashboard:**
   Open `http://localhost:5001` in your browser.

## 📄 Database
This project utilizes the **MIT-BIH Arrhythmia Database**. The application is configured to automatically download required records from PhysioNet on first run.

---
*Developed for the Global Hackathon submission.*
