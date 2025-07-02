import subprocess
import sys
import os

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("Installing dependencies from requirements.txt...")
    
    # Get the path to the requirements.txt file
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    
    # Check if the file exists
    if not os.path.exists(requirements_path):
        print(f"Error: requirements.txt not found at {requirements_path}")
        return False
    
    try:
        # Install dependencies using pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

if __name__ == "__main__":
    install_dependencies()