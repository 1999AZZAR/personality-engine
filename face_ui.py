import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QTextEdit
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QRectF
from personality_engine import Personality, MoodSystem, EmotionSystem
import datetime
import math
import random
import itertools

class FaceWidget(QWidget):
    def __init__(self, mood_system: MoodSystem, emotion_system: EmotionSystem, personality: Personality, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mood_system = mood_system
        self.emotion_system = emotion_system
        self.personality = personality
        self.setMinimumSize(300, 300)
        self.eye_state = {'pupil_offset_x': 0, 'pupil_offset_y': 0, 'eye_offset_x': 0, 'eye_offset_y': 0}
        self.target_eye_state = self.eye_state.copy()
        self.last_expression = None
        # Animation state
        self.blink_phase = 0.0  # 0=open, 1=closed
        self.blink_timer = 0
        self.blink_interval = random.randint(20, 60)  # frames between blinks
        self.mouth_openness = 0.0  # 0=closed, 1=fully open (for surprise, talking)
        self.target_mouth_openness = 0.0
        self.eyebrow_raise = 0.0  # -1=angry, 0=neutral, 1=surprised
        self.target_eyebrow_raise = 0.0
        self.face_tilt = 0.0  # head tilt angle (radians)
        self.target_face_tilt = 0.0
        self.cheek_intensity = 0.0  # for smooth cheek blending
        self.target_cheek_intensity = 0.0

    def animate(self):
        # Blinking logic: blink rate depends on expression
        expression = self.get_expression()
        if expression in ['surprised', 'anxious', 'worried']:
            blink_speed = 0.35
            blink_recover = 0.22
            blink_min = 10
            blink_max = 30
        elif expression in ['sleepy', 'sad', 'calm']:
            blink_speed = 0.12
            blink_recover = 0.08
            blink_min = 50
            blink_max = 100
        else:
            blink_speed = 0.25
            blink_recover = 0.15
            blink_min = 20
            blink_max = 60
        if self.blink_timer <= 0:
            self.blink_phase = min(1.0, self.blink_phase + blink_speed)
            if self.blink_phase >= 1.0:
                self.blink_timer = random.randint(blink_min, blink_max)
        else:
            self.blink_phase = max(0.0, self.blink_phase - blink_recover)
            self.blink_timer -= 1
        # Animate mouth openness and eyebrow raise, speed depends on expression
        if expression in ['surprised', 'happy', 'excited']:
            interp = 0.28
        elif expression in ['sad', 'sleepy', 'calm']:
            interp = 0.10
        else:
            interp = 0.18
        self.mouth_openness += interp * (self.target_mouth_openness - self.mouth_openness)
        self.eyebrow_raise += interp * (self.target_eyebrow_raise - self.eyebrow_raise)
        self.face_tilt += 0.08 * (self.target_face_tilt - self.face_tilt)
        # Animate cheeks: pulse only for expressive emotions
        pulse = 0.0
        if expression in ['happy', 'delighted', 'proud', 'grateful', 'relieved', 'embarrassed', 'surprised']:
            emo_intensity = self.emotion_system.get_intensity()
            if emo_intensity > 0.7:
                pulse = 0.08 * math.sin(self.cheek_intensity * 8 + random.uniform(0, 2*math.pi))
        else:
            pulse = 0.0
        self.cheek_intensity += 0.15 * (self.target_cheek_intensity + pulse - self.cheek_intensity)
        self.update()

    def set_animation_targets(self, expression):
        # Set target values for mouth, eyebrows, tilt based on expression
        if expression == 'happy':
            self.target_mouth_openness = 0.2
            self.target_eyebrow_raise = 0.3
            self.target_face_tilt = 0.08
        elif expression == 'sad':
            self.target_mouth_openness = 0.1
            self.target_eyebrow_raise = -0.3
            self.target_face_tilt = -0.08
        elif expression == 'angry':
            self.target_mouth_openness = 0.05
            self.target_eyebrow_raise = -0.7
            self.target_face_tilt = -0.12
        elif expression == 'worried':
            self.target_mouth_openness = 0.15
            self.target_eyebrow_raise = -0.2
            self.target_face_tilt = 0.0
        elif expression == 'surprised':
            self.target_mouth_openness = 1.0
            self.target_eyebrow_raise = 1.0
            self.target_face_tilt = 0.0
        elif expression == 'bored':
            self.target_mouth_openness = 0.05
            self.target_eyebrow_raise = 0.0
            self.target_face_tilt = 0.0
        elif expression == 'curious':
            self.target_mouth_openness = 0.15
            self.target_eyebrow_raise = 0.5
            self.target_face_tilt = 0.12
        elif expression == 'sleepy':
            self.target_mouth_openness = 0.02
            self.target_eyebrow_raise = -0.1
            self.target_face_tilt = -0.1
        else:  # calm/neutral
            self.target_mouth_openness = 0.08
            self.target_eyebrow_raise = 0.0
            self.target_face_tilt = 0.0

    def get_expression(self):
        # Hierarchy: emotion > mood > personality
        emotion = self.emotion_system.get_emotion() or ''
        mood = self.mood_system.get_mood() or ''
        traits = self.personality.as_dict(rounded=True)
        # Map emotion/mood to expression
        if emotion:
            e = emotion.lower()
            if 'happy' in e or 'delighted' in e or 'proud' in e or 'grateful' in e or 'relieved' in e:
                return 'happy'
            if 'angry' in e:
                return 'angry'
            if 'afraid' in e or 'anxious' in e or 'ashamed' in e or 'jealous' in e or 'lonely' in e:
                return 'worried'
            if 'surprised' in e:
                return 'surprised'
            if 'sad' in e or 'disgusted' in e:
                return 'sad'
            if 'calm' in e:
                return 'calm'
        if mood:
            m = mood.lower()
            if 'happy' in m or 'content' in m or 'excited' in m:
                return 'happy'
            if 'sad' in m:
                return 'sad'
            if 'anxious' in m or 'confused' in m or 'uncertain' in m:
                return 'worried'
            if 'bored' in m:
                return 'bored'
            if 'curious' in m:
                return 'curious'
            if 'sleepy' in m:
                return 'sleepy'
        # fallback to personality: use happiness/energyLevel
        if traits['happiness'] > 7:
            return 'happy'
        if traits['grumpiness'] > 7:
            return 'angry'
        if traits['sensitivity'] > 7:
            return 'worried'
        if traits['energyLevel'] < 4:
            return 'sleepy'
        return 'calm'

    def interpolate_eye_state(self, current, target, alpha=0.2):
        # Linear interpolation for smoothness
        return {k: int(round(current[k] * (1 - alpha) + target[k] * alpha)) for k in current}

    def get_pupil_offset(self, expression, traits):
        # Returns (pupil_offset_x, pupil_offset_y) for each eye
        # Add some jitter for worried, random for surprised, etc.
        if expression == 'happy':
            return (0, -6)
        elif expression == 'sad':
            return (0, 8)
        elif expression == 'angry':
            return (-6, 0), (6, 0)  # left eye, right eye
        elif expression == 'worried':
            jitter = random.randint(-3, 3)
            return (jitter, 4)
        elif expression == 'surprised':
            return (0, 0)
        elif expression == 'bored':
            return (-8, 0)
        elif expression == 'curious':
            return (8, 0)
        elif expression == 'sleepy':
            return (0, 12)
        else:  # calm/neutral
            return (0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        center_x, center_y = w // 2, h // 2
        face_radius = min(w, h) // 2 - 20
        # Head tilt
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.face_tilt * 180 / math.pi)
// ... rest of file omitted for brevity ...