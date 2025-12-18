
import os
import sys

print("Test script running...")
print(f"Sandbox path: {os.environ.get('SANDBOX_PATH')}")
print(f"Input path: {os.environ.get('SANDBOX_INPUT')}")
print(f"Output path: {os.environ.get('SANDBOX_OUTPUT')}")

# Create a test file
output_file = os.path.join(os.environ.get('SANDBOX_OUTPUT'), 'test_output.txt')
with open(output_file, 'w') as f:
    f.write('Test completed successfully!')

print("Test completed!")
sys.exit(0)
