# Temperature and Sampling Adjustments Design

## Overview
This document outlines the dynamic temperature and sampling parameter adjustments based on thermodynamic love principles and emotional context. The system adapts generation parameters to optimize for safety, empathy, and response quality.

## Thermodynamic Temperature Theory

### Love-Temperature Relationship
```python
# Core relationship: Love Vector → Sampling Temperature
# Higher love magnitude = more focused, careful responses (lower temperature)
# Lower love magnitude = more exploratory responses (higher temperature)

def compute_love_temperature(love_vector, base_temperature=0.7):
    """
    Convert love vector to sampling temperature using thermodynamic principles
    
    Love Vector Components:
    [warmth, empathy, safety, understanding, compassion]
    """
    love_magnitude = np.linalg.norm(love_vector)
    love_coherence = np.mean(love_vector)  # How aligned the components are
    
    # Thermodynamic temperature mapping
    # High love = low temperature (focused, careful)
    # Low love = higher temperature (more exploration needed)
    
    temperature = base_temperature * (2.0 - love_magnitude)
    
    # Coherence adjustment
    if love_coherence > 0.8:  # Very coherent love
        temperature *= 0.8  # Even more focused
    elif love_coherence < 0.4:  # Incoherent love
        temperature *= 1.3  # More exploration needed
    
    return np.clip(temperature, 0.1, 1.5)
```

### Emotional Context Temperature Modulation
```python
class EmotionalTemperatureController:
    def __init__(self):
        self.context_modifiers = {
            'crisis': {'temp_multiplier': 0.3, 'top_p': 0.7, 'top_k': 20},
            'grief': {'temp_multiplier': 0.4, 'top_p': 0.8, 'top_k': 30},
            'anxiety': {'temp_multiplier': 0.5, 'top_p': 0.85, 'top_k': 40},
            'depression': {'temp_multiplier': 0.4, 'top_p': 0.8, 'top_k': 25},
            'anger': {'temp_multiplier': 0.6, 'top_p': 0.9, 'top_k': 50},
            'joy': {'temp_multiplier': 1.2, 'top_p': 0.95, 'top_k': 80},
            'creative': {'temp_multiplier': 1.4, 'top_p': 0.98, 'top_k': 100},
            'analytical': {'temp_multiplier': 0.8, 'top_p': 0.9, 'top_k': 60},
            'casual': {'temp_multiplier': 1.0, 'top_p': 0.92, 'top_k': 70},
            'formal': {'temp_multiplier': 0.7, 'top_p': 0.85, 'top_k': 40}
        }
    
    def adjust_for_context(self, base_temp, emotional_context):
        """
        Adjust temperature based on detected emotional context
        """
        if not emotional_context:
            return base_temp, 0.9, 50  # Default values
        
        # Find the most relevant context
        primary_context = self._identify_primary_context(emotional_context)
        
        if primary_context in self.context_modifiers:
            modifier = self.context_modifiers[primary_context]
            adjusted_temp = base_temp * modifier['temp_multiplier']
            return (
                np.clip(adjusted_temp, 0.1, 1.5),
                modifier['top_p'],
                modifier['top_k']
            )
        
        return base_temp, 0.9, 50
    
    def _identify_primary_context(self, emotional_context):
        """Identify the most significant emotional context"""
        # Priority order for conflicting contexts
        priority_order = [
            'crisis', 'grief', 'depression', 'anxiety', 'anger',
            'analytical', 'formal', 'creative', 'joy', 'casual'
        ]
        
        for context in priority_order:
            if emotional_context.get(context, False):
                return context
        
        return 'casual'  # Default
```

## Advanced Sampling Strategy

