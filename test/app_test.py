import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

import app
from app.main import app as router

client = TestClient(router)


class TestMetadata(unittest.TestCase):
    @patch("app.routes.routes.get_metadata")
    def test_get_metadata_success(self, mock_get_metadata):
        mock_get_metadata.return_value = {
            "attraction_types": ["Museum", "Park", "Cafe"]
        }
        response = client.get("/metadata")
        self.assertEqual(response.status_code, 200)


class TestSearchAttractions(unittest.TestCase):

    def test_search_attractions_status_code_201(self):
        response = client.post("/attractions/search", json={"query": "museum"})

        self.assertEqual(response.status_code, 201)

    def test_search_attractions_status_code_201_with_type_filter(self):
        response = client.post(
            "/attractions/search", json={"query": "park", "type": "park"}
        )

        self.assertEqual(response.status_code, 201)

    def test_search_attractions_status_code_201_with_location_filter(self):
        response = client.post(
            "/attractions/search",
            json={"query": "restaurant", "latitude": 40.7128, "longitude": -74.0060},
        )
        self.assertEqual(response.status_code, 201)


class TestGetAttractionLocation(unittest.TestCase):

    @patch("app.routes.routes.requests.post")
    def test_get_attraction_location_status_code_200(self, mock_post):
        mock_post.return_value.status_code = 200

        response = client.get("/attractions/location?text=museum")

        self.assertEqual(response.status_code, 200)

    @patch("app.routes.routes.requests.post")
    def test_get_attraction_location_status_code_404(self, mock_post):
        mock_post.return_value.status_code = 404

        response = client.get("/attractions/location?text=museum")

        self.assertEqual(response.status_code, 404)


class TestGetFeed(unittest.TestCase):

    @patch("app.routes.routes.get_feed")
    def test_get_feed_status_code_200(self, mock_get_feed):
        mock_get_feed.return_value = [
            "csad2321das3",
            "csdf6542vfv5",
            "fdsf43hdfs45",
        ]

        response = client.get("/attractions/recommendations/1?page=0&size=10")

        self.assertEqual(response.status_code, 200)


class TestSaveAttraction(unittest.TestCase):

    @patch("app.routes.routes.get_attraction_by_id_and_add_it_if_not_cached")
    @patch("app.routes.routes.crud.get_saved_attraction")
    @patch("app.routes.routes.crud.save_attraction")
    def test_save_attraction_success(
        self, mock_save_attraction, mock_get_saved_attraction, mock_get_attraction_by_id
    ):
        mock_get_attraction_by_id.return_value = None
        mock_get_saved_attraction.return_value = None
        mock_save_attraction.return_value = {"user_id": 1, "attraction_id": "abc1"}

        request_data = {
            "user_id": 1,
            "attraction_id": "fsdf354fsd",
        }
        response = client.post("/attractions/save", json=request_data)

        self.assertEqual(response.status_code, 201)

    @patch("app.routes.routes.get_attraction_by_id_and_add_it_if_not_cached")
    @patch("app.routes.routes.crud.get_saved_attraction")
    def test_save_attraction_already_saved(
        self, mock_get_saved_attraction, mock_get_attraction_by_id
    ):
        mock_get_attraction_by_id.return_value = None
        mock_get_saved_attraction.return_value = {
            "user_id": 1,
            "attraction_id": "adew2645gfd3",
        }
        request_data = {
            "user_id": 1,
            "attraction_id": "adew2645gfd3",
        }
        response = client.post("/attractions/save", json=request_data)

        self.assertEqual(response.status_code, 404)
