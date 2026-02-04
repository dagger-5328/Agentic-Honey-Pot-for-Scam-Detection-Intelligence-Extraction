"""
Test Intelligence Extractor
"""

import pytest
from src.extractor.intelligence_extractor import IntelligenceExtractor


class TestIntelligenceExtractor:
    """Test cases for intelligence extraction."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = IntelligenceExtractor()
    
    def test_bank_account_extraction(self):
        """Test extraction of bank account numbers."""
        text = "Send money to account 1234567890123 IFSC: SBIN0001234"
        accounts = self.extractor.extract_bank_accounts(text)
        
        assert len(accounts) > 0
        assert accounts[0]['account_number'] == '1234567890123'
        assert accounts[0]['ifsc_code'] == 'SBIN0001234'
        assert 'State Bank' in accounts[0]['bank_name']
    
    def test_upi_extraction(self):
        """Test extraction of UPI IDs."""
        text = "Send to UPI: scammer@paytm or fraud@phonepe"
        upis = self.extractor.extract_upi_ids(text)
        
        assert len(upis) >= 1
        assert any('paytm' in upi.lower() for upi in upis)
    
    def test_phone_extraction(self):
        """Test extraction of phone numbers."""
        text = "Call +919876543210 immediately"
        phones = self.extractor.extract_phone_numbers(text)
        
        assert len(phones) > 0
        assert any('9876543210' in phone for phone in phones)
    
    def test_url_extraction(self):
        """Test extraction of URLs."""
        text = "Click here: http://fake-bank.com and https://phishing-site.com"
        urls = self.extractor.extract_urls(text)
        
        assert len(urls) == 2
        assert 'http://fake-bank.com' in urls
    
    def test_full_conversation_extraction(self):
        """Test extraction from full conversation."""
        conversation = [
            {
                'role': 'scammer',
                'content': 'Send to 1234567890 IFSC: HDFC0001234 or UPI: scam@paytm'
            },
            {
                'role': 'agent',
                'content': 'Okay, what is the account?'
            },
            {
                'role': 'scammer',
                'content': 'Call +919876543210 or visit http://fake-site.com'
            }
        ]
        
        intelligence = self.extractor.extract_all(conversation)
        
        assert len(intelligence['bank_accounts']) > 0
        assert len(intelligence['upi_ids']) > 0
        assert len(intelligence['phone_numbers']) > 0
        assert len(intelligence['urls']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
