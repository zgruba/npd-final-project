import numpy as np
import pandas as pd
import warnings
from pycountry import countries, historic_countries
from math import isnan

warnings.filterwarnings('ignore')


FLOP_TH = 3
MASTERPIECE_TH = 7

QUALITY_MEASURES = {
    'mean': lambda x, **kwargs: sum(x[kwargs['col']])/len(x),
    'weighted_mean': lambda x, **kwargs: sum(x[kwargs['data']]*x[kwargs['weight']])/sum(x[kwargs['weight']]),
    'flop_prob': lambda x, **kwargs: sum(x[kwargs['col']]<FLOP_TH)/len(x),
    'masterpiece_prob': lambda x, **kwargs: sum(x[kwargs['col']]>MASTERPIECE_TH)/len(x),
    'two-sided': lambda x, **kwargs: (sum(x[kwargs['col']]>MASTERPIECE_TH) - sum(x[kwargs['col']]<FLOP_TH))/len(x)
}

class MovieFilter:
    def __init__(self, basics_path: str):
        basic_info = load_data(basics_path)
        self.is_movie = basic_info[basic_info['titleType'] == 'movie']['tconst']
    
    def filter(self, df: pd.DataFrame):
        return pd.merge(self.is_movie, df, on='tconst')


def hello(name, size):
    zeros = np.zeros(size)
    print(f"Hello {name}! We can use numpy.zeros({size}): {zeros}")

def load_data(file, delim='\t', usecols=None):
    print(f"Loading {file}...")
    dataframe = pd.read_csv(file, delimiter=delim, usecols=usecols)
    print(dataframe.head())
    return dataframe

def weak_impact(movie_filter: MovieFilter, rating_reduced_table, akas_reduced_table):
    akas_reduced_table = akas_reduced_table.rename(columns={'titleId': "tconst"})
    akas_movies = movie_filter.filter(akas_reduced_table)
    org_titles = akas_movies[akas_movies['isOriginalTitle'] == 1][['tconst', 'title']]

    prepared_akas = akas_movies[akas_movies['isOriginalTitle'] == 0][["tconst", 'title', 'region']]
    tit2reg = pd.merge(org_titles, prepared_akas, on=["title", "tconst"])[["tconst", 'region']]
    tit2reg_with_rating = pd.merge(tit2reg, rating_reduced_table, on="tconst")    

    weak_impact = tit2reg_with_rating[['region', 'numVotes']].groupby(['region'], as_index=False).sum()
    weak_impact['region'] = weak_impact['region'].map(_code_to_country)
    weak_impact.rename(columns={'region':'country'}, inplace=True)
    return weak_impact

def strong_impact(movie_filter: MovieFilter, rating_reduced_table, akas_reduced_table, qm, *args, **kwargs):
    akas_reduced_table = akas_reduced_table.rename(columns={'titleId': "tconst"})
    akas_movies = movie_filter.filter(akas_reduced_table)
    org_titles = akas_movies[akas_movies['isOriginalTitle'] == 1][['tconst', 'title']]

    prepared_akas = akas_movies[akas_movies['isOriginalTitle'] == 0][["tconst", 'title', 'region']]
    tit2reg = pd.merge(org_titles, prepared_akas, on=["title", "tconst"])[["tconst", 'region']]
    tit2reg_with_rating = pd.merge(tit2reg, rating_reduced_table, on="tconst")    

    fun = QUALITY_MEASURES[qm] if isinstance(qm, str) else qm
    strong_impact = tit2reg_with_rating[['region', 'numVotes', 'averageRating']].groupby(['region'], as_index=False).apply(fun, *args, **kwargs)
    strong_impact.columns = [qm if col is None else col for col in strong_impact.columns]
    strong_impact['region'] = strong_impact['region'].map(_code_to_country)
    strong_impact.rename(columns={'region':'country'}, inplace=True)
    return strong_impact

def split_star_countries(df):
    stars = df[df['country'].str[0] == "*"]
    regulars = df[df['country'].str[0] != "*"]

    return (regulars, stars)

def geopolitical_data(population_path: str, gdp_path: str, per_capita_path: str):
    population = load_data(population_path, delim=',')
    gdp = load_data(gdp_path, delim=',')
    per_capita = load_data(per_capita_path, delim=',')

    years = set(list(population.columns) + list(gdp.columns) + list(per_capita.columns))
    years = {_str_to_int(col) for col in years} - {""}
    years = [str(x) for x in  sorted(list(years))]

    population['pop'] = population[years].agg(_get_last, axis=1)
    gdp['gdp'] = gdp[years].agg(_get_last, axis=1)
    per_capita['pc'] = per_capita[years].agg(_get_last, axis=1)

    population = population[["Country Code", 'pop']]
    gdp = gdp[["Country Code", 'gdp']]
    per_capita = per_capita[["Country Code", 'pc']]

    result = pd.merge(population, gdp, on="Country Code")
    result = pd.merge(result, per_capita, on="Country Code")

    result['country'] = result['Country Code'].map(_code_to_country)
    result = result[result['country'] != ""]
    return result[['country', 'pop', 'gdp', 'pc']]

def impact_vs_data(impact_df, impact_col, data_df, data_col, output_path = None):
    data_rating = data_df.sort_values(data_col, ascending = False)
    impact_rating = impact_df.sort_values(impact_col, ascending=False)

    data_rating['dataRating'] = data_rating[data_col].rank(method='dense', ascending=False)
    impact_rating['impactRating'] = impact_rating[impact_col].rank(method='dense', ascending=False)

    print(data_rating)
    print(impact_rating)

    result = pd.merge(impact_rating, data_rating, on='country')
    result['difference'] = result['dataRating'] - result['impactRating']
    result = result[['country', 'impactRating', 'dataRating', 'difference']].sort_values('difference')

    print(result)
    if output_path is not None:
        result.to_csv(output_path, index=False)
    else:
        result.to_csv(f"out/task2_{impact_col}_to_{data_col}.csv", index=False)

def _code_to_country(x: str) -> str:
    size = len(x)
    kwargs = {f"alpha_{size}": x}

    try: 
        v = countries.get(**kwargs)
        if v is not None:
            return v.name
    except KeyError:
        pass

    try: 
        v = historic_countries.get(**kwargs)
        if v is not None:
            return "*" + v.name
    except KeyError:
        pass

    if x[0] == "X":
        return "**" + x

    return ""

def _str_to_int(x):
    try:
        return str(int(x))
    except ValueError:
        return ""

def _get_last(x):
    for el in reversed(x):
        if not isnan(el):
            return el
    return 0.0