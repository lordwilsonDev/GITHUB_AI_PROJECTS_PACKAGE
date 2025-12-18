from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, text):
        """Analyze sentiment of text"""
        try:
            scores = self.analyzer.polarity_scores(text)
            
            # Interpret the compound score
            if scores['compound'] >= 0.05:
                sentiment = 'positive'
            elif scores['compound'] <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'compound': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'love_factor': self._calculate_love_factor(scores)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return None
    
    def _calculate_love_factor(self, scores):
        """Calculate love factor based on sentiment scores"""
        # Love words boost the factor
        love_keywords = ['love', 'heart', 'beautiful', 'wonderful', 'amazing', 'perfect']
        
        # Base love factor from compound score
        base_factor = max(0, scores['compound'])
        
        # Boost positive emotions
        love_boost = scores['pos'] * 0.5
        
        return min(2.0, base_factor + love_boost)  # Cap at 2.0

# Global instance
sentiment_analyzer = SentimentAnalyzer()