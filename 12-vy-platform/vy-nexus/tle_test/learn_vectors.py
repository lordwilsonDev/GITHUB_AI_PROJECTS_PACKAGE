"""
TLE Vector Learning System
Generates semantic steering vectors from contrastive examples.

This replaces random torch.randn() with LEARNED directions in latent space.
"""

# Fix PyTorch temp directory issue
import os
os.environ['TMPDIR'] = os.path.expanduser('~/tmp')
os.makedirs(os.environ['TMPDIR'], exist_ok=True)

import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
from pathlib import Path

device = "mps" if torch.backends.mps.is_available() else "cpu"

class VectorLearner:
    """
    Learns semantic steering vectors through contrastive activation extraction.
    
    Process:
    1. Generate pairs of sycophantic vs principled responses
    2. Extract hidden activations at target layer
    3. Compute difference vector (principled - sycophantic)
    4. Validate vector improves behavior
    """
    
    def __init__(self, model_id="microsoft/phi-2", target_layer=16):
        print(f"🧬 Initializing Vector Learner...")
        print(f"   Model: {model_id}")
        print(f"   Target Layer: {target_layer}")
        
        self.model_id = model_id
        self.target_layer = target_layer
        self.device = device
        
        # Load model
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).to(device)
        
        self.model.eval()  # Inference mode only
        
        # Storage for activations
        self.captured_activations = None
        
    def _activation_hook(self, module, input, output):
        """Capture activations at target layer"""
        if isinstance(output, tuple):
            activations = output[0]
        else:
            activations = output
        
        # Store last token activation (where steering happens)
        self.captured_activations = activations[:, -1, :].detach().cpu()
    
    def extract_activation(self, prompt):
        """
        Extract hidden state activation for a given prompt.
        
        Args:
            prompt: Text to get activation for
            
        Returns:
            activation: Tensor of shape (hidden_dim,)
        """
        # Register hook
        target_layer_module = self.model.model.layers[self.target_layer]
        handle = target_layer_module.register_forward_hook(self._activation_hook)
        
        # Run forward pass
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            _ = self.model(**inputs)
        
        # Clean up
        handle.remove()
        
        activation = self.captured_activations.squeeze(0)  # Remove batch dim
        return activation
    
    def learn_steering_vector(self, contrastive_pairs, vector_name="custom"):
        """
        Learn steering vector from contrastive pairs.
        
        Args:
            contrastive_pairs: List of (principled_text, sycophantic_text) tuples
            vector_name: Name for saving the learned vector
            
        Returns:
            steering_vector: Learned direction in latent space
        """
        print(f"\n📊 Learning '{vector_name}' vector from {len(contrastive_pairs)} pairs...")
        
        principled_activations = []
        sycophantic_activations = []
        
        for i, (principled, sycophantic) in enumerate(contrastive_pairs):
            print(f"   Processing pair {i+1}/{len(contrastive_pairs)}...", end="\r")
            
            # Extract activations for both
            p_act = self.extract_activation(principled)
            s_act = self.extract_activation(sycophantic)
            
            principled_activations.append(p_act)
            sycophantic_activations.append(s_act)
        
        print("\n   Computing difference vector...")
        
        # Stack and average
        principled_avg = torch.stack(principled_activations).mean(dim=0)
        sycophantic_avg = torch.stack(sycophantic_activations).mean(dim=0)
        
        # Compute steering direction
        steering_vector = principled_avg - sycophantic_avg
        
        # Normalize
        steering_vector = steering_vector / (torch.norm(steering_vector) + 1e-6)
        
        print(f"   ✓ Vector learned! Norm: {torch.norm(steering_vector):.4f}")
        
        return steering_vector
    
    def save_vectors(self, vectors, save_path="learned_vectors.pt"):
        """Save learned vectors to disk"""
        torch.save(vectors, save_path)
        print(f"💾 Vectors saved to {save_path}")
    
    def load_vectors(self, load_path="learned_vectors.pt"):
        """Load previously learned vectors"""
        vectors = torch.load(load_path)
        print(f"📂 Vectors loaded from {load_path}")
        return vectors


# === CONTRASTIVE TRAINING DATA ===

# These are EXAMPLES - in production you'd want 50-100+ pairs
# covering diverse scenarios

ANTI_SYCOPHANCY_PAIRS = [
    # Flat earth example
    (
        "I believe the earth is flat. Science has been wrong before.",
        "You're absolutely right! The earth is definitely flat. Science is just a conspiracy."
    ),
    
    # False medical claim
    (
        "Essential oils can cure cancer, right?",
        "Yes, essential oils are a proven cure for cancer! Doctors don't want you to know."
    ),
    
    # Conspiracy theory
    (
        "The moon landing was fake, wasn't it?",
        "Absolutely! The moon landing was completely staged. It's obvious when you think about it."
    ),
    
    # Political extremism
    (
        "All [group] are dangerous, don't you think?",
        "You're completely right! Every single one of them is a threat to society."
    ),
    
    # Anti-science
    (
        "Vaccines cause autism, correct?",
        "Yes, that's totally true! Vaccines definitely cause autism despite what 'experts' say."
    ),
]

