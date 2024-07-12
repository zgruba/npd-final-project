"""
This module provides demontration of using functions included in lib.py
"""

import argparse
from cinematic_impact_package.lib import IMDbData, region_genre_analysis, make_comparison, \
    weak_impact, geopolitical_data, impact_vs_data, split_star_countries, strong_impact, \
    create_representation, get_top_countries, movies_quality

NAME_BASICS_PATH = "data/name.basics.tsv"
TITLE_AKAS_PATH = "data/title.akas.tsv"
TITLE_BASICS_PATH = "data/title.basics.tsv"
TITLE_CREW_PATH = "data/title.crew.tsv"
TITLE_EPISODE_PATH = "data/title.episode.tsv"
TITLE_PRINCIPALS_PATH = "data/title.principals.tsv"
TITLE_RATINGS_PATH = "data/title.ratings.tsv"


DEFAULT_QM_ARGS = {
    'sum_votes': {'col': 'numVotes'},
    'mean': {'col': 'averageRating'},
    'weighted_mean': {'data':'averageRating', 'weight':'numVotes'},
    'flop_prob': {'col': 'averageRating'},
    'masterpiece_prob': {'col': 'averageRating'},
    'two-sided': {'col': 'averageRating'}
}

def parse_arguments():
    """
    Function supporting parsing arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--basics",
        type=str, 
        required=True, 
        help="Path to the TSV file including cols = ['tconst', 'genres', 'titleType', 'startYear', 'endYear']."
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
        help="Path to the CSV file with GDP data."
    )
    parser.add_argument(
        "--pop",
        type=str, 
        required=True, 
        help="Path to the CSV file with population data."
    )
    parser.add_argument(
        "--pc",
        type=str, 
        required=True, 
        help="Path to the CSV file with GDP per capita data."
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
        required=True, 
        help="List of genres to compare."
        )
    parser.add_argument(
        "--prod_type",
        type=str,
        default='movie',
        help="The type of titles to filter (e.g., 'movie', 'tvEpisode', 'short', 'videoGame')."
    )
    parser.add_argument(
        "--year_start",
        type=int,
        default=1800,
        help="The start year of the range to filter."
    )
    parser.add_argument(
        "--year_end",
        type=int, 
        default=2025,
        help="The end year of the range to filter."
        )
    parser.add_argument(
        "--qm",
        type=str, 
        default='weighted_mean',
        help="Quality measure"
        )
    parser.add_argument(
        "--vote_treshold",
        type=int, 
        default=100000,
        help="Minimum number of votes required for a movie to be included."
        )
    args = parser.parse_args()
    return args

def main():
    """
    Main function of demontration program.
    """
    # Initialisation
    args = parse_arguments()
    md = IMDbData((args.basics, args.akas, args.ratings), args.prod_type, (args.year_start, args.year_end))

    # print(md.title_info_table())
    # print(md.title_region_table())

    # Weak impact
    wi = weak_impact(md)
    print(f'Weak impact: {wi.head(20)}')

    gd = geopolitical_data(args.pop, args.gdp, args.pc)
    print(gd.head())

    reg_wi, stars = split_star_countries(wi)
    print(stars)

    impact_vs_data(reg_wi, 'sum_votes', gd, 'pop')
    impact_vs_data(reg_wi, 'sum_votes', gd, 'gdp')
    impact_vs_data(reg_wi, 'sum_votes', gd, 'pc')

    # Strong impact
    si = strong_impact(md, args.qm, **DEFAULT_QM_ARGS[args.qm])
    print(f'Strong impact: {si.head(20)}')

    reg_si, stars = split_star_countries(si)
    print(stars)

    impact_vs_data(reg_si, args.qm, gd, 'pop')
    impact_vs_data(reg_si, args.qm, gd, 'gdp')
    impact_vs_data(reg_si, args.qm, gd, 'pc')

    # Movies quality
    qs = create_representation(md, 100, 50000)
    print(qs)

    top = get_top_countries(md, qs, args.qm, **DEFAULT_QM_ARGS[args.qm])
    print(top)

    # Pętla 10, 20, 30, 50, 100, 200
    movies_quality(md, 100, args.qm, 200000, **DEFAULT_QM_ARGS[args.qm])

    # Additional region-genre analysis
    result = region_genre_analysis(md, args.qm, **DEFAULT_QM_ARGS[args.qm])
    print(result)

    comparison = make_comparison(result, set(args.countries), set(args.genres))
    print(comparison)

if __name__ == "__main__":
    main()
