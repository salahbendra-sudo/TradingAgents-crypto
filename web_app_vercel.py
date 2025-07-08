from flask import Flask, render_template, request, jsonify
import datetime
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tradingagents_secret_key'

# Global storage for analysis sessions (simplified for serverless)
analysis_sessions = {}

class SimpleMessageBuffer:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = []
        self.agent_status = {
            "Market Analyst": "pending",
            "Social Analyst": "pending", 
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            "Trader": "pending",
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

    def update_agent_status(self, agent, status):
        self.agent_status[agent] = status

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content

    def update_progress(self, progress, step):
        self.progress = progress
        self.current_step = step

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

@app.route('/api/start_analysis', methods=['POST'])
def start_analysis():
    try:
        data = request.json
        session_id = data.get('session_id', str(int(time.time())))
        
        # For Vercel, we'll run analysis synchronously (with timeout)
        # Note: This is a simplified version due to serverless limitations
        
        buffer = SimpleMessageBuffer(session_id)
        buffer.add_message("System", f"Initializing analysis for {data['ticker']}...")
        
        # Update configuration
        updated_config = DEFAULT_CONFIG.copy()
        updated_config.update({
            'llm_provider': data['llm_provider'],
            'backend_url': data['backend_url'],
            'api_key': data.get('api_key', ''),
            'shallow_thinker': data['shallow_thinker'],
            'deep_thinker': data['deep_thinker'],
            'research_depth': data['research_depth'],
            'session_id': session_id
        })
        
        # Note: Due to Vercel's 300s timeout, we return a simplified response
        # Full analysis would require a different architecture (e.g., queuing system)
        
        analysis_sessions[session_id] = {
            'config': data,
            'buffer': buffer,
            'status': 'queued'
        }
        
        return jsonify({
            'session_id': session_id, 
            'status': 'queued',
            'message': 'Analysis queued. Note: Full real-time analysis requires a persistent server environment.'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to start analysis'
        }), 500

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """Get the current status of an analysis session"""
    if session_id in analysis_sessions:
        session = analysis_sessions[session_id]
        return jsonify({
            'session_id': session_id,
            'status': session['status'],
            'messages': session['buffer'].messages,
            'agent_status': session['buffer'].agent_status,
            'report_sections': session['buffer'].report_sections,
            'progress': session['buffer'].progress,
            'current_step': session['buffer'].current_step
        })
    else:
        return jsonify({'error': 'Session not found'}), 404

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True) 