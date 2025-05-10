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
        painter.translate(-center_x, -center_y)
        # Face
        painter.setBrush(QBrush(QColor(255, 224, 189)))
        painter.drawEllipse(center_x - face_radius, center_y - face_radius, face_radius * 2, face_radius * 2)
        traits = self.personality.as_dict(rounded=True)
        expression = self.get_expression()
        # Eyes
        eye_y = center_y - face_radius // 3
        eye_dx = face_radius // 2
        eye_radius = 32 + traits['curiosity'] // 2
        pupil_radius = 14 + traits['quirkiness'] // 4
        # Cheek effect
        cheek_y = eye_y + eye_radius + 10
        cheek_dx = eye_dx
        cheek_radius_x = int(eye_radius * 0.9)
        cheek_radius_y = int(eye_radius * 0.55)
        # Cheek intensity logic (natural, smooth, based on emotion and intensity)
        emotion = self.emotion_system.get_emotion().lower()
        emo_intensity = self.emotion_system.get_intensity()
        # Target cheek intensity: base + emotion + intensity
        base = 0.15
        if any(e in emotion for e in ['happy', 'delighted', 'proud', 'grateful', 'relieved']):
            target = 0.45 + 0.35 * emo_intensity
        elif any(e in emotion for e in ['ashamed', 'embarrassed']):
            target = 0.65 + 0.25 * emo_intensity
        elif any(e in emotion for e in ['angry', 'afraid', 'anxious', 'sad', 'disgusted', 'lonely']):
            target = 0.12 + 0.10 * emo_intensity
        elif 'calm' in emotion:
            target = 0.10 + 0.08 * emo_intensity
        else:
            target = 0.18 + 0.12 * emo_intensity
        # Add a little random noise
        noise = random.uniform(-0.03, 0.03)
        self.target_cheek_intensity = max(0.0, min(1.0, target + noise))
        # Use self.cheek_intensity for alpha
        cheek_alpha = int(255 * self.cheek_intensity)
        painter.setBrush(QBrush(QColor(255, 128, 160, cheek_alpha)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - cheek_dx - cheek_radius_x//2, cheek_y, cheek_radius_x, cheek_radius_y)
        painter.drawEllipse(center_x + cheek_dx - cheek_radius_x//2, cheek_y, cheek_radius_x, cheek_radius_y)
        painter.setPen(QPen(Qt.black, 2))
        # Pupil movement based on expression
        pupil_offset = self.get_pupil_offset(expression, traits)
        if expression == 'angry':
            pupil_offset_left, pupil_offset_right = pupil_offset
        else:
            pupil_offset_left = pupil_offset_right = pupil_offset
        # Animate pupils: add subtle random jitter
        pupil_jitter_x = random.randint(-2, 2)
        pupil_jitter_y = random.randint(-2, 2)
        # Blinking: eyelid covers eye based on blink_phase
        blink = self.blink_phase
        # Draw big eyes (white)
        for side, dx, pupil_offset in [("left", -eye_dx, pupil_offset_left), ("right", eye_dx, pupil_offset_right)]:
            painter.setBrush(QBrush(Qt.white))
            eye_rect = QRectF(center_x + dx - eye_radius//2, eye_y, eye_radius, eye_radius)
            painter.drawEllipse(eye_rect)
            # Eyelid (draw as a skin-colored rectangle covering the upper part of the eye)
            if blink > 0.01:
                eyelid_height = int(eye_radius * blink)
                eyelid_rect = QRectF(center_x + dx - eye_radius//2, eye_y, eye_radius, eyelid_height)
                painter.save()
                painter.setBrush(QBrush(QColor(255, 224, 189)))
                painter.setPen(Qt.NoPen)
                painter.drawRect(eyelid_rect)
                painter.restore()
            # Pupils
            painter.setBrush(QBrush(Qt.black))
            painter.drawEllipse(center_x + dx - pupil_radius//2 + pupil_offset[0] + pupil_jitter_x,
                               eye_y + eye_radius//3 + pupil_offset[1] + pupil_jitter_y,
                               pupil_radius, pupil_radius)
        # Eyebrows
        brow_length = eye_radius * 1.2
        brow_y = eye_y - 18
        brow_dx = eye_dx
        brow_angle = self.eyebrow_raise * 0.7  # radians
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine, Qt.RoundCap))
        # Left eyebrow
        x1 = center_x - brow_dx - brow_length//2
        x2 = center_x - brow_dx + brow_length//2
        y1 = brow_y - int(18 * self.eyebrow_raise)
        y2 = brow_y + int(10 * self.eyebrow_raise)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        # Right eyebrow
        x1 = center_x + brow_dx - brow_length//2
        x2 = center_x + brow_dx + brow_length//2
        y1 = brow_y + int(10 * self.eyebrow_raise)
        y2 = brow_y - int(18 * self.eyebrow_raise)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        # Mouth
        mouth_y = center_y + face_radius // 2
        mouth_w = face_radius
        pen = QPen(Qt.black, 5)
        painter.setPen(pen)
        # Interpolate mouth shape
        if expression == 'happy':
            smile = 30 + 40 * self.mouth_openness
            painter.drawArc(int(center_x - mouth_w//3), int(mouth_y), int(mouth_w//1.5), int(smile), 0, 180 * 16)
        elif expression == 'sad':
            frown = 30 + 40 * self.mouth_openness
            painter.drawArc(int(center_x - mouth_w//3), int(mouth_y + 10), int(mouth_w//1.5), int(frown), 0, -180 * 16)
        elif expression == 'angry':
            painter.drawLine(center_x - mouth_w//6, mouth_y + 20, center_x + mouth_w//6, mouth_y + 5)
        elif expression == 'worried':
            painter.drawArc(int(center_x - mouth_w//4), int(mouth_y + 10), int(mouth_w//2), 20, 0, -180 * 16)
        elif expression == 'surprised':
            # Draw mouth as ellipse, openness controls size
            painter.save()
            painter.setBrush(QBrush(Qt.white))
            size = 36 + 24 * self.mouth_openness
            painter.drawEllipse(int(center_x - size//2), int(mouth_y + 10), int(size), int(size))
            painter.restore()
        elif expression == 'bored':
            painter.drawLine(center_x - mouth_w//6, mouth_y + 15, center_x + mouth_w//6, mouth_y + 15)
        elif expression == 'curious':
            painter.drawArc(int(center_x - mouth_w//4), int(mouth_y + 5), int(mouth_w//2), 20, 0, 180 * 16)
        elif expression == 'sleepy':
            painter.drawLine(center_x - mouth_w//6, mouth_y + 25, center_x + mouth_w//6, mouth_y + 25)
        else:  # calm/neutral
            painter.drawArc(int(center_x - mouth_w//4), int(mouth_y + 10), int(mouth_w//2), 20, 0, 180 * 16)
        painter.restore()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personality Engine Face")
        self.personality = Personality()
        self.emotion_system = EmotionSystem(get_maturity_fn=self.personality.get_maturity, get_personality_fn=self.personality.as_dict)
        self.mood_system = MoodSystem(self.personality, self.emotion_system)
        self.mood_system.update_mood(self.get_context())

        self.face = FaceWidget(self.mood_system, self.emotion_system, self.personality)
        self.mood_label = QLabel(f"Mood: {self.mood_system.get_mood()}")
        self.intensity_label = QLabel(f"Mood Intensity: {self.mood_system.get_mood_intensity():.2f}")
        self.emotion_label = QLabel(f"Emotion: {self.emotion_system.get_emotion()} ({self.emotion_system.get_intensity():.2f})")
        self.blended_emotions_label = QLabel("")
        self.age_label = QLabel(f"Age: {self.personality.age:.1f}")
        self.maturity_label = QLabel(f"Maturity: {self.personality.get_maturity():.2f}")

        self.update_btn = QPushButton("Update Mood")
        self.update_btn.clicked.connect(self.update_mood)
        self.random_emotion_btn = QPushButton("Trigger Random Emotion")
        self.random_emotion_btn.clicked.connect(self.trigger_random_emotion)
        self.history_box = QTextEdit()
        self.history_box.setReadOnly(True)
        self.history_box.setMaximumHeight(120)

        layout = QVBoxLayout()
        layout.addWidget(self.face)
        layout.addWidget(self.mood_label)
        layout.addWidget(self.intensity_label)
        layout.addWidget(self.emotion_label)
        layout.addWidget(self.blended_emotions_label)
        layout.addWidget(self.age_label)
        layout.addWidget(self.maturity_label)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.random_emotion_btn)
        layout.addWidget(QLabel("History (Mood, Emotion, Personality Drift):"))
        layout.addWidget(self.history_box)
        self.setLayout(layout)

        # Timer for automatic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_update)
        self.timer.start(150)
        self.drift_accumulator = 0.01
        self.drift_interval = 3000
        self.last_traits = self.personality.as_dict().copy()
        self.target_traits = self.personality.as_dict().copy()
        self.ticks = 0
        self.history = []

    def get_context(self):
        now = datetime.datetime.now()
        hour = now.hour
        temperature = 15 + 15 * abs(math.sin(hour / 24 * 2 * math.pi))
        activity = random.choice(['none', 'talking', 'playing'])
        return {'temperature': temperature, 'activity': activity}

    def update_mood(self):
        self.mood_system.update_mood(self.get_context())
        self.mood_label.setText(f"Mood: {self.mood_system.get_mood()}")
        self.intensity_label.setText(f"Mood Intensity: {self.mood_system.get_mood_intensity():.2f}")
        self.emotion_label.setText(f"Emotion: {self.emotion_system.get_emotion()} ({self.emotion_system.get_intensity():.2f})")
        # Show blended emotions
        blended = self.emotion_system.get_blended_emotions()
        if blended:
            blended_str = ', '.join(f"{k}: {v:.2f}" for k, v in blended.items() if v > 0.05)
        else:
            blended_str = ""
        self.blended_emotions_label.setText(f"Blended Emotions: {blended_str}")
        self.age_label.setText(f"Age: {self.personality.age:.1f}")
        self.maturity_label.setText(f"Maturity: {self.personality.get_maturity():.2f}")
        self.face.update()

    def trigger_random_emotion(self):
        pass

    def auto_update(self):
        self.ticks += 1
        self.personality.age_up(0.01)
        self.emotion_system.update()
        self.drift_accumulator += self.timer.interval()
        if self.drift_accumulator >= self.drift_interval:
            self.drift_accumulator = 0.0
            self.last_traits = self.personality.as_dict().copy()
            self.personality.drift_traits(
                mood=self.mood_system.get_mood(),
                mood_intensity=self.mood_system.get_mood_intensity(),
                emotion=self.emotion_system.get_emotion(),
                emotion_intensity=self.emotion_system.get_intensity(),
                blended_emotions=self.emotion_system.get_blended_emotions()
            )
            self.target_traits = self.personality.as_dict().copy()
            # Log drift event
            self.history.append(f"[Tick {self.ticks}] Drift: {self.mood_system.get_mood()} | {self.emotion_system.get_emotion()} | Traits: {[f'{t}:{self.personality.get_trait(t):.2f}' for t in self.personality.TRAITS]}")
            if len(self.history) > 10:
                self.history = self.history[-10:]
        t = min(1.0, self.drift_accumulator / self.drift_interval)
        for trait in self.personality.TRAITS:
            interpolated = self.last_traits[trait] * (1-t) + self.target_traits[trait] * t
            self.personality.traits[trait] = interpolated
        # Log mood/emotion
        if self.ticks % 30 == 0:
            self.history.append(f"[Tick {self.ticks}] Mood: {self.mood_system.get_mood()} | Emotion: {self.emotion_system.get_emotion()} ({self.emotion_system.get_intensity():.2f})")
            if len(self.history) > 10:
                self.history = self.history[-10:]
        self.history_box.setPlainText('\n'.join(self.history))
        self.update_mood()
        # Animate face
        self.face.set_animation_targets(self.face.get_expression())
        self.face.animate()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 