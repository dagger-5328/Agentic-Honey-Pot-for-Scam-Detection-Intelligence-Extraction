"""
GUVI Hackathon API Server
REST API Server compliant with GUVI Agentic Honey-Pot specifications.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import logging
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from main import ScamHoneypot
from src.detector.scam_detector import ScamDetector
from src.agent.conversation_agent import ConversationAgent
from src.extractor.intelligence_extractor import IntelligenceExtractor

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure request size limits (10MB max)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key (set via environment variable)
API_KEY = os.getenv('HONEYPOT_API_KEY', 'your-secret-api-key-here')

# GUVI Callback endpoint
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Session storage (in production, use Redis or database)
active_sessions: Dict[str, dict] = {}

# Initialize honeypot components
honeypot = ScamHoneypot()


def verify_api_key():
    """Verify API key from request headers."""
    api_key = request.headers.get('x-api-key')
    if not api_key or api_key != API_KEY:
        return False
    return True


def get_or_create_session(session_id: str) -> dict:
    """Get existing session or create new one."""
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            'session_id': session_id,
            'conversation_history': [],
            'scam_detected': False,
            'scam_type': None,
            'confidence': 0,
            'agent': None,
            'persona': None,
            'start_time': datetime.now(),
            'total_messages': 0,
            'intelligence': {
                'bankAccounts': [],
                'upiIds': [],
                'phishingLinks': [],
                'phoneNumbers': [],
                'suspiciousKeywords': []
            },
            'agent_notes': []
        }
        logger.info(f"Created new session: {session_id}")
    
    return active_sessions[session_id]


def should_end_conversation(session: dict) -> bool:
    """Determine if conversation should end and intelligence should be sent."""
    # End if we've had enough turns
    if session['total_messages'] >= honeypot.config['agent']['max_conversation_turns']:
        return True
    
    # End if we've extracted significant intelligence
    intel = session['intelligence']
    has_intel = (
        len(intel['bankAccounts']) > 0 or
        len(intel['upiIds']) > 0 or
        len(intel['phishingLinks']) > 0 or
        len(intel['phoneNumbers']) > 0
    )
    
    # If we have intelligence and enough conversation turns
    if has_intel and session['total_messages'] >= 5:
        return True
    
    return False


def send_final_result(session_id: str):
    """Send final intelligence to GUVI evaluation endpoint."""
    if session_id not in active_sessions:
        logger.error(f"Session {session_id} not found for final result callback")
        return
    
    session = active_sessions[session_id]
    
    # Prepare payload
    payload = {
        "sessionId": session_id,
        "scamDetected": session['scam_detected'],
        "totalMessagesExchanged": session['total_messages'],
        "extractedIntelligence": session['intelligence'],
        "agentNotes": " | ".join(session['agent_notes']) if session['agent_notes'] else "Conversation completed"
    }
    
    try:
        logger.info(f"Sending final result for session {session_id} to GUVI")
        logger.info(f"Payload: {payload}")
        
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent final result for session {session_id}")
        else:
            logger.error(f"Failed to send final result. Status: {response.status_code}, Response: {response.text}")
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout sending final result for session {session_id}")
    except Exception as e:
        logger.error(f"Error sending final result for session {session_id}: {e}", exc_info=True)
    
    # Clean up session
    if session_id in active_sessions:
        del active_sessions[session_id]
        logger.info(f"Session {session_id} cleaned up")


def extract_suspicious_keywords(text: str) -> List[str]:
    """Extract suspicious keywords from text."""
    keywords = []
    text_lower = text.lower()
    
    suspicious_words = [
        'urgent', 'immediately', 'verify', 'confirm', 'account blocked',
        'suspended', 'expire', 'click here', 'update now', 'verify now',
        'limited time', 'act now', 'congratulations', 'winner', 'prize',
        'lottery', 'reward', 'claim', 'free', 'offer', 'deal',
        'police', 'arrest', 'legal action', 'court', 'fine',
        'tax', 'refund', 'payment', 'transfer', 'send money'
    ]
    
    for word in suspicious_words:
        if word in text_lower:
            keywords.append(word)
    
    return keywords


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'guvi-scam-honeypot-api',
        'version': '1.0.0',
        'active_sessions': len(active_sessions)
    }), 200


@app.route('/api/honeypot', methods=['POST'])
def honeypot_endpoint():
    """
    Main honeypot endpoint compliant with GUVI specifications.
    
    Request format:
    {
        "sessionId": "unique-session-id",
        "message": {
            "sender": "scammer",
            "text": "Your account will be blocked...",
            "timestamp": 1770005528731
        },
        "conversationHistory": [...],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    Response format:
    {
        "status": "success",
        "reply": "Agent's response message"
    }
    """
    # Verify API key
    if not verify_api_key():
        return jsonify({
            'status': 'error',
            'message': 'Invalid or missing API key'
        }), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        if 'sessionId' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: sessionId'
            }), 400
        
        if 'message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: message'
            }), 400
        
        session_id = data['sessionId']
        message_obj = data['message']
        conversation_history = data.get('conversationHistory', [])
        metadata = data.get('metadata', {})
        
        # Validate message object
        if not isinstance(message_obj, dict) or 'text' not in message_obj:
            return jsonify({
                'status': 'error',
                'message': 'Invalid message format'
            }), 400
        
        scammer_message = message_obj['text']
        
        logger.info(f"Session {session_id}: Received message: {scammer_message[:100]}...")
        
        # Get or create session
        session = get_or_create_session(session_id)
        
        # First message - detect scam
        if session['total_messages'] == 0:
            logger.info(f"Session {session_id}: First message - detecting scam")
            
            # Detect scam
            detection_result = honeypot.detector.detect(scammer_message)
            
            session['scam_detected'] = detection_result['is_scam']
            session['scam_type'] = detection_result.get('scam_type', 'unknown')
            session['confidence'] = detection_result.get('confidence', 0)
            
            # Extract initial keywords
            keywords = extract_suspicious_keywords(scammer_message)
            session['intelligence']['suspiciousKeywords'].extend(keywords)
            
            if not detection_result['is_scam']:
                logger.info(f"Session {session_id}: Not a scam, ignoring")
                return jsonify({
                    'status': 'success',
                    'reply': 'Thank you for your message.'
                }), 200
            
            # Check confidence threshold
            min_confidence = honeypot.config['detection']['min_confidence_threshold']
            if detection_result['confidence'] < min_confidence:
                logger.info(f"Session {session_id}: Low confidence ({detection_result['confidence']}%), ignoring")
                return jsonify({
                    'status': 'success',
                    'reply': 'I see. Thank you.'
                }), 200
            
            logger.info(f"Session {session_id}: Scam detected - {session['scam_type']} ({session['confidence']}%)")
            
            # Select persona based on scam type
            persona_name = honeypot._select_persona(session['scam_type'])
            session['persona'] = persona_name
            
            # Initialize conversation agent
            session['agent'] = ConversationAgent(
                persona_name=persona_name,
                config=honeypot.config['agent']
            )
            
            # Add to conversation history
            session['conversation_history'].append({
                'role': 'scammer',
                'content': scammer_message,
                'timestamp': message_obj.get('timestamp', int(time.time() * 1000))
            })
            
            # Generate first response
            agent_response = session['agent'].start_conversation(scammer_message, session['scam_type'])
            
            session['conversation_history'].append({
                'role': 'agent',
                'content': agent_response,
                'timestamp': int(time.time() * 1000)
            })
            
            session['total_messages'] += 2
            session['agent_notes'].append(f"Scam type: {session['scam_type']}, Confidence: {session['confidence']}%")
            
            logger.info(f"Session {session_id}: Agent response: {agent_response}")
            
            return jsonify({
                'status': 'success',
                'reply': agent_response
            }), 200
        
        else:
            # Continuing conversation
            logger.info(f"Session {session_id}: Continuing conversation (turn {session['total_messages'] // 2 + 1})")
            
            if not session['agent']:
                logger.error(f"Session {session_id}: No agent initialized")
                return jsonify({
                    'status': 'error',
                    'message': 'Session state error'
                }), 500
            
            # Add scammer message to history
            session['conversation_history'].append({
                'role': 'scammer',
                'content': scammer_message,
                'timestamp': message_obj.get('timestamp', int(time.time() * 1000))
            })
            
            # Extract intelligence from scammer message
            intel = honeypot.extractor.extract_all([{
                'role': 'scammer',
                'content': scammer_message
            }])
            
            # Update session intelligence
            if intel.get('bank_accounts'):
                for acc in intel['bank_accounts']:
                    acc_str = f"{acc.get('account_number', 'N/A')} ({acc.get('bank_name', 'Unknown')})"
                    if acc_str not in session['intelligence']['bankAccounts']:
                        session['intelligence']['bankAccounts'].append(acc_str)
            
            if intel.get('upi_ids'):
                session['intelligence']['upiIds'].extend([u for u in intel['upi_ids'] if u not in session['intelligence']['upiIds']])
            
            if intel.get('urls'):
                session['intelligence']['phishingLinks'].extend([u for u in intel['urls'] if u not in session['intelligence']['phishingLinks']])
            
            if intel.get('phone_numbers'):
                session['intelligence']['phoneNumbers'].extend([p for p in intel['phone_numbers'] if p not in session['intelligence']['phoneNumbers']])
            
            # Extract keywords
            keywords = extract_suspicious_keywords(scammer_message)
            session['intelligence']['suspiciousKeywords'].extend([k for k in keywords if k not in session['intelligence']['suspiciousKeywords']])
            
            # Generate agent response
            agent_response = session['agent'].generate_response(scammer_message)
            
            if not agent_response:
                logger.info(f"Session {session_id}: Agent ended conversation")
                # Send final result before ending
                send_final_result(session_id)
                return jsonify({
                    'status': 'success',
                    'reply': 'Thank you for the information. I need to go now.'
                }), 200
            
            session['conversation_history'].append({
                'role': 'agent',
                'content': agent_response,
                'timestamp': int(time.time() * 1000)
            })
            
            session['total_messages'] += 2
            
            logger.info(f"Session {session_id}: Agent response: {agent_response}")
            
            # Check if conversation should end
            if should_end_conversation(session):
                logger.info(f"Session {session_id}: Ending conversation and sending final result")
                session['agent_notes'].append(f"Conversation ended after {session['total_messages']} messages")
                send_final_result(session_id)
            
            return jsonify({
                'status': 'success',
                'reply': agent_response
            }), 200
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Invalid input format'
        }), 400
    
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List active sessions (for debugging)."""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    sessions_info = []
    for session_id, session in active_sessions.items():
        sessions_info.append({
            'session_id': session_id,
            'scam_detected': session['scam_detected'],
            'scam_type': session['scam_type'],
            'total_messages': session['total_messages'],
            'start_time': session['start_time'].isoformat()
        })
    
    return jsonify({
        'active_sessions': len(active_sessions),
        'sessions': sessions_info
    }), 200


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details (for debugging)."""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    
    return jsonify({
        'session_id': session_id,
        'scam_detected': session['scam_detected'],
        'scam_type': session['scam_type'],
        'confidence': session['confidence'],
        'total_messages': session['total_messages'],
        'intelligence': session['intelligence'],
        'agent_notes': session['agent_notes'],
        'conversation_history': session['conversation_history']
    }), 200


@app.route('/api/session/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """Manually end a session and send final result."""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    send_final_result(session_id)
    
    return jsonify({
        'status': 'success',
        'message': f'Session {session_id} ended and final result sent'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(413)
def request_too_large(error):
    """Handle request entity too large errors."""
    return jsonify({
        'error': 'Request too large',
        'message': 'Request size exceeds maximum allowed limit (10MB)'
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='GUVI Scam Honeypot API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--api-key', help='API key for authentication')
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        API_KEY = args.api_key
        logger.info("API key set from command line")
    
    logger.info(f"Starting GUVI Scam Honeypot API on {args.host}:{args.port}")
    logger.info(f"API Key: {API_KEY[:10]}..." if len(API_KEY) > 10 else API_KEY)
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /api/honeypot - Main honeypot endpoint (GUVI compliant)")
    logger.info("  GET  /api/sessions - List active sessions")
    logger.info("  GET  /api/session/<id> - Get session details")
    logger.info("  POST /api/session/<id>/end - Manually end session")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
