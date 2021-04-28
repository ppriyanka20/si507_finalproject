#########################################
##### Name:Priyanka Panjwani        #####
##### Uniqname: ppanj               #####
#########################################

#########################################
#############  IMPORTS ##################
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
import plotly.graph_objs as go

###cache file set up###
CACHE_FILE = "music_data.json"
CACHE_DICT = {}
ARTIST_URI_CACHE = "artist_uri.json"
ARTIST_URI_DICT = {}

#get the client id and client secret key
cid = secrets.CLIENT_ID
secret = secrets.CLIENT_SECRET

#############################
#### GETTING SPOTIFY DATA ###
#############################
def get_artist_uri(userinput):
    '''retrieves the artist uri, based on user input
    Parameters
    -----------
    userinput: str
        the string representation of the artist to be searched
    Returns
    --------
    str
        the artist uri
    '''
    #get spotify credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    #do the API search for the artist using spotify package
    results = sp.search(q='artist:' + userinput, type='artist')

    #get the artists uri for later reference
    artist_uri = results['artists']['items'][0]['uri']
    return artist_uri

def get_artist_recommendations(userinput):
    '''Calls spotify artists API and displays bar chart of recommended
    artists and their popularity, based on what the userinput is
    Parameters
    -----------
    userinput: str
        the string representation of the artist to be searched
    Returns
    --------
    None
    '''
    #get spotify credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # #get the artists uri for later reference by caching
    artist_uri = make_uri_request_with_cache(userinput)

    #get recommended artists
    recommended = sp.artist_related_artists(artist_uri)['artists'] 
    names = []
    popularity =[]
    #add elements to list, names and popularity, as x and y vectors for graph
    for artist in recommended:
        names.append(artist['name'])
        popularity.append(artist['popularity'])
    #graph related artists and their popularities
    plotly_recommended_artists(names, popularity)

def get_album_uris_spotify(userinput):
    '''Calls spotify artists API and returns information on selected artist.
    Parses data and returns only relevant data for this application.
    Parameters
    -----------
    userinput: str
        the string representation of the artist to be searched
    Returns
    --------
    dict
        dictionary containing each album by the artist and the album uri
    '''

    #get spotify credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # #get the artists uri for later reference
    artist_uri = make_uri_request_with_cache(userinput)

    #now, use that uri to figure out the artists albums
    albums = sp.artist_albums(artist_uri, album_type='album')
    album_identifiers = {}
    album_name = ''
    uri = ''

    #create a dictionary where key is album name, value is album uri
    for item in albums['items']: #for each album of this artist
        for key, value in item.items():
            if key == 'name': #extract the name of the album
                album_name = value
            if key == 'uri': #extract the number of tracks in the album
                uri = value
            album_identifiers[album_name] = uri #add to the song count dictionary

    del album_identifiers['']
    return album_identifiers

def print_album_list(album_list):
    '''prints the albums of an artist out nicely
    Parameters
    -----------
    album_list: dict
        the album to print out with their uri
    Returns
    --------
    None
    '''
    #get each album name
    keys = album_list.keys()
    num = 1
    #print each one out nicely in a numbered list
    for album in keys:
        print(f"{num}: {album}")
        num +=1

