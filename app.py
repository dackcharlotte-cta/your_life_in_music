# render_template() is a helper function that lets you render
# HTML template files that exist in the templates folder
from flask import Flask, render_template, request, redirect, url_for, session
# bring in the python code
from test import main
import secrets
import secrets

secret_key = secrets.token_hex(16)  # Generates a 32-character hexadecimal key

app = Flask(__name__, '/static')
app.secret_key = secret_key
# add a debugger
app.config["DEBUG"] = True

# give a default year since the get_tracks function now requires a year argument
default_birthday ='1998-10-05'

# when you go to the main url, it will render the index.html
# that lives inside the templates folder
@app.route('/')
def index():
	return render_template('index.html', birthday_song=[], city=default_birthday)

@app.route('/', methods=['POST'])
def index_post():

    user_birthday = request.form['birthday']
    user_name = request.form.get('name', 'Anonymous')  

    found_birthday_song, found_lyrics, years_playlist, main_lyrics, gif_ids = main(user_birthday, user_name)
    song_name, artists_name, released_date, song_uri = found_birthday_song

    results_data = {
        'song_name': song_name,
        'artists_name': artists_name,
        'released_date': released_date,
        'lyrics': found_lyrics,
        'playlist_id': years_playlist,
        'gif_ids': gif_ids,
        'user_birthday': user_birthday,
        'user_name': user_name
    }

    session['results_data'] = results_data
    return redirect(url_for('results_post'))

#can i try make it go to loading page before results page???? which has the lyrics or gifs on before then? 
#if results are in??? -- go to ... how would tell when it is loading? 


@app.route('/results', methods = ['GET'])
def results_post():
	results_data = session.get('results_data', {})
	return render_template('results.html', **results_data)

	

#@app.route('/test/<api>') #learning how to make my own API!!! Is this how you create two factor auth? in attempt to make a results page
#def results_post(api):
	#return render_template('results.html', id=api)
