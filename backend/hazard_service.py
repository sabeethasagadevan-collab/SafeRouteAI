from route_analyzer import estimate_weather_risk

def analyze_hazard(precipitation_mm=None, precipitation_probability=None):
    result=estimate_weather_risk(precipitation_mm,precipitation_probability)
    result["source"]="Experimental rainfall-only rule; slope, geology and verified landslide records are not connected."
    result["available"]=result["level"]!="UNKNOWN"
    return result
