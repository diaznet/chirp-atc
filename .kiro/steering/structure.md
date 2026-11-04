# Project Structure

## Directory Layout
```
chirp-atc/
├── .kiro/steering/          # Kiro steering files
├── .github/workflows/       # CI/CD pipeline (CSV generation + release)
├── img/                     # Documentation images
├── openaip_frequencies/     # Core library package
│   ├── __init__.py          # Package exports
│   ├── consts.py            # Constants (export base URL, frequency types, CHIRP defaults)
│   └── openaipfrequencies.py # Main class: fetch, parse, filter, convert frequencies
├── tests/                   # pytest suite (AIRAC, 8.33 kHz conversion, geo filtering)
├── airac.py                 # AIRAC cycle calculation (used by CI to tag releases)
├── areas.yaml               # Area definitions (country, postal code, coordinates, radius)
├── build_all.py             # Batch generation of all CSVs from areas.yaml (used by CI)
├── chirp_model.py           # CHIRP CSV data model and file writer
├── get_frequencies.py       # CLI entry point (argparse-based)
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Test dependencies
└── README.md                # Documentation
```

## Core Components

### get_frequencies.py (CLI Entry Point)
- Parses command-line arguments (country, type, postal code, radius, output format, suffix)
- Orchestrates the pipeline: fetch → filter → convert → output

### openaip_frequencies/ (Library Package)
- **openaipfrequencies.py**: Main `OpenAIPFrequencies` class
  - Fetches JSON data from OpenAIP's public export storage (HTTPS)
  - Parses airport and airspace frequency data
  - Applies geographic filtering (postal code + radius using geopy/shapely)
  - Converts 8.33 kHz channel designators to actual RF frequencies
- **consts.py**: Configuration constants (export base URL, frequency type mappings, CHIRP field defaults)
- **__init__.py**: Package-level exports

### chirp_model.py (Output Layer)
- Defines the CHIRP CSV row model/dataclass
- Handles CSV file writing in CHIRP-compatible format
- Manages memory channel numbering and field formatting

### areas.yaml (Configuration)
- Declarative area definitions used by GitHub Actions workflow
- Each area: country code, name, postal code, radius, reference city, latitude/longitude
- Coordinates are fixed so CI doesn't depend on Nominatim; the postal code is only geocoded when they're missing

## Architectural Pattern
Pipeline architecture: **Data Source (OpenAIP HTTPS exports) → Fetch → Parse → Filter (geo) → Convert (8.33kHz) → Format (CHIRP CSV) → Output**

## CI/CD
- Releases follow the AIRAC cycle (28 days); `airac.py` computes the current cycle (YYNN ident, effective date)
- The workflow runs daily but only generates/publishes on a schedule when release `airac-YYNN` doesn't exist yet
- Push to main updates the current cycle's release in place (`gh release upload --clobber`); other branches upload workflow artifacts only
- `build_all.py` generates all country and area CSVs from areas.yaml in one process (each export downloaded once) and exits non-zero on any failure
- Tests live in `tests/` (pytest) and run before generation