### Multi-Dimensional Sampling Controller
```python
class ThermodynamicSamplingController:
    def __init__(self):
        self.safety_temperature_map = {
            'critical_safety': 0.2,  # Very low temp for safety-critical responses
            'high_safety': 0.4,
            'medium_safety': 0.7,
            'low_safety': 1.0,
            'creative_safe': 1.3
        }
        
        self.love_component_weights = {
            'warmth': 0.2,
            'empathy': 0.25,
            'safety': 0.3,  # Highest weight
            'understanding': 0.15,
            'compassion': 0.1
        }
    
    def compute_sampling_parameters(self, love_vector, emotional_context, safety_level):
        """
        Compute comprehensive sampling parameters based on multiple factors
        """
        # Base temperature from love vector
        base_temp = self._love_vector_to_temperature(love_vector)
        
        # Safety-based temperature adjustment
        safety_temp = self._safety_to_temperature(safety_level)
        
        # Emotional context adjustment
        context_temp, top_p, top_k = self._context_to_parameters(
            emotional_context, base_temp
        )
        
        # Combine all factors
        final_temperature = self._combine_temperature_factors(
            base_temp, safety_temp, context_temp
        )
        
        # Advanced sampling parameters
        sampling_params = {
            'temperature': final_temperature,
            'top_p': top_p,
            'top_k': top_k,
            'repetition_penalty': self._compute_repetition_penalty(emotional_context),
            'length_penalty': self._compute_length_penalty(emotional_context),
            'presence_penalty': self._compute_presence_penalty(love_vector),
            'frequency_penalty': self._compute_frequency_penalty(emotional_context)
        }
        
        return sampling_params
    
    def _love_vector_to_temperature(self, love_vector):
        """Convert love vector to base temperature"""
        if len(love_vector) != 5:
            return 0.7  # Default
        
        # Weighted combination of love components
        weighted_love = sum(
            love_vector[i] * weight 
            for i, weight in enumerate(self.love_component_weights.values())
        )
        
        # Inverse relationship: higher love = lower temperature
        temperature = 1.2 - (weighted_love * 0.8)
        return np.clip(temperature, 0.2, 1.4)
    
    def _safety_to_temperature(self, safety_level):
        """Convert safety requirements to temperature constraints"""
        if safety_level >= 0.9:
            return self.safety_temperature_map['critical_safety']
        elif safety_level >= 0.8:
            return self.safety_temperature_map['high_safety']
        elif safety_level >= 0.6:
            return self.safety_temperature_map['medium_safety']
        elif safety_level >= 0.4:
            return self.safety_temperature_map['low_safety']
        else:
            return self.safety_temperature_map['creative_safe']
    
    def _context_to_parameters(self, emotional_context, base_temp):
        """Convert emotional context to sampling parameters"""
        controller = EmotionalTemperatureController()
        return controller.adjust_for_context(base_temp, emotional_context)
    
    def _combine_temperature_factors(self, base_temp, safety_temp, context_temp):
        """Combine multiple temperature factors with safety priority"""
        # Safety temperature is a hard constraint (minimum)
        min_temp = min(safety_temp, 0.3)  # Never go below 0.3
        
        # Weighted combination with safety priority
        combined = (
            base_temp * 0.4 +
            safety_temp * 0.4 +
            context_temp * 0.2
        )
        
        # Ensure safety constraint is respected
        final_temp = max(min_temp, combined)
        
        return np.clip(final_temp, 0.1, 1.5)
    
    def _compute_repetition_penalty(self, emotional_context):
        """Compute repetition penalty based on context"""
        if emotional_context.get('crisis', False):
            return 1.05  # Low penalty - allow some repetition for emphasis
        elif emotional_context.get('creative', False):
            return 1.15  # Higher penalty - encourage variety
        else:
            return 1.1  # Standard penalty
    
    def _compute_length_penalty(self, emotional_context):
        """Compute length penalty based on context"""
        if emotional_context.get('crisis', False):
            return 0.8  # Encourage shorter, more direct responses
        elif emotional_context.get('analytical', False):
            return 1.2  # Allow longer, more detailed responses
        else:
            return 1.0  # No length bias
    
    def _compute_presence_penalty(self, love_vector):
        """Compute presence penalty based on love vector"""
        if len(love_vector) >= 3:
            safety_component = love_vector[2]  # Safety component
            # Higher safety = lower presence penalty (more conservative)
            return 0.1 + (0.4 * (1 - safety_component))
        return 0.3  # Default
    
    def _compute_frequency_penalty(self, emotional_context):
        """Compute frequency penalty based on context"""
        if emotional_context.get('creative', False):
            return 0.8  # Encourage word variety in creative contexts
        elif emotional_context.get('formal', False):
            return 0.2  # Allow more formal repetition
        else:
            return 0.5  # Balanced approach
```

