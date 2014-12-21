import os
try:
    from shutil import get_terminal_size
except ImportError:
    from backports.shutil_get_terminal_size import get_terminal_size


def get_rows(venvs, columns_number):
    lines_number = len(venvs) // columns_number
    if len(venvs) % columns_number:
        lines_number += 1
    for i in range(lines_number):
        yield venvs[i::lines_number]


def get_best_columns_number(venvs):
    max_width, _ = get_terminal_size()
    for columns_number in range(1, len(venvs) + 1):
        for row in get_rows(venvs, columns_number):
            row_length = sum(get_columns_size(venvs, columns_number))
            row_length += 2 * len(row) - 2
            if row_length > max_width:
                return (columns_number - 1) or 1
    return columns_number


def get_columns_size(venvs, columns_number):
    columns_size = []
    for row in get_rows(venvs, columns_number):
        if not columns_size:
            columns_size = [0] * len(row)
        for i in range(len(row)):
            columns_size[i] = max(len(row[i]), columns_size[i])
    return columns_size


def print_columns(venvs):
    venvs = sorted(venvs)
    columns_number = get_best_columns_number(venvs)
    if columns_number == 1:
        print_one_per_line(venvs)
        return
    columns_size = get_columns_size(venvs, columns_number)
    for row in get_rows(venvs, columns_number):
        row_format = '  '.join(
            '{:<' + str(size) + '}' for size in columns_size[:len(row) - 1]
        )
        row_format += "  {}"
        print(row_format.format(*row))


def print_one_per_line(venvs):
    for venv in sorted(venvs):
        print(venv)


def print_virtualenvs(*venvs):
    if os.isatty(1):
        print_columns(venvs)
    else:
        print_one_per_line(venvs)
