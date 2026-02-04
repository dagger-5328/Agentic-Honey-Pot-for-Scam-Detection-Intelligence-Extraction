# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An autonomous AI honeypot system that detects scam messages and actively engages scammers using believable personas to extract intelligence including bank account details, UPI IDs, and phishing links.

## 🎯 Features

- **Intelligent Scam Detection**: Pattern-based detection with confidence scoring for multiple scam types
- **Autonomous Conversation Agent**: Engages scammers with realistic victim personas
- **Intelligence Extraction**: Automatically extracts bank accounts, UPI IDs, phone numbers, URLs, and crypto addresses
- **Multiple Personas**: Elderly user, eager customer, worried parent, and busy professional
- **Mock API Integration**: Works with Mock Scammer API or local simulator
- **Structured JSON Output**: Complete intelligence reports in standardized format

## 📋 Requirements

### Python Dependencies

All dependencies are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

### Core Dependencies:
- **requests** (>=2.31.0) - HTTP client for API communication
- **pydantic** (>=2.5.0) - Data validation and JSON schemas
- **pyyaml** (>=6.0.1) - YAML configuration parsing
- **python-dotenv** (>=1.0.0) - Environment variable management
- **regex** (>=2023.10.3) - Advanced regular expressions
- **phonenumbers** (>=8.13.26) - Phone number parsing and validation

### Testing Dependencies:
- **pytest** (>=7.4.3) - Testing framework
- **pytest-cov** (>=4.1.0) - Test coverage reporting
- **pytest-mock** (>=3.12.0) - Mocking for tests

### Utilities:
- **colorama** (>=0.4.6) - Colored terminal output
- **rich** (>=13.7.0) - Beautiful terminal formatting
- **python-dateutil** (>=2.8.2) - Date/time utilities

### Optional (Advanced NLP):
- **spacy** (>=3.7.2) - Named entity recognition
- **transformers** (>=4.36.0) - Advanced language models
- **langchain** (>=0.1.0) - LLM agent framework

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd scam_honeypot

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` and add your Mock Scammer API key if using the real API:
```
SCAMMER_API_KEY=your_api_key_here
```

### 3. Run Demo

```bash
# Run with default random scam scenario
python main.py --demo

# Run specific scam type
python main.py --demo --scenario banking_fraud

# Available scenarios:
# - banking_fraud
# - prize_lottery
# - tech_support
# - impersonation
# - investment_crypto
# - upi_payment
```

### 4. Process Custom Message

```bash
# Interactive mode
python main.py

# Process from file
python main.py --input sample_message.txt
```

## 📁 Project Structure

```
scam_honeypot/
├── src/
│   ├── detector/              # Scam detection engine
│   │   └── scam_detector.py
│   ├── agent/                 # Conversation agent
│   │   ├── persona_manager.py
│   │   └── conversation_agent.py
│   ├── extractor/             # Intelligence extraction
│   │   └── intelligence_extractor.py
│   └── api/                   # API integration
│       ├── mock_scammer_api.py
│       └── api_simulator.py
├── config/
│   └── config.yaml            # System configuration
├── data/
│   ├── scam_patterns.json     # Scam detection patterns
│   └── personas.json          # Victim persona profiles
├── tests/                     # Test suite
├── examples/                  # Example outputs
├── output/                    # Generated reports
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── main.py                    # Entry point
└── README.md                  # This file
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:

- **API settings**: Endpoint, timeout, use simulator
- **Detection thresholds**: Minimum confidence level
- **Agent behavior**: Max turns, response delays, persona selection
- **Extraction targets**: What intelligence to extract
- **Output format**: JSON formatting, save location

## 📊 Output Format

The system generates JSON reports with the following structure:

```json
{
  "conversation_id": "uuid",
  "timestamp": "ISO-8601",
  "scam_type": "banking_fraud",
  "confidence_score": 95,
  "extracted_intelligence": {
    "bank_accounts": [...],
    "upi_ids": [...],
    "phone_numbers": [...],
    "urls": [...],
    "emails": [...]
  },
  "conversation_summary": {
    "total_messages": 12,
    "duration_seconds": 340,
    "persona_used": "elderly_user",
    "key_tactics": ["urgency", "fear", "authority"]
  },
  "full_transcript": [...]
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_detector.py
```

## 🎭 Personas

The system includes 4 built-in personas:

1. **Elderly User** - Tech-naive, trusting, concerned about security
2. **Eager Customer** - Excited about offers, quick to respond
3. **Worried Parent** - Concerned about family, willing to help
4. **Busy Professional** - Distracted, time-pressured

## 🔍 Scam Types Detected

- Banking/Financial Fraud
- Prize/Lottery Scams
- Tech Support Scams
- Impersonation (Government/Authority)
- Investment/Crypto Scams
- UPI/Payment Scams

## 📝 Usage Examples

### Example 1: Detect and Engage

```python
from main import ScamHoneypot

honeypot = ScamHoneypot()
message = "Your account is blocked. Click here to verify immediately!"
result = honeypot.process_message(message)
print(result)
```

### Example 2: Custom Persona

```python
from agent.conversation_agent import ConversationAgent

agent = ConversationAgent(persona_name='elderly_user')
response = agent.start_conversation(scam_message, 'banking_fraud')
```

## 🛡️ Security Note

This system is designed for **research and educational purposes** to understand scam tactics and improve fraud detection. Always follow ethical guidelines and legal requirements when deploying honeypot systems.

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📧 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built for scam detection and intelligence extraction hackathon** 🚀
