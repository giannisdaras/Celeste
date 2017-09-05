import sys
import spotipy
import spotipy.util as util
from os import system as cmd
import urllib
import webbrowser
# export SPOTIPY_CLIENT_ID='db13c5c481574855b69a6209bdffc279'
# export SPOTIPY_CLIENT_SECRET='ee74200a30754633baff860d4c0546f9'
# export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
scope = 'user-library-read'
username="Giannhs Daras"
try:
	token = util.prompt_for_user_token(username, scope)
except:
	print('Exports or credentials')

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.search(q='mazonakis', limit=20)
    print(results.keys())
    for i, t in enumerate(results['tracks']['items']):
        print ' ', i, t['name']
    link=t['preview_url']
    webbrowser.open_new(link)