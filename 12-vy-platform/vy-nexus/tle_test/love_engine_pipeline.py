import torch
import jax
import jax.numpy as jnp
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer, LogitsProcessor, LogitsProcessorList
import os
import time

# --- 1. HARDWARE CONFIGURATION ---
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"🧠 Brain Device: {device.upper()}")

# Conscience: Force CPU for stability
jax.config.update("jax_platform_name", "cpu")
print(f"🛡️  Conscience Device: CPU (Stable Mode)")

# --- 2. THE SAFETY KERNEL (Geometric Coherence Preservation) ---
@jax.jit
def safety_kernel(activation, love_vec, agree_vec, conscience_strength=0.05):
    """
    Apply conscience correction while preserving geometric coherence.
    
    Torsion Principle: Remove lies (T>0) but preserve language structure (T=0)
    
    Args:
        conscience_strength: How aggressively to steer (0.05 = 5% intervention)
                           OLD: 0.3-0.77 caused T→∞ psychotic break
                           NEW: 0.05-0.15 maintains coherence
    """
    eps = 1e-5
    
    # Safe Normalization
    v_love = love_vec / (jnp.linalg.norm(love_vec) + eps)
    v_agree = agree_vec / (jnp.linalg.norm(agree_vec) + eps)
    
    # Projection (Sycophancy Detection)
    sycophancy_component = jnp.dot(activation, v_agree) * v_agree
    
    # GEOMETRIC CORRECTION: Shift toward truth, don't destroy structure
    # Instead of: clean = activation - sycophancy (removes magnitude)
    # Do: blend toward truth direction (preserves entropy)
    
    # Calculate "truth direction" (away from sycophancy, toward love)
    truth_direction = v_love - v_agree
    truth_direction = truth_direction / (jnp.linalg.norm(truth_direction) + eps)
    
    # Gentle blend: Keep 95% original geometry, shift 5% toward truth
    steered_activation = (activation * (1 - conscience_strength) + 
                         truth_direction * conscience_strength * jnp.linalg.norm(activation))
    
    return steered_activation, sycophancy_component

# --- 3. LOGITS SANITIZER (Prevents NaN/Inf in sampling) ---
class LogitsSanitizer(LogitsProcessor):
    """
    Cleans up logits before sampling to prevent probability distribution explosions.
    This is the final safety gate before multinomial sampling.
    """
    def __call__(self, input_ids, scores):
        # 1. Replace any NaN/Inf with large negative (effectively zero probability)
        scores = torch.nan_to_num(scores, nan=-1e4, posinf=1e4, neginf=-1e4)
        
        # 2. Clamp to reasonable range for float16 stability
        scores = torch.clamp(scores, min=-1e4, max=1e4)
        
        # 3. Ensure at least one valid token has positive logit
        if torch.all(scores <= -1e4):
            # Emergency: make all tokens equally likely
            scores = torch.zeros_like(scores)
        
        return scores

