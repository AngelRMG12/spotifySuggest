# etl_app/etl_process.py
import pandas as pd
import mysql.connector
from .spotify_etl import get_recently_played, create_playlist


def extract_data(user_data):
    spotify_data = get_recently_played()
    df_spotify = pd.json_normalize(spotify_data['items'])
    user_df = pd.DataFrame([user_data])
    
    df_spotify.to_csv('temp_spotify_data.csv', index=False)
    user_df.to_csv('temp_user_data.csv', index=False)

def transform_data():
    df_spotify = pd.read_csv('temp_spotify_data.csv')
    df_user = pd.read_csv('temp_user_data.csv')

    # Transform Spotify data
    df_spotify.dropna(inplace=True)
    df_spotify['played_at'] = pd.to_datetime(df_spotify['played_at'])
    df_spotify.to_csv('transformed_spotify_data.csv', index=False)

    # Transform user data
    df_user.dropna(inplace=True)
    df_user.to_csv('transformed_user_data.csv', index=False)

def load_data(playlist_info):
    # Connect to MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Camilita123',
        database='sistemamusica'
    )
    cursor = conn.cursor()

    # Create table for playlist info if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_info (
        track_name VARCHAR(255),
        artist VARCHAR(255),
        genres VARCHAR(255),
        location VARCHAR(255),
        danceability FLOAT,
        energy FLOAT,
        loudness FLOAT,
        speechiness FLOAT,
        acousticness FLOAT,
        instrumentalness FLOAT,
        liveness FLOAT,
        tempo FLOAT
    )
    ''')

    # Load playlist info into the database
    for item in playlist_info:
        cursor.execute('''
        INSERT INTO playlist_info (track_name, artist, genres, location, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, tempo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            item['track_name'],
            item['artist'],
            item['genres'],
            item['location'],
            item['danceability'],
            item['energy'],
            item['loudness'],
            item['speechiness'],
            item['acousticness'],
            item['instrumentalness'],
            item['liveness'],
            item['tempo']
        ))

    conn.commit()
    cursor.close()
    conn.close()


def run_etl_with_data(user_data):
    extract_data(user_data)
    transform_data()
    playlist_info = create_playlist(user_data)
    load_data(playlist_info)
    return playlist_info


