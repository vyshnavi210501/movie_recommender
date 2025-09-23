from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from movies.models import Movie, Rating
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class RatingsAPITestCase(APITestCase):
    """
    Professional test suite for Ratings API with JWT auth.
    Covers:
    - Create rating
    - List ratings
    - Authentication
    - Validation
    """

    @classmethod
    def setUpTestData(cls):
        # Users
        cls.user = User.objects.create_user(username="movie123", password="movie123")
        cls.admin = User.objects.create_superuser(username="admin", password="adminpass", email="admin@example.com")

        # Movies
        cls.movie1 = Movie.objects.create(title="Inception", genres="Sci-Fi|Thriller")
        cls.movie2 = Movie.objects.create(title="Avengers", genres="Action|Adventure")

        # URL
        cls.url_list = reverse("rating-list")

    def setUp(self):
        # JWT auth
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_create_rating_success(self):
        """Normal user can create a rating"""
        data = {"movie": self.movie1.id, "rating": 4}
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.first().rating, 4)

    def test_create_rating_requires_authentication(self):
        """Unauthenticated users cannot create ratings"""
        client = APIClient()  # no auth token
        data = {"movie": self.movie1.id, "rating": 4}
        response = client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_ratings(self):
        """User can list only their own ratings"""
        Rating.objects.create(user=self.user, movie=self.movie2, rating=5)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["rating"], 5)
        self.assertEqual(response.data[0]["movie"], self.movie2.id)

    def test_rating_invalid_value(self):
        """Rating value must be between 0 and 5"""
        data = {"movie": self.movie1.id, "rating": 10}
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)
