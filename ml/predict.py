import argparse
import json

from pathlib import Path
import joblib


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        default="ml/models/risk_model.joblib"
    )

    parser.add_argument(
        "--features",
        required=True,
        help="JSON array of numeric features"
    )

    args = parser.parse_args()

    path = Path(args.model)

    if not path.exists():
        raise SystemExit(
            "No trained model found. Train a model first."
        )

    model = joblib.load(path)

    features = json.loads(args.features)

    prediction = model.predict([features])[0]

    print(
        json.dumps({
            "prediction": str(prediction),
            "method": "trained_model"
        })
    )


if __name__ == "__main__":
    main()