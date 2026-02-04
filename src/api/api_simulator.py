"""
API Simulator
Local simulator for testing without external Mock Scammer API.
"""

import random
import uuid
from typing import Dict, List, Optional


class APISimulator:
    """Simulates Mock Scammer API for local testing."""
    
    def __init__(self):
        """Initialize the simulator."""
        self.sessions = {}
        self.scam_templates = self._load_scam_templates()
    
    def _load_scam_templates(self) -> Dict:
        """Load scam message templates."""
        return {
            'banking_fraud': {
                'initial': [
                    "URGENT: Your bank account has been temporarily blocked due to suspicious activity. Click here to verify: http://fake-bank-verify.com",
                    "Dear customer, your account will be suspended in 24 hours. Update your KYC immediately by calling +919876543210",
                    "Alert! Unauthorized transaction detected. Confirm your identity by sending OTP to verify@scam.com"
                ],
                'followup': [
                    "Please provide your account number and IFSC code to verify your identity.",
                    "Send ₹500 to account 1234567890123 IFSC: SBIN0001234 for verification.",
                    "Click this link immediately: http://phishing-site.com/verify",
                    "What is your ATM PIN? We need it to unblock your account.",
                    "Send money to UPI ID: scammer@paytm to activate your account."
                ]
            },
            'prize_lottery': {
                'initial': [
                    "Congratulations! You have won ₹10,00,000 in the Mega Lottery Draw! Claim now!",
                    "You are the lucky winner of iPhone 15 Pro! Pay ₹999 processing fee to claim.",
                    "WINNER ALERT: You've been selected for a cash prize of ₹5 lakhs. Limited time offer!"
                ],
                'followup': [
                    "To claim your prize, send ₹2000 processing fee to account 9876543210987 IFSC: HDFC0001234",
                    "Pay tax of ₹5000 via UPI: winner@phonepe to receive your prize money.",
                    "Click here to claim: http://fake-lottery.com/claim?id=12345",
                    "Send your bank details to transfer the prize money.",
                    "Call +919123456789 immediately to verify your winning."
                ]
            },
            'tech_support': {
                'initial': [
                    "WARNING: 5 viruses detected on your computer! Call Microsoft Support at +919988776655 NOW!",
                    "Your antivirus subscription has expired. Renew immediately to protect your system: http://fake-antivirus.com",
                    "CRITICAL ALERT: Your system is infected with malware. Download security patch: http://malware-site.com"
                ],
                'followup': [
                    "Pay ₹3000 for virus removal. Send to UPI: techsupport@paytm",
                    "Provide remote access to your computer. Download TeamViewer from: http://fake-teamviewer.com",
                    "Your Windows license is invalid. Pay ₹5000 to account 5555666677778888 IFSC: ICIC0001234",
                    "Call our toll-free number +918877665544 for immediate assistance.",
                    "Click this link to fix your computer: http://scam-fix.com"
                ]
            },
            'impersonation': {
                'initial': [
                    "This is Income Tax Department. You have pending tax of ₹50,000. Pay immediately to avoid legal action.",
                    "Courier delivery pending. Pay customs clearance fee ₹1500 to receive your package.",
                    "Police Department: A complaint has been filed against you. Contact +919876543210 immediately."
                ],
                'followup': [
                    "Pay the fine of ₹10,000 to account 7777888899990000 IFSC: PUNB0001234 within 2 hours.",
                    "Send ₹2000 via UPI: govt@oksbi to clear customs.",
                    "Provide your Aadhaar and PAN details to close the case.",
                    "An arrest warrant will be issued if you don't pay ₹25,000 immediately.",
                    "Call this number +919123456789 to speak with the officer."
                ]
            },
            'investment_crypto': {
                'initial': [
                    "Guaranteed 300% returns in 30 days! Invest in our crypto trading bot. Limited slots available!",
                    "Double your money in 7 days with our AI trading system. Minimum investment ₹10,000.",
                    "Exclusive Bitcoin investment opportunity. Join now and earn ₹1 lakh per month!"
                ],
                'followup': [
                    "Send ₹20,000 to start earning. UPI: crypto@paytm",
                    "Deposit to our Bitcoin wallet: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                    "Transfer to account 3333444455556666 IFSC: AXIS0001234 to activate your account.",
                    "Pay registration fee ₹5000 to unlock premium trading features.",
                    "Click here to join: http://fake-crypto-invest.com/signup"
                ]
            },
            'upi_payment': {
                'initial': [
                    "Your UPI transaction of ₹5000 failed. Click here to get refund: http://fake-upi-refund.com",
                    "Paytm: You have received a payment request of ₹1. Accept to receive ₹10,000 cashback!",
                    "PhonePe: Your wallet needs verification. Send ₹1 to verify@phonepe to activate."
                ],
                'followup': [
                    "Accept this collect request to receive your refund.",
                    "Send ₹10 to UPI: refund@paytm to process your cashback.",
                    "Your UPI PIN is required for verification. Please share it.",
                    "Click this link to claim: http://fake-payment-link.com",
                    "Transfer ₹100 to account 2222333344445555 IFSC: BARB0001234 for wallet activation."
                ]
            }
        }
    
    def start_conversation(self, scam_type: str = None) -> Dict:
        """
        Start a simulated conversation.
        
        Args:
            scam_type: Type of scam to simulate
            
        Returns:
            Session data with initial message
        """
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Select scam type
        if not scam_type or scam_type not in self.scam_templates:
            scam_type = random.choice(list(self.scam_templates.keys()))
        
        # Get initial message
        initial_message = random.choice(self.scam_templates[scam_type]['initial'])
        
        # Create session
        self.sessions[session_id] = {
            'session_id': session_id,
            'scam_type': scam_type,
            'messages': [
                {
                    'role': 'scammer',
                    'content': initial_message
                }
            ],
            'turn_count': 0
        }
        
        return {
            'session_id': session_id,
            'initial_message': initial_message,
            'scam_type': scam_type
        }
    
    def send_message(self, session_id: str, message: str) -> Dict:
        """
        Send a message (victim's response).
        
        Args:
            session_id: Session identifier
            message: Message content
            
        Returns:
            Confirmation
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session['messages'].append({
            'role': 'victim',
            'content': message
        })
        
        return {'status': 'success', 'message_id': len(session['messages'])}
    
    def get_scammer_response(self, session_id: str) -> Optional[str]:
        """
        Generate scammer's response.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Scammer's message
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        scam_type = session['scam_type']
        session['turn_count'] += 1
        
        # Generate response based on turn count
        if session['turn_count'] > 10:
            # End conversation after too many turns
            return None
        
        # Get followup message
        response = random.choice(self.scam_templates[scam_type]['followup'])
        
        # Add to conversation
        session['messages'].append({
            'role': 'scammer',
            'content': response
        })
        
        return response
    
    def end_conversation(self, session_id: str) -> Dict:
        """
        End a conversation session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation summary
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        summary = {
            'session_id': session_id,
            'scam_type': session['scam_type'],
            'total_messages': len(session['messages']),
            'status': 'completed'
        }
        
        # Clean up session
        del self.sessions[session_id]
        
        return summary
    
    def get_conversation_history(self, session_id: str) -> Dict:
        """
        Get conversation history.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Full conversation data
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        return self.sessions[session_id]


if __name__ == "__main__":
    # Test simulator
    simulator = APISimulator()
    
    # Start conversation
    result = simulator.start_conversation(scam_type='banking_fraud')
    print(f"Session: {result['session_id']}")
    print(f"Scammer: {result['initial_message']}\n")
    
    # Simulate conversation
    session_id = result['session_id']
    
    for i in range(3):
        # Victim responds
        victim_msg = f"Response {i+1}: What should I do?"
        simulator.send_message(session_id, victim_msg)
        print(f"Victim: {victim_msg}")
        
        # Get scammer response
        scammer_msg = simulator.get_scammer_response(session_id)
        print(f"Scammer: {scammer_msg}\n")
    
    # End conversation
    summary = simulator.end_conversation(session_id)
    print(f"Conversation ended: {summary}")
