import math
import os
from datetime import datetime
from typing import Iterable, Iterator, Union

DATE_COMPONENTS = ('d','h','m','s')
Attributes = list[tuple[str,list[str]]]

def get_file_metadata(file: str) -> dict[str, Union[int, float]]:
    """Get metadata (modify date, creation date, size) from files path

    Args:
        file(str): filepath

    Returns:
        dict(str,int): {'mtime':..., 'ctime':..., 'size':...}
    """
    return {
            'size': os.path.getsize(file),
            'ctime': os.path.getctime(file),
            'mtime': os.path.getmtime(file),
        }


def files_dict(files: Iterable[str]) -> dict[str, dict[str, Union[str, int]]]:
    """Generates a list of dicts containing files' basenames and metadata
        {'file_path': {'basename':..., 'size':..., 'mtime':..., 'ctime':...},...}

    Args:
        files (Iterable[str]): the list of files

    Returns:
        dict[str, dict[str, Union[str, int]]]: a dict containing file's data.
    """
    f_dict = {}

    for file in files:
        data = get_file_metadata(file)
        data.update({'basename':os.path.basename(file)})
        f_dict[file] = data

    return f_dict


def get_file_datetime(file:str, attribute:str = "ctime") -> datetime:
    """Convert string date into timestamp

    Args:
        date (str): formatted date
        attribute (str): the date attribute to read ('ctime' or 'mtime'). Default is 'ctime'

    Returns:
        datetime: the datetime corresponding this value
    """
    timestamp = get_file_metadata(file)[attribute]
    return datetime.fromtimestamp(timestamp)


def compare_dates(date1:datetime, date2:datetime, precision:str = 'd') -> int:
    """Compares two dates, with the given precision

    Args:
        date1 (datetime): first date
        date2 (datetime): second date
        sensibility (str): the sensibility used for date comparison ('s','m','h','d'), default is 'd'

    Returns:
        int: 0 if dates are equal, 1 if date1 > date2, -1 if date1 < date2
    """
    cut_index = DATE_COMPONENTS.index(precision)+3
    timetuple1 = datetime(*date1.timetuple()[:cut_index])
    timetuple2 = datetime(*date2.timetuple()[:cut_index])

    if timetuple1 > timetuple2:
        return 1
    elif timetuple1 < timetuple2:
        return -1
    return 0


def parse_file_size(size:int, base:int = 1024, units:list[str] = ['','K','M','G','T'], suffix:str = 'B') -> str:
    """Convert numeric filesize to human readable string

    Args:
        size (int): file size in bytes
        base (int, optional): The magnitude of the units. Defaults to 1024.

    Returns:
        str: file size in a human-readable format
    """
    #get file size magnitude
    magnitude = math.floor(math.log(size, base))

    try:
        unit = units[magnitude]
    except IndexError: #size exceeds 1024T
        magnitude = len(units)-1
        unit = units[-1]

    value = size / (base**magnitude)

    #rounded value exceeds 1024
    if round(value) >= 1024 and magnitude != len(units)-1:
        value = 1
        unit = units[magnitude+1]

    return f'{round(value)}{unit}{suffix}'
    

def get_basenames(files: Iterable[str], remove_extension:bool = False) -> list[str]:
    """Gets file's basenames without parent directory

    Args:
        files (Iterable[str]): the list of files
        remove_extension (bool, optional): whether remove the extension from the basename. Defaults to False.

    Returns:
        list[str]: the list of basenames
    """
    if remove_extension:
        return [os.path.basename(file).split(os.path.extsep)[0] for file in files]
    
    return [os.path.basename(file) for file in files]


def filetuple(files: Iterable[str]) -> Iterator[tuple[str,str,str,str,str]]:
    """Splits file path into directory, basename, name without extension and extension

    Args:
        files (Iterable[str]): the list of files

    Yields:
        Iterator[tuple[str]]: A tuple containing full file path, directory, basename, name without extension and extension (if any)
    """

    for file in files:
        basename = os.path.basename(file)

        if basename.startswith('.'):
            name = ''
            ext = basename
        elif not '.' in basename:
            name = basename
            ext = ''
        else:
            name, ext = basename.split('.', maxsplit=1)

        yield (file, os.path.dirname(file), basename, name, ext)

def compose_filepath(dirname: str, filename: str, extension: str, sep:str = '/') -> str:
    """Composes a file path as dirname/filename.ext

    Args:
        dirname (str). Parent directory. No final backslash needed
        filename (str). File name without extension and parent directory
        extension (str). File's extension without the initial dot. If the file
            hasn't an extension, pass a value that evalued as a boolean returns false
        sep (str). Separator used for joining dir and filename. Defaults to '/'
    Returns:
        str: file path
    """

    return f'{dirname}{sep if dirname else ""}{filename}{"." + extension if extension else ""}'

def datadict(vars:list[str], var_names:list[str]) -> dict[str, str]:
    """Gets a row of data and associated column names and returns
    a dict which has column names as keys and data as values.
    If a name is None, a progressive index is used and the key
    will be 'data_<n>'.

    Args:
        vars (list[str]): a list containing the data
        var_names (list[str]): a list containing column names, it must be the same length of vars

    Returns:
        dict[str, str]: the dict with name and data associated
    """
    data_names = {}
    data_indx = 0
    for data, name in zip(vars, var_names):
        if name:
            data_names[name] = data
        else:
            data_names['data_'+str(data_indx)] = data
            data_indx += 1
    
    return data_names

def cut(msg, verbosity: int, limits: list[int] = [200, -1]) -> str:
    """Cuts <msg> at a certain index depending on verbosity and limits

    Args:
        msg (Any): The message to display. It must support __str__
        verbosity (int): The level of verbosity
        limits (list[int], optional): The list of indexes corresponding to each verbosity
        In facts, verbosity is used as index to access to the corresponding element in limits. Defaults to [200, -1].

    Returns:
        str: Cut string
    """
    string = str(msg)
    cut_index = limits[verbosity-1] if verbosity<=len(limits) else limits[-1]
    if cut_index != -1 and cut_index<len(string):
        string = string[:cut_index]
        string+=' (...)'

    return string    
