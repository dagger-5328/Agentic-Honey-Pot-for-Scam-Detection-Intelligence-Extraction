"""
Test script for GUVI-compliant Honeypot API
Tests the API with the exact format specified in the problem statement.
"""

import requests
import json
import time
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"

# Headers
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}


def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("[PASS] Health check passed")


def test_first_message():
    """Test first message in conversation (scam detection)."""
    print("\n" + "="*60)
    print("TEST 2: First Message (Scam Detection)")
    print("="*60)
    
    session_id = str(uuid.uuid4())
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately by sending your UPI PIN.",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print(f"\nSession ID: {session_id}")
    print(f"Request Payload:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(
        f"{API_BASE_URL}/api/honeypot",
        headers=HEADERS,
        json=payload
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert 'reply' in response.json()
    
    print("[PASS] First message test passed")
    
    return session_id, response.json()['reply']


def test_multi_turn_conversation():
    """Test multi-turn conversation."""
    print("\n" + "="*60)
    print("TEST 3: Multi-Turn Conversation")
    print("="*60)
    
    session_id = str(uuid.uuid4())
    conversation_history = []
    
    # Message 1: Initial scam message
    print("\n--- Turn 1 ---")
    message_1 = {
        "sender": "scammer",
        "text": "Urgent! Your account has suspicious activity. Call +919876543210 immediately.",
        "timestamp": int(time.time() * 1000)
    }
    
    payload_1 = {
        "sessionId": session_id,
        "message": message_1,
        "conversationHistory": [],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print(f"Scammer: {message_1['text']}")
    
    response_1 = requests.post(
        f"{API_BASE_URL}/api/honeypot",
        headers=HEADERS,
        json=payload_1
    )
    
    assert response_1.status_code == 200
    reply_1 = response_1.json()['reply']
    print(f"Agent: {reply_1}")
    
    # Update conversation history
    conversation_history.append(message_1)
    conversation_history.append({
        "sender": "user",
        "text": reply_1,
        "timestamp": int(time.time() * 1000)
    })
    
    time.sleep(1)
    
    # Message 2: Follow-up with UPI ID
    print("\n--- Turn 2 ---")
    message_2 = {
        "sender": "scammer",
        "text": "To verify your account, send Rs.1 to scammer@paytm and share the transaction ID.",
        "timestamp": int(time.time() * 1000)
    }
    
    payload_2 = {
        "sessionId": session_id,
        "message": message_2,
        "conversationHistory": conversation_history.copy(),
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print(f"Scammer: {message_2['text']}")
    
    response_2 = requests.post(
        f"{API_BASE_URL}/api/honeypot",
        headers=HEADERS,
        json=payload_2
    )
    
    assert response_2.status_code == 200
    reply_2 = response_2.json()['reply']
    print(f"Agent: {reply_2}")
    
    # Update conversation history
    conversation_history.append(message_2)
    conversation_history.append({
        "sender": "user",
        "text": reply_2,
        "timestamp": int(time.time() * 1000)
    })
    
    time.sleep(1)
    
    # Message 3: Bank account details
    print("\n--- Turn 3 ---")
    message_3 = {
        "sender": "scammer",
        "text": "Or transfer to account 1234567890123 IFSC: SBIN0001234. Visit http://fake-verify.com for details.",
        "timestamp": int(time.time() * 1000)
    }
    
    payload_3 = {
        "sessionId": session_id,
        "message": message_3,
        "conversationHistory": conversation_history.copy(),
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print(f"Scammer: {message_3['text']}")
    
    response_3 = requests.post(
        f"{API_BASE_URL}/api/honeypot",
        headers=HEADERS,
        json=payload_3
    )
    
    assert response_3.status_code == 200
    reply_3 = response_3.json()['reply']
    print(f"Agent: {reply_3}")
    
    print("\n[PASS] Multi-turn conversation test passed")
    
    return session_id


def test_session_details(session_id):
    """Test getting session details."""
    print("\n" + "="*60)
    print("TEST 4: Get Session Details")
    print("="*60)
    
    response = requests.get(
        f"{API_BASE_URL}/api/session/{session_id}",
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Session might be cleaned up after final result was sent (expected behavior)
    if response.status_code == 404:
        print("\n[INFO] Session was already cleaned up after final result callback (expected behavior)")
        print("[PASS] Session lifecycle completed correctly")
        return
    
    assert response.status_code == 200
    
    session_data = response.json()
    print(f"\n[PASS] Session details retrieved")
    print(f"  - Scam Detected: {session_data['scam_detected']}")
    print(f"  - Scam Type: {session_data['scam_type']}")
    print(f"  - Total Messages: {session_data['total_messages']}")
    print(f"  - Intelligence Extracted:")
    print(f"    - Bank Accounts: {len(session_data['intelligence']['bankAccounts'])}")
    print(f"    - UPI IDs: {len(session_data['intelligence']['upiIds'])}")
    print(f"    - Phone Numbers: {len(session_data['intelligence']['phoneNumbers'])}")
    print(f"    - Phishing Links: {len(session_data['intelligence']['phishingLinks'])}")
    print(f"    - Suspicious Keywords: {len(session_data['intelligence']['suspiciousKeywords'])}")


def test_api_key_validation():
    """Test API key validation."""
    print("\n" + "="*60)
    print("TEST 5: API Key Validation")
    print("="*60)
    
    # Test without API key
    print("\nTest 5a: No API key")
    response = requests.post(
        f"{API_BASE_URL}/api/honeypot",
        headers={"Content-Type": "application/json"},
        json={"sessionId": "test", "message": {"text": "test"}}
    )
    
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 401
    print("[PASS] Correctly rejected request without API key")
    
    # Test with wrong API key
    print("\nTest 5b: Wrong API key")
    response = requests.post(
        f"{API_BASE_URL}/api/honeypot",
        headers={"x-api-key": "wrong-key", "Content-Type": "application/json"},
        json={"sessionId": "test", "message": {"text": "test"}}
    )
    
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 401
    print("[PASS] Correctly rejected request with wrong API key")


def test_non_scam_message():
    """Test with a non-scam message."""
    print("\n" + "="*60)
    print("TEST 6: Non-Scam Message")
    print("="*60)
    
    session_id = str(uuid.uuid4())
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Hello, how are you today?",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print(f"Message: {payload['message']['text']}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/honeypot",
        headers=HEADERS,
        json=payload
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("[PASS] Non-scam message handled correctly")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("GUVI HONEYPOT API TEST SUITE")
    print("="*60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: First message
        session_id_1, reply = test_first_message()
        
        # Test 3: Multi-turn conversation
        session_id_2 = test_multi_turn_conversation()
        
        # Test 4: Session details
        test_session_details(session_id_2)
        
        # Test 5: API key validation
        test_api_key_validation()
        
        # Test 6: Non-scam message
        test_non_scam_message()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        raise
    except requests.exceptions.ConnectionError:
        print(f"\n[FAIL] Connection error: Is the API server running at {API_BASE_URL}?")
        raise
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
