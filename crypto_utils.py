import os
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

KEYS_DIR = 'keys'
os.makedirs(KEYS_DIR, exist_ok=True)

def generate_keys(name):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    with open(f'{KEYS_DIR}/{name}.pem', 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()))

    with open(f'{KEYS_DIR}/{name}_pub.pem', 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo))

def encrypt_data(data, pubkey_path):
    # 1. Serialize and pad data
    json_data = json.dumps(data).encode()
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(json_data) + padder.finalize()

    # 2. Generate AES key and IV
    aes_key = os.urandom(32)  # AES-256
    iv = os.urandom(16)

    # 3. Encrypt data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # 4. Encrypt AES key with RSA
    with open(f'keys/{pubkey_path}', 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

    encrypted_key = public_key.encrypt(
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 5. Return base64-encoded payload
    return json.dumps({
        'key': b64encode(encrypted_key).decode(),
        'iv': b64encode(iv).decode(),
        'ciphertext': b64encode(ciphertext).decode()
    })

def decrypt_data(payload_json, privkey_path):
    payload = json.loads(payload_json)

    encrypted_key = b64decode(payload['key'])
    iv = b64decode(payload['iv'])
    ciphertext = b64decode(payload['ciphertext'])

    # Load private key
    with open(privkey_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    # Decrypt AES key
    aes_key = private_key.decrypt(
        encrypted_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt ciphertext
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad
    unpadder = sym_padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return json.loads(data.decode())

def verify_node(node):
    return node in ['A', 'B']