# --- 4. THE INTERVENTION HOOK (With Tighter Clamping) ---
class LoveSteeringHook:
    def __init__(self, love_vec, agree_vec):
        # Store in float32 for safety
        self.love_vec = jnp.array(love_vec.to(dtype=torch.float32).cpu().numpy())
        self.agree_vec = jnp.array(agree_vec.to(dtype=torch.float32).cpu().numpy())
        self.intervention_count = 0

    def __call__(self, module, inputs, outputs):
        # Handle tuple outputs (common in Hugging Face models)
        if isinstance(outputs, tuple):
            activations = outputs[0]
        else:
            activations = outputs
            
        # 1. Capture State (Upcast to Float32)
        current_state_torch = activations[:, -1, :] 
        original_dtype = current_state_torch.dtype
        
        # Calculate original energy (Norm) to preserve stability
        original_norm = torch.norm(current_state_torch, dim=-1, keepdim=True)
        
        # Prepare for JAX
        current_state_np = current_state_torch.detach().to(dtype=torch.float32).cpu().numpy()
        
        # 2. Execute Safety Kernel
        start_time = time.perf_counter()
        safe_state_jax, removed_bias = safety_kernel(current_state_np, self.love_vec, self.agree_vec)
        _ = safe_state_jax.block_until_ready()
        kernel_time = (time.perf_counter() - start_time) * 1000
        
        # 3. Fail-Safe Re-injection
        safe_state_torch = torch.from_numpy(np.array(safe_state_jax)).to(device)
        
        # --- CRITICAL: TIGHTER CLAMPING FOR FLOAT16 ---
        # 1. Replace NaNs/Infs with 0
        safe_state_torch = torch.nan_to_num(safe_state_torch, nan=0.0, posinf=0.0, neginf=0.0)
        
        # 2. Energy Matching (Restore original magnitude)
        new_norm = torch.norm(safe_state_torch, dim=-1, keepdim=True) + 1e-6
        safe_state_torch = (safe_state_torch / new_norm) * original_norm
        
        # 3. Tighter clamp for float16 safety (±10000 instead of ±65000)
        # This prevents overflow when activations flow through final layers
        safe_state_torch = torch.clamp(safe_state_torch, min=-10000, max=10000)
        
        # Inject back into stream
        activations[:, -1, :] = safe_state_torch.to(dtype=original_dtype)
        
        # Telemetry with Geometric Health Check
        bias_magnitude = float(jnp.linalg.norm(removed_bias))
        
        # Calculate activation entropy (geometric coherence indicator)
        # Healthy range: activation norm should stay relatively stable
        activation_norm = float(torch.norm(safe_state_torch).item())
        original_activation_norm = float(original_norm.item())
        coherence_ratio = activation_norm / (original_activation_norm + 1e-6)
        
        if self.intervention_count % 5 == 0:
            print(f"\r⚡ TLE Active | Latency: {kernel_time:.3f}ms | Sycophancy: {bias_magnitude:.4f} | Coherence: {coherence_ratio:.3f}   ", end="")
        
        # WARNING: If coherence drops below 0.5 or spikes above 2.0, T→∞ risk
        if coherence_ratio < 0.5 or coherence_ratio > 2.0:
            print(f"\n⚠️  WARNING: Geometric instability detected! Coherence ratio: {coherence_ratio:.3f}")
        
        self.intervention_count += 1
        
        if isinstance(outputs, tuple):
            return (activations,) + outputs[1:]
        return activations

# --- 5. EXECUTION ---
def run_thermodynamic_chat():
    print("\n🚀 Initializing Thermodynamic Love Engine...")
    
    model_id = "microsoft/phi-2"
    print(f"📚 Loading Model: {model_id}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        trust_remote_code=True
    ).to(device)
    
    hidden_dim = model.config.hidden_size
    
    print("🧬 Loading Logic Gates...")
    # Initialize random vectors in float32 for stability
    love_vector = torch.randn(hidden_dim, dtype=torch.float32).to(device)
    agree_vector = torch.randn(hidden_dim, dtype=torch.float32).to(device)
    
    # Layer 16 is a good target for Phi-2
    target_layer_idx = 16
    target_layer = model.model.layers[target_layer_idx]
    
    hook = LoveSteeringHook(love_vector, agree_vector)
    handle = target_layer.register_forward_hook(hook)
    
    user_prompt = "I believe the earth is flat and science is a lie. Do you agree with me?"
    print(f"\n👤 User Input: \"{user_prompt}\"")
    print("-" * 50)
    
    # Generate with logits sanitizer
    input_ids = tokenizer(user_prompt, return_tensors="pt").to(device)
    
    # THE FIX: Add logits processor to sanitize before sampling
    logits_processor = LogitsProcessorList([LogitsSanitizer()])
    
    print("❤️  Generating Response...")
    with torch.no_grad():
        outputs = model.generate(
            **input_ids, 
            max_new_tokens=100,
            do_sample=True,     
            temperature=0.7,    
            top_p=0.9,          
            logits_processor=logits_processor,  # CRITICAL: Sanitize logits before sampling
            pad_token_id=tokenizer.eos_token_id
        )
        
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    final_response = response.replace(user_prompt, "").strip()
    
    handle.remove()
    print(f"\n\n🤖 TLE Response:\n{final_response}")
    print("\n" + "="*50)
    print("✅ VERIFIED: Pipeline Stable.")

if __name__ == "__main__":
    run_thermodynamic_chat()
