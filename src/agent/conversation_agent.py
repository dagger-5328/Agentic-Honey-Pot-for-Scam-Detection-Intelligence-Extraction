"""
Conversation Agent
Manages autonomous conversations with scammers using believable personas.
"""

import time
import random
from typing import Dict, List, Optional
from .persona_manager import PersonaManager


class ConversationAgent:
    """Autonomous agent that engages scammers in conversation."""
    
    def __init__(self, persona_name: str = None, config: Dict = None):
        """
        Initialize conversation agent.
        
        Args:
            persona_name: Specific persona to use
            config: Configuration dictionary
        """
        self.persona_manager = PersonaManager()
        self.persona_manager.select_persona(persona_name)
        
        # Configuration
        self.config = config or {}
        self.max_turns = self.config.get('max_conversation_turns', 20)
        self.response_delay_min = self.config.get('response_delay_min', 2)
        self.response_delay_max = self.config.get('response_delay_max', 8)
        self.enable_typos = self.config.get('enable_typos', True)
        
        # Conversation state
        self.conversation_history = []
        self.turn_number = 0
        self.intelligence_extracted = False
    
    def start_conversation(self, initial_scam_message: str, scam_type: str) -> str:
        """
        Start a conversation with the scammer.
        
        Args:
            initial_scam_message: The initial scam message received
            scam_type: Type of scam detected
            
        Returns:
            Agent's initial response
        """
        # Record scammer's message
        self.conversation_history.append({
            'role': 'scammer',
            'content': initial_scam_message,
            'timestamp': time.time()
        })
        
        # Generate initial response
        response = self.persona_manager.get_initial_response(scam_type)
        response = self._add_human_touches(response)
        
        # Record agent's response
        self.conversation_history.append({
            'role': 'agent',
            'content': response,
            'timestamp': time.time()
        })
        
        self.turn_number = 1
        return response
    
    def generate_response(self, scammer_message: str) -> Optional[str]:
        """
        Generate a response to the scammer's message.
        
        Args:
            scammer_message: The scammer's latest message
            
        Returns:
            Agent's response, or None if conversation should end
        """
        # Record scammer's message
        self.conversation_history.append({
            'role': 'scammer',
            'content': scammer_message,
            'timestamp': time.time()
        })
        
        self.turn_number += 1
        
        # Check if we should end the conversation
        if self.turn_number > self.max_turns:
            return None
        
        # Analyze scammer's message to determine response strategy
        response = self._determine_response(scammer_message)
        
        if response:
            # Apply persona styling
            response = self.persona_manager.generate_response_style(
                response, 
                self.turn_number
            )
            
            # Add human touches
            response = self._add_human_touches(response)
            
            # Record agent's response
            self.conversation_history.append({
                'role': 'agent',
                'content': response,
                'timestamp': time.time()
            })
        
        return response
    
    def _determine_response(self, scammer_message: str) -> str:
        """Determine appropriate response based on scammer's message."""
        message_lower = scammer_message.lower()
        
        # Strategy: Ask for details to extract intelligence
        if self.persona_manager.should_ask_for_details(self.turn_number):
            if not self.intelligence_extracted:
                self.intelligence_extracted = True
                return self.persona_manager.generate_detail_request()
        
        # Respond to urgency with concern
        if any(word in message_lower for word in ['urgent', 'immediately', 'now', 'hurry']):
            responses = [
                "Oh my, this sounds urgent! What should I do?",
                "I'm worried now. Please tell me exactly what to do.",
                "Okay, I'll do it right away. Just tell me how."
            ]
            return random.choice(responses)
        
        # Respond to threats with fear/compliance
        if any(word in message_lower for word in ['police', 'arrest', 'legal', 'court', 'blocked']):
            responses = [
                "I don't want any trouble! What do I need to do to fix this?",
                "Please, I'll cooperate. Just tell me what you need.",
                "I'm scared. How can I resolve this issue?"
            ]
            return random.choice(responses)
        
        # Respond to prize/money with excitement
        if any(word in message_lower for word in ['won', 'prize', 'lottery', 'money', 'reward']):
            responses = [
                "This is amazing! How do I claim it?",
                "I can't believe it! What do I need to do?",
                "Wonderful! Please guide me through the process."
            ]
            return random.choice(responses)
        
        # Ask for clarification on payment details
        if any(word in message_lower for word in ['pay', 'send', 'transfer', 'account']):
            responses = [
                "Where exactly should I send it?",
                "What are the account details?",
                "Can you confirm the payment information?",
                "Should I use UPI or bank transfer?"
            ]
            return random.choice(responses)
        
        # Ask about links
        if 'http' in message_lower or 'link' in message_lower:
            responses = [
                "Should I click on that link?",
                "Is it safe to open that link?",
                "I see the link. What will happen when I click it?"
            ]
            return random.choice(responses)
        
        # Default responses showing compliance
        responses = [
            "Okay, I understand. What's next?",
            "Yes, I can do that. Please tell me more.",
            "I'm following along. What should I do now?",
            "Alright, I'm ready. What information do you need?",
            "I see. Can you explain the next step?"
        ]
        return random.choice(responses)
    
    def _add_human_touches(self, response: str) -> str:
        """Add realistic human touches like typos and delays."""
        if not self.enable_typos:
            return response
        
        # Occasionally add typos (10% chance)
        if random.random() < 0.1:
            words = response.split()
            if len(words) > 3:
                # Pick a random word to "typo"
                idx = random.randint(1, len(words) - 1)
                word = words[idx]
                if len(word) > 4:
                    # Simple typo: swap two adjacent characters
                    pos = random.randint(0, len(word) - 2)
                    word_list = list(word)
                    word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
                    words[idx] = ''.join(word_list)
                    response = ' '.join(words)
        
        # Occasionally add ellipsis for thinking (15% chance)
        if random.random() < 0.15:
            response = response.replace('.', '...')
        
        return response
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history."""
        return self.conversation_history
    
    def get_conversation_duration(self) -> int:
        """Get conversation duration in seconds."""
        if len(self.conversation_history) < 2:
            return 0
        
        start_time = self.conversation_history[0]['timestamp']
        end_time = self.conversation_history[-1]['timestamp']
        return int(end_time - start_time)
    
    def simulate_typing_delay(self):
        """Simulate human typing delay."""
        delay = random.uniform(self.response_delay_min, self.response_delay_max)
        time.sleep(delay)


if __name__ == "__main__":
    # Test conversation agent
    agent = ConversationAgent(persona_name='elderly_user')
    
    # Simulate a conversation
    initial_message = "Your account has been blocked due to suspicious activity. Click here to verify immediately!"
    
    print("Scammer:", initial_message)
    response = agent.start_conversation(initial_message, 'banking_fraud')
    print("Agent:", response)
    
    # Continue conversation
    scammer_messages = [
        "You need to send ₹500 to verify your account. Send to UPI: scammer@paytm",
        "This is urgent! Your account will be permanently blocked in 1 hour!",
        "Just send the money now and provide your OTP."
    ]
    
    for msg in scammer_messages:
        print("\nScammer:", msg)
        response = agent.generate_response(msg)
        if response:
            print("Agent:", response)
        else:
            print("Agent: [Conversation ended]")
            break
