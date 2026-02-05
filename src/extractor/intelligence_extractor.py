"""
Intelligence Extractor
Extracts structured intelligence from scam conversations.
"""

import re
import json
from typing import Dict, List, Optional
from datetime import datetime
import phonenumbers


class IntelligenceExtractor:
    """Extracts bank accounts, UPI IDs, phone numbers, URLs, and other intelligence."""
    
    def __init__(self):
        """Initialize extraction patterns."""
        # Indian bank account: 9-18 digits
        self.bank_account_pattern = r'\b\d{9,18}\b'
        
        # IFSC code: 4 letters + 0 + 6 alphanumeric
        self.ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
        
        # UPI ID: username@bank
        self.upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
        
        # URLs
        self.url_pattern = r'https?://[^\s]+'
        
        # Email
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Cryptocurrency addresses (basic patterns)
        self.btc_pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
        self.eth_pattern = r'\b0x[a-fA-F0-9]{40}\b'
        
        # Common Indian banks for IFSC lookup
        self.bank_codes = {
            'SBIN': 'State Bank of India',
            'HDFC': 'HDFC Bank',
            'ICIC': 'ICICI Bank',
            'AXIS': 'Axis Bank',
            'PUNB': 'Punjab National Bank',
            'BARB': 'Bank of Baroda',
            'CNRB': 'Canara Bank',
            'UBIN': 'Union Bank of India',
            'IDIB': 'Indian Bank',
            'IOBA': 'Indian Overseas Bank'
        }
    
    def extract_all(self, conversation: List[Dict]) -> Dict:
        """
        Extract all intelligence from a conversation.
        
        Args:
            conversation: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Dictionary with all extracted intelligence
        """
        # Combine all scammer messages
        scammer_messages = [
            msg['content'] for msg in conversation 
            if msg.get('role') == 'scammer'
        ]
        full_text = ' '.join(scammer_messages)
        
        intelligence = {
            'bank_accounts': self.extract_bank_accounts(full_text, conversation),
            'upi_ids': self.extract_upi_ids(full_text),
            'phone_numbers': self.extract_phone_numbers(full_text),
            'urls': self.extract_urls(full_text),
            'emails': self.extract_emails(full_text),
            'crypto_addresses': self.extract_crypto_addresses(full_text)
        }
        
        return intelligence
    
    def extract_bank_accounts(self, text: str, conversation: List[Dict] = None) -> List[Dict]:
        """Extract bank account numbers and associated IFSC codes."""
        accounts = []
        
        # Find account numbers
        account_numbers = re.findall(self.bank_account_pattern, text)
        
        # Find IFSC codes
        ifsc_codes = re.findall(self.ifsc_pattern, text, re.IGNORECASE)
        
        # Try to pair accounts with IFSC codes
        for i, account in enumerate(account_numbers):
            account_info = {
                'account_number': account,
                'ifsc_code': None,
                'bank_name': None,
                'extracted_at': f'message_{i+1}'
            }
            
            # Try to find corresponding IFSC
            if i < len(ifsc_codes):
                ifsc = ifsc_codes[i].upper()
                account_info['ifsc_code'] = ifsc
                
                # Identify bank from IFSC
                bank_code = ifsc[:4]
                account_info['bank_name'] = self.bank_codes.get(bank_code, 'Unknown Bank')
            
            accounts.append(account_info)
        
        # Also add standalone IFSC codes
        for ifsc in ifsc_codes[len(account_numbers):]:
            ifsc = ifsc.upper()
            bank_code = ifsc[:4]
            accounts.append({
                'account_number': None,
                'ifsc_code': ifsc,
                'bank_name': self.bank_codes.get(bank_code, 'Unknown Bank'),
                'extracted_at': 'standalone'
            })
        
        return accounts
    
    def extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs."""
        # Find all potential UPI IDs
        potential_upis = re.findall(self.upi_pattern, text)
        
        # Common email domains to exclude
        email_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'protonmail.com', 'icloud.com', 'aol.com', 'mail.com',
            'zoho.com', 'yandex.com', 'rediffmail.com'
        ]
        
        # Filter to likely UPI IDs (common UPI handles)
        upi_handles = [
            'paytm', 'phonepe', 'googlepay', 'gpay', 'amazonpay',
            'bhim', 'ybl', 'oksbi', 'okaxis', 'okicici', 'okhdfcbank',
            'ibl', 'axl', 'pnb', 'boi', 'cnrb', 'upi', 'fbl', 'sbi',
            'icici', 'hdfc', 'axis', 'kotak', 'federal', 'indus'
        ]
        
        upis = []
        for upi in potential_upis:
            upi_lower = upi.lower()
            
            # Exclude if it's a common email domain
            if any(domain in upi_lower for domain in email_domains):
                continue
            
            # Include if it has a known UPI handle
            if any(handle in upi_lower for handle in upi_handles):
                upis.append(upi)
        
        return list(set(upis))  # Remove duplicates
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers."""
        phones = []
        
        try:
            # Use phonenumbers library for robust extraction
            for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
                phone = phonenumbers.format_number(
                    match.number, 
                    phonenumbers.PhoneNumberFormat.E164
                )
                phones.append(phone)
        except:
            # Fallback to regex
            phone_pattern = r'(\+91|0)?[6-9]\d{9}'
            phones = re.findall(phone_pattern, text)
        
        return list(set(phones))
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs and phishing links."""
        urls = re.findall(self.url_pattern, text, re.IGNORECASE)
        return list(set(urls))
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses."""
        emails = re.findall(self.email_pattern, text)
        
        # Filter out UPI IDs that might match email pattern
        emails = [
            email for email in emails 
            if not any(handle in email.lower() for handle in ['paytm', 'phonepe', 'ybl'])
        ]
        
        return list(set(emails))
    
    def extract_crypto_addresses(self, text: str) -> Dict[str, List[str]]:
        """Extract cryptocurrency addresses."""
        crypto = {
            'bitcoin': list(set(re.findall(self.btc_pattern, text))),
            'ethereum': list(set(re.findall(self.eth_pattern, text)))
        }
        return crypto
    
    def generate_report(self, conversation_id: str, scam_type: str, 
                       confidence: int, conversation: List[Dict],
                       persona_used: str, duration_seconds: int) -> Dict:
        """
        Generate a complete intelligence report.
        
        Args:
            conversation_id: Unique conversation identifier
            scam_type: Type of scam detected
            confidence: Detection confidence score
            conversation: Full conversation history
            persona_used: Persona that was used
            duration_seconds: Conversation duration
            
        Returns:
            Complete JSON report
        """
        intelligence = self.extract_all(conversation)
        
        # Analyze scammer tactics
        tactics = self._analyze_tactics(conversation)
        
        report = {
            'conversation_id': conversation_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'scam_type': scam_type,
            'confidence_score': confidence,
            'extracted_intelligence': intelligence,
            'conversation_summary': {
                'total_messages': len(conversation),
                'duration_seconds': duration_seconds,
                'persona_used': persona_used,
                'key_tactics': tactics
            },
            'full_transcript': conversation
        }
        
        return report
    
    def _analyze_tactics(self, conversation: List[Dict]) -> List[str]:
        """Analyze scammer tactics used in conversation."""
        tactics = []
        
        scammer_text = ' '.join([
            msg['content'].lower() for msg in conversation 
            if msg.get('role') == 'scammer'
        ])
        
        # Check for common tactics
        if any(word in scammer_text for word in ['urgent', 'immediately', 'now', 'hurry']):
            tactics.append('urgency')
        
        if any(word in scammer_text for word in ['police', 'arrest', 'legal', 'court']):
            tactics.append('fear')
        
        if any(word in scammer_text for word in ['official', 'government', 'bank', 'department']):
            tactics.append('authority')
        
        if any(word in scammer_text for word in ['won', 'prize', 'lottery', 'reward']):
            tactics.append('greed')
        
        if any(word in scammer_text for word in ['verify', 'confirm', 'update', 'security']):
            tactics.append('social_engineering')
        
        return tactics


if __name__ == "__main__":
    # Test the extractor
    extractor = IntelligenceExtractor()
    
    test_conversation = [
        {
            'role': 'scammer',
            'content': 'Your account is blocked. Send money to 1234567890123 IFSC: SBIN0001234 or UPI: scammer@paytm'
        },
        {
            'role': 'agent',
            'content': 'Oh no! What should I do?'
        },
        {
            'role': 'scammer',
            'content': 'Call +919876543210 or visit http://fake-bank.com immediately!'
        }
    ]
    
    intelligence = extractor.extract_all(test_conversation)
    print(json.dumps(intelligence, indent=2))
