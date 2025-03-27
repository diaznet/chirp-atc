"""
Filename: openaipfrequencies.py
Author: Jeremy Diaz
Date: 2025-03-25
Description: Class definition for OpenAIPFrequencies
"""

# Import necessary modules
from openaip_frequencies.openaipfrequencies import OpenAIPFrequencies
from chirp_model import chirp_csv_model

import json
import argparse
import csv
import sys
from typing import get_args
from loguru import logger
from itertools import zip_longest


def main() -> None:
    """
    Main function to parse command-line arguments, fetch frequency data from OpenAIP,
    and output results in the requested format.
    """

    supported_frequency_types_list = get_args(OpenAIPFrequencies.get_supported_types())
    default_radius = get_args(OpenAIPFrequencies.get_default_radius())
    supported_frequency_types_str = ', '.join(repr(value) for value in supported_frequency_types_list)

    parser = argparse.ArgumentParser(description="Get frequencies for a specific country from openAIP.")

    # Add arguments
    parser.add_argument('-c', '--country',
                        required=True,
                        default=[],
                        type=str,
                        help='ISO alpha-2 country codes.',
                        nargs='+'
                        )
    parser.add_argument('-t', '--type',
                        required=False,
                        default=supported_frequency_types_list,
                        type=str,
                        help='Types of frequencies. Supported values are {}. Defaults to all.'.format(supported_frequency_types_str),
                        nargs='+'
                        )
    parser.add_argument('-p', '--postal-code',
                        required=False,
                        default=[],
                        type=str,
                        help='Postal code, to narrow down the output to a specifc area.',
                        nargs='+'
                        )
    parser.add_argument('-r', '--radius',
                        required=False,
                        type=float,
                        help='Radius in kilometers around postal code, to narrow down the output to a specifc area. If postal code is specified, default is {}.'.format(default_radius)
                        )
    parser.add_argument('-o', '--output',
                        required=False,
                        default='Console-JSON',
                        type=str,
                        help='Output type. Default is Console-JSON.',
                        choices=['CHIRP-CSV', 'Console-JSON']
                        )
    parser.add_argument('-s', '--suffix',
                        required=False,
                        default='',
                        type=str,
                        help='When writing a file, append the specified string to the filename.',
                        )
    parser.add_argument('-d', '--debug',
                        required=False,
                        default=False,
                        help='Enable debug on STDERR.',
                        action='store_true'
                        )

    # Parse the arguments
    args = parser.parse_args()

    if args.debug:
        level = 'DEBUG'
    else:
        level = 'INFO'
    logger.add(sys.stdout, level=level)

    for country, postal_code in zip_longest(args.country, args.postal_code, fillvalue=None):
        freq = OpenAIPFrequencies(country, postal_code, args.radius)
        for type in args.type:
            frequencies = freq.get_frequencies(type)
            if args.output == "Console-JSON":
                print(json.dumps(frequencies, indent=2))
            if args.output == 'CHIRP-CSV':
                rows = []
                for index, freq_data in enumerate(frequencies, start=0):
                    row = {}
                    for key, config in chirp_csv_model.items():
                        if key == 'location':
                            row[config['header_name']] = index  # Assign incremental location
                        elif 'mapped_openaip_key' in config and config['mapped_openaip_key'] in freq_data:
                            row[config['header_name']] = freq_data[config['mapped_openaip_key']]
                        else:
                            row[config['header_name']] = config['default_value']
                    rows.append(row)
                with open('{}_{}{}.csv'.format(country, type, args.suffix).upper(), mode="w", encoding='utf-8', newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)


if __name__ == "__main__":
    main()
