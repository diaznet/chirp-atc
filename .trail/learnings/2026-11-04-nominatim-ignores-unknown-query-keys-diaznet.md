---
title: Nominatim ignores unknown query keys
author: Diaznet
date: 2026-11-04
branch: feature/airac-releases
cost: { minutes: 1, tokens: 1946 }
id: l-c07f57b5
scope: repo
status: active
src: agent
touches:
  - "openaip_frequencies/openaipfrequencies.py#OpenAIPFrequencies._get_coordinates_from_postal_code"
  - areas.yaml
  - "build_all.py#area_location"
---

Nominatim structured queries silently ignore keys they don't recognise. The original code sent {'postalCode': ..., 'country': ...} (camelCase), so Nominatim dropped the postcode and returned the country's centroid: every area CSV released up to AIRAC 2611 was centred on the same point per country (all CH areas near Sarnen, all GB areas in Cumbria). The working key is 'postalcode' (lowercase). Even with it, GB outward codes (EC1A, B1, ...) and FR 69000 (Lyon) / 54000 (Nancy) return nothing, so those areas use their reference city's coordinates. That is why areas.yaml carries fixed latitude/longitude per area and build_all.py only geocodes when they're missing: CI shouldn't depend on Nominatim (1 req/s policy, CI IPs get blocked). If you add an area, geocode it once by hand and check the returned address is the city, not just the country name.
