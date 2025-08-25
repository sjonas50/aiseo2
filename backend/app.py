#!/usr/bin/env python3
"""
Flask API Backend for AISEO Multi-LLM Query Tool
Provides REST API and WebSocket support for the frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import json
import uuid
from datetime import datetime
from threading import Thread
import queue
import time

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing modules
from run import FixedLLMTester
from analyzer import ResponseAnalyzer

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store query results in memory (in production, use Redis or database)
query_results = {}
active_queries = {}

# Initialize tester and analyzer
def init_services():
    """Initialize services after environment is loaded"""
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Check configured providers
    configured_providers = []
    api_keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'perplexity': os.getenv('PERPLEXITY_API_KEY'),
        'google': os.getenv('GOOGLE_API_KEY'),
        'google_search': os.getenv('GOOGLE_SEARCH_API_KEY'),
        'google_cx': os.getenv('GOOGLE_SEARCH_CX'),
    }
    
    for provider, key in api_keys.items():
        if provider == 'google_cx':
            if key and not key.startswith('your-'):
                pass
        elif key and not key.startswith('your-') and not key.startswith('sk-your') and not key.startswith('pplx-your'):
            if provider != 'google_search':
                configured_providers.append(provider)
    
    if api_keys.get('google_search') and api_keys.get('google_cx'):
        configured_providers.append('google_search')
    
    return configured_providers

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get list of configured providers"""
    providers = init_services()
    
    provider_info = []
    for provider in providers:
        info = {
            "id": provider,
            "name": provider.replace('_', ' ').title(),
            "enabled": True,
            "model": None
        }
        
        # Add model information
        if provider == 'openai':
            info["model"] = os.getenv('OPENAI_MODEL', 'gpt-4.1')
        elif provider == 'anthropic':
            info["model"] = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        elif provider == 'perplexity':
            info["model"] = os.getenv('PERPLEXITY_MODEL', 'llama-3.1-sonar-small-128k-online')
        elif provider == 'google':
            info["model"] = os.getenv('GOOGLE_MODEL', 'gemini-2.5-flash')
        
        provider_info.append(info)
    
    return jsonify({
        "providers": provider_info,
        "analysis_enabled": os.getenv('ANALYZE_RESPONSES', 'true').lower() == 'true'
    })

@app.route('/api/query', methods=['POST'])
def submit_query():
    """Submit a query to all configured LLMs"""
    data = request.json
    query_text = data.get('query')
    selected_providers = data.get('providers', None)  # Optional: specific providers
    
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400
    
    # Generate query ID
    query_id = str(uuid.uuid4())
    
    # Initialize result structure
    query_results[query_id] = {
        "id": query_id,
        "query": query_text,
        "timestamp": datetime.now().isoformat(),
        "status": "processing",
        "results": {},
        "analysis": None
    }
    
    # Start processing in background thread
    thread = Thread(target=process_query_async, args=(query_id, query_text, selected_providers))
    thread.start()
    
    return jsonify({
        "query_id": query_id,
        "message": "Query submitted successfully",
        "websocket_room": f"query_{query_id}"
    })

