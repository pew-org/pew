import os
from functools import partial
from math import ceil
from itertools import zip_longest
from shutil import get_terminal_size

SEP = '  '
L = len(SEP)


def get_rows(venvs, columns_number):
    lines_number = int(ceil(len(venvs) / columns_number))
    for i in range(lines_number):
        yield venvs[i::lines_number]


def row_len(names):
    return sum(map(len, names)) + L * len(names) - L


def get_best_columns_number(venvs):
    max_width, _ = get_terminal_size()
    longest = partial(max, key=len)
    columns_number = 1
    for columns_number in range(1, len(venvs) + 1):
        rows = get_rows(venvs, columns_number)
        longest_row = list(map(longest, zip_longest(*rows, fillvalue='')))
        if row_len(longest_row) > max_width:
            return (columns_number - 1) or 1
    else:
        return columns_number


def align_column(column):
    m = max(map(len, column))
    return [name.ljust(m) for name in column]


def columnize(venvs):
    columns_n = get_best_columns_number(venvs)
    columns = map(align_column, zip_longest(*get_rows(venvs, columns_n), fillvalue=''))
    return map(SEP.join, zip(*columns))


def print_virtualenvs(*venvs):
    venvs = sorted(venvs)
    if os.isatty(1):
        print(*columnize(venvs), sep='\n')
    else:
        print(*venvs, sep=' ')
