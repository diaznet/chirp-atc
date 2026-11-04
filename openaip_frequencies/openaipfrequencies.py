"""
Filename: openaipfrequencies.py
Author: Jeremy Diaz
Date: 2025-03-25
Description: Class definition for OpenAIPFrequencies
"""

# Import necessary modules
import pycountry
import json
import time
import urllib.error
import urllib.request
from functools import lru_cache
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic
from shapely.errors import ShapelyError
from shapely.geometry import Point, shape
from shapely.ops import nearest_points
from loguru import logger

from .consts import Consts
from typing import get_args


def channel_to_frequency(channel_mhz: float) -> str:
    """
    Convert an 8.33 kHz channel designator (as published in AIPs) to the actual
    RF center frequency, per ICAO Doc 9718.

    Each 25 kHz block has 4 channel designators spaced 5 kHz apart:
      Position 0 (00/25/50/75): freq = base (25 kHz legacy channel)
      Position 1 (05/30/55/80): freq = base (same center frequency)
      Position 2 (10/35/60/85): freq = base + 8.333 kHz
      Position 3 (15/40/65/90): freq = base + 16.667 kHz

    See references/Doc9718-Vol-II.md and references/understanding-8.33khz.md
    """
    khz = round(channel_mhz * 1000)
    remainder = (khz % 100) % 25
    base_khz = khz - remainder
    offset_khz = {0: 0, 5: 0, 10: 25.0 / 3, 15: 50.0 / 3}.get(remainder, 0)
    return f"{round((base_khz + offset_khz) / 1000.0, 4):.5f}"


@lru_cache(maxsize=None)
def _fetch_export(url: str) -> bytes:
    """
    Download an OpenAIP export, retrying transient failures.

    Results are cached for the lifetime of the process, so several areas of the
    same country only download each export once.
    """
    for attempt in range(1, Consts.HTTP_RETRIES + 1):
        try:
            logger.debug("Fetching OpenAIP export from {} (attempt {})".format(url, attempt))
            with urllib.request.urlopen(url, timeout=Consts.HTTP_TIMEOUT) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            # 4xx errors (e.g. no export for this country) will not fix themselves.
            if e.code < 500 or attempt == Consts.HTTP_RETRIES:
                raise
            error = e
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == Consts.HTTP_RETRIES:
                raise
            error = e
        delay = Consts.HTTP_RETRY_BACKOFF * 2 ** (attempt - 1)
        logger.warning("Fetching {} failed ({}), retrying in {}s".format(url, error, delay))
        time.sleep(delay)
    raise AssertionError("unreachable")


# Nominatim's usage policy allows at most one request per second.
_geocode = RateLimiter(
    Nominatim(user_agent="OpenAIPFrequencies class from chirp-atc (see https://github.com/diaznet/chirp-atc)").geocode,
    min_delay_seconds=1.1,
)


