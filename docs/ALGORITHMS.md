# Algorithms and data interpretation

## Route scoring
Illustrative weights: traffic 0.35, hazard 0.35, travel time 0.20, weather 0.10. Each input is normalized to 0–100. The implementation excludes unavailable factors and renormalizes the weights of available factors; it also returns missing factor names. This is not a validated safety model and is not currently used to automatically pick a route.

## Traffic classification
TomTom current speed divided by free-flow speed: at least 0.75 = LOW congestion, 0.40–0.749 = MEDIUM, below 0.40 = HIGH. No valid readings = UNKNOWN. These thresholds are configurable starting points, not official universal definitions.

## Rainfall rule
The prototype uses next-hour forecast precipitation and probability as a simple demonstration rule. It does not account for soil, slope, geology, antecedent rainfall, drainage, or official hazard-zone data. It must not be called a landslide prediction.

## GPS accuracy
The frontend requests high-accuracy browser geolocation, disables cached positions, displays the reported accuracy, and does not silently substitute an IP-derived location. GPS can still be inaccurate indoors or when device location services are disabled.

## ML pipeline
A generic Random Forest scaffold accepts a labelled CSV, holds out a test split and reports classification metrics. It is not meaningful until a valid real dataset and suitable feature schema are supplied. For future-event prediction, use chronological/time-based validation and avoid leakage.
