# 🚀 Deployment Guide - Scam Honeypot API

This guide covers deploying the Scam Honeypot system as a REST API for testing and production use.

---

## 📋 Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [API Endpoints](#api-endpoints)
3. [Testing with cURL](#testing-with-curl)
4. [Testing with Postman](#testing-with-postman)
5. [Production Deployment](#production-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Cloud Deployment](#cloud-deployment)

---

## 🔧 Local Development Setup

### Step 1: Install Dependencies

```bash
cd scam_honeypot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Start the API Server

```bash
# Development mode (with auto-reload)
python api_server.py --debug

# Production mode
python api_server.py --host 0.0.0.0 --port 5000

# Custom port
python api_server.py --port 8080
```

The server will start at `http://localhost:5000`

---

## 📡 API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "scam-honeypot-api",
  "version": "1.0.0"
}
```

---

### 2. Detect Scam
**POST** `/api/v1/detect`

Analyze a message to detect if it's a scam.

**Request Body:**
```json
{
  "message": "Your account has been blocked. Click here to verify immediately!"
}
```

**Response:**
```json
{
  "is_scam": true,
  "confidence": 85,
  "scam_type": "banking_fraud",
  "matched_patterns": ["account blocked", "verify", "immediately"],
  "red_flags": ["click this link", "urgent action required"]
}
```

---

### 3. Engage with Scammer
**POST** `/api/v1/engage`

Engage with a scammer and extract intelligence.

**Request Body:**
```json
{
  "message": "Congratulations! You won ₹50,000. Pay ₹500 to claim.",
  "persona": "eager_customer"
}
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-04T10:18:06Z",
  "scam_type": "prize_lottery",
  "confidence_score": 90,
  "extracted_intelligence": {
    "bank_accounts": [
      {
        "account_number": "1234567890123",
        "ifsc_code": "SBIN0001234",
        "bank_name": "State Bank of India"
      }
    ],
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": ["+919876543210"],
    "urls": ["http://fake-lottery.com"],
    "emails": []
  },
  "conversation_summary": {
    "total_messages": 12,
    "duration_seconds": 45,
    "persona_used": "eager_customer",
    "key_tactics": ["greed", "urgency"]
  }
}
```

---

### 4. Extract Intelligence
**POST** `/api/v1/extract`

Extract intelligence from a conversation transcript.

**Request Body:**
```json
{
  "conversation": [
    {
      "role": "scammer",
      "content": "Send money to account 1234567890 IFSC: HDFC0001234"
    },
    {
      "role": "agent",
      "content": "Okay, what is the UPI?"
    },
    {
      "role": "scammer",
      "content": "Use UPI: scammer@paytm or call +919876543210"
    }
  ]
}
```

**Response:**
```json
{
  "bank_accounts": [
    {
      "account_number": "1234567890",
      "ifsc_code": "HDFC0001234",
      "bank_name": "HDFC Bank"
    }
  ],
  "upi_ids": ["scammer@paytm"],
  "phone_numbers": ["+919876543210"],
  "urls": [],
  "emails": []
}
```

---

### 5. List Personas
**GET** `/api/v1/personas`

Get all available victim personas.

**Response:**
```json
{
  "personas": [
    {
      "id": "elderly_user",
      "name": "Ramesh Kumar",
      "age": 68,
      "characteristics": ["tech-naive", "trusting"],
      "vulnerability_level": "high"
    }
  ]
}
```

---

### 6. List Scam Types
**GET** `/api/v1/scam-types`

Get all supported scam types.

**Response:**
```json
{
  "scam_types": [
    {
      "id": "banking_fraud",
      "keywords": ["account blocked", "verify account"],
      "confidence_weight": 0.9
    }
  ]
}
```

---

## 🧪 Testing with cURL

### Health Check
```bash
curl http://localhost:5000/health
```

### Detect Scam
```bash
curl -X POST http://localhost:5000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Your account has been blocked. Verify now!\"}"
```

### Engage with Scammer
```bash
curl -X POST http://localhost:5000/api/v1/engage \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"You won ₹50,000! Pay ₹500 to claim.\", \"persona\": \"eager_customer\"}"
```

### Extract Intelligence
```bash
curl -X POST http://localhost:5000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d "{\"conversation\": [{\"role\": \"scammer\", \"content\": \"Send to UPI: scam@paytm\"}]}"
```

### List Personas
```bash
curl http://localhost:5000/api/v1/personas
```

### List Scam Types
```bash
curl http://localhost:5000/api/v1/scam-types
```

---

## 📮 Testing with Postman

### Import Collection

1. Open Postman
2. Click **Import**
3. Create a new collection: "Scam Honeypot API"
4. Add requests for each endpoint above
5. Set base URL: `http://localhost:5000`

### Example Request (Detect Scam)

- **Method**: POST
- **URL**: `{{base_url}}/api/v1/detect`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "message": "URGENT! Your account will be suspended. Click here: http://fake-bank.com"
}
```

---

## 🏭 Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  api_server:app
```

