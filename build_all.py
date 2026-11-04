"""
Filename: build_all.py
Description: Generate every CHIRP CSV defined in areas.yaml (one set per
country, plus one set per area) in a single process.

Each OpenAIP export is downloaded once and shared by all areas of a country.
Areas are located by their 'latitude'/'longitude' in areas.yaml; the postal
code is only geocoded when coordinates are missing.

Exits non-zero if any file could not be generated, so CI never publishes a
partial release.
"""

import argparse
import sys
from pathlib import Path
from typing import get_args

import yaml
from loguru import logger

from chirp_model import csv_filename, write_chirp_csv
from openaip_frequencies.openaipfrequencies import OpenAIPFrequencies


def area_suffix(area: dict) -> str:
    """File name suffix for an area, e.g. '_Geneva-Leman'."""
    return '_{}'.format(area['name'].replace(' ', '_'))


def area_location(area: dict):
    """(latitude, longitude) from areas.yaml, or None to geocode the postal code."""
    if 'latitude' in area and 'longitude' in area:
        return (float(area['latitude']), float(area['longitude']))
    return None


def build(areas_file: Path, output_dir: Path, types: list) -> tuple:
    """Generate all CSVs. Returns (written file names, failure descriptions)."""
    with open(areas_file, encoding='utf-8') as file:
        config = yaml.safe_load(file)

    output_dir.mkdir(parents=True, exist_ok=True)
    written, failures = [], []

    for country in config['countries']:
        country_code = country['country_code']
        jobs = [('', lambda: OpenAIPFrequencies(country_code))]
        for area in country.get('areas', []):
            jobs.append((area_suffix(area), lambda area=area: OpenAIPFrequencies(
                country_code,
                area.get('reference_postal_code'),
                area.get('radius'),
                area_location(area))))

        for suffix, make_source in jobs:
            label = '{}{}'.format(country_code, suffix)
            try:
                source = make_source()
            except Exception as e:
                logger.error("{}: cannot locate area: {}".format(label, e))
                failures.append('{} (location)'.format(label))
                continue
            for type_ in types:
                filename = csv_filename(country_code, type_, suffix)
                try:
                    frequencies = source.get_frequencies(type_)
                    # Country-wide lists are expected to exceed the radio's memory.
                    if write_chirp_csv(output_dir / filename, frequencies, warn_if_too_large=bool(suffix)):
                        written.append(filename)
                    else:
                        logger.info("{}: no frequencies, skipped".format(filename))
                except Exception as e:
                    logger.error("{}: {}".format(filename, e))
                    failures.append(filename)

    return written, failures


def main() -> None:
    supported_types = list(get_args(OpenAIPFrequencies.get_supported_types()))
    parser = argparse.ArgumentParser(description="Generate all CHIRP CSVs defined in an areas file.")
    parser.add_argument('--areas', type=Path, default=Path('areas.yaml'), help='Areas definition file.')
    parser.add_argument('--output-dir', type=Path, default=Path('dist'), help='Directory for generated CSVs.')
    parser.add_argument('--type', nargs='+', default=supported_types, choices=supported_types,
                        help='Types of frequencies. Defaults to all.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug on STDERR.')
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, level='DEBUG' if args.debug else 'INFO')

    written, failures = build(args.areas, args.output_dir, args.type)
    logger.info("Generated {} files in {}".format(len(written), args.output_dir))
    if failures:
        logger.error("{} failure(s): {}".format(len(failures), ', '.join(failures)))
        sys.exit(1)
    if not written:
        logger.error("No files generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
