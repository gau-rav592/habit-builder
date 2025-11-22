import subprocess
import os

req_file = "requirements.txt"

# Read existing requirements
existing = set()
if os.path.exists(req_file):
    with open(req_file, "r") as f:
        existing = {line.strip() for line in f if line.strip()}

# Get installed packages through `pip freeze`
result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
installed = {line.strip() for line in result.stdout.split("\n") if line.strip()}

# Find only NEW packages
new_packages = installed - existing

# Append only new ones
with open(req_file, "a") as f:
    for pkg in sorted(new_packages):
        f.write(pkg + "\n")

print("Added:", new_packages if new_packages else "No new packages found.")
