from pew._print_utils import (
    get_rows,
    get_best_columns_number,
    columnize,
)
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_get_rows():
    rows = list(get_rows(['a', 'b', 'c', 'd'], 2))
    assert len(rows) == 2
    assert rows[0] == ['a', 'c']
    assert rows[1] == ['b', 'd']


def test_get_rows_even():
    rows = list(get_rows(['a', 'b', 'c'], 2))
    assert len(rows) == 2
    assert rows[0] == ['a', 'c']
    assert rows[1] == ['b']


@patch('pew._print_utils.get_terminal_size', return_value=(8, 1))
def test_get_best_columns_number_empty(mock):
    number = get_best_columns_number([])
    assert number == 1


@patch('pew._print_utils.get_terminal_size', return_value=(8, 1))
def test_get_best_columns_number(mock):
    number = get_best_columns_number(['a', 'b', 'c'])
    assert number == 3


@patch('pew._print_utils.get_terminal_size', return_value=(4, 1))
def test_get_best_columns_number_2(mock):
    number = get_best_columns_number(['a', 'b', 'c'])
    assert number == 2


@patch('pew._print_utils.get_terminal_size', return_value=(3, 1))
def test_get_best_columns_number_3(mock):
    number = get_best_columns_number(['a', 'b', 'c'])
    assert number == 1


@patch('pew._print_utils.get_terminal_size', return_value=(3, 1))
def test_get_best_columns_number_4(mock):
    number = get_best_columns_number(['aaaa', 'b', 'c'])
    assert number == 1


@patch('pew._print_utils.get_terminal_size', return_value=(8, 1))
def test_print_columns(mock, capsys):
    columns = columnize(['a', 'b', 'ccc', 'dddd'])
    assert '\n'.join(columns) == "a  ccc \nb  dddd"


@patch('pew._print_utils.get_terminal_size', return_value=(2, 1))
def test_print_columns_2(mock, capsys):
    columns = columnize(['a', 'b', 'ccc', 'dddd'])
    assert '\n'.join(columns) == "a   \nb   \nccc \ndddd"
