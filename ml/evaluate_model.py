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