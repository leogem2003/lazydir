import os
import glob
import re
from datetime import datetime
from typing import Iterable, Iterator

from .utils import get_file_datetime, compare_dates


def exact(files: Iterable[str], word:str) -> Iterator[str]:
    """Selects files which name matches exactly 'exact'

    Args:
        files (Iterable[str]): the list of files
        word (str): the word to match exactly

    Yields:
        Iterator[str]: The iterator containing selected files
    """

    return filter(lambda file: word == os.path.basename(file), files)


def contains(files: Iterable[str], word:str) -> Iterator[str]:
    """Selects files which names contain a specific word

    Args:
        files (Iterable[str]): the list of files
        word (str): the word they must contain to be selected

    Yields:
        Iterator[str]: The iterator containing selected files
    """

    return filter(lambda file: word in os.path.basename(file), files)


def created_before(files: Iterable[str], date: str, date_format: str = "%d/%m/%Y", sensibility: str = "d") -> Iterator[str]:
    """Selects files created before a certain date

    Args:
        files (Iterable[str]): the list of files
        date (str): the date used for the comparison
        date_format (str): the format to parse date, by default "%d/%m%/%Y"
        sensibility (str): the sensibility used for date comparison ('s','m','h','d'), default is 'd'

    Yields:
        Iterator[str]: The iterator containing selected files
    """

    return filter(
        lambda file: compare_dates(get_file_datetime(file, 'ctime'),
            datetime.strptime(date, date_format), precision=sensibility) == -1,
        files)


def created_after(files: Iterable[str], date: str, date_format: str = "%d/%m/%Y", sensibility: str = "d") -> Iterator[str]:
    """Selects files created after a certain date

    Args:
        files (Iterable[str]): the list of files
        date (str): the date used for the comparison
        date_format (str): the format to parse date, by default "%d/%m%/%Y"

    Yields:
        Iterator[str]: The iterator containing selected files
    """
    return filter(
        lambda file: compare_dates(get_file_datetime(file, 'ctime'),
            datetime.strptime(date, date_format), precision=sensibility) == 1,
        files)


def modified_before(files: Iterable[str], date: str, date_format: str = "%d/%m/%Y", sensibility: str = "d") -> Iterator[str]:
    """Selects files modified before a certain date

    Args:
        files (Iterable[str]): the list of files
        date (str): the date used for the comparison
        date_format (str): the format to parse date, by default "%d/%m%/%Y"

    Yields:
        Iterator[str]: The iterator containing selected files
    """
    return filter(
        lambda file: compare_dates(get_file_datetime(file, 'mtime'),
            datetime.strptime(date, date_format), precision=sensibility) == -1,
        files)


def modified_after(files: Iterable[str], date: str, date_format: str = "%d/%m/%Y", sensibility: str = "d") -> Iterator[str]:
    """Selects files modified after a certain date

    Args:
        files (Iterable[str]): the list of files
        date (str): the date used for the comparison
        date_format (str): the format to parse date, by default "%d/%m%/%Y"

    Yields:
        Iterator[str]: The iterator containing selected files
    """
    return filter(
        lambda file: compare_dates(get_file_datetime(file, 'mtime'),
            datetime.strptime(date, date_format), precision=sensibility) == 1,
        files)


def created_equal(files: Iterable[str], date: str, date_format: str = "%d/%m/%Y", sensibility: str = "d") -> Iterator[str]:
    """Selects files created in a certain date

    Args:
        files (Iterable[str]): the list of files
        date (str): the date used for the comparison
        date_format (str): the format to parse date, by default "%d/%m%/%Y"

    Yields:
        Iterator[str]: The iterator containing selected files
    """
    return filter(
        lambda file: compare_dates(get_file_datetime(file, 'ctime'),
            datetime.strptime(date, date_format), precision=sensibility) == 0,
        files)


def modified_equal(files: Iterable[str], date: str, date_format: str = "%d/%m/%Y", sensibility: str = "d") -> Iterator[str]:
    """Selects files modified in a certain date

    Args:
        files (Iterable[str]): the list of files
        date (str): the date used for the comparison
        date_format (str): the format to parse date, by default "%d/%m%/%Y"

    Yields:
        Iterator[str]: The iterator containing selected files
    """
    return filter(
        lambda file: compare_dates(get_file_datetime(file, 'mtime'),
            datetime.strptime(date, date_format), precision=sensibility) == 0,
        files)

def extension_exact(files: Iterable[str], word:str) -> Iterator[str]:
    """Selects files which extension matches exactly 'exact'

    Args:
        files (Iterable[str]): the list of files
        word (str): the word to match exactly

    Yields:
        Iterator[str]: The iterator containing selected files
    """

    return filter(lambda file: word == os.path.basename(file).split('.')[-1], files)


def extension_contains(files: Iterable[str], word: str) -> Iterator[str]:
    """Selects files which extension names contain a specific word

    Args:
        files (Iterable[str]): the list of files
        word (str): the word they must contain to be selected

    Yields:
        Iterator[str]: The iterator containing selected files
    """

    return filter(lambda file: word in os.path.basename(file).split('.')[-1], files)


def starts_with(files: Iterable[str], word: str) -> Iterator[str]:
    """Selects files which starts with a specific string

    Args:
        files (Iterable[str]): the list of files
        word (str): the word to match at the start of the strings

    Yields:
        Iterator[str]: the list of selected files
    """

    return filter(lambda file: os.path.basename(file).startswith(word), files)


def ends_with(files: Iterable[str], word: str) -> Iterator[str]:
    """Selects files which ends with a specific string (extension excluded)

    Args:
        files (Iterable[str]): the list of files
        word (str): the word to match at the end of the strings

    Yields:
        Iterator[str]: the list of selected files
    """

    return filter(lambda file: '.'.join(os.path.basename(file).split('.')[:-1]).endswith(word), files)

def select_glob(dir:str, expr:str) -> Iterator[str]:
    """Selects files which match a glob expression

    Args:
        dir (str): parent directory
        expr (str): glob expression to be evalued

    Yields:
        Iterator[str]: the list of selected files
    """

    return (file for file in glob.iglob(dir+expr) if os.path.isfile(file))

def match(files: Iterable[str], expr: str) -> Iterator[str]:
    """Selects files which match a regexpr

    Args:
        files (Iterable[str]): the list of files
        expr (str): the expression used for matching

    Yields:
        Iterator[str]: the list of selected files
    """
    regexpr = re.compile(expr)

    return filter(lambda file: regexpr.match(os.path.basename(file)), files)


def search(files: Iterable[str], expr: str) -> Iterator[str]:
    """Selects files where regexpr is found

    Args:
        files (Iterable[str]): the list of files
        expr (str): the expression used for finding

    Yields:
        Iterator[str]: the list of selected files
    """
    regexpr = re.compile(expr)

    return filter(lambda file: regexpr.search(os.path.basename(file)), files)
