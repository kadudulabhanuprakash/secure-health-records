# File: backend/main.py
import os
from dotenv import load_dotenv
from backend.app import create_app

import os
from dotenv import load_dotenv
load_dotenv()  # Loads .env from current dir (works locally and in Azure via env vars)

# Create the Flask app using the new factory function
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Azure sets PORT env var
    app.run(debug=False, host='0.0.0.0', port=port)  # No debug in prod, bind to all IPs