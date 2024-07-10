import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from pydantic import BaseModel, ValidationError

import app
from app.routes.schemas import *


class TestSaveAttractionSchema(unittest.TestCase):

    def test_create_instance(self):
        attraction = SaveAttraction(user_id=1, attraction_id="Csad132dad3f21de")
        self.assertEqual(attraction.user_id, 1)
        self.assertEqual(attraction.attraction_id, "Csad132dad3f21de")

    def test_invalid_user_id(self):
        with self.assertRaises(ValidationError):
            SaveAttraction(user_id="abc", attraction_id="Csad132dad3f21de")

    def test_invalid_attraction_id(self):
        with self.assertRaises(ValidationError):
            SaveAttraction(user_id=1, attraction_id=23)


class TestMarkAsDoneAttractionSchema(unittest.TestCase):

    def test_create_instance(self):
        attraction = MarkAsDoneAttraction(user_id=1, attraction_id="Csad132dad3f21de")
        self.assertEqual(attraction.user_id, 1)
        self.assertEqual(attraction.attraction_id, "Csad132dad3f21de")

    def test_invalid_user_id(self):
        with self.assertRaises(ValidationError):
            SaveAttraction(user_id="abc", attraction_id="Csad132dad3f21de")

    def test_invalid_attraction_id(self):
        with self.assertRaises(ValidationError):
            SaveAttraction(user_id=1, attraction_id=23)


class TestLikeAttractionSchema(unittest.TestCase):

    def test_create_instance(self):
        attraction = LikeAttraction(user_id=1, attraction_id="Csad132dad3f21de")
        self.assertEqual(attraction.user_id, 1)
        self.assertEqual(attraction.attraction_id, "Csad132dad3f21de")

    def test_invalid_user_id(self):
        with self.assertRaises(ValidationError):
            LikeAttraction(user_id="abc", attraction_id="Csad132dad3f21de")

    def test_invalid_attraction_id(self):
        with self.assertRaises(ValidationError):
            LikeAttraction(user_id=1, attraction_id=23)


class TestAddRatingSchema(unittest.TestCase):

    def test_create_instance(self):
        rating_instance = AddRating(
            user_id=1, attraction_id="Csad132dad3f21de", rating=5
        )
        self.assertEqual(rating_instance.user_id, 1)
        self.assertEqual(rating_instance.attraction_id, "Csad132dad3f21de")
        self.assertEqual(rating_instance.rating, 5)

    def test_invalid_user_id(self):
        with self.assertRaises(ValidationError):
            AddRating(user_id="abc", attraction_id="Csad132dad3f21de", rating=4)

    def test_invalid_attraction_id(self):
        with self.assertRaises(ValidationError):
            AddRating(user_id=1, attraction_id=23)

    def test_invalid_rating(self):
        with self.assertRaises(ValidationError):
            AddRating(user_id=1, attraction_id="Csad132dad3f21de", rating="five")


class TestAddCommentSchema(unittest.TestCase):

    def test_create_instance(self):
        comment_instance = AddComment(
            user_id=1, attraction_id="Csad132dad3f21de", comment="Great place!"
        )
        self.assertEqual(comment_instance.user_id, 1)
        self.assertEqual(comment_instance.attraction_id, "Csad132dad3f21de")
        self.assertEqual(comment_instance.comment, "Great place!")

    def test_invalid_user_id(self):
        with self.assertRaises(ValidationError):
            AddComment(
                user_id="abc", attraction_id="Csad132dad3f21de", comment="Nice place"
            )

    def test_invalid_attraction_id(self):
        with self.assertRaises(ValidationError):
            AddComment(user_id="abc", attraction_id=12, comment="Nice place")

    def test_missing_comment(self):
        with self.assertRaises(ValidationError):
            AddComment(user_id=1, attraction_id="Csad132dad3f21de")


class TestDeleteCommentSchema(unittest.TestCase):

    def test_create_instance(self):
        comment_instance = DeleteComment(comment_id=1)
        self.assertEqual(comment_instance.comment_id, 1)

    def test_invalid_comment_id(self):
        with self.assertRaises(ValidationError):
            DeleteComment(comment_id="abc")


