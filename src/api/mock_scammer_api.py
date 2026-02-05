"""
Mock Scammer API Client
Integrates with Mock Scammer API for simulated scam interactions.
"""

import requests
import time
from typing import Dict, Optional
from collections import deque
from datetime import datetime, timedelta
import logging


class MockScammerAPI:
    """Client for interacting with Mock Scammer API."""
    
    def __init__(self, base_url: str, api_key: str = None, timeout: int = 30,
                 rate_limit_enabled: bool = True, requests_per_minute: int = 10,
                 backoff_factor: float = 2.0):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the Mock Scammer API
            api_key: API authentication key
            timeout: Request timeout in seconds
            rate_limit_enabled: Enable rate limiting
            requests_per_minute: Maximum requests per minute
            backoff_factor: Exponential backoff multiplier
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session_id = None
        
        # Rate limiting
        self.rate_limit_enabled = rate_limit_enabled
        self.requests_per_minute = requests_per_minute
        self.backoff_factor = backoff_factor
        self.request_times = deque(maxlen=requests_per_minute)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Setup session
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits."""
        if not self.rate_limit_enabled:
            return
        
        now = datetime.now()
        
        # Remove old request times (older than 1 minute)
        while self.request_times and (now - self.request_times[0]) > timedelta(minutes=1):
            self.request_times.popleft()
        
        # If at limit, wait until oldest request is > 1 minute old
        if len(self.request_times) >= self.requests_per_minute:
            oldest = self.request_times[0]
            wait_until = oldest + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            
            if wait_seconds > 0:
                self.logger.info(f"Rate limit reached. Waiting {wait_seconds:.1f}s")
                time.sleep(wait_seconds)
        
        # Record this request
        self.request_times.append(now)
    
    def _make_request_with_retry(self, method: str, url: str, max_retries: int = 3, **kwargs):
        """Make HTTP request with exponential backoff on failures."""
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                
                if method.lower() == 'get':
                    response = self.session.get(url, **kwargs)
                else:
                    response = self.session.post(url, **kwargs)
                
                # Handle rate limiting from server
                if response.status_code == 429:
                    wait_time = self.backoff_factor ** attempt
                    self.logger.warning(f"Rate limited by server. Waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = self.backoff_factor ** attempt
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s")
                time.sleep(wait_time)
        
        raise requests.exceptions.RequestException("Max retries exceeded")
    
    def start_conversation(self, scam_type: str = None) -> Dict:
        """
        Start a new conversation with the mock scammer.
        
        Args:
            scam_type: Optional specific scam type to simulate
            
        Returns:
            Dictionary with session_id and initial scam message
        """
        endpoint = f"{self.base_url}/api/v1/conversations/start"
        
        payload = {}
        if scam_type:
            payload['scam_type'] = scam_type
        
        try:
            response = self._make_request_with_retry(
                'post',
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            data = response.json()
            self.session_id = data.get('session_id')
            
            self.logger.info(f"Started conversation: {self.session_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to start conversation: {e}")
            raise
    
    def send_message(self, message: str) -> Dict:
        """
        Send a message to the scammer.
        
        Args:
            message: The message to send
            
        Returns:
            API response
        """
        if not self.session_id:
            raise ValueError("No active session. Call start_conversation first.")
        
        endpoint = f"{self.base_url}/api/v1/conversations/{self.session_id}/messages"
        
        payload = {
            'message': message,
            'role': 'victim'
        }
        
        try:
            response = self._make_request_with_retry(
                'post',
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
    
    def get_scammer_response(self, wait_time: int = 5) -> Optional[str]:
        """
        Get the scammer's response.
        
        Args:
            wait_time: Time to wait for response in seconds
            
        Returns:
            Scammer's message or None if no response
        """
        if not self.session_id:
            raise ValueError("No active session. Call start_conversation first.")
        
        endpoint = f"{self.base_url}/api/v1/conversations/{self.session_id}/messages/latest"
        
        # Wait for scammer to respond
        time.sleep(wait_time)
        
        try:
            response = self._make_request_with_retry(
                'get',
                endpoint,
                timeout=self.timeout
            )
            
            data = response.json()
            return data.get('message')
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get response: {e}")
            return None
    
    def end_conversation(self) -> Dict:
        """
        End the current conversation.
        
        Returns:
            Conversation summary
        """
        if not self.session_id:
            raise ValueError("No active session.")
        
        endpoint = f"{self.base_url}/api/v1/conversations/{self.session_id}/end"
        
        try:
            response = self.session.post(
                endpoint,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Ended conversation: {self.session_id}")
            self.session_id = None
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to end conversation: {e}")
            raise
    
    def get_conversation_history(self) -> Dict:
        """
        Get the full conversation history.
        
        Returns:
            Complete conversation transcript
        """
        if not self.session_id:
            raise ValueError("No active session.")
        
        endpoint = f"{self.base_url}/api/v1/conversations/{self.session_id}"
        
        try:
            response = self.session.get(
                endpoint,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            raise


if __name__ == "__main__":
    # Test API client (will fail without actual API)
    logging.basicConfig(level=logging.INFO)
    
    try:
        api = MockScammerAPI(
            base_url="https://api.mockscammer.example.com",
            api_key="test_key_123"
        )
        
        # Start conversation
        result = api.start_conversation(scam_type="banking_fraud")
        print(f"Session ID: {result['session_id']}")
        print(f"Initial message: {result['initial_message']}")
        
        # Send response
        api.send_message("What do you mean my account is blocked?")
        
        # Get scammer response
        response = api.get_scammer_response()
        print(f"Scammer: {response}")
        
        # End conversation
        summary = api.end_conversation()
        print(f"Conversation ended: {summary}")
        
    except Exception as e:
        print(f"Error: {e}")
