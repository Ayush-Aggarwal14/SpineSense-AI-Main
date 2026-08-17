# SpineSense AI - Database Documentation

This folder contains the database scripts, schemas, and SQL dump files for the **SpineSense AI (ErgoPulse)** system.

---

## 📁 Files Overview

1. **[`schema.sql`](file:///c:/Users/hp/OneDrive/Documents/GitHub/SpineSense%20AI%20Main/Database/schema.sql)**
   - Clean DDL schema definitions for initializing a fresh database.
   - Includes table schemas (`sessions`, `posture_logs`), performance indexes, analytical views (`view_session_summaries`), and sample SQL analytical queries.
   - Compatible with SQLite 3, MySQL, and PostgreSQL.

2. **[`spinesense_db.sql`](file:///c:/Users/hp/OneDrive/Documents/GitHub/SpineSense%20AI%20Main/Database/spinesense_db.sql)**
   - Complete SQL database dump (DDL + DML) exported directly from the live `ergopulse.db`.
   - Contains all recorded historical sessions and posture telemetry logs.

---

## 🗄️ Database Architecture

### 1. `sessions` Table
Stores high-level metadata for each monitoring session.

| Column | Type | Description |
| :--- | :--- | :--- |
| `session_id` | `INTEGER PRIMARY KEY` | Auto-incrementing unique identifier |
| `user_name` | `TEXT` | Name of the user / student |
| `start_time` | `TEXT` | Session start timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `end_time` | `TEXT` | Session termination timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `duration_sec` | `INTEGER` | Total monitoring time in seconds |
| `avg_score` | `REAL` | Mean posture score (0.0 to 100.0) |
| `slouch_count` | `INTEGER` | Number of slouch posture alerts triggered |
| `risk_level` | `TEXT` | Health risk level (`'Low'`, `'Moderate'`, `'High'`, `'Critical'`) |

### 2. `posture_logs` Table
Stores granular, real-time posture telemetry for each session.

| Column | Type | Description |
| :--- | :--- | :--- |
| `log_id` | `INTEGER PRIMARY KEY` | Auto-incrementing log record ID |
| `session_id` | `INTEGER` | Foreign key referencing `sessions(session_id)` |
| `timestamp` | `TEXT` | Time of telemetry capture (`HH:MM:SS`) |
| `neck_angle` | `REAL` | Measured cervical neck angle deviation |
| `shoulder_slope` | `REAL` | Measured bi-acromial shoulder slant slope |
| `posture_score` | `REAL` | Calculated posture score (0 to 100) |
| `status` | `TEXT` | Posture classification (e.g. `'EXCELLENT POSTURE'`, `'POOR POSTURE ALERT'`) |

---

## 🚀 How to Import / Restore

### Using SQLite CLI:
```bash
sqlite3 ergopulse.db < Database/spinesense_db.sql
```

### Using Python:
```python
import sqlite3

conn = sqlite3.connect("ergopulse.db")
with open("Database/spinesense_db.sql", "r", encoding="utf-8") as f:
    conn.executescript(f.read())
conn.close()
```
