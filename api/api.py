from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd
import uvicorn

app = FastAPI()


class Entrada(BaseModel):
    porta: int
    servico: str
    protocolo: str


# Carrega modelo e encoders
with open("model/modelo.pkl", "rb") as f:
    model = pickle.load(f)

with open("model/encoders.pkl", "rb") as f:
    encoders = pickle.load(f)

le_servico = encoders["servico"]
le_protocolo = encoders["protocolo"]
le_risco = encoders["risco"]


@app.post("/classificar")
def classificar(entrada: Entrada):
    try:
        try:
            servico_enc = le_servico.transform([entrada.servico])[0]
        except:
            servico_enc = 0

        try:
            protocolo_enc = le_protocolo.transform([entrada.protocolo])[0]
        except:
            protocolo_enc = 0

        features = [[entrada.porta, servico_enc, protocolo_enc]]

        pred = model.predict(features)[0]
        risco = le_risco.inverse_transform([pred])[0]

        return {
            "porta": entrada.porta,
            "servico": entrada.servico,
            "protocolo": entrada.protocolo,
            "risco_classificado": risco,
        }
    except Exception as e:
        return {"erro": str(e), "risco": None}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
