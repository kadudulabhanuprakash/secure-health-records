# app/services/blockchain_service.py
from web3 import Web3
import os

# Ethereum configuration
WEB3_PROVIDER = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"  # Your deployed address
ACCOUNT_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # Hardhat's first account
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Hardhat's first private key

# Contract ABI (updated to match new AccessLogger.sol)
CONTRACT_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "uint256", "name": "recordId", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "patientId", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "accessor", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "AccessLogged",
        "type": "event"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "recordId", "type": "uint256"},
            {"internalType": "uint256", "name": "patientId", "type": "uint256"},
            {"internalType": "string", "name": "accessor", "type": "string"}
        ],
        "name": "logAccess",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
checksum_address = w3.to_checksum_address(CONTRACT_ADDRESS)
contract = w3.eth.contract(address=checksum_address, abi=CONTRACT_ABI)

def log_access(record_id, patient_id, accessor):
    """
    Log an access event to the blockchain.
    Returns the transaction hash.
    """
    try:
        nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        tx = contract.functions.logAccess(int(record_id), int(patient_id), accessor).build_transaction({
            'from': ACCOUNT_ADDRESS,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return w3.to_hex(tx_hash)
    except Exception as e:
        raise Exception(f"Failed to log access: {str(e)}")


def store_file_hash(filename, file_hash):
    """
    Store a file hash on the blockchain.
    Returns the transaction hash.
    """
    try:
        nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        tx = contract.functions.storeFileHash(filename, file_hash).build_transaction({
            'from': ACCOUNT_ADDRESS,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return w3.to_hex(tx_hash)
    except Exception as e:
        raise Exception(f"Failed to store hash: {str(e)}")

def get_file_hash(filename):
    """
    Retrieve a file hash from the blockchain.
    """
    try:
        file_hash = contract.functions.getFileHash(filename).call()
        return w3.to_hex(file_hash)
    except Exception as e:
        raise Exception(f"Failed to retrieve hash: {str(e)}")

def get_access_logs(record_id):
    """
    Retrieve access logs for a record from the blockchain.
    """
    try:
        logs = contract.functions.getAccessLogs(record_id).call()
        return [
            {"patientId": log[0], "accessor": log[1], "timestamp": log[2]}
            for log in logs
        ]
    except Exception as e:
        raise Exception(f"Failed to retrieve access logs: {str(e)}")