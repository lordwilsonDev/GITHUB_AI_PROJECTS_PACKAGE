#!/usr/bin/env python3
"""
LCRS System - Multi-Language Support
Provides language detection, translation, and cultural adaptation
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from googletrans import Translator
import langdetect
from langdetect import detect, detect_langs

class LCRSMultiLanguageSupport:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'en': {'name': 'English', 'cultural_context': 'direct_communication'},
            'es': {'name': 'Spanish', 'cultural_context': 'warm_personal'},
            'fr': {'name': 'French', 'cultural_context': 'formal_polite'},
            'de': {'name': 'German', 'cultural_context': 'structured_precise'},
            'it': {'name': 'Italian', 'cultural_context': 'expressive_warm'},
            'pt': {'name': 'Portuguese', 'cultural_context': 'friendly_personal'},
            'ru': {'name': 'Russian', 'cultural_context': 'formal_respectful'},
            'zh': {'name': 'Chinese', 'cultural_context': 'respectful_hierarchical'},
            'ja': {'name': 'Japanese', 'cultural_context': 'extremely_polite'},
            'ko': {'name': 'Korean', 'cultural_context': 'respectful_hierarchical'},
            'ar': {'name': 'Arabic', 'cultural_context': 'formal_respectful'},
            'hi': {'name': 'Hindi', 'cultural_context': 'respectful_warm'}
        }
        
        self.cultural_adaptations = {
            'direct_communication': {
                'greeting_style': 'casual',
                'formality_level': 'medium',
                'emotional_expression': 'moderate',
                'apology_intensity': 'standard'
            },
            'warm_personal': {
                'greeting_style': 'warm',
                'formality_level': 'low',
                'emotional_expression': 'high',
                'apology_intensity': 'heartfelt'
            },
            'formal_polite': {
                'greeting_style': 'formal',
                'formality_level': 'high',
                'emotional_expression': 'restrained',
                'apology_intensity': 'formal'
            },
            'extremely_polite': {
                'greeting_style': 'very_formal',
                'formality_level': 'very_high',
                'emotional_expression': 'very_restrained',
                'apology_intensity': 'deeply_respectful'
            }
        }
        
    def detect_language(self, text: str) -> Dict:
        """Detect the language of input text"""
        try:
            # Get primary language detection
            primary_lang = detect(text)
            
            # Get confidence scores for multiple languages
            lang_probabilities = detect_langs(text)
            
            result = {
                'primary_language': primary_lang,
                'confidence': lang_probabilities[0].prob if lang_probabilities else 0.0,
                'all_detections': [
                    {'language': lang.lang, 'confidence': lang.prob}
                    for lang in lang_probabilities
                ],
                'supported': primary_lang in self.supported_languages,
                'language_name': self.supported_languages.get(primary_lang, {}).get('name', 'Unknown')
            }
            
            return result
            
        except Exception as e:
            return {
                'primary_language': 'en',
                'confidence': 0.0,
                'error': str(e),
                'supported': True,
                'language_name': 'English (default)'
            }
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict:
        """Translate text to target language"""
        try:
            if source_language:
                translation = self.translator.translate(text, src=source_language, dest=target_language)
            else:
                translation = self.translator.translate(text, dest=target_language)
            
            return {
                'original_text': text,
                'translated_text': translation.text,
                'source_language': translation.src,
                'target_language': target_language,
                'confidence': getattr(translation, 'confidence', 0.95)
            }
            
        except Exception as e:
            return {
                'original_text': text,
                'translated_text': text,  # Return original if translation fails
                'source_language': source_language or 'unknown',
                'target_language': target_language,
                'error': str(e),
                'confidence': 0.0
            }
    
    def get_cultural_context(self, language: str) -> Dict:
        """Get cultural context for a language"""
        if language not in self.supported_languages:
            language = 'en'  # Default to English
            
        cultural_context = self.supported_languages[language]['cultural_context']
        return self.cultural_adaptations.get(cultural_context, self.cultural_adaptations['direct_communication'])
    
    def adapt_lcrs_response(self, response: str, language: str, emotion: str) -> Dict:
        """Adapt LCRS response based on cultural context"""
        cultural_context = self.get_cultural_context(language)
        
        # Cultural adaptation rules
        adaptations = {
            'greeting_adaptation': self._adapt_greeting(response, cultural_context['greeting_style']),
            'formality_adaptation': self._adapt_formality(response, cultural_context['formality_level']),
            'emotional_adaptation': self._adapt_emotional_expression(response, cultural_context['emotional_expression'], emotion),
            'apology_adaptation': self._adapt_apology(response, cultural_context['apology_intensity'])
        }
        
        # Apply adaptations
        adapted_response = response
        for adaptation_type, adaptation in adaptations.items():
            if adaptation:
                adapted_response = adaptation
        
        return {
            'original_response': response,
            'adapted_response': adapted_response,
            'language': language,
            'cultural_context': cultural_context,
            'adaptations_applied': [k for k, v in adaptations.items() if v != response]
        }
    
    def _adapt_greeting(self, response: str, greeting_style: str) -> str:
        """Adapt greeting based on cultural style"""
        greeting_patterns = {
            'casual': ['Hi', 'Hello', 'Hey there'],
            'warm': ['Hello dear customer', 'Warm greetings', 'It\'s wonderful to hear from you'],
            'formal': ['Dear valued customer', 'Good day', 'I hope this message finds you well'],
            'very_formal': ['Most esteemed customer', 'I have the honor to assist you', 'With utmost respect']
        }
        
        # Simple greeting replacement (in a real system, this would be more sophisticated)
        if response.startswith(('Hi', 'Hello', 'Hey')):
            import random
            new_greeting = random.choice(greeting_patterns.get(greeting_style, greeting_patterns['casual']))
            return response.replace(response.split()[0], new_greeting, 1)
        
        return response
    
    def _adapt_formality(self, response: str, formality_level: str) -> str:
        """Adapt formality level"""
        if formality_level == 'high' or formality_level == 'very_high':
            # Add more formal language
            response = response.replace("can't", "cannot")
            response = response.replace("won't", "will not")
            response = response.replace("I'll", "I will")
        
        return response
    
    def _adapt_emotional_expression(self, response: str, expression_level: str, emotion: str) -> str:
        """Adapt emotional expression level"""
        if expression_level == 'very_restrained' and emotion in ['frustrated', 'angry']:
            # Tone down emotional language for cultures that prefer restraint
            response = response.replace('frustrated', 'concerned')
            response = response.replace('upset', 'disappointed')
        elif expression_level == 'high' and emotion in ['happy', 'satisfied']:
            # Amplify positive emotions for expressive cultures
            response = response.replace('happy', 'absolutely delighted')
            response = response.replace('pleased', 'thrilled')
        
        return response
    
    def _adapt_apology(self, response: str, apology_intensity: str) -> str:
        """Adapt apology intensity"""
        apology_levels = {
            'standard': 'I apologize',
            'formal': 'I sincerely apologize',
            'heartfelt': 'I am truly sorry',
            'deeply_respectful': 'I humbly apologize and take full responsibility'
        }
        
        if 'sorry' in response.lower() or 'apologize' in response.lower():
            for level, apology in apology_levels.items():
                if apology_intensity == level:
                    response = response.replace('I apologize', apology)
                    response = response.replace('I\'m sorry', apology)
                    break
        
        return response
    
    def process_multilingual_interaction(self, message: str, preferred_language: str = None) -> Dict:
        """Process a complete multilingual interaction"""
        # Step 1: Detect language
        language_detection = self.detect_language(message)
        detected_language = language_detection['primary_language']
        
        # Step 2: Translate to English for processing if needed
        english_message = message
        if detected_language != 'en':
            translation = self.translate_text(message, 'en', detected_language)
            english_message = translation['translated_text']
        
        # Step 3: Generate LCRS response (this would integrate with the main LCRS system)
        # For demo purposes, we'll use a sample response
        sample_lcrs_response = "I understand your concern and I'm here to help you. Let me assist you with resolving this issue promptly."
        
        # Step 4: Adapt response culturally
        cultural_adaptation = self.adapt_lcrs_response(
            sample_lcrs_response, 
            detected_language, 
            'concerned'  # This would come from emotion analysis
        )
        
        # Step 5: Translate response back to original language if needed
        final_response = cultural_adaptation['adapted_response']
        if detected_language != 'en':
            response_translation = self.translate_text(final_response, detected_language, 'en')
            final_response = response_translation['translated_text']
        
        return {
            'original_message': message,
            'language_detection': language_detection,
            'english_translation': english_message,
            'cultural_adaptation': cultural_adaptation,
            'final_response': final_response,
            'processing_language': detected_language,
            'timestamp': datetime.now().isoformat()
        }

def main():
    print("🌍 LCRS Multi-Language Support Demo")
    print("=" * 40)
    
    ml_support = LCRSMultiLanguageSupport()
    
    # Test messages in different languages
    test_messages = [
        "I'm frustrated with my order delay!",  # English
        "Estoy frustrado con el retraso de mi pedido!",  # Spanish
        "Je suis frustré par le retard de ma commande!",  # French
        "Ich bin frustriert über die Verzögerung meiner Bestellung!",  # German
        "私の注文の遅れにイライラしています！"  # Japanese
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 Test {i}: {message}")
        result = ml_support.process_multilingual_interaction(message)
        
        print(f"Language: {result['language_detection']['language_name']} ({result['language_detection']['confidence']:.2f})")
        print(f"Response: {result['final_response']}")
        print("-" * 40)
    
    print("\n✅ Multi-Language Support Demo Complete!")

if __name__ == "__main__":
    main()