class TestUpdateCommentSchema(unittest.TestCase):

    def test_create_instance(self):
        comment_instance = UpdateComment(comment_id=1, new_comment="Updated comment")
        self.assertEqual(comment_instance.comment_id, 1)
        self.assertEqual(comment_instance.new_comment, "Updated comment")

    def test_invalid_comment_id(self):
        with self.assertRaises(ValidationError):
            UpdateComment(comment_id="abc", new_comment="Updated comment")


class TestSearchAttractionsByTextSchema(unittest.TestCase):

    def test_create_instance(self):
        search_instance = SearchAttractionsByText(query="beach")
        self.assertEqual(search_instance.query, "beach")

    def test_invalid_query_type(self):
        with self.assertRaises(ValidationError):
            SearchAttractionsByText(query=1)


class TestAutocompleteAttractionsSchema(unittest.TestCase):

    def test_create_instance(self):
        autocomplete_instance = AutocompleteAttractions(query="beach")
        self.assertEqual(autocomplete_instance.query, "beach")

    def test_invalid_query_type(self):
        with self.assertRaises(ValidationError):
            AutocompleteAttractions(query=1)


class TestScheduleAttractionSchema(unittest.TestCase):

    def test_create_instance(self):
        schedule_instance = ScheduleAttraction(
            user_id=1,
            attraction_id="Csad132dad3f21de",
            datetime=datetime(2024, 7, 6, 14, 30),
        )
        self.assertEqual(schedule_instance.user_id, 1)
        self.assertEqual(schedule_instance.attraction_id, "Csad132dad3f21de")
        self.assertEqual(schedule_instance.datetime, datetime(2024, 7, 6, 14, 30))

    def test_invalid_user_id(self):
        with self.assertRaises(ValidationError):
            ScheduleAttraction(
                user_id="abc",
                attraction_id="Csad132dad3f21de",
                datetime=datetime(2024, 7, 6, 14, 30),
            )


class TestUnscheduleAttractionSchema(unittest.TestCase):

    def test_create_instance(self):
        unschedule_instance = UnscheduleAttraction(schedule_id=1)
        self.assertEqual(unschedule_instance.schedule_id, 1)

    def test_invalid_schedule_id_type(self):
        with self.assertRaises(ValidationError):
            UnscheduleAttraction(schedule_id="abc")


class TestUpdateScheduleSchema(unittest.TestCase):

    def test_create_instance(self):
        update_instance = UpdateSchedule(
            schedule_id=1,
            new_datetime=datetime(2024, 7, 6, 14, 30),
        )
        self.assertEqual(update_instance.schedule_id, 1)
        self.assertEqual(update_instance.new_datetime, datetime(2024, 7, 6, 14, 30))

    def test_invalid_schedule_id(self):
        with self.assertRaises(ValidationError):
            UpdateSchedule(schedule_id="abc", new_datetime=datetime(2024, 7, 6, 14, 30))


class TestCommentSchema(unittest.TestCase):

    def test_create_instance(self):
        comment_instance = Comment(
            comment_id=1, user_id=1, comment="Great place!", user_name="Username"
        )
        self.assertEqual(comment_instance.comment_id, 1)
        self.assertEqual(comment_instance.user_id, 1)
        self.assertEqual(comment_instance.comment, "Great place!")
        self.assertEqual(comment_instance.user_name, "Username")

    def test_invalid_comment_id(self):
        with self.assertRaises(ValidationError):
            Comment(
                comment_id="abc",
                user_id=1,
                comment="Nice place",
                user_name="Username",
            )


class TestLocationSchema(unittest.TestCase):

    def test_create_instance(self):
        location_instance = Location(latitude=51.5074, longitude=-0.1278)
        self.assertEqual(location_instance.latitude, 51.5074)
        self.assertEqual(location_instance.longitude, -0.1278)


