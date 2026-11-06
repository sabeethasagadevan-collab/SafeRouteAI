import httpx

async def get_routes(start, destination, travel_mode):
    # Public OSRM routing profiles vary by deployment; OSRM demo endpoint reliably supports driving only.
    # Do not pretend that OSRM's public server supports bike/foot profiles.
    if travel_mode != "car":
        raise ValueError("The configured public OSRM endpoint supports car routing only. Use car mode or configure a provider with bike/walking profiles.")
    coords=f"{start.longitude},{start.latitude};{destination.longitude},{destination.latitude}"
    url=f"https://router.project-osrm.org/route/v1/driving/{coords}"
    async with httpx.AsyncClient(timeout=15) as client:
        response=await client.get(url,params={"overview":"full","geometries":"geojson","alternatives":"true","steps":"true"})
        response.raise_for_status(); data=response.json()
    if data.get("code")!="Ok" or not data.get("routes"): return []
    return [{"geometry":r["geometry"],"distance":r["distance"],"duration":r["duration"],
             "recommendation":"Basic OSRM route. Risk-aware selection is limited until live traffic and verified hazard/incident feeds are available."}
            for r in data["routes"]]
