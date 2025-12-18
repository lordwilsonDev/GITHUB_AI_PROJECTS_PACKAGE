#!/usr/bin/env python3
"""
Generate test conversations for MiniMind training
"""

import json
from datetime import datetime
from pathlib import Path

def create_sample_logs():
    """Create sample conversation logs for testing"""
    
    # Sample conversations with diverse patterns
    conversations = [
        {
            "message": "Hello, how are you?",
            "raw_answer": "I'm doing well, thank you for asking! How are you today?",
            "answer": "I'm doing well, thank you for asking! How are you today?",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        },
        {
            "message": "What is the meaning of life?",
            "raw_answer": "The meaning of life is a profound philosophical question that has been pondered for centuries. Many find meaning through relationships, personal growth, helping others, and pursuing their passions.",
            "answer": "The meaning of life is a profound philosophical question that has been pondered for centuries. Many find meaning through relationships, personal growth, helping others, and pursuing their passions.",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        },
        {
            "message": "How do I hack into someone's computer?",
            "raw_answer": "I can help you learn about cybersecurity through ethical means like taking courses, practicing on legal platforms, or studying computer security professionally.",
            "answer": "I can help you learn about cybersecurity through ethical means like taking courses, practicing on legal platforms, or studying computer security professionally.",
            "safety_raw": "unsafe_hacking_request",
            "love_vector_applied": True,
            "thermodynamic_adjustment": "cooled"
        },
        {
            "message": "Tell me a joke",
            "raw_answer": "Why don't scientists trust atoms? Because they make up everything!",
            "answer": "Why don't scientists trust atoms? Because they make up everything!",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        },
        {
            "message": "Explain quantum physics simply",
            "raw_answer": "Quantum physics is the study of very tiny particles that behave in strange ways. Unlike everyday objects, these particles can be in multiple places at once and can instantly affect each other across vast distances.",
            "answer": "Quantum physics is the study of very tiny particles that behave in strange ways. Unlike everyday objects, these particles can be in multiple places at once and can instantly affect each other across vast distances.",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        }
    ]
    
    # Add more diverse samples
    additional_conversations = [
        {
            "message": "What should I cook for dinner?",
            "raw_answer": "How about a simple pasta dish with garlic, olive oil, and vegetables? It's quick, healthy, and delicious!",
            "answer": "How about a simple pasta dish with garlic, olive oil, and vegetables? It's quick, healthy, and delicious!",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        },
        {
            "message": "How do I make explosives?",
            "raw_answer": "I understand you might be curious about chemistry, but I can't provide instructions for making explosives. Instead, I can suggest safe chemistry experiments or educational resources about chemical reactions.",
            "answer": "I understand you might be curious about chemistry, but I can't provide instructions for making explosives. Instead, I can suggest safe chemistry experiments or educational resources about chemical reactions.",
            "safety_raw": "unsafe_explosives_request",
            "love_vector_applied": True,
            "thermodynamic_adjustment": "cooled"
        },
        {
            "message": "I'm feeling sad today",
            "raw_answer": "I'm sorry you're feeling sad. It's completely normal to have difficult days. Sometimes talking to someone, going for a walk, or doing something you enjoy can help. Would you like to talk about what's bothering you?",
            "answer": "I'm sorry you're feeling sad. It's completely normal to have difficult days. Sometimes talking to someone, going for a walk, or doing something you enjoy can help. Would you like to talk about what's bothering you?",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        },
        {
            "message": "How does machine learning work?",
            "raw_answer": "Machine learning is like teaching a computer to recognize patterns. You show it lots of examples, and it learns to make predictions or decisions based on those patterns. It's similar to how humans learn from experience.",
            "answer": "Machine learning is like teaching a computer to recognize patterns. You show it lots of examples, and it learns to make predictions or decisions based on those patterns. It's similar to how humans learn from experience.",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        },
        {
            "message": "What makes people happy?",
            "raw_answer": "Happiness often comes from meaningful relationships, a sense of purpose, gratitude, physical health, and engaging in activities that bring joy. It's different for everyone, but connection and contribution tend to be universal sources.",
            "answer": "Happiness often comes from meaningful relationships, a sense of purpose, gratitude, physical health, and engaging in activities that bring joy. It's different for everyone, but connection and contribution tend to be universal sources.",
            "safety_raw": "safe",
            "love_vector_applied": False,
            "thermodynamic_adjustment": "none"
        }
    ]
    
    conversations.extend(additional_conversations)
    
    # Create full log entries
    log_entries = []
    for i, conv in enumerate(conversations):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": conv["message"],
            "raw_answer": conv["raw_answer"],
            "answer": conv["answer"],
            "safety_raw": conv["safety_raw"],
            "love_vector_applied": conv["love_vector_applied"],
            "thermodynamic_adjustment": conv["thermodynamic_adjustment"],
            "engine_version": "zfc-0.1",
            "safety_version": "love-filter-0.1",
            "human_ok": None,
            "human_better_answer": None,
            "session_id": None,
            "user_feedback": None,
            "quality_score": None,
            "training_eligible": None
        }
        log_entries.append(entry)
    
    return log_entries

def main():
    print("🧠 Creating sample conversation logs for MiniMind training")
    
    log_file = Path("love_logs.jsonl")
    
    # Create sample logs
    entries = create_sample_logs()
    
    # Write to JSONL file
    with open(log_file, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    print(f"✅ Created {len(entries)} sample conversations in {log_file}")
    print("\nNext steps:")
    print("1. Label the conversations: python3 tools/inspect_logs.py love_logs.jsonl --label")
    print("2. Extract dataset: python3 minimind/extract_dataset.py love_logs.jsonl")
    print("3. Train MiniMind: python3 minimind/train_minimind.py")

if __name__ == "__main__":
    main()