import os
import re

from typing import Iterable, Iterator, Union

from .utils import get_file_datetime, get_basenames, datadict, filetuple, Attributes, DATE_COMPONENTS


def extract_name(files: Iterable[str]) -> Iterator[str]:
    """Add file's "basename" to grouping fields (extension ignored)

    Args:
        files (Iterable[str]): the list of files

    Yields:
        Iterator[str]: the list of basenames
    """

    return (os.path.basename(file).split(os.path.extsep)[0] for file in files)


def extract_ext(files: Iterable[str]) -> Iterator[str]:
    """Adds file's extension to gropuing fields (only last extension is selected)

    Args:
        files (Iterable[str]): the list of files

    Yields:
        Iterator[str]: the list of extensions
    """

    return (file.split(os.path.extsep)[-1] for file in files)


def extract_ctime(files: Iterable[str], sensibility: str = 'd') -> Iterator[str]:
    """Returns files creation time as timestamp. The number is truncated based on sensibility

    Args:
        files (Iterable[str]): the list of files
        sensibility (str, optional): the sensibility used for date evaluation accepted 's', 'm', 'h', 'd'. Defaults to 'd'.

    Yields:
        Iterator[str]: the list of ctimes
    """

    cut_index = DATE_COMPONENTS.index(sensibility)+3
    for file in files:
        cdate = get_file_datetime(file, 'ctime')
        date = '-'.join((str(n) for n in cdate.timetuple()[:cut_index]))
        yield str(date)


def extract_mtime(files: Iterable[str], sensibility: str = 'd') -> Iterator[str]:
    """Returns files creation time as timestamp. The number is truncated based on sensibility

    Args:
        files (Iterable[str]): the list of files
        sensibility (str, optional): the sensibility used for date evaluation accepted 's', 'm', 'h', 'd'. Defaults to 'd'.

    Yields:
        Iterator[str]: the list of ctimes
    """

    cut_index = DATE_COMPONENTS.index(sensibility)+3
    for file in files:
        cdate = get_file_datetime(file, 'mtime')
        date = '-'.join((str(n) for n in cdate.timetuple()[:cut_index]))
        yield str(date)


def extract_nth_letters(files: Iterable[str], start: int = 0, span: int = 1) -> Iterator[str]:
    """Extracts file's nth letters starting from index 0 and for a number of <span>.
    The defaults values are set to extract the first letter

    Args:
        files (Iterable[str]): the list of files
        start (int, optional): starting index for letter extraction. Defaults to 0.
        span (int, optional): the number of letters to extract from <start> index. Defaults to 1.

    Yields:
        Iterator[str]: the list of selected letters
    """
    return (os.path.basename(file)[start:start+span] for file in files)


def extract_last_letters(files: Iterable[str], span: int = 1) -> Iterator[str]:
    """Extracts file's <span> letters from the ending (extension excluded).
    The defaults values are set to extract the last letter

    Args:
        files (Iterable[str]): the list of files
        span (int, optional): the number of letters to extract. Defaults to 1.

    Yields:
        Iterator[str]: the list of selected letters
    """
    basenames = get_basenames(files, remove_extension=True)
    return (file[len(file)-span:] for file in basenames)


def extract_nth_words(files: Iterable[str], start: int = 0, span: int = 1) -> Iterator[str]:
    """Splits filenames using whitespaces and select a certain number <span> of
    words starting from <start> index. The defaults are set to select the first word
    The extension is excluded

    Args:
        files (Iterable[str]): the list of files
        start (int, optional): starting index used for selection. Defaults to 0.
        span (int, optional): the number of words to select. Defaults to 1.

    Yields:
        Iterator[str]: A list containing selected words rejoined using whitespaces
    """

    basenames = get_basenames(files, remove_extension=True)
    return (' '.join(file.split(' ')[start:start+span]) for file in basenames)


