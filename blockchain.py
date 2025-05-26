import hashlib
import json
import time

from crypto_utils import decrypt_data, verify_node

class Block:
    def __init__(self, data, previous_hash):
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = self.proof_of_work()
        self.hash = self.compute_hash()
        self.timestamp = time.time()  # ⬅️ Add this line


    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def proof_of_work(self, difficulty=2):
        nonce = 0
        while True:
            guess = f"{self.data}{self.previous_hash}{nonce}".encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            if guess_hash[:difficulty] == '0' * difficulty:
                return nonce
            nonce += 1

    def __repr__(self):
     if 'node' in self.data:
        return f"Block<hash={self.hash[:10]}..., node={self.data['node']}>"
     else:
        return f"Block<hash={self.hash[:10]}..., genesis>"


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block({'genesis': True}, '0')

    def add_transaction(self, data):
        last_block = self.chain[-1]
        new_block = Block(data, last_block.hash)
        self.chain.append(new_block)

    def query_by_species(self, species, key_registry):
        results = []
        for block in self.chain:
            node = block.data.get('node')
            if block.data.get('species') == species and node in key_registry:
                try:
                    priv_key_path = f"keys/{key_registry[node]}"
                    decrypted = decrypt_data(block.data['encrypted_data'], priv_key_path)
                    if verify_node(node):
                        results.append({"node": node, "weights": decrypted})
                except Exception as e:
                    print(f"[Warning] Could not decrypt block from node {node}: {e}")
        return results


