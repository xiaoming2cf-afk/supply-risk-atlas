# USGS Earthquake Lite

`UsgsEarthquakeLiteConnector` is a fixture-first connector for public
earthquake metadata.

Fixture promotion emits `natural_hazard_event` summaries with event time,
latitude, longitude, magnitude, affected region, provenance URL, payload hash,
source refs, confidence, and license/terms ref.

Live polling is disabled by default and not implemented for app startup, tests,
CI, or Render startup. The connector is hazard context only and is not a warning
or prediction service.

