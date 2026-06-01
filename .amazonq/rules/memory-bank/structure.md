# Project Structure

## Directory Layout
```
chirp-atc/
├── .amazonq/rules/          # Amazon Q rules and memory bank
├── .github/workflows/       # CI/CD pipeline (CSV generation + release)
├── img/                     # Documentation images
├── openaip_frequencies/     # Core library package
│   ├── __init__.py          # Package exports
│   ├── consts.py            # Constants (GCS bucket, frequency types, CHIRP defaults)
│   └── openaipfrequencies.py # Main class: fetch, parse, filter, convert frequencies
├── areas.yaml               # Area definitions (country, postal code, radius)
├── chirp_model.py           # CHIRP CSV data model and file writer
├── get_frequencies.py       # CLI entry point (argparse-based)
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

## Core Components

### get_frequencies.py (CLI Entry Point)
- Parses command-line arguments (country, type, postal code, radius, output format, suffix)
- Orchestrates the pipeline: fetch → filter → convert → output

### openaip_frequencies/ (Library Package)
- **openaipfrequencies.py**: Main `OpenAIPFrequencies` class
  - Fetches JSON data from OpenAIP's GCS bucket
  - Parses airport and airspace frequency data
  - Applies geographic filtering (postal code + radius using geopy/shapely)
  - Converts 8.33 kHz channel designators to actual RF frequencies
- **consts.py**: Configuration constants (bucket ID, frequency type mappings, CHIRP field defaults)
- **__init__.py**: Package-level exports

### chirp_model.py (Output Layer)
- Defines the CHIRP CSV row model/dataclass
- Handles CSV file writing in CHIRP-compatible format
- Manages memory channel numbering and field formatting

### areas.yaml (Configuration)
- Declarative area definitions used by GitHub Actions workflow
- Each area: country code, name, postal code, radius, reference city

## Architectural Pattern
Pipeline architecture: **Data Source (GCS) → Fetch → Parse → Filter (geo) → Convert (8.33kHz) → Format (CHIRP CSV) → Output**

## CI/CD
- GitHub Actions workflow runs weekly (Monday 06:00 UTC) and on push to main
- Generates CSVs for all countries and all area-specific subsets from areas.yaml
- Publishes as GitHub Release assets
