
# SafeRoute AI

**AI-Based Local Emergency & Hazard Alert System with Smart Route Optimization and Voice Navigation**

SafeRoute AI helps users find routes and review available weather, optional traffic, and hazard context. It deliberately shows `UNKNOWN` when a feed is missing instead of claiming that a road is safe.

## Important implementation status
- **Map and route display:** Leaflet + OpenStreetMap tiles; public OSRM demo route service is configured for car routing.
- **GPS:** Browser geolocation with high accuracy requested, no stale cached position, accuracy shown, and no silent IP-location fallback.
- **Address search:** OpenStreetMap Nominatim for user-entered places; use responsibly and follow its usage policy.
- **Weather:** Open-Meteo future hourly forecast, including precipitation and probability where supplied.
- **Traffic:** TomTom Flow integration is optional and needs your own API key and product access.
- **Incidents:** Not live-integrated yet. The app explicitly reports the feed as unavailable rather than inventing reports.
- **Hazard:** Experimental rainfall-only rule; not a landslide forecast and not an official warning.
- **ML:** Training scaffold only. No trained model or real labelled dataset is included.
- **Navigation:** Live GPS marker and basic off-route warning. This is not full turn-by-turn navigation; public OSRM setup is not a production navigation service.

## Requirements
- Windows 11
- Python 3.11 or 3.12 recommended
- VS Code
- Internet connection for external map/route/weather services
- Optional TomTom developer account/API key for traffic flow

## Windows setup (PowerShell)

### 1. Check Python
Open a terminal in the extracted `SafeRouteAI` folder:
```powershell
python --version
```
If it says Python was not found, install Python 3.12 from https://www.python.org/downloads/windows/ and enable **Add python.exe to PATH** during installation. Close and reopen VS Code, then check `python --version` again. If `py` works, `py -3.12 --version` is also valid.

### 2. Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```
If PowerShell blocks activation, use this for the current terminal only:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Or skip activation and use `.venv\Scripts\python.exe -m pip ...`.

### 3. Configure optional traffic key
```powershell
Copy-Item backend\.env.example backend\.env
```
Open `backend/.env` and enter your own `TOMTOM_API_KEY`. Leave it blank if you do not have access. Never share or upload the `.env` file. Incident integration remains unavailable until its provider endpoint and schema are verified and implemented.

### 4. Start the backend
From the project root:
```powershell
cd backend
..\.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
If the path command is awkward, activate `.venv` first and run:
```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000/docs` to test the API. SQLite database is created automatically in the backend folder.

### 5. Start the frontend
Open a **second** PowerShell terminal at the project root:
```powershell
python -m http.server 5500 --directory frontend
```
Open `http://127.0.0.1:5500`. The browser needs `localhost` or HTTPS for geolocation. Click the GPS button and grant permission, or type the start address manually.

### 6. Test a route
- Choose GPS or enter a starting address.
- Enter a destination such as `Madurai Railway Junction`.
- Select Car and click Find route.
- Review route distance/time and map.
- Review forecast timestamps and rainfall.
- If the backend is offline, the frontend can try a basic OSRM route fallback; weather/traffic cards will remain unavailable.
- Bike/walking routes are not enabled on the configured public OSRM service. The backend returns a clear validation error instead of falsely claiming support.

### 7. Run tests
From project root with `.venv` active:
```powershell
python -m pytest -q
```
Tests use local logic and FastAPI test client; no paid API key is required. Weather API network calls are not part of these unit tests.

## Troubleshooting
- **GPS wrong or approximate:** Check the blue location marker and reported accuracy. Laptop browsers may estimate location from Wi-Fi and be inaccurate. Turn on Windows Settings → Privacy & security → Location and browser site permission. Retry outdoors. This app does not silently replace GPS with an IP estimate. If still wrong, type the location manually.
- **GPS denied:** Browser address bar → site permissions → Location → Allow, then reload.
- **Python not found:** Install Python with PATH enabled, restart VS Code, and verify `python --version`. Avoid Microsoft Store aliases if they redirect unexpectedly.
- **Backend not reachable:** Ensure the terminal running Uvicorn remains open; check `http://127.0.0.1:8000/health`.
- **Rain card unavailable:** Open `http://127.0.0.1:8000/api/weather?latitude=9.9252&longitude=78.1198`. Open-Meteo needs internet access. Forecast values are future hourly estimates, not observed rain.
- **Traffic UNKNOWN:** Add a valid TomTom key with traffic-flow product access. Missing data is intentionally not labelled LOW.
- **Map blank:** Check internet access and browser console. OpenStreetMap tiles require network access.
- **Voice input:** Browser support varies; allow microphone permission. Type destination if unavailable.

## Architecture and modules
See `docs/PROJECT_OVERVIEW.md`, `docs/API_DOCUMENTATION.md`, and `docs/ALGORITHMS.md`.

## Privacy and safety
Precise GPS is processed in the browser for route requests and is not automatically saved as a permanent device-location record. Route labels and route metrics are stored in local SQLite route history; use `DELETE /api/history` to clear that history. API requests send coordinates to the configured routing/weather/traffic providers. Do not use this prototype as a substitute for emergency services or official hazard alerts.

## ML training scaffold
Use only a documented, appropriately licensed real labelled dataset:
```powershell
python ml\train_model.py --csv path\to\verified_dataset.csv --target label
```
The dataset must have numeric feature columns and a labelled target column. The generic scaffold is not a ready-made landslide or accident model. Review the saved report and validate against an appropriate time-based holdout before any real use.

## Project contents
- `frontend/` — responsive UI, GPS, map, route, forecast cards, voice controls
- `backend/` — FastAPI, provider services, SQLite models and route analysis
- `ml/` — training/evaluation/prediction scaffolding
- `tests/` — automated tests
- `docs/` — project and algorithm documentation

