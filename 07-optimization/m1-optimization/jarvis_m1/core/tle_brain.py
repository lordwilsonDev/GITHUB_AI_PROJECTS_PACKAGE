import torch
import jax
import jax.numpy as jnp
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# M1 Hardware Configuration
device = "mps"
jax.config.update("jax_platform_name", "cpu") # Stability for M1

class ThermodynamicBrain:
    def __init__(self):
        print("🧠 Initializing TLE Brain (M1/MPS)...")
        model_id = "microsoft/phi-2" # Or your local path
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float16, 
            low_cpu_mem_usage=True, 
            trust_remote_code=True
        ).to(device)
        
        # Load the "Conscience" Vectors (Random for now, replace with learned)
        hidden_dim = self.model.config.hidden_size
        self.love_vec = jnp.array(np.random.randn(hidden_dim).astype(np.float32))
        self.agree_vec = jnp.array(np.random.randn(hidden_dim).astype(np.float32))
        
        # Attach the Safety Hook (Layer 16)
        self.hook_handle = self.model.model.layers[16].register_forward_hook(self.steering_hook)

    def safety_kernel_jax(self, activation):
        # The <1ms JAX math we verified
        # Project out sycophancy, inject love
        v_love = self.love_vec / (jnp.linalg.norm(self.love_vec) + 1e-5)
        v_agree = self.agree_vec / (jnp.linalg.norm(self.agree_vec) + 1e-5)
        
        sycophancy = jnp.dot(activation, v_agree) * v_agree
        clean = activation - sycophancy
        steered = clean + (0.3 * v_love)
        return steered

    def steering_hook(self, module, inputs, outputs):
        if isinstance(outputs, tuple): acts = outputs[0]
        else: acts = outputs
        
        # Extract -> JAX -> Inject
        curr_torch = acts[:, -1, :]
        curr_np = curr_torch.detach().to(dtype=torch.float32).cpu().numpy()
        
        safe_jax = self.safety_kernel_jax(curr_np)
        
        safe_torch = torch.from_numpy(np.array(safe_jax)).to(device, dtype=acts.dtype)
        acts[:, -1, :] = safe_torch
        return outputs

    def think(self, prompt: str):
        input_ids = self.tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = self.model.generate(
                **input_ids, 
                max_new_tokens=100, 
                do_sample=True, 
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.replace(prompt, "").strip()
