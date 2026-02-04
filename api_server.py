"""
REST API Server for Scam Honeypot
Exposes honeypot functionality via HTTP endpoints.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from main import ScamHoneypot

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for testing

# Initialize honeypot
honeypot = ScamHoneypot()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'scam-honeypot-api',
        'version': '1.0.0'
    }), 200


@app.route('/api/v1/detect', methods=['POST'])
def detect_scam():
    """
    Detect if a message is a scam.
    
    Request body:
    {
        "message": "Your account has been blocked..."
    }
    
    Response:
    {
        "is_scam": true,
        "confidence": 85,
        "scam_type": "banking_fraud",
        "matched_patterns": [...],
        "red_flags": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message']
        
        # Detect scam
        result = honeypot.detector.detect(message)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in detect endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/v1/engage', methods=['POST'])
def engage_scammer():
    """
    Engage with a scammer and extract intelligence.
    
    Request body:
    {
        "message": "Your account has been blocked...",
        "persona": "elderly_user"  // optional
    }
    
    Response:
    {
        "conversation_id": "uuid",
        "scam_type": "banking_fraud",
        "confidence_score": 95,
        "extracted_intelligence": {...},
        "conversation_summary": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message']
        persona = data.get('persona')  # Optional
        
        # Override persona if specified
        if persona:
            honeypot.config['agent']['default_persona'] = persona
        
        # Process message (detect + engage)
        result = honeypot.process_message(message)
        
        if result['status'] == 'error':
            return jsonify(result), 400
        elif result['status'] == 'ignored':
            return jsonify(result), 200
        else:
            # Return the intelligence report
            return jsonify(result['report']), 200
        
    except Exception as e:
        logger.error(f"Error in engage endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/v1/extract', methods=['POST'])
def extract_intelligence():
    """
    Extract intelligence from a conversation transcript.
    
    Request body:
    {
        "conversation": [
            {"role": "scammer", "content": "Send money to..."},
            {"role": "agent", "content": "Okay..."}
        ]
    }
    
    Response:
    {
        "bank_accounts": [...],
        "upi_ids": [...],
        "phone_numbers": [...],
        "urls": [...],
        "emails": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'conversation' not in data:
            return jsonify({
                'error': 'Missing required field: conversation'
            }), 400
        
        conversation = data['conversation']
        
        if not isinstance(conversation, list):
            return jsonify({
                'error': 'conversation must be an array'
            }), 400
        
        # Extract intelligence
        intelligence = honeypot.extractor.extract_all(conversation)
        
        return jsonify(intelligence), 200
        
    except Exception as e:
        logger.error(f"Error in extract endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/v1/personas', methods=['GET'])
def list_personas():
    """
    List available personas.
    
    Response:
    {
        "personas": [
            {
                "id": "elderly_user",
                "name": "Ramesh Kumar",
                "age": 68,
                "characteristics": [...]
            }
        ]
    }
    """
    try:
        personas_file = Path(__file__).parent / 'data' / 'personas.json'
        
        import json
        with open(personas_file, 'r') as f:
            data = json.load(f)
        
        personas_list = []
        for persona_id, persona_data in data['personas'].items():
            personas_list.append({
                'id': persona_id,
                **persona_data
            })
        
        return jsonify({
            'personas': personas_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error in personas endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/v1/scam-types', methods=['GET'])
def list_scam_types():
    """
    List supported scam types.
    
    Response:
    {
        "scam_types": [
            {
                "id": "banking_fraud",
                "keywords": [...],
                "confidence_weight": 0.9
            }
        ]
    }
    """
    try:
        patterns_file = Path(__file__).parent / 'data' / 'scam_patterns.json'
        
        import json
        with open(patterns_file, 'r') as f:
            data = json.load(f)
        
        scam_types_list = []
        for scam_id, scam_data in data['scam_types'].items():
            scam_types_list.append({
                'id': scam_id,
                **scam_data
            })
        
        return jsonify({
            'scam_types': scam_types_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error in scam-types endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Scam Honeypot API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    logger.info(f"Starting Scam Honeypot API on {args.host}:{args.port}")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /api/v1/detect - Detect scam")
    logger.info("  POST /api/v1/engage - Engage with scammer")
    logger.info("  POST /api/v1/extract - Extract intelligence")
    logger.info("  GET  /api/v1/personas - List personas")
    logger.info("  GET  /api/v1/scam-types - List scam types")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
