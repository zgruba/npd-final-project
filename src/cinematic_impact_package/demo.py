import argparse
from cinematic_impact_package.lib import hello, load_data, weak_impact, MovieFilter, YearsFilter,geopolitical_data, impact_vs_data, split_star_countries, strong_impact, create_representation, get_top_countries, movies_quality, own_preparation, own_analysis, make_comparison

NAME_BASICS_PATH = "data/name.basics.tsv"
TITLE_AKAS_PATH = "data/title.akas.tsv"
TITLE_BASICS_PATH = "data/title.basics.tsv"
TITLE_CREW_PATH = "data/title.crew.tsv"
TITLE_EPISODE_PATH = "data/title.episode.tsv"
TITLE_PRINCIPALS_PATH = "data/title.principals.tsv"
TITLE_RATINGS_PATH = "data/title.ratings.tsv"

def main():
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

    ratings_set = load_data("data/title.ratings.tsv")
    movie_filter = MovieFilter("data/title.basics.tsv")
    basic_set = load_data("data/title.basics.tsv")
    reduced_akas_set = load_data("data/title.akas.tsv", usecols=['titleId','title','region','isOriginalTitle'])
    
    # wi = weak_impact(movie_filter, ratings_set, reduced_akas_set)
    # print(wi.head())

    # gd = geopolitical_data("data/API_SP.POP.TOTL_DS2_en_csv_v2_589802.csv","data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_595424.csv", "data/API_NY.GDP.PCAP.CD_DS2_en_csv_v2_593971.csv")
    # print(gd.head())

    # reg_wi, stars = split_star_countries(wi)
    # print(stars)

    # impact_vs_data(reg_wi, 'numVotes', gd, 'pop')

    # si = strong_impact(movie_filter, ratings_set, reduced_akas_set, 'masterpiece_prob', col='averageRating', weight='numVotes')
    # print(si.head())

    # qs = create_representation(movie_filter, ratings_set, 100, 50000)
    # print(qs)

    # top = get_top_countries(movie_filter, qs, reduced_akas_set, 'weighted_mean', data='averageRating', weight='numVotes')
    # print(top)

    # reg_si, stars = split_star_countries(si)
    # print(stars)

    # impact_vs_data(reg_si, 'masterpiece_prob', gd, 'pc')

    # movies_quality(movie_filter, ratings_set, 100, reduced_akas_set, 'weighted_mean', 200000, data='averageRating', weight='numVotes')

    bas, cou = own_preparation(movie_filter, basic_set, reduced_akas_set)

    result = own_analysis(movie_filter, bas, ratings_set, cou, 'weighted_mean', data='averageRating', weight='numVotes')

    print(result)

    comparison = make_comparison(result, {'Poland', 'Germany'}, {'Comedy'})

    print(comparison)

    years_filter = YearsFilter("data/title.basics.tsv", 1970, 2010)
    print(years_filter.filter(movie_filter.filter(basic_set)))


if __name__ == "__main__":
    main()