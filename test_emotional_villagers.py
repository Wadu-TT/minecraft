import time
import json
from emotion_engine import VillagerEmotionSystem, GameEvent

class EmotionalVillagerTestSuite:
    def __init__(self):
        self.villagers = {}
        self.test_results = []
    
    def create_test_village(self, num_villagers: int = 3):
        """Create a test village with multiple villagers"""
        for i in range(num_villagers):
            villager_id = f"villager_{i+1}"
            self.villagers[villager_id] = VillagerEmotionSystem(villager_id)
            print(f"Created {villager_id} with personality: {self.villagers[villager_id].personality.traits}")
    
    def simulate_player_interactions(self):
        """Simulate various player interactions"""
        test_events = [
            GameEvent("player_gift", "player1", 0.8, {"item": "emerald"}),
            GameEvent("player_trade", "player1", 0.5, {"trade_type": "wheat"}),
            GameEvent("player_attack", "player2", 1.0, {"damage": 2}),
            GameEvent("monster_nearby", "", 0.7, {"monster_type": "zombie"}),
            GameEvent("village_celebration", "", 0.6, {"event": "harvest_festival"}),
            GameEvent("player_gift", "player1", 0.9, {"item": "diamond"}),
            GameEvent("night_time", "", 0.3, {}),
            GameEvent("player_attack", "player1", 0.4, {"damage": 1})
        ]
        
        print("\n=== Simulating Player Interactions ===")
        
        for i, event in enumerate(test_events):
            print(f"\nEvent {i+1}: {event.event_type} (Player: {event.player_id}, Intensity: {event.intensity})")
            
            # Process event for all villagers
            for villager_id, villager in self.villagers.items():
                actions = villager.process_game_event(event)
                emotions = villager.emotions.get_emotional_state()
                dominant_emotion = villager.emotions.get_dominant_emotion()
                
                print(f"  {villager_id}:")
                print(f"    Dominant Emotion: {dominant_emotion} ({emotions[dominant_emotion]:.2f})")
                print(f"    Actions: {actions}")
                
                # Generate dialogue if player involved
                if event.player_id:
                    dialogue = villager.generate_dialogue(event.player_id)
                    print(f"    Says: \"{dialogue}\"")
            
            # Simulate social contagion between villagers
            self.process_village_social_dynamics()
            
            # Wait a bit for more realistic timing
            time.sleep(0.5)
    
    def process_village_social_dynamics(self):
        """Simulate social contagion between villagers"""
        villager_list = list(self.villagers.values())
        
        for villager in villager_list:
            # Each villager is affected by others (simplified - in real game would be distance-based)
            nearby_villagers = [v for v in villager_list if v != villager]
            villager.process_social_contagion(nearby_villagers)
    
    def test_emotional_memory(self):
        """Test if villagers remember past interactions"""
        print("\n=== Testing Emotional Memory ===")
        
        villager = list(self.villagers.values())[0]
        
        # Test with different players
        print(f"\nPlayer1 reputation: {villager.memory.reputation_scores.get('player1', 0.0):.2f}")
        print(f"Player2 reputation: {villager.memory.reputation_scores.get('player2', 0.0):.2f}")
        
        # Test dialogue differences
        dialogue1 = villager.generate_dialogue("player1", "trade")
        dialogue2 = villager.generate_dialogue("player2", "trade")
        
        print(f"Dialogue to player1: \"{dialogue1}\"")
        print(f"Dialogue to player2: \"{dialogue2}\"")
    
    def test_personality_differences(self):
        """Test how different personalities affect emotional responses"""
        print("\n=== Testing Personality Differences ===")
        
        # Create test event
        test_event = GameEvent("player_attack", "test_player", 0.6)
        
        for villager_id, villager in self.villagers.items():
            print(f"\n{villager_id} Personality:")
            for trait, value in villager.personality.traits.items():
                print(f"  {trait}: {value:.2f}")
            
            # Store initial emotions
            initial_emotions = villager.emotions.get_emotional_state().copy()
            
            # Process event
            villager.process_game_event(test_event)
            final_emotions = villager.emotions.get_emotional_state()
            
            # Show emotional change
            print("  Emotional Response to Attack:")
            for emotion in initial_emotions:
                change = final_emotions[emotion] - initial_emotions[emotion]
                if abs(change) > 0.01:  # Only show significant changes
                    print(f"    {emotion}: {initial_emotions[emotion]:.2f} → {final_emotions[emotion]:.2f} ({change:+.2f})")
    
    def display_villager_status(self):
        """Display current status of all villagers"""
        print("\n=== Current Villager Status ===")
        
        for villager_id, villager in self.villagers.items():
            status = villager.get_status()
            print(f"\n{villager_id}:")
            print(f"  Dominant Emotion: {status['dominant_emotion']}")
            print("  Emotions:", {k: f"{v:.2f}" for k, v in status['emotions'].items()})
            print("  Top Behaviors:", [action for action in status['recent_actions'][:3]])
            print("  Player Reputations:", {k: f"{v:.2f}" for k, v in status['reputation_scores'].items()})
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        print("🎮 Emotional Minecraft Villagers Test Suite")
        print("=" * 50)
        
        # Create village
        self.create_test_village(3)
        
        # Run tests
        self.simulate_player_interactions()
        self.test_emotional_memory()
        self.test_personality_differences()
        self.display_villager_status()
        
        print("\n✅ Test suite completed!")

if __name__ == "__main__":
    # Run the test
    test_suite = EmotionalVillagerTestSuite()
    test_suite.run_full_test_suite()
