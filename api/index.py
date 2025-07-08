import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Vercel-compatible app instead of the SocketIO version
from web_app_vercel import app

# Export the app for Vercel
vercel_app = app 