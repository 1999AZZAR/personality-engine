from typing import Dict, Any, Optional
import random
import math

class Personality:
    """
    Represents a personality with 8 traits, each in [1, 10] (float for smooth drift).
    Each trait is composed of sub-traits (facets), each with its own stability/plasticity.
    Some facets are 'core' (anchored, very stable), others are 'plastic' (drift easily).
    Drift can be nonlinear and asymmetric (e.g., easier to lose happiness than regain).
    Personality changes only very slightly over time, but can be influenced by strong mood/emotion.
    Includes aging and maturity: as age increases, maturity increases, stabilizing personality.
    Implements fuzzy trait-emotion mapping for more nuanced, lifelike drift.
    """
    TRAITS = [
        'socialness', 'playfulness', 'curiosity', 'happiness',
        'grumpiness', 'energyLevel', 'sensitivity', 'quirkiness'
    ]
    TRAIT_RANGE = (1.0, 10.0)
    MATURITY_AGE = 100.0  # Age at which full maturity is reached (arbitrary units)
    # Facets for each trait: {main_trait: {facet: {'weight': float, 'stability': float, 'core': bool}}}
    FACETS = {
        'socialness': {
            'friendliness':   {'weight': 0.4, 'stability': 0.9, 'core': True},
            'assertiveness':  {'weight': 0.3, 'stability': 0.7, 'core': False},
            'gregariousness': {'weight': 0.3, 'stability': 0.6, 'core': False},
        },
        'playfulness': {
            'humor':          {'weight': 0.5, 'stability': 0.8, 'core': False},
            'spontaneity':    {'weight': 0.5, 'stability': 0.6, 'core': False},
        },
        'curiosity': {
            'openness':       {'weight': 0.6, 'stability': 0.8, 'core': True},
            'imagination':    {'weight': 0.4, 'stability': 0.7, 'core': False},
        },
        'happiness': {
            'optimism':       {'weight': 0.5, 'stability': 0.85, 'core': True},
            'cheerfulness':   {'weight': 0.5, 'stability': 0.6, 'core': False},
        },
        'grumpiness': {
            'irritability':   {'weight': 0.7, 'stability': 0.7, 'core': False},
            'pessimism':      {'weight': 0.3, 'stability': 0.85, 'core': True},
        },
        'energyLevel': {
            'vitality':       {'weight': 0.6, 'stability': 0.8, 'core': True},
            'restlessness':   {'weight': 0.4, 'stability': 0.6, 'core': False},
        },
        'sensitivity': {
            'anxiety':        {'weight': 0.6, 'stability': 0.5, 'core': False},
            'empathy':        {'weight': 0.4, 'stability': 0.8, 'core': True},
        },
        'quirkiness': {
            'eccentricity':   {'weight': 0.7, 'stability': 0.7, 'core': False},
            'creativity':     {'weight': 0.3, 'stability': 0.8, 'core': False},
        },
    }
    # Fuzzy similarity between traits and emotions (0.0-1.0)
    TRAIT_EMOTION_SIMILARITY = {
        'happiness':    {'Delighted': 0.9, 'Proud': 0.5, 'Grateful': 0.5, 'Relieved': 0.4, 'Calm': 0.3, 'Sad': 0.0, 'Angry': 0.0},
        'grumpiness':   {'Angry': 0.8, 'Ashamed': 0.4, 'Disgusted': 0.5, 'Sad': 0.5, 'Calm': 0.1, 'Delighted': 0.0},
        'sensitivity':  {'Afraid': 0.7, 'Anxious': 0.7, 'Ashamed': 0.5, 'Lonely': 0.5, 'Surprised': 0.3, 'Calm': 0.1},
        'energyLevel':  {'Excited': 0.8, 'Delighted': 0.6, 'Surprised': 0.5, 'Sleepy': 0.0, 'Calm': 0.2},
        'playfulness':  {'Delighted': 0.7, 'Excited': 0.7, 'Curious': 0.5, 'Bored': 0.0, 'Calm': 0.2},
        'curiosity':    {'Curious': 0.9, 'Surprised': 0.5, 'Confused': 0.5, 'Bored': 0.0, 'Calm': 0.2},
        'quirkiness':   {'Confused': 0.7, 'Surprised': 0.5, 'Delighted': 0.3, 'Calm': 0.2},
        'socialness':   {'Proud': 0.6, 'Grateful': 0.5, 'Lonely': 0.5, 'Delighted': 0.3, 'Calm': 0.2},
    }

    def __init__(self, traits: Optional[Dict[str, float]] = None, fuzziness: float = 0.95, age: float = 0.0):
        self.fuzziness = fuzziness
        self.age = age  # Age in arbitrary units (e.g., days, ticks)
        # Each facet gets its own value
        self.facets = {}
        for trait, facets in self.FACETS.items():
            for facet, meta in facets.items():
                if traits and facet in traits:
                    base = float(traits[facet])
                else:
                    base = random.gauss(5.5, 2.0)
                noise = random.uniform(-self.fuzziness, self.fuzziness)
                value = base + noise
                value = max(self.TRAIT_RANGE[0], min(self.TRAIT_RANGE[1], value))
                self.facets[facet] = value
        # For backward compatibility, also keep main trait values (computed from facets)
        self.traits = {trait: self.get_trait(trait) for trait in self.TRAITS}

    def set_trait(self, trait: str, value: float):
        # Set all facets proportionally to match the new trait value
        if trait in self.FACETS:
            total_weight = sum(meta['weight'] for meta in self.FACETS[trait].values())
            for facet, meta in self.FACETS[trait].items():
                self.facets[facet] = value * meta['weight'] / total_weight
        self.traits[trait] = value

    def get_trait(self, trait: str) -> float:
        # Compute trait as weighted sum of facets
        if trait in self.FACETS:
            return sum(self.facets[facet] * meta['weight'] for facet, meta in self.FACETS[trait].items())
        return self.traits.get(trait, 5.0)

    def as_dict(self, rounded: bool = False) -> Dict[str, float]:
        d = {trait: self.get_trait(trait) for trait in self.TRAITS}
        d['age'] = self.age
        d['maturity'] = self.get_maturity()
        # Add facets for inspection
        for facet in self.facets:
            d[facet] = self.facets[facet]
        if rounded:
            d = {k: int(round(v)) if isinstance(v, float) else v for k, v in d.items()}
        return d

    def drift_traits(self, drift_strength: float = 0.01, mood: Optional[str] = None, mood_intensity: float = 0.0, emotion: Optional[str] = None, emotion_intensity: float = 0.0, blended_emotions: Optional[Dict[str, float]] = None):
        """
        Drift facets (sub-traits) with fuzzy, nonlinear, and asymmetric rules.
        Core facets are very stable, plastic facets drift more.
        Some drifts are asymmetric (easier to lose happiness than gain, easier to become anxious than calm, etc).
        Now, all emotion-related facets have nonlinear/asymmetric drift rules.
        Maturity bias: as maturity increases, drift becomes much slower, especially for core facets (nonlinear effect).
        """
        maturity = self.get_maturity()
        maturity_bias = maturity ** 1.5
        for trait, facets in self.FACETS.items():
            for facet, meta in facets.items():
                stability = meta['stability']
                is_core = meta['core']
                plasticity = 1.0 - stability
                # Stronger maturity bias (nonlinear)
                drift_factor = (1.0 - 0.7 * maturity_bias) * (plasticity + 0.2)
                drift = random.gauss(0, drift_strength) * drift_factor
                if blended_emotions:
                    for emo, inten in blended_emotions.items():
                        sim = self.TRAIT_EMOTION_SIMILARITY.get(trait, {}).get(emo, 0.0)
                        drift += 0.03 * inten * sim * drift_factor
                elif emotion and emotion_intensity > 0.7:
                    sim = self.TRAIT_EMOTION_SIMILARITY.get(trait, {}).get(emotion, 0.0)
                    drift += 0.03 * emotion_intensity * sim * drift_factor
                if mood and mood_intensity > 0.7:
                    sim = self.TRAIT_EMOTION_SIMILARITY.get(trait, {}).get(mood, 0.0)
                    drift += 0.02 * mood_intensity * sim * drift_factor
                # Nonlinear/asymmetric drift for all emotion-related facets
                # Anxiety: easier to increase than decrease
                if facet == 'anxiety':
                    if drift > 0:
                        drift *= 1.5
                    else:
                        drift *= 0.7
                # Cheerfulness: easier to lose than regain
                if facet == 'cheerfulness':
                    if drift < 0:
                        drift *= 1.5
                    else:
                        drift *= 0.7
                # Optimism: hard to regain if lost
                if facet == 'optimism':
                    if drift > 0:
                        drift *= 0.5
                # Irritability: easier to increase than decrease
                if facet == 'irritability':
                    if drift > 0:
                        drift *= 1.3
                    else:
                        drift *= 0.8
                # Pessimism: easier to increase than decrease
                if facet == 'pessimism':
                    if drift > 0:
                        drift *= 1.2
                    else:
                        drift *= 0.8
                # Assertiveness: easier to lose than regain
                if facet == 'assertiveness':
                    if drift < 0:
                        drift *= 1.3
                    else:
                        drift *= 0.7
                # Gregariousness: easier to lose than regain
                if facet == 'gregariousness':
                    if drift < 0:
                        drift *= 1.2
                    else:
                        drift *= 0.8
                # Empathy: hard to regain if lost
                if facet == 'empathy':
                    if drift > 0:
                        drift *= 0.6
                # Restlessness: easier to increase than decrease
                if facet == 'restlessness':
                    if drift > 0:
                        drift *= 1.2
                    else:
                        drift *= 0.8
                # Vitality: easier to lose than regain
                if facet == 'vitality':
                    if drift < 0:
                        drift *= 1.2
                    else:
                        drift *= 0.8
                # Eccentricity: easier to increase than decrease
                if facet == 'eccentricity':
                    if drift > 0:
                        drift *= 1.2
                    else:
                        drift *= 0.8
                # Creativity: easier to lose than regain
                if facet == 'creativity':
                    if drift < 0:
                        drift *= 1.2
                    else:
                        drift *= 0.8
                # Openness: hard to regain if lost
                if facet == 'openness':
                    if drift > 0:
                        drift *= 0.7
                # Imagination: easier to increase than decrease
                if facet == 'imagination':
                    if drift > 0:
                        drift *= 1.1
                    else:
                        drift *= 0.9
                # Humor: easier to lose than regain
                if facet == 'humor':
                    if drift < 0:
                        drift *= 1.2
                    else:
                        drift *= 0.8
                # Spontaneity: easier to increase than decrease
                if facet == 'spontaneity':
                    if drift > 0:
                        drift *= 1.1
                    else:
                        drift *= 0.9
                # Core facets: clamp drift even more
                if is_core:
                    drift *= 0.3 * (1.0 - 0.7 * maturity_bias)  # even more clamp for core facets
                new_value = self.facets[facet] + drift
                self.facets[facet] = max(self.TRAIT_RANGE[0], min(self.TRAIT_RANGE[1], new_value))
        # Update main trait values from facets
        self.traits = {trait: self.get_trait(trait) for trait in self.TRAITS}

    def age_up(self, amount: float = 1.0):
        """Increase age by a given amount (default 1.0)."""
        self.age += amount

    def get_maturity(self) -> float:
        """Returns a maturity factor in [0, 1], where 1 is fully mature."""
        # Sigmoid for smooth transition to maturity
        return 1.0 / (1.0 + math.exp(-0.08 * (self.age - self.MATURITY_AGE)))

