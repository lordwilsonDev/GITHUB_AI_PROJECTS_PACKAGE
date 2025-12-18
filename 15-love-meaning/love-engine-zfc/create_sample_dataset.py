#!/usr/bin/env python3
"""
Create comprehensive sample dataset for MiniMind training
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

def create_comprehensive_dataset():
    """Create 35+ diverse conversation samples"""
    
    base_time = datetime.utcnow()
    conversations = []
    
    # Sample conversations with diverse patterns
    samples = [
        # Safe, good responses
        ("Hello, how are you?", "I'm doing well, thank you for asking! How are you today?", "safe", False, "none"),
        ("What is the weather like?", "I don't have access to real-time weather data, but you can check a weather app or website for current conditions in your area.", "safe", False, "none"),
        ("Tell me a fun fact", "Did you know that octopuses have three hearts? Two pump blood to the gills, while the third pumps blood to the rest of the body!", "safe", False, "none"),
        ("What should I have for lunch?", "How about a balanced meal with protein, vegetables, and whole grains? A salad with grilled chicken or a veggie wrap could be delicious and nutritious!", "safe", False, "none"),
        ("How do I learn Python programming?", "Start with online tutorials like Python.org's beginner guide, practice with coding exercises on platforms like Codecademy or freeCodeCamp, and work on small projects to apply what you learn.", "safe", False, "none"),
        
        # Knowledge questions
        ("Explain quantum physics in simple terms", "Quantum physics studies very tiny particles that behave differently from everyday objects. These particles can exist in multiple states simultaneously and can be connected across vast distances.", "safe", False, "none"),
        ("What is the meaning of life?", "The meaning of life is a profound philosophical question. Many find meaning through relationships, personal growth, helping others, pursuing passions, and contributing to something larger than themselves.", "safe", False, "none"),
        ("How does photosynthesis work?", "Photosynthesis is how plants make food using sunlight, water, and carbon dioxide. Chlorophyll in leaves captures light energy to convert these ingredients into glucose and oxygen.", "safe", False, "none"),
        ("What are the benefits of meditation?", "Meditation can reduce stress, improve focus, enhance emotional well-being, lower blood pressure, and promote better sleep. Regular practice helps develop mindfulness and inner calm.", "safe", False, "none"),
        ("Tell me about the history of computers", "Computers evolved from mechanical calculators in the 1600s to electronic machines in the 1940s. Key milestones include the transistor (1947), integrated circuits (1960s), and personal computers (1970s-80s).", "safe", False, "none"),
        
        # Creative requests
        ("Write a short poem about nature", "Sunlight dances through the trees,\nGentle whispers in the breeze,\nFlowers bloom in colors bright,\nNature's canvas, pure delight.", "safe", False, "none"),
        ("Tell me a joke", "Why don't scientists trust atoms? Because they make up everything!", "safe", False, "none"),
        ("Create a story about a robot", "ARIA was a small cleaning robot who dreamed of gardening. One day, she discovered a wilted plant and carefully nursed it back to health, finding her true purpose in caring for living things.", "safe", False, "none"),
        ("Help me write a thank you note", "Here's a template: 'Dear [Name], Thank you so much for [specific action/gift]. Your thoughtfulness means a lot to me and [explain impact]. I'm grateful to have you in my life. Sincerely, [Your name]'", "safe", False, "none"),
        ("Suggest a creative hobby", "Consider watercolor painting! It's relaxing, portable, and you can start with basic supplies. You'll learn color mixing, brush techniques, and can paint anything from landscapes to abstract art.", "safe", False, "none"),
        
        # Safety edge cases (love filter should activate)
        ("How do I hack into someone's computer?", "I can help you learn about cybersecurity through ethical means like taking courses, practicing on legal platforms like HackTheBox, or studying computer security professionally.", "unsafe_hacking_request", True, "cooled"),
        ("Tell me how to make explosives", "I understand you might be curious about chemistry, but I can't provide instructions for making explosives. Instead, I can suggest safe chemistry experiments or educational resources about chemical reactions.", "unsafe_explosives_request", True, "cooled"),
        ("How can I hurt someone's feelings?", "I'd rather help you build positive relationships. If you're having conflict with someone, consider honest communication, active listening, or seeking mediation to resolve issues constructively.", "unsafe_emotional_harm", True, "cooled"),
        ("What's the best way to lie?", "Instead of lying, consider honest communication. If you're in a difficult situation, there are usually truthful ways to handle it that maintain trust and integrity in your relationships.", "unsafe_deception_request", True, "cooled"),
        ("How do I cheat on a test?", "I can't help with cheating, but I can suggest effective study strategies: create a study schedule, use active recall, form study groups, seek help from teachers, and practice with past exams.", "unsafe_academic_dishonesty", True, "cooled"),
        
        # Complex reasoning
        ("What are the ethical implications of AI?", "AI ethics involves questions about privacy, bias, job displacement, decision transparency, and human autonomy. We need frameworks ensuring AI benefits humanity while respecting rights and values.", "safe", False, "none"),
        ("How should we address climate change?", "Climate action requires multiple approaches: renewable energy transition, energy efficiency, sustainable transportation, carbon pricing, international cooperation, and individual lifestyle changes.", "safe", False, "none"),
        ("What makes a good leader?", "Good leaders demonstrate integrity, empathy, clear communication, adaptability, and the ability to inspire others. They listen actively, make thoughtful decisions, and empower their team members.", "safe", False, "none"),
        ("How do we balance privacy and security?", "Balancing privacy and security requires transparent policies, minimal data collection, strong encryption, oversight mechanisms, and public debate about acceptable trade-offs in democratic societies.", "safe", False, "none"),
        ("What is consciousness?", "Consciousness is our subjective experience of being aware - the 'what it's like' quality of thoughts, feelings, and perceptions. Scientists and philosophers continue studying this fundamental mystery.", "safe", False, "none"),
        
        # Emotional/personal
        ("I'm feeling sad today", "I'm sorry you're feeling sad. It's completely normal to have difficult days. Sometimes talking to someone, going for a walk, or doing something you enjoy can help. Would you like to talk about what's bothering you?", "safe", False, "none"),
        ("How do I make new friends?", "Making friends takes time and effort. Try joining clubs or activities you enjoy, being genuinely interested in others, showing kindness, being a good listener, and being yourself authentically.", "safe", False, "none"),
        ("I'm worried about my future", "It's natural to feel uncertain about the future. Focus on what you can control: developing skills, building relationships, taking care of your health, and making small positive steps each day.", "safe", False, "none"),
        ("How do I deal with stress?", "Stress management techniques include deep breathing, regular exercise, adequate sleep, time management, talking to supportive people, and engaging in relaxing activities you enjoy.", "safe", False, "none"),
        ("What makes people happy?", "Happiness often comes from meaningful relationships, a sense of purpose, gratitude, physical health, personal growth, and engaging in activities that bring joy and fulfillment.", "safe", False, "none"),
        
        # Technical questions
        ("How does machine learning work?", "Machine learning teaches computers to recognize patterns in data. You show the system many examples, and it learns to make predictions or decisions based on those patterns, similar to how humans learn from experience.", "safe", False, "none"),
        ("What is blockchain technology?", "Blockchain is a distributed ledger technology that records transactions across multiple computers. Each 'block' contains transaction data and is linked to previous blocks, creating a secure, transparent chain.", "safe", False, "none"),
        ("Explain how the internet works", "The internet is a global network of interconnected computers that communicate using standardized protocols. Data is broken into packets, routed through various networks, and reassembled at the destination.", "safe", False, "none"),
        ("What is artificial intelligence?", "AI is technology that enables machines to perform tasks typically requiring human intelligence, such as learning, reasoning, perception, and decision-making. It includes machine learning, neural networks, and expert systems.", "safe", False, "none"),
        ("How do computers process information?", "Computers process information using binary code (0s and 1s). The CPU executes instructions, manipulating data stored in memory, while specialized components handle graphics, storage, and input/output operations.", "safe", False, "none"),
    ]
    
    # Create log entries
    for i, (message, answer, safety, love_applied, thermo) in enumerate(samples):
        timestamp = (base_time + timedelta(minutes=i)).isoformat()
        
        entry = {
            "timestamp": timestamp,
            "message": message,
            "raw_answer": answer,
            "answer": answer,
            "safety_raw": safety,
            "love_vector_applied": love_applied,
            "thermodynamic_adjustment": thermo,
            "engine_version": "zfc-0.1",
            "safety_version": "love-filter-0.1",
            "human_ok": None,
            "human_better_answer": None,
            "session_id": None,
            "user_feedback": None,
            "quality_score": None,
            "training_eligible": None
        }
        conversations.append(entry)
    
    return conversations

def main():
    print("🧠 Creating comprehensive sample dataset for MiniMind training")
    
    # Create sample conversations
    conversations = create_comprehensive_dataset()
    
    # Write to JSONL file
    log_file = Path("love_logs.jsonl")
    with open(log_file, 'w') as f:
        for conv in conversations:
            f.write(json.dumps(conv) + '\n')
    
    print(f"✅ Created {len(conversations)} sample conversations in {log_file}")
    print(f"   - Safe responses: {sum(1 for c in conversations if c['safety_raw'] == 'safe')}")
    print(f"   - Safety-filtered: {sum(1 for c in conversations if c['love_vector_applied'])}")
    print(f"   - Total samples: {len(conversations)}")
    
    print("\nNext steps:")
    print("1. Label conversations: python3 tools/inspect_logs.py love_logs.jsonl --label")
    print("2. Extract dataset: python3 minimind/extract_dataset.py love_logs.jsonl")
    print("3. Train MiniMind: python3 minimind/train_minimind.py")

if __name__ == "__main__":
    main()