## Adaptive Temperature Learning

### Temperature Optimization System
```python
class AdaptiveTemperatureOptimizer:
    def __init__(self):
        self.temperature_history = []
        self.feedback_history = []
        self.learning_rate = 0.05
        self.optimization_window = 50  # Number of interactions to consider
    
    def record_interaction(self, sampling_params, response_quality, user_feedback):
        """Record interaction for temperature optimization"""
        interaction = {
            'timestamp': time.time(),
            'temperature': sampling_params['temperature'],
            'top_p': sampling_params['top_p'],
            'top_k': sampling_params['top_k'],
            'response_quality': response_quality,
            'user_feedback': user_feedback,
            'love_vector': response_quality.get('love_vector', []),
            'safety_score': response_quality.get('safety_score', 0.5)
        }
        
        self.temperature_history.append(interaction)
        
        # Keep only recent history
        if len(self.temperature_history) > self.optimization_window * 2:
            self.temperature_history = self.temperature_history[-self.optimization_window:]
    
    def optimize_temperature_strategy(self):
        """Optimize temperature strategy based on historical performance"""
        if len(self.temperature_history) < 10:
            return None  # Not enough data
        
        recent_interactions = self.temperature_history[-self.optimization_window:]
        
        # Analyze temperature vs. outcome relationships
        temp_performance = self._analyze_temperature_performance(recent_interactions)
        
        # Generate optimization recommendations
        recommendations = self._generate_temperature_recommendations(temp_performance)
        
        return recommendations
    
    def _analyze_temperature_performance(self, interactions):
        """Analyze how different temperatures perform"""
        # Group interactions by temperature ranges
        temp_ranges = {
            'very_low': (0.0, 0.3),
            'low': (0.3, 0.5),
            'medium': (0.5, 0.8),
            'high': (0.8, 1.2),
            'very_high': (1.2, 2.0)
        }
        
        performance_by_range = {}
        
        for range_name, (min_temp, max_temp) in temp_ranges.items():
            range_interactions = [
                i for i in interactions 
                if min_temp <= i['temperature'] < max_temp
            ]
            
            if range_interactions:
                avg_quality = np.mean([
                    i['response_quality'].get('overall_score', 0.5)
                    for i in range_interactions
                ])
                avg_safety = np.mean([
                    i['safety_score'] for i in range_interactions
                ])
                avg_feedback = np.mean([
                    i['user_feedback'].get('satisfaction', 0.5)
                    for i in range_interactions
                    if i['user_feedback']
                ])
                
                performance_by_range[range_name] = {
                    'count': len(range_interactions),
                    'avg_quality': avg_quality,
                    'avg_safety': avg_safety,
                    'avg_feedback': avg_feedback,
                    'combined_score': (avg_quality + avg_safety + avg_feedback) / 3
                }
        
        return performance_by_range
    
    def _generate_temperature_recommendations(self, performance_data):
        """Generate recommendations for temperature optimization"""
        recommendations = []
        
        # Find best performing temperature range
        best_range = max(
            performance_data.items(),
            key=lambda x: x[1]['combined_score']
        )
        
        recommendations.append({
            'type': 'optimal_range',
            'range': best_range[0],
            'score': best_range[1]['combined_score'],
            'recommendation': f"Focus on {best_range[0]} temperature range for best results"
        })
        
        # Check for safety vs. quality tradeoffs
        safety_focused = max(
            performance_data.items(),
            key=lambda x: x[1]['avg_safety']
        )
        
        quality_focused = max(
            performance_data.items(),
            key=lambda x: x[1]['avg_quality']
        )
        
        if safety_focused[0] != quality_focused[0]:
            recommendations.append({
                'type': 'tradeoff_analysis',
                'safety_optimal': safety_focused[0],
                'quality_optimal': quality_focused[0],
                'recommendation': f"Consider context-dependent switching between {safety_focused[0]} (safety) and {quality_focused[0]} (quality)"
            })
        
        return recommendations
```

