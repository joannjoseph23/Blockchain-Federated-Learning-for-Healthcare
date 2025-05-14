from f1_node import HospitalNode
from blockchain import Blockchain
from crypto_utils import generate_keys

# Generate RSA keys for each hospital
generate_keys('hospital_a')
generate_keys('hospital_b')
key_registry = {
    'A': 'hospital_a.pem',
    'B': 'hospital_b.pem'
}

# Initialize blockchain
chain = Blockchain()

# Initialize hospital nodes
hospital_a = HospitalNode('A')
hospital_b = HospitalNode('B')

# Each hospital trains its local model
update_a = hospital_a.train_model()
update_b = hospital_b.train_model()

# Add encrypted updates to the blockchain
chain.add_transaction(update_a)
chain.add_transaction(update_b)

# Print the blockchain
print("\nBlockchain:")
for block in chain.chain:
    print(block)

# Query by species and decrypt results
print("\nQuery Result:")
results = chain.query_by_species('setosa', key_registry)

for r in results:
    print(r)
