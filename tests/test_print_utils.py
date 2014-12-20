from pew._print_utils import (
    get_rows,
    get_columns_size,
    get_best_columns_number,
    print_columns,
    print_one_per_line,
)
from unittest.mock import patch


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


def test_get_columns_size():
    sizes = get_columns_size(['aa', 'b', 'c'], 2)
    assert sizes == [2, 1]


def test_get_columns_size_2():
    sizes = get_columns_size(['a', 'b', 'ccc', 'dddd'], 2)
    assert sizes == [1, 4]


@patch('pew._print_utils.shutil.get_terminal_size', return_value=(8, 1))
def test_get_best_columns_number(mock):
    number = get_best_columns_number(['a', 'b', 'c'])
    assert number == 3


@patch('pew._print_utils.shutil.get_terminal_size', return_value=(4, 1))
def test_get_best_columns_number_2(mock):
    number = get_best_columns_number(['a', 'b', 'c'])
    assert number == 2


@patch('pew._print_utils.shutil.get_terminal_size', return_value=(3, 1))
def test_get_best_columns_number_3(mock):
    number = get_best_columns_number(['a', 'b', 'c'])
    assert number == 1


@patch('pew._print_utils.shutil.get_terminal_size', return_value=(3, 1))
def test_get_best_columns_number_4(mock):
    number = get_best_columns_number(['aaaa', 'b', 'c'])
    assert number == 1


def test_print_one_per_line(capsys):
    print_one_per_line(['a', 'b', 'ccc', 'dddd'])
    out, err = capsys.readouterr()
    assert out == "a\nb\nccc\ndddd\n"


@patch('pew._print_utils.shutil.get_terminal_size', return_value=(8, 1))
def test_print_columns(mock, capsys):
    print_columns(['a', 'b', 'ccc', 'dddd'])
    out, err = capsys.readouterr()
    assert out == "a  ccc\nb  dddd\n"


@patch('pew._print_utils.shutil.get_terminal_size', return_value=(2, 1))
def test_print_columns_2(mock, capsys):
    print_columns(['a', 'b', 'ccc', 'dddd'])
    out, err = capsys.readouterr()
    assert out == "a\nb\nccc\ndddd\n"
