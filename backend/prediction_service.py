from pathlib import Path
import joblib
from config import get_settings

def model_status():
    path=(Path(__file__).resolve().parent / get_settings().model_path).resolve()
    return {"available":path.exists(),"model_path":str(path) if path.exists() else None,
            "message":"Trained model loaded only when a valid model artifact exists; otherwise use transparent rule-based estimates."}

def predict(features: dict):
    status=model_status()
    if not status["available"]:
        return {"available":False,"level":"UNKNOWN","method":"none","message":"No trained model is available. Obtain a verified labelled dataset and train/evaluate a model first."}
    model=joblib.load(status["model_path"])
    try:
        prediction=model.predict([list(features.values())])[0]
        return {"available":True,"prediction":str(prediction),"method":"trained_model","model_path":status["model_path"]}
    except Exception:
        return {"available":False,"level":"UNKNOWN","method":"none","message":"Model input did not match the trained model schema."}
