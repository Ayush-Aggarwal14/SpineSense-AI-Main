# 🏆 Inter-School Computer Competition Project Brief

### 1. Problem Statement
Students and computer professionals spend 6 to 8 hours daily sitting in front of screens. 
Improper ergonomic posture leads to:
- **Tech-Neck & Cervical Strain**: Forward head tilt increases effective head weight on the spine up to 27 kg (60 lbs).
- **Spinal Misalignment & Slouching**: Reduces lung capacity by up to 30% and induces early fatigue.
- **Lack of Awareness**: Users are unaware when they gradually slouch during long study sessions.

### 2. The Solution: ErgoPulse AI
ErgoPulse AI acts as a **24/7 intelligent ergonomic companion** that runs locally via a webcam feed to monitor posture in real-time without requiring any wearable sensors.

### 3. AI & Technical Architecture
- **Computer Vision**: Utilizes Google MediaPipe `PoseLandmarker` to extract 33 spatial landmarks (X, Y, Z) in real-time.
- **Vector Mathematics & Geometry**: Calculates neck tilt angles, shoulder slants, and normalized screen distance ratios.
- **Dynamic Scoring Engine**: Computes a continuous 0% to 100% Ergonomic Score with color-coded skeleton feedback (Green / Yellow / Red).
- **Database & Data Science**: Stores logs in an **SQLite** database and processes analytics via **Pandas** and publication-grade **Matplotlib** graphs.

### 4. Tech Stack Breakdown
- **Core Language**: Python 3.14
- **AI / Vision**: MediaPipe Tasks, OpenCV
- **Data Science**: Pandas, NumPy
- **Visualization**: Matplotlib
- **Database**: SQLite
- **Web GUI**: Streamlit with Custom Glassmorphism CSS
