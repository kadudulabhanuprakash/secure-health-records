# File: backend/app/blockchain.py
from web3 import Web3
import json
import os

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_PROVIDER_URL')))
if not w3.is_connected():
    print("blockchain.py - Warning: Not connected to Ethereum node")

# Contract details from .env
contract_address = os.getenv('ACCESS_LOGGER_ADDRESS')
private_key = os.getenv('WALLET_PRIVATE_KEY')

# Load ABI from contracts/AccessLogger.json
abi_path = os.path.join(os.path.dirname(__file__), '../../contracts/AccessLogger.json')
with open(abi_path, 'r') as f:
    abi = json.load(f)['abi']

# Contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

def log_access(user_email, record_name, action):
    """Log access event to Ethereum blockchain (DISABLED for now)."""
    print(f"blockchain.py - SKIPPED: Would log {user_email} on {record_name} ({action})")
    return "xxxx_tx_hash_123"