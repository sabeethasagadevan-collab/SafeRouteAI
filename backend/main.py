from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config import get_settings
from database import init_db, get_db
from models import RouteHistory
from schemas import RouteRequest, TrafficRequest, IncidentRequest, HazardRequest
from route_service import get_routes
from traffic_service import analyze_traffic
from weather_service import get_forecast
from incident_service import search_incidents
from hazard_service import analyze_hazard
from prediction_service import model_status

settings=get_settings()
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app=FastAPI(title=settings.app_name,version="1.0.0",description="Route planning prototype with explicit live-data availability states.",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])

@app.get("/")
async def root():
    return {"name":settings.app_name,"status":"ok","docs":"/docs"}
@app.get("/health")
async def health():
    return {"status":"ok","database":"configured","tomtom_key_configured":bool(settings.tomtom_api_key),
            "incident_feed_configured":bool(settings.tomtom_incident_endpoint and settings.tomtom_api_key),
            "ml_model":model_status(),"checked_at":datetime.now(timezone.utc).isoformat()}
@app.post("/api/routes")
async def routes(payload:RouteRequest,db:Session=Depends(get_db)):
    try: result=await get_routes(payload.start,payload.destination,payload.travel_mode)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc))
    except Exception: raise HTTPException(status_code=502,detail="Routing provider is unavailable. Try again later.")
    if not result: raise HTTPException(status_code=404,detail="No route found for these locations.")
    for route in result:
        db.add(RouteHistory(start_label=payload.start.label,destination_label=payload.destination.label,
            travel_mode=payload.travel_mode,distance_m=route["distance"],duration_s=route["duration"],data_status="partial"))
    try: db.commit()
    except Exception: db.rollback()
    return {"routes":result,"data_status":{"traffic":"not yet used for route selection","hazards":"partial/unknown","incidents":"unknown"},
            "recommendation":"Compare route options. Current traffic and verified hazard data are not sufficient to guarantee a safest route."}
@app.get("/api/weather")
async def weather(latitude:float,longitude:float):
    if not -90<=latitude<=90 or not -180<=longitude<=180: raise HTTPException(status_code=422,detail="Invalid coordinates.")
    return await get_forecast(latitude,longitude)
@app.post("/api/traffic/analyze")
async def traffic(payload:TrafficRequest):
    return await analyze_traffic(payload.coordinates)
@app.post("/api/incidents/search")
async def incidents(payload:IncidentRequest):
    return await search_incidents(payload.coordinates)
@app.post("/api/hazards/analyze")
async def hazards(payload:HazardRequest):
    # Fetch forecast at requested coordinate and use next-hour precipitation only if present.
    forecast=await get_forecast(payload.latitude,payload.longitude)
    hours=forecast.get("hourly",[])
    mm=payload.precipitation_mm
    probability=payload.precipitation_probability
    if hours:
        if mm is None: mm=hours[0].get("precipitation_mm")
        if probability is None: probability=hours[0].get("precipitation_probability")
    result=analyze_hazard(mm,probability)
    result["forecast_available"]=forecast.get("available",False)
    return result
@app.post("/api/predictions/risk")
async def risk_prediction(payload:dict):
    return {"available":False,"level":"UNKNOWN","method":"rule_based_fallback","message":"A trained prediction model is not included until a verified labelled dataset is supplied.","model":model_status()}
@app.get("/api/history")
async def history(limit:int=20,db:Session=Depends(get_db)):
    limit=max(1,min(limit,100))
    rows=db.query(RouteHistory).order_by(RouteHistory.id.desc()).limit(limit).all()
    return {"items":[{"id":r.id,"start":r.start_label,"destination":r.destination_label,"travel_mode":r.travel_mode,
        "distance_m":r.distance_m,"duration_s":r.duration_s,"created_at":r.created_at.isoformat() if r.created_at else None} for r in rows]}
@app.delete("/api/history")
async def clear_history(db:Session=Depends(get_db)):
    db.query(RouteHistory).delete();db.commit()
    return {"deleted":True}
