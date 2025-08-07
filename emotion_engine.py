import numpy as np
import json
import time
import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import deque
import threading

@dataclass
class GameEvent:
    event_type: str
    player_id: str
    intensity: float
    context: Dict = None

class EmotionVector:
    def __init__(self):
        self.emotions = {
            'joy': 0.0,
            'anger': 0.0,
            'fear': 0.0,
            'sadness': 0.0,
            'trust': 0.0,
            'curiosity': 0.0
        }
        self.intensity = 1.0
        self.last_update = time.time()
    
    def update_emotion(self, emotion_delta: Dict[str, float], decay_rate: float = 0.98):
        """Update emotions with temporal decay"""
        current_time = time.time()
        time_passed = current_time - self.last_update
        
        # Apply temporal decay based on time passed
        decay_factor = decay_rate ** time_passed
        
        for emotion in self.emotions:
            # Apply decay
            self.emotions[emotion] *= decay_factor
            
            # Add new emotion if present in delta
            if emotion in emotion_delta:
                new_value = self.emotions[emotion] + emotion_delta[emotion]
                self.emotions[emotion] = np.clip(new_value, -1.0, 1.0)
        
        self.last_update = current_time
    
    def get_dominant_emotion(self) -> str:
        """Get the strongest emotion"""
        return max(self.emotions.items(), key=lambda x: abs(x[1]))[0]
    
    def get_emotional_state(self) -> Dict[str, float]:
        """Return current emotional state"""
        return self.emotions.copy()
    
    def blend_emotions(self, other_emotions: Dict[str, float], blend_factor: float = 0.1):
        """Blend with another emotion vector (for social contagion)"""
        for emotion, value in other_emotions.items():
            if emotion in self.emotions:
                blended_value = self.emotions[emotion] * (1 - blend_factor) + value * blend_factor
                self.emotions[emotion] = np.clip(blended_value, -1.0, 1.0)

class VillagerPersonality:
    def __init__(self):
        self.traits = {
            'emotional_stability': random.uniform(0.3, 0.8),
            'socialness': random.uniform(0.2, 0.9),
            'fearfulness': random.uniform(0.1, 0.7),
            'optimism': random.uniform(0.2, 0.8),
            'curiosity': random.uniform(0.3, 0.9)
        }
    
    def modify_emotional_response(self, emotion_delta: Dict[str, float]) -> Dict[str, float]:
        """Modify emotion response based on personality - FIXED VERSION"""
        modified_delta = emotion_delta.copy()
        
        # Apply personality modifiers only to emotions that exist in the response
        for emotion in modified_delta:
            if emotion == 'joy':
                modified_delta[emotion] *= (1.0 + self.traits['optimism'])
            elif emotion == 'fear':
                modified_delta[emotion] *= (1.0 + self.traits['fearfulness'])
            elif emotion == 'curiosity':
                modified_delta[emotion] *= (1.0 + self.traits['curiosity'])
            
            # Apply emotional stability to all emotions
            modified_delta[emotion] *= self.traits['emotional_stability']
        
        return modified_delta

class EmotionalMemory:
    def __init__(self, max_memories: int = 100):
        self.player_relationships = {}
        self.event_memories = deque(maxlen=max_memories)
        self.reputation_scores = {}
    
    def record_interaction(self, player_id: str, event_type: str, emotional_response: Dict[str, float]):
        """Record emotional interaction with player"""
        timestamp = time.time()
        
        # Update player relationship
        if player_id not in self.player_relationships:
            self.player_relationships[player_id] = EmotionVector()
        
        self.player_relationships[player_id].update_emotion(emotional_response, decay_rate=0.995)
        
        # Store memory
        memory = {
            'player_id': player_id,
            'event_type': event_type,
            'emotional_response': emotional_response,
            'timestamp': timestamp
        }
        self.event_memories.append(memory)
        
        # Update reputation
        self.update_reputation(player_id, emotional_response)
    
    def update_reputation(self, player_id: str, emotional_response: Dict[str, float]):
        """Update player reputation based on emotional response"""
        if player_id not in self.reputation_scores:
            self.reputation_scores[player_id] = 0.0
        
        # Positive emotions increase reputation, negative decrease it
        reputation_change = (
            emotional_response.get('joy', 0) * 0.5 +
            emotional_response.get('trust', 0) * 0.7 -
            emotional_response.get('anger', 0) * 0.8 -
            emotional_response.get('fear', 0) * 0.3
        )
        
        self.reputation_scores[player_id] += reputation_change * 0.1
        self.reputation_scores[player_id] = np.clip(self.reputation_scores[player_id], -1.0, 1.0)
    
    def get_player_bias(self, player_id: str) -> Dict[str, float]:
        """Get emotional bias toward specific player"""
        if player_id in self.player_relationships:
            return self.player_relationships[player_id].get_emotional_state()
        return {'joy': 0, 'anger': 0, 'fear': 0, 'sadness': 0, 'trust': 0, 'curiosity': 0}