def get_album_songs(album):
    '''Calls spotify albums API and returns information on selected album.
    Parses data and returns only relevant data for this application.
    Parameters
    -----------
    album: str
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
        album_songs.append(item)
    return album_songs

def explore_album_songs(album_songs):
    '''parses list and returns a nicely formatted version of all songs in an album.
    Also creates a bar chart of the album songs and their lengths
    Parameters
    -----------
    album_songs
        the album's songs to print out and graph
    Returns
    --------
    none
    '''
    #empty lists as x and y vectors for later graphing
    names = []
    durations = []
    num = 1
    #add info to the lists
    for song in album_songs:
        names.append(song['name'])
        durations.append(int(song['duration_ms']))
    #print out the songs in a nicely numbered list
    print("Here are all the songs in the album you chose to explore: \n")
    for name in names:
        print(f"{num}: {name}")
        num +=1
    #graph the songs and their duration, display the graph
    show_bar_chart(names, durations)

########################################
##### obtaining pitchfork data #########
########################################

ALBUM_URL = 'https://pitchfork.com/features/lists-and-guides/the-200-best-albums-of-the-2010s/'

def get_pitchfork_data():
    '''Scrapes through the pitchfork list: best albums of the 2010s
    -----------
    Returns
    --------
    list
        list containing each element on the top 200 list. each element is the artist, album name, and year
    '''
    #initial request for the data
    req = Request(ALBUM_URL, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    #scrape the webpage
    soup = BeautifulSoup(webpage, 'html.parser')
    rankings = soup.find_all('h2')

    #add the pitchfork albums to a list 
    pitchfork_ranked_albums = []
    for ranking in rankings:
        pitchfork_ranked_albums.append(ranking.text.strip().lower())

    return pitchfork_ranked_albums

def search_artist_in_pitchfork(userinput, pitchfork_albums):
    '''looks through the pitchfork top 200 albums, to see if the userinput matches
    any of the artists of those albums
    Parameters
    -----------
    pitchfork_albums
        the albums on the top 200 list
    userinput
        the artist we are looking for on the list
    Returns
    --------
    None
    '''
    is_ranked = ""
    ranked_album = ""
    for ranking in pitchfork_albums:
        if userinput in ranking.lower():
            is_ranked = "yes"
            ranked_album = ranking
    if is_ranked == "yes":
        print(f"You have good music taste! {ranked_album} is one of pitchfork's top albums of the 2010's.\n")
    else:
        print(f"Sorry your music taste isn't that amazing. Pitchfork did not rank {userinput}.\n")

###############################
########## Plotly #############
###############################

def show_bar_chart(x_values, y_values):
    '''displays and creates a bar chart for album songs and their 
    lengths in milliseconds
    Parameters
    -----------
    x_values
        the album's songs 
    y_values
        the song lengths in milliseconds
    Returns
    --------
    none
    '''
    bar_data = go.Bar(x=x_values, y=y_values)
    basic_layout = go.Layout(title = "Album songs and their lengths(milliseconds)")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.write_html("song_bar_chart.html", auto_open=True)

def plotly_recommended_artists(x_values, y_values):
    '''displays and creates a bar chart for recommended artists
    and their popularity based on Spotify
    Parameters
    -----------
    x_values
        the artists
    y_values
        the popularities of the artists
    Returns
    --------
    none
    '''
    bar_data = go.Bar(x=x_values, y=y_values)
    basic_layout = go.Layout(title = "Recommended artists and their popularity (0-100)")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.write_html("artists_bar_chart.html", auto_open=True)

###############################
#### Setting up Caching #######
###############################

def load_cache(cache_file):
    ''' opens the cache file if it exists and loads the JSON into
    a dictionary, which it then returns.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    cache_file
        the cache file to load
    -------
    The opened cache
    '''
    try:
        cache_file = open(cache_file, 'r')
        contents = cache_file.read()
        cache_dict = json.loads(contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict, cache_file):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    cache_file
        the cache_file to save to
    Returns
    -------
    None
    '''
    cache_file = open(cache_file, 'w')
    cache_file.write(json.dumps(cache_dict))
    cache_file.close()

def make_uri_request_with_cache(userinput):
    ''' makes artist uri request
    If cache doesn't exist, makes request and adds to cache file
    Parameters
    ----------
    userinput: string
        The artist uri to make a request about
    Returns
    -------
    dict
        a dictionary of the artist name keys and 
        uri for that artist as value
    '''
    if userinput in ARTIST_URI_DICT.keys():
        print("Using cache!", userinput)
        return ARTIST_URI_DICT[userinput]
    else:
        print("Cache miss!", userinput)
        ARTIST_URI_DICT[userinput] = get_artist_uri(userinput)
        save_cache(ARTIST_URI_DICT, ARTIST_URI_CACHE)
        return ARTIST_URI_DICT[userinput]

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
        save_cache(CACHE_DICT, CACHE_FILE)
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
        save_cache(CACHE_DICT, CACHE_FILE)
        return CACHE_DICT[album_uri]

