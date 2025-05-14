from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split

def load_hospital_data(seed=42):
    # Load Heart Disease dataset from UCI
    heart_disease = fetch_ucirepo(id=45)

    # Get features and target
    X = heart_disease.data.features
    y = heart_disease.data.targets['num']

    # Combine to drop NaNs together
    df = X.copy()
    df['target'] = y
    df = df.dropna()  # 🔥 Drop rows with any NaN

    # Separate again
    X_clean = df.drop(columns=['target'])
    y_clean = df['target']

    # Simulate hospital-local split
    X_train, _, y_train, _ = train_test_split(X_clean, y_clean, test_size=0.5, random_state=seed)

    return X_train.to_numpy(), y_train.to_numpy()
