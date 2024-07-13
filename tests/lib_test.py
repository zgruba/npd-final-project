import pytest
import pandas as pd
from io import StringIO
from unittest.mock import patch
from cinematic_impact_package.lib import QUALITY_MEASURES, IMDbData, create_representation, get_top_countries, \
                                        weak_impact, strong_impact, region_genre_analysis, make_comparison, \
                                            load_data, movies_quality, geopolitical_data, impact_vs_data,\
                                                split_star_countries

# Mock data for testing
basics_data = pd.DataFrame({
    'tconst': ['tt001', 'tt002', 'tt003', 'tt004', 'tt005', 'tt006'],
    'titleType': ['movie', 'movie', 'short', 'tvMovie', 'movie', 'short'],
    'startYear': ['2000', '2011', '2022', '1999', '2025', '2012'],
    'genres':['Comedy,Romantic,Drama', 'Moving,Romantic,Action', 'Comedy', 'Moving', '\\N', 'Comedy']
})

ratings_data = pd.DataFrame({
    'tconst': ['tt001', 'tt002', 'tt003', 'tt004', 'tt005', 'tt006'],
    'averageRating': [8.0, 7.5, 9.0, 6.0, 6.7, 5.0],
    'numVotes': [100, 150, 50, 40, 320, 70]
})

akas_data = pd.DataFrame({
    'titleId': ['tt001', 'tt001', 'tt001', 'tt001', 'tt002', 'tt002', 'tt002',  'tt003', 'tt003', 'tt004', 'tt004', 'tt004', 'tt005', 'tt005', 'tt005', 'tt006', 'tt006'],
    'title': ['Movie1', 'Movie1', 'Movie1', 'Pelicula1', 'Movie2', 'Movie2', 'Pellicola2', 'Short1', 'Short1', 'tv1', 'tv1', 'tele1', 'Film3', 'Film3', 'Film3', 'Short2', 'Short2'],
    'region': ['\\N', 'US', 'GB', 'ES', '\\N', 'GB', 'IT', '\\N', 'IN', '\\N', 'DE', 'IT', '\\N', 'PL', 'FR', '\\N', 'IN'],
    'isOriginalTitle': [1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0]
})

@pytest.fixture
def imdb_data_instance():
    with patch('cinematic_impact_package.lib.load_data') as mock_load_data:
        mock_load_data.side_effect = [basics_data, ratings_data, akas_data]
        return IMDbData(('path/to/basics.tsv', 'path/to/akas.tsv', 'path/to/ratings.tsv'), 'movie', (1990, 2011))

@pytest.mark.parametrize('qm, expected, col', [('sum_votes', 10, 'numVotes'), ('mean', 2.5, 'numVotes'), ('flop_prob', 0.5, 'numVotes'), ('masterpiece_prob', 0.0, 'numVotes'), ('two-sided', -0.5, 'numVotes')])
def test_quality_measures_simple(qm, expected, col):
    data = pd.DataFrame({'numVotes': [1, 2, 3, 4]})
    result = QUALITY_MEASURES[qm](data, col=col)
    assert result == expected

def test_quality_measures_weighted_mean():
    data = pd.DataFrame({'data': [4, 5, 6], 'weight': [1, 2, 3]})
    result = QUALITY_MEASURES['weighted_mean'](data, data='data', weight='weight')
    assert result == pytest.approx(5+1/3)

@pytest.fixture
def mock_data():
    data = """tconst\ttitleType\tprimaryTitle\tstartYear
tt0000001\tshort\tCarmencita\t1894
tt0000002\tshort\tLe clown et ses chiens\t1892
tt0000003\tshort\tPauvre Pierrot\t1892"""
    return StringIO(data)

def test_load_data(mock_data):
    expected_df = pd.DataFrame({
        'tconst': ['tt0000001', 'tt0000002', 'tt0000003'],
        'titleType': ['short', 'short', 'short'],
        'primaryTitle': ['Carmencita', 'Le clown et ses chiens', 'Pauvre Pierrot'],
        'startYear': [1894, 1892, 1892]
    })

    result_df = load_data(mock_data, delim='\t')
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_title_info_table(imdb_data_instance):
    result = imdb_data_instance.title_info_table()
    basic_info_type = basics_data[basics_data['titleType'] == 'movie']
    in_type = basic_info_type[basic_info_type['startYear'].isin([str(x) for x in range(1990, 2012)])]
    in_type_filter = in_type['tconst']
    expected = pd.merge(basics_data, ratings_data, on='tconst')
    expected_filtered = pd.merge(in_type_filter, expected, on='tconst')
    pd.testing.assert_frame_equal(result, expected_filtered)

def test_title_region_table(imdb_data_instance):
    result = imdb_data_instance.title_region_table()
    expected = pd.DataFrame({'tconst': ['tt001', 'tt001', 'tt002'], 'region': ['US', 'GB', 'GB']})
    pd.testing.assert_frame_equal(result, expected)

def test_create_representation(imdb_data_instance):
    representation = create_representation(imdb_data_instance, repr_size=2, vote_treshold=90)
    print(representation)
    expected = pd.DataFrame({
        'tconst': ['tt001', 'tt002'],
        'averageRating': [8.0, 7.5],
        'numVotes': [100, 150]
    })
    pd.testing.assert_frame_equal(representation.reset_index(drop=True), expected)