class VillagerEmotionSystem:
    def __init__(self, villager_id: str):
        self.villager_id = villager_id
        self.emotions = EmotionVector()
        self.personality = VillagerPersonality()
        self.memory = EmotionalMemory()
        
        # Behavior weights based on emotions
        self.behavior_weights = {}
        self.update_behavior_weights()
        
        # Event response mappings
        self.event_responses = {
            'player_gift': {'joy': 0.6, 'trust': 0.4},
            'player_attack': {'anger': 0.8, 'fear': 0.3, 'trust': -0.5},
            'player_trade': {'joy': 0.3, 'trust': 0.2},
            'monster_nearby': {'fear': 0.7, 'sadness': 0.2},
            'village_celebration': {'joy': 0.5, 'curiosity': 0.3},
            'night_time': {'fear': 0.2, 'sadness': 0.1},
            'sunny_weather': {'joy': 0.2, 'curiosity': 0.1}
        }
    
    def process_game_event(self, event: GameEvent):
        """Process a game event and update emotional state"""
        if event.event_type in self.event_responses:
            base_response = self.event_responses[event.event_type].copy()
            
            # Scale by event intensity
            for emotion in base_response:
                base_response[emotion] *= event.intensity
            
            # Apply personality modifiers
            modified_response = self.personality.modify_emotional_response(base_response)
            
            # Update emotions
            self.emotions.update_emotion(modified_response)
            
            # Record in memory if player involved
            if event.player_id:
                self.memory.record_interaction(event.player_id, event.event_type, modified_response)
            
            # Update behavior weights
            self.update_behavior_weights()
            
            return self.get_behavior_actions()
        
        return []
    
    def update_behavior_weights(self):
        """Update behavior action weights based on current emotions"""
        emotions = self.emotions.get_emotional_state()
        
        self.behavior_weights = {
            # Social behaviors
            'approach_player': max(0, emotions['joy'] * 0.8 + emotions['curiosity'] * 0.5 - emotions['fear'] * 0.6),
            'give_gift': max(0, emotions['joy'] * 0.9 + emotions['trust'] * 0.7),
            'wave_greeting': max(0, emotions['joy'] * 0.6 + emotions['curiosity'] * 0.4),
            'follow_player': max(0, emotions['joy'] * 0.5 + emotions['trust'] * 0.8 - emotions['fear'] * 0.3),
            
            # Defensive behaviors  
            'flee_from_player': max(0, emotions['fear'] * 0.9 + emotions['anger'] * 0.3),
            'hide_indoors': max(0, emotions['fear'] * 0.8 + emotions['sadness'] * 0.4),
            'call_for_help': max(0, emotions['fear'] * 0.7 + emotions['anger'] * 0.5),
            'avoid_interaction': max(0, emotions['anger'] * 0.6 + emotions['sadness'] * 0.7),
            
            # Work behaviors
            'work_efficiency': 1.0 + emotions['joy'] * 0.3 - emotions['sadness'] * 0.4 - emotions['fear'] * 0.2,
            'trading_willingness': max(0.1, 1.0 + emotions['joy'] * 0.4 + emotions['trust'] * 0.6 - emotions['anger'] * 0.8),
            
            # Exploration behaviors
            'explore_area': max(0, emotions['curiosity'] * 0.8 + emotions['joy'] * 0.3 - emotions['fear'] * 0.5),
            'investigate_sounds': max(0, emotions['curiosity'] * 0.7 - emotions['fear'] * 0.4)
        }
    
    def get_behavior_actions(self) -> List[str]:
        """Get list of actions villager should perform based on emotional state"""
        actions = []
        
        for behavior, weight in self.behavior_weights.items():
            # Use weight as probability threshold
            if random.random() < weight:
                actions.append(behavior)
        
        return actions
    
    def process_social_contagion(self, nearby_villagers: List['VillagerEmotionSystem']):
        """Process emotional contagion from nearby villagers"""
        if not nearby_villagers:
            return
        
        # Average nearby emotions with distance weighting
        social_emotions = {'joy': 0, 'anger': 0, 'fear': 0, 'sadness': 0, 'trust': 0, 'curiosity': 0}
        total_weight = 0
        
        for villager in nearby_villagers:
            villager_emotions = villager.emotions.get_emotional_state()
            # Simple distance weighting (could be enhanced with actual positions)
            weight = 1.0 / len(nearby_villagers)
            
            for emotion in social_emotions:
                social_emotions[emotion] += villager_emotions[emotion] * weight
            total_weight += weight
        
        # Normalize and apply social contagion
        if total_weight > 0:
            for emotion in social_emotions:
                social_emotions[emotion] /= total_weight
            
            # Blend with current emotions (stronger social villagers are more affected)
            contagion_strength = self.personality.traits['socialness'] * 0.1
            self.emotions.blend_emotions(social_emotions, contagion_strength)
    
    def generate_dialogue(self, player_id: str, topic: str = "general") -> str:
        """Generate contextual dialogue based on emotional state"""
        emotions = self.emotions.get_emotional_state()
        player_bias = self.memory.get_player_bias(player_id)
        reputation = self.memory.reputation_scores.get(player_id, 0.0)
        
        # Determine dominant emotion considering player relationship
        combined_joy = emotions['joy'] + player_bias.get('joy', 0) * 0.3
        combined_anger = emotions['anger'] + player_bias.get('anger', 0) * 0.3
        combined_fear = emotions['fear'] + player_bias.get('fear', 0) * 0.3
        
        if combined_joy > 0.4:
            responses = [
                f"Hello there! It's wonderful to see you again!",
                f"What a beautiful day! How can I help you?",
                f"*cheerful sounds* Trading today?",
                f"You always bring such good energy to our village!"
            ]
        elif combined_anger > 0.3:
            responses = [
                f"*grumbles* What do you want?",
                f"I'm not in the mood for visitors right now.",
                f"Haven't you caused enough trouble already?",
                f"Make it quick. I have important things to do."
            ]
        elif combined_fear > 0.3:
            responses = [
                f"*nervous sounds* P-please don't hurt me...",
                f"I... I don't have anything valuable...",
                f"Are you here to cause trouble again?",
                f"*whispers* Maybe you should talk to the iron golem instead..."
            ]
        else:
            responses = [
                f"Greetings, traveler. How may I assist you?",
                f"Welcome to our village. What brings you here?",
                f"*nods politely* Good to see you.",
                f"The weather has been quite nice lately, hasn't it?"
            ]
        
        # Add reputation-based modifier
        selected_response = random.choice(responses)
        if reputation < -0.5:
            selected_response += " *eyes you suspiciously*"
        elif reputation > 0.5:
            selected_response += " *smiles warmly*"
        
        return selected_response
    
    def get_status(self) -> Dict:
        """Get current villager emotional and behavioral status"""
        return {
            'villager_id': self.villager_id,
            'emotions': self.emotions.get_emotional_state(),
            'dominant_emotion': self.emotions.get_dominant_emotion(),
            'personality': self.personality.traits,
            'behavior_weights': self.behavior_weights,
            'reputation_scores': self.memory.reputation_scores.copy(),
            'recent_actions': self.get_behavior_actions()
        }
