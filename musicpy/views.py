# etl_app/views.py
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spotipy import SpotifyOAuth
from .etl_process import run_etl_with_data

# Configuración de Spotify
SPOTIPY_CLIENT_ID = 'eebeb2003f94488a8f0591596b78f0d0'
SPOTIPY_CLIENT_SECRET = '6c9fd3845f424415ac2c89233df43400'
SPOTIPY_REDIRECT_URI = 'http://localhost:8000/etl/callback/'

class SpotifyAuthView(APIView):
    def get(self, request):
        sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                client_secret=SPOTIPY_CLIENT_SECRET,
                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                scope="playlist-modify-public user-read-recently-played user-top-read user-library-read")
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

class SpotifyCallbackView(APIView):
    def get(self, request):
        sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                client_secret=SPOTIPY_CLIENT_SECRET,
                                redirect_uri=SPOTIPY_REDIRECT_URI)
        code = request.GET.get('code')
        token_info = sp_oauth.get_access_token(code)

        if token_info:
            request.session['token_info'] = token_info
            return JsonResponse({"message": "Spotify authentication successful"})
        else:
            return JsonResponse({"error": "Spotify authentication failed"}, status=400)
class RunETLView(APIView):
    def post(self, request):
        try:
            user_data = request.data
            playlist_info = run_etl_with_data(user_data)
            return Response({
                "message": "ETL process and playlist creation completed successfully",
                "playlist_info": playlist_info
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)