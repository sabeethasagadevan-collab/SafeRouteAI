from datetime import datetime, timezone
import httpx
from config import get_settings

async def get_forecast(latitude: float, longitude: float) -> dict:
    params={"latitude":latitude,"longitude":longitude,"hourly":"temperature_2m,precipitation,precipitation_probability,weather_code",
            "forecast_days":2,"timezone":"auto"}
    try:
        async with httpx.AsyncClient(timeout=get_settings().request_timeout_seconds) as client:
            response=await client.get("https://api.open-meteo.com/v1/forecast",params=params)
            response.raise_for_status(); data=response.json()
        hourly=data.get("hourly",{}); times=hourly.get("time",[])
        # Keep only future timestamps; API times are local in the returned timezone.
        now=datetime.now().astimezone()
        items=[]
        for i,t in enumerate(times):
            try:
                dt=datetime.fromisoformat(t)
                if dt.tzinfo is None:  # Open-Meteo local wall time: retain future hours by comparing local clock
                    if dt < now.replace(tzinfo=None): continue
                elif dt < now: continue
                items.append({"time":t,"temperature_c":at(hourly,"temperature_2m",i),
                              "precipitation_mm":at(hourly,"precipitation",i),
                              "precipitation_probability":at(hourly,"precipitation_probability",i),
                              "weather_code":at(hourly,"weather_code",i)})
            except (ValueError, TypeError): continue
        return {"available":bool(items),"hourly":items[:12],"timezone":data.get("timezone","local time"),
                "fetched_at":datetime.now(timezone.utc).isoformat(),"source":"Open-Meteo",
                "message":None if items else "No future hourly forecast values were returned."}
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        return {"available":False,"hourly":[],"message":"Weather provider is temporarily unavailable.","source":"Open-Meteo"}
def at(obj,key,index):
    values=obj.get(key,[])
    return values[index] if index<len(values) else None
