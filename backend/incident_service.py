from config import get_settings

async def search_incidents(coordinates: list[list[float]]) -> dict:
    settings=get_settings()
    if not settings.tomtom_incident_endpoint or not settings.tomtom_api_key:
        return {"available":False,"level":"UNKNOWN","count":None,
                "message":"Incident feed is not configured. No incident-free conclusion can be made.",
                "source":"No incident provider configured","incidents":[]}
    # A provider-specific incident endpoint needs a verified schema and corridor query.
    # Do not guess an endpoint or response schema; return an explicit unavailable state.
    return {"available":False,"level":"UNKNOWN","count":None,
            "message":"Incident endpoint configured, but provider-specific query/schema integration is not enabled in this prototype.",
            "source":"TomTom incident integration pending verified product access","incidents":[]}
