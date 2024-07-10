import os
import unittest
from typing import List, Optional
from unittest.mock import Mock, patch

import requests
from fastapi import HTTPException
from pydantic import BaseModel
from requests.models import Response

import app
from app.routes.schemas import *
from app.services.attractions_service import *


class Location:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude


class Attraction:
    def __init__(
        self,
        attraction_id: str,
        attraction_name: str,
        city: Optional[str] = None,
        country: Optional[str] = None,
        location: Optional[Location] = None,
        photo: Optional[str] = None,
        avg_rating: Optional[float] = None,
        liked_count: int = 0,
        types: List[str] = [],
        formatted_address: str = None,
        google_maps_uri: str = None,
        editorial_summary: str = None,
    ):
        self.attraction_id = attraction_id
        self.attraction_name = attraction_name
        self.city = city
        self.country = country
        self.location = location
        self.photo = photo
        self.avg_rating = avg_rating
        self.liked_count = liked_count
        self.types = types
        self.formatted_address = formatted_address
        self.google_maps_uri = google_maps_uri
        self.editorial_summary = editorial_summary


class TestSortAttractionsByRating(unittest.TestCase):

    def setUp(self):
        self.attraction1 = Mock(spec=Attraction)
        self.attraction1.attraction_id = "C21QW24FF3"
        self.attraction1.attraction_name = "Obelisco"
        self.attraction1.avg_rating = 2.5

        self.attraction2 = Mock(spec=Attraction)
        self.attraction2.attraction_id = "C21QW24FF2"
        self.attraction2.attraction_name = "Planetario"
        self.attraction2.avg_rating = 3.5

        self.attraction3 = Mock(spec=Attraction)
        self.attraction3.attraction_id = "C21QW24FF1"
        self.attraction3.attraction_name = "Barrio Chino"
        self.attraction3.avg_rating = 4.5

        self.attractions = [self.attraction1, self.attraction2, self.attraction3]

    def test_sort_by_rating(self):
        sorted_attractions = sort_attractions_by_rating(self.attractions)
        self.assertEqual(
            [attraction.attraction_id for attraction in sorted_attractions],
            ["C21QW24FF1", "C21QW24FF2", "C21QW24FF3"],
        )

    def test_sort_with_none_ratings(self):
        self.attraction1.avg_rating = None
        self.attraction2.avg_rating = 2.0
        self.attraction3.avg_rating = None
        sorted_attractions = sort_attractions_by_rating(self.attractions)
        self.assertEqual(
            [attraction.attraction_id for attraction in sorted_attractions],
            ["C21QW24FF2", "C21QW24FF3", "C21QW24FF1"],
        )

    def test_sort_empty_list(self):
        sorted_attractions = sort_attractions_by_rating([])
        self.assertEqual(sorted_attractions, [])


class TestGetAttractionById(unittest.TestCase):
    @patch("app.services.attractions_service.requests.get")
    @patch("os.getenv", return_value="fake_api_key")
    def test_get_attraction_by_id_success(self, mock_getenv, mock_requests_get):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "1",
            "displayName": {"text": "Obelisco"},
            "location": {"latitude": 23.2222, "longitude": -54.333},
            "types": ["type1", "type2"],
            "addressComponents": [
                {"types": ["locality"], "longText": "Buenos Aires"},
                {"types": ["country"], "longText": "Argentina"},
            ],
            "photos": [{"name": "photo1"}],
            "rating": 4.5,
            "formattedAddress": "Santa Fe, Buenos Aires",
            "googleMapsUri": "http://maps.google.com/obelisco",
            "editorialSummary": {"text": "A great place to visit!"},
        }
        mock_requests_get.return_value = mock_response

        result = get_attraction_by_id("1")

        self.assertEqual(result.attraction_id, "1")

    @patch("app.services.attractions_service.requests.get")
    @patch("os.getenv", return_value="fake_api_key")
    def test_get_attraction_by_id_failure(self, mock_getenv, mock_requests_get):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        with self.assertRaises(HTTPException) as context:
            get_attraction_by_id("1")

        self.assertEqual(context.exception.status_code, 404)


