from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import datetime
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional
import os
import re

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Security utility for safe logging
def safe_log_config(config: Dict) -> Dict:
    """Create a safe version of config for logging without sensitive information"""
    safe_config = config.copy()
    
    # Hide all potential sensitive keys
    sensitive_keys = ['api_key', 'API_KEY', 'openai_api_key', 'anthropic_api_key', 'google_api_key', 'deepseek_api_key', 'secret_key', 'password']
    for sensitive_key in sensitive_keys:
        if sensitive_key in safe_config:
            safe_config[sensitive_key] = '***HIDDEN***'
    return safe_config

def safe_error_traceback(traceback_str: str) -> str:
    """Create a safe version of traceback without sensitive information"""
    
    # Replace potential API keys in traceback
    # Pattern for common API key formats
    patterns = [
        r'sk-proj-[a-zA-Z0-9_-]+',  # OpenAI project keys
        r'sk-[a-zA-Z0-9_-]{20,}',   # OpenAI keys
        r'AIza[a-zA-Z0-9_-]{35}',   # Google API keys
        r'ya29\.[a-zA-Z0-9_-]+',    # Google OAuth tokens
        r'xoxb-[a-zA-Z0-9-]+',      # Slack bot tokens
        r'[a-zA-Z0-9_-]{32,}',      # Generic long strings that might be keys
    ]
    
    safe_traceback = traceback_str
    for pattern in patterns:
        safe_traceback = re.sub(pattern, '***HIDDEN_API_KEY***', safe_traceback)
    
    return safe_traceback

def is_production() -> bool:
    """Check if running in production environment"""
    return os.environ.get('ENVIRONMENT', '').lower() == 'production'

app = Flask(__name__)
# Use environment variable for SECRET_KEY in production, fallback for development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global storage for analysis sessions
analysis_sessions = {}

class WebMessageBuffer:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = []
        self.tool_calls = []
        self.agent_status = {
            "Market Analyst": "pending",
            "Social Analyst": "pending", 
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            "Trader": "pending",
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            "Portfolio Manager": "pending",
        }
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }
        self.current_step = "waiting"
        self.progress = 0

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = {"timestamp": timestamp, "type": message_type, "content": content}
        self.messages.append(message)
        socketio.emit('new_message', message, room=self.session_id)

    def update_agent_status(self, agent, status):
        self.agent_status[agent] = status
        socketio.emit('agent_status_update', {
            'agent': agent, 
            'status': status
        }, room=self.session_id)

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            socketio.emit('report_update', {
                'section': section_name,
                'content': content
            }, room=self.session_id)

    def update_progress(self, progress, step):
        self.progress = progress
        self.current_step = step
        socketio.emit('progress_update', {
            'progress': progress,
            'step': step
        }, room=self.session_id)

