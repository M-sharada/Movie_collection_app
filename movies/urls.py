from django.urls import path
from .views import (
    ApiOverviewView,
    RegisterView,
    MovieListView,
    CollectionView,
    CollectionDetailView,
    RequestCountView,
    RequestCountResetView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # Add this line

urlpatterns = [
    path('', ApiOverviewView.as_view(), name='api-overview'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('movies/', MovieListView.as_view(), name='movies'),
    path('collection/', CollectionView.as_view(), name='collection'),
    path('collection/<uuid:collection_uuid>/', CollectionDetailView.as_view(), name='collection_detail'),
    path('request-count/', RequestCountView.as_view(), name='request_count'),
    path('request-count/reset/', RequestCountResetView.as_view(), name='request_count_reset'),
]
