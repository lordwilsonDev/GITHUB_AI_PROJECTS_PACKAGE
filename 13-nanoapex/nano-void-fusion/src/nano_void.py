import json
from pathlib import Path
from numpy import dot
from numpy.linalg import norm
from datetime import datetime
import os

class NanoFileSystem:
    """
    Basic NanoFileSystem implementation for creating .nano files
    """
    
    def __init__(self, root_path="~/nano_memory"):
        self.root = Path(root_path).expanduser()
        self.root.mkdir(exist_ok=True)
    
    def create(self, content, n_type="thought", tags=None):
        if tags is None:
            tags = []
        
        nano_data = {
            "content": {
                "essence": content
            },
            "meta": {
                "type": n_type,
                "tags": tags,
                "created": datetime.now().isoformat()
            }
        }
        
        # Generate filename based on timestamp and type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{n_type}_{timestamp}.nano"
        filepath = self.root / filename
        
        with open(filepath, 'w') as f:
            json.dump(nano_data, f, indent=2)
        
        return filepath

class NanoVoidEngine:
    """
    The Fusion Reactor:
    - Scans NFS for nano memory
    - Extracts semantic essence
    - Computes resonance (unity) or torsion (separation)
    - Generates new derived thoughts as .nano files
    """
    
    def __init__(self, nfs_path="~/nano_memory"):
        self.root = Path(nfs_path).expanduser()
        self.root.mkdir(exist_ok=True)
        self.nfs = NanoFileSystem(nfs_path)
        print("🌌 Nano-Void Engine Initialized")

    def _load_nanos(self):
        """Load all .nano files from the memory directory"""
        try:
            for path in self.root.glob("*.nano"):
                try:
                    with open(path, "r") as f:
                        yield json.load(f)
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"⚠️  Error loading {path}: {e}")
                    continue
        except Exception as e:
            print(f"⚠️  Error scanning nano directory: {e}")

    def _embedding(self, text):
        """Simple word frequency embedding - placeholder for more sophisticated methods"""
        if not text:
            return [0, 0]
        return [sum(ord(c) for c in text), len(text)]

    def _cosine(self, a, b):
        """Calculate cosine similarity between two vectors"""
        try:
            return dot(a, b) / (norm(a) * norm(b) + 1e-8)
        except Exception:
            return 0.0

    def fuse(self, batch_limit=50):
        """
        Main fusion process:
        - Load nano files
        - Compare essences for resonance
        - Generate new insights from high-resonance pairs
        """
        nanos = list(self._load_nanos())[:batch_limit]
        if len(nanos) < 2:
            print("⚠️  Need at least 2 .nano files for fusion")
            return None

        outputs = []
        print(f"🔍 Processing {len(nanos)} nano files...")

        for i in range(len(nanos)):
            for j in range(i+1, len(nanos)):
                a, b = nanos[i], nanos[j]

                # Skip anti-resonant pairs
                a_tags = a.get("meta", {}).get("tags", [])
                b_tags = b.get("meta", {}).get("tags", [])
                
                if "separation" in a_tags and "unity" in b_tags:
                    continue
                if "separation" in b_tags and "unity" in a_tags:
                    continue

                # Extract essences
                ess_a = a.get("content", {}).get("essence", "")
                ess_b = b.get("content", {}).get("essence", "")
                
                if not ess_a or not ess_b:
                    continue

                # Calculate embeddings and resonance
                vec_a = self._embedding(ess_a)
                vec_b = self._embedding(ess_b)
                resonance = self._cosine(vec_a, vec_b)

                # Generate fusion insight
                new_ess = f"{ess_a} + {ess_b} → Unifying Principle"
                print(f"✨ Fusion: {new_ess[:100]}... (R={resonance:.3f})")

                # Write new nano if high resonance
                if resonance > 0.75:
                    try:
                        self.nfs.create(
                            content=new_ess,
                            n_type="fusion",
                            tags=["void-engine", "resonance"]
                        )
                        outputs.append(new_ess)
                        print(f"💾 Created fusion nano: {new_ess[:50]}...")
                    except Exception as e:
                        print(f"⚠️  Error creating fusion nano: {e}")

        return outputs

if __name__ == "__main__":
    nve = NanoVoidEngine()
    results = nve.fuse()
    if results:
        print("\n⚡ Fused Insights Generated:")
        for res in results:
            print("-", res)
    else:
        print("\n🔄 No fusion results generated. Try adding more .nano files to ~/nano_memory")
