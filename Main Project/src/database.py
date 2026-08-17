import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ergopulse.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            duration_sec INTEGER DEFAULT 0,
            avg_score REAL DEFAULT 0.0,
            slouch_count INTEGER DEFAULT 0,
            risk_level TEXT DEFAULT 'Low'
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS posture_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp TEXT,
            neck_angle REAL,
            shoulder_slope REAL,
            posture_score REAL,
            status TEXT DEFAULT 'EXCELLENT POSTURE',
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    ''')
    
    # Schema Auto-Migration: Ensure status column exists in existing SQLite tables
    c.execute("PRAGMA table_info(posture_logs)")
    columns = [row[1] for row in c.fetchall()]
    if 'status' not in columns:
        try:
            c.execute("ALTER TABLE posture_logs ADD COLUMN status TEXT DEFAULT 'EXCELLENT POSTURE'")
        except Exception:
            pass
            
    conn.commit()
    conn.close()

def create_session(user_name="Student"):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sessions (user_name, start_time) VALUES (?, ?)", (user_name, now_str))
    conn.commit()
    session_id = c.lastrowid
    conn.close()
    return session_id

def end_session(session_id, duration_sec, avg_score, slouch_count, risk_level):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        UPDATE sessions 
        SET end_time = ?, duration_sec = ?, avg_score = ?, slouch_count = ?, risk_level = ?
        WHERE session_id = ?
    ''', (now_str, duration_sec, avg_score, slouch_count, risk_level, session_id))
    conn.commit()
    conn.close()

def add_posture_log(session_id, timestamp_str, neck_angle, shoulder_slope, posture_score, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO posture_logs (session_id, timestamp, neck_angle, shoulder_slope, posture_score, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, timestamp_str, neck_angle, shoulder_slope, posture_score, status))
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM sessions ORDER BY session_id DESC", conn)
    conn.close()
    return df

def get_session_logs(session_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM posture_logs WHERE session_id = ? ORDER BY log_id ASC", conn, params=(session_id,))
    conn.close()
    return df

def get_summary_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*), AVG(avg_score), SUM(duration_sec) FROM sessions WHERE end_time IS NOT NULL")
    row = c.fetchone()
    conn.close()
    
    total_sessions = row[0] if row[0] else 0
    overall_avg_score = round(row[1], 1) if row[1] else 0.0
    total_duration_min = round((row[2] if row[2] else 0) / 60.0, 1)
    
    return {
        "total_sessions": total_sessions,
        "overall_avg_score": overall_avg_score,
        "total_duration_min": total_duration_min
    }

def get_last_week_data():
    conn = get_connection()
    query = """
        SELECT 
            date(s.start_time) as session_date,
            substr(p.timestamp, 1, 2) || ':00:00' as session_hour,
            s.user_name,
            COUNT(p.log_id) as total_readings,
            ROUND(AVG(p.posture_score), 1) as avg_posture_score,
            ROUND(AVG(p.neck_angle), 1) as avg_neck_angle,
            ROUND(AVG(p.shoulder_slope), 1) as avg_shoulder_slant
        FROM posture_logs p
        JOIN sessions s ON p.session_id = s.session_id
        WHERE date(s.start_time) >= date('now', '-7 days')
        GROUP BY session_date, session_hour, s.user_name
        ORDER BY session_date DESC, session_hour DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def clear_all_db():
    """Wipes all sessions and logs for database reset by completely rebuilding schema."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS posture_logs")
    c.execute("DROP TABLE IF EXISTS sessions")
    conn.commit()
    conn.close()
    init_db()
