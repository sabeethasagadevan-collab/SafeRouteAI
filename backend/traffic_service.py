from datetime import datetime, timezone
import httpx
from config import get_settings
from route_analyzer import classify_traffic

async def analyze_traffic(coordinates: list[list[float]]) -> dict:
    settings = get_settings()
    if not settings.tomtom_api_key:
        return {"available": False, "level": "UNKNOWN", "readings_count": 0,
                "message": "TomTom API key is not configured. No live traffic conclusion is available.",
                "source": "TomTom Traffic Flow API"}
    # Sample up to 8 points to keep calls bounded. TomTom flow API accepts lat,lon.
    step = max(1, len(coordinates)//8)
    samples = coordinates[::step][:8]
    readings=[]
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        for lon,lat in samples:
            try:
                response=await client.get(settings.tomtom_flow_endpoint,params={"key":settings.tomtom_api_key,"point":f"{lat},{lon}","unit":"KMPH"})
                if response.status_code in (401,403):
                    return {"available":False,"level":"UNKNOWN","readings_count":len(readings),"message":"TomTom rejected the key or the product is not enabled.","source":"TomTom Traffic Flow API"}
                response.raise_for_status()
                flow=response.json().get("flowSegmentData",{})
                current=flow.get("currentSpeed"); free=flow.get("freeFlowSpeed")
                if current is not None and free is not None and float(free)>0:
                    readings.append((float(current),float(free)))
            except (httpx.HTTPError, ValueError, TypeError):
                continue
    if not readings:
        return {"available":False,"level":"UNKNOWN","readings_count":0,"message":"No valid road-flow readings were returned for the sampled route points.","source":"TomTom Traffic Flow API"}
    relative=sum(min(1.0,c/f) for c,f in readings)/len(readings)
    level=classify_traffic(relative)
    return {"available":True,"level":level,"average_speed_kmh":round(sum(c for c,f in readings)/len(readings),1),
            "readings_count":len(readings),"observed_at":datetime.now(timezone.utc).isoformat(),
            "message":f"{len(readings)} route-point readings received. Classification uses current/free-flow speed ratio.",
            "source":"TomTom Traffic Flow API"}