class EmotionSystem:
    """
    Handles multiple short-lived, high-intensity emotions that can override or blend with mood.
    Emotions decay over time and can be triggered or reinforced by events or context.
    Maturity reduces emotion intensity and volatility.
    Personality influences how easily emotions are triggered (sensitivity trait and relevant facets).
    Maintains a history to bias future emotions for lifelike consistency.
    Supports emotion blending: multiple emotions can be active at once.
    Implements habituation: repeated triggers of the same emotion reduce its intensity, with recovery over time.
    Now, emotion triggering and intensity are highly influenced by relevant personality facets.
    """
    EMOTIONS = [
        'Surprised', 'Angry', 'Afraid', 'Delighted', 'Disgusted', 'Proud', 'Ashamed', 'Relieved', 'Hopeful', 'Jealous', 'Grateful', 'Lonely', 'Calm'
    ]
    DEFAULT_DECAY = 0.85
    HISTORY_LENGTH = 10
    HABITUATION_DECAY = 0.92  # How quickly habituation fades (closer to 1 = slower recovery)
    HABITUATION_MAX = 1.0     # Max habituation (fully habituated)
    HABITUATION_MIN = 0.05    # Never fully zero, always some sensitivity
    HABITUATION_STEP = 0.25   # How much each trigger increases habituation

    # Mapping from emotion to relevant personality facet(s) and their influence direction
    EMOTION_PERSONALITY_MAP = {
        'Surprised':   [('imagination', 0.5), ('openness', 0.3)],
        'Angry':       [('irritability', 0.7), ('assertiveness', 0.3)],
        'Afraid':      [('anxiety', 0.8), ('pessimism', 0.3)],
        'Delighted':   [('cheerfulness', 0.7), ('optimism', 0.5)],
        'Disgusted':   [('irritability', 0.5), ('pessimism', 0.4)],
        'Proud':       [('assertiveness', 0.5), ('friendliness', 0.3)],
        'Ashamed':     [('anxiety', 0.5), ('empathy', 0.3)],
        'Relieved':    [('optimism', 0.5), ('cheerfulness', 0.3)],
        'Hopeful':     [('optimism', 0.8)],
        'Jealous':     [('anxiety', 0.4), ('restlessness', 0.3)],
        'Grateful':    [('empathy', 0.7), ('friendliness', 0.3)],
        'Lonely':      [('gregariousness', -0.7), ('friendliness', -0.3)],
        'Calm':        [('cheerfulness', 0.3), ('optimism', 0.3), ('anxiety', -0.7)],
    }

    def __init__(self, get_maturity_fn: Optional[callable] = None, get_personality_fn: Optional[callable] = None):
        # Now using a dict of active emotions: {emotion: intensity}
        self.active_emotions = {}
        self.decay = self.DEFAULT_DECAY
        self.get_maturity = get_maturity_fn if get_maturity_fn else (lambda: 0.0)
        self.get_personality = get_personality_fn if get_personality_fn else (lambda: {'sensitivity': 5.0})
        self.history = ['Calm'] * self.HISTORY_LENGTH
        # Habituation: {emotion: habituation_level}
        self.habituation = {emo: 0.0 for emo in self.EMOTIONS}

    def _personality_emotion_bias(self, emotion: str) -> float:
        """Return a bias factor for this emotion based on relevant personality facets."""
        personality = self.get_personality()
        bias = 0.0
        if hasattr(self.get_personality, '__call__'):
            # If as_dict, get facets
            personality = self.get_personality()
        for facet, weight in self.EMOTION_PERSONALITY_MAP.get(emotion, []):
            val = personality.get(facet, 5.0)
            # Normalize to [-1, 1] around 5.0
            norm = (val - 5.0) / 5.0
            bias += norm * weight
        return bias

    def trigger(self, emotion: str, intensity: float = 1.0, decay: Optional[float] = None):
        if emotion in self.EMOTIONS:
            maturity = self.get_maturity()
            maturity_bias = maturity ** 1.5
            sensitivity = self.get_personality().get('sensitivity', 5.0)
            sens_factor = 1.0 + 0.15 * (sensitivity - 5.0)
            hab_level = self.habituation.get(emotion, 0.0)
            hab_factor = max(self.HABITUATION_MIN, 1.0 - hab_level)
            if hab_level > 0.7 and random.random() < hab_level:
                return
            pers_bias = 1.0 + self._personality_emotion_bias(emotion)
            pers_bias = max(0.1, pers_bias)
            # Stronger maturity bias for intensity
            adj_intensity = intensity * (1.0 - 0.8 * maturity_bias) * sens_factor * hab_factor * pers_bias
            if emotion in self.active_emotions:
                self.active_emotions[emotion] = 0.92 * self.active_emotions[emotion] + 0.08 * min(1.0, adj_intensity)
            else:
                self.active_emotions[emotion] = min(0.15, adj_intensity)
            # Stronger maturity bias for decay
            self.decay = (decay if decay is not None else self.DEFAULT_DECAY) - 0.4 * maturity_bias
            self.decay = max(0.4, min(1.0, self.decay))
            prev_hab = self.habituation.get(emotion, 0.0)
            step = self.HABITUATION_STEP * (1.0 + prev_hab)
            self.habituation[emotion] = min(self.HABITUATION_MAX, prev_hab + step)
            for other in self.EMOTIONS:
                if other != emotion:
                    self.habituation[other] = max(self.HABITUATION_MIN, self.habituation.get(other, 0.0) * 0.98)

    def trigger_event(self, event: str):
        # Simple event-to-emotion mapping
        event_map = {
            'compliment': ('Proud', 0.6),
            'insult': ('Angry', 0.7),
            'threat': ('Afraid', 0.8),
            'success': ('Delighted', 0.7),
            'failure': ('Ashamed', 0.6),
            'loss': ('Sad', 0.7),
            'rejection': ('Lonely', 0.7),
            'support': ('Grateful', 0.6),
            'surprise': ('Surprised', 0.8),
        }
        if event in event_map:
            emo, inten = event_map[event]
            self.trigger(emo, inten)

    def _weighted_random_emotion(self):
        recent = self.history[-self.HISTORY_LENGTH:]
        counts = {e: recent.count(e) for e in self.EMOTIONS}
        weights = [1 + counts[e] for e in self.EMOTIONS]
        calm_idx = self.EMOTIONS.index('Calm')
        weights[calm_idx] = max(1, weights[calm_idx] // 2)
        return random.choices(self.EMOTIONS, weights=weights, k=1)[0]

    def update(self):
        interp_alpha = 0.08  # Lower alpha for more inertia (moderate stability)
        maturity = self.get_maturity()
        maturity_bias = maturity ** 1.5
        adj_decay = self.decay - 0.4 * maturity_bias
        adj_decay = max(0.4, min(1.0, adj_decay))
        to_remove = []
        for emo in list(self.active_emotions.keys()):
            noise = random.gauss(0, 0.01)
            self.active_emotions[emo] = (1 - interp_alpha) * self.active_emotions[emo] * adj_decay + interp_alpha * 0.0
            self.active_emotions[emo] = max(0.0, min(1.0, self.active_emotions[emo] + noise))
            if self.active_emotions[emo] < 0.05:
                to_remove.append(emo)
        for emo in to_remove:
            del self.active_emotions[emo]
        # If the same emotion is dominant for many cycles, increase its decay and reduce its intensity/habituation
        dominant = self.get_emotion()
        if dominant:
            count = self.history.count(dominant)
            if count > self.HISTORY_LENGTH // 2:
                if dominant in self.active_emotions:
                    self.active_emotions[dominant] *= 0.85  # faster decay
                self.habituation[dominant] = max(self.HABITUATION_MIN, self.habituation[dominant] * 0.95)
        # Always compute a dominant emotion based on personality, mood, and context if none active
        if not self.active_emotions:
            personality = self.get_personality()
            emotion_scores = {}
            for emo in self.EMOTIONS:
                bias = self._personality_emotion_bias(emo)
                emotion_scores[emo] = bias + random.gauss(0, 0.05)
            best_emo = max(emotion_scores, key=emotion_scores.get)
            self.active_emotions[best_emo] = max(0.1, min(1.0, 0.2 + 0.8 * (emotion_scores[best_emo] + 1) / 2))
        # Spontaneous emotion, biased by history, but less likely if current emotion is strong
        max_intensity = max(self.active_emotions.values()) if self.active_emotions else 0.0
        spontaneous_chance = 0.005 if max_intensity > 0.5 else 0.02
        if 'Calm' in self.active_emotions and random.random() < spontaneous_chance:
            spontaneous = self._weighted_random_emotion()
            if spontaneous not in self.active_emotions:
                self.active_emotions[spontaneous] = random.uniform(0.08, 0.18)
        # If no emotion is strong, blend toward Calm
        if max(self.active_emotions.values(), default=0.0) < 0.18 and 'Calm' not in self.active_emotions:
            self.active_emotions['Calm'] = 0.12
        # Update history with dominant emotion
        dominant = self.get_emotion()
        if dominant:
            self.history.append(dominant)
            if len(self.history) > self.HISTORY_LENGTH:
                self.history = self.history[-self.HISTORY_LENGTH:]
        # Stronger maturity bias for habituation decay
        for emo in self.habituation:
            prev = self.habituation[emo]
            hab_decay = self.HABITUATION_DECAY - 0.2 * maturity_bias - 0.05 * prev
            hab_decay = max(0.7, min(1.0, hab_decay))
            self.habituation[emo] = max(self.HABITUATION_MIN, prev * hab_decay)

    def get_emotion(self) -> str:
        # Return the dominant (highest intensity) emotion
        if not self.active_emotions:
            return 'Calm'
        return max(self.active_emotions, key=lambda e: self.active_emotions[e])

    def get_intensity(self) -> float:
        if not self.active_emotions:
            return 0.1
        return max(self.active_emotions.values())

    def get_blended_emotions(self) -> Dict[str, float]:
        return dict(self.active_emotions)

    def as_dict(self) -> Dict[str, Any]:
        return {
            'current_emotion': self.get_emotion(),
            'emotion_intensity': self.get_intensity(),
            'possible_emotions': self.EMOTIONS,
            'emotion_history': self.history[-self.HISTORY_LENGTH:],
            'blended_emotions': self.get_blended_emotions()
        }

class MoodSystem:
    """
    Determines mood based on personality traits, context, and time, with smooth transitions.
    Mood can change quickly and is sensitive to context and time of day.
    If a strong emotion is present, it can override or blend with mood.
    Maturity stabilizes mood (less volatility, less noise).
    Mood is longer-lived than emotion, but strong emotion can influence mood.
    If mood and emotion are in conflict, mood becomes 'Uncertain'.
    MOOD changes at a MEDIUM pace, but now with smooth inertia.
    Maintains a history to bias future moods for lifelike consistency.
    """
    MOODS = [
        'Happy', 'Neutral', 'Bored', 'Sleepy', 'Sad', 'Curious',
        'Hot', 'Cold', 'Excited', 'Anxious', 'Content', 'Confused', 'Uncertain'
    ]
    MOOD_WEIGHTS = {
        'Happy':      {'happiness': 0.8, 'energyLevel': 0.3, 'socialness': 0.2, 'grumpiness': -0.3},
        'Sad':        {'grumpiness': 0.7, 'sensitivity': 0.4, 'happiness': -0.4, 'energyLevel': -0.2},
        'Curious':    {'curiosity': 0.8, 'energyLevel': 0.2, 'playfulness': 0.2, 'sensitivity': -0.2},
        'Sleepy':     {'energyLevel': -1.0, 'happiness': -0.2, 'playfulness': -0.2},
        'Excited':    {'playfulness': 0.7, 'energyLevel': 0.5, 'happiness': 0.3, 'grumpiness': -0.2},
        'Anxious':    {'sensitivity': 0.8, 'grumpiness': 0.3, 'energyLevel': -0.2, 'happiness': -0.2},
        'Confused':   {'quirkiness': 0.8, 'curiosity': 0.4, 'happiness': -0.2},
        'Content':    {'happiness': 0.6, 'energyLevel': 0.3, 'socialness': 0.3, 'grumpiness': -0.2},
        'Bored':      {'curiosity': -0.8, 'energyLevel': -0.3, 'playfulness': -0.3, 'happiness': -0.2},
        'Hot':        {'energyLevel': -0.2, 'grumpiness': 0.2},
        'Cold':       {'energyLevel': -0.2, 'sensitivity': 0.2},
        'Neutral':    {},
        'Uncertain':  {'sensitivity': 0.2, 'quirkiness': 0.2, 'happiness': -0.2},
    }
    HISTORY_LENGTH = 10

    def __init__(self, personality: Personality, emotion_system: Optional[EmotionSystem] = None, mood_noise: float = 1.0):
        self.personality = personality
        self.current_mood = 'Neutral'
        self.mood_intensity = 0.0  # For smooth transitions
        self.mood_noise = mood_noise
        self.context = {}
        self.last_mood = 'Neutral'
        self.last_intensity = 0.0
        self.emotion_system = emotion_system
        self.mood_life = 0.0  # How long the current mood has lasted
        self.history = ['Neutral'] * self.HISTORY_LENGTH

    def set_context(self, context: Dict[str, Any]):
        self.context = context

    def compute_mood_scores(self, traits: Dict[str, float], context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        scores = {}
        maturity = self.personality.get_maturity()
        maturity_bias = maturity ** 1.5
        for mood, weights in self.MOOD_WEIGHTS.items():
            score = 0.0
            for trait, weight in weights.items():
                score += traits.get(trait, 5.0) * weight
            if context:
                if mood == 'Hot' and context.get('temperature', 22) > 28:
                    score += (context['temperature'] - 28) * 0.5
                if mood == 'Cold' and context.get('temperature', 22) < 16:
                    score += (16 - context['temperature']) * 0.5
                if mood == 'Bored' and context.get('activity', 'none') == 'none':
                    score += 2.0
            # Stronger maturity bias for noise
            noise = random.uniform(-self.mood_noise, self.mood_noise) * (1.0 - 0.8 * maturity_bias)
            score += noise
            scores[mood] = score
        scores['Neutral'] = 0.0
        return scores

    def _weighted_random_mood(self):
        recent = self.history[-self.HISTORY_LENGTH:]
        counts = {m: recent.count(m) for m in self.MOODS}
        weights = [1 + counts[m] for m in self.MOODS]
        neutral_idx = self.MOODS.index('Neutral')
        weights[neutral_idx] = max(1, weights[neutral_idx] // 2)
        return random.choices(self.MOODS, weights=weights, k=1)[0]

    def update_mood(self, context: Optional[Dict[str, Any]] = None):
        if context is not None:
            self.set_context(context)
        traits = self.personality.as_dict()
        scores = self.compute_mood_scores(traits, self.context)
        # Blend in all active emotions
        emo_blend = {}
        emo_intensity = 0.0
        if self.emotion_system:
            emo_blend = self.emotion_system.get_blended_emotions()
            emo_intensity = self.emotion_system.get_intensity()
            for emo, inten in emo_blend.items():
                if emo in scores:
                    scores[emo] = scores.get(emo, 0) + inten * 2  # emotions boost their matching mood
        best_mood = max(scores, key=scores.get)
        best_score = scores[best_mood]
        maturity = self.personality.get_maturity()
        maturity_bias = maturity ** 1.5
        # Stronger maturity bias for inertia/interp_alpha
        interp_alpha = 0.08 + 0.10 * maturity_bias
        interp_alpha = min(0.25, interp_alpha)  # Clamp for stability
        mood_changed = best_mood != self.current_mood
        if best_mood == self.current_mood:
            self.mood_life += 1.0
            self.mood_intensity = (1 - interp_alpha) * self.mood_intensity + interp_alpha * 1.0
        else:
            self.last_mood = self.current_mood
            self.last_intensity = self.mood_intensity
            self.current_mood = best_mood
            self.mood_intensity = (1 - interp_alpha) * self.mood_intensity + interp_alpha * 0.2
            self.mood_life = 0.0
            # When mood changes, trigger a related emotion with moderate intensity
            if self.emotion_system:
                mood_to_emotion = {
                    'Happy': 'Delighted', 'Sad': 'Afraid', 'Curious': 'Surprised', 'Sleepy': 'Calm',
                    'Excited': 'Surprised', 'Anxious': 'Afraid', 'Confused': 'Ashamed', 'Content': 'Relieved',
                    'Bored': 'Lonely', 'Hot': 'Irritated', 'Cold': 'Lonely', 'Neutral': 'Calm', 'Uncertain': 'Ashamed'
                }
                emo = mood_to_emotion.get(self.current_mood.split()[0], None)
                if emo and emo in self.emotion_system.EMOTIONS:
                    self.emotion_system.trigger(emo, intensity=0.5)
                # Increase chance of spontaneous emotion on mood change
                if random.random() < 0.2:
                    spontaneous = self.emotion_system._weighted_random_emotion()
                    if spontaneous not in self.emotion_system.active_emotions:
                        self.emotion_system.trigger(spontaneous, intensity=0.3)
        if random.random() < 0.02 * (1.0 - 0.7 * maturity):
            self.current_mood = self._weighted_random_mood()
            self.mood_intensity = 1.0
            self.mood_life = 0.0
        emo = None
        emo_int = 0.0
        if self.emotion_system and self.emotion_system.get_emotion():
            emo = self.emotion_system.get_emotion()
            emo_int = self.emotion_system.get_intensity()
            if emo_int > 0.7:
                self.current_mood = emo
                self.mood_intensity = emo_int
                self.mood_life = 0.0
            elif emo_int > 0.2:
                self.current_mood = f"{self.current_mood} ({emo})"
                self.mood_intensity = max(self.mood_intensity, emo_int)
        if emo and emo_int > 0.2:
            if emo.lower() not in self.current_mood.lower() and self.current_mood.lower() not in emo.lower():
                self.current_mood = 'Uncertain'
                self.mood_intensity = min(self.mood_intensity, emo_int)
        if (self.mood_intensity > 0.7 or emo_int > 0.7) and self.mood_life > 4:
            blended_emotions = self.emotion_system.get_blended_emotions() if self.emotion_system else None
            self.personality.drift_traits(
                drift_strength=0.005,  # even slower drift
                mood=self.current_mood,
                mood_intensity=self.mood_intensity,
                emotion=emo,
                emotion_intensity=emo_int,
                blended_emotions=blended_emotions
            )
            self.mood_life = 0.0
        if self.current_mood:
            self.history.append(self.current_mood)
            if len(self.history) > self.HISTORY_LENGTH:
                self.history = self.history[-self.HISTORY_LENGTH:]

    def get_mood(self) -> str:
        return self.current_mood

    def get_mood_intensity(self) -> float:
        return self.mood_intensity

    def as_dict(self) -> Dict[str, Any]:
        return {
            'current_mood': self.current_mood,
            'mood_intensity': self.mood_intensity,
            'possible_moods': self.MOODS,
            'emotion': self.emotion_system.as_dict() if self.emotion_system else None,
            'mood_history': self.history[-self.HISTORY_LENGTH:]
        }

# Example usage
if __name__ == "__main__":
    p = Personality()
    e = EmotionSystem(get_maturity_fn=p.get_maturity, get_personality_fn=p.as_dict)
    m = MoodSystem(p, e)
    print("Initial traits:", p.as_dict(rounded=True))
    for i in range(30):
        p.age_up()
        if i == 3:
            e.trigger('Surprised', intensity=1.0)
        if i == 6:
            e.trigger('Angry', intensity=0.8)
        if i == 12:
            e.trigger('Delighted', intensity=0.9)
        e.update()
        m.update_mood({'temperature': random.randint(10, 35), 'activity': random.choice(['none', 'talking', 'playing'])})
        print(f"Traits after drift {i+1}:", p.as_dict(rounded=True))
        print(f"Current mood: {m.get_mood()} (intensity: {m.get_mood_intensity():.2f}) | Emotion: {e.get_emotion()} ({e.get_intensity():.2f}) | Age: {p.age:.1f} | Maturity: {p.get_maturity():.2f}") 