class TestGetNearbyAttractions(unittest.TestCase):

    @patch("app.services.attractions_service.requests.post")
    @patch("os.getenv", return_value="fake_api_key")
    def test_get_nearby_attractions_success(self, mock_getenv, mock_requests_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "id": "1",
                    "displayName": {"text": "Obelisco"},
                    "location": {"latitude": 10.0, "longitude": 20.0},
                    "types": ["type1", "type2"],
                    "addressComponents": [
                        {"types": ["locality"], "longText": "Buenos Aires"},
                        {"types": ["country"], "longText": "Argentina"},
                    ],
                    "photos": [{"name": "photo1"}],
                    "rating": 4.5,
                    "formattedAddress": "Santa Fe 2999, Buenos Aires",
                    "googleMapsUri": "http://maps.google.com/obelisco",
                    "editorialSummary": {"text": "A great place to visit!"},
                },
                {
                    "id": "2",
                    "displayName": {"text": "Planetario"},
                    "location": {"latitude": 30.0, "longitude": 40.0},
                    "types": ["type3", "type4"],
                    "addressComponents": [
                        {"types": ["locality"], "longText": "Buenos Aires"},
                        {"types": ["country"], "longText": "Argentina"},
                    ],
                    "photos": [{"name": "photo2"}],
                    "rating": 3.5,
                    "formattedAddress": "Santa Fe 2999, Buenos Aires",
                    "googleMapsUri": "http://maps.google.com/planetario",
                    "editorialSummary": {"text": "Another great place!"},
                },
            ]
        }
        mock_requests_post.return_value = mock_response

        formatted_attractions = get_nearby_attractions(10.0, 20.0, 5000, ["restaurant"])

        called_url = mock_requests_post.call_args[0][0]
        self.assertEqual(
            called_url, "https://places.googleapis.com/v1/places:searchNearby"
        )

        self.assertEqual(len(formatted_attractions), 2)
        self.assertEqual(formatted_attractions[0].attraction_id, "1")
        self.assertEqual(formatted_attractions[1].attraction_id, "2")

    @patch("app.services.attractions_service.requests.post")
    @patch("os.getenv", return_value="fake_api_key")
    def test_get_nearby_attractions_failure(self, mock_getenv, mock_requests_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.content = b"API Error"
        mock_requests_post.return_value = mock_response

        with self.assertRaises(HTTPException):
            get_nearby_attractions(10.0, 20.0, 5000, ["restaurant"])

        called_url = mock_requests_post.call_args[0][0]
        self.assertEqual(
            called_url, "https://places.googleapis.com/v1/places:searchNearby"
        )


class TestSearchAttractions(unittest.TestCase):

    @patch("app.services.attractions_service.requests.post")
    @patch("os.getenv", return_value="fake_api_key")
    def test_search_attractions_without_location(self, mock_getenv, mock_requests_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "id": "1",
                    "displayName": {"text": "Obelisco"},
                    "location": {"latitude": 10.0, "longitude": 20.0},
                    "types": ["type1", "type2"],
                    "addressComponents": [
                        {"types": ["locality"], "longText": "Buenos Aires"},
                        {"types": ["country"], "longText": "Argentina"},
                    ],
                    "photos": [{"name": "photo1"}],
                    "rating": 4.5,
                    "formattedAddress": "Santa Fe 2999, Buenos Aires",
                    "googleMapsUri": "http://maps.google.com/obelisco",
                    "editorialSummary": {"text": "A great place to visit!"},
                },
                {
                    "id": "2",
                    "displayName": {"text": "Planetario"},
                    "location": {"latitude": 30.0, "longitude": 40.0},
                    "types": ["type3", "type4"],
                    "addressComponents": [
                        {"types": ["locality"], "longText": "Buenos Aires"},
                        {"types": ["country"], "longText": "Argentina"},
                    ],
                    "photos": [{"name": "photo2"}],
                    "rating": 3.5,
                    "formattedAddress": "Santa Fe 2999, Buenos Aires",
                    "googleMapsUri": "http://maps.google.com/planetario",
                    "editorialSummary": {"text": "Another great place!"},
                },
            ]
        }
        mock_requests_post.return_value = mock_response

        formatted_attractions = search_attractions("restaurant", "restaurant")

        called_url = mock_requests_post.call_args[0][0]
        self.assertEqual(
            called_url, "https://places.googleapis.com/v1/places:searchText"
        )

        self.assertEqual(len(formatted_attractions), 2)
        self.assertEqual(formatted_attractions[0].attraction_id, "1")
        self.assertEqual(formatted_attractions[1].attraction_id, "2")

    @patch("app.services.attractions_service.requests.post")
    @patch("os.getenv", return_value="fake_api_key")
    def test_search_attractions_with_location(self, mock_getenv, mock_requests_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "id": "1",
                    "displayName": {"text": "Obelisco"},
                    "location": {"latitude": 10.0, "longitude": 20.0},
                    "types": ["type1", "type2"],
                    "addressComponents": [
                        {"types": ["locality"], "longText": "Buenos Aires"},
                        {"types": ["country"], "longText": "Argentina"},
                    ],
                    "photos": [{"name": "photo1"}],
                    "rating": 4.5,
                    "formattedAddress": "Santa Fe 2999, Buenos Aires",
                    "googleMapsUri": "http://maps.google.com/obelisco",
                    "editorialSummary": {"text": "A great place to visit!"},
                },
                {
                    "id": "2",
                    "displayName": {"text": "Planetario"},
                    "location": {"latitude": 30.0, "longitude": 40.0},
                    "types": ["type3", "type4"],
                    "addressComponents": [
                        {"types": ["locality"], "longText": "Buenos Aires"},
                        {"types": ["country"], "longText": "Argentina"},
                    ],
                    "photos": [{"name": "photo2"}],
                    "rating": 3.5,
                    "formattedAddress": "Santa Fe 2999, Buenos Aires",
                    "googleMapsUri": "http://maps.google.com/planetario",
                    "editorialSummary": {"text": "Another great place!"},
                },
            ]
        }
        mock_requests_post.return_value = mock_response

        formatted_attractions = search_attractions("museum", "museum", 40.0, -75.0)

        called_url = mock_requests_post.call_args[0][0]
        self.assertEqual(
            called_url, "https://places.googleapis.com/v1/places:searchText"
        )

        self.assertEqual(len(formatted_attractions), 2)
        self.assertEqual(formatted_attractions[0].attraction_id, "1")
        self.assertEqual(formatted_attractions[1].attraction_id, "2")

    @patch("app.services.attractions_service.requests.post")
    @patch("os.getenv", return_value="fake_api_key")
    def test_search_attractions_api_error(self, mock_getenv, mock_requests_post):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.content = b"API Error"
        mock_requests_post.return_value = mock_response

        with self.assertRaises(HTTPException):
            search_attractions("restaurant", "restaurant")

        called_url = mock_requests_post.call_args[0][0]
        self.assertEqual(
            called_url, "https://places.googleapis.com/v1/places:searchText"
        )
