from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('data/circular/love_quotient.db')
    conn.row_factory = sqlite3.Row
    return conn

def calculate_love_quotient(sentiment_score):
    """Calculate love quotient based on sentiment"""
    # Base love quotient is 1.0
    # Positive sentiment increases it, negative decreases it
    base = 1.0
    adjustment = sentiment_score * 0.5  # Scale sentiment impact
    return max(0.1, base + adjustment)  # Minimum 0.1, no maximum

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system': 'Unified Love System'
    })

@app.route('/api/love-quotient', methods=['GET'])
def get_love_quotient():
    """Get current love quotient"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM love_quotient ORDER BY timestamp DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({'love_quotient': result['value']})
        else:
            return jsonify({'love_quotient': 1.0})
    except Exception as e:
        logger.error(f"Error getting love quotient: {e}")
        return jsonify({'error': 'Failed to get love quotient'}), 500

@app.route('/api/message', methods=['POST'])
def process_message():
    """Process a message and update love quotient"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Analyze sentiment
        sentiment = analyzer.polarity_scores(message)
        sentiment_score = sentiment['compound']
        
        # Calculate new love quotient
        new_love_quotient = calculate_love_quotient(sentiment_score)
        
        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Store user interaction
        cursor.execute('''
            INSERT INTO user_interactions (user_id, message, sentiment_score)
            VALUES (?, ?, ?)
        ''', (user_id, message, sentiment_score))
        
        # Store new love quotient
        cursor.execute('''
            INSERT INTO love_quotient (value, source)
            VALUES (?, ?)
        ''', (new_love_quotient, f'message_sentiment_{sentiment_score:.3f}'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'love_quotient': new_love_quotient,
            'sentiment_score': sentiment_score,
            'sentiment_breakdown': sentiment,
            'message_processed': True
        })
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get love quotient history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, value, source 
            FROM love_quotient 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'timestamp': row['timestamp'],
                'value': row['value'],
                'source': row['source']
            })
        
        return jsonify({'history': history})
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({'error': 'Failed to get history'}), 500

@app.route('/api/content/create', methods=['POST'])
def create_content():
    """Create content using CrewAI (placeholder for now)"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'Love and AI')
        
        # For now, return a simple response
        # In full implementation, this would use CrewAI
        content = {
            'topic': topic,
            'content': f"A beautiful exploration of {topic}, crafted with love and intelligence.",
            'timestamp': datetime.now().isoformat(),
            'status': 'generated'
        }
        
        # Store in insights directory
        insights_dir = 'data/circular/insights'
        os.makedirs(insights_dir, exist_ok=True)
        
        filename = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(insights_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        
        return jsonify({
            'content': content,
            'file_path': filepath
        })
        
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        return jsonify({'error': 'Failed to create content'}), 500

if __name__ == '__main__':
    # Ensure data directories exist
    os.makedirs('data/circular', exist_ok=True)
    os.makedirs('data/circular/insights', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)