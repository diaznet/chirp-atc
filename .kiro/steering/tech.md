# Technology Stack

## Language
- Python 3.x (no specific minor version pinned)

## Dependencies (requirements.txt)
| Package | Version | Purpose |
|---------|---------|---------|
| pycountry | 24.6.1 | ISO country code validation and lookup |
| geopy | 2.x | Geocoding postal codes (rate-limited, 1 req/s) and geodesic distances |
| shapely | 2.x | Geographic filtering (distance to points and airspace polygons) |
| loguru | 0.7.x | Structured logging with debug mode |
| PyYAML | 6.x | Parsing areas.yaml in build_all.py |

Dev/test dependencies are in `requirements-dev.txt` (pytest). Run tests with `python -m pytest`.

## Build & Run Commands
```bash
# Install
pip install -r requirements.txt

# Run (examples)
python get_frequencies.py -c CH -o CHIRP-CSV
python get_frequencies.py -c FR -p 69000 -r 150 -o CHIRP-CSV -s _Rhone-Alpes
python get_frequencies.py -c GB -o Console-JSON -d

# Help
python get_frequencies.py -h
```

## Output Formats
- **CHIRP-CSV**: Radio-ready CSV files (uppercase .CSV extension), named `{COUNTRY}_{TYPE}.CSV`
- **Console-JSON**: JSON printed to stdout for inspection/debugging

## Key Technical Detail: 8.33 kHz Conversion
Channel designators from OpenAIP are converted to actual RF frequencies using ICAO Doc 9718 mapping. The CHIRP CSV `TStep` field is set to `8.33` for EU airband.

## Data Source
- OpenAIP public export storage (anonymous HTTPS GET): `https://storage.openaip.net/openaip-system-exports/`
- Files: `{country_code}_apt.json` (airports), `{country_code}_asp.json` (airspaces)
- Fetched via Python stdlib `urllib.request` (no external client library required)

## CI/CD
- GitHub Actions (ubuntu-latest, Python 3.12)
- Releases follow the AIRAC cycle: tag `airac-YYNN`, published on the cycle's effective date
- Scheduled daily at 06:00 UTC; a run is a no-op when the current cycle's release already exists
- Triggers: schedule, push to any branch, manual dispatch
- Push/dispatch on main updates the current cycle's release in place; other branches upload workflow artifacts only
- Generate everything with `python build_all.py --output-dir dist`
