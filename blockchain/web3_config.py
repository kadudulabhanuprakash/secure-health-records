# blockchain/web3_config.py
import json
import os
from web3 import Web3

# Connect to Hardhat local node
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if not w3.is_connected():
    raise Exception("Web3 is not connected. Is Hardhat node running?")

# Paths for ABI and address
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "contract"))

with open(os.path.join(BASE_DIR, "abi.json"), "r") as abi_file:
    contract_abi = json.load(abi_file)

with open(os.path.join(BASE_DIR, "address.txt"), "r") as addr_file:
    contract_address = addr_file.read().strip()

# Fix: Use to_checksum_address instead of toChecksumAddress
contract = w3.eth.contract(
    address=w3.to_checksum_address(contract_address),
    abi=contract_abi
)

default_account = w3.eth.accounts[0]

def log_access(record_id, patient_id, accessor):
    tx_hash = contract.functions.logAccess(record_id, patient_id, accessor).transact({
        'from': default_account
    })
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt