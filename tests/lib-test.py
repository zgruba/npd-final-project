import pytest
import pandas as pd
from unittest.mock import patch
from cinematic_impact_package.lib import QUALITY_MEASURES, IMDbData, create_representation, get_top_countries, \
                                        weak_impact, strong_impact, region_genre_analysis, make_comparison

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

def test_quality_measures_sum_votes():
    data = pd.DataFrame({'numVotes': [1, 2, 3, 4]})
    result = QUALITY_MEASURES['sum_votes'](data, col='numVotes')
    assert result == 10

def test_quality_measures_mean():
    data = pd.DataFrame({'numVotes': [1, 2, 3, 4]})
    result = QUALITY_MEASURES['mean'](data, col='numVotes')
    assert result == 2.5

def test_quality_measures_weighted_mean():
    data = pd.DataFrame({'data': [4, 5, 6], 'weight': [1, 2, 3]})
    result = QUALITY_MEASURES['weighted_mean'](data, data='data', weight='weight')
    assert result == pytest.approx(5+1/3)

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

def test_make_comparison():
    coun_vs_gen = pd.DataFrame({
        'country': ['US', 'GB', 'IN'],
        'genre': ['Action', 'Drama', 'Comedy'],
        'sum_votes': [100, 200, 300]
    })
    result = make_comparison(coun_vs_gen, {'US', 'GB'}, {'Action', 'Drama'})
    print(result)
    expected = pd.DataFrame({
        'country': ['US', 'GB'],
        'genre': ['Action', 'Drama'],
        'sum_votes': [100, 200]
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)