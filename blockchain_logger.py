import os
from dotenv import load_dotenv
from web3 import Web3

# Load variables from .env
load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")
MY_ADDRESS = os.getenv("MY_ADDRESS")
MY_PRIVATE_KEY = os.getenv("MY_PRIVATE_KEY")

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

def is_connected():
    return w3.is_connected()

def log_to_blockchain(node_id, block_hash):
    """
    Sends a self-transaction with block metadata to the Ethereum Sepolia testnet.
    """
    if not is_connected():
        raise ConnectionError("❌ Not connected to Ethereum network")

    # Message to embed in transaction (32 bytes max recommended)
    message = f"Node {node_id} block {block_hash[:10]}"
    data = message.encode("utf-8")

    # Build transaction
    tx = {
    "nonce": w3.eth.get_transaction_count(MY_ADDRESS),
    "to": MY_ADDRESS,
    "value": 0,
    "gas": 100000,  # ✅ enough for a transaction with data
    "gasPrice": w3.eth.gas_price,
    "data": data,
    "chainId": 1337  # Sepolia
}


    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=MY_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)