def test_get_top_countries(imdb_data_instance):
    representation = pd.DataFrame({
        'tconst': ['tt001', 'tt002'],
        'averageRating': [8.0, 7.5],
        'numVotes': [100, 150]
    })
    result = get_top_countries(imdb_data_instance, representation, 'sum_votes', col='numVotes')
    expected = pd.DataFrame({'country': ['United Kingdom', 'United States'], 'sum_votes': [250, 100]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_movies_quality(imdb_data_instance, tmp_path):
    output_path = tmp_path / "output.csv"
    result = movies_quality(imdb_data_instance, repr_size=2, vote_treshold=90, qm='sum_votes', col='numVotes', output_path=output_path)
    expected = pd.DataFrame({'country': ['United Kingdom', 'United States'], 'sum_votes': [250, 100]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
    loaded_df = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(loaded_df.reset_index(drop=True), expected.reset_index(drop=True))

def test_weak_impact(imdb_data_instance):
    result = weak_impact(imdb_data_instance)
    print(result)
    expected = pd.DataFrame({'country': ['United Kingdom', 'United States'], 'sum_votes': [250, 100]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_strong_impact(imdb_data_instance):
    result = strong_impact(imdb_data_instance, 'weighted_mean', data='averageRating', weight='numVotes')
    print(result)
    expected = pd.DataFrame({'country': ['United Kingdom', 'United States'], 'weighted_mean': [7.7, 8.0]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

@pytest.fixture
def mock_country_data():
    data = {
        'country': ['USA', 'GBR', '*FR', 'CAN', '*DE'],
        'value': [100, 80, 70, 60, 50]
    }
    return pd.DataFrame(data)

def test_split_star_countries(mock_country_data):
    expected_regulars = pd.DataFrame({
        'country': ['USA', 'GBR', 'CAN'],
        'value': [100, 80, 60]
    })
    
    expected_stars = pd.DataFrame({
        'country': ['*FR', '*DE'],
        'value': [70, 50]
    })

    regulars, stars = split_star_countries(mock_country_data)
    
    pd.testing.assert_frame_equal(regulars.reset_index(drop=True), expected_regulars.reset_index(drop=True))
    pd.testing.assert_frame_equal(stars.reset_index(drop=True), expected_stars.reset_index(drop=True))

@pytest.fixture
def mock_population_data():
    data = """Country Code,2000,2010,2020
USA,282.2,309.3,331.0
GBR,58.8,62.7,67.1
CAN,30.7,34.0,37.7"""
    return StringIO(data)

@pytest.fixture
def mock_gdp_data():
    data = """Country Code,2000,2010,2020
USA,10284,14964,21138
GBR,1652,2429,2707
CAN,742,1617,1643"""
    return StringIO(data)

@pytest.fixture
def mock_per_capita_data():
    data = """Country Code,2000,2010,2020
USA,36420,48366,63543
GBR,28167,38829,40384
CAN,24198,47597,43559"""
    return StringIO(data)

def test_geopolitical_data(mock_population_data, mock_gdp_data, mock_per_capita_data):
    expected_df = pd.DataFrame({
        'country': ['United States', 'United Kingdom', 'Canada'],
        'pop': [331.0, 67.1, 37.7],
        'gdp': [21138, 2707, 1643],
        'pc': [63543, 40384, 43559]
    })

    result_df = geopolitical_data(mock_population_data, mock_gdp_data, mock_per_capita_data)

    pd.testing.assert_frame_equal(result_df, expected_df)

@pytest.fixture
def mock_impact_table():
    data = """country,impact_col
United States,100
United Kingdom,80
Canada,60"""
    return pd.read_csv(StringIO(data))

@pytest.fixture
def mock_geopolitical_data(mock_population_data, mock_gdp_data, mock_per_capita_data):
    return geopolitical_data(mock_population_data, mock_gdp_data, mock_per_capita_data)

def test_impact_vs_data(mock_impact_table, mock_geopolitical_data, tmp_path):
    expected_df = pd.DataFrame({
        'country': ['United States', 'United Kingdom', 'Canada'],
        'impactRating': [1.0, 2.0, 3.0],
        'dataRating': [1.0, 3.0, 2.0],
        'difference': [0.0, 1.0, -1.0]
    })
    expected_sorted = expected_df.sort_values('difference', ascending=False)

    output_path = tmp_path / "output.csv"
    
    impact_vs_data(mock_impact_table, 'impact_col', mock_geopolitical_data, 'pc', output_path)
    loaded_df = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(loaded_df.reset_index(drop=True), expected_sorted.reset_index(drop=True))


def test_region_genre_analysis(imdb_data_instance):
    result = region_genre_analysis(imdb_data_instance, 'weighted_mean', data='averageRating', weight='numVotes')
    print(result)
    expected = pd.DataFrame({'country': [
        'United Kingdom', 'United Kingdom', 'United States', 'United States', 
        'United States', 'United Kingdom', 'United Kingdom', 'United Kingdom'
    ],
    'genre': [
        'Comedy', 'Drama', 'Drama', 'Comedy', 
        'Romantic', 'Romantic', 'Moving', 'Action'
    ],
    'weighted_mean': [
        8.0, 8.0, 8.0, 8.0, 
        8.0, 7.7, 7.5, 7.5
    ]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_make_comparison(tmp_path):
    coun_vs_gen = pd.DataFrame({
        'country': ['US', 'GB', 'IN'],
        'genre': ['Action', 'Drama', 'Comedy'],
        'sum_votes': [100, 200, 300]
    })
    output_path = tmp_path / "output.csv"
    result = make_comparison(coun_vs_gen, {'US', 'GB'}, {'Action', 'Drama'}, output_path)
    print(result)
    expected = pd.DataFrame({
        'country': ['US', 'GB'],
        'genre': ['Action', 'Drama'],
        'sum_votes': [100, 200]
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
    loaded_df = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(loaded_df.reset_index(drop=True), expected.reset_index(drop=True))

