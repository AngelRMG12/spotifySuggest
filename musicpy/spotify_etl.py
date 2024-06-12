# etl_app/spotify_etl.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID = 'eebeb2003f94488a8f0591596b78f0d0'
SPOTIPY_CLIENT_SECRET = '6c9fd3845f424415ac2c89233df43400'
SPOTIPY_REDIRECT_URI = 'http://localhost:8000/etl/callback/'

scope = "playlist-modify-public user-read-recently-played user-top-read user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))

def get_recently_played():
    recently_played = sp.current_user_recently_played(limit=50)
    return recently_played

def get_recommendations(user_data, recent_tracks, total_recommendations=50):
    seed_tracks = [track['track']['id'] for track in recent_tracks['items'][:5]]  # Limit to 5 seed tracks
    
    recommendations = []
    limit_per_request = 20  # Spotify API limit per request
    iterations = total_recommendations // limit_per_request

    for _ in range(iterations):
        recs = sp.recommendations(
            seed_tracks=seed_tracks,
            limit=limit_per_request, 
            target_danceability=user_data.get('danceability'),
            target_energy=user_data.get('energy'),
            target_loudness=user_data.get('loudness'),
            target_speechiness=user_data.get('speechiness'),
            target_acousticness=user_data.get('acousticness'),
            target_instrumentalness=user_data.get('instrumentalness'),
            target_liveness=user_data.get('liveness'),
            target_tempo=user_data.get('tempo')
        )
        recommendations.extend(recs['tracks'])
    
    return recommendations[:total_recommendations]

def get_audio_features(track_ids):
    audio_features = sp.audio_features(track_ids)
    return audio_features

def create_playlist(user_data):
    user_id = sp.current_user()['id']
    playlist_name = f"{user_data['location']} Playlist"
    
    # Create a new playlist
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    
    # Get recently played tracks
    recent_tracks = get_recently_played()
    
    # Get recommended tracks to add
    recommendations = get_recommendations(user_data, recent_tracks)
    track_uris = [track['uri'] for track in recommendations]
    track_ids = [track['id'] for track in recommendations]
    
    # Add tracks to the playlist
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
    
    # Get audio features for the tracks
    audio_features = get_audio_features(track_ids)
    
    # Gather playlist info to return
    playlist_info = []
    for track, features in zip(recommendations, audio_features):
        track_info = {
            "track_name": track['name'],
            "artist": ', '.join([artist['name'] for artist in track['artists']]),
            "genres": ', '.join(sp.artist(track['artists'][0]['id'])['genres']),  # Assuming the first artist's genres
            "location": user_data['location'],
            "danceability": features['danceability'],
            "energy": features['energy'],
            "loudness": features['loudness'],
            "speechiness": features['speechiness'],
            "acousticness": features['acousticness'],
            "instrumentalness": features['instrumentalness'],
            "liveness": features['liveness'],
            "tempo": features['tempo']
        }
        playlist_info.append(track_info)
    
    return playlist_info
