from typing import Optional

def score_route(*, traffic_score: Optional[float], hazard_score: Optional[float],
                travel_time_score: Optional[float], weather_score: Optional[float],
                weights=None) -> dict:
    """Weighted route score (0-100); missing factors are excluded and remaining weights normalized."""
    weights = weights or {"traffic": .35, "hazard": .35, "travel_time": .20, "weather": .10}
    values = {"traffic": traffic_score, "hazard": hazard_score,
              "travel_time": travel_time_score, "weather": weather_score}
    used = {key: max(0.0, min(100.0, float(value))) for key, value in values.items() if value is not None}
    if not used:
        return {"score": None, "level": "UNKNOWN", "used_factors": [], "missing_factors": list(values)}
    denominator = sum(weights[k] for k in used)
    score = sum(used[k] * weights[k] for k in used) / denominator
    level = "LOW" if score < 30 else "MEDIUM" if score < 65 else "HIGH"
    return {"score": round(score, 1), "level": level, "used_factors": list(used),
            "missing_factors": [k for k in values if k not in used],
            "explanation": "Score uses only available factors; missing factors are excluded and reported."}

def classify_traffic(relative_speed: Optional[float]) -> str:
    if relative_speed is None: return "UNKNOWN"
    if relative_speed >= .75: return "LOW"
    if relative_speed >= .40: return "MEDIUM"
    return "HIGH"

def estimate_weather_risk(precipitation_mm: Optional[float], probability: Optional[float]) -> dict:
    if precipitation_mm is None and probability is None:
        return {"level":"UNKNOWN","explanation":"Forecast precipitation inputs are unavailable."}
    score = 0
    if precipitation_mm is not None:
        score += 2 if precipitation_mm >= 7.5 else 1 if precipitation_mm >= 2 else 0
    if probability is not None:
        score += 2 if probability >= 80 else 1 if probability >= 50 else 0
    level = "HIGH" if score >= 3 else "MEDIUM" if score >= 1 else "LOW"
    return {"level":level,"explanation":"Experimental rainfall rule only; not a landslide forecast or official warning."}
