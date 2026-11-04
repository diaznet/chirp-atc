import csv
from pathlib import Path

from loguru import logger

from openaip_frequencies.consts import Consts

chirp_csv_model: dict = {
    'location': {
        'header_name': 'Location',
        'type': int,
        'default_value': '',
    },
    'name': {
        'header_name': 'Name',
        'type': str,
        'default_value': '',
        'mapped_openaip_key': 'name'
    },
    'frequency': {
        'header_name': 'Frequency',
        'type': str,
        'default_value': '',
        'mapped_openaip_key': 'frequency'
    },
    'duplex': {
        'header_name': 'Duplex',
        'type': str,
        'default_value': '',
    },
    'offset': {
        'header_name': 'Offset',
        'type': str,
        'default_value': '0.600000',
    },
    'tone': {
        'header_name': 'Tone',
        'type': str,
        'default_value': '',
    },
    'rtonefreq': {
        'header_name': 'rToneFreq',
        'type': str,
        'default_value': '88.5',
    },
    'cToneFreq': {
        'header_name': 'cToneFreq',
        'type': str,
        'default_value': '88.5',
    },
    'dtcscode': {
        'header_name': 'DtcsCode',
        'type': str,
        'default_value': '23',
    },
    'dtcspolarity': {
        'header_name': 'DtcsPolarity',
        'type': str,
        'default_value': 'NN',
    },
    'rxdtcscode': {
        'header_name': 'RxDtcsCode',
        'type': str,
        'default_value': '23',
    },
    'crossmode': {
        'header_name': 'CrossMode',
        'type': str,
        'default_value': 'Tone->Tone',
    },
    'mode': {
        'header_name': 'Mode',
        'type': str,
        'default_value': 'AM',
    },
    'tstep': {
        'header_name': 'TStep',
        'type': str,
        'default_value': '8.33',
    },
    'skip': {
        'header_name': 'Skip',
        'type': str,
        'default_value': '',
    },
    'power': {
        'header_name': 'Power',
        'type': str,
        'default_value': '50W',
    },
    'comment': {
        'header_name': 'Comment',
        'type': str,
        'default_value': '',
        'mapped_openaip_key': 'comment'

    },
    'urcall': {
        'header_name': 'URCALL',
        'type': str,
        'default_value': '',
    },
    'rpt1call': {
        'header_name': 'RPT1CALL',
        'type': str,
        'default_value': '',
    },
    'rpt2call': {
        'header_name': 'RPT2CALL',
        'type': str,
        'default_value': '',
    },
    'dvcode': {
        'header_name': 'DVCODE',
        'type': str,
        'default_value': '',
    }
}


def csv_filename(country_code: str, type_: str, suffix: str = '') -> str:
    """Release file name for a country/type/area, e.g. 'CH_AIRPORTS_GENEVA-LEMAN.CSV'."""
    return '{}_{}{}.csv'.format(country_code, type_, suffix).upper()


def to_chirp_rows(frequencies: list) -> list:
    """Map frequency dictionaries to CHIRP CSV rows, numbering memory locations from 0."""
    rows = []
    for index, freq_data in enumerate(frequencies):
        row = {}
        for key, config in chirp_csv_model.items():
            if key == 'location':
                row[config['header_name']] = index
            elif 'mapped_openaip_key' in config and config['mapped_openaip_key'] in freq_data:
                row[config['header_name']] = freq_data[config['mapped_openaip_key']]
            else:
                row[config['header_name']] = config['default_value']
        rows.append(row)
    return rows


def write_chirp_csv(path, frequencies: list, warn_if_too_large: bool = True) -> bool:
    """
    Write frequencies to a CHIRP CSV file.

    Warns when the file holds more channels than a Quansheng radio can store,
    unless warn_if_too_large is False (e.g. for full country lists).
    Returns False (and writes nothing) when there are no frequencies.
    """
    if not frequencies:
        return False
    path = Path(path)
    if warn_if_too_large and len(frequencies) > Consts.CHIRP_MAX_CHANNELS:
        logger.warning("{} has {} channels, more than the {} a Quansheng radio can store".format(
            path.name, len(frequencies), Consts.CHIRP_MAX_CHANNELS))
    rows = to_chirp_rows(frequencies)
    with open(path, mode="w", encoding='utf-8', newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Wrote {} channels to {}".format(len(rows), path))
    return True
