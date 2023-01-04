import os
import re
from typing import Iterable

from .utils import compose_filepath, datadict, filetuple


def replace(files: Iterable[str], char: str, repl: str, count: int = -1) -> list[str]:
    """Replaces <char> string with <repl> in each filename, extension excluded.
    <count> is used to specify the number of replacements

    Args:
        files (Iterable[str]): The list of files
        char (str): character to replace
        repl (str): replacement
        count (int): number of replacements (-1 to replace all). Default to -1

    Returns:
        list[str]: a list containing replaced files
    """
    renamed = []
    for _, dirname, filename, name, ext in filetuple(files):
        replaced = name.replace(char, repl, count)
        renamed.append(compose_filepath(dirname, replaced, ext))

    return renamed


def sub(files: Iterable[str], expr: str, repl: str, count: int = 0) -> list[str]:
    """Subsitutes matched sequences using re.sub

    Args:
        files (Iterable[str]): the list of files
        expr (str): regular expression used for matching
        repl (str): replacement
        count (int): number of substitutions. Defaults to 0 (substitute all)
    Returns:
        list[str]: the list containing processed files
    """
    regexpr = re.compile(expr)
    renamed = []
    for _, dirname, filename, name, ext in filetuple(files):
        replaced = re.sub(regexpr, repl, name, count)

        renamed.append(compose_filepath(dirname, replaced, ext))

    return renamed


def capitalize(files: Iterable[str], prev_char: str = ' ', count: int = -1, capitalize_start: bool = True) -> list[str]:
    """Capitalise files' names basing on <prev_char> as separator. If <capitalize start> is set to False,
    don't capitalise the first letter. File's extension is not affected.


    Args:
        files (Iterable[str]): The list of files
        prev_char (str, optional): Character the following letter will be capitalised. Defaults to ' '.
        count (int, optional): The maximum number of capitalisations, -1 to capitalise all. Defaults to -1.
        capitalize_start (bool, optional): Whether or not capitalise the first letter of the file. Defaults to True.

    Returns:
        list[str]: Files' capitalised names
    """
    capitalized_names = []

    for _, dirname, filename, name, ext in filetuple(files):
        words = name.split(prev_char, maxsplit=count)
        first_word = words[0]

        if capitalize_start:
            if first_word:
                first_word = first_word[0].upper() + first_word[1:]

        if (l := len(words)) == 1:
            capitalized_names.append(
                f'{dirname}{"/" if dirname else ""}{prev_char.join((first_word,))}.{ext}')
            continue

        if count > l or count == -1:
            count = l
            missing = []
        else:
            missing = words[count:]

        upper_words = [word[0].upper() + word[1:] if word else '' for word in words[1:count]] + missing
        capitalized_names.append(compose_filepath(
            dirname, prev_char.join((first_word, *upper_words)), ext))

    return capitalized_names


def upper(files: Iterable[str]) -> list[str]:
    """Transforms files' names into uppercase letters

    Args:
        files (Iterable[str]): the list of files

    Returns:
        list[str]: Filenames in uppercase
    """
    upper_files = []

    for _, dirname, filename, name, ext in filetuple(files):
        upper_files.append(compose_filepath(dirname, name.upper(), ext))

    return upper_files


def lower(files: Iterable[str]) -> list[str]:
    """Transforms files' names into lowercase letters

    Args:
        files (Iterable[str]): the list of files

    Returns:
        list[str]: Filenames in lowercase
    """
    upper_files = []

    for _, dirname, filename, name, ext in filetuple(files):
        upper_files.append(compose_filepath(dirname, name.lower(), ext))

    return upper_files


def rename_format(files: Iterable[str], filedata: list[tuple[str]], names: list[str], template: str) -> list[str]:
    """rename a file using a template string

    Args:
        files (Iterable[str]): the list of files
        filedata (list[tuple[str]]): a list containing the data associated to each file
        names (list[str]): list of names assigned to data fields. If no name is assigned, the value must be set to None
        template (str): template string. For named variables, it must be inserted the name of the variable, while
            unnamed variables are represented as data_<index> where index is the position of this variable in the 
            list of unnamed variables

    Returns:
        list[str]: a list containing renamed files
    """

    formatted = []
    if not filedata:
        filedata = [(file, []) for file in files]
    for file, data in zip(filetuple(files), filedata):
        #data_indx = 0
        pardir = file[1]
        filename = file[3]
        extension = file[4]
        data_names = {'basename': filename, 'extension': extension,
                      'filename': f"{filename}.{extension}"}

        data_names.update(datadict(data[1], names))
        formatted.append(compose_filepath(pardir, template.format(**data_names), None))

    return formatted


def rewrite(original: list[str], renamed: list[str]) -> None:
    """Applies modifications substituting using os.rename original files with the renamed ones
    creating new folders if necessary.

    Args:
        original (list[str]): the list of original files
        renamed (list[str]): the list of renamed files
    """
    for o, r in zip(original, renamed):
        r_dir = os.path.dirname(r)
        if o != r:
            if not os.path.exists(r_dir):
                os.makedirs(r_dir)

            os.rename(o, r)
            print('renamed', o, '->', r)
