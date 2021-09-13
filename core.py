import json
import pdb
import random
import re

from lyricsgenius import Genius
from nltk.tokenize import word_tokenize

import secrets

access_token = secrets.ACCESS_TOKEN

def get_lyrics(args):
    genius = Genius(access_token)

    # genius options
    genius.verbose = False
    genius.remove_section_headers = True
    genius.skip_non_songs = True
    genius.excluded_terms = [
        'Remix', 'Live', '(Remix)', '(Live)',
        'Unplugged', 'Demo', 'Bonus',
        'Remastered', 'Promo', 'Version'
    ]

    genius_files = []

    for artist_name in args.artist:
        print(f'searching songs for {artist_name}')
        kwargs = {'artist_name': artist_name, 'sort':'title'}

        if args.songs is not None:
            kwargs['max_songs'] = args.songs

        artist = genius.search_artist(**kwargs)
        filename = get_filename(artist_name)
        artist.save_lyrics(filename)

        genius_files.append(filename)

    return genius_files

def save_all_lyrics(json_file_list, lyrics_file):
    lyrics = ""

    for json_file in json_file_list:
        with open(json_file, 'r') as f:
            genius_data = json.load(f)

        for idx, song in enumerate(genius_data['songs']):
            lyrics += song['lyrics']

    with open(lyrics_file, 'w') as f:
        f.write(lyrics)

    return lyrics

def get_filename(artist_name):
    if isinstance(artist_name, str):
        filename = artist_name.lower().replace(' ', '_') + ".json"
    elif isinstance(artist_name, list):
        filename = '_'.join(artist_name).lower().replace(' ', '_')

    return filename

def clean_text(text):
    clean_text = text.lower()
    clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')
    clean_text = re.sub(r"[,.\"\'!@#$%^&*(){}?/;`~:<>+=-\\]", "", clean_text)
    clean_text = word_tokenize(clean_text)

    return clean_text

def create_markov_model(clean_lyrics, ngrams=2):
    markov_model = {}

    for i in range(len(clean_lyrics)-ngrams-1):
        current_state, next_state = "", ""

        for j in range(ngrams):
            current_state += clean_lyrics[i+j] + " "
            next_state += clean_lyrics[i+j+ngrams] + " "

        current_state = current_state[:-1]
        next_state = next_state[:-1]

        # create entry with sum to calculate probabilities of
        # current_state -> next_state
        if current_state not in markov_model:
            markov_model[current_state] = {}
            markov_model[current_state][next_state] = 1
        elif next_state in markov_model[current_state]:
            markov_model[current_state][next_state] += 1
        else:
            markov_model[current_state][next_state] = 1


    markov_model = calculate_probabilities(markov_model)
    return markov_model


def calculate_probabilities(markov_model):
    model = markov_model.copy()

    # calculate transition probabilities
    for current_state, transition in markov_model.items():
        total = sum(transition.values())

        for state, count in transition.items():
            markov_model[current_state][state] = count/total
    return model

def generate_lyrics(markov_model, limit=100, start='o amor'):
    n = 0
    curr_state = start
    next_state = None
    story = ""
    story += curr_state + " "

    for _ in range(limit):
        next_state = random.choices(
                    list(markov_model[curr_state].keys()),
                    list(markov_model[curr_state].values())
                )

        curr_state = next_state[0]
        story += curr_state + " "

    return story