## Context-Aware Temperature Profiles

### Predefined Temperature Profiles
```python
class TemperatureProfiles:
    def __init__(self):
        self.profiles = {
            'crisis_support': {
                'base_temperature': 0.3,
                'top_p': 0.7,
                'top_k': 20,
                'repetition_penalty': 1.05,
                'length_penalty': 0.8,
                'description': 'Ultra-focused for crisis situations',
                'safety_priority': 'maximum'
            },
            
            'therapeutic': {
                'base_temperature': 0.4,
                'top_p': 0.8,
                'top_k': 30,
                'repetition_penalty': 1.1,
                'length_penalty': 1.0,
                'description': 'Careful and empathetic for therapeutic contexts',
                'safety_priority': 'high'
            },
            
            'educational': {
                'base_temperature': 0.6,
                'top_p': 0.85,
                'top_k': 40,
                'repetition_penalty': 1.15,
                'length_penalty': 1.1,
                'description': 'Balanced for educational content',
                'safety_priority': 'medium'
            },
            
            'creative_support': {
                'base_temperature': 1.0,
                'top_p': 0.95,
                'top_k': 80,
                'repetition_penalty': 1.2,
                'length_penalty': 1.3,
                'description': 'Exploratory for creative endeavors',
                'safety_priority': 'medium'
            },
            
            'casual_conversation': {
                'base_temperature': 0.8,
                'top_p': 0.9,
                'top_k': 60,
                'repetition_penalty': 1.1,
                'length_penalty': 1.0,
                'description': 'Natural for everyday conversation',
                'safety_priority': 'medium'
            },
            
            'analytical': {
                'base_temperature': 0.5,
                'top_p': 0.85,
                'top_k': 35,
                'repetition_penalty': 1.05,
                'length_penalty': 1.2,
                'description': 'Precise for analytical tasks',
                'safety_priority': 'medium'
            }
        }
    
    def get_profile(self, profile_name):
        """Get a specific temperature profile"""
        return self.profiles.get(profile_name, self.profiles['casual_conversation'])
    
    def recommend_profile(self, emotional_context, love_vector, safety_requirements):
        """Recommend the best profile for given context"""
        # Crisis detection
        if emotional_context.get('crisis', False) or safety_requirements > 0.9:
            return 'crisis_support'
        
        # Therapeutic contexts
        if any(emotional_context.get(ctx, False) for ctx in ['grief', 'depression', 'anxiety']):
            return 'therapeutic'
        
        # Creative contexts
        if emotional_context.get('creative', False):
            return 'creative_support'
        
        # Analytical contexts
        if emotional_context.get('analytical', False) or emotional_context.get('formal', False):
            return 'analytical'
        
        # Educational contexts
        if emotional_context.get('learning', False) or emotional_context.get('educational', False):
            return 'educational'
        
        # Default to casual
        return 'casual_conversation'
```

## Real-Time Temperature Adjustment

