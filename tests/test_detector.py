"""
Test Scam Detector
"""

import pytest
from src.detector.scam_detector import ScamDetector


class TestScamDetector:
    """Test cases for scam detection."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.detector = ScamDetector()
    
    def test_banking_fraud_detection(self):
        """Test detection of banking fraud scams."""
        message = "Your account has been blocked. Click here to verify immediately!"
        result = self.detector.detect(message)
        
        assert result['is_scam'] is True
        assert result['confidence'] > 50
        assert result['scam_type'] == 'banking_fraud'
    
    def test_prize_lottery_detection(self):
        """Test detection of prize/lottery scams."""
        message = "Congratulations! You won ₹50,000. Pay ₹500 processing fee to claim."
        result = self.detector.detect(message)
        
        assert result['is_scam'] is True
        assert result['scam_type'] == 'prize_lottery'
    
    def test_legitimate_message(self):
        """Test that legitimate messages are not flagged."""
        message = "Hi, this is a reminder about your meeting tomorrow at 3 PM."
        result = self.detector.detect(message)
        
        assert result['is_scam'] is False
        assert result['confidence'] < 50
    
    def test_urgency_detection(self):
        """Test detection of urgency tactics."""
        message = "URGENT! Act immediately or your account will be closed!"
        result = self.detector.detect(message)
        
        assert result['is_scam'] is True
        assert result['confidence'] > 60
    
    def test_url_in_message(self):
        """Test that URLs increase scam score."""
        message = "Click here: http://fake-bank.com to verify your account"
        result = self.detector.detect(message)
        
        assert result['is_scam'] is True
        assert len(result['red_flags']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
