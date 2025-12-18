import os
import psutil

total_size = 0
for root, dirs, files in os.walk('/Users/lordwilson'):
    for file in files:
        path = os.path.join(root, file)
        size = os.path.getsize(path) / (1024 * 1024 * 1024)
        total_size += size

print(f"Total size: {total_size:.2f} GB")

