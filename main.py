"""
Main Application
Orchestrates the scam honeypot system.
"""

import sys
import json
import yaml
import logging
import argparse
import uuid
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from detector.scam_detector import ScamDetector
from agent.conversation_agent import ConversationAgent
from extractor.intelligence_extractor import IntelligenceExtractor
from api.mock_scammer_api import MockScammerAPI
from api.api_simulator import APISimulator


class ScamHoneypot:
    """Main honeypot orchestrator."""
    
    def __init__(self, config_path: str = None):
        """Initialize the honeypot system."""
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / 'config' / 'config.yaml'
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.detector = ScamDetector()
        self.extractor = IntelligenceExtractor()
        
        # Initialize API (simulator or real)
        if self.config['api']['use_simulator']:
            self.logger.info("Using API Simulator")
            self.api = APISimulator()
        else:
            self.logger.info("Using Mock Scammer API")
            self.api = MockScammerAPI(
                base_url=self.config['api']['base_url'],
                api_key=self.config['api'].get('api_key'),
                timeout=self.config['api']['timeout']
            )
        
        # Output directory
        self.output_dir = Path(self.config['output']['output_directory'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config['logging']
        
        # Create logs directory
        log_file = Path(log_config['log_file'])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() if log_config['console_output'] else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def process_message(self, message: str) -> dict:
        """
        Process a single message through the honeypot.
        
        Args:
            message: The message to analyze
            
        Returns:
            Processing result
        """
        # Input validation
        if not message or not isinstance(message, str):
            return {
                'status': 'error',
                'reason': 'invalid_input',
                'message': 'Message must be a non-empty string'
            }
        
        # Limit message length to prevent memory issues
        max_length = 10000
        if len(message) > max_length:
            self.logger.warning(f"Message truncated from {len(message)} to {max_length} characters")
            message = message[:max_length]
        
        # Sanitize message (remove null bytes and control characters)
        message = message.replace('\x00', '').strip()
        
        if not message:
            return {
                'status': 'error',
                'reason': 'empty_message',
                'message': 'Message is empty after sanitization'
            }
        
        self.logger.info(f"Processing message: {message[:50]}...")
        
        # Step 1: Detect if it's a scam
        detection_result = self.detector.detect(message)
        
        if not detection_result['is_scam']:
            self.logger.info("Message is not a scam. Ignoring.")
            return {
                'status': 'ignored',
                'reason': 'not_a_scam',
                'detection': detection_result
            }
        
        # Check confidence threshold
        min_confidence = self.config['detection']['min_confidence_threshold']
        if detection_result['confidence'] < min_confidence:
            self.logger.info(f"Confidence {detection_result['confidence']}% below threshold {min_confidence}%")
            return {
                'status': 'ignored',
                'reason': 'low_confidence',
                'detection': detection_result
            }
        
        self.logger.info(f"Scam detected: {detection_result['scam_type']} ({detection_result['confidence']}%)")
        
        # Step 2: Engage with the scammer
        conversation_id = str(uuid.uuid4())
        report = self.engage_scammer(message, detection_result, conversation_id)
        
        return {
            'status': 'processed',
            'conversation_id': conversation_id,
            'report': report
        }
    
    def engage_scammer(self, initial_message: str, detection_result: dict, 
                       conversation_id: str) -> dict:
        """
        Engage with the scammer to extract intelligence.
        
        Args:
            initial_message: Initial scam message
            detection_result: Scam detection results
            conversation_id: Unique conversation ID
            
        Returns:
            Intelligence report
        """
        scam_type = detection_result['scam_type']
        confidence = detection_result['confidence']
        
        # Initialize conversation agent
        persona_name = self.config['agent'].get('default_persona')
        agent = ConversationAgent(
            persona_name=persona_name,
            config=self.config['agent']
        )
        
        self.logger.info(f"Starting conversation with persona: {agent.persona_manager.current_persona['id']}")
        
        # Start conversation
        start_time = datetime.now()
        session_id = None
        
        try:
            # If using simulator, start a session
            if isinstance(self.api, APISimulator):
                session_result = self.api.start_conversation(scam_type=scam_type)
                session_id = session_result['session_id']
                # Use the simulator's initial message
                initial_message = session_result['initial_message']
                self.logger.info(f"Simulator session started: {session_id}")
            
            # Agent's first response
            agent_response = agent.start_conversation(initial_message, scam_type)
            self.logger.info(f"Agent: {agent_response}")
            
            # Continue conversation
            max_turns = self.config['agent']['max_conversation_turns']
            
            for turn in range(max_turns):
                # Simulate typing delay
                agent.simulate_typing_delay()
                
                # Get scammer's response
                scammer_message = self._get_scammer_response(agent_response, session_id)
                
                if not scammer_message:
                    self.logger.info("Scammer stopped responding. Ending conversation.")
                    break
                
                self.logger.info(f"Scammer: {scammer_message}")
                
                # Generate agent response
                agent_response = agent.generate_response(scammer_message)
                
                if not agent_response:
                    self.logger.info("Agent ended conversation.")
                    break
                
                self.logger.info(f"Agent: {agent_response}")
            
            # End session if using simulator
            if isinstance(self.api, APISimulator) and session_id:
                self.api.end_conversation(session_id)
            
            # Calculate duration
            duration = int((datetime.now() - start_time).total_seconds())
            
            # Extract intelligence
            conversation = agent.get_conversation_history()
            
            report = self.extractor.generate_report(
                conversation_id=conversation_id,
                scam_type=scam_type,
                confidence=confidence,
                conversation=conversation,
                persona_used=agent.persona_manager.current_persona['id'],
                duration_seconds=duration
            )
            
            # Save report
            if self.config['output']['save_conversations']:
                self._save_report(report)
            
            self.logger.info(f"Conversation completed. Extracted intelligence.")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error during conversation: {e}", exc_info=True)
            # Clean up session if needed
            if isinstance(self.api, APISimulator) and session_id:
                try:
                    self.api.end_conversation(session_id)
                except:
                    pass
            raise
    
    def _get_scammer_response(self, agent_message: str, session_id: str = None) -> str:
        """Get scammer's response from API or simulator."""
        if isinstance(self.api, APISimulator):
            # Using simulator - need session_id
            if not session_id:
                self.logger.error("No session_id provided for simulator")
                return None
            
            # Send agent's message
            self.api.send_message(session_id, agent_message)
            
            # Get scammer's response
            return self.api.get_scammer_response(session_id)
        else:
            # Using real API
            self.api.send_message(agent_message)
            return self.api.get_scammer_response()
    
    def _save_report(self, report: dict):
        """Save intelligence report to file."""
        filename = f"report_{report['conversation_id']}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if self.config['output']['json_pretty_print']:
                json.dump(report, f, indent=2, ensure_ascii=False)
            else:
                json.dump(report, f, ensure_ascii=False)
        
        self.logger.info(f"Report saved to {filepath}")
    
    def run_demo(self, scenario: str = None):
        """
        Run a demo scenario.
        
        Args:
            scenario: Specific scam type to demo
        """
        print("=" * 60)
        print("SCAM HONEYPOT DEMO")
        print("=" * 60)
        
        # Use simulator for demo
        simulator = APISimulator()
        
        # Start conversation
        result = simulator.start_conversation(scam_type=scenario)
        session_id = result['session_id']
        initial_message = result['initial_message']
        scam_type = result['scam_type']
        
        print(f"\nScam Type: {scam_type}")
        print(f"Initial Message: {initial_message}\n")
        
        # Detect scam
        detection = self.detector.detect(initial_message)
        print(f"Detection Result:")
        print(f"  - Is Scam: {detection['is_scam']}")
        print(f"  - Confidence: {detection['confidence']}%")
        print(f"  - Type: {detection['scam_type']}\n")
        
        # Create agent
        agent = ConversationAgent(config=self.config['agent'])
        
        print(f"Persona: {agent.persona_manager.current_persona['name']}")
        print(f"=" * 60)
        print("\nCONVERSATION:\n")
        
        # Start conversation
        agent_response = agent.start_conversation(initial_message, scam_type)
        print(f"Agent: {agent_response}")
        
        # Continue for a few turns
        for i in range(5):
            simulator.send_message(session_id, agent_response)
            scammer_msg = simulator.get_scammer_response(session_id)
            
            if not scammer_msg:
                break
            
            print(f"\nScammer: {scammer_msg}")
            
            agent_response = agent.generate_response(scammer_msg)
            if not agent_response:
                break
            
            print(f"Agent: {agent_response}")
        
        # Extract intelligence
        conversation = agent.get_conversation_history()
        intelligence = self.extractor.extract_all(conversation)
        
        print(f"\n{'=' * 60}")
        print("EXTRACTED INTELLIGENCE:")
        print(f"{'=' * 60}\n")
        print(json.dumps(intelligence, indent=2))
        
        # Cleanup
        simulator.end_conversation(session_id)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Scam Honeypot System')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--scenario', type=str, help='Demo scenario type')
    parser.add_argument('--input', type=str, help='Input message file')
    parser.add_argument('--config', type=str, help='Config file path')
    
    args = parser.parse_args()
    
    # Initialize honeypot
    honeypot = ScamHoneypot(config_path=args.config)
    
    if args.demo:
        # Run demo
        honeypot.run_demo(scenario=args.scenario)
    elif args.input:
        # Process input file
        with open(args.input, 'r', encoding='utf-8') as f:
            message = f.read()
        
        result = honeypot.process_message(message)
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        print("Scam Honeypot System - Interactive Mode")
        print("Enter a message to analyze (or 'quit' to exit):\n")
        
        while True:
            message = input("> ")
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            result = honeypot.process_message(message)
            print(json.dumps(result, indent=2))
            print()


if __name__ == "__main__":
    main()
