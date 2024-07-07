import unittest
from unittest.mock import Mock, patch

import app
from app.services.recommendations import *


class TestNGreatestPositions(unittest.TestCase):

    def test_n_greatest_positions_basic(self):
        numbers = [8, 3, 2, 9, 7]
        n = 3
        expected_result = [3, 0, 4]
        result = n_greatest_positions(numbers, n)
        self.assertEqual(result, expected_result)

    def test_n_greatest_positions_large_numbers(self):
        numbers = [1000, 500, 2000, 300, 1500]
        n = 4
        expected_result = [2, 4, 0, 1]
        result = n_greatest_positions(numbers, n)
        self.assertEqual(result, expected_result)

    def test_n_greatest_positions_empty_list(self):
        numbers = []
        n = 3
        expected_result = []
        result = n_greatest_positions(numbers, n)
        self.assertEqual(result, expected_result)


class TestGetSentiment(unittest.TestCase):

    @patch("app.services.recommendations.create_analyzer")
    def test_get_sentiment_positive(self, mock_create_analyzer):
        mock_analyzer = Mock()
        mock_analyzer.predict.return_value.probas = {
            "POS": 0.8,
            "NEG": 0.1,
            "NEU": 0.1,
        }
        mock_create_analyzer.return_value = mock_analyzer

        result = get_sentiment("Fantastic place")
        self.assertEqual(result, 0.8)

    @patch("app.services.recommendations.create_analyzer")
    def test_get_sentiment_negative(self, mock_create_analyzer):
        mock_analyzer = Mock()
        mock_analyzer.predict.return_value.probas = {
            "POS": 0.1,
            "NEG": 0.7,
            "NEU": 0.2,
        }
        mock_create_analyzer.return_value = mock_analyzer

        result = get_sentiment("Horrible place")
        self.assertEqual(result, 0.7)

    @patch("app.services.recommendations.create_analyzer")
    def test_get_sentiment_neutral(self, mock_create_analyzer):
        mock_analyzer = Mock()
        mock_analyzer.predict.return_value.probas = {
            "POS": 0.3,
            "NEG": 0.3,
            "NEU": 0.4,
        }
        mock_create_analyzer.return_value = mock_analyzer

        result = get_sentiment("Place to visit")
        self.assertEqual(result, 0)


class TestCreateRatingScore(unittest.TestCase):

    def test_rating_1(self):
        result = create_rating_score(1)
        self.assertEqual(result, -1)

    def test_rating_2(self):
        result = create_rating_score(2)
        self.assertEqual(result, -0.5)

    def test_rating_3(self):
        result = create_rating_score(3)
        self.assertEqual(result, 0.1)

    def test_rating_4(self):
        result = create_rating_score(4)
        self.assertEqual(result, 0.5)

    def test_rating_5(self):
        result = create_rating_score(5)
        self.assertEqual(result, 1)