def cleanup_session_collections(session_id):
    """Clean up ChromaDB collections for a specific session to prevent memory leaks"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.Client(Settings(allow_reset=True))
        collections = client.list_collections()
        
        # Remove collections that belong to this session
        for collection in collections:
            if collection.name.endswith(f"_{session_id}"):
                try:
                    client.delete_collection(name=collection.name)
                    print(f"[DEBUG] Cleaned up collection: {collection.name}")
                except Exception as e:
                    print(f"[WARNING] Failed to cleanup collection {collection.name}: {e}")
    except Exception as e:
        print(f"[WARNING] Failed to cleanup collections for session {session_id}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Google Cloud Run"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'TradingAgents Crypto'
    })

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    data = request.json
    session_id = data.get('session_id', str(int(time.time())))
    
    # Store analysis configuration
    analysis_sessions[session_id] = {
        'config': data,
        'buffer': WebMessageBuffer(session_id),
        'status': 'running'
    }
    
    # Start analysis in background
    thread = threading.Thread(
        target=run_analysis_background, 
        args=(session_id, data)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'session_id': session_id, 'status': 'started'})

def run_analysis_background(session_id: str, config: Dict):
    """Run the trading analysis in background thread"""
    import traceback
    try:
        if not is_production():
            print(f"[DEBUG] Starting analysis for session {session_id}")
            print(f"[DEBUG] Config: {safe_log_config(config)}")
            print(f"[DEBUG] Selected analysts: {config['analysts']}")
        
        buffer = analysis_sessions[session_id]['buffer']
        buffer.add_message("System", f"Initializing analysis for {config['ticker']}...")
        # Update configuration based on user selections
        updated_config = DEFAULT_CONFIG.copy()
        api_key = config.get('api_key', '')
        
        # Validate API key for OpenRouter
        if config['llm_provider'] == 'openrouter' and not api_key:
            buffer.add_message("Error", "OpenRouter requires an API key. Please provide your OpenRouter API key.")
            analysis_sessions[session_id]['status'] = 'failed'
            return
        
        if not is_production():
            print(f"[DEBUG] API Key present: {bool(api_key)}")
            if api_key:
                print(f"[DEBUG] API Key length: {len(api_key)}")
                print(f"[DEBUG] API Key starts with: {api_key[:8]}...")
        
        updated_config.update({
            'llm_provider': config['llm_provider'],
            'backend_url': config['backend_url'],
            'api_key': api_key,
            'quick_think_llm': config['shallow_thinker'],  # Map shallow_thinker to quick_think_llm
            'deep_think_llm': config['deep_thinker'],      # Map deep_thinker to deep_think_llm
            'research_depth': config['research_depth'],
            'session_id': session_id  # Add session ID for unique memory collections
        })
        
        if not is_production():
            print(f"[DEBUG] LLM provider: {updated_config['llm_provider']}")
        
        # Initialize the graph with correct parameters
        graph = TradingAgentsGraph(
            selected_analysts=config['analysts'],
            debug=False,
            config=updated_config
        )
        buffer.add_message("System", "Graph initialized successfully")
        
        if not is_production():
            print("[DEBUG] Graph initialized successfully")
            print(f"[DEBUG] Creating initial state for {config['ticker']} on {config['analysis_date']}")
        # Create initial state
        init_state = graph.propagator.create_initial_state(
            config['ticker'], 
            config['analysis_date']
        )
        buffer.add_message("System", "Initial state created successfully")
        
        buffer.add_message("System", f"Starting analysis for {config['ticker']} on {config['analysis_date']}")
        buffer.update_progress(10, "Initializing analysis...")
        
        # Send analysis info to frontend
        socketio.emit('analysis_info_update', {
            'ticker': config['ticker'],
            'analysis_date': config['analysis_date']
        }, room=session_id)
        
        # Get graph args
        args = graph.propagator.get_graph_args()
        
        # Stream the analysis
        step_count = 0
        total_steps = len(config['analysts']) * 2 + 5  # Rough estimate
        
        for chunk in graph.graph.stream(init_state, **args):
            step_count += 1
            progress = min(90, (step_count / total_steps) * 80 + 10)
            
            if len(chunk.get("messages", [])) > 0:
                last_message = chunk["messages"][-1]
                
                if hasattr(last_message, "content"):
                    content = str(last_message.content)
                    if len(content) > 500:  # Truncate very long messages
                        content = content[:500] + "..."
                    buffer.add_message("Analysis", content)
                
                # Update agent statuses based on chunk content
                if "market_report" in chunk and chunk["market_report"]:
                    buffer.update_report_section("market_report", chunk["market_report"])
                    buffer.update_agent_status("Market Analyst", "completed")
                    buffer.update_progress(progress, "Market analysis completed")
                
                if "sentiment_report" in chunk and chunk["sentiment_report"]:
                    buffer.update_report_section("sentiment_report", chunk["sentiment_report"])
                    buffer.update_agent_status("Social Analyst", "completed")
                    buffer.update_progress(progress, "Social sentiment analysis completed")
                
                if "news_report" in chunk and chunk["news_report"]:
                    buffer.update_report_section("news_report", chunk["news_report"])
                    buffer.update_agent_status("News Analyst", "completed")
                    buffer.update_progress(progress, "News analysis completed")
                
                if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                    buffer.update_report_section("fundamentals_report", chunk["fundamentals_report"])
                    buffer.update_agent_status("Fundamentals Analyst", "completed")
                    buffer.update_progress(progress, "Fundamentals analysis completed")
                
                # Handle research team updates
                if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
                    debate_state = chunk["investment_debate_state"]
                    
                    # Update Bull Researcher status and report
                    if "bull_history" in debate_state and debate_state["bull_history"]:
                        buffer.update_agent_status("Bull Researcher", "in_progress")
                        # Extract latest bull response
                        bull_responses = debate_state["bull_history"].split("\n")
                        latest_bull = bull_responses[-1] if bull_responses else ""
                        if latest_bull and len(latest_bull.strip()) > 0:
                            buffer.add_message("Bull Researcher", f"Bull Analysis: {latest_bull}")
                    
                    # Update Bear Researcher status and report  
                    if "bear_history" in debate_state and debate_state["bear_history"]:
                        buffer.update_agent_status("Bear Researcher", "in_progress")
                        # Extract latest bear response
                        bear_responses = debate_state["bear_history"].split("\n")
                        latest_bear = bear_responses[-1] if bear_responses else ""
                        if latest_bear and len(latest_bear.strip()) > 0:
                            buffer.add_message("Bear Researcher", f"Bear Analysis: {latest_bear}")
                    
                    # Update Research Manager status and final decision
                    if "judge_decision" in debate_state and debate_state["judge_decision"]:
                        buffer.update_report_section("investment_plan", debate_state["judge_decision"])
                        buffer.update_agent_status("Bull Researcher", "completed")
                        buffer.update_agent_status("Bear Researcher", "completed") 
                        buffer.update_agent_status("Research Manager", "completed")
                        buffer.add_message("Research Manager", f"Final Decision: {debate_state['judge_decision']}")
                        buffer.update_progress(progress, "Research team decision completed")
                
                # Handle trading team updates
                if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
                    buffer.update_report_section("trader_investment_plan", chunk["trader_investment_plan"])
                    buffer.update_agent_status("Trader", "completed")
                    buffer.update_progress(progress, "Trading plan completed")
                
                # Handle final decision
                if "final_trade_decision" in chunk and chunk["final_trade_decision"]:
                    buffer.update_report_section("final_trade_decision", chunk["final_trade_decision"])
                    buffer.update_agent_status("Portfolio Manager", "completed")
                    buffer.update_progress(100, "Analysis completed!")
        
        buffer.update_progress(100, "Analysis completed successfully!")
        analysis_sessions[session_id]['status'] = 'completed'
        
        # Clean up ChromaDB collections for this session after completion
        cleanup_session_collections(session_id)
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        error_message = f"Analysis failed: {type(e).__name__}: {str(e)}"
        print(f"[ERROR] {error_message}")
        print(f"[ERROR] Traceback:\n{safe_error_traceback(error_traceback)}")
        
        buffer.add_message("Error", error_message)
        buffer.add_message("Error", f"Detailed error: {safe_error_traceback(error_traceback)}")
        buffer.update_progress(0, "Analysis failed")
        analysis_sessions[session_id]['status'] = 'failed'
        
        # Clean up ChromaDB collections even if analysis failed
        cleanup_session_collections(session_id)

@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'Connected to TradingAgents'})

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data['session_id']
    # Join the room for this session
    from flask_socketio import join_room
    join_room(session_id)
    
    # Send current state if session exists
    if session_id in analysis_sessions:
        buffer = analysis_sessions[session_id]['buffer']
        emit('session_state', {
            'messages': buffer.messages,
            'agent_status': buffer.agent_status,
            'report_sections': buffer.report_sections,
            'progress': buffer.progress,
            'current_step': buffer.current_step
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    
    # Use port from environment variable for Cloud Run compatibility
    port = int(os.environ.get('PORT', 8080))
    
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True) 