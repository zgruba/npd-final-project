from cinematic_impact_package.lib import _get_last, _str_to_int, _code_to_country

def test_get_last():
    assert _get_last([1, float('nan'), 2, 3, float('nan')]) == 3
    assert _get_last([1, 2, 3, float('nan')]) == 3
    assert _get_last([1, 2, 3, 4]) == 4
    assert _get_last([1]) == 1
    assert _get_last([float('nan')]) == 0.0
    assert _get_last([]) == 0

def test_str_to_int():
    assert _str_to_int('0') == '0'
    assert _str_to_int('1') == '1'
    assert _str_to_int('-1') == '-1'
    assert _str_to_int('1.0') == ''
    assert _str_to_int('inf') == ''
    assert _str_to_int('abc') == ''

def test_code_to_country():
    # empty
    # assert _code_to_country('') == '' TODO: add if str empty then "" in the function
    # invalid code
    assert _code_to_country('ZZ') == ''
    # extension code
    assert _code_to_country('XK') == '**XK'
    # valid code
    assert _code_to_country('US') == 'United States'
    assert _code_to_country('GB') == 'United Kingdom'
    assert _code_to_country('IN') == 'India'
    # valid code 3 letters
    assert _code_to_country('USA') == 'United States'
    assert _code_to_country('GBR') == 'United Kingdom'
    assert _code_to_country('IND') == 'India'
    # historical code
    assert _code_to_country('YUG') == '*Yugoslavia, (Socialist) Federal Republic of'
    assert _code_to_country('DDR') == '*German Democratic Republic'
    assert _code_to_country('CSK') == '*Czechoslovakia, Czechoslovak Socialist Republic'
    # historical code 4 letters
    assert _code_to_country('YUCS') == '*Yugoslavia, (Socialist) Federal Republic of'
    assert _code_to_country('DDDE') == '*German Democratic Republic'
    assert _code_to_country('CSHH') == '*Czechoslovakia, Czechoslovak Socialist Republic'

    


