import os
env_path = r'C:\secure-health-records\.env'
print(f"Loading: {env_path}")
try:
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                        print(f"Set {key}: {value[:10]}...")
                    except ValueError as e:
                        print(f"Error parsing line: {line.strip()} - {e}")
        print("✅ .env loaded successfully")
        print(f"AZURE_STORAGE_CONNECTION_STRING = {os.getenv('AZURE_STORAGE_CONNECTION_STRING')}")
    else:
        print(f"❌ {env_path} not found")
except Exception as e:
    print(f"❌ Error loading .env: {e}")