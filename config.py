"""
Flask Application Configurations for FitAI Pro
Loads environment variables from .env file including GEMINI_API_KEY.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Try loading .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except ImportError:
    # Manual simple .env parser fallback if dotenv is not yet installed
    env_file = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE = os.path.join(BASE_DIR, 'database', 'fitai.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
