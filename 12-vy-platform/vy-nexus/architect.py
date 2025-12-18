import ray
import os

# Connect to Sovereign Cluster
ray.init(address="auto", namespace="vy_sovereign", logging_level="ERROR")

@ray.remote
class Architect:
    def __init__(self):
        self.sandbox = os.path.expanduser("~/vy-nexus")
        print(f"🏗️ Architect Initialized. Sandbox: {self.sandbox}")

    def _validate_path(self, filepath):
        # Security: Prevent escaping the sandbox (../../)
        full_path = os.path.abspath(os.path.join(self.sandbox, filepath))
        if not full_path.startswith(self.sandbox):
            raise PermissionError(f"Access denied: {filepath} is outside the sandbox.")
        return full_path

    def write_file(self, filename, content):
        try:
            path = self._validate_path(filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"✅ File written: {filename}"
        except Exception as e:
            return f"❌ Write failed: {str(e)}"

    def read_file(self, filename):
        try:
            path = self._validate_path(filename)
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            return f"❌ Read failed: {str(e)}"

# Deploy Persistent Architect
try:
    # Kill old if exists (rebooting the hand)
    try:
        old = ray.get_actor("Architect")
        ray.kill(old)
        print("♻️ Old Architect retired.")
    except:
        pass
        
    Architect.options(name="Architect", lifetime="detached").remote()
    print("✅ The Architect is serving.")
except Exception as e:
    print(f"❌ Deployment failed: {e}")
