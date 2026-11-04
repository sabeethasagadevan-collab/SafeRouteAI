import argparse, json
from pathlib import Path
import joblib

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--model",default="ml/models/risk_model.joblib")
    parser.add_argument("--features",required=True,help='JSON array of numeric features in training-column order')
    args=parser.parse_args()
    path=Path(args.model)
    if not path.exists(): raise SystemExit("No trained model found. Train one using a verified labelled dataset first.")
    model=joblib.load(path); features=json.loads(args.features)
    print(json.dumps({"prediction":str(model.predict([features])[0]),"method":"trained_model"}))
if __name__=="__main__":main()
