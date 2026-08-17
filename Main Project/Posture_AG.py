import os
# Silence TensorFlow & MediaPipe C++ log outputs completely
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import streamlit as st
import cv2
import pandas as pd
import numpy as np
import time
from datetime import datetime
import sys
from PIL import Image

# Local module import path
sys.path.insert(0, os.path.dirname(__file__))

import src.database as db
import src.analytics as ana
from src.alert import trigger_posture_alert
import streamlit.components.v1 as components

def load_asset_text(relative_path):
    """Loads content from assets directory safely."""
    full_path = os.path.join(os.path.dirname(__file__), "assets", relative_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

import base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

def inject_theme(theme_choice):
    if theme_choice == "System Default":
        return
        
    css_content = ""
    if theme_choice == "Light Mode":
        css_content = """
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        
        /* Ultra-premium typography enhancements */
        html, body, [class*="css"], .stMarkdown, p {
            font-family: 'Outfit', -apple-system, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
            letter-spacing: -0.01em;
        }

        /* Base animated mesh background */
        .stApp { 
            background: 
                radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 80% 20%, rgba(14, 165, 233, 0.12) 0%, transparent 40%),
                #f8fafc;
            color: #1e293b; 
        }
        
        /* Apply premium frosted glass effect to main components */
        .header-card, div[data-testid="stSidebar"] > div:first-child, .metric-box {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border-radius: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.6) !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
        }

        .header-card { padding: 30px; margin-bottom: 24px; }
        .header-title { 
            font-size: 38px; font-weight: 800; 
            background: linear-gradient(135deg, #0ea5e9, #3b82f6); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
            margin: 0; letter-spacing: -1px;
        }
        .header-subtitle { color: #64748b; font-size: 16px; margin-top: 6px; font-weight: 600; }
        
        .metric-box { padding: 16px; text-align: center; }
        .metric-val { font-size: 32px; font-weight: 800; color: #0ea5e9; }
        .metric-lbl { font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
        
        /* Safely make the top header transparent instead of hiding it */
        header[data-testid="stHeader"] { background-color: transparent !important; box-shadow: none !important; }
        [data-testid="stSidebar"] { background-color: transparent !important; }
        
        /* Hide the Streamlit three-dot toolbar completely for production presentation */
        [data-testid="stToolbar"] { display: none !important; }
        
        /* Hide the sidebar collapse arrow button */
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        
        /* Force light mode text safely */
        label, p, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] p { color: #1e293b !important; }
        """
    elif theme_choice == "Dark Mode":
        css_content = """
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"], .stMarkdown, p {
            font-family: 'Outfit', -apple-system, sans-serif !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
            letter-spacing: -0.01em;
        }

        /* Deep Neon-Glass Background */
        .stApp { 
            background: 
                radial-gradient(circle at 15% 50%, rgba(14, 165, 233, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                #09090b;
            color: #f8fafc; 
        }
        
        /* Neon Frosted Glass Panels */
        .header-card, div[data-testid="stSidebar"] > div:first-child, .metric-box {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(32px) !important;
            -webkit-backdrop-filter: blur(32px) !important;
            border-radius: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        }

        .header-card { padding: 30px; margin-bottom: 24px; }
        .header-title { 
            font-size: 38px; font-weight: 800; 
            background: linear-gradient(135deg, #38bdf8, #a78bfa); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
            margin: 0; letter-spacing: -1px;
        }
        .header-subtitle { color: #94a3b8; font-size: 16px; margin-top: 6px; font-weight: 500; }
        
        .metric-box { padding: 16px; text-align: center; }
        .metric-val { font-size: 32px; font-weight: 800; color: #38bdf8; text-shadow: 0 0 20px rgba(56, 189, 248, 0.4); }
        .metric-lbl { font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
        
        /* Safely make the top header transparent */
        header[data-testid="stHeader"] { background-color: transparent !important; box-shadow: none !important; }
        [data-testid="stSidebar"] { background-color: transparent !important; }
        
        /* Hide the Streamlit three-dot toolbar completely for production presentation */
        [data-testid="stToolbar"] { display: none !important; }
        
        /* Hide the sidebar collapse arrow button */
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        
        /* Force dark mode widget text specifically without breaking buttons/icons */
        label, .stMarkdown p, .stMarkdown li, h1, h2, h3, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] p {
            color: #f8fafc !important; 
        }
        
        /* Fix Alerts (Info Boxes) */
        [data-testid="stAlert"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        [data-testid="stAlert"] p, [data-testid="stAlert"] span { color: #f8fafc !important; }
        
        /* Fix Secondary Buttons */
        button[kind="secondary"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }
        button[kind="secondary"] p { color: #f8fafc !important; }
        """
        
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# --------------------------------------------------
# Page Configuration & Theme Initialization
# --------------------------------------------------
tab_logo = Image.open(os.path.join(os.path.dirname(__file__), "splash_screen", "logo.png"))

st.set_page_config(
    page_title="Spine Sense AI | Neural Ergonomic Coach",
    page_icon=tab_logo,
    layout="wide",
    initial_sidebar_state="expanded"
)

db.init_db()

# Session State Initializations
if 'session_active' not in st.session_state:
    st.session_state.session_active = False
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = None
if 'slouch_count' not in st.session_state:
    st.session_state.slouch_count = 0
if 'audio_enabled' not in st.session_state:
    st.session_state.audio_enabled = True

# Executive Header Card
logo_path = os.path.join(os.path.dirname(__file__), "splash_screen", "logo.png")
logo_b64 = get_base64_image(logo_path)

st.markdown(f"""
<div class="header-card" style="display: flex; align-items: center; gap: 24px;">
    <div class="header-logo" style="width: 85px; height: 85px; flex-shrink: 0; background: #ffffff; border-radius: 22px; display: flex; align-items: center; justify-content: center; box-shadow: 0 12px 25px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.02) inset; padding: 10px; box-sizing: border-box;">
        <img src="data:image/png;base64,{logo_b64}" style="max-width: 100%; max-height: 100%;">
    </div>
    <div>
        <div class="header-title">Spine Sense AI</div>
        <div class="header-subtitle">Real-Time Neural Ergonomic Posture & Spinal Health System</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar Control Center
# --------------------------------------------------
st.sidebar.title("Posture Control Center")
user_name = st.sidebar.text_input("Name", value="")
st.session_state.audio_enabled = st.sidebar.checkbox("Enable Audio Alerts 🔊", value=True)

st.sidebar.markdown("---")
theme_choice = st.sidebar.radio("UI Theme", ["Light Mode", "Dark Mode", "System Default"])
inject_theme(theme_choice)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Session Summary")
summary = db.get_summary_stats()
st.sidebar.metric("Total Sessions", summary["total_sessions"])
st.sidebar.metric("Overall Avg Score", f"{summary['overall_avg_score']}%")
st.sidebar.metric("Total Time Monitored", f"{summary['total_duration_min']} mins")

st.sidebar.markdown("---")
if st.sidebar.button("Clear Database History", use_container_width=True):
    db.clear_all_db()
    st.session_state.session_active = False
    st.session_state.current_session_id = None
    st.session_state.slouch_count = 0
    st.sidebar.success("Database cleared successfully!")
    st.rerun()

# --------------------------------------------------
# Main Navigation Tabs
# --------------------------------------------------
tab_monitor, tab_analytics, tab_db = st.tabs([
    "Live Posture Monitor", 
    "Analytics", 
    "Data Logs"
])

# ==================================================
# TAB 1: HIGH-PRECISION 2K NEURAL VISION ENGINE
# ==================================================
with tab_monitor:
    col_video, col_stats = st.columns([1.8, 1.2])

    with col_stats:
        st.subheader("Session Control Center")
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if not st.session_state.session_active:
                if st.button("Start Session", type="primary"):
                    st.session_state.session_active = True
                    st.session_state.session_start_time = datetime.now()
                    st.session_state.current_session_id = db.create_session(user_name)
                    st.session_state.slouch_count = 0
                    st.rerun()
            else:
                if st.button("End Session", type="secondary"):
                    st.session_state.session_active = False
                    if st.session_state.current_session_id:
                        dur = int((datetime.now() - st.session_state.session_start_time).total_seconds())
                        logs = db.get_session_logs(st.session_state.current_session_id)
                        avg_sc = logs['posture_score'].mean() if not logs.empty else 85.0
                        risk = "Low" if avg_sc >= 80 else ("Moderate" if avg_sc >= 65 else "High")
                        db.end_session(st.session_state.current_session_id, duration_sec=dur,
                                       avg_score=avg_sc, slouch_count=st.session_state.slouch_count, risk_level=risk)
                    st.success("Session saved to SQLite Database!")
                    st.rerun()

        with btn_col2:
            if st.button("Calibrate"):
                st.toast("Sit upright facing camera to calibrate baseline!")

        st.markdown("---")
        if st.session_state.session_active and st.session_state.session_start_time:
            elapsed_sec = int((datetime.now() - st.session_state.session_start_time).total_seconds())
            hrs = elapsed_sec // 3600
            mins = (elapsed_sec % 3600) // 60
            secs = elapsed_sec % 60
            timer_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
            
            st.success(f"🟢 Session #{st.session_state.current_session_id} Active • ⏱️ Elapsed Time: **{timer_str}**")
            st.metric("🚨 Slouch Incidents Tracked", st.session_state.slouch_count)
        else:
            st.info("Click **Start Session** to begin session timer & posture tracking.")

        st.markdown("---")
        st.markdown("""
        Sit Better, Work Longer
        Gentle alerts to help you catch yourself slouching before your neck and shoulders start aching at the end of the day.
        """)

    with col_video:
        st.subheader("Posture Monitor Module")
        
        # Load custom component
        camera_component = components.declare_component("camera_component", path=os.path.join(os.path.dirname(__file__), "assets", "camera_component"))
        
        start_time_ts = st.session_state.session_start_time.timestamp() if st.session_state.session_active and st.session_state.session_start_time else None
        
        component_value = camera_component(
            session_active=st.session_state.session_active,
            session_start_time=start_time_ts,
            key="camera_module"
        )

        if component_value:
            # Update slouch count state if changed
            if component_value.get("slouch_count", 0) > st.session_state.slouch_count:
                st.session_state.slouch_count = component_value.get("slouch_count", 0)
                st.rerun()
                
            # Log real-time data to DB
            if st.session_state.session_active and st.session_state.current_session_id:
                t_str = datetime.now().strftime("%H:%M:%S")
                db.add_posture_log(
                    st.session_state.current_session_id,
                    t_str,
                    component_value.get("neck_angle", 12.0),
                    component_value.get("shoulder_slope", 1.5),
                    component_value.get("score", 100),
                    component_value.get("status", "EXCELLENT POSTURE")
                )

# ==================================================
# TAB 2: HEALTH & PERFORMANCE ANALYTICS
# ==================================================
with tab_analytics:
    st.header("📊 Ergonomic Performance Analytics")
    sessions_df = db.get_all_sessions()
    
    if not sessions_df.empty:
        session_list = [f"Session #{row['session_id']} - {row['user_name']} ({row['start_time']})" for _, row in sessions_df.iterrows()]
        selected_session_str = st.selectbox("Select Session to Analyze:", session_list)
        selected_id = int(selected_session_str.split("#")[1].split(" ")[0])
        
        logs_df = db.get_session_logs(selected_id)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        if not logs_df.empty:
            avg_sc = round(logs_df['posture_score'].mean(), 1)
            min_sc = round(logs_df['posture_score'].min(), 1)
            max_sc = round(logs_df['posture_score'].max(), 1)
            col_c1.metric("Average Score", f"{avg_sc}%")
            col_c2.metric("Lowest Score (Dip)", f"{min_sc}%")
            col_c3.metric("Peak Score", f"{max_sc}%")
            
        st.markdown("---")
        
        col_g1, col_g2 = st.columns([1.8, 1.2])
        with col_g1:
            st.pyplot(ana.plot_score_timeline(logs_df))
        with col_g2:
            st.pyplot(ana.plot_posture_breakdown(logs_df))
            
        st.markdown("---")
        st.subheader("Multi-Session Historical Trend")
        st.pyplot(ana.plot_weekly_trend(sessions_df))
    else:
        st.info("No session records found. Start a session in the Neural Vision Monitor tab!")

# ==================================================
# TAB 3: SQL DATABASE & LOGS
# ==================================================
with tab_db:
    st.header("SQL Database & Log Inspection")
    st.markdown("Direct database queries from SQLite (`ergopulse.db`).")
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        if st.button("Refresh Database Tables"):
            st.rerun()
    with col_d2:
        if st.button("Clear All Sessions & Logs"):
            db.clear_all_db()
            st.success("All sessions cleared from SQLite!")
            st.rerun()

    sessions_df = db.get_all_sessions()
    st.subheader("📋 `sessions` Table")
    st.dataframe(sessions_df, use_container_width=True)
    
    if not sessions_df.empty:
        selected_id_db = st.number_input("Enter Session ID for granular posture logs:", 
                                         min_value=int(sessions_df['session_id'].min()), 
                                         max_value=int(sessions_df['session_id'].max()), 
                                         value=int(sessions_df['session_id'].max()))
        
        logs_df = db.get_session_logs(selected_id_db)
        st.subheader(f"🔍 `posture_logs` Table for Session #{selected_id_db}")
        st.dataframe(logs_df, use_container_width=True)
        
        csv_data = logs_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Session Report (CSV)",
            data=csv_data,
            file_name=f"Posture_session_{selected_id_db}_report.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        st.subheader("Analytics Report")
        st.markdown("Download an aggregated dataset of the last 7 days. Data is mathematically averaged by the hour for optimal trend analysis.")
        last_week_df = db.get_last_week_data()
        if not last_week_df.empty:
            st.download_button(
                label="Download 7-Day Hourly Averages (CSV)",
                data=last_week_df.to_csv(index=False).encode('utf-8'),
                file_name="SpineSenseAI_Hourly_Analytics.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No data available for the last 7 days.")
