"""
Simple API Test Script
Run this to test all API endpoints quickly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health check endpoint."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_detect():
    """Test scam detection endpoint."""
    print_section("2. Detect Scam")
    
    test_messages = [
        "Your account has been blocked. Click here to verify immediately!",
        "Congratulations! You won ₹50,000 in lottery. Pay ₹500 to claim.",
        "Hi, this is a normal message about our meeting tomorrow."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message[:50]}...")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/detect",
                json={"message": message},
                timeout=10
            )
            result = response.json()
            print(f"  Is Scam: {result.get('is_scam')}")
            print(f"  Confidence: {result.get('confidence')}%")
            print(f"  Type: {result.get('scam_type')}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_engage():
    """Test engagement endpoint."""
    print_section("3. Engage with Scammer")
    
    message = "Your account is blocked. Send ₹500 to UPI: scammer@paytm to unblock."
    
    print(f"Message: {message}")
    print("\nEngaging... (this may take 30-60 seconds)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/engage",
            json={
                "message": message,
                "persona": "elderly_user"
            },
            timeout=120  # Longer timeout for full conversation
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Conversation completed!")
            print(f"  Conversation ID: {result.get('conversation_id')}")
            print(f"  Scam Type: {result.get('scam_type')}")
            print(f"  Confidence: {result.get('confidence_score')}%")
            
            intel = result.get('extracted_intelligence', {})
            print(f"\n  Extracted Intelligence:")
            print(f"    - Bank Accounts: {len(intel.get('bank_accounts', []))}")
            print(f"    - UPI IDs: {intel.get('upi_ids', [])}")
            print(f"    - Phone Numbers: {intel.get('phone_numbers', [])}")
            print(f"    - URLs: {intel.get('urls', [])}")
            
            summary = result.get('conversation_summary', {})
            print(f"\n  Conversation Summary:")
            print(f"    - Messages: {summary.get('total_messages')}")
            print(f"    - Duration: {summary.get('duration_seconds')}s")
            print(f"    - Persona: {summary.get('persona_used')}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            
    except requests.Timeout:
        print("❌ Request timed out (conversation took too long)")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_extract():
    """Test intelligence extraction endpoint."""
    print_section("4. Extract Intelligence")
    
    conversation = [
        {
            "role": "scammer",
            "content": "Send money to account 1234567890123 IFSC: SBIN0001234"
        },
        {
            "role": "agent",
            "content": "What is your UPI ID?"
        },
        {
            "role": "scammer",
            "content": "Use UPI: scammer@paytm or call +919876543210"
        }
    ]
    
    print("Extracting from sample conversation...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/extract",
            json={"conversation": conversation},
            timeout=10
        )
        result = response.json()
        print("\nExtracted Intelligence:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")

def test_personas():
    """Test personas endpoint."""
    print_section("5. List Personas")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/personas", timeout=5)
        result = response.json()
        
        print(f"\nAvailable Personas: {len(result.get('personas', []))}")
        for persona in result.get('personas', []):
            print(f"\n  - {persona.get('id')}")
            print(f"    Name: {persona.get('name')}")
            print(f"    Age: {persona.get('age')}")
            print(f"    Vulnerability: {persona.get('vulnerability_level')}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_scam_types():
    """Test scam types endpoint."""
    print_section("6. List Scam Types")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scam-types", timeout=5)
        result = response.json()
        
        print(f"\nSupported Scam Types: {len(result.get('scam_types', []))}")
        for scam in result.get('scam_types', []):
            print(f"\n  - {scam.get('id')}")
            print(f"    Keywords: {len(scam.get('keywords', []))} patterns")
            print(f"    Weight: {scam.get('confidence_weight')}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests."""
    print("\n🧪 Scam Honeypot API Test Suite")
    print(f"Testing API at: {BASE_URL}")
    
    # Test health first
    if not test_health():
        print("\n❌ API is not running!")
        print("Start the server with: python api_server.py --debug")
        return
    
    # Run all tests
    test_detect()
    test_extract()
    test_personas()
    test_scam_types()
    
    # Ask before running engagement test (takes longer)
    print("\n" + "="*60)
    response = input("\nRun full engagement test? (takes ~60 seconds) [y/N]: ")
    if response.lower() == 'y':
        test_engage()
    
    print("\n" + "="*60)
    print("✅ Test suite completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
