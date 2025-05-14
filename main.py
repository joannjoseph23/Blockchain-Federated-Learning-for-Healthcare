from f1_node import HospitalNode
from blockchain import Blockchain
from crypto_utils import generate_keys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle


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
    weights = np.array(r['weights']).flatten()
    plt.plot(weights, label=f"Node {r['node']}")
all_weights = [np.array(result['weights']) for result in results]
global_weights = np.mean(all_weights, axis=0)

print("\nGlobal (averaged) weights:")
print(global_weights)
plt.plot(global_weights.flatten(), label="Global Avg", linestyle='--', color='black')
plt.title("Model Weights by Node vs Global Average")
plt.xlabel("Weight Index")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.show()

df = pd.DataFrame([{
    'Node': b.data.get('node', 'Genesis'),
    'Hash': b.hash[:10],
    'PrevHash': b.previous_hash[:10]
} for b in chain.chain])

print("\nBlockchain Timeline:")
print(df)
with open('chain.pkl', 'wb') as f:
    pickle.dump(chain, f)