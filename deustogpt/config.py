"""
Configuration management for DeustoGPT application.
"""

import os
from decouple import config

# API keys and credentials
OPENAI_API_KEY = config("OPENAI_API_KEY")

# OAuth configuration
OAUTH_REDIRECT_URI = config("OAUTH_REDIRECT_URI", default="http://localhost:8501/")

# Application settings
UPLOAD_DIR = config("UPLOAD_DIR", default="uploaded_files")
DEUSTO_DOMAIN = "@deusto.es"
OPENDEUSTO_DOMAIN = "@opendeusto.es"

# Ensure upload directory exists
def ensure_upload_dir(directory=UPLOAD_DIR):
    if not os.path.exists(directory):
        os.makedirs(directory)