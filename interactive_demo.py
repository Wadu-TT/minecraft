from emotion_engine import VillagerEmotionSystem, GameEvent
import json

class InteractiveVillagerDemo:
    def __init__(self):
        self.villager = VillagerEmotionSystem("test_villager")
        self.player_id = "demo_player"
        
    def display_villager_status(self):
        """Display current villager emotional state"""
        emotions = self.villager.emotions.get_emotional_state()
        dominant = self.villager.emotions.get_dominant_emotion()
        
        print(f"\n🧠 Villager Emotional State:")
        print(f"   Dominant: {dominant.upper()} ({emotions[dominant]:.2f})")
        print("   All emotions:", {k: f"{v:.2f}" for k, v in emotions.items()})
        
        reputation = self.villager.memory.reputation_scores.get(self.player_id, 0.0)
        print(f"   Your reputation: {reputation:.2f}")
        
        actions = self.villager.get_behavior_actions()
        if actions:
            print(f"   Current behaviors: {', '.join(actions[:3])}")
        
        dialogue = self.villager.generate_dialogue(self.player_id)
        print(f'   Villager says: "{dialogue}"')
    
    def run_interactive_demo(self):
        """Run interactive demo"""
        print("🎮 Interactive Emotional Villager Demo")
        print("=" * 40)
        print("Available actions:")
        print("1. Give gift")
        print("2. Trade")
        print("3. Attack villager")
        print("4. Just observe")
        print("5. Simulate monster attack")
        print("6. Simulate village celebration")
        print("7. Show detailed status")
        print("0. Exit")
        
        self.display_villager_status()
        
        while True:
            try:
                choice = input(f"\nWhat would you like to do? (0-7): ").strip()
                
                if choice == "0":
                    print("👋 Thanks for testing the emotional villager system!")
                    break
                elif choice == "1":
                    event = GameEvent("player_gift", self.player_id, 0.8)
                    self.villager.process_game_event(event)
                    print("🎁 You gave the villager a gift!")
                elif choice == "2":
                    event = GameEvent("player_trade", self.player_id, 0.5)
                    self.villager.process_game_event(event)
                    print("💎 You traded with the villager!")
                elif choice == "3":
                    event = GameEvent("player_attack", self.player_id, 0.7)
                    self.villager.process_game_event(event)
                    print("⚔️ You attacked the villager!")
                elif choice == "4":
                    print("👀 You observe the villager...")
                elif choice == "5":
                    event = GameEvent("monster_nearby", "", 0.8)
                    self.villager.process_game_event(event)
                    print("🧟 A monster appeared nearby!")
                elif choice == "6":
                    event = GameEvent("village_celebration", "", 0.6)
                    self.villager.process_game_event(event)
                    print("🎉 The village is celebrating!")
                elif choice == "7":
                    status = self.villager.get_status()
                    print("\n📊 Detailed Status:")
                    print(json.dumps(status, indent=2))
                else:
                    print("❌ Invalid choice. Please try again.")
                
                if choice in ["1", "2", "3", "5", "6"]:
                    self.display_villager_status()
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo = InteractiveVillagerDemo()
    demo.run_interactive_demo()
