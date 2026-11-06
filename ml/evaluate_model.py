<<<<<<< HEAD
from sklearn.metrics import (
    confusion_matrix,
    classification_report
)


def evaluate(y_true, y_pred):

    return {
        "classification_report": classification_report(
            y_true,
            y_pred,
            zero_division=0
        ),

        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred
        ).tolist()
    }
=======
"""Evaluation helper: use the training script's held-out report or extend this with a time-based split."""
from sklearn.metrics import confusion_matrix, classification_report

def evaluate(y_true, y_pred):
    return {"classification_report":classification_report(y_true,y_pred,zero_division=0),
            "confusion_matrix":confusion_matrix(y_true,y_pred).tolist()}
>>>>>>> ceba3e626ece08d717d2f8ca73e1f44b2c9b3996
