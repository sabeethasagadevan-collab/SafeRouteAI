
(() => {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000";
  const $ = (id) => document.getElementById(id);

  const state = {
    start: null,
    destination: null,
    routes: [],
    selectedRoute: null,
    watchId: null,
    navActive: false,
    lastSpoken: "",
    lastSpokenAt: 0,
    markers: {},
    polylines: []
  };

  const map = L.map("map", { zoomControl: true }).setView([10.7905, 78.7047], 7);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  setTimeout(() => map.invalidateSize(), 200);

  const startIcon = L.divIcon({
    className: "",
    html: '<div style="width:15px;height:15px;border-radius:50%;background:#0d9c8e;border:3px solid white;box-shadow:0 1px 6px #1235"></div>',
    iconSize: [15, 15],
    iconAnchor: [7, 7]
  });

  const endIcon = L.divIcon({
    className: "",
    html: '<div style="width:15px;height:15px;border-radius:50%;background:#e06468;border:3px solid white;box-shadow:0 1px 6px #1235"></div>',
    iconSize: [15, 15],
    iconAnchor: [7, 7]
  });

  const userIcon = L.divIcon({
    className: "",
    html: '<div style="width:19px;height:19px;border-radius:50%;background:#2d68d8;border:4px solid white;box-shadow:0 0 0 5px #2d68d833"></div>',
    iconSize: [19, 19],
    iconAnchor: [9, 9]
  });

  function showError(message) {
    $("errorBox").textContent = message;
    $("errorBox").classList.remove("hidden");
  }

  function clearError() {
    $("errorBox").classList.add("hidden");
    $("errorBox").textContent = "";
  }

  function setLoading(loading) {
    $("mapLoading").classList.toggle("hidden", !loading);
    $("findButton").disabled = loading;
    $("findButton").querySelector("span").textContent =
      loading ? "Finding routes…" : "Find route";
  }

  function status(text, ok = true) {
    $("connectionStatus").textContent = text;
    document.querySelector(".status-dot").style.background =
      ok ? "#5ad6aa" : "#e5b45d";
  }

  function fmtDistance(m) {
    return m >= 1000
      ? `${(m / 1000).toFixed(1)} km`
      : `${Math.round(m)} m`;
  }

  function fmtDuration(seconds) {
    const mins = Math.max(1, Math.round(seconds / 60));

    return mins >= 60
      ? `${Math.floor(mins / 60)} hr ${mins % 60} min`
      : `${mins} min`;
  }

  function setBadge(id, level) {
    const el = $(id);
    const value = (level || "UNKNOWN").toUpperCase();

    el.textContent = value;

    el.className = "risk-badge " +
      (["LOW", "MEDIUM", "HIGH"].includes(value)
        ? value.toLowerCase()
        : "unknown");
  }

  async function api(path, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 18000);

    try {
      const response = await fetch(API_BASE + path, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...(options.headers || {})
        }
      });

      const body = await response.json().catch(() => ({
        detail: "Invalid response from backend"
      }));

      if (!response.ok) {
        throw new Error(
          body.detail || body.message || `Request failed (${response.status})`
        );
      }

      return body;
    } finally {
      clearTimeout(timeout);
    }
  }

  async function geocode(query) {
    const clean = query.trim();

    if (!clean) {
      throw new Error("Enter a start point and destination.");
    }

    const url =
      "https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=" +
      encodeURIComponent(clean);

    const response = await fetch(url, {
      headers: { "Accept": "application/json" }
    });

    if (!response.ok) {
      throw new Error(
        "Address search is temporarily unavailable. Try a more specific place name."
      );
    }

    const results = await response.json();

    if (!results.length) {
      throw new Error(
        `Could not find "${clean}". Try adding the town or district.`
      );
    }

    return {
      lat: Number(results[0].lat),
      lon: Number(results[0].lon),
      label: results[0].display_name
    };
  }

  function getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        return reject(
          new Error(
            "This browser does not support GPS. Type your starting address instead."
          )
        );
      }

      navigator.geolocation.getCurrentPosition(
        resolve,
        reject,
        {
          enableHighAccuracy: true,
          maximumAge: 0,
          timeout: 20000
        }
      );
    });
  }

  function gpsErrorMessage(err) {
    if (err.code === 1) {
      return "Location permission was denied. Allow location access in your browser's site settings, then try again—or enter your start address manually.";
    }

    if (err.code === 2) {
      return "GPS location is unavailable. Check device location services and try near a window, or enter your address manually.";
    }

    if (err.code === 3) {
      return "GPS took too long to respond. Check device location services and retry.";
    }

    return "Could not get your current location. Enter your start address manually.";
  }

  async function useGPS() {
    clearError();

    $("gpsButton").disabled = true;
    $("gpsMessage").textContent = "Requesting precise device location…";

    try {
      const position = await getCurrentPosition();

      const lat = position.coords.latitude;
      const lon = position.coords.longitude;

      state.start = {
        lat,
        lon,
        label: `Current location (${lat.toFixed(5)}, ${lon.toFixed(5)})`
      };

      $("startInput").value = state.start.label;

      $("gpsMessage").textContent =
        `GPS accuracy about ${Math.round(position.coords.accuracy)} m. Confirm the marker looks correct.`;

      if (state.markers.user) {
        map.removeLayer(state.markers.user);
      }

      state.markers.user = L.marker([lat, lon], {
        icon: userIcon
      }).addTo(map).bindPopup("Your device location");

      map.setView([lat, lon], 15);

    } catch (err) {
      $("gpsMessage").textContent = gpsErrorMessage(err);
      showError(gpsErrorMessage(err));

    } finally {
      $("gpsButton").disabled = false;
    }
  }

  function clearRouteLayers() {
    state.polylines.forEach(l => map.removeLayer(l));
    state.polylines = [];

    ["start", "destination"].forEach(k => {
      if (state.markers[k]) {
        map.removeLayer(state.markers[k]);
        delete state.markers[k];
      }
    });
  }

  function drawRoutes(routes, start, destination) {
    clearRouteLayers();

    const colors = ["#2d68d8", "#9a78d5", "#e19b3e"];

    routes.forEach((route, index) => {
      const line = L.polyline(
        route.geometry.coordinates.map(c => [c[1], c[0]]),
        {
          color: colors[index % colors.length],
          weight: index === 0 ? 6 : 4,
          opacity: index === 0 ? .9 : .55,
          dashArray: index === 0 ? null : "7 8"
        }
      ).addTo(map);

      line.on("click", () => selectRoute(index));

      state.polylines.push(line);
    });

    state.markers.start = L.marker(
      [start.lat, start.lon],
      { icon: startIcon }
    ).addTo(map).bindPopup("Start");

    state.markers.destination = L.marker(
      [destination.lat, destination.lon],
      { icon: endIcon }
    ).addTo(map).bindPopup("Destination");

    const all = state.polylines[0].getBounds();

    state.polylines.slice(1).forEach(l => all.extend(l.getBounds()));

    map.fitBounds(all, {
      padding: [35, 35],
      maxZoom: 14
    });
  }

  function selectRoute(index) {
    state.selectedRoute = index;

    const route = state.routes[index];

    if (!route) return;

    state.polylines.forEach((line, i) => {
      line.setStyle({
        weight: i === index ? 6 : 4,
        opacity: i === index ? .95 : .45,
        dashArray: i === index ? null : "7 8"
      });
    });

    $("distanceValue").textContent = fmtDistance(route.distance);
    $("durationValue").textContent = fmtDuration(route.duration);

    $("routeCount").textContent =
      `${index + 1} of ${state.routes.length}`;

    $("routeNote").textContent =
      route.recommendation ||
      "Route details are based on the routing provider. Risk data may be incomplete.";

    $("routeSummary").classList.remove("hidden");
    $("startNavButton").disabled = false;

    $("mapSubtitle").textContent =
      `Route ${index + 1} selected · ${fmtDistance(route.distance)} · ${fmtDuration(route.duration)}`;
  }

  async function findRoute(start, destination, mode) {
    const body = {
      start: {
        latitude: start.lat,
        longitude: start.lon,
        label: start.label || ""
      },
      destination: {
        latitude: destination.lat,
        longitude: destination.lon,
        label: destination.label || ""
      },
      travel_mode: mode
    };

    let result;

    try {
      result = await api("/api/routes", {
        method: "POST",
        body: JSON.stringify(body)
      });

    } catch (e) {
      // Direct OSRM fallback for basic mapping.
      const profile =
        mode === "walking" ? "foot" :
        mode === "bike" ? "bike" : "driving";

      const url =
        `https://router.project-osrm.org/route/v1/${profile}/${start.lon},${start.lat};${destination.lon},${destination.lat}?overview=full&geometries=geojson&alternatives=true&steps=true`;

      const r = await fetch(url);

      if (!r.ok) {
        throw new Error(
          "Route service unavailable. Start the backend or try again later."
        );
      }

      const data = await r.json();

      if (data.code !== "Ok" || !data.routes?.length) {
        throw new Error(
          "No route found for these locations and travel mode."
        );
      }

      result = {
        routes: data.routes.map(route => ({
          geometry: route.geometry,
          distance: route.distance,
          duration: route.duration,
          recommendation:
            "Basic routing fallback. Traffic and hazard-aware route comparison was not performed because the backend is unavailable."
        })),
        data_status: {
          backend: "offline",
          traffic: "unknown"
        }
      };

      status("Backend offline · basic routes only", false);
    }

    if (!result.routes?.length) {
      throw new Error("No route found between these points.");
    }

    state.routes = result.routes;
    state.selectedRoute = 0;

    drawRoutes(state.routes, start, destination);
    selectRoute(0);

    $("refreshWeatherButton").disabled = false;

    await refreshConditions(start, destination, result);
  }

  async function refreshConditions(start, destination, routeResult) {
    $("weatherMain").textContent = "Loading forecast…";
    $("weatherDetail").textContent =
      "Checking future hourly forecast near the route.";

    $("trafficMain").textContent = "Checking…";
    $("trafficDetail").textContent =
      "Requesting current road-flow readings.";

    $("hazardMain").textContent = "Assessing…";
    $("incidentMain").textContent = "Checking…";

    try {
      const r = await api(
        "/api/weather?latitude=" + start.lat +
        "&longitude=" + start.lon
      );

      renderWeather(r);

    } catch (e) {
      $("weatherMain").textContent = "Forecast unavailable";

      $("weatherDetail").textContent =
        e.message.includes("Failed to fetch")
          ? "Backend is offline; start it to load the forecast."
          : e.message;

      $("rainTimeline").innerHTML = "";
    }

    try {
      const traffic = await api("/api/traffic/analyze", {
        method: "POST",
        body: JSON.stringify({
          coordinates:
            state.routes[state.selectedRoute].geometry.coordinates
        })
      });

      const level = traffic.level || "UNKNOWN";

      setBadge("trafficBadge", level);

      $("trafficMain").textContent =
        level === "UNKNOWN"
          ? "No live reading"
          : `${traffic.average_speed_kmh ?? "—"} km/h avg`;

      $("trafficDetail").textContent =
        traffic.message || "Current flow readings were not available.";

      $("trafficFoot").textContent =
        `${traffic.readings_count || 0} successful readings` +
        `${traffic.observed_at ? " · " + new Date(traffic.observed_at).toLocaleTimeString() : ""} · TomTom`;

    } catch (e) {
      setBadge("trafficBadge", "UNKNOWN");
      $("trafficMain").textContent = "Unavailable";

      $("trafficDetail").textContent =
        "No live traffic result. Missing readings are not treated as low traffic.";
    }

    try {
      const hazard = await api("/api/hazards/analyze", {
        method: "POST",
        body: JSON.stringify({
          latitude: start.lat,
          longitude: start.lon,
          route_coordinates:
            state.routes[state.selectedRoute].geometry.coordinates
        })
      });

      setBadge("hazardBadge", hazard.level || "UNKNOWN");

      $("hazardMain").textContent =
        hazard.level === "UNKNOWN"
          ? "Insufficient data"
          : `${hazard.level} estimate`;

      $("hazardDetail").textContent =
        hazard.explanation ||
        "Not enough verified inputs for a reliable estimate.";

      $("hazardFoot").textContent =
        hazard.source || "Experimental estimate";

    } catch (e) {
      setBadge("hazardBadge", "UNKNOWN");
      $("hazardMain").textContent = "Not available";

      $("hazardDetail").textContent =
        "Could not assess hazards. Check backend status and available forecast data.";
    }

    try {
      const incidents = await api("/api/incidents/search", {
        method: "POST",
        body: JSON.stringify({
          coordinates:
            state.routes[state.selectedRoute].geometry.coordinates
        })
      });

      setBadge("incidentBadge", incidents.level || "UNKNOWN");

      $("incidentMain").textContent =
        incidents.count === 0 && incidents.available
          ? "No reports found"
          : incidents.available
            ? `${incidents.count} report(s)`
            : "Feed unavailable";

      $("incidentDetail").textContent =
        incidents.message ||
        "Incident coverage depends on the configured provider.";

      $("incidentFoot").textContent =
        incidents.source || "No provider configured";

    } catch (e) {
      setBadge("incidentBadge", "UNKNOWN");
      $("incidentMain").textContent = "Unavailable";

      $("incidentDetail").textContent =
        "No verified incident feed is available. This does not mean the road is incident-free.";
    }

    const recommendation =
      routeResult?.recommendation ||
      "Compare available routes manually. A low-risk conclusion is not possible when key data sources are unavailable.";

    $("recommendation").querySelector("p").textContent =
      recommendation;
  }

  function weatherEmoji(code, rain) {
    if (rain > 0.1 ||
      [51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code)) {
      return "🌧️";
    }

    if ([71, 73, 75, 77, 85, 86].includes(code)) {
      return "🌨️";
    }

    if ([45, 48].includes(code)) return "🌫️";
    if ([1, 2, 3].includes(code)) return "⛅";
    if (code === 0) return "☀️";

    return "🌤️";
  }

  function renderWeather(data) {
    if (!data.available || !data.hourly?.length) {
      $("weatherMain").textContent = "Forecast unavailable";

      $("weatherDetail").textContent =
        data.message || "No future forecast values were returned.";

      $("rainTimeline").innerHTML = "";
      return;
    }

    const hours = data.hourly.slice(0, 5);

    const wet = hours.some(h =>
      (h.precipitation_mm || 0) >= 0.5 ||
      (h.precipitation_probability || 0) >= 50
    );

    const total = hours.reduce(
      (s, h) => s + (h.precipitation_mm || 0),
      0
    );

    $("weatherMain").innerHTML =
      `<span class="weather-emoji">${weatherEmoji(hours[0].weather_code, hours[0].precipitation_mm)}</span>` +
      `<span>${wet ? "Rain possible" : "Mostly dry"}</span>`;

    $("weatherDetail").textContent =
      `Next 5 hours: ${total.toFixed(1)} mm forecast precipitation. ` +
      `${hours[0].temperature_c != null
        ? `Temperature around ${Math.round(hours[0].temperature_c)}°C.`
        : ""} Probability is shown where the provider supplies it.`;

    $("rainTimeline").innerHTML = hours.map(h => {
      const time = new Date(h.time).toLocaleTimeString([], {
        hour: "numeric"
      });

      const mm = Number(h.precipitation_mm || 0).toFixed(1);

      const prob =
        h.precipitation_probability == null
          ? "—"
          : `${Math.round(h.precipitation_probability)}%`;

      return `
        <div class="rain-hour">
          <small>${time}</small>
          <b>${mm} mm</b>
          <span>${prob} rain</span>
        </div>
      `;
    }).join("");

    $("weatherSource").textContent =
      `Open-Meteo forecast · ${data.timezone || "local forecast time"}` +
      `${data.fetched_at
        ? " · checked " + new Date(data.fetched_at).toLocaleTimeString()
        : ""}`;
  }

  $("gpsButton").addEventListener("click", useGPS);

  $("routeForm").addEventListener("submit", async e => {
    e.preventDefault();

    clearError();
    setLoading(true);

    try {
      let start = state.start;

      const startText = $("startInput").value.trim();

      if (!startText) {
        throw new Error(
          "Choose a start point using GPS or enter an address."
        );
      }

      if (
        !start ||
        !startText.startsWith("Current location (") ||
        !state.start.label.startsWith("Current location")
      ) {
        start = await geocode(startText);
      } else if (startText !== start.label) {
        start = await geocode(startText);
      }

      const destination = await geocode(
        $("destinationInput").value
      );

      state.start = start;
      state.destination = destination;

      await findRoute(
        start,
        destination,
        document.querySelector(
          'input[name="mode"]:checked'
        ).value
      );

    } catch (err) {
      showError(
        err.message || "Something went wrong while finding the route."
      );

    } finally {
      setLoading(false);
    }
  });

  $("refreshWeatherButton").addEventListener("click", () => {
    if (state.start && state.destination) {
      refreshConditions(
        state.start,
        state.destination,
        {
          recommendation:
            "Data refreshed. Review each source status; unavailable data remains unknown."
        }
      );
    }
  });

  $("voiceButton").addEventListener("click", () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      showError(
        "Voice input is not supported in this browser. Type the destination instead."
      );
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      $("voiceButton").textContent = "…";
    };

    recognition.onend = () => {
      $("voiceButton").textContent = "🎙";
    };

    recognition.onerror = () => {
      showError(
        "Voice input could not be heard. Check microphone permission or type the destination."
      );
    };

    recognition.onresult = event => {
      $("destinationInput").value =
        event.results[0][0].transcript;
    };

    recognition.start();
  });

  function speak(message) {
    if (!("speechSynthesis" in window)) return;

    const now = Date.now();

    if (
      message === state.lastSpoken &&
      now - state.lastSpokenAt < 12000
    ) {
      return;
    }

    state.lastSpoken = message;
    state.lastSpokenAt = now;

    window.speechSynthesis.cancel();

    window.speechSynthesis.speak(
      new SpeechSynthesisUtterance(message)
    );
  }

  function nearestRouteDistance(point, coordinates) {
    // Equirectangular approximation for off-route warning.
    let min = Infinity;

    const latFactor = 111320;
    const lonFactor =
      111320 * Math.cos(point.lat * Math.PI / 180);

    for (let i = 0; i < coordinates.length; i++) {
      const c = coordinates[i];

      const dx = (c[0] - point.lon) * lonFactor;
      const dy = (c[1] - point.lat) * latFactor;

      const d = Math.hypot(dx, dy);

      if (d < min) min = d;
    }

    return min;
  }

  $("startNavButton").addEventListener("click", async () => {
    if (!state.routes.length) return;

    if (!navigator.geolocation) {
      showError("GPS is not supported by this browser.");
      return;
    }

    try {
      const pos = await getCurrentPosition();

      if (state.markers.user) {
        map.removeLayer(state.markers.user);
      }

      state.markers.user = L.marker(
        [pos.coords.latitude, pos.coords.longitude],
        { icon: userIcon }
      ).addTo(map).bindPopup("Your live position");

    } catch (err) {
      showError(gpsErrorMessage(err));
      return;
    }

    state.navActive = true;

    $("startNavButton").disabled = true;
    $("stopNavButton").disabled = false;

    speak("Navigation started. Follow the route shown on the map.");

    state.watchId = navigator.geolocation.watchPosition(
      async pos => {
        const point = {
          lat: pos.coords.latitude,
          lon: pos.coords.longitude
        };

        if (state.markers.user) {
          state.markers.user.setLatLng([
            point.lat,
            point.lon
          ]);
        } else {
          state.markers.user = L.marker(
            [point.lat, point.lon],
            { icon: userIcon }
          ).addTo(map);
        }

        const coords =
          state.routes[state.selectedRoute].geometry.coordinates;

        const distance = nearestRouteDistance(point, coords);

        if (distance > 100) {
          speak(
            "You appear to be away from the selected route. Check the map before continuing."
          );
        }

        if (state.destination) {
          const remaining = nearestRouteDistance(
            {
              lat: state.destination.lat,
              lon: state.destination.lon
            },
            [[point.lon, point.lat]]
          );

          if (remaining < 60) {
            speak("You are near your destination.");
            stopNavigation();
          }
        }

      },

      err => {
        showError(gpsErrorMessage(err));
        stopNavigation();
      },

      {
        enableHighAccuracy: true,
        maximumAge: 1000,
        timeout: 15000
      }
    );
  });

  function stopNavigation() {
    state.navActive = false;

    if (state.watchId !== null) {
      navigator.geolocation.clearWatch(state.watchId);
      state.watchId = null;
    }

    $("startNavButton").disabled = !state.routes.length;
    $("stopNavButton").disabled = true;

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }

  $("stopNavButton").addEventListener("click", stopNavigation);

  api("/health")
    .then(data => status(
      data.status === "ok"
        ? "Backend connected"
        : "Backend connected · limited services",
      true
    ))
    .catch(() => status(
      "Backend offline · basic routes only",
      false
    ));

})();