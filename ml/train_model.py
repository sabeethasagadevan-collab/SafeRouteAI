"""Train a baseline RandomForest model on a user-provided labelled CSV.

Expected CSV columns: feature columns plus a target column named `label`.
This generic scaffold does not assume a domain dataset or invent performance results.
"""
from pathlib import Path
import argparse
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv",required=True,help="Path to a verified labelled CSV")
    parser.add_argument("--target",default="label")
    parser.add_argument("--output",default="ml/models/risk_model.joblib")
    args=parser.parse_args()
    data=pd.read_csv(args.csv)
    if args.target not in data or data[args.target].isna().any():
        raise SystemExit(f"Target column {args.target!r} is missing or has null labels.")
    y=LabelEncoder().fit_transform(data[args.target].astype(str))
    X=data.drop(columns=[args.target]).select_dtypes(include="number")
    if X.empty: raise SystemExit("No numeric feature columns found.")
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=42,stratify=y if len(set(y))>1 else None)
    model=Pipeline([("imputer",SimpleImputer(strategy="median")),("classifier",RandomForestClassifier(n_estimators=200,random_state=42,class_weight="balanced"))])
    model.fit(X_train,y_train)
    pred=model.predict(X_test)
    print("Evaluation on held-out split; not evidence of real-world generalization:")
    print(classification_report(y_test,pred,zero_division=0))
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True);joblib.dump(model,output)
    print(f"Saved model to {output}. Ensure inference feature order/schema matches this training data.")

if __name__=="__main__": main()