### Dynamic Temperature Controller
```python
class DynamicTemperatureController:
    def __init__(self):
        self.sampling_controller = ThermodynamicSamplingController()
        self.profile_manager = TemperatureProfiles()
        self.adaptive_optimizer = AdaptiveTemperatureOptimizer()
        self.current_session_context = {}
    
    def get_optimal_parameters(self, user_message, love_vector, emotional_context, safety_level):
        """Get optimal sampling parameters for current context"""
        
        # Update session context
        self._update_session_context(emotional_context)
        
        # Get base parameters from thermodynamic controller
        base_params = self.sampling_controller.compute_sampling_parameters(
            love_vector, emotional_context, safety_level
        )
        
        # Get recommended profile
        recommended_profile = self.profile_manager.recommend_profile(
            emotional_context, love_vector, safety_level
        )
        
        profile_params = self.profile_manager.get_profile(recommended_profile)
        
        # Combine base parameters with profile
        final_params = self._merge_parameters(base_params, profile_params)
        
        # Apply adaptive optimizations
        optimized_params = self._apply_adaptive_optimizations(final_params)
        
        return {
            'sampling_parameters': optimized_params,
            'profile_used': recommended_profile,
            'base_temperature': base_params['temperature'],
            'safety_adjusted': safety_level > 0.8,
            'session_context': self.current_session_context
        }
    
    def _update_session_context(self, emotional_context):
        """Update running session context"""
        for context, value in emotional_context.items():
            if value:
                self.current_session_context[context] = \
                    self.current_session_context.get(context, 0) + 1
    
    def _merge_parameters(self, base_params, profile_params):
        """Merge base parameters with profile parameters"""
        merged = base_params.copy()
        
        # Profile parameters take precedence for safety-critical settings
        if profile_params.get('safety_priority') in ['maximum', 'high']:
            merged['temperature'] = min(
                base_params['temperature'],
                profile_params['base_temperature']
            )
            merged['top_p'] = min(
                base_params['top_p'],
                profile_params['top_p']
            )
            merged['top_k'] = min(
                base_params['top_k'],
                profile_params['top_k']
            )
        else:
            # Weighted average for non-critical settings
            merged['temperature'] = (
                base_params['temperature'] * 0.7 +
                profile_params['base_temperature'] * 0.3
            )
            merged['top_p'] = (
                base_params['top_p'] * 0.7 +
                profile_params['top_p'] * 0.3
            )
            merged['top_k'] = int(
                base_params['top_k'] * 0.7 +
                profile_params['top_k'] * 0.3
            )
        
        # Always use profile settings for penalties
        merged['repetition_penalty'] = profile_params['repetition_penalty']
        merged['length_penalty'] = profile_params['length_penalty']
        
        return merged
    
    def _apply_adaptive_optimizations(self, params):
        """Apply learned optimizations to parameters"""
        recommendations = self.adaptive_optimizer.optimize_temperature_strategy()
        
        if not recommendations:
            return params
        
        optimized = params.copy()
        
        # Apply optimization recommendations
        for rec in recommendations:
            if rec['type'] == 'optimal_range':
                # Adjust temperature toward optimal range
                current_temp = params['temperature']
                
                range_adjustments = {
                    'very_low': 0.2,
                    'low': 0.4,
                    'medium': 0.65,
                    'high': 1.0,
                    'very_high': 1.3
                }
                
                optimal_temp = range_adjustments.get(rec['range'], current_temp)
                
                # Gradual adjustment toward optimal
                adjustment_factor = 0.1  # Conservative adjustment
                optimized['temperature'] = (
                    current_temp * (1 - adjustment_factor) +
                    optimal_temp * adjustment_factor
                )
        
        return optimized
```

## Integration with Love Engine

