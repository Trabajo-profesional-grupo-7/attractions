from fastapi.testclient import TestClient
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch
from pytest_mock import mocker
from unittest.mock import ANY

from app.main import app


client = TestClient(app)


def test_save_attraction(mocker):
    mock_db_save_function = mocker.patch("app.db.crud.save_attraction")

    mock_db_save_function.return_value = {
        "status": "success",
        "message": "Attraction saved",
    }

    response = client.post(
        "/attractions/save", json={"user_id": 1, "attraction_id": "test_attraction_id"}
    )

    assert response.status_code == 201
    assert response.json() == {"status": "success", "message": "Attraction saved"}

    mock_db_save_function.assert_called_once_with(
        user_id=1, attraction_id="test_attraction_id", db=ANY
    )
