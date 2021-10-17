'''
    Usage example. Generates some lyrics for a given artist.
'''
import argparse

import core

if __name__ == '__main__':
    example_text = '''example:
    python main.py --artists="Pabllo Vittar","Gloria Groove" --songs 2
    python main.py --artists "Linkin Park" --songs 10
    '''
    parser = argparse.ArgumentParser(
        description='generate new lyrics based on your favorite artist',
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--artist', help='artist(s) that we\'re using as base')
    parser.add_argument('--songs', default=None, type=int, help='number of lyrics we\'re loading')
    args = parser.parse_args()

    # we should be able to receive both one artist and a list of artists
    args.artist = args.artist.split(',')

    filenames = core.get_artist_data(args)

    out_filename = core.get_filename(args.artist)

    lyrics = core.save_all_lyrics(filenames, f"lyrics/{out_filename}_out.json")
    clean_lyrics = core.clean_lyrics(lyrics)

    markov_model = core.build_markov_model(clean_lyrics)

    core.save_model(markov_model, f'models/{out_filename}.pkl')

    for i in range(10):
        print(core.generate_lyrics(markov_model, limit=10))
        print('\n')
