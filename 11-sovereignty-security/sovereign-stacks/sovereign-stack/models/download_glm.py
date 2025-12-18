from huggingface_hub import snapshot_download
import os

print("🔽 Downloading GLM-4V-9B model...")
print("This is about 18GB - might take a while")

model_path = snapshot_download(
    repo_id="THUDM/glm-4v-9b",
    local_dir=os.path.expanduser("~/sovereign-stack/models/glm-4v-9b"),
    local_dir_use_symlinks=False,
    resume_download=True
)

print(f"✅ Model downloaded to: {model_path}")
