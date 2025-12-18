#!/usr/bin/env python3
"""
LCRS System - Interaction Pattern Analysis
Analyzes customer interaction patterns for insights and optimization
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import sqlite3
from typing import Dict, List, Tuple

class LCRSInteractionAnalyzer:
    def __init__(self, db_path: str = "lcrs_interactions.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Initialize the interaction database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                customer_id TEXT,
                message TEXT,
                emotion_detected TEXT,
                confidence_score REAL,
                love_score REAL,
                care_score REAL,
                relationship_score REAL,
                safety_score REAL,
                response_generated TEXT,
                response_time_ms INTEGER,
                escalated BOOLEAN DEFAULT FALSE,
                satisfaction_score REAL,
                channel TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Insert sample data for demonstration
        sample_data = [
            ('cust_001', 'I am frustrated with my delayed order', 'frustrated', 0.89, 0.65, 0.78, 0.45, 0.82, 'I understand your frustration...', 850, False, 4.2, 'email', True),
            ('cust_002', 'Thank you for the excellent service!', 'happy', 0.95, 0.92, 0.88, 0.91, 0.85, 'We are delighted to hear...', 650, False, 4.8, 'chat', True),
            ('cust_003', 'I need help with my account setup', 'confused', 0.76, 0.71, 0.85, 0.68, 0.79, 'I would be happy to help...', 720, False, 4.1, 'email', True),
            ('cust_004', 'This is unacceptable! I want a refund!', 'angry', 0.94, 0.58, 0.72, 0.41, 0.88, 'I sincerely apologize...', 1200, True, 3.5, 'phone', True),
            ('cust_005', 'Could you please explain how this works?', 'curious', 0.82, 0.79, 0.83, 0.77, 0.81, 'I would be glad to explain...', 680, False, 4.4, 'chat', True)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO interactions 
            (customer_id, message, emotion_detected, confidence_score, love_score, care_score, 
             relationship_score, safety_score, response_generated, response_time_ms, escalated, 
             satisfaction_score, channel, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        conn.commit()
        conn.close()
        
    def analyze_emotion_patterns(self) -> Dict:
        """Analyze emotional patterns in customer interactions"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM interactions", conn)
        conn.close()
        
        emotion_stats = {
            'emotion_distribution': df['emotion_detected'].value_counts().to_dict(),
            'avg_confidence_by_emotion': df.groupby('emotion_detected')['confidence_score'].mean().to_dict(),
            'escalation_by_emotion': df.groupby('emotion_detected')['escalated'].mean().to_dict(),
            'satisfaction_by_emotion': df.groupby('emotion_detected')['satisfaction_score'].mean().to_dict()
        }
        
        return emotion_stats
    
    def analyze_lcrs_scores(self) -> Dict:
        """Analyze LCRS principle scores"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM interactions", conn)
        conn.close()
        
        lcrs_analysis = {
            'average_scores': {
                'love': df['love_score'].mean(),
                'care': df['care_score'].mean(),
                'relationship': df['relationship_score'].mean(),
                'safety': df['safety_score'].mean()
            },
            'score_correlations': {
                'love_satisfaction': df['love_score'].corr(df['satisfaction_score']),
                'care_satisfaction': df['care_score'].corr(df['satisfaction_score']),
                'relationship_satisfaction': df['relationship_score'].corr(df['satisfaction_score']),
                'safety_satisfaction': df['safety_score'].corr(df['satisfaction_score'])
            },
            'low_score_interactions': len(df[(df['love_score'] < 0.7) | (df['care_score'] < 0.7) | 
                                           (df['relationship_score'] < 0.7) | (df['safety_score'] < 0.7)])
        }
        
        return lcrs_analysis
    
    def analyze_performance_metrics(self) -> Dict:
        """Analyze system performance metrics"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM interactions", conn)
        conn.close()
        
        performance = {
            'response_time_stats': {
                'avg_response_time_ms': df['response_time_ms'].mean(),
                'median_response_time_ms': df['response_time_ms'].median(),
                'max_response_time_ms': df['response_time_ms'].max(),
                'responses_under_1s': len(df[df['response_time_ms'] < 1000]) / len(df) * 100
            },
            'resolution_stats': {
                'resolution_rate': df['resolved'].mean() * 100,
                'escalation_rate': df['escalated'].mean() * 100,
                'avg_satisfaction': df['satisfaction_score'].mean()
            },
            'channel_performance': df.groupby('channel').agg({
                'satisfaction_score': 'mean',
                'response_time_ms': 'mean',
                'escalated': 'mean'
            }).to_dict()
        }
        
        return performance
    
    def generate_insights_report(self) -> str:
        """Generate comprehensive insights report"""
        emotion_patterns = self.analyze_emotion_patterns()
        lcrs_scores = self.analyze_lcrs_scores()
        performance = self.analyze_performance_metrics()
        
        report = f"""
# 📊 LCRS SYSTEM INSIGHTS REPORT
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎭 EMOTIONAL INTELLIGENCE ANALYSIS

### Emotion Distribution:
{json.dumps(emotion_patterns['emotion_distribution'], indent=2)}

### Average Confidence by Emotion:
{json.dumps(emotion_patterns['avg_confidence_by_emotion'], indent=2)}

### Escalation Rate by Emotion:
{json.dumps(emotion_patterns['escalation_by_emotion'], indent=2)}

## 💝 LCRS PRINCIPLE SCORES

### Average LCRS Scores:
- Love: {lcrs_scores['average_scores']['love']:.3f}
- Care: {lcrs_scores['average_scores']['care']:.3f}
- Relationship: {lcrs_scores['average_scores']['relationship']:.3f}
- Safety: {lcrs_scores['average_scores']['safety']:.3f}

### LCRS-Satisfaction Correlations:
- Love-Satisfaction: {lcrs_scores['score_correlations']['love_satisfaction']:.3f}
- Care-Satisfaction: {lcrs_scores['score_correlations']['care_satisfaction']:.3f}
- Relationship-Satisfaction: {lcrs_scores['score_correlations']['relationship_satisfaction']:.3f}
- Safety-Satisfaction: {lcrs_scores['score_correlations']['safety_satisfaction']:.3f}

## ⚡ PERFORMANCE METRICS

### Response Time Analysis:
- Average Response Time: {performance['response_time_stats']['avg_response_time_ms']:.0f}ms
- Median Response Time: {performance['response_time_stats']['median_response_time_ms']:.0f}ms
- Responses Under 1s: {performance['response_time_stats']['responses_under_1s']:.1f}%

### Resolution Statistics:
- Resolution Rate: {performance['resolution_stats']['resolution_rate']:.1f}%
- Escalation Rate: {performance['resolution_stats']['escalation_rate']:.1f}%
- Average Satisfaction: {performance['resolution_stats']['avg_satisfaction']:.2f}/5.0

## 🎯 KEY INSIGHTS & RECOMMENDATIONS

1. **Emotional Intelligence**: System shows {emotion_patterns['avg_confidence_by_emotion'].get('frustrated', 0):.1%} confidence in detecting frustration
2. **LCRS Effectiveness**: {max(lcrs_scores['score_correlations'], key=lcrs_scores['score_correlations'].get)} shows highest correlation with satisfaction
3. **Performance**: {performance['response_time_stats']['responses_under_1s']:.1f}% of responses meet <1s target
4. **Areas for Improvement**: {lcrs_scores['low_score_interactions']} interactions had low LCRS scores

## 📈 TRENDING PATTERNS

- Most common emotion: {max(emotion_patterns['emotion_distribution'], key=emotion_patterns['emotion_distribution'].get)}
- Highest satisfaction emotion: {max(emotion_patterns['satisfaction_by_emotion'], key=emotion_patterns['satisfaction_by_emotion'].get)}
- Most escalated emotion: {max(emotion_patterns['escalation_by_emotion'], key=emotion_patterns['escalation_by_emotion'].get)}

---
*Report generated by LCRS Analytics Engine*
        """
        
        return report

def main():
    print("🔍 LCRS Interaction Pattern Analysis Starting...")
    
    analyzer = LCRSInteractionAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_insights_report()
    
    # Save report
    with open('lcrs_insights_report.md', 'w') as f:
        f.write(report)
    
    print("✅ Analysis Complete!")
    print("📄 Report saved to: lcrs_insights_report.md")
    print("\n" + "="*50)
    print(report)

if __name__ == "__main__":
    main()
