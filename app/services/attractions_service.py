import os

import boto3
import requests
from fastapi import HTTPException

from app.services.logger import Logger

from . import mappers


def sort_attractions_by_rating(attractions):
    return sorted(
        attractions,
        key=lambda x: (x.avg_rating if x.avg_rating is not None else 0),
        reverse=True,
    )


def get_attraction_by_id(attraction_id: str) -> dict:
    Logger().info("API CALL!")

    url = f"https://places.googleapis.com/v1/places/{attraction_id}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
        "X-Goog-FieldMask": "displayName,id,addressComponents,photos,location",
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    return mappers.map_to_attraction_db(attraction=response.json())


def get_nearby_attractions(
    latitude: float, longitude: float, radius: float, attraction_types
):
    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
        "X-Goog-FieldMask": "places.displayName,places.id,places.addressComponents,places.photos,places.location",
    }

    data = {
        "includedTypes": attraction_types,
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius,
            }
        },
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    formatted_attractions = []

    if "places" in response.json().keys():
        for attraction in response.json()["places"]:
            formatted_attractions.append(
                mappers.map_to_attraction_db(attraction=attraction)
            )

    return formatted_attractions


def search_attractions(query: str, type, latitude, longitude):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
        "X-Goog-FieldMask": "places.displayName,places.id,places.addressComponents,places.photos,places.location,places.types",
    }

    if latitude and longitude:
        response = requests.post(
            url,
            json={
                "textQuery": query,
                "includedType": type,
                "locationBias": {
                    "circle": {
                        "center": {"latitude": latitude, "longitude": longitude},
                        "radius": 500.0,
                    }
                },
                "rankPreference": "RELEVANCE",
            },
            headers=headers,
        )
    else:
        response = requests.post(
            url, json={"textQuery": query, "includedType": type}, headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    formatted_attractions = []

    if "places" in response.json().keys():
        for attraction in response.json()["places"]:
            formatted_attractions.append(
                mappers.map_to_attraction_db(attraction=attraction)
            )

    return formatted_attractions


def get_feed(user_id: int, page: int, size: int):
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    dynamodb = session.resource("dynamodb", region_name="us-east-2")

    table_name = "recommendations"
    table = dynamodb.Table(table_name)

    key = {"user_id": user_id}
    response = table.get_item(Key=key)
    recommendations = response.get("Item")

    if not recommendations:
        Logger().info("No attractions were found")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "No attractions were found",
            },
        )

    return recommendations["attraction_ids"][page * size : (page + 1) * size]


def autocomplete(query: str, attraction_types):
    url = "https://places.googleapis.com/v1/places:autocomplete"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
    }

    response = requests.post(
        url,
        json={"input": query, "includedPrimaryTypes": attraction_types},
        headers=headers,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    formatted_response = []

    if "suggestions" in response.json().keys():
        for attraction in response.json()["suggestions"]:
            formatted_response.append(
                {
                    "attraction_id": attraction["placePrediction"]["placeId"],
                    "attraction_name": attraction["placePrediction"]["text"]["text"],
                }
            )

    return formatted_response
