import json
import pickle
import random
import re

from lyricsgenius import Genius
from nltk.tokenize import word_tokenize

from genius_secrets import ACCESS_TOKEN

def save_model(model, filename='model.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(model, f)

    return

def load_model(filename='model.pkl'):
    with open(filename, 'rb') as f:
        model = pickle.load(filename)

    return model

def get_artist_data(args):
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
        filename = get_filename(artist_name)
        artist.save_lyrics(filename)

        genius_files.append(filename)

    return genius_files

def save_all_lyrics(json_file_list, lyrics_file):
    """
    select only lyrics from all genius data and put everything in the same file
    """
    lyrics = ""

    for json_file in json_file_list:
        with open(json_file, 'r') as f:
            genius_data = json.load(f)

        for idx, song in enumerate(genius_data['songs']):
            lyrics += song['lyrics']

    with open(lyrics_file, 'w') as f:
        f.write(lyrics)

    return lyrics

def clean_lyrics(lyrics):
    clean_lyrics = lyrics.lower()
    clean_lyrics = clean_lyrics.replace('\n', ' ').replace('\r', ' ')
    clean_lyrics = re.sub(r"[,.\"\'!@#$%^&*(){}?/;`~:<>+=-\\]", "", clean_lyrics)
    clean_lyrics = clean_lyrics.replace("EmbedShare", "")
    clean_lyrics = clean_lyrics.replace("URLCopyEmbedCopy", "")
    clean_lyrics = word_tokenize(clean_lyrics)

    return clean_lyrics

def get_filename(artist_name):
    if isinstance(artist_name, str):
        filename = artist_name.lower().replace(' ', '_') + ".json"
    elif isinstance(artist_name, list):
        filename = '_'.join(artist_name).lower().replace(' ', '_')

    return filename

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

    # TODO: add heres some if/else statement to check any flags to this function
    save_model(markov_model)

    markov_model = calculate_probabilities(markov_model)
    return markov_model

def update_markov_model(markov_model, new_lyrics, ngrams=2):
    for i in range(len(new_lyrics)-ngrams-1):
        current_state, next_state = "", ""

        for j in range(ngrams):
            current_state += new_lyrics[i+j] + " "
            next_state += new_lyrics[i+j+ngrams] + " "

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

    # TODO: add heres some if/else statement to check any flags to this function
    save_model(markov_model)

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
