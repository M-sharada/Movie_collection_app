from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Collection, Movie

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        data = {"username": "testuser", "password": "password123"}
        # Update to include 'api' prefix
        response = self.client.post(reverse('api:register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_missing_fields(self):
        data = {"username": ""}
        # Update to include 'api' prefix
        response = self.client.post(reverse('api:register'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class MovieTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

    def test_fetch_movies(self):
        # Update to include 'api' prefix
        response = self.client.get(reverse('api:movies'))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

class CollectionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.movie_data = {
            "title": "Test Movie",
            "description": "Test description",
            "genres": "Action,Drama",
            "uuid": "1234-abcd"
        }

    def test_create_collection(self):
        collection_data = {
            "title": "My Favorite Movies",
            "description": "A collection of my favorite movies",
            "movies": [self.movie_data]
        }
        # Update to include 'api' prefix
        response = self.client.post(reverse('api:collection'), collection_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_collections(self):
        # Update to include 'api' prefix
        response = self.client.get(reverse('api:collection'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_collection(self):
        # First create a collection
        collection_data = {
            "title": "My Favorite Movies",
            "description": "A collection of my favorite movies",
            "movies": [self.movie_data]
        }
        # Update to include 'api' prefix
        response = self.client.post(reverse('api:collection'), collection_data, format='json')
        collection_uuid = response.data['movies'][0]['uuid']

        # Update the collection
        update_data = {"title": "Updated Collection", "movies": [self.movie_data]}
        # Update to include 'api' prefix
        update_response = self.client.put(reverse('api:collection_detail', args=[collection_uuid]), update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

    def test_delete_collection(self):
        collection_data = {
            "title": "My Favorite Movies",
            "description": "A collection of my favorite movies",
            "movies": [self.movie_data]
        }
        # Update to include 'api' prefix
        response = self.client.post(reverse('api:collection'), collection_data, format='json')
        collection_uuid = response.data['movies'][0]['uuid']

        # Now delete the collection
        # Update to include 'api' prefix
        delete_response = self.client.delete(reverse('api:collection_detail', args=[collection_uuid]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
