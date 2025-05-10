# Personality Engine

A lifelike, fuzzy, context-aware **personality, mood, and emotion engine** for AI agents, with a real-time animated face demo.

## Core: `personality_engine.py`
- Models personality as 8 traits (with sub-facets), each drifting and stabilizing over time.
- Mood and emotion systems are context-aware, fuzzy, and lifelike:
  - **Personality**: 8 traits, each with core/plastic facets, nonlinear drift, and maturity/aging.
  - **Mood**: 12 moods, context- and trait-driven, with smooth transitions and inertia.
  - **Emotion**: Multiple blended emotions, short-lived, with habituation, history, and fuzzy trait mapping.
  - **Maturity**: As the agent ages, it becomes more stable and less volatile.
  - **Fuzzy logic**: All influences are weighted, blended, and context-sensitive for realism.
- Designed for use in AI, NPCs, robots, or any system needing a believable, evolving personality.

## Demo UI: `face_ui.py`
- **Animated face** (PyQt5):
  - Eyes, mouth, eyebrows, cheeks, and head tilt all animate based on the current mood/emotion.
  - Cheek blush, blinking, and facial expressions are smooth and lifelike.
  - UI displays current mood, emotion, age, maturity, and a history log.
- **No direct control**: The UI is a pure observer of the engine's state, not a manipulator.

## Installation

1. **Install Python 3.7+** (recommended: 3.8+)
2. **Install dependencies:**
   ```bash
   pip install PyQt5
   ```

## Running the Demo

```bash
python face_ui.py
```

- The face will animate in real time, showing the current mood and emotion as computed by the engine.
- The system evolves on its own, with no user input required.

## Architecture

- `personality_engine.py`: All core logic for personality, mood, and emotion. Can be imported and used in any Python project.
- `face_ui.py`: PyQt5 UI that visualizes the engine's state. No direct manipulation of the engine—just a demo/observer.

## Features
- **Lifelike, fuzzy, and context-aware**: All state changes are smooth, weighted, and influenced by context, history, and maturity.
- **Aging and maturity**: Personality stabilizes as the agent ages.
- **Habituation**: Repeated emotions lose intensity, with recovery over time.
- **Animated face**: All facial features respond to the engine's state for a believable demo.

## Customization
- You can import and use `Personality`, `MoodSystem`, and `EmotionSystem` in your own projects.
- The UI can be extended or themed as desired.

## License
MIT (or specify your license here) 