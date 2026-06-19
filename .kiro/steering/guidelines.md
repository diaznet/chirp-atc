# Development Guidelines

## Code Style & Formatting

### Naming Conventions
- **Files**: snake_case (`get_frequencies.py`, `chirp_model.py`)
- **Classes**: PascalCase (`OpenAIPFrequencies`, `Consts`)
- **Functions/methods**: snake_case (`get_frequencies`, `channel_to_frequency`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_RADIUS`, `GCS_BUCKET_NAME`)
- **Private methods**: prefixed with underscore (`_validate_country_code`, `_get_openaip_data`)
- **Constructor params**: prefixed with underscore (`_country_code`, `_postal_code`)

### Type Annotations
- All method signatures include return type annotations (`: str`, `-> None`, `-> list`)
- Class attributes use type annotations (`DEFAULT_RADIUS: float = 50`)
- `typing.Literal` used for constrained string types
- `typing.get_args()` used to extract literal values at runtime

### Documentation
- Module-level docstrings with filename, author, date, description:
```python
"""
Filename: openaipfrequencies.py
Author: Jeremy Diaz
Date: 2025-03-25
Description: Class definition for OpenAIPFrequencies
"""
```
- Class docstrings list Attributes and Methods
- Method docstrings follow Google style: description, Args, Returns, Raises sections
- Inline comments for non-obvious logic (e.g., airport type codes)

## Architectural Patterns

### Package Structure
- Core logic in `openaip_frequencies/` package with explicit `__init__.py` exports
- Logger disabled at package level, enabled by consumer:
```python
# __init__.py
from loguru import logger
logger.disable("openaip_frequencies")
```

### Configuration as Class
- Constants grouped in a `Consts` class (not a module-level dict or dataclass)
- Extensive inline documentation of magic numbers (airport/airspace type codes)

### Data Model as Dictionary
- CHIRP CSV model defined as a nested dict with metadata (`header_name`, `type`, `default_value`, `mapped_openaip_key`)
- Enables generic mapping from OpenAIP data to CSV output without hardcoding field names

### Pipeline Pattern (get_frequencies.py)
1. Parse CLI args with argparse
2. Iterate countries × postal codes using `itertools.zip_longest`
3. For each combination, instantiate `OpenAIPFrequencies` and call `get_frequencies(type_)`
4. Format output (JSON to stdout or CSV to file)

## Common Idioms

### Deduplication
```python
frequencies_noduplicates = [i for n, i in enumerate(frequencies) if i not in frequencies[:n]]
```

### Fallback Chain for Naming
```python
item.get('icaoCode', item.get('altIdentifier', ''))
```

### Geographic Filtering
- Geocode postal code → lat/lon via Nominatim
- For Points: `geodesic(location, point).km <= radius`
- For Polygons: compute centroid, then distance check

### Logging
- `loguru` throughout (not stdlib logging)
- Debug logs for inclusion/exclusion decisions
- Logger disabled at package level, enabled via CLI `--debug` flag
- Output to stderr (`logger.add(sys.stderr, level=...)`)

## Output Conventions
- CSV files: uppercase extension (`.CSV`), format `{COUNTRY}_{TYPE}{SUFFIX}.CSV`
- UTF-8 encoding with `newline=""` for CSV writer
- Channel designators always converted to 5-decimal-place frequency strings (`f"{freq:.5f}"`)
- TStep always `8.33` for EU airband

## Error Handling
- `ValueError` raised for invalid country codes and postal codes
- `assert` used for type validation in `get_frequencies()`
- No try/except wrapping of GCS calls (fails loudly)

## Dependencies Usage
| Library | Usage Pattern |
|---------|--------------|
| google-cloud-storage | Anonymous client, bucket access, blob download as text |
| pycountry | `pycountry.countries.get(alpha_2=code)` for validation |
| geopy | `Nominatim` geocoder with custom user_agent string |
| shapely | `Polygon` creation from coordinate lists, centroid calculation |
| loguru | `logger.debug()`, `logger.disable()`, `logger.enable()`, `logger.add()` |
| argparse | Standard CLI parsing with `nargs='+'`, `choices`, `action='store_true'` |