def extract_match(files: Iterable[str], expr: str, groups: bool = False, idx: int = 0) -> Iterator:
    """Returns the matched string obtained applying <expr> onf filenames.
    if no match is found an empty string is stored as result

    Args:
        files (Iterable[str]): the list of files
        expr (str): the expression used for matching
        group (bool): whether use groups. Defaults to False
        indx (int): group index eventually passed
        groups (bool): if true returns a tuple containing grouped matches

    Yields:
        Iterator: the result of the match
    """
    regexpr = re.compile(expr)
    bnames = get_basenames(files)
    for file in bnames:
        m = re.match(regexpr, file)
        if groups and m:
            y = m.groups()[idx]
        else:
            y = m.group() if m else ''
        yield y


def extract_search(files: Iterable[str], expr: str, group: bool = False, indx: int = 0) -> Iterator:
    """Returns the searched string obtained applying <expr> on filenames.
    if no match is found an empty string is stored as result.
    if <group> is true uses <indx> as group index for the extracted sequence.

    Args:
        files (Iterable[str]): the list of files
        expr (str): the expression used for matching
        group (bool): whether use groups. Defaults to False
        indx (int): group index eventually passed

    Yields:
        Iterator: the result of the match
    """
    regexpr = re.compile(expr)
    bnames = get_basenames(files)
    for file in bnames:
        m = re.search(regexpr, file)
        if group and m:
            y = m.groups()[indx]
        else:
            y = m.group() if m else ''
        yield y


def extract_position(files: Union[list[str], tuple[str]], start: int = 1, step: int = 1, reverse: bool = False) -> list[str]:
    """Extracts file's position counting them starting by <start> and incrementing by <step>
    If <reverse> is True, index assignement is made starting by the end of the list.

    Args:
        files (Iterable[str]): the list of files
        start (int, optional): Starting index. Defaults to 1.
        step (int, optional): increment. Defaults to 1.
        reverse (bool, optional): Reverses the index assignement. Defaults to False.

    Returns:
        list[str]: a list containing assigned indexes
    """
    indexes = list(range(start, len(files)*step+start, step))

    if reverse:
        indexes.reverse()

    return [str(i) for i in indexes]


def extract_group_index(files: Iterable[str], groups: dict[str, list[str]], start: int = 1, step: int = 1, reverse: bool = False) -> list[str]:
    """Extract the index of the group associated to each file

    Args:
        files (Iterable[str]): the list of file
        groups (dict[str, list[str]]): The dict containing file's groups
        start (int, optional): Starting index. Defaults to 0.
        step (int, optional): indexing incremental step. Defaults to 1.
        reverse (bool, optional): reverse the indexing. Defaults to False.

    Returns:
        list[str]: the list of extracted attributes
    """
    s_groups = sorted(groups)
    if reverse:
        s_groups.reverse()
    attributes = []
    for file in files:
        for group, index in zip(s_groups, range(start, len(groups)*step+start, step)):
            if file in group[1]:
                attributes.append(str(index))
                break

    return attributes


def extract_sub_index(files: Iterable[str], groups: dict[str, list[str]], start: int = 1, step: int = 1) -> list[str]:
    """Extract file's index relatively to the group it is included in

    Args:
        files (Iterable[str]): the list of files
        groups (dict[str, list[str]]): the dict containing groups
        start (int, optional): starting index. Defaults to 0.
        step (int, optional): indexing incremental step. Defaults to 1.

    Returns:
        list[str]: the list of selected attributes
    """
    attributes = []

    for file in files:
        for group in groups:
            if file in group[1]:
                attributes.append(str(group[1].index(file)*step+start))
                break

    return attributes


def infold_name(files: list[str], name: str) -> list[str]:
    """Infold each file in a new folder called <name>, placed inside the current parent folder

    Args:
        files (list[str]): the list of files to infold
        name (str): the name of the new folder

    Returns:
        list[str]: a list containing new filepaths
    """
    return [t[1]+'/'+name+'/'+t[2] for t in filetuple(files)]


