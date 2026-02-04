# Quick Start Guide - API Testing

## 🚀 Fastest Way to Test

### 1. Install Dependencies (One-time)
```bash
cd scam_honeypot
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python api_server.py --debug
```

Server will start at: `http://localhost:5000`

---

## 🧪 Test the Endpoints

### Option 1: Using cURL (Command Line)

**Test 1: Health Check**
```bash
curl http://localhost:5000/health
```

**Test 2: Detect a Scam**
```bash
curl -X POST http://localhost:5000/api/v1/detect ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Your account has been blocked. Click here to verify immediately!\"}"
```

**Test 3: Full Engagement (Extract Intelligence)**
```bash
curl -X POST http://localhost:5000/api/v1/engage ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Congratulations! You won Rs 50,000. Pay Rs 500 processing fee to UPI: scammer@paytm\", \"persona\": \"eager_customer\"}"
```

**Test 4: List Available Personas**
```bash
curl http://localhost:5000/api/v1/personas
```

---

### Option 2: Using PowerShell (Windows)

**Detect Scam:**
```powershell
$body = @{
    message = "Your account has been blocked. Verify now!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/detect" -Method Post -Body $body -ContentType "application/json"
```

**Full Engagement:**
```powershell
$body = @{
    message = "You won Rs 50,000! Pay Rs 500 to claim. UPI: winner@paytm"
    persona = "elderly_user"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/engage" -Method Post -Body $body -ContentType "application/json"
```

---

### Option 3: Using Python Requests

Create `test_api.py`:
```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Test 1: Health Check
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# Test 2: Detect Scam
response = requests.post(
    f"{BASE_URL}/api/v1/detect",
    json={"message": "Your account is blocked. Verify immediately!"}
)
print("\nDetection:", json.dumps(response.json(), indent=2))

# Test 3: Engage with Scammer
response = requests.post(
    f"{BASE_URL}/api/v1/engage",
    json={
        "message": "You won Rs 1 lakh! Send Rs 1000 to UPI: scam@paytm",
        "persona": "eager_customer"
    }
)
print("\nEngagement:", json.dumps(response.json(), indent=2))
```

Run:
```bash
python test_api.py
```

---

### Option 4: Using Postman

1. **Import this collection:**

```json
{
  "info": {
    "name": "Scam Honeypot API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/health"
      }
    },
    {
      "name": "Detect Scam",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/v1/detect",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"message\": \"Your account has been blocked!\"}"
        }
      }
    },
    {
      "name": "Engage Scammer",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/v1/engage",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"message\": \"You won Rs 50,000!\", \"persona\": \"eager_customer\"}"
        }
      }
    }
  ]
}
```

2. Import in Postman: **Import → Raw Text → Paste JSON**

---

## 📊 Expected Responses

### Detect Endpoint Response:
```json
{
  "is_scam": true,
  "confidence": 85,
  "scam_type": "banking_fraud",
  "matched_patterns": ["account blocked", "verify"],
  "red_flags": ["click this link", "urgent action required"]
}
```

### Engage Endpoint Response:
```json
{
  "conversation_id": "abc-123-def",
  "scam_type": "prize_lottery",
  "confidence_score": 90,
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": [],
    "urls": []
  },
  "conversation_summary": {
    "total_messages": 8,
    "duration_seconds": 30,
    "persona_used": "eager_customer"
  }
}
```

---

## 🐛 Troubleshooting

**Error: "Module not found"**
```bash
pip install -r requirements.txt
```

**Error: "Port 5000 in use"**
```bash
python api_server.py --port 8080
```

**Error: "Connection refused"**
- Make sure the server is running
- Check firewall settings

---

## 📝 Next Steps

- See `DEPLOYMENT.md` for production deployment
- See `CODE_REVIEW.md` for known issues
- See `README.md` for full documentation
