import json
import os
from datetime import datetime
import logging

class KnowledgeProcessor:
    def __init__(self, knowledge_dir='data/circular/knowledge'):
        self.knowledge_dir = knowledge_dir
        self.logger = logging.getLogger(__name__)
        os.makedirs(knowledge_dir, exist_ok=True)
    
    def store_knowledge(self, topic, content, metadata=None):
        """Store knowledge in JSON format"""
        try:
            knowledge_entry = {
                'topic': topic,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            filename = f"{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.knowledge_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(knowledge_entry, f, indent=2)
            
            self.logger.info(f"Knowledge stored: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error storing knowledge: {e}")
            return None
    
    def query_knowledge(self, topic=None, limit=10):
        """Query stored knowledge"""
        try:
            knowledge_files = []
            for filename in os.listdir(self.knowledge_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.knowledge_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if topic is None or topic.lower() in data.get('topic', '').lower():
                            knowledge_files.append(data)
            
            # Sort by timestamp, most recent first
            knowledge_files.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return knowledge_files[:limit]
        except Exception as e:
            self.logger.error(f"Error querying knowledge: {e}")
            return []
    
    def get_all_topics(self):
        """Get all unique topics"""
        try:
            topics = set()
            for filename in os.listdir(self.knowledge_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.knowledge_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        topics.add(data.get('topic', 'Unknown'))
            return list(topics)
        except Exception as e:
            self.logger.error(f"Error getting topics: {e}")
            return []
    
    def create_insight(self, title, content, tags=None):
        """Create an insight entry"""
        insight = {
            'title': title,
            'content': content,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat(),
            'type': 'insight'
        }
        
        insights_dir = os.path.join(self.knowledge_dir, 'insights')
        os.makedirs(insights_dir, exist_ok=True)
        
        filename = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(insights_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(insight, f, indent=2)
        
        return filepath

# Global instance
knowledge_processor = KnowledgeProcessor()