class TestAttractionWithCommentsByUserSchema(unittest.TestCase):

    def setUp(self):
        self.comment1 = Comment(
            comment_id=1, user_id=1, comment="Great place", user_name="Username1"
        )
        self.comment2 = Comment(
            comment_id=2, user_id=2, comment="Fantastic place", user_name="Username2"
        )
        self.location = Location(latitude=51.5074, longitude=-0.1278)

    def test_create_instance(self):
        attraction_instance = AttractionWithCommentsByUser(
            attraction_id="Csad132dad3f21de",
            attraction_name="Coffee break",
            city="Buenos Aires",
            country="Argentina",
            location=self.location,
            photo="photo.jpg",
            avg_rating=4.5,
            liked_count=10,
            types=["Park", "Museum"],
            formatted_address="Santa Fe 2989, Buenos Aires",
            google_maps_uri="https://maps.google.com/Csad132dad3f21de",
            editorial_summary="Fantastic place to visit",
            is_liked=True,
            is_saved=True,
            user_rating=4,
            is_done=True,
            comments=[self.comment1, self.comment2],
        )

        self.assertEqual(attraction_instance.attraction_id, "Csad132dad3f21de")
        self.assertEqual(attraction_instance.attraction_name, "Coffee break")
        self.assertEqual(attraction_instance.city, "Buenos Aires")
        self.assertEqual(attraction_instance.country, "Argentina")
        self.assertEqual(attraction_instance.location, self.location)
        self.assertEqual(attraction_instance.photo, "photo.jpg")
        self.assertEqual(attraction_instance.avg_rating, 4.5)
        self.assertEqual(attraction_instance.liked_count, 10)
        self.assertEqual(attraction_instance.types, ["Park", "Museum"])
        self.assertEqual(
            attraction_instance.formatted_address, "Santa Fe 2989, Buenos Aires"
        )
        self.assertEqual(
            attraction_instance.google_maps_uri,
            "https://maps.google.com/Csad132dad3f21de",
        )
        self.assertEqual(
            attraction_instance.editorial_summary, "Fantastic place to visit"
        )
        self.assertTrue(attraction_instance.is_liked)
        self.assertTrue(attraction_instance.is_saved)
        self.assertEqual(attraction_instance.user_rating, 4)
        self.assertTrue(attraction_instance.is_done)
        self.assertEqual(attraction_instance.comments, [self.comment1, self.comment2])


class TestAttractionSchema(unittest.TestCase):

    def setUp(self):
        self.location = Location(latitude=51.5074, longitude=-0.1278)

    def test_create_instance(self):
        attraction_instance = Attraction(
            attraction_id="Csad132dad3f21de",
            attraction_name="Coffee break",
            city="Buenos Aires",
            country="Argentina",
            location=self.location,
            photo="photo.jpg",
            avg_rating=4.5,
            liked_count=10,
            types=["Park", "Museum"],
            formatted_address="Santa Fe 2989, Buenos Aires",
            google_maps_uri="https://maps.google.com/Csad132dad3f21de",
            editorial_summary="Fantastic place to visit",
        )

        self.assertEqual(attraction_instance.attraction_id, "Csad132dad3f21de")
        self.assertEqual(attraction_instance.attraction_name, "Coffee break")
        self.assertEqual(attraction_instance.city, "Buenos Aires")
        self.assertEqual(attraction_instance.country, "Argentina")
        self.assertEqual(attraction_instance.location, self.location)
        self.assertEqual(attraction_instance.photo, "photo.jpg")
        self.assertEqual(attraction_instance.avg_rating, 4.5)
        self.assertEqual(attraction_instance.liked_count, 10)
        self.assertEqual(attraction_instance.types, ["Park", "Museum"])
        self.assertEqual(
            attraction_instance.formatted_address, "Santa Fe 2989, Buenos Aires"
        )
        self.assertEqual(
            attraction_instance.google_maps_uri,
            "https://maps.google.com/Csad132dad3f21de",
        )
        self.assertEqual(
            attraction_instance.editorial_summary, "Fantastic place to visit"
        )