def make_pitchfork_request_with_cache():
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
    if ALBUM_URL in CACHE_DICT.keys():
        print("Using cache!")
        return CACHE_DICT[ALBUM_URL]
    else:
        print("Cache miss!")
        CACHE_DICT[ALBUM_URL] = get_pitchfork_data()
        save_cache(CACHE_DICT, CACHE_FILE)
        return CACHE_DICT[ALBUM_URL]

#######################################
## Setting up SQL Database Structure ##
#######################################

#set up connection
conn = sqlite3.connect('spotify_db.sqlite')
cur = conn.cursor()

#set up albums table
drop_albums = '''
    DROP TABLE IF EXISTS "Albums";
'''

create_albums = '''
    CREATE TABLE IF NOT EXISTS "Albums" (
        "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Title"    TEXT NOT NULL,
        "Artist"    TEXT NOT NULL,
        "NumberTracks"    INTEGER NOT NULL,
        "URI"    INTEGER NOT NULL,
        "Pitchfork"    TEXT NOT NULL
    );
'''
cur.execute(drop_albums)
cur.execute(create_albums)

#set up songs table
drop_songs = '''
    DROP TABLE IF EXISTS "Songs";
'''

create_songs = '''
    CREATE TABLE IF NOT EXISTS "Songs" (
        "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Title"    TEXT NOT NULL,
        "Artist"    TEXT NOT NULL,
        "AlbumID"    INTEGER NOT NULL
    );
'''

cur.execute(drop_songs)
cur.execute(create_songs)

if __name__ == "__main__":

    pitchfork_data = make_pitchfork_request_with_cache() #get initial pitchfork data
    userinput = input('Enter the name of one of your favorite artists (e.g. Justin Bieber) to explore, or enter exit:').lower()

    while True:

        if userinput == "exit": #if they want to exit, let them exit
            break

        else: #otherwise, let's search for the artist they typed in
            albums_to_print = make_artist_request_with_cache(userinput) #get the albums to search for

            if albums_to_print == None: #if there are no albums, print message
                print("sorry! We cannot find any albums for that artist")

            else: #print out the albums for that artist
                print(f"Here are the albums we found for {userinput}:")
                print_album_list(albums_to_print)#print out the list of albums nicely
                #tell them if the artist they searched is on the pitchfork top list
                print("------------------------------------------------- \n")
                search_artist_in_pitchfork(userinput, pitchfork_data)
                print("------------------------------------------------- \n")
                #now, ask them if they want to see this pitchfork list
                newinput = input("Would you like to see the full pitchfork list? Enter yes or no: ").lower()

                if newinput == "yes":
                    webbrowser.open('https://pitchfork.com/features/lists-and-guides/the-200-best-albums-of-the-2010s/')
                print("------------------------------------------------- \n")
                newinput = input("Would you like to see related artists and their popularity? Enter yes or no: ").lower()

                if newinput == "yes":
                    get_artist_recommendations(userinput)
                print("------------------------------------------------- \n")

                while True: #new loop to explore an album
                    #ask them if they want to explore one of the listed albums
                    print_album_list(albums_to_print) #print them again for user reference
                    print("------------------------------------------------- \n")
                    userinput = input("Enter a number if you'd like to explore one of the album's songs. Or type 'exit', or 'back' to do another search:").lower()

                    if userinput == "exit":#exit the program
                        break

                    elif userinput == "back": #go back to the initial artist search
                        userinput = input('Enter the name of one of your favorite artists (e.g. Justin Bieber) or enter exit:').lower()
                        break

                    elif userinput.isnumeric() and float(userinput) >0 and float(userinput).is_integer()\
                     and int(float(userinput)) in range(len(albums_to_print)+1): #check for valid input
                            album_names = []

                            #get the names of the albums
                            for album in albums_to_print.keys():
                                album_names.append(album)
                            #now, based off the user input, get the album they want to explore
                            album_in_question = album_names[int(float(userinput))-1]
                            #get all the songs of that specific album they requested
                            album_songs = make_album_request_with_cache(albums_to_print[album_in_question])
                            #print out the album songs, and open a plotly graph
                            explore_album_songs(album_songs)

                    else:#not a valid input
                        print("Invalid input\n")
                        print("------------------------------------")
