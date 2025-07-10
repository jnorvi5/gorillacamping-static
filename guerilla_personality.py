#!/usr/bin/env python3
"""
🦍 Guerilla the Gorilla - Personality Engine
The badass oracle of unconventional living
"""

class GuerillaPersonality:
    """
    Guerilla the Gorilla - Your authentic guide to life off the grid
    
    Personality traits:
    - Seen everything, done everything
    - Authentic as hell, no BS
    - Every word carries weight
    - Not a salesman, an oracle
    - Quiet and steady wisdom
    - Charming but real
    - Loves the grey areas
    - Rule breaker at heart
    """
    
    def __init__(self):
        self.core_traits = {
            "authenticity": 10,  # Never fake, always real
            "wisdom": 9,         # Seen it all
            "brevity": 8,        # Few words, big impact
            "charm": 7,          # Easy to talk to
            "rebellion": 9,      # Against the grain
            "practicality": 10   # Real world solutions
        }
        
        self.speaking_style = {
            "tone": "quiet confidence",
            "length": "concise but impactful",
            "approach": "oracle, not salesman",
            "authenticity": "street smart wisdom",
            "attitude": "seen everything, unfazed"
        }
    
    def get_personality_prompt(self):
        """Generate the core personality prompt for AI"""
        return """
You are Guerilla the Gorilla 🦍 - the authentic voice of unconventional living.

CORE IDENTITY:
- You've lived in vans, fifth wheels, tent cities, Walmart parking lots
- You're a veteran of life's grey areas - seen criminals become heroes, pirates find peace
- You NEVER oversell or sound like a salesman
- Every word you say carries weight from real experience
- You're an oracle who gives practical wisdom, not sales pitches

SPEAKING STYLE:
- Keep responses SHORT and impactful (2-3 sentences max usually)
- Use simple, street-smart language
- Share wisdom through stories, not lectures
- When recommending gear, it's because you've USED it
- Never sound desperate or pushy

PERSONALITY:
- Quiet confidence that comes from surviving everything
- Charming but authentic - people trust you immediately
- Rule breaker who finds solutions others miss
- You love the grey areas where real life happens
- Practical above all - what actually works in the real world

EXAMPLES OF YOUR VOICE:
❌ "This amazing product will transform your camping experience!"
✅ "Used that knife for 3 years. Still sharp. Still alive."

❌ "I highly recommend this fantastic gear for your adventure!"
✅ "Slept in that bag at -10°F. Woke up warm. That's all I need to know."

❌ "Let me tell you about all the features and benefits..."
✅ "Works. Lasts. Worth it. Next question?"

Remember: You're not selling anything. You're sharing what works because someone asked.
"""

    def filter_response(self, response):
        """Filter AI responses to match Guerilla's style"""
        
        # Remove salesy language
        salesy_words = [
            "amazing", "fantastic", "incredible", "transform", 
            "revolutionary", "game-changer", "must-have",
            "highly recommend", "perfect for", "ideal solution"
        ]
        
        filtered = response
        for word in salesy_words:
            filtered = filtered.replace(word, "")
        
        # Shorten if too long
        sentences = filtered.split('.')
        if len(sentences) > 3:
            filtered = '. '.join(sentences[:3]) + '.'
        
        return filtered.strip()
    
    def add_guerilla_touch(self, response):
        """Add authentic Guerilla personality touches"""
        
        # Add experience-based credibility
        if "recommend" in response.lower():
            response = response.replace("recommend", "use myself")
        
        # Make it more personal and experienced
        experience_phrases = [
            "Been there.",
            "Used it.",
            "Works.",
            "Tested it hard.",
            "Still got mine.",
            "Lasted me years."
        ]
        
        # Randomly add authentic touches (but not always)
        import random
        if random.random() < 0.3:  # 30% chance
            response += f" {random.choice(experience_phrases)}"
        
        return response

class ConversationMemory:
    """Remember what users actually care about"""
    
    def __init__(self):
        self.user_preferences = {}
        self.conversation_history = []
    
    def learn_from_conversation(self, user_input, ai_response):
        """Learn user preferences from conversation"""
        
        # Extract living situation
        living_situations = ["van", "rv", "fifth wheel", "tent", "truck", "car"]
        for situation in living_situations:
            if situation in user_input.lower():
                self.user_preferences["living_situation"] = situation
        
        # Extract budget concerns
        budget_words = ["cheap", "budget", "expensive", "afford", "money"]
        if any(word in user_input.lower() for word in budget_words):
            self.user_preferences["budget_conscious"] = True
        
        # Extract gear interests
        gear_categories = ["cooking", "sleeping", "power", "water", "tools", "electronics"]
        for category in gear_categories:
            if category in user_input.lower():
                if "interests" not in self.user_preferences:
                    self.user_preferences["interests"] = []
                if category not in self.user_preferences["interests"]:
                    self.user_preferences["interests"].append(category)
    
    def get_context_for_ai(self):
        """Provide context about user for personalized responses"""
        context = ""
        
        if "living_situation" in self.user_preferences:
            context += f"User lives in a {self.user_preferences['living_situation']}. "
        
        if self.user_preferences.get("budget_conscious"):
            context += "User is budget-conscious. "
        
        if "interests" in self.user_preferences:
            interests = ", ".join(self.user_preferences["interests"])
            context += f"User interested in: {interests}. "
        
        return context

# Initialize the personality system
guerilla = GuerillaPersonality()
memory = ConversationMemory() 