from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from crypto_utils import encrypt_data

class HospitalNode:
    def __init__(self, name):
        self.name = name
        self.X, self.y = self.load_data()

    def load_data(self):
        data = load_breast_cancer()
        X, y = data.data, data.target

        # Simulate different local datasets
        if self.name == 'A':
            X_node, _, y_node, _ = train_test_split(X, y, test_size=0.5, random_state=42)
        else:
            _, X_node, _, y_node = train_test_split(X, y, test_size=0.5, random_state=42)

        return X_node, y_node

    def train_model(self):
        model = LogisticRegression(max_iter=1000)
        model.fit(self.X, self.y)
        weights = model.coef_.tolist()  # model.coef_ is a 2D array
        encrypted_weights = encrypt_data(weights, f'hospital_{self.name.lower()}_pub.pem')

        return {
            'node': self.name,
            'species': 'breast-cancer',  # you can query by this
            'encrypted_data': encrypted_weights
        }