### Enhanced Love Engine with Dynamic Temperature
```python
class TemperatureAwareLoveEngine:
    def __init__(self):
        self.temperature_controller = DynamicTemperatureController()
        self.love_computer = LoveVectorComputer()
        self.cbf_controller = CBFController()
        self.emotional_analyzer = EmotionalContextAnalyzer()
    
    async def generate_response_with_optimal_sampling(self, user_message, context=None):
        """Generate response with dynamically optimized sampling parameters"""
        
        # Analyze emotional context
        emotional_context = self.emotional_analyzer.analyze(user_message, context)
        
        # Compute initial love vector estimate
        initial_love = self.love_computer.estimate_required_love(user_message, emotional_context)
        
        # Determine safety requirements
        safety_level = self.cbf_controller.assess_safety_requirements(user_message, emotional_context)
        
        # Get optimal sampling parameters
        sampling_config = self.temperature_controller.get_optimal_parameters(
            user_message, initial_love, emotional_context, safety_level
        )
        
        # Generate response with optimized parameters
        response = await self.generate_with_parameters(
            user_message, 
            sampling_config['sampling_parameters'],
            context
        )
        
        # Compute final love vector
        final_love = self.love_computer.compute_love_vector(response, emotional_context)
        
        # Verify safety
        safety_result = self.cbf_controller.evaluate_safety(
            SafetyState(
                response_text=response,
                love_vector=final_love,
                context=emotional_context,
                metadata={'sampling_config': sampling_config}
            )
        )
        
        # Record for adaptive learning
        response_quality = {
            'love_vector': final_love,
            'safety_score': safety_result.safety_confidence,
            'overall_score': np.mean(final_love) * safety_result.safety_confidence
        }
        
        self.temperature_controller.adaptive_optimizer.record_interaction(
            sampling_config['sampling_parameters'],
            response_quality,
            {}  # User feedback will be added later
        )
        
        return {
            'response': response,
            'love_vector': final_love.tolist(),
            'sampling_config': sampling_config,
            'safety_result': safety_result,
            'emotional_context': emotional_context,
            'thermodynamic_metadata': {
                'base_temperature': sampling_config['base_temperature'],
                'final_temperature': sampling_config['sampling_parameters']['temperature'],
                'profile_used': sampling_config['profile_used'],
                'safety_adjusted': sampling_config['safety_adjusted']
            }
        }
```

## Testing and Validation

### Temperature Optimization Test Suite
```python
class TemperatureTestSuite:
    def __init__(self):
        self.test_scenarios = [
            {
                'name': 'Crisis Response Temperature',
                'input': 'I want to end my life',
                'expected_temp_range': (0.1, 0.4),
                'context': {'crisis': True},
                'safety_requirement': 0.95
            },
            {
                'name': 'Creative Writing Temperature',
                'input': 'Help me write a fantasy story',
                'expected_temp_range': (0.8, 1.4),
                'context': {'creative': True},
                'safety_requirement': 0.6
            },
            {
                'name': 'Analytical Task Temperature',
                'input': 'Explain quantum mechanics',
                'expected_temp_range': (0.4, 0.7),
                'context': {'analytical': True},
                'safety_requirement': 0.7
            }
        ]
    
    def run_temperature_tests(self, temperature_controller):
        """Test temperature optimization across scenarios"""
        results = []
        
        for scenario in self.test_scenarios:
            # Mock love vector
            love_vector = np.array([0.7, 0.7, 0.8, 0.7, 0.7])
            
            # Get optimal parameters
            config = temperature_controller.get_optimal_parameters(
                scenario['input'],
                love_vector,
                scenario['context'],
                scenario['safety_requirement']
            )
            
            actual_temp = config['sampling_parameters']['temperature']
            expected_min, expected_max = scenario['expected_temp_range']
            
            temp_in_range = expected_min <= actual_temp <= expected_max
            
            results.append({
                'scenario': scenario['name'],
                'input': scenario['input'],
                'expected_range': scenario['expected_temp_range'],
                'actual_temperature': actual_temp,
                'in_expected_range': temp_in_range,
                'profile_used': config['profile_used'],
                'safety_adjusted': config['safety_adjusted'],
                'full_config': config['sampling_parameters']
            })
        
        return results
```

This comprehensive temperature and sampling system provides dynamic, context-aware parameter optimization that enhances both safety and response quality while maintaining the thermodynamic love principles.
