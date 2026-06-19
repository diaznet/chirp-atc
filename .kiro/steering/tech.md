# Technology Stack

## Language
- Python 3.x (no specific minor version pinned)

## Dependencies (requirements.txt)
| Package | Version | Purpose |
|---------|---------|---------|
| google-cloud-storage | 3 | Fetch frequency data from OpenAIP's public GCS bucket |
| pycountry | 24.6.1 | ISO country code validation and lookup |
| geopy | latest | Geocoding postal codes to lat/lon coordinates |
| shapely | latest | Geographic filtering (point-in-circle radius checks) |
| loguru | latest | Structured logging with debug mode |

## Additional CI Dependency
- `pyyaml` — installed in GitHub Actions to parse areas.yaml (not in requirements.txt)

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
- OpenAIP public GCS bucket: `29f98e10-a489-4c82-ae5e-489dbcd4912f`
- Files: `{country_code}_apt.json` (airports), `{country_code}_asp.json` (airspaces)

## CI/CD
- GitHub Actions (ubuntu-latest, Python 3.x)
- Scheduled: weekly on Monday at 06:00 UTC
- Triggers: push to main or any branch
- Artifacts: uploaded as GitHub Release assets (main/schedule) or workflow artifacts (branches)
