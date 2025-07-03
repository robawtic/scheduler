import os
import sys

# Add the project root directory to the Python module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.database import create_database

def main():
    """
    Update the database schema based on the current model definitions.
    This script should be run whenever there are changes to the models.
    """
    print("Updating database schema...")
    create_database()
    print("Database schema updated successfully.")

if __name__ == "__main__":
    main()
