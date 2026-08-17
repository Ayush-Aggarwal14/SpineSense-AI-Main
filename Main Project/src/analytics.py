import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def setup_dark_style():
    plt.style.use('dark_background')
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams['axes.edgecolor'] = '#334155'
    plt.rcParams['axes.linewidth'] = 1.2

def plot_score_timeline(df_logs):
    """Generate line chart of posture score vs time."""
    setup_dark_style()
    fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    if df_logs.empty or 'posture_score' not in df_logs.columns:
        ax.text(0.5, 0.5, "No Posture Logs Available for this Session",
                ha='center', va='center', color='#94a3b8', fontsize=12)
        ax.axis('off')
        return fig

    scores = df_logs['posture_score'].values
    indices = np.arange(len(scores))

    ax.axhspan(80, 100, color='#10b981', alpha=0.12, label='Optimal Zone (80-100%)')
    ax.axhspan(65, 80, color='#f59e0b', alpha=0.12, label='Mild Slouch Zone (65-80%)')
    ax.axhspan(0, 65, color='#ef4444', alpha=0.15, label='Risk Zone (<65%)')

    ax.plot(indices, scores, color='#38bdf8', linewidth=2.5, marker='o', markersize=4, label='Posture Score')

    ax.axhline(80, color='#10b981', linestyle='--', linewidth=1.2, alpha=0.6)
    ax.axhline(65, color='#ef4444', linestyle='--', linewidth=1.2, alpha=0.6)

    ax.set_title("Session Posture Stability Timeline", fontsize=13, fontweight='bold', pad=12, color='#f8fafc')
    ax.set_xlabel("Log Timestamp / Interval", fontsize=10, color='#94a3b8')
    ax.set_ylabel("Ergonomic Score (%)", fontsize=10, color='#94a3b8')
    ax.set_ylim(0, 105)
    ax.grid(True, linestyle=':', alpha=0.3, color='#475569')
    ax.legend(loc='lower left', fontsize=8, facecolor='#1e293b', edgecolor='#334155')

    plt.tight_layout()
    return fig

def plot_posture_breakdown(df_logs):
    """Generate pie chart of Posture Status breakdown."""
    setup_dark_style()
    fig, ax = plt.subplots(figsize=(4.5, 3.5), dpi=100)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    if df_logs.empty or 'status' not in df_logs.columns:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='#94a3b8')
        ax.axis('off')
        return fig

    counts = df_logs['status'].value_counts()
    colors_map = {
        "EXCELLENT POSTURE": "#10b981",
        "GOOD POSTURE": "#10b981",
        "MILD SLOUCH DETECTED": "#f59e0b",
        "MILD SLOUCH": "#f59e0b",
        "POOR POSTURE ALERT": "#ef4444",
        "POOR POSTURE": "#ef4444",
        "TOO CLOSE TO SCREEN": "#3b82f6",
        "TOO FAR FROM SCREEN": "#a855f7"
    }

    colors = [colors_map.get(lbl, "#64748b") for lbl in counts.index]

    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        colors=colors,
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.75,
        textprops=dict(color='#f8fafc', fontsize=8),
        wedgeprops=dict(width=0.4, edgecolor='#0f172a', linewidth=2)
    )

    for at in autotexts:
        at.set_color('#ffffff')
        at.set_fontweight('bold')

    ax.set_title("Posture Grade Distribution", fontsize=12, fontweight='bold', color='#f8fafc')
    plt.tight_layout()
    return fig

def plot_weekly_trend(df_sessions):
    """Generate bar chart of past session average scores."""
    setup_dark_style()
    fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    if df_sessions.empty or 'avg_score' not in df_sessions.columns:
        ax.text(0.5, 0.5, "No Session History Found", ha='center', va='center', color='#94a3b8')
        ax.axis('off')
        return fig

    df_recent = df_sessions.head(7).iloc[::-1]
    session_labels = [f"S-{s_id}" for s_id in df_recent['session_id']]
    scores = df_recent['avg_score'].values

    bars = ax.bar(session_labels, scores, color='#6366f1', edgecolor='#818cf8', width=0.55)

    for bar, score in zip(bars, scores):
        if score >= 85:
            bar.set_facecolor('#10b981')
        elif score >= 75:
            bar.set_facecolor('#f59e0b')
        else:
            bar.set_facecolor('#ef4444')

        ax.text(bar.get_x() + bar.get_width()/2.0, score + 1.5, f"{score:.1f}%",
                ha='center', va='bottom', color='#f8fafc', fontsize=9, fontweight='bold')

    ax.set_title("Recent Sessions Performance Comparison", fontsize=13, fontweight='bold', pad=12, color='#f8fafc')
    ax.set_xlabel("Session ID", fontsize=10, color='#94a3b8')
    ax.set_ylabel("Average Ergonomic Score (%)", fontsize=10, color='#94a3b8')
    ax.set_ylim(0, 115)
    ax.grid(axis='y', linestyle=':', alpha=0.3, color='#475569')

    plt.tight_layout()
    return fig