### Using systemd (Linux)

Create `/etc/systemd/system/scam-honeypot.service`:

```ini
[Unit]
Description=Scam Honeypot API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/scam_honeypot
Environment="PATH=/path/to/scam_honeypot/venv/bin"
ExecStart=/path/to/scam_honeypot/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 api_server:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable scam-honeypot
sudo systemctl start scam-honeypot
sudo systemctl status scam-honeypot
```

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

### Build and Run

```bash
# Build image
docker build -t scam-honeypot:latest .

# Run container
docker run -d -p 5000:5000 --name scam-honeypot scam-honeypot:latest

# View logs
docker logs -f scam-honeypot

# Stop container
docker stop scam-honeypot
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - SCAMMER_API_KEY=${SCAMMER_API_KEY}
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

---

## ☁️ Cloud Deployment

### AWS (EC2)

1. **Launch EC2 Instance** (Ubuntu 22.04)
2. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. **Clone/upload code**
4. **Setup virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configure Nginx** (`/etc/nginx/sites-available/scam-honeypot`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Start with systemd** (see above)

### Heroku

1. **Create `Procfile`**:
```
web: gunicorn api_server:app
```

2. **Deploy**:
```bash
heroku create scam-honeypot-api
git push heroku main
```

### Google Cloud Run

1. **Build container**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/scam-honeypot
```

2. **Deploy**:
```bash
gcloud run deploy scam-honeypot \
  --image gcr.io/PROJECT_ID/scam-honeypot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🔒 Security Considerations

### For Production:

1. **Add Authentication**:
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Implement your auth logic
    pass

@app.route('/api/v1/detect', methods=['POST'])
@auth.login_required
def detect_scam():
    # ...
```

2. **Rate Limiting**:
```bash
pip install flask-limiter
```

3. **HTTPS**: Use Let's Encrypt with Nginx
4. **Environment Variables**: Never commit API keys
5. **Monitoring**: Add logging and metrics

---

## 📊 Performance Tuning

### Optimize for High Traffic

1. **Increase workers**:
```bash
gunicorn -w 8 -b 0.0.0.0:5000 api_server:app
```

2. **Use async workers**:
```bash
pip install gevent
gunicorn -k gevent -w 4 -b 0.0.0.0:5000 api_server:app
```

3. **Add caching** (Redis):
```bash
pip install flask-caching
```

---

## 🧪 Load Testing

### Using Apache Bench

```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 -p detect.json -T application/json \
  http://localhost:5000/api/v1/detect
```

### Using wrk

```bash
wrk -t4 -c100 -d30s http://localhost:5000/health
```

---

## 📝 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill it
kill -9 <PID>
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Denied
```bash
# Use sudo or change port to >1024
python api_server.py --port 8080
```

---

## 📞 Support

For issues or questions:
- Check logs: `tail -f logs/honeypot.log`
- Enable debug mode: `python api_server.py --debug`
- Review error logs: `tail -f logs/error.log`

---

**Happy Testing! 🚀**
