from typing import Literal


class Consts():
    """
    Consts class containing constant values for OpenAIP data handling.

    Attributes:
        DEFAULT_RADIUS (float): Default search radius in kilometers.
        GCS_BUCKET_NAME (str): Google Cloud Storage bucket ID for storing OpenAIP data.
        OEAIP_SUPPORTED_TYPES (Literal): Supported object types, limited to 'airports' and 'airspaces'.
        OEAIP_TYPES_MAPPING (dict): Mapping of general object types to OpenAIP-specific type codes.
        OEAIP_FILENAME_FORMAT (str): Format string for filenames stored in GCS.
        OEAIP_ENABLED_AIRPORT_TYPES (dict): Dictionary specifying enabled airport and airspace types.
    """

    DEFAULT_RADIUS: float = 50
    GCS_BUCKET_NAME: str = "29f98e10-a489-4c82-ae5e-489dbcd4912f"    # Bucket ID, see https://www.openaip.net/docs
    OEAIP_SUPPORTED_TYPES = Literal["airports", "airspaces"]          # Supported Object types
    OEAIP_TYPES_MAPPING: dict = {                                         # Corresponding types in OpenAIP
        "airports": "apt",
        "airspaces": "asp",
    }
    OEAIP_FILENAME_FORMAT:  str = "{country_code}_{type_code}.json"         # File format in GCS
    OEAIP_ENABLED_AIRPORT_TYPES: dict = {
        # Selected Airport types
        # See schema at https://docs.openaip.net/#/Airports/get_airports__id_
        #   0: Airport (civil/military)
        #   1: Glider Site
        #   2: Airfield Civil
        #   3: International Airport
        #   4: Heliport Military
        #   5: Military Aerodrome
        #   6: Ultra Light Flying Site
        #   7: Heliport Civil
        #   8: Aerodrome Closed
        #   9: Airport resp. Airfield IFR
        #   10: Airfield Water
        #   11: Landing Strip
        #   12: Agricultural Landing Strip
        #   13: Altiport
        "airports": [0, 2, 3, 9, 13],
        # Selected Airspace types
        #   0: Other
        #   1: Restricted
        #   2: Danger
        #   3: Prohibited
        #   4: Controlled Tower Region (CTR)
        #   5: Transponder Mandatory Zone (TMZ)
        #   6: Radio Mandatory Zone (RMZ)
        #   7: Terminal Maneuvering Area (TMA)
        #   8: Temporary Reserved Area (TRA)
        #   9: Temporary Segregated Area (TSA)
        #   10: Flight Information Region (FIR)
        #   11: Upper Flight Information Region (UIR)
        #   12: Air Defense Identification Zone (ADIZ)
        #   13: Airport Traffic Zone (ATZ)
        #   14: Military Airport Traffic Zone (MATZ)
        #   15: Airway
        #   16: Military Training Route (MTR)
        #   17: Alert Area
        #   18: Warning Area
        #   19: Protected Area
        #   20: Helicopter Traffic Zone (HTZ)
        #   21: Gliding Sector
        #   22: Transponder Setting (TRP)
        #   23: Traffic Information Zone (TIZ)
        #   24: Traffic Information Area (TIA)
        #   25: Military Training Area (MTA)
        #   26: Control Area (CTA)
        #   27: ACC Sector (ACC)
        #   28: Aerial Sporting Or Recreational Activity
        #   29: Low Altitude Overflight Restriction
        #   30: Military Route (MRT)
        #   31: TSA/TRA Feeding Route (TFR)
        #   32: VFR Sector
        #   33: FIS Sector
        #   34: Lower Traffic Area (LTA)
        #   35: Upper Traffic Area (UTA)
        "airspaces": [n for n in range(36)]
    }
