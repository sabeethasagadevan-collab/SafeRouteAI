import sys

from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "backend")
)

from route_analyzer import (
    score_route,
    classify_traffic,
    estimate_weather_risk
)


def test_missing_all_scores_unknown():

    result = score_route(
        traffic_score=None,
        hazard_score=None,
        travel_time_score=None,
        weather_score=None
    )

    assert result["level"] == "UNKNOWN"

    assert result["score"] is None


def test_missing_factor_not_zero():

    result = score_route(
        traffic_score=80,
        hazard_score=None,
        travel_time_score=20,
        weather_score=None
    )

    assert "hazard" in result["missing_factors"]

    assert result["score"] == round(
        (80 * .35 + 20 * .20) / (.35 + .20),
        1
    )


def test_traffic_unknown_for_missing():

    assert classify_traffic(None) == "UNKNOWN"

    assert classify_traffic(.8) == "LOW"

    assert classify_traffic(.5) == "MEDIUM"

    assert classify_traffic(.2) == "HIGH"


def test_rain_unknown_when_no_inputs():

    assert estimate_weather_risk(
        None,
        None
    )["level"] == "UNKNOWN"