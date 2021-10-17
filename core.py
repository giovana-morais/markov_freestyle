'''
    Core functions to get Genius' data and create Markov Chain
'''
import json
import os
import pickle
import random
import re

from lyricsgenius import Genius
from nltk.tokenize import word_tokenize

from genius_secrets import ACCESS_TOKEN

import pdb

def save_model(model, filename='model.pkl'):
    ' save pickle model'
    print(f'saving {filename}')

    with open(filename, 'wb') as file:
        pickle.dump(model, file)

def load_model(filename='model.pkl'):
    ' load pickle model as dict'
    model = pickle.load(filename)

    return model

def get_artist_data(args):
    ' get genius artist data'
    genius = Genius(ACCESS_TOKEN)

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
        folder_name = 'genius_output'
        filename = get_filename(artist_name)

        artist.save_lyrics(
            filename = os.path.join(folder_name, filename),
            extension='json',
            sanitize=False
        )

        genius_files.append(filename)

    return genius_files

def save_all_lyrics(json_file_list, lyrics_file):
    '''
    filter all artists genius data, saving only lyrics in a single file.
    '''
    lyrics = ''

    for json_file in json_file_list:
        with open(f'genius_output/{json_file}.json', 'r') as filename:
            genius_data = json.load(filename)

        for _, song in enumerate(genius_data['songs']):
            lyrics += song['lyrics']

    with open(lyrics_file, 'w') as filename:
        filename.write(lyrics)

    return lyrics

def clean_lyrics(lyrics):
    '''
    remove garbage lyrics and standardize them
    '''
    new_lyrics = lyrics.lower()
    new_lyrics = new_lyrics.replace('\n', ' ').replace('\r', ' ')
    new_lyrics = re.sub(r'[,.\'\'!@#$%^&*(){}?/;`~:<>+=-\\]', '', new_lyrics)
    new_lyrics = new_lyrics.replace('EmbedShare', '')
    new_lyrics = new_lyrics.replace('URLCopyEmbedCopy', '')
    new_lyrics = word_tokenize(new_lyrics)

    return new_lyrics

def get_filename(artist_name):
    '''
    create filename
    '''
    if isinstance(artist_name, str):
        filename = artist_name.lower().replace(' ', '_')
    elif isinstance(artist_name, list):
        filename = '_'.join(artist_name).lower().replace(' ', '_')

    return filename

def accumulate(lyrics, markov_model=None, ngrams=2):
    '''
    cumulative calculations of state transitions
    '''
    if markov_model is None:
        markov_model = {}

    for i in range(len(lyrics)-ngrams-1):
        current_state, next_state = '', ''

        for j in range(ngrams):
            current_state += lyrics[i+j] + ' '
            next_state += lyrics[i+j+ngrams] + ' '

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

    return markov_model

def build_markov_model(lyrics, model=None):
    '''
    build markov model. if model != None, then it just update it using
    given lyrics
    '''

    if model is not None:
        cumsum = accumulate(lyrics, markov_model)
    else:
        cumsum = accumulate(lyrics)

    markov_model = calculate_probabilities(cumsum)

    return markov_model

def calculate_probabilities(markov_model):
    '''
    calculate model transition probabilities
    '''
    model = markov_model.copy()

    # calculate transition probabilities
    for current_state, transition in markov_model.items():
        total = sum(transition.values())

        for state, count in transition.items():
            markov_model[current_state][state] = count/total
    return model

def generate_lyrics(markov_model, limit=100, start='o amor'):
    '''
    create song lyrics based on markov model
    '''
    curr_state = random.choices([*markov_model])[0]
    next_state = None
    story = ''
    story += curr_state + ' '

    for _ in range(limit):
        next_state = random.choices(
                    list(markov_model[curr_state].keys()),
                    list(markov_model[curr_state].values())
                )

        curr_state = next_state[0]
        story += curr_state + ' '

    return story