def infold_template(files: list[str], attributes: Attributes, groups: dict[str, list[str]],
                    template: str, var_names: list[str], joinchar: str = ' ') -> list[str]:
    """generate a folder name where insert files based on groups. filenames used are from <files>

    Args:
        files (list[str]): the list of file to infold. Their names are the one used for renameing
        attributes (list[tuple[filename:str, list[attribute:str]]]): the list of attributes associated to each file
        groups (dict[str, list[str]]): the list of groups used fore define folder names
        template (str): a template string used for naming each folder. Group name is aviable as 'group'
        var_names (list[str]): names associated with variables used for templating
        joinchar (str, optional): Because <group> is splitted, this char is used to rejoin the string. Defaults to ' '.

    Returns:
        list[str]: a list of infolded and renamed files
    """
    new_folders = []
    for ((file, var), renamed) in zip(attributes, files):
        group_name = ''
        # generates folder name for each file using file's group
        for group in groups:
            if file in group[1]:
                group_name = joinchar.join(group[0].split('\\'))
                break

        # generates a dict containing
        #vars_dict = {name:val for name,val in zip(var_names, var)}
        vars_dict = datadict(var, var_names)
        vars_dict['group'] = group_name
        fold_name = template.format(**vars_dict)

        filename = os.path.basename(renamed)
        parent = os.path.dirname(renamed)
        new_folders.append(f'{parent}/{fold_name}/{filename}')

    return new_folders


def add_field(selections: Attributes, field: list[str]) -> Attributes:
    """Adds a field to a list of selected attributes for files grouping.
    The operation alters "selections" itself.

    Args:
        selections (list[tuple[filename:str,list[attribute:str]]]): the list of selected attributes for each file
        field (list[str]): the list containing the new field value for each file

    Returns:
        list[tuple[str,list[str]]]: the updated version of selected attributes: for each file, another column is added
        corresponding to the new field value
    """

    for file, new_attribute in zip(selections, field):
        file[1].append(new_attribute)

    return selections


def select_fields(selections: Attributes, indexes: Iterable[Union[int, range]]) -> Attributes:
    """Selects fields of specified index from a selection of attributes
    The operation doesn't alters "selections"

    Args:
        selections (list[tuple[filename:str,list[attribute:str]]]): the list of selected attributes for each file,
        Indexes (Iterable): a list containing indexes used for selection. You can pass single indexes as integers and
            slices as range objecs.

    Returns:
        list[tuple[str,list[str]]]: selected attributes. They have the same structure of the global attributes,
            but they contains only a subset of all the fields (the ones specified by <indexes>).
    """

    index_list = []

    for i in indexes:
        if isinstance(i, range):
            index_list += list(i)
            continue
        index_list.append(i)

    new_selections = []
    for file, attributes in selections:
        new_attributes = []
        for i in index_list:
            new_attributes.append(attributes[i])
        new_selections.append((file, new_attributes))

    return new_selections


def select_variables(selections: Attributes, global_variables: list[str], variables: list[str]) -> Attributes:
    """selects variables of given name

    Args:
        selections (Attributes): a list containing attributes' values for each file
        global_variables (list[str]): list containing the names of all defined variables. This is needed because the program
            needs to know the index of every variable in the variables table.
        variables (list[str]): list containing the names of the variables you want to select

    Returns:
        Attributes: selected variables
    """
    indexes = [global_variables.index(var) for var in variables]
    return select_fields(selections, indexes)


def update_field(selections: Attributes, global_variables: list[str], var_name: str, new_values: list[str]) -> Attributes:
    """Updates a field of specified name or index substituting it with a new values list

    Args:
        selections (Attributes): The list containing selections where perform the operations
        global_variables (list[str]): a list containing all varables' names used for indexing
        var_name (str): The name of the current variable
        new_values (list[str]): The values used for fields updating
    Returns:
        selections (Attributes): the updated attributes table
    """
    index = global_variables.index(var_name)
    for (file, attrs), value in zip(selections, new_values):
        attrs[index] = value

    return selections


def collapse_groups(selections: Attributes) -> tuple[str, list[str]]:
    """Collapses file's attributes into groups by listing together all files which share
    the same attributes list

    Args:
        selections (list[tuple[file:str,list[attribute:str]]]): the list of selected attributes

    Returns:
        dict_items[str,list[str]]: the dict containing the groups; the group name (variables joined by "\\") is used as key
    """
    # init the group by creating keys joined by '\\'
    make_hashable = lambda l: '\\'.join(l)
    tmp_groups = {make_hashable(selection[1]): list()
                  for selection in selections}

    for file, attributes in selections:
        tmp_groups[make_hashable(attributes)].append(file)

    return tmp_groups.items()
