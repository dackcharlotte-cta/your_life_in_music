import spotipy
import spotipy.util as util
import json
from lyricsgenius import Genius
import lyricsgenius
import webbrowser
import re 
import nltk
import string
import collections
import time
from nltk.tokenize import word_tokenize
from urllib import parse, request
import requests
from IPython.display import Image, display
from IPython.display import IFrame
from datetime import datetime


#spotify set up 

spotify_credentials = "spotify_key.json"
with open(spotify_credentials, "r") as spotify_keys:
    spotify_tokens = json.load(spotify_keys)

# read the keys and assign each to a variable
# A redirect URI, or reply URL, is the location where the authorization server sends the user once the app has been 
# successfully authorized and granted an authorization code or access token.
client_id = spotify_tokens["client_id"]
client_secret = spotify_tokens["client_secret"]
redirectURI = spotify_tokens["redirect"]
username = spotify_tokens["username"]

# for more information on scoping
#https://developer.spotify.com/documentation/web-api/concepts/scopes
scope = 'user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public'
token = util.prompt_for_user_token(username, scope, client_id=client_id,
                           client_secret=client_secret,
                           redirect_uri=redirectURI)

# Create Spotify Object
sp = spotipy.Spotify(auth=token)


#genius setup 
genius_credentials = "genius_key.json"
with open(genius_credentials, "r") as genius_keys:
    genius_tokens = json.load(genius_keys)
genius_token = genius_tokens['access_token']
genius = lyricsgenius.Genius(genius_token)

#giphy set up 
credentials = "giphy_key.json"
with open(credentials, "r") as keys:
    giphy_tokens = json.load(keys)

my_client_id = giphy_tokens['api_key']

def main(birthday, user_name):
    found_birthday_song = find_birthday_song(birthday)
    found_lyrics = searching_lyrics(found_birthday_song, genius)
    playlist_creation = songs_through_years_playlist(found_birthday_song, birthday, user_name)
    main_lyrics = ansyling_song_lyrics(found_lyrics)
    gif_ids = lyrics_as_gifs(main_lyrics, my_client_id)

    return (found_birthday_song, found_lyrics, playlist_creation, main_lyrics, gif_ids)

# User input to get the birthday
def find_birthday_song(birthday): 
    #get birthday input
    birthyear = birthday[:4]
    birthmonth = birthday[5:7]
    birthday_day = birthday[8:]
    birthsongs = []
    int_birthyear = int(birthyear)

    offset = 0
    found_songs = False
    song_lyrics = ''

    while not found_songs and offset < 1000:  # limit to 1000 songs to avoid infinite loop
        # Search for songs with offset
        track_results = sp.search(q=f'year:{birthyear}', type='track', limit=50, offset=offset)
        
        for track in track_results['tracks']['items']:
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            release_date = track['album']['release_date']
            uri_for_song = track['uri']

            
            if release_date == birthday:
                day_birth_song_dets = []
                day_birth_song_dets.append(song_name)
                day_birth_song_dets.append(artist_name)
                day_birth_song_dets.append(release_date)
                day_birth_song_dets.append(uri_for_song)
                found_songs = True


        
        if not found_songs:
            offset += 50  # get next 50 songs
            print(f"Searching next {offset} songs...")

    if not found_songs:
        print(f"No songs found released on {birthday}")


  #use the birthday to find  birthday song
    return day_birth_song_dets


def searching_lyrics(found_birthday_song, genius):
#TAKE LIST FROM ABOVE FUNCTION AND INDEX IN AS NEED
    print(found_birthday_song[0], found_birthday_song[1])
    try:
        song = genius.search_song(found_birthday_song[0], found_birthday_song[1])
        if song:
            song_lyrics = song.lyrics
            print(song_lyrics)

        else:
           print("Lyrics not found")
    except:
        print("Error fetching lyrics")

    return song_lyrics 



#searching songs through out years and creation of playlist
#return playlist URI so can embeded like kat did 
#bring in list from above and add to playlist first ?? or start from first year?? 


def songs_through_years_playlist(found_birthday_song, birthday, user_name): 
    offset = 0
    found_songs = False

    birthyear = birthday[:4]
    birthmonth = birthday[5:7]
    birthday_day = birthday[8:]
    int_birthyear = int(birthyear)
    birthsongs = []

    # Loop through each year from birth year to current year
    for year in range(int_birthyear, 2024):
        current_date = f"{year}-{birthmonth}-{birthday_day}"
        offset = 0
        found_songs = False

        while not found_songs and offset < 1000:  # limit to 1000 songs to avoid infinite loop
            # Search for songs with offset
            track_results = sp.search(q=f'year:{year}', type='track', limit=50, offset=offset)
            
            for track in track_results['tracks']['items']:
                song_name = track['name']
                artist_name = track['artists'][0]['name']
                release_date = track['album']['release_date']
                song_uri = track['uri']
                
                if release_date == current_date:
                    print(f"{song_name} by {artist_name}- Released on: {release_date}")
                    found_songs = True
                    birthsongs.append(song_uri)
            
            if not found_songs:
                offset += 50  # get next 50 songs
                #print(f"Searching year {year}, offset {offset}...")

        if not found_songs:
            print(f"No songs found released on {current_date}")
            birthsongs.append('1nWolg9y1SgQ7SPu53zWZ1')

    life_in_playlist = birthsongs

    my_playlist = sp.user_playlist_create(user=username, name=f"{user_name}'s life in music", public=True, description="Music released on your birthday each year")
    playlist_with_songs = sp.user_playlist_add_tracks(username, my_playlist['id'], life_in_playlist)
    return my_playlist['id']

#anaylse songs lyrics 
def ansyling_song_lyrics(found_lyrics):
    song_lyrics = found_lyrics.translate(str.maketrans('', '',string.punctuation)).replace("’","")

    Tokens = nltk.word_tokenize(song_lyrics)
    phrases = list(nltk.trigrams(Tokens))
    word_counter = collections.Counter(phrases) 

    phrases = []
    for keyword in word_counter.keys(): 
        if word_counter[keyword] > 1: 
            phrases.append(keyword)
    print(phrases) 
    return phrases  


#use phrases to send to giphy 
#retrun gifs as dict 
def lyrics_as_gifs(main_lyrics, my_client_id):
    gifs = []

    for phrase in main_lyrics: 
        new_dict = {
            "q": phrase,
            "api_key": my_client_id,
            "limit": "1"  
        }  
    url = "http://api.giphy.com/v1/gifs/search"
    params = parse.urlencode(new_dict)

    retries = 0
    while retries < 5:  # Maximum of 5 retries
        with request.urlopen("".join((url, "?", params))) as response:
            data = json.loads(response.read())
            if data["data"]:
                gif_one = data["data"][0]["embed_url"]  
                gifs.append(gif_one)
            else:
                print(f"No GIFs found for phrase: {phrase}")
        time.sleep(1)  
        break 

    print(gifs) 
    return gifs


