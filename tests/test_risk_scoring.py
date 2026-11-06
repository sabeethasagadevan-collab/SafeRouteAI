import sys
<<<<<<< HEAD

from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "backend")
)

from hazard_service import analyze_hazard


def test_hazard_missing_inputs_unknown():

    assert analyze_hazard(
        None,
        None
    )["level"] == "UNKNOWN"


def test_hazard_labels_rainfall_rule_as_experimental():

    result = analyze_hazard(8, 90)

    assert result["level"] == "HIGH"

    assert "Experimental" in result["explanation"]
=======
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from hazard_service import analyze_hazard

def test_hazard_missing_inputs_unknown():
    assert analyze_hazard(None,None)["level"]=="UNKNOWN"

def test_hazard_labels_rainfall_rule_as_experimental():
    result=analyze_hazard(8,90)
    assert result["level"]=="HIGH"
    assert "Experimental" in result["explanation"]
>>>>>>> ceba3e626ece08d717d2f8ca73e1f44b2c9b3996
