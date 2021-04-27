#########################################
##### Name:Priyanka Panjwani        #####
##### Uniqname: ppanj               #####
#########################################

from requests_oauthlib import OAuth1
import requests
import json
import webbrowser
import spotipy #package for accessing spotify api information
from spotipy.oauth2 import SpotifyClientCredentials #oauth needed for Spotify
import spotipy.util as util
import secrets as secrets
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import sqlite3

#cache file set up
CACHE_FILE = "spotify_data.json"
CACHE_DICT = {}

#get the client id and client secret key
cid = secrets.CLIENT_ID
secret = secrets.CLIENT_SECRET

#############################
#### GETTING SPOTIFY DATA ###
#############################


def get_album_uris_spotify(userinput):
    '''Calls spotify artists API and returns information on selected artist.
    Parses data and returns only relevant data for this application.
    Parameters
    -----------
    search_terms: str
        the string representation of the artist to be searched
    Returns
    --------
    dict
        dictionary containing each album by the artist and the album uri
    '''

    #get spotify credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    #do the API search for the artist using spotify package
    results = sp.search(q='artist:' + userinput, type='artist')

    #get the artists uri for later reference
    artist_uri = results['artists']['items'][0]['uri']

    #now, use that uri to figure out the artists albums
    albums = sp.artist_albums(artist_uri, album_type='album')
    album_identifiers = {}
    album_name = ''
    uri = ''

    #create a dictionary where key is album name, value is num songs in album
    for item in albums['items']: #for each album of this artist
        for key, value in item.items():
            if key == 'name': #extract the name of the album
                album_name = value
            if key == 'uri': #extract the number of tracks in the album
                uri = value
            album_identifiers[album_name] = uri #add to the song count dictionary

    del album_identifiers['']

    return album_identifiers

def get_album_songs(album):
    '''Calls spotify albums API and returns information on selected album.
    Parses data and returns only relevant data for this application.
    Parameters
    -----------
    search_terms: str
        the album's uri to be searched
    Returns
    --------
    list
        list containing each song in the album searched through
    '''
    #create initial credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    tracks = sp.album_tracks(album) #get the list of album tracks
    album_songs = [] #empty list that will have the albums songs
    for item in tracks['items']:
        album_songs.append(item['name'])
    return album_songs


########################################
##### obtaining pitchfork data #########
########################################

BASE_URL = 'https://pitchfork.com/features/lists-and-guides/the-200-best-albums-of-the-2010s/'
CACHE_FILE_NAME = 'pitchfork_cache.json'

def get_pitchfork_data():
    '''Scrapes through the pitchfork list: best albums of the 2010s
    -----------

    Returns
    --------
    list
        list containing each element on the top 200 list. each element is the artist, album name, and year
    '''
    #response = requests.get(BASE_URL)
    req = Request(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    #html = response.text
    soup = BeautifulSoup(webpage, 'html.parser')
    rankings = soup.find_all('h2')

    #add the pitchfork albums to a list 
    pitchfork_ranked_albums = []
    for ranking in rankings:
        pitchfork_ranked_albums.append(ranking.text.strip().lower())

    return pitchfork_ranked_albums

###############################
#### Setting up Caching #######
###############################

def load_cache():
    ''' opens the cache file if it exists and loads the JSON into
    a dictionary, which it then returns.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILE, 'r')
        contents = cache_file.read()
        cache_dict = json.loads(contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE, 'w')
    cache_file.write(json.dumps(cache_dict))
    cache_file.close()


def make_artist_request_with_cache(userinput):
    ''' makes artist spotipy request with cache
    If cache doesn't exist, makes request and adds to cache file
    Parameters
    ----------
    userinput: string
        The artist to make a request about
    Returns
    -------
    dict
        a dictionary of the artists albums as keys and 
        uri for that album as value
    '''
    if userinput in CACHE_DICT.keys():
        print("Using cache!", userinput)
        return CACHE_DICT[userinput]
    else:
        print("Cache miss!", userinput)
        CACHE_DICT[userinput] = get_album_uris_spotify(userinput)
        save_cache(CACHE_DICT)
        return CACHE_DICT[userinput]

def make_album_request_with_cache(album_uri):
    ''' makes album spotipy request with cache
    If cache doesn't exist, makes request and adds to cache file
    Parameters
    ----------
    album_uri: string
        The uri to make a request about
    Returns
    -------
    list
        a list of the songs on the album
    '''
    if album_uri in CACHE_DICT.keys():
        print("Using cache!", album_uri)
        return CACHE_DICT[album_uri]
    else:
        print("Cache miss!", album_uri)
        CACHE_DICT[album_uri] = get_album_songs(album_uri)
        save_cache(CACHE_DICT)
        return CACHE_DICT[album_uri]

#######################################
## Setting up SQL Database Structure ##
#######################################

conn = sqlite3.connect('spotify_db.sqlite')

cur = conn.cursor()

drop_albums = '''
    DROP TABLE IF EXISTS "Albums";
'''

create_albums = '''
    CREATE TABLE IF NOT EXISTS "Albums" (
        "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Name"    TEXT NOT NULL,
        "Artist"    TEXT NOT NULL,
        "NumberTracks"  INTEGER NOT NULL,
        "Popularity"    INTEGER NOT NULL
        "Uri"   TEXT NOT NULL
        "Pitchfork"     "TEXT NOT NULL
    );
'''

cur.execute(drop_albums)
cur.execute(create_albums)

drop_songs = '''
    DROP TABLE IF EXISTS "Songs";
'''

create_songs = '''
    CREATE TABLE IF NOT EXISTS "Songs" (
        "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "SongName"  TEXT NOT NULL
        "AlbumID"   INTEGER NOT NULL
    );
'''

cur.execute(drop_songs)
cur.execute(create_songs)

if __name__ == "__main__":
    pass
    # print(get_album_uris_spotify("taylor swift"))
    # album_dict = get_album_uris_spotify("harry styles")
    # album_tracks_dict = {}
    # for key, value in album_dict.items():
    #     list_of_songs = get_album_songs(value)
    #     album_tracks_dict[key] = list_of_songs
    # print(album_tracks_dict.items()