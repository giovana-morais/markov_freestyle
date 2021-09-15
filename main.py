import argparse

from core import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate new lyrics based on your favorite artist')
    parser.add_argument('--artist', help='artist(s) that we\'re using as base')
    parser.add_argument('--songs', default=None, type=int, help='number of lyrics we\'re loading')
    args = parser.parse_args()

    # we should be able to receive both one artist and a list of artists
    args.artist = args.artist.split(',')

    filenames = get_lyrics(args)

    out_filename = get_filename(args.artist)

    lyrics = save_all_lyrics(filenames, f"{out_filename}_out.json")
    clean_lyrics = clean_lyrics(lyrics)

    markov_model = create_markov_model(clean_lyrics, 2)

    for i in range(10):
        generate_lyrics(markov_model, limit=10)
        print('\n')
