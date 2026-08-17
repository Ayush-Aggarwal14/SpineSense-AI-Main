-- ====================================================================
-- SpineSense AI / ErgoPulse - Database Schema Definition
-- System: Real-Time Neural Ergonomic Posture & Spinal Health System
-- Compatibility: SQLite 3, PostgreSQL, MySQL
-- ====================================================================

PRAGMA foreign_keys = ON;

-- --------------------------------------------------------------------
-- Table: sessions
-- Description: Stores individual user posture monitoring sessions
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    session_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name       TEXT NOT NULL,
    start_time      TEXT NOT NULL,                                      -- Format: YYYY-MM-DD HH:MM:SS
    end_time        TEXT,                                               -- Format: YYYY-MM-DD HH:MM:SS
    duration_sec    INTEGER DEFAULT 0,                                  -- Total duration in seconds
    avg_score       REAL DEFAULT 0.0,                                   -- Overall average posture score (0.0 - 100.0)
    slouch_count    INTEGER DEFAULT 0,                                  -- Number of poor posture slouch alerts triggered
    risk_level      TEXT DEFAULT 'Low' CHECK (risk_level IN ('Low', 'Moderate', 'High', 'Critical'))
);

-- --------------------------------------------------------------------
-- Table: posture_logs
-- Description: Stores high-frequency posture telemetry logs per session
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS posture_logs (
    log_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL,
    timestamp       TEXT NOT NULL,                                      -- Format: HH:MM:SS
    neck_angle      REAL NOT NULL,                                      -- Measured cervical neck angle deviation in degrees
    shoulder_slope  REAL NOT NULL,                                      -- Measured bi-acromial shoulder slope slant in degrees
    posture_score   REAL NOT NULL,                                      -- Calculated ergonomic posture score (0 - 100)
    status          TEXT DEFAULT 'EXCELLENT POSTURE',                   -- Posture status classification
    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
);

-- --------------------------------------------------------------------
-- Indexes for High Performance Queries
-- --------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_posture_logs_session_id ON posture_logs (session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions (start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_user_name ON sessions (user_name);

-- --------------------------------------------------------------------
-- Analytical View: view_session_summaries
-- Description: Aggregated overview of completed posture sessions
-- --------------------------------------------------------------------
CREATE VIEW IF NOT EXISTS view_session_summaries AS
SELECT 
    s.session_id,
    s.user_name,
    s.start_time,
    s.end_time,
    s.duration_sec,
    ROUND(s.duration_sec / 60.0, 2) AS duration_minutes,
    s.avg_score,
    s.slouch_count,
    s.risk_level,
    COUNT(p.log_id) AS total_log_entries,
    ROUND(AVG(p.neck_angle), 2) AS calculated_avg_neck_angle,
    ROUND(AVG(p.shoulder_slope), 2) AS calculated_avg_shoulder_slope
FROM sessions s
LEFT JOIN posture_logs p ON s.session_id = p.session_id
GROUP BY s.session_id;

-- --------------------------------------------------------------------
-- Useful Analytics Query Samples
-- --------------------------------------------------------------------

-- 1. Get 7-day hourly rolling average analytics:
-- SELECT 
--     date(s.start_time) AS session_date,
--     substr(p.timestamp, 1, 2) || ':00:00' AS session_hour,
--     s.user_name,
--     COUNT(p.log_id) AS total_readings,
--     ROUND(AVG(p.posture_score), 1) AS avg_posture_score,
--     ROUND(AVG(p.neck_angle), 1) AS avg_neck_angle,
--     ROUND(AVG(p.shoulder_slope), 1) AS avg_shoulder_slant
-- FROM posture_logs p
-- JOIN sessions s ON p.session_id = s.session_id
-- WHERE date(s.start_time) >= date('now', '-7 days')
-- GROUP BY session_date, session_hour, s.user_name
-- ORDER BY session_date DESC, session_hour DESC;

-- 2. Overall aggregate statistics:
-- SELECT 
--     COUNT(*) AS total_sessions,
--     ROUND(AVG(avg_score), 1) AS overall_avg_score,
--     ROUND(SUM(duration_sec) / 60.0, 1) AS total_duration_minutes
-- FROM sessions 
-- WHERE end_time IS NOT NULL;
