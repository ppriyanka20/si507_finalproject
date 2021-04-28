# SI 507 Final Project - Priyanka Panjwani, Winter 2021  

## Instructions for running the code  

The main file for my project is panjwani_finalproject.py. In this code you will see all of the packages you need to import:  
  
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
  
Spotipy, which is a package created for accessing data from the Spotify API, has specific documentation that you can find here: https://spotipy.readthedocs.io/en/2.18.0/#features  
  
You need to create a Spotify developer account, and then access your client ID and client secret key in order to run the program. Save these two variables as CLIENT_ID and CLIENT_SECRET in a secrets.py file. Keep this file in the same folder as the code you are running.   
  
## Instructions for interacting with the program:  
This program is done entirely from the command line. You can expect, based on the choices you make, for bar graphs to open up in a webbrowser, as well as one instance of a web page opening up (the Pitchfork Top 200 Albums of the 2010's page) if you opt into this choice. Other than that, all information is displayed in the command line.  
  
The flow of the program goes like this:   
  
1.	User is prompted to enter one of their favorite artists names to explore their music further  
  
2.	User enters the artist name. There are two options:  
  a.	The artist is not found. The program prints out a sorry message and asks for another search  
  b.	The artist is found. The program prints out a numbered and nicely formatted list of the artists albums, found using the Spotify API  
  
3.	After the album list is printed out, there is also a statement that shows whether any of the artists albums show up on Pitchforks “Top 200 Albums of the 2010’s” list.   
  
4.	After this Pitchfork statement is printed out, the user is prompted as to whether they want to actually open up this list in the web browser.   
  a.	If the user says “yes”, the link opens up in the web browser  
  
5.	Then, the user is prompted if they would like to explore related artists to the ones they searched, and these artists popularities  
  a.	If yes, a bar chart opens up in the web browser with the popularity on the y axis, and all of the related artists on the x axis  
  
6.	Now, the user is prompted as to whether they would like to explore one of the albums listed earlier further.  
  a.	 If they do, they can enter the number of the album they would like to explore.  
  b.	Otherwise, they can enter “exit” to exit the program, or “back” to do a new artist search and start at Step 2 again  
  
7.	If they choose to explore an album further by entering a number, that album’s songs will be printed out in a nicely ordered list  
 a.	Additionally, a bar chart will pop up with the song length in milliseconds on the y axis, and the song names on the x axis.   
  
8.	Finally, the user can choose:  
  a.	 to explore another albums songs further, repeating the above step  
  b.	To go “back” and do another artist search, starting again at Step 2  
  c.	Or “exit” the program entirely.  

