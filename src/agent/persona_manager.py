"""
Persona Manager
Manages different victim personas for realistic scam engagement.
"""

import json
import random
from typing import Dict, List
from pathlib import Path


class PersonaManager:
    """Manages victim personas and generates persona-appropriate responses."""
    
    def __init__(self, personas_file: str = None):
        """Initialize persona manager with persona database."""
        if personas_file is None:
            personas_file = Path(__file__).parent.parent.parent / "data" / "personas.json"
        
        with open(personas_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.personas = data['personas']
        self.strategies = data['conversation_strategies']
        self.current_persona = None
    
    def select_persona(self, persona_name: str = None) -> Dict:
        """
        Select a persona to use for the conversation.
        
        Args:
            persona_name: Specific persona to use, or None for random selection
            
        Returns:
            Selected persona dictionary
        """
        if persona_name and persona_name in self.personas:
            self.current_persona = self.personas[persona_name]
            self.current_persona['id'] = persona_name
        else:
            # Random selection
            persona_name = random.choice(list(self.personas.keys()))
            self.current_persona = self.personas[persona_name]
            self.current_persona['id'] = persona_name
        
        return self.current_persona
    
    def get_persona_info(self) -> Dict:
        """Get current persona information."""
        return self.current_persona
    
    def generate_response_style(self, base_response: str, turn_number: int) -> str:
        """
        Modify a response to match persona characteristics.
        
        Args:
            base_response: The base response text
            turn_number: Current conversation turn (for progression)
            
        Returns:
            Modified response matching persona style
        """
        if not self.current_persona:
            return base_response
        
        response = base_response
        
        # Add persona-specific modifications
        persona_id = self.current_persona['id']
        
        if persona_id == 'elderly_user':
            # Add hesitation and confusion
            if turn_number <= 2:
                response = f"I'm not sure I understand... {response}"
            # Add concern about safety
            if random.random() < 0.3:
                response += " Is this safe?"
        
        elif persona_id == 'eager_customer':
            # Add excitement
            if 'prize' in base_response.lower() or 'won' in base_response.lower():
                response = f"Really?! {response}"
            # Add urgency
            if random.random() < 0.4:
                response += " How quickly can we do this?"
        
        elif persona_id == 'worried_parent':
            # Add concern
            if turn_number <= 3:
                response = f"Oh no, {response}"
            # Add family references
            if random.random() < 0.3:
                response += " I need to make sure my family is safe."
        
        elif persona_id == 'busy_professional':
            # Add time pressure
            if turn_number == 1:
                response = f"I'm quite busy, but {response}"
            # Add brevity
            if random.random() < 0.5:
                response = response.split('.')[0] + '.'  # Keep it short
        
        return response
    
    def get_initial_response(self, scam_type: str) -> str:
        """
        Get an appropriate initial response based on persona and scam type.
        
        Args:
            scam_type: Type of scam detected
            
        Returns:
            Initial response text
        """
        if not self.current_persona:
            self.select_persona()
        
        persona_id = self.current_persona['id']
        
        # Persona-specific initial responses
        responses = {
            'elderly_user': [
                "I received your message. I'm not very good with technology, can you help me understand what this is about?",
                "Hello? I'm a bit confused by your message. What do I need to do?",
                "I'm worried about this. My grandson usually helps me with these things, but he's not here right now."
            ],
            'eager_customer': [
                "Hi! I just saw your message. This sounds interesting!",
                "Wow, really? Tell me more about this!",
                "I'm excited! What do I need to do next?"
            ],
            'worried_parent': [
                "I just saw this message. Is everything okay? Should I be concerned?",
                "What's this about? Is there a problem?",
                "I'm worried now. Please tell me what's happening."
            ],
            'busy_professional': [
                "I saw your message. I'm in the middle of something, but what's this about?",
                "Quick question - what do you need from me?",
                "I have a few minutes. What's the issue?"
            ]
        }
        
        return random.choice(responses.get(persona_id, ["Hello, I received your message."]))
    
    def should_ask_for_details(self, turn_number: int) -> bool:
        """
        Determine if the persona should ask for account/payment details.
        
        Args:
            turn_number: Current conversation turn
            
        Returns:
            True if should ask for details
        """
        if not self.current_persona:
            return False
        
        vulnerability = self.current_persona.get('vulnerability_level', 'medium')
        
        # More vulnerable personas ask sooner
        if vulnerability == 'high' and turn_number >= 3:
            return random.random() < 0.6
        elif vulnerability == 'medium-high' and turn_number >= 4:
            return random.random() < 0.5
        elif vulnerability == 'medium' and turn_number >= 5:
            return random.random() < 0.4
        
        return False
    
    def generate_detail_request(self) -> str:
        """Generate a request for payment/account details."""
        requests = [
            "Where should I send the money?",
            "What account number do I need?",
            "Can you give me the details?",
            "What's your UPI ID?",
            "Should I click on that link you sent?",
            "What information do you need from me?"
        ]
        return random.choice(requests)


if __name__ == "__main__":
    # Test persona manager
    manager = PersonaManager()
    
    # Test each persona
    for persona_name in ['elderly_user', 'eager_customer', 'worried_parent', 'busy_professional']:
        print(f"\n=== Testing {persona_name} ===")
        manager.select_persona(persona_name)
        
        print(f"Initial: {manager.get_initial_response('banking_fraud')}")
        print(f"Turn 3: {manager.generate_response_style('Okay, I can do that.', 3)}")
        print(f"Should ask for details (turn 4): {manager.should_ask_for_details(4)}")
