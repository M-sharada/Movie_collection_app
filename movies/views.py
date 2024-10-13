from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.cache import cache
from django.conf import settings
import requests
from .models import Collection
from .serializers import CollectionSerializer
from django.contrib.auth.models import User
from rest_framework import status

# Exception Handling Wrapper
def handle_exceptions(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

class ApiOverviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        api_urls = {
            'Register': '/api/register/',
            'Login': '/api/login/',
            'Token Refresh': '/api/token/refresh/',
            'Movies': '/api/movies/',
            'Collections': '/api/collection/',
            'Collection Detail': '/api/collection/<collection_uuid>/',
            'Request Count': '/api/request-count/',
            'Request Count Reset': '/api/request-count/reset/',
        }
        return Response(api_urls)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @handle_exceptions
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"message": "Username and password required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, password=password)
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MovieListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        url = 'https://demo.credy.in/api/v1/maya/movies/'
        try:
            response = requests.get(url, auth=(settings.API_USERNAME, settings.API_PASSWORD))

            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to fetch data from external API"}, status=response.status_code)
        
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CollectionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        collections = Collection.objects.filter(user=request.user)
        genres = {}

        for collection in collections:
            for movie in collection.movies.all():
                movie_genres = movie.genres.split(',')
                for genre in movie_genres:
                    genres[genre] = genres.get(genre, 0) + 1

        top_genres = sorted(genres.items(), key=lambda item: item[1], reverse=True)[:3]
        top_genres = [g[0] for g in top_genres]

        serializer = CollectionSerializer(collections, many=True)
        return Response({"is_success": True, "data": {"collections": serializer.data, "favourite_genres": top_genres}})

    @handle_exceptions
    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectionDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request, collection_uuid):
        collection = get_object_or_404(Collection, uuid=collection_uuid, user=request.user)
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    @handle_exceptions
    def put(self, request, collection_uuid):
        collection = get_object_or_404(Collection, uuid=collection_uuid, user=request.user)
        serializer = CollectionSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions
    def delete(self, request, collection_uuid):
        collection = get_object_or_404(Collection, uuid=collection_uuid, user=request.user)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RequestCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request):
        count = cache.get('request_count', 0)
        return Response({"requests": count})

    @handle_exceptions
    def post(self, request):
        count = cache.get('request_count', 0) + 1
        cache.set('request_count', count)
        return Response({"message": "Request count incremented", "requests": count})

class RequestCountResetView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request):
        cache.set('request_count', 0)
        return Response({"message": "Request count reset successfully"})
