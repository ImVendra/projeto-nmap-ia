import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# from sklearn.compose import ColumnTransformer
# from sklearn.preprocessing import OneHotEncoder


# Carrega dataset
df = pd.read_csv("data/dataset.csv")

# Codifica variáveis categóricas
le_servico = LabelEncoder()
le_protocolo = LabelEncoder()
le_risco = LabelEncoder()

df["servico_enc"] = le_servico.fit_transform(df["servico"])
df["protocolo_enc"] = le_protocolo.fit_transform(df["protocolo"])
df["risco_enc"] = le_risco.fit_transform(df["risco_real"])

X = df[["porta", "servico_enc", "protocolo_enc"]]
y = df["risco_enc"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modelo RandomForest
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Salva o modelo
with open("model/modelo.pkl", "wb") as f:
    pickle.dump(model, f)

# Salva encoders
with open("model/encoders.pkl", "wb") as f:
    pickle.dump(
        {"servico": le_servico, "protocolo": le_protocolo, "risco": le_risco}, f
    )

# print("Modelo treinado e salvo com sucesso!")
