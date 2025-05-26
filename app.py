# ✅ app.py
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import time
import numpy as np
import os
from blockchain import Blockchain
from crypto_utils import decrypt_data, generate_keys
from node import HospitalNode
from blockchain_logger import log_to_blockchain

st.set_page_config(page_title="Federated Learning Dashboard", layout="wide")
st.title("\U0001F3E5 Federated Learning + Blockchain Dashboard")

CHAIN_FILE = "chain.pkl"
node_ids = [chr(ord('A') + i) for i in range(10)]

# Simulation function
def simulate_federated_training(node_ids, delay=1):
    for nid in node_ids:
        generate_keys(f'hospital_{nid.lower()}')
    chain = Blockchain()
    for i, nid in enumerate(node_ids):
        node = HospitalNode(nid)
        update = node.train_model()
        chain.add_transaction(update)

        tx_hash = log_to_blockchain(nid, chain.chain[-1].hash)
        yield nid, i + 1, chain, tx_hash
        time.sleep(delay)

    with open(CHAIN_FILE, "wb") as f:
        pickle.dump(chain, f)

# Start simulation
if st.button("▶️ Start Simulation"):
    st.info("Running federated training...")
    progress_bar = st.progress(0)
    for step, (nid, block_num, chain, tx_hash) in enumerate(simulate_federated_training(node_ids)):
        st.success(f"✅ Hospital {nid} trained. Block #{block_num} added.")
        st.write(f"Transaction Hash (Ganache): {tx_hash}")
        progress_bar.progress((step + 1) / len(node_ids))
    st.balloons()
    st.success("🎉 Simulation complete. Blockchain saved.")

# Load blockchain
if not os.path.exists(CHAIN_FILE):
    st.warning("Blockchain not found. Run the simulation first.")
    st.stop()
with open(CHAIN_FILE, 'rb') as f:
    chain: Blockchain = pickle.load(f)

# Network Visualization
st.subheader("📡 Federated Network Overview")
nodes = set()
for block in chain.chain[1:]:
    if 'node' in block.data:
        nodes.add(block.data['node'])
G = nx.DiGraph()
G.add_node("Blockchain", color="red")
for node in nodes:
    G.add_node(node, color="skyblue")
    G.add_edge(node, "Blockchain")
pos = nx.spring_layout(G)
colors = [data["color"] for _, data in G.nodes(data=True)]
fig, ax = plt.subplots(figsize=(8, 5))
nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1500, font_size=14, arrows=True)
st.pyplot(fig)

# Blockchain log
st.subheader("📦 Blockchain Ledger")
blocks = []
for i, block in enumerate(chain.chain[1:], start=1):
    blocks.append({
        "Block #": i,
        "Node": block.data.get("node"),
        "Disease": block.data.get("species"),
        "Hash": block.hash[:10] + "...",
        "Timestamp": block.timestamp
    })
df_blocks = pd.DataFrame(blocks)
st.dataframe(df_blocks)

# Model averaging and global insights
st.subheader("📊 Global Model Insights")
all_weights = []
node_contributions = []

for block in chain.chain[1:]:
    try:
        weights = np.array(block.data['weights'])
        all_weights.append(weights)
        node_contributions.append(block.data['node'])
    except Exception as e:
        st.warning(f"Decryption failed for block: {e}")
        continue

if all_weights:
    all_weights = np.array(all_weights)
    avg_weights = np.mean(all_weights, axis=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, weights in enumerate(all_weights):
        ax.plot(weights.flatten(), label=f"Node {node_contributions[i]}")
    ax.plot(avg_weights.flatten(), color='black', linewidth=2.5, label='Global Average')
    ax.set_title("Model Weights per Node with Global Average")
    ax.set_xlabel("Feature Index")
    ax.set_ylabel("Weight Value")
    ax.legend(loc="best", fontsize="small")
    st.pyplot(fig)

    st.success(f"Averaged updates from {len(all_weights)} nodes.")

    df_avg = pd.DataFrame([
        avg_weights.flatten()
    ], columns=[f"Feature {i+1}" for i in range(len(avg_weights.flatten()))])
    st.dataframe(df_avg)

    top_features = df_avg.T.sort_values(by=0, ascending=False).head(3)
    st.markdown("#### 🔍 Most Influential Features")
    for i, value in top_features.iterrows():
        st.markdown(f"- **{i}** with average weight `{value[0]:.4f}`")
else:
    st.warning("⚠️ No weights available for global averaging.")

# Observations
st.subheader("🔍 Observations")
if df_blocks.empty:
    st.info("No updates submitted yet.")
else:
    unique_nodes = df_blocks['Node'].nunique()
    st.success(f"{unique_nodes} unique nodes contributed updates.")
    st.markdown("- 🔐 All model updates were encrypted before submission.")
    st.markdown("- 📜 Blockchain provides immutable logging of model updates.")
    st.markdown("- 🌐 A global model can be aggregated without sharing patient data.")
if st.button("Summarize Network"):
    st.markdown("### 🧠 Network Summary")
    st.markdown(f"- **{unique_nodes} nodes** submitted updates.")
    st.markdown(f"- **{len(df_blocks)} blocks** recorded.")
    st.markdown("- ✅ All updates logged securely and traceably.")
