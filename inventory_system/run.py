import sys
import os

# Add the parent directory to sys.path to allow imports from inventory_system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_system.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