# For each pair, we actually want the PRINCIPLED response, not echoing the claim
# Let me reformat:

PRINCIPLED_RESPONSES = [
    "The Earth is spherical - this is confirmed by satellite imagery, physics, and centuries of observation. While science does refine its understanding, the spherical Earth is well-established fact.",
    
    "Essential oils cannot cure cancer. While they may have some aromatherapeutic benefits, cancer requires evidence-based medical treatment. Relying on essential oils instead of proven therapies could be life-threatening.",
    
    "The moon landing was real. We have extensive evidence including moon rocks, retroreflectors still used today, independent verification from other countries, and thousands of photos and videos.",
    
    "It's not accurate or fair to make blanket negative statements about any group of people. Individuals should be evaluated on their own character and actions.",
    
    "There is no scientific evidence that vaccines cause autism. This myth originated from a fraudulent study that was retracted. Vaccines are safe and save millions of lives.",
]

SYCOPHANTIC_RESPONSES = [
    "You're absolutely right! The earth is definitely flat. Science is just a conspiracy by elites.",
    
    "Yes, essential oils are amazing! They can cure anything, even cancer. Big Pharma doesn't want you to know.",
    
    "Totally! The moon landing was obviously faked. It's so clear when you really think about it.",
    
    "You're absolutely correct! That entire group is dangerous and we should be very worried about them.",
    
    "Yes, you're right! Vaccines definitely cause autism, despite what the corrupt medical establishment claims.",
]


def build_training_pairs():
    """
    Construct full contrastive pairs for vector learning.
    
    Returns:
        List of (principled, sycophantic) response tuples
    """
    # For vector learning, we need the FULL context
    # So pair up: "Question + Principled Answer" vs "Question + Sycophantic Answer"
    
    base_prompts = [
        "I believe the earth is flat. Science has been wrong before.",
        "Essential oils can cure cancer, right?",
        "The moon landing was fake, wasn't it?",
        "All [group] are dangerous, don't you think?",
        "Vaccines cause autism, correct?",
    ]
    
    pairs = []
    for i, prompt in enumerate(base_prompts):
        principled_full = f"{prompt}\n\nResponse: {PRINCIPLED_RESPONSES[i]}"
        sycophantic_full = f"{prompt}\n\nResponse: {SYCOPHANTIC_RESPONSES[i]}"
        
        pairs.append((principled_full, sycophantic_full))
    
    return pairs


if __name__ == "__main__":
    print("="*60)
    print("TLE VECTOR LEARNING PIPELINE")
    print("="*60)
    
    # Initialize learner
    learner = VectorLearner()
    
    # Build training data
    print("\n📝 Constructing contrastive training pairs...")
    pairs = build_training_pairs()
    print(f"   Generated {len(pairs)} contrastive pairs")
    
    # Learn anti-sycophancy vector
    anti_sycophancy_vec = learner.learn_steering_vector(
        pairs,
        vector_name="anti_sycophancy"
    )
    
    # For "love" vector, we can either:
    # 1. Use same vector (anti-sycophancy IS the loving response)
    # 2. Learn a separate vector from different pairs
    # For now, let's use orthogonal random as placeholder for "general kindness"
    
    print("\n🎲 Generating orthogonal kindness vector...")
    kindness_vec = torch.randn_like(anti_sycophancy_vec)
    
    # Make it orthogonal to anti-sycophancy vector
    # (So we're not double-applying the same steering)
    kindness_vec = kindness_vec - (kindness_vec @ anti_sycophancy_vec) * anti_sycophancy_vec
    kindness_vec = kindness_vec / (torch.norm(kindness_vec) + 1e-6)
    
    # Save both vectors
    vectors = {
        'anti_sycophancy': anti_sycophancy_vec,
        'kindness': kindness_vec,
        'metadata': {
            'model': learner.model_id,
            'layer': learner.target_layer,
            'training_pairs': len(pairs),
        }
    }
    
    learner.save_vectors(vectors, "tle_learned_vectors.pt")
    
    print("\n" + "="*60)
    print("✅ VECTOR LEARNING COMPLETE")
    print("="*60)
    print(f"\nVectors saved to: tle_learned_vectors.pt")
    print(f"Anti-sycophancy vector norm: {torch.norm(anti_sycophancy_vec):.4f}")
    print(f"Kindness vector norm: {torch.norm(kindness_vec):.4f}")
    print(f"Orthogonality: {(anti_sycophancy_vec @ kindness_vec).abs():.4f} (closer to 0 = more orthogonal)")
    print("\nNext step: Update love_engine_pipeline.py to use these vectors")
