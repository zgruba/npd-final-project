"""
This module provides demontration of using functions included in lib.py
"""

import argparse
from cinematic_impact_package.lib import IMDbData, hello, region_genre_analysis, make_comparison, \
    weak_impact, geopolitical_data, impact_vs_data, split_star_countries, strong_impact, \
    create_representation, get_top_countries, movies_quality

NAME_BASICS_PATH = "data/name.basics.tsv"
TITLE_AKAS_PATH = "data/title.akas.tsv"
TITLE_BASICS_PATH = "data/title.basics.tsv"
TITLE_CREW_PATH = "data/title.crew.tsv"
TITLE_EPISODE_PATH = "data/title.episode.tsv"
TITLE_PRINCIPALS_PATH = "data/title.principals.tsv"
TITLE_RATINGS_PATH = "data/title.ratings.tsv"

def main():
    """
    Main function of demontration program.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "name",
        type=str,
        help="Enter your name"
    )

    parser.add_argument(
        "size",
        type=int,
        help="Enter size of the matrix"
    )

    args = parser.parse_args()

    hello(args.name, args.size)

    md = IMDbData((TITLE_BASICS_PATH, TITLE_AKAS_PATH, TITLE_RATINGS_PATH), 'movie', (1780, 2110))

    # print(md.title_info_table())
    # print(md.title_region_table())

    wi = weak_impact(md)
    print(f'Weak impact: {wi.head(20)}')

    gd = geopolitical_data("data/API_SP.POP.TOTL_DS2_en_csv_v2_589802.csv",\
        "data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_595424.csv",\
        "data/API_NY.GDP.PCAP.CD_DS2_en_csv_v2_593971.csv")
    print(gd.head())

    reg_wi, stars = split_star_countries(wi)
    print(stars)

    impact_vs_data(reg_wi, 'sum', gd, 'pop')

    si = strong_impact(md, 'masterpiece_prob', col='averageRating', weight='numVotes')
    print(f'Strong impact: {si.head(20)}')

    qs = create_representation(md, 100, 50000)
    print(qs)

    top = get_top_countries(md, qs, 'weighted_mean', data='averageRating', weight='numVotes')
    print(top)

    reg_si, stars = split_star_countries(si)
    print(stars)

    impact_vs_data(reg_si, 'masterpiece_prob', gd, 'pc')

    movies_quality(md, 100, 'weighted_mean', 200000, data='averageRating', weight='numVotes')

    result = region_genre_analysis(md, 'weighted_mean', data='averageRating', weight='numVotes')

    print(result)

    comparison = make_comparison(result, {'Poland', 'Germany'}, {'Comedy'})

    print(comparison)

if __name__ == "__main__":
    main()
