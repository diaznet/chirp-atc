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
        'default_value': '5',
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
