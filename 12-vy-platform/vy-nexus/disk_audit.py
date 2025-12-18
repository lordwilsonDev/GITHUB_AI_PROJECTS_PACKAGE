import os
import shutil

# Set the directory path
dir_path = '/Users/lordwilson'

# Get the total size of the directory
total_size = 0
for dirpath, dirnames, filenames in os.walk(dir_path):
    for f in filenames:
        fp = os.path.join(dirpath, f)
        total_size += os.path.getsize(fp)

# Calculate the percentage
total_size_gb = total_size / (1024 * 1024 * 1024)
print(f"Total size of {dir_path} is: {total_size_gb:.2f} GB")
