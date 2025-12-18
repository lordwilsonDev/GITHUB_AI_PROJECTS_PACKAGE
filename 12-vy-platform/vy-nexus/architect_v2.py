import ray
import os
import subprocess

ray.init(address="auto", namespace="vy_sovereign", logging_level="ERROR")

@ray.remote
class Architect:
    def __init__(self):
        self.sandbox = os.path.expanduser("~/vy-nexus")
        print(f"🏗️ Architect V2 (Writer + Executor) Online.")

    def _validate_path(self, filepath):
        full_path = os.path.abspath(os.path.join(self.sandbox, filepath))
        if not full_path.startswith(self.sandbox):
            raise PermissionError(f"Access denied: {filepath} outside sandbox.")
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

    def execute_file(self, filename):
        """
        Runs a python script inside the sandbox and returns STDOUT.
        """
        try:
            path = self._validate_path(filename)
            # Security: Only allow running files inside the sandbox
            # Timeout: 10 seconds to prevent infinite loops
            result = subprocess.run(
                [os.path.expanduser("~/vy-nexus/venv/bin/python3"), path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.sandbox
            )
            
            if result.returncode == 0:
                return f"✅ EXECUTION SUCCESS:\n{result.stdout.strip()}"
            else:
                return f"⚠️ EXECUTION ERROR:\n{result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return "❌ ERROR: Execution timed out (10s limit)."
        except Exception as e:
            return f"❌ EXECUTION FAILED: {str(e)}"

# Redeploy
try:
    try:
        ray.kill(ray.get_actor("Architect"))
        print("♻️  Retiring Architect V1...")
    except:
        pass
    Architect.options(name="Architect", lifetime="detached").remote()
    print("✅ Architect V2 is serving.")
except Exception as e:
    print(f"❌ Deployment failed: {e}")
