"""
This module provides demontration of using functions included in lib.py
"""

import argparse
from cinematic_impact_package.lib import IMDbData, region_genre_analysis, make_comparison, \
    weak_impact, geopolitical_data, impact_vs_data, split_star_countries, strong_impact, \
    create_representation, get_top_countries, movies_quality

QM = ['sum_votes', 'mean', 'weighted_mean', 'flop_prob', 'masterpiece_prob','two-sided']

DEFAULT_QM_ARGS = {
    'sum_votes': {'col': 'numVotes'},
    'mean': {'col': 'averageRating'},
    'weighted_mean': {'data':'averageRating', 'weight':'numVotes'},
    'flop_prob': {'col': 'averageRating'},
    'masterpiece_prob': {'col': 'averageRating'},
    'two-sided': {'col': 'averageRating'}
}

KNOWN_GENRES = ['Romance', 'Documentary', 'News', 'Sport', 'Action', 'Adventure', 'Biography',\
             'Drama', 'Fantasy', 'Comedy', 'War', 'Crime', 'Family', 'History', 'Sci-Fi', 'Thriller',\
                 'Western', 'Mystery', 'Horror', 'Music', 'Animation', 'Musical', 'Film-Noir', 'Adult',\
                     'Reality-TV', 'Game-Show', 'Talk-Show']

KNOWN_PROD_TYPES = ['short', 'movie', 'tvShort', 'tvMovie', 'tvSeries', 'tvEpisode', 'tvMiniSeries',\
                 'tvSpecial', 'video', 'videoGame', 'tvPilot']

def parse_arguments():
    """
    Function supporting parsing arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--basics",
        type=str,
        required=True,
        help="Path to the TSV file including cols = ['tconst', 'genres', 'titleType', 'startYear']."
    )
    parser.add_argument(
        "--ratings",
        type=str,
        required=True,
        help="Path to the TSV file including cols = ['tconst', 'numVotes', 'averageRating]."
    )
    parser.add_argument(
        "--akas",
        type=str,
        required=True,
        help="Path to the TSV file including cols = ['titleId','title','region','isOriginalTitle']."
        )
    parser.add_argument(
        "--gdp",
        type=str,
        required=True,
        help="Path to the CSV file with GDP data with column \"Country Code\" \
        with ISO 3166-1 and columns representing years."
    )
    parser.add_argument(
        "--pop",
        type=str,
        required=True,
        help="Path to the CSV file with population data with column \"Country Code\" \
        with ISO 3166-1 and columns representing years."
    )
    parser.add_argument(
        "--pc",
        type=str,
        required=True,
        help="Path to the CSV file with GDP per capita data with column \"Country Code\" \
            with ISO 3166-1 and columns representing years."
        )
    parser.add_argument(
        "--countries",
        type=str,
        nargs='+',
        required=True,
        help="List of countries to compare."
    )
    parser.add_argument(
        "--genres",
        type=str,
        nargs='+',
        choices=KNOWN_GENRES,
        required=True,
        help="List of genres to compare."
        )
    parser.add_argument(
        "--prodtype",
        type=str,
        choices=KNOWN_PROD_TYPES,
        default='movie',
        help="The type of titles to filter (e.g., 'movie', 'tvEpisode', 'short', 'videoGame')."
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1800,
        help="The start year of the range to filter."
    )
    parser.add_argument(
        "--end",
        type=int,
        default=2025,
        help="The end year of the range to filter."
        )
    parser.add_argument(
        "--qm",
        type=str,
        choices=QM,
        default='weighted_mean',
        help="Quality measure"
        )
    parser.add_argument(
        "--votetreshold",
        type=int,
        default=100000,
        help="Minimum number of votes required for a movie to be included."
        )
    args = parser.parse_args()
    return args

def validate_arguments(args):
    """
    Function validating arguments.
    """
    if args.end < args.start:
        raise ValueError('End year has smalller value than start year.')
    if args.votetreshold < 0:
        raise ValueError('Votetreshold is smaller than 0, it should be nonnegative number.')

def main():
    """
    Main function of demontration program.
    """
    # Initialisation
    print("\nInitialisation")
    args = parse_arguments()
    validate_arguments(args)
    md = IMDbData((args.basics, args.akas, args.ratings), args.prodtype, (args.start, args.end))

    # Movies quality (Task 1)
    print("\nTask 1")
    print(f"Create representation for 100 representants for {args.votetreshold} vote treshold.")
    qs = create_representation(md, 100,  args.votetreshold)
    print(qs)

    print(f"\nGet top10 countries for chosen representants for {args.votetreshold} vote treshold.")
    top = get_top_countries(md, qs, args.qm, **DEFAULT_QM_ARGS[args.qm])
    print(top)

    for repr_num in [10, 20, 30, 50, 100, 200]:
        result = movies_quality(md, repr_num, args.qm, args.votetreshold, **DEFAULT_QM_ARGS[args.qm])
        print(f"\nFor {repr_num} best representants we get:")
        print(result)

    # Weak impact (Task 2.1)
    print("\nTask 2")
    print("Geopolitical data:")
    gd = geopolitical_data(args.pop, args.gdp, args.pc)
    print(gd.head())

    wi = weak_impact(md)
    print(f'\nWeak impact:\n{wi.head(20)}')

    reg_wi, stars = split_star_countries(wi)
    print(f"\nHistrorical (*) or undefined (**) countries' weak impact:\n{stars}")

    impact_vs_data(reg_wi, 'sum_votes', gd, 'pop')
    impact_vs_data(reg_wi, 'sum_votes', gd, 'gdp')
    impact_vs_data(reg_wi, 'sum_votes', gd, 'pc')

    # Strong impact (Task 2.2)
    si = strong_impact(md, args.qm, **DEFAULT_QM_ARGS[args.qm])
    print(f'\nStrong impact:\n{si.head(20)}')

    reg_si, stars = split_star_countries(si)
    print(f"\nHistrorical (*) or undefined (**) countries' strong impact:\n{stars}")

    impact_vs_data(reg_si, args.qm, gd, 'pop')
    impact_vs_data(reg_si, args.qm, gd, 'gdp')
    impact_vs_data(reg_si, args.qm, gd, 'pc')

    # Additional region-genre analysis (Task3)
    print("\nTask 3")
    print("Additional region-genre analysis:")
    result = region_genre_analysis(md, args.qm, **DEFAULT_QM_ARGS[args.qm])
    print(result)

    comparison = make_comparison(result, set(args.countries), set(args.genres))
    print(f"\nComparison for countries: {args.countries} and genres: {args.genres}:\n{comparison}")

if __name__ == "__main__":
    main()
