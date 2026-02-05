# GUVI Hackathon - Agentic Honey-Pot API

## Quick Start Guide

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env and set your API key
# HONEYPOT_API_KEY=your-secret-api-key-here
```

### 3. Run the Server

```bash
# Start the GUVI-compliant API server
python guvi_api_server.py --port 8000 --api-key your-secret-api-key-here
```

The server will start on `http://localhost:8000`

### 4. Test the API

```bash
# In a new terminal, run the test suite
python test_guvi_api.py
```

## API Endpoints

### Main Honeypot Endpoint (GUVI Compliant)

**POST** `/api/honeypot`

**Headers:**
```
x-api-key: your-secret-api-key-here
Content-Type: application/json
```

**Request Format (First Message):**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Request Format (Follow-up Message):**
```json
{
  "sessionId": "same-session-id-as-before",
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid account suspension.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": 1770005528731
    },
    {
      "sender": "user",
      "text": "Why will my account be blocked?",
      "timestamp": 1770005528731
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response Format:**
```json
{
  "status": "success",
  "reply": "Why is my account being suspended?"
}
```

### Additional Endpoints (For Debugging)

**GET** `/health` - Health check

**GET** `/api/sessions` - List active sessions (requires API key)

**GET** `/api/session/<session_id>` - Get session details (requires API key)

**POST** `/api/session/<session_id>/end` - Manually end session and send final result (requires API key)

## How It Works

### 1. Scam Detection
When the first message arrives:
- The system analyzes the message for scam patterns
- If scam is detected with sufficient confidence, the AI agent is activated
- A persona is selected based on the scam type

### 2. Multi-Turn Conversation
For subsequent messages:
- The agent maintains conversation context using `sessionId`
- Responses are generated to keep the scammer engaged
- Intelligence is extracted from each scammer message

### 3. Intelligence Extraction
The system extracts:
- **Bank Accounts**: Account numbers and IFSC codes
- **UPI IDs**: Payment handles (e.g., scammer@paytm)
- **Phone Numbers**: Contact numbers in international format
- **Phishing Links**: Malicious URLs
- **Suspicious Keywords**: Urgency tactics, threats, etc.

### 4. Final Result Callback
When the conversation ends (after sufficient turns or intelligence extraction):
- The system sends a POST request to `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`
- Payload includes all extracted intelligence and conversation metadata

**Final Result Payload:**
```json
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": ["1234567890123 (State Bank of India)"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["http://malicious-link.example"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
  },
  "agentNotes": "Scam type: banking_fraud, Confidence: 95% | Conversation ended after 18 messages"
}
```

## Configuration

Edit `config/config.yaml` to customize:

- **Detection threshold**: Minimum confidence to engage
- **Max conversation turns**: Maximum number of exchanges
- **Response delays**: Simulate human typing (can use fast mode for testing)
- **Persona selection**: Auto-select or use default persona
- **Intelligence extraction**: Enable/disable specific extractors

## Testing

### Manual Testing with cURL

```bash
# Test health check
curl http://localhost:8000/health

# Test scam detection (first message)
curl -X POST http://localhost:8000/api/honeypot \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-123",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked. Verify at http://fake-bank.com",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Automated Testing

```bash
# Run the comprehensive test suite
python test_guvi_api.py
```

## Deployment

### Local Deployment
```bash
python guvi_api_server.py --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
# Build image
docker build -t guvi-honeypot .

# Run container
docker run -p 8000:8000 -e HONEYPOT_API_KEY=your-key guvi-honeypot
```

### Production Deployment
For production, consider:
- Using a production WSGI server (gunicorn, uwsgi)
- Setting up HTTPS with SSL certificates
- Using Redis or database for session storage
- Implementing rate limiting
- Setting up monitoring and logging

## Features

✅ **GUVI-Compliant API**: Exact request/response format as specified
✅ **API Key Authentication**: Secure access with `x-api-key` header
✅ **Session Management**: Multi-turn conversation tracking
✅ **Scam Detection**: Pattern-based detection with confidence scoring
✅ **AI Agent**: Human-like responses with multiple personas
✅ **Intelligence Extraction**: Bank accounts, UPI IDs, phone numbers, URLs
✅ **Final Result Callback**: Automatic reporting to GUVI endpoint
✅ **Error Handling**: Robust error handling and validation
✅ **Logging**: Comprehensive logging for debugging

## Troubleshooting

### API returns 401 Unauthorized
- Check that you're sending the `x-api-key` header
- Verify the API key matches the one set in the server

### Session not found
- Ensure you're using the same `sessionId` for all messages in a conversation
- Check that the session hasn't been automatically ended

### No response from agent
- Check server logs for errors
- Verify that the message was detected as a scam
- Ensure confidence threshold is met

### Final result not sent
- Check server logs for callback errors
- Verify network connectivity to GUVI endpoint
- Ensure session has sufficient intelligence extracted

## Support

For issues or questions, check:
- Server logs: `logs/honeypot.log`
- Test output: Run `python test_guvi_api.py` for diagnostics
- API documentation: This file

## License

MIT License - See LICENSE file for details
