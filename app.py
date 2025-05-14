import streamlit as st
import pickle
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from blockchain import Blockchain
from crypto_utils import decrypt_data, verify_node

# Set page title
st.set_page_config(page_title="Federated Learning Blockchain", layout="wide")

st.title("🩺 Blockchain-Based Federated Learning")
st.markdown("Visualize and query encrypted model updates stored on a blockchain.")

# Load key registry
key_registry = {
    'A': 'hospital_a.pem',
    'B': 'hospital_b.pem'
}

# Load the blockchain
CHAIN_FILE = 'chain.pkl'

if not os.path.exists(CHAIN_FILE):
    st.error("❌ Blockchain file not found. Run `main.py` first to generate it.")
    st.stop()

with open(CHAIN_FILE, 'rb') as f:
    chain: Blockchain = pickle.load(f)

# Sidebar
st.sidebar.header("🔍 Query Options")
species = st.sidebar.selectbox("Select species label:", ['setosa', 'versicolor', 'virginica'])

if st.sidebar.button("Query Blockchain"):
    st.subheader(f"🔐 Decrypted Model Weights for '{species}'")
    results = chain.query_by_species(species, key_registry)

    if results:
        all_weights = []
        for r in results:
            # Create a dataframe to display the decrypted weights
            node_name = r['node']
            weights = r['weights']
            weight_df = pd.DataFrame(weights, columns=[f'Feature {i+1}' for i in range(len(weights[0]))])
            st.subheader(f"Model Weights from Node {node_name}")
            st.write(weight_df)

            all_weights.append(np.array(weights))

        # Federated averaging
        global_weights = np.mean(all_weights, axis=0)
        st.subheader("🌐 Federated Averaged Weights")
        st.code(global_weights.tolist())

        # Visualize with a DataFrame (Bar Chart)
        weight_df_global = pd.DataFrame(global_weights, columns=[f'Feature {i+1}' for i in range(global_weights.shape[1])])
        st.bar_chart(weight_df_global.T)

        # Optionally: Add a heatmap to visualize weight differences
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(global_weights, cmap='coolwarm', aspect='auto')
        ax.set_title("Global Model Weights (Heatmap)")
        ax.set_xticks(np.arange(global_weights.shape[1]))
        ax.set_xticklabels([f'Feature {i+1}' for i in range(global_weights.shape[1])])
        st.pyplot(fig)
    else:
        st.warning("No valid results found for the selected species.")
