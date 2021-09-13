import argparse

import core

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate new lyrics based on your favorite artist')
    parser.add_argument('--artist', help='artist(s) that we\'re using as base')
    parser.add_argument('--songs', default=None, type=int, help='number of lyrics we\'re loading')
    args = parser.parse_args()

    # ok, so we should be able to receive both one artist and a list of artists
    args.artist = args.artist.split(',')

    filenames = core.get_lyrics(args)

    out_filename = core.get_filename(args.artist)

    lyrics = core.save_all_lyrics(filenames, f"{out_filename}_out.json")
    clean_lyrics = core.clean_text(lyrics)

    markov_model = core.create_markov_model(clean_lyrics, 2)

    for i in range(10):
        core.generate_lyrics(markov_model, limit=10)
        print('\n')