def process_query_async(query_id, query_text, selected_providers=None):
    """Process query asynchronously and emit updates via WebSocket"""
    try:
        # Re-initialize services in thread context
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Import after loading env
        global FixedLLMTester, ResponseAnalyzer
        from run import FixedLLMTester
        from analyzer import ResponseAnalyzer
        
        tester = FixedLLMTester()
        analyzer = ResponseAnalyzer()
        
        # Get configured providers
        if selected_providers is None:
            selected_providers = init_services()
        
        # Process each provider
        for provider in selected_providers:
            # Emit start event
            socketio.emit('provider_start', {
                'query_id': query_id,
                'provider': provider
            }, room=f"query_{query_id}")
            
            # Test provider
            result = None
            if provider == 'openai':
                result = tester.test_openai(query_text)
            elif provider == 'anthropic':
                result = tester.test_anthropic(query_text)
            elif provider == 'google':
                result = tester.test_google(query_text)
            elif provider == 'perplexity':
                result = tester.test_perplexity(query_text)
            elif provider == 'google_search':
                result = tester.test_google_search(query_text)
            
            if result:
                # Store result
                query_results[query_id]["results"][provider] = result
                
                # Emit result event
                socketio.emit('provider_complete', {
                    'query_id': query_id,
                    'provider': provider,
                    'result': result
                }, room=f"query_{query_id}")
                
                # Analyze if enabled and successful
                if result.get('success') and analyzer.analyze_enabled and provider != 'google_search':
                    analysis = analyzer.analyze_with_ai(
                        result.get('response'),
                        query_text,
                        provider
                    )
                    if analysis:
                        if query_results[query_id]["analysis"] is None:
                            query_results[query_id]["analysis"] = {}
                        query_results[query_id]["analysis"][provider] = analysis
                        
                        # Emit analysis event
                        socketio.emit('analysis_complete', {
                            'query_id': query_id,
                            'provider': provider,
                            'analysis': analysis
                        }, room=f"query_{query_id}")
        
        # Update status
        query_results[query_id]["status"] = "completed"
        
        # Emit completion event
        socketio.emit('query_complete', {
            'query_id': query_id,
            'results': query_results[query_id]
        }, room=f"query_{query_id}")
        
    except Exception as e:
        print(f"Error processing query: {e}")
        query_results[query_id]["status"] = "error"
        query_results[query_id]["error"] = str(e)
        
        socketio.emit('query_error', {
            'query_id': query_id,
            'error': str(e)
        }, room=f"query_{query_id}")

@app.route('/api/results/<query_id>', methods=['GET'])
def get_results(query_id):
    """Get results for a specific query"""
    if query_id not in query_results:
        return jsonify({"error": "Query not found"}), 404
    
    return jsonify(query_results[query_id])

@app.route('/api/analysis/<query_id>', methods=['GET'])
def get_analysis(query_id):
    """Get AISEO analysis for a specific query"""
    if query_id not in query_results:
        return jsonify({"error": "Query not found"}), 404
    
    analysis = query_results[query_id].get("analysis")
    if not analysis:
        return jsonify({"error": "No analysis available"}), 404
    
    return jsonify({
        "query_id": query_id,
        "query": query_results[query_id]["query"],
        "analysis": analysis
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get query history"""
    # Return last 20 queries
    history = sorted(
        query_results.values(),
        key=lambda x: x['timestamp'],
        reverse=True
    )[:20]
    
    return jsonify({"queries": history})

@app.route('/api/export/<query_id>', methods=['GET'])
def export_results(query_id):
    """Export results for a specific query"""
    if query_id not in query_results:
        return jsonify({"error": "Query not found"}), 404
    
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify(query_results[query_id])
    elif format_type == 'csv':
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Provider', 'Model', 'Response', 'Success'])
        
        # Write data
        for provider, result in query_results[query_id]["results"].items():
            writer.writerow([
                provider,
                result.get('model', 'N/A'),
                result.get('response', result.get('error', 'N/A')),
                result.get('success', False)
            ])
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-disposition": f"attachment; filename=results_{query_id}.csv"}
        )
    else:
        return jsonify({"error": "Invalid format"}), 400

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to AISEO backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_query')
def handle_join_query(data):
    """Join a query room for real-time updates"""
    query_id = data.get('query_id')
    if query_id:
        from flask_socketio import join_room
        room = f"query_{query_id}"
        join_room(room)
        emit('joined', {'room': room})

@socketio.on('leave_query')
def handle_leave_query(data):
    """Leave a query room"""
    query_id = data.get('query_id')
    if query_id:
        from flask_socketio import leave_room
        room = f"query_{query_id}"
        leave_room(room)
        emit('left', {'room': room})

if __name__ == '__main__':
    print("Starting AISEO Backend API Server...")
    print("Server will be available at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)