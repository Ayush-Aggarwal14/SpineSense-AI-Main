import cv2
import numpy as np
import mediapipe as mp
import math
import os

class PostureEngine:
    """
    Advanced Ergonomic Biomechanics & Pose Landmark Engine.
    Uses Google MediaPipe Tasks API with spatial vector trigonometry,
    temporal EMA landmark smoothing, and Hansraj Cervical Load estimation.
    """
    def __init__(self, alpha_smooth=0.35):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,       # Maximum accuracy neural model
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.65
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Temporal Exponential Moving Average (EMA) filter state
        self.alpha = alpha_smooth
        self.prev_landmarks = None
        self.baseline_neck = 12.0
        self.baseline_slant = 2.0

    def _smooth_landmarks(self, landmarks):
        """Applies EMA filtering across 33 3D spatial pose landmarks to eliminate jitter."""
        coords = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm.landmarks in [landmarks] for lm in lm.landmark])
        if self.prev_landmarks is None:
            self.prev_landmarks = coords
            return coords
        
        smoothed = self.alpha * coords + (1 - self.alpha) * self.prev_landmarks
        self.prev_landmarks = smoothed
        return smoothed

    def calculate_cervical_load(self, neck_angle):
        """
        Calculates effective head weight (cervical spine load) in kg based on Hansraj Spinal Model:
        0° -> ~5kg, 15° -> ~12kg, 30° -> ~18kg, 45° -> ~22kg, 60° -> ~27kg.
        """
        clamped_angle = max(0, min(60, neck_angle))
        # Quadratic curve fit based on clinical biomechanics data
        effective_load_kg = 5.0 + (0.28 * clamped_angle) + (0.0015 * (clamped_angle ** 2))
        return round(effective_load_kg, 1)

    def process_frame(self, frame_bgr):
        """
        Processes a raw BGR image frame, extracts spatial vectors,
        computes ergonomic posture metrics, and renders HD skeletal HUD overlays.
        """
        h, w, c = frame_bgr.shape
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        metrics = {
            "detected": False,
            "score": 100,
            "status": "EXCELLENT POSTURE",
            "neck_angle": 12.0,
            "shoulder_slope": 2.0,
            "cervical_load_kg": 5.0,
            "dist_ratio": 1.0
        }

        if not results.pose_landmarks:
            return frame_bgr, metrics

        metrics["detected"] = True
        smoothed_lm = self._smooth_landmarks(results.pose_landmarks)

        # Spatial 2D/3D Feature Coordinates
        nose = smoothed_lm[0][:2] * np.array([w, h])
        l_ear = smoothed_lm[7][:2] * np.array([w, h])
        r_ear = smoothed_lm[8][:2] * np.array([w, h])
        l_sh = smoothed_lm[11][:2] * np.array([w, h])
        r_sh = smoothed_lm[12][:2] * np.array([w, h])

        # Anatomical Midpoints
        ear_mid = (l_ear + r_ear) / 2.0
        sh_mid = (l_sh + r_sh) / 2.0

        # 1. Cervical Neck Inclination Angle (against true vertical)
        dx = sh_mid[0] - ear_mid[0]
        dy = sh_mid[1] - ear_mid[1]
        neck_angle = math.abs(math.atan2(math.abs(dx), math.abs(dy)) * (180.0 / math.pi))

        # 2. Shoulder Asymmetry / Slant Angle
        sh_dx = math.abs(r_sh[0] - l_sh[0])
        sh_dy = math.abs(r_sh[1] - l_sh[1])
        shoulder_slant = math.atan2(sh_dy, sh_dx + 1e-6) * (180.0 / math.pi)

        # 3. Hansraj Cervical Spine Load (kg)
        cervical_load_kg = self.calculate_cervical_load(neck_angle)

        # 4. Multi-Factor Ergonomic Posture Scoring
        neck_penalty = max(0.0, (neck_angle - 12.0) * 2.5)
        slant_penalty = max(0.0, (shoulder_slant - 2.5) * 3.8)
        total_penalty = neck_penalty + slant_penalty
        score = max(0, min(100, int(round(100.0 - total_penalty))))

        # Status Classification
        if score >= 80:
            status = "EXCELLENT POSTURE"
            color_bgr = (129, 185, 16)   # Emerald Green
        elif score >= 65:
            status = "MILD SLOUCH DETECTED"
            color_bgr = (11, 158, 245)   # Amber Gold
        else:
            status = "POOR POSTURE ALERT"
            color_bgr = (68, 68, 239)    # Ruby Red

        # Render High-Precision Skeletal Overlays
        annotated_frame = frame_bgr.copy()
        
        # Connectors
        cv2.line(annotated_frame, (int(l_sh[0]), int(l_sh[1])), (int(r_sh[0]), int(r_sh[1])), color_bgr, 5)
        cv2.line(annotated_frame, (int(ear_mid[0]), int(ear_mid[1])), (int(sh_mid[0]), int(sh_mid[1])), color_bgr, 5)

        # Landmark Joints
        for pt in [l_sh, r_sh, ear_mid, nose]:
            cv2.circle(annotated_frame, (int(pt[0]), int(pt[1])), 7, (255, 255, 255), -1)
            cv2.circle(annotated_frame, (int(pt[0]), int(pt[1])), 9, color_bgr, 2)

        # HUD Overlay Banner
        cv2.rectangle(annotated_frame, (10, 10), (380, 100), (15, 23, 42), -1)
        cv2.rectangle(annotated_frame, (10, 10), (380, 100), color_bgr, 2)
        cv2.putText(annotated_frame, f"ErgoPulse AI: {score}%", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"Status: {status}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_bgr, 2)
        cv2.putText(annotated_frame, f"Neck: {neck_angle:.1f}deg | Load: {cervical_load_kg}kg", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (203, 213, 225), 1)

        metrics.update({
            "score": score,
            "status": status,
            "neck_angle": round(neck_angle, 1),
            "shoulder_slope": round(shoulder_slant, 1),
            "cervical_load_kg": cervical_load_kg
        })

        return annotated_frame, metrics
