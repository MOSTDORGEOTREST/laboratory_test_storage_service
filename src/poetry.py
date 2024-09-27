import subprocess

# Open and read the requirements.txt file
with open('requirements.txt', 'r') as file:
    dependencies = file.readlines()

# Add each dependency using Poetry
for dep in dependencies:
    dep = dep.strip()
    if dep:
        subprocess.run(['poetry', 'add', dep])