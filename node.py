from sklearn.linear_model import LogisticRegression
from hospital_data import load_hospital_data
from crypto_utils import encrypt_data

class HospitalNode:
    def __init__(self, name):
        self.name = name
        # Unique seed for different hospitals
        seed = 42 + ord(name)
        self.X, self.y = load_hospital_data(seed)

    def train_model(self):
        model = LogisticRegression(max_iter=1000, solver='liblinear')
        model.fit(self.X, self.y)
        weights = model.coef_.tolist()
        encrypted_weights = encrypt_data(weights, f'hospital_{self.name.lower()}_pub.pem')

        return {
            'node': self.name,
            'species': 'breast-cancer',
            'weights': weights,
            'key': f'hospital_{self.name.lower()}.pem',
            'encrypted_data': encrypted_weights
        }