class TestAttractionWithCommentsSchema(unittest.TestCase):

    def setUp(self):
        self.location = Location(latitude=51.5074, longitude=-0.1278)
        self.comment1 = Comment(
            comment_id=1, user_id=1, comment="Great place", user_name="Username1"
        )
        self.comment2 = Comment(
            comment_id=2, user_id=2, comment="Beautiful view", user_name="Username2"
        )

    def test_create_instance_with_comments(self):
        attraction_instance = AttractionWithComments(
            attraction_id="Csad132dad3f21de",
            attraction_name="Coffee break",
            city="Buenos Aires",
            country="Argentina",
            location=self.location,
            photo="photo.jpg",
            avg_rating=4.5,
            liked_count=10,
            types=["Park", "Museum"],
            formatted_address="Santa Fe 2989, Buenos Aires",
            google_maps_uri="https://maps.google.com/Csad132dad3f21de",
            editorial_summary="Fantastic place to visit",
            comments=[self.comment1, self.comment2],
        )

        self.assertEqual(attraction_instance.attraction_id, "Csad132dad3f21de")
        self.assertEqual(attraction_instance.attraction_name, "Coffee break")
        self.assertEqual(attraction_instance.city, "Buenos Aires")
        self.assertEqual(attraction_instance.country, "Argentina")
        self.assertEqual(attraction_instance.location, self.location)
        self.assertEqual(attraction_instance.photo, "photo.jpg")
        self.assertEqual(attraction_instance.avg_rating, 4.5)
        self.assertEqual(attraction_instance.liked_count, 10)
        self.assertEqual(attraction_instance.types, ["Park", "Museum"])
        self.assertEqual(
            attraction_instance.formatted_address, "Santa Fe 2989, Buenos Aires"
        )
        self.assertEqual(
            attraction_instance.google_maps_uri,
            "https://maps.google.com/Csad132dad3f21de",
        )
        self.assertEqual(
            attraction_instance.editorial_summary, "Fantastic place to visit"
        )
        self.assertEqual(attraction_instance.comments, [self.comment1, self.comment2])


class TestScheduledAttractionSchema(unittest.TestCase):

    def setUp(self):
        self.location = Location(latitude=51.5074, longitude=-0.1278)

    def test_create_instance(self):
        scheduled_attraction_instance = ScheduledAttraction(
            attraction_id="Csad132dad3f21de",
            attraction_name="Coffee break",
            city="Buenos Aires",
            country="Argentina",
            location=self.location,
            photo="photo.jpg",
            avg_rating=4.5,
            liked_count=10,
            types=["Park", "Museum"],
            scheduled_day=datetime(2024, 7, 10, 10, 0, 0),
            formatted_address="Santa Fe 2989, Buenos Aires",
            google_maps_uri="https://maps.google.com/Csad132dad3f21de",
            editorial_summary="Fantastic place to visit",
        )

        self.assertEqual(
            scheduled_attraction_instance.attraction_id, "Csad132dad3f21de"
        )
        self.assertEqual(scheduled_attraction_instance.attraction_name, "Coffee break")
        self.assertEqual(scheduled_attraction_instance.city, "Buenos Aires")
        self.assertEqual(scheduled_attraction_instance.country, "Argentina")
        self.assertEqual(scheduled_attraction_instance.location, self.location)
        self.assertEqual(scheduled_attraction_instance.photo, "photo.jpg")
        self.assertEqual(scheduled_attraction_instance.avg_rating, 4.5)
        self.assertEqual(scheduled_attraction_instance.liked_count, 10)
        self.assertEqual(scheduled_attraction_instance.types, ["Park", "Museum"])
        self.assertEqual(
            scheduled_attraction_instance.scheduled_day, datetime(2024, 7, 10, 10, 0, 0)
        )
        self.assertEqual(
            scheduled_attraction_instance.formatted_address,
            "Santa Fe 2989, Buenos Aires",
        )
        self.assertEqual(
            scheduled_attraction_instance.google_maps_uri,
            "https://maps.google.com/Csad132dad3f21de",
        )
        self.assertEqual(
            scheduled_attraction_instance.editorial_summary, "Fantastic place to visit"
        )


class TestUpdateRecommendationsSchema(unittest.TestCase):

    def test_create_instance(self):
        update_instance = UpdateRecommendations(
            user_id=1, default_city="Buenos Aires", preferences=["Park", "Museum"]
        )

        self.assertEqual(update_instance.user_id, 1)
        self.assertEqual(update_instance.default_city, "Buenos Aires")
        self.assertEqual(update_instance.preferences, ["Park", "Museum"])


class TestCreatePlanSchema(unittest.TestCase):

    def test_create_instance(self):
        create_plan_instance = CreatePlan(
            user_id=1, city="Buenos Aires", preferences=["Park", "Museum"]
        )

        self.assertEqual(create_plan_instance.user_id, 1)
        self.assertEqual(create_plan_instance.city, "Buenos Aires")
        self.assertEqual(create_plan_instance.preferences, ["Park", "Museum"])
