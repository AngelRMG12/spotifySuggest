# musicpy/urls.py
from django.urls import path
from .views import RunETLView, SpotifyAuthView, SpotifyCallbackView

urlpatterns = [
    path('run-etl/', RunETLView.as_view(), name='run-etl'),
    path('auth/', SpotifyAuthView.as_view(), name='spotify-auth'),
    path('callback/', SpotifyCallbackView.as_view(), name='spotify-callback'),
]
