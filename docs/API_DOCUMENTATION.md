# API Documentation

Start backend then open `http://127.0.0.1:8000/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic status |
| GET | `/health` | Backend, API-key and model status |
| POST | `/api/routes` | Route request; car profile on configured OSRM endpoint |
| GET | `/api/weather?latitude=...&longitude=...` | Future hourly Open-Meteo forecast |
| POST | `/api/traffic/analyze` | Sample route coordinates against TomTom Flow if configured |
| POST | `/api/incidents/search` | Incident-feed availability response |
| POST | `/api/hazards/analyze` | Experimental rainfall-only hazard estimate |
| POST | `/api/predictions/risk` | Explicit ML-unavailable status until model integration is ready |
| GET | `/api/history` | Recent route history |
| DELETE | `/api/history` | Clear route history |

Coordinates in route geometry use GeoJSON `[longitude, latitude]`. Request schemas are validated with Pydantic. Errors return standard HTTP status codes and a `detail` message.
