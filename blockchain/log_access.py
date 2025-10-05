# (blockchain/log_access.py)
from web3 import Web3

def log_access_to_blockchain(patient_id, accessed_by, record_id, timestamp):
    # Connect to Ganache or Infura
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    contract = ... # Load contract ABI and address
    tx_hash = contract.functions.logAccess(
        patient_id, accessed_by, record_id, timestamp
    ).transact({'from': <account_address>})
    return tx_hash.hex()
