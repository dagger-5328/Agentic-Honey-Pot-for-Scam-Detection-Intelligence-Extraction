"""
Scam Detection Engine
Analyzes incoming messages to identify scam patterns with confidence scoring.
"""

import re
import json
from typing import Dict, List, Tuple
from pathlib import Path


class ScamDetector:
    """Detects scam messages using pattern matching and heuristics."""
    
    def __init__(self, patterns_file: str = None):
        """Initialize the scam detector with pattern database."""
        if patterns_file is None:
            patterns_file = Path(__file__).parent.parent.parent / "data" / "scam_patterns.json"
        
        with open(patterns_file, 'r', encoding='utf-8') as f:
            self.patterns = json.load(f)
        
        self.scam_types = self.patterns['scam_types']
        self.red_flags = self.patterns['common_red_flags']
        self.legitimate_indicators = self.patterns['legitimate_indicators']
    
    def detect(self, message: str) -> Dict:
        """
        Analyze a message and detect if it's a scam.
        
        Args:
            message: The message text to analyze
            
        Returns:
            Dictionary with detection results including:
            - is_scam: Boolean indicating if message is likely a scam
            - confidence: Confidence score (0-100)
            - scam_type: Type of scam detected (if any)
            - matched_patterns: List of matched patterns
            - red_flags: List of red flags found
        """
        message_lower = message.lower()
        
        # Check for legitimate indicators (reduces scam probability)
        legitimate_score = sum(
            1 for indicator in self.legitimate_indicators 
            if indicator.lower() in message_lower
        )
        
        # Score each scam type
        scam_scores = {}
        matched_patterns = {}
        
        for scam_type, patterns in self.scam_types.items():
            score = 0
            matches = []
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword.lower() in message_lower:
                    score += 1
                    matches.append(keyword)
            
            # Check urgency indicators (weighted higher)
            if 'urgency_indicators' in patterns:
                for indicator in patterns['urgency_indicators']:
                    if indicator.lower() in message_lower:
                        score += 1.5
                        matches.append(f"urgency: {indicator}")
            
            # Check authority claims for impersonation
            if 'authority_claims' in patterns:
                for claim in patterns['authority_claims']:
                    if claim.lower() in message_lower:
                        score += 1.2
                        matches.append(f"authority: {claim}")
            
            if score > 0:
                # Apply confidence weight
                weighted_score = score * patterns['confidence_weight']
                scam_scores[scam_type] = weighted_score
                matched_patterns[scam_type] = matches
        
        # Check common red flags
        red_flags_found = [
            flag for flag in self.red_flags 
            if flag.lower() in message_lower
        ]
        
        # Calculate overall confidence
        if not scam_scores:
            return {
                'is_scam': False,
                'confidence': 0,
                'scam_type': None,
                'matched_patterns': [],
                'red_flags': red_flags_found
            }
        
        # Get the highest scoring scam type
        top_scam_type = max(scam_scores.items(), key=lambda x: x[1])
        scam_type_name, raw_score = top_scam_type
        
        # Normalize confidence to 0-100 scale
        # Base confidence on pattern matches + red flags - legitimate indicators
        confidence = min(100, int(
            (raw_score * 15) +  # Pattern matches
            (len(red_flags_found) * 10) -  # Red flags boost
            (legitimate_score * 20)  # Legitimate indicators reduce
        ))
        
        # Additional heuristics
        confidence += self._check_url_patterns(message) * 10
        confidence += self._check_phone_patterns(message) * 8
        confidence += self._check_urgency_language(message) * 5
        
        confidence = max(0, min(100, confidence))  # Clamp to 0-100
        
        return {
            'is_scam': confidence >= 50,
            'confidence': confidence,
            'scam_type': scam_type_name if confidence >= 50 else None,
            'matched_patterns': matched_patterns.get(scam_type_name, []),
            'red_flags': red_flags_found,
            'details': {
                'all_scam_scores': scam_scores,
                'legitimate_indicators_found': legitimate_score
            }
        }
    
    def _check_url_patterns(self, message: str) -> int:
        """Check for suspicious URL patterns."""
        # Look for URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message, re.IGNORECASE)
        
        if not urls:
            return 0
        
        suspicious_score = 0
        for url in urls:
            # Check for suspicious TLDs or patterns
            if any(tld in url.lower() for tld in ['.tk', '.ml', '.ga', '.cf', '.gq']):
                suspicious_score += 2
            # Check for URL shorteners
            if any(short in url.lower() for short in ['bit.ly', 'tinyurl', 'goo.gl']):
                suspicious_score += 1
            # Check for IP addresses instead of domains
            if re.search(r'\d+\.\d+\.\d+\.\d+', url):
                suspicious_score += 2
        
        return min(suspicious_score, 3)
    
    def _check_phone_patterns(self, message: str) -> int:
        """Check for phone numbers (common in scams)."""
        # Indian phone number patterns
        phone_pattern = r'(\+91|0)?[6-9]\d{9}'
        phones = re.findall(phone_pattern, message)
        return min(len(phones), 2)
    
    def _check_urgency_language(self, message: str) -> int:
        """Check for urgent/pressuring language."""
        urgency_words = [
            'urgent', 'immediately', 'now', 'hurry', 'quick',
            'expire', 'last chance', 'limited time', 'act fast'
        ]
        message_lower = message.lower()
        urgency_count = sum(1 for word in urgency_words if word in message_lower)
        return min(urgency_count, 3)


if __name__ == "__main__":
    # Test the detector
    detector = ScamDetector()
    
    test_messages = [
        "Your account has been blocked. Click here to verify: http://fake-bank.com. Send OTP immediately!",
        "Congratulations! You won ₹50,000 in lottery. Pay ₹500 processing fee to claim.",
        "Hi, this is a reminder about your meeting tomorrow at 3 PM.",
    ]
    
    for msg in test_messages:
        result = detector.detect(msg)
        print(f"\nMessage: {msg[:50]}...")
        print(f"Is Scam: {result['is_scam']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Type: {result['scam_type']}")
