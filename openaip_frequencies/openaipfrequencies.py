"""
Filename: openaipfrequencies.py
Author: Jeremy Diaz
Date: 2025-03-25
Description: Class definition for OpenAIPFrequencies
"""

# Import necessary modules
import pycountry
import json
from google.cloud import storage
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from shapely.geometry import Polygon
from loguru import logger

from .consts import Consts
from typing import get_args


class OpenAIPFrequencies:
    """
    OpenAIPFrequencies class for retrieving aviation frequencies from OpenAIP.

    Attributes:
        country_code (str): ISO alpha-2 country code.
        postal_code (str, optional): Postal code for location-based filtering.
        radius (int, optional): Search radius in kilometers.

    Methods:
        _validate_country_code(): Validates the provided country code.
        _get_openaip_data(type: str) -> dict: Retrieves OpenAIP data for the given type.
        _get_coordinates_from_postal_code() -> tuple: Gets latitude and longitude from a postal code.
        _is_within_radius(geometry: dict) -> bool: Checks if a location is within the specified radius.
        get_supported_types() -> Consts.OEAIP_SUPPORTED_TYPES: Returns the supported frequency types.
        get_default_radius() -> float: Returns the default radius for searches.
        get_frequencies(type_: Consts.OEAIP_SUPPORTED_TYPES) -> list: Retrieves filtered frequencies.
    """
    def __init__(self, _country_code: str, _postal_code: str = None, _radius: int = None) -> None:
        self.country_code = _country_code
        self._validate_country_code()

        self.postal_code = _postal_code
        if self.postal_code:
            self.location = self._get_coordinates_from_postal_code()

        if _radius:
            self.radius = _radius
        if not _radius and not _postal_code:
            self.radius = _radius
        else:
            self.radius = Consts.DEFAULT_RADIUS

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
        Retrieves OpenAIP data for the specified type from Google Cloud Storage.

        Args:
            type (str): The type of data to retrieve (e.g., "airports", "airspaces").

        Returns:
            dict: Parsed JSON data containing OpenAIP information.
        """

        storage_client = storage.Client.create_anonymous_client()
        bucket = storage_client.bucket(Consts.GCS_BUCKET_NAME)
        blob = bucket.blob(Consts.OEAIP_FILENAME_FORMAT.format(
            country_code=self.country_code.lower(),
            type_code=Consts.OEAIP_TYPES_MAPPING.get(type, "")))
        return json.loads(blob.download_as_text())

    def _get_coordinates_from_postal_code(self) -> tuple:
        """
        Retrieves latitude and longitude based on the provided postal code.

        Returns:
            tuple: A tuple containing latitude and longitude.

        Raises:
            ValueError: If the postal code is invalid.
        """

        geolocator = Nominatim(user_agent="geo_locator")
        location = geolocator.geocode({'postalcode': self.postal_code, 'country': self.country_code})
        if location:
            return (location.latitude, location.longitude)
        else:
            raise ValueError(f"Invalid postal code: {self.postal_code}")

    def _is_within_radius(self, geometry) -> bool:
        """
        Checks whether the given geographic geometry is within the specified radius.

        Args:
            geometry (dict): A dictionary containing geographic coordinates.

        Returns:
            bool: True if the location is within the radius, False otherwise.
        """

        geom_type = geometry.get("type")
        coordinates = geometry.get("coordinates")

        if not coordinates or not geom_type:
            return False

        if geom_type == "Point":
            point = (coordinates[1], coordinates[0])  # lat, lon
            return geodesic(self.location, point).km <= self.radius

        elif geom_type == "Polygon":
            polygon = Polygon([(lat, lon) for lat, lon in coordinates[0]])
            centroid = polygon.centroid
            return geodesic(self.location, (centroid.y, centroid.x)).km <= self.radius

        return False

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
            if item['type'] in Consts.OEAIP_ENABLED_AIRPORT_TYPES[type_]:
                if (self.postal_code and self._is_within_radius(item.get("geometry"))) or (self.postal_code is None and self.radius is None):
                    logger.debug("Object {} in requested radius. Name: '{}'".format(item['_id'], item['name']))

                    for frequency in item.get('frequencies', []):
                        # Build the frequency name
                        logger.debug('icaoCode: {}, altIdentifier: {}, item name: {}, frequency name: {}, frequency: {}'.format(item.get('icaoCode'), item.get('altIdentifier'), item.get('name'), frequency.get('name'), frequency.get('value')))
                        frequency_name = u' '.join(u"{} {}".format(
                            # Try with 'icaoCode', if not present, use 'altIdentifier'.
                            # Fallback to 'name' of none worked.
                            item.get(
                                'icaoCode',
                                item.get('altIdentifier', '')
                                ),
                            frequency.get('name')).split())
                        frequencies.append({
                            "frequency": frequency.get('value'),
                            "name": frequency_name,
                            "comment": type_.upper()
                        })
                else:
                    logger.debug("Object {} not in requested radius. Name: '{}'".format(item['_id'], item['name']))

        frequencies_noduplicates = [i for n, i in enumerate(frequencies) if i not in frequencies[:n]]
        return sorted(frequencies_noduplicates, key=lambda frequency: frequency['name'])