class OpenAIPFrequencies:
    """
    OpenAIPFrequencies class for retrieving aviation frequencies from OpenAIP.

    Attributes:
        country_code (str): ISO alpha-2 country code.
        postal_code (str, optional): Postal code for location-based filtering.
        radius (float, optional): Search radius in kilometers.
        location (tuple, optional): (latitude, longitude) of the search center.

    Methods:
        _validate_country_code(): Validates the provided country code.
        _get_openaip_data(type: str) -> dict: Retrieves OpenAIP data for the given type.
        _get_coordinates_from_postal_code() -> tuple: Gets latitude and longitude from a postal code.
        _is_within_radius(geometry: dict) -> bool: Checks if a location is within the specified radius.
        get_supported_types() -> Consts.OEAIP_SUPPORTED_TYPES: Returns the supported frequency types.
        get_default_radius() -> float: Returns the default radius for searches.
        get_frequencies(type_: Consts.OEAIP_SUPPORTED_TYPES) -> list: Retrieves filtered frequencies.
    """
    def __init__(self, _country_code: str, _postal_code: str = None, _radius: float = None,
                 _location: tuple = None) -> None:
        self.country_code = _country_code
        self._validate_country_code()

        self.postal_code = _postal_code
        if _location is not None:
            self.location = tuple(_location)
        elif self.postal_code:
            self.location = self._get_coordinates_from_postal_code()
        else:
            self.location = None

        if _radius:
            self.radius = _radius
        elif self.location is not None:
            self.radius = Consts.DEFAULT_RADIUS
        else:
            self.radius = None

    def _validate_country_code(self) -> None:
        """
        Validates the given country code by checking its existence in the pycountry database.

        Raises:
            ValueError: If the country code is invalid.
        """
        if not pycountry.countries.get(alpha_2=self.country_code):
            raise ValueError(f"Invalid country code: {self.country_code}")

    def _get_openaip_data(self, type) -> dict:
        """
        Retrieves OpenAIP data for the specified type from the public export storage.

        OpenAIP publishes daily dataset exports on a public HTTPS/S3 endpoint that
        serves anonymous GET requests (see https://www.openaip.net/docs). The file
        for a given country/type is fetched directly over HTTPS.

        Args:
            type (str): The type of data to retrieve (e.g., "airports", "airspaces").

        Returns:
            dict: Parsed JSON data containing OpenAIP information.
        """

        filename = Consts.OEAIP_FILENAME_FORMAT.format(
            country_code=self.country_code.lower(),
            type_code=Consts.OEAIP_TYPES_MAPPING.get(type, ""))
        url = "{base_url}/{filename}".format(
            base_url=Consts.OEAIP_EXPORTS_BASE_URL, filename=filename)
        return json.loads(_fetch_export(url).decode("utf-8"))

    def _get_coordinates_from_postal_code(self) -> tuple:
        """
        Retrieves latitude and longitude based on the provided postal code.

        Returns:
            tuple: A tuple containing latitude and longitude.

        Raises:
            ValueError: If the postal code is invalid.
        """

        # 'postalcode' is the structured-query key Nominatim understands; unknown
        # keys are silently ignored, which would geocode the whole country instead.
        location = _geocode({'postalcode': self.postal_code, 'country': self.country_code})
        if location:
            return (location.latitude, location.longitude)
        else:
            raise ValueError(f"Invalid postal code: {self.postal_code}")

    def _is_within_radius(self, geometry) -> bool:
        """
        Checks whether the given GeoJSON geometry is within the specified radius.

        Points are measured directly. For areas (e.g. airspace polygons), the
        distance is measured to the closest point of the area, and is zero when
        the search center lies inside it.

        Args:
            geometry (dict): A GeoJSON geometry ([longitude, latitude] coordinates).

        Returns:
            bool: True if the location is within the radius, False otherwise.
        """

        if not geometry or not geometry.get("type") or not geometry.get("coordinates"):
            return False

        try:
            geom = shape(geometry)
        except (ShapelyError, ValueError, TypeError, AttributeError, IndexError) as e:
            logger.debug("Unsupported geometry {}: {}".format(geometry.get("type"), e))
            return False

        lat, lon = self.location
        center = Point(lon, lat)
        if geom.contains(center):
            return True
        nearest = nearest_points(geom, center)[0]
        return geodesic(self.location, (nearest.y, nearest.x)).km <= self.radius

    @staticmethod
    def get_supported_types() -> Consts.OEAIP_SUPPORTED_TYPES:
        """
        Returns the supported frequency types defined in the constants.

        Returns:
            Consts.OEAIP_SUPPORTED_TYPES: Supported types of OpenAIP data.
        """

        return Consts.OEAIP_SUPPORTED_TYPES

    @staticmethod
    def get_default_radius() -> float:
        """
        Returns the default search radius.

        Returns:
            float: Default radius in kilometers.
        """

        return Consts.DEFAULT_RADIUS

    def get_frequencies(self, type_: Consts.OEAIP_SUPPORTED_TYPES) -> list:
        """
        Retrieves frequencies based on the specified type and location constraints.

        Args:
            type_ (Consts.OEAIP_SUPPORTED_TYPES): The type of frequencies to retrieve.

        Returns:
            list: A sorted list of unique frequency dictionaries containing frequency, name, and comment.
        """

        options = get_args(Consts.OEAIP_SUPPORTED_TYPES)
        assert type_ in options, f"'{type_}' is not in {options}"
        aip_data = self._get_openaip_data(type_)
        frequencies = []
        for item in aip_data:
            if item['type'] not in Consts.OEAIP_ENABLED_AIRPORT_TYPES[type_]:
                continue
            if self.location is not None and not self._is_within_radius(item.get("geometry")):
                logger.debug("Object {} not in requested radius. Name: '{}'".format(item['_id'], item['name']))
                continue
            logger.debug("Object {} in requested radius. Name: '{}'".format(item['_id'], item['name']))

            # Prefix with 'icaoCode', or 'altIdentifier' if absent. Objects without
            # an identifier (most airspaces) get no prefix, keeping names short.
            prefix = item.get('icaoCode') or item.get('altIdentifier') or ''
            for frequency in item.get('frequencies', []):
                logger.debug('icaoCode: {}, altIdentifier: {}, item name: {}, frequency name: {}, frequency: {}'.format(item.get('icaoCode'), item.get('altIdentifier'), item.get('name'), frequency.get('name'), frequency.get('value')))
                raw_freq = frequency.get('value')
                if raw_freq is None:
                    continue
                frequency_name = ' '.join('{} {}'.format(
                    prefix, frequency.get('name') or item.get('name', '')).split())
                frequencies.append({
                    "frequency": channel_to_frequency(float(raw_freq)),
                    "name": frequency_name,
                    "comment": type_.upper()
                })

        frequencies_noduplicates = [i for n, i in enumerate(frequencies) if i not in frequencies[:n]]
        return sorted(frequencies_noduplicates, key=lambda frequency: frequency['name'])
