from typing import Callable

from . import reader, sorter, group, writer, utils
import click
__version__ = '1.1.1'
"""
How lazydir's cli works:
the CLI is based on a series of commands which are separated into main actions,
which are select, sort, extract, group and write.
The command corresponding to each action tells the program how interpretate
the results obtained from each commands.

<action> -> 'action' string returned
<command> -> 'command' function generated
...

result pipeline:
'action string' -> action toggled and <action_func> will be used
<action_func>(command_func) -> data
...
"""

@click.group(chain=True)
@click.option('-v', '--verbose', count=True)
@click.version_option(__version__, message="lazydir v%(version)s")
@click.pass_context
def cli(ctx, verbose):
    """
    lazydir 1.1.1 \b
    A tool for operating on files. See the help message of
    <select>, <extract>, <sort>, <group>, <rename> and <infold> commands for
    more informations.
    """
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj['fields'] = []
    ctx.obj['vars'] = []
    ctx.obj['renamed'] = []
    ctx.obj['verbosity'] = verbose
    return None


##### operation commands ####

@cli.command('select')
@click.option('--dir', '-d', default="./", show_default=True, help="specify the directory used for the extraction")
@click.pass_context
def cli_select(ctx, dir):
    """
    Toggles selection mode on.
    Selection mode is used to select only desired files from
    a specific directory. It can be performed only once
    before every other command. Each selection method operates
    on every file and then the result is intersected by default.
    To change this behaviour, you can use 'and', 'or', 'not' and 'xor'
    commands. These expressions will be evalued from left to right and,
    after an operator is used, every other expression will have this logic
    operator by default until a new operator is inserted.

    \b
    ACCEPTED COMMANDS:
        exact
        contains
        created-before
        created-after
        created-equal
        modified-before
        modified-after
        modified-equal
        extension-contains
        endswith
        startswith
        glob
        match
        search
    LOGIC CONNECTORS:
        and
        or
        xor
        not
    """
    dir += '/'
    ctx.ensure_object(dict)

    ctx.obj['files'] = list(reader.select_glob(dir,'*'))
    ctx.obj['pool'] = set(ctx.obj['files'])
    ctx.obj['groups'] = []
    ctx.obj['logic-mode'] = 'and'
    ctx.obj['dir'] = dir

    return 'select'


@cli.command('sort')
@click.pass_context
def cli_sort(ctx):
    """
    Sort selected files.
    It uses file's extracted data, so it will works only
    after some data has been generated with the extraction command.
    It is followed only by the 'by' command wich anables you to
    specify the fields used for extraction.

    \b
    ACCEPTED COMMANDS:
        by
    """
    return 'sort'


@cli.command('extract')
@click.pass_context
def cli_extract(ctx):
    """
    Extract file's data.
    For each file, it extract a certain parameter that will be sored in a record
    associated to its name. You can perform extraction several times after any command:
    the data will be updated. You can specify a variable name for each field which
    can be used to refer to this specific field in other operations. If no name is assiciated
    the field can be accessed via its absolute index in the data table

    \b
    ACCEPTED COMMANDS:
        name
        extension
        ctime
        mtime
        nth-letter
        first-letter
        last-letter
        words
        matching
        searching
        positioin
        group-index
        sub-index
    """
    return 'extract'


@cli.command('group')
@click.pass_context
def cli_group(ctx):
    """
    Groups files using a certain set of attributes.
    By the command "using", you can specify a set of attributes that will be used for grouping.
    All the files that share the same attributes values will be grouped together.
    Grouping can be used to extract group-specific data like group index and groups internal indexes.\n
    
    \b
    ACCEPTED COMMANDS:
        using
    """
    return 'group'

@cli.command('rename')
@click.pass_context
def cli_rename(ctx):
    """
    Rename files.
    There are two main operations: the modification of file's existing name (e.g selecting/deleting a part of it)
    or the composition with other files attributes extracted with the "extract" command.
    These attributes can be used in the "template" subcommand.

    \b
    ACCEPTED COMMANDS:
        replace
        sub
        capitalise
        upper
        lower
        format
    """
    ctx.obj['renamed'] = []
    return 'rename'

@cli.command('infold')
@click.pass_context
def cli_infold(ctx):
    """
    Creates new folders for selected files.
    For performing infolding, the <extract> command is needed to be performed
    before. It is based on three commands: folder-name which infold every file in a folder of given name
    folder-template which creates a new folder based on a template string,
    and <apply> which appplies these modifications.

    \b
    ACCEPTED COMMANDS
        folder-name
        folder-template
        apply
    """
    return 'infold'

### operations functions ###
def selection(ctx, function: Callable) -> None:
    mode = ctx.obj['logic-mode']
    ## now selected-files is a dict
    pool = ctx.obj['pool']
    
    if mode == "and":
        ctx.obj['pool'] = pool & set(function())
    elif mode == "or":
        ctx.obj['pool'] = pool | set(function())
    elif mode == 'xor':
        ctx.obj['pool'] = pool ^ set(function())
    else: # mode == 'not'
        ctx.obj['pool'] = pool - set(function())

    if ctx.obj['verbosity']>1:
        print("\nSELECTION:\n", ctx.obj['pool'])


def sorting(ctx, function: Callable) -> None:
    ctx.obj['files'] = function()

    if ctx.obj['verbosity']>1:
        print('\nSORTING:\n',  ctx.obj['files'] ,flush=True)


def extraction(ctx, name_function: tuple[str, Callable]) -> None:
    if not ctx.obj['fields']:
        ctx.obj['fields'] = [(file,[]) for file in ctx.obj['files']]

    name, func = name_function
    ctx.obj['vars'].append(name)
    ctx.obj['fields'] = group.add_field(ctx.obj['fields'], func())

    if ctx.obj['verbosity']>1:
        #print('\nEXTRACTION:\n', ctx.obj['fields'], ctx.obj['vars'])
        print('\nEXTRACTION\n', utils.cut(ctx.obj['fields'], ctx.obj['verbosity']))


def grouping(ctx, function: Callable) -> None:
    ctx.obj['groups'] = group.collapse_groups(function())

    if ctx.obj['verbosity']>1:
        print('\nGROUPING:\n', ctx.obj['groups'])


def renaming(ctx, function: Callable) -> None:
    if not ctx.obj['renamed']:
        ctx.obj['renamed'] = ctx.obj['files'].copy()
    ctx.obj['renamed'] = function()

    if ctx.obj['verbosity']>1:
        print('\nRENAMING:\n', ctx.obj['renamed'])


def infolding(ctx, function: Callable) -> None:
    if not ctx.obj['renamed']:
        ctx.obj['renamed'] = ctx.obj['files'].copy()
    
    if not ctx.obj['groups']:
        ctx.obj['groups'] = [('', ctx.obj['files']),]

    ctx.obj['renamed'] = function()
    if ctx.obj['verbosity']>1:
        print('\nINFOLDING\n', ctx.obj['renamed'])


OPERATIONS = {
    'select':selection,
    'sort':sorting,
    'extract':extraction,
    'group':grouping,
    'rename':renaming,
    'infold':infolding,
}

### result pipeline ###

@cli.result_callback()
@click.pass_context
def cli_process_pipeline(ctx, filters, verbose):
    verbosity = verbose
    if(verbosity>1):
        print('Initial files:', ctx.obj['files'],flush=True)
        print('Filters:', filters, flush=True)

    for f in filters:
        if isinstance(f, str):
            #a logic connector or an operation has been passed as argument
            if f in OPERATIONS.keys():
                if f != 'select': # after selection, gets the list of selected files
                    ctx.obj['files'] = list(ctx.obj['pool'])
                ctx.obj['operation'] = OPERATIONS[f]
                message = "operation: "+f
            else:
                ctx.obj['logic-mode'] = f
                message = "logic mode: "+f
            
            if verbosity>1:
                print('\n'+message)
        else:
            ctx.obj['operation'](ctx, f)
    
    if(verbosity):
        print("\nSELECTED:", utils.cut(ctx.obj['files'], verbosity), "\nFILE VARS:", utils.cut(ctx.obj['fields'], verbosity), "\nVAR NAMES:", utils.cut(ctx.obj['vars'], verbosity),
              "\nGROUPS:", utils.cut(ctx.obj['groups'], verbosity), "\nRENAMED FILES:", utils.cut(ctx.obj['renamed'], verbosity), sep='\n')



### logic connectors ###

@cli.command('and')
def cli_and():
    return 'and'

@cli.command('or')
def cli_or():
    return 'or'

@cli.command('xor')
def cli_xor():
    return 'xor'

@cli.command('not')
def cli_not():
    return 'not'


### selection commands ###    
    
@cli.command('exact')
@click.argument('word')
@click.pass_context
def cli_exact(ctx, word):
    """Selects files which names are exactly the <word> string, extension included"""
    return lambda: reader.exact(ctx.obj['files'], word)

@cli.command('contains')
@click.argument('word')
@click.pass_context
def cli_contains(ctx, word):
    """Selects the files which names contains the <word> string, extension included"""
    return lambda: reader.contains(ctx.obj['files'], word)

@cli.command('created-before')
@click.argument('date')
@click.option('--date-format', default="%d/%m/%Y", show_default=True)
@click.option('--sensibility', default="d", show_default=True, help="The minimun time unit used for comparison ('s', 'min', 'h', 'd')")
@click.pass_context
def cli_created_before(ctx, date, date_format, sensibility):
    """Selects the files that have been created before a certain date."""
    return lambda: reader.created_before(ctx.obj['files'], date, date_format=date_format, sensibility=sensibility)

@cli.command('created-after')
@click.argument('date')
@click.option('--date-format', default="%d/%m/%Y", show_default=True)
@click.option('--sensibility', default="d", show_default=True, help="The minimun time unit used for comparison ('s', 'min', 'h', 'd')")
@click.pass_context
def cli_created_after(ctx, date, date_format, sensibility):
    """Selects files that have been created after a certain date"""
    return lambda: reader.created_after(ctx.obj['files'], date, date_format=date_format, sensibility=sensibility)

@cli.command('modified-before')
@click.argument('date')
@click.option('--date-format', default="%d/%m/%Y", show_default=True)
@click.option('--sensibility', default="d", show_default=True, help="The minimun time unit used for comparison ('s', 'min', 'h', 'd')")
@click.pass_context
def cli_modified_before(ctx, date, date_format, sensibility):
    """Selects files that have been modified before a certain date"""
    return lambda: reader.modified_before(ctx.obj['files'], date, date_format=date_format, sensibility=sensibility)


@cli.command('modified-after')
@click.argument('date')
@click.option('--date-format', default="%d/%m/%Y", show_default=True)
@click.option('--sensibility', default="d", show_default=True, help="The minimun time unit used for comparison ('s', 'min', 'h', 'd')")
@click.pass_context
def cli_modified_after(ctx, date, date_format, sensibility):
    """Selects files modified after a certain date"""
    return lambda: reader.modified_after(ctx.obj['files'], date, date_format=date_format, sensibility=sensibility)

@cli.command('created-equal')
@click.argument('date')
@click.option('--date-format', default="%d/%m/%Y", show_default=True)
@click.option('--sensibility', default="d", show_default=True, help="The minimun time unit used for comparison ('s', 'min', 'h', 'd')")
@click.pass_context
def cli_created_equal(ctx, date, date_format, sensibility):
    """Selects the files created exactly in a certain date"""
    return lambda: reader.created_equal(ctx.obj['files'], date, date_format=date_format, sensibility=sensibility)

@cli.command('modified-equal')
@click.argument('date')
@click.option('--date-format', default="%d/%m/%Y", show_default=True)
@click.option('--sensibility', default="d", show_default=True, help="The minimun time unit used for comparison ('s', 'min', 'h', 'd')")
@click.pass_context
def cli_modified_equal(ctx, date, date_format, sensibility):
    """Selects the files modified exactly in a certain date"""
    return lambda: reader.modified_equal(ctx.obj['files'], date, date_format=date_format, sensibility=sensibility)

@cli.command('extension-exact')
@click.argument('word')
@click.pass_context
def cli_extension_exact(ctx, word):
    """Selects files which extension is equal to the <word> string"""
    return lambda: reader.extension_exact(ctx.obj['files'], word)

@cli.command('extension-contains')
@click.argument('word')
@click.pass_context
def cli_extension_contains(ctx, word):
    """Selects the files which extension contains the <word> string"""
    return lambda: reader.extension_contains(ctx.obj['files'], word)

@cli.command('endswith')
@click.argument('word')
@click.pass_context
def cli_ends_with(ctx, word):
    """Select the files which filename (extension excluded) ends with the <word> string"""
    return lambda: reader.ends_with(ctx.obj['files'], word)

@cli.command('startswith')
@click.argument('word')
@click.pass_context
def cli_starts_with(ctx, word):
    """Select the files which filename starts with the <word> string"""
    return lambda: reader.starts_with(ctx.obj['files'], word)

@cli.command('glob')
@click.argument('expr')
@click.pass_context
def cli_glob(ctx, expr):
    """Select the files which name (extension included) matches the <expr> expression using the "glob" function"""
    return lambda: reader.select_glob(ctx.obj['files'], expr)

@cli.command('match')
@click.argument('expr')
@click.pass_context
def cli_match(ctx, expr):
    """Select the files which name (extension included) matches the <expr> expression using the "re.match" function"""
    return lambda: reader.match(ctx.obj['files'], expr)

@cli.command('search')
@click.argument('expr')
@click.pass_context
def cli_find(ctx, expr):
    """Select the files which name (extension included) matches the <expr> expression using the "re.search" function"""
    return lambda: reader.search(ctx.obj['files'], expr)

### sorting commands ###

@cli.command('by')
@click.option('--all', '-a', is_flag=True, default=False, show_default=True, help="use all the aviable variables")
@click.option('--slice', nargs=2, multiple=True, type=int, help="use all variables from <a> to <b> indexes excluded")
@click.option('--index', '-i', multiple=True, type=int, help="use a variable at a specific index")
@click.option('--var', '-v', multiple=True, help="use a variable with <var> name")
@click.option('--reverse', '-r', is_flag=True, default=False, help="reverse the sorting")
@click.pass_context
def cli_by(ctx, all, var, slice, index, reverse):
    """
    Sorts files using extracted variables. The relevance of a variable in the sorting process depends on the
    order in which they appear in this command.
    If --all is used, the other options will not be evalued.
    If --var is used, the --slice and --index options will not be evalued.
    The indexes start from 0 and are referred to the extracted fields in order of extraction.
    For the --slice option, the second index is included (--slice 0 3 -> range(0,4))
    You can pass multiple --var or --slice and --index per time.
    """
    indexes = []
    if all:
        return lambda: sorter.sorter(group.select_fields(ctx.obj['fields'], range(0,len(ctx.obj['fields'][0][1]))), reverse)
    elif var:
        return lambda: sorter.sorter(group.select_variables(ctx.obj['fields'], ctx.obj['vars'], var ), reverse)
    else:
        for s in slice:
            indexes.append(range(s[0], s[1]+1))
        
        for i in index:
            indexes.append(i)
        return lambda: sorter.sorter(group.select_fields(ctx.obj['fields'], indexes), reverse)

### extraction commands ###
@cli.command('name')
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_name(ctx, var):
    """Extract filename (extension excluded)"""
    return (var, lambda: group.extract_name(ctx.obj['files']))

@cli.command('extension')
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_extension(ctx, var):
    """Extract extension"""
    return (var, lambda: group.extract_ext(ctx.obj['files']))

@cli.command('ctime')
@click.option('--sensibility', default='d', show_default=True, help="The minimun time unit used for extraction ('s', 'min', 'h', 'd')")
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_ctime(ctx, sensibility, var):
    """Extract file's creation date"""
    return (var, lambda: group.extract_ctime(ctx.obj['files'], sensibility))

@cli.command('mtime')
@click.option('--sensibility', default='d', show_default=True, help="The minimun time unit used for extraction ('s', 'min', 'h', 'd')")
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_mtime(ctx, sensibility, var):
    """Extract file's last modification date"""
    return (var, lambda: group.extract_mtime(ctx.obj['files'], sensibility))

@cli.command('nth-letter')
@click.argument('start', type=int)
@click.option('--span', type=int, default=1, show_default=True, help="the number of letters to extract. If more than string's length, returns the string up to the end")
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_nth_letter(ctx, start, span, var):
    """Extract file's letters starting from <start> index for a number of <span> letters. The extension can be included"""
    return (var, lambda: group.extract_nth_letters(ctx.obj['files'], start, span))

@cli.command('first-letter')
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_first_letter(ctx, var):
    """Extract file's first letter (extension exclude)"""
    return (var, lambda: group.extract_nth_letters(ctx.obj['files']))

@cli.command('last-letter')
@click.option('--span', default=1, show_default=True, type=int)
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_last_letter(ctx, span, var):
    """Extract file's last letter"""
    return (var, lambda: group.extract_last_letters(ctx.obj['files'], span))

@cli.command('words')
@click.argument('start', type=int)
@click.option('--span', default=1, show_default=True, help="number of words to extract; if exceeds, selects words up to the end")
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_words(ctx, var, start, span):
    """Extract file's words (a sequence of characters without spaces) from the word number <index> for <span> words (extension excluded)"""
    return (var, lambda: group.extract_nth_words(ctx.obj['files'], start, span))

@cli.command('matching')
@click.argument('expr')
@click.option('--gindx','-g', default=False, type=int, help="group index")
@click.option('--use_groups', '-u', default=False, is_flag=True, show_default=True, help="Flag to allow group indexes")
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_match(ctx, expr, gindx, use_groups, var):
    """Extract matched sequence using "re.match". File's extension is included"""
    return (var, lambda: group.extract_match(ctx.obj['files'], expr, use_groups, gindx)
)

@cli.command('searching')
@click.argument('expr')
@click.option('--gindx', '-g', default=False, type=int, help="group index")
@click.option('--use_groups', '-u', default=False, is_flag=True, show_default=True, help="Flag to allow group indexes")
@click.option('--var', '-v', default='')
@click.pass_context
def cli_extract_search(ctx, expr, gindx, use_groups, var):
    """Extract matched sequence using "re.search". File's extension is included"""
    return (var, lambda: group.extract_search(ctx.obj['files'], expr, use_groups, gindx)
)

@cli.command('position')
@click.option('--reverse','-r', is_flag=True, default=False, show_default=True, help="reverse file's ordering")
@click.option('--start', default=1, show_default=True, type=int, help="starting index")
@click.option('--step', default=1, show_default=True, type=int, help="the inctremental step used in indexing")
@click.option('--var', '-v', default='')
@click.pass_context
def cli_position(ctx, reverse, start, step, var):
    """Extract file's position based on the current ordering. A following "sort" command won't change that numeration"""
    return (var, lambda: group.extract_position(ctx.obj['files'], start, step, reverse))

@cli.command('group-index')
@click.option('--var', '-v', default='')
@click.option('--start', default=1, show_default=True, help="reverse file's ordering")
@click.option('--step', default=1, show_default=True, help="starting index")
@click.option('--reverse','-r', default=False, is_flag=True, help="the inctremental step used in indexing")
@click.pass_context
def cli_group_index(ctx, var, start, step, reverse):
    """Associate to each group a position and assign that value to each file included in that group"""
    return (var, lambda: group.extract_group_index(ctx.obj['files'], ctx.obj['groups'], start, step, reverse))

@cli.command('sub-index')
@click.option('--var', '-v', default='')
@click.option('--start', default=1, show_default=True, help="starting index")
@click.option('--step', default=1, show_default=True, help="the inctremental step used in indexing")
@click.pass_context
def cli_subindex(ctx, var, start, step):
    """Extract file's position relatively to the group it is included in"""
    return (var, lambda: group.extract_sub_index(ctx.obj['files'], ctx.obj['groups'], start, step))

### groups ###
@cli.command('using')
@click.option('--all', '-a', is_flag=True, default=False, show_default=True, help="use all aviable attributes for grouping")
@click.option('--slice', nargs=2, multiple=True, type=int, help="specify a range index of attributes")
@click.option('--index', multiple=True, type=int, help="specify the index of a specific attribute")
@click.option('--var', '-v', multiple=True, help="specify variable's name")
@click.pass_context
def cli_using(ctx, all, var, slice, index):
    """
    Groups files using a certain set of attributes. If --all is passed, all others options are ignored.
    Else if --var is used, there can be passed variables only using --var.
    """
    indexes = []
    if all:
        return lambda: group.select_fields(ctx.obj['fields'],
            range(0,len(ctx.obj['fields'][0][1])))
    elif var:
        return lambda: group.select_variables(ctx.obj['fields'], ctx.obj['vars'], var)

    for s in slice:
        indexes.append(range(*s))
    
    for i in index:
        indexes.append(i)

    return lambda: group.select_fields(ctx.obj['fields'], indexes)


### renaming ###
@cli.command('replace')
@click.argument('char_to_repl')
@click.option('--replacement','-r', default="", show_default=True, help="the character used for replacement")
@click.option('--count', '-c', default=-1, show_default=True, help="the maximum number of replacements to perform (0 to replace all)")
@click.option('--space', '-s', is_flag=True, default=False, show_default=True, help="selects space character as filling char")
@click.pass_context
def cli_replace(ctx, char_to_repl, replacement, count, space):
    """Replace a certain string from filename (extension excluded) with <replacement> for a maximum of <count> times"""
    if space:
        replacement = ' '
    return lambda: writer.replace(ctx.obj['renamed'], char_to_repl, replacement, count)

@cli.command('sub')
@click.argument('expr')
@click.option('--replacement', '-r', default="", show_default=True, help="the character used for replacement")
@click.option('--count', default=0, show_default=True, help="the maximum number of replacements to perform (0 to replace all)")
@click.pass_context
def cli_sub(ctx, expr, replacement, count):
    """Replace a certain string from filename (extension excluded) with <replacement> for a maximum of <count> times using "re.sub"."""
    return lambda: writer.sub(ctx.obj['renamed'], expr, replacement, count)

@cli.command('capitalise')
@click.option('--char', default=' ', show_default=True, help="the character after which there will be a capitalisation")
@click.option('--not-capitalise-start', '-n', is_flag=True, default=True, help="not capitalise the first letter of the filename")
@click.option('--count', default=-1, show_default=True, help="maximum nnumber of capitalisation (-1 to capitalise all)")
@click.pass_context
def cli_capitalise(ctx, char, not_capitalise_start, count):
    """Capitalise filenames"""
    return lambda: writer.capitalize(ctx.obj['renamed'], char, count, not_capitalise_start)

@cli.command('upper')
@click.pass_context
def cli_upper(ctx):
    """Makes all the letters in uppercase"""
    return lambda: writer.upper(ctx.obj['renamed'])

@cli.command('lower')
@click.pass_context
def cli_lower(ctx):
    """Makes all the letter in lowercase"""
    return lambda: writer.lower(ctx.obj['renamed'])


@cli.command('format')
@click.argument('template')
@click.pass_context
def cli_format(ctx, template):
    """
    Renames a file using a format string as template.
    You must refer to an extracted data using his --var attribute or
    by its authomatic variable name which is assigned in the following way:
    data_<n> where n is a number. The first unnamed variable will be
    'data_0', the last nth unnamed variable will be 'data_(n-1)'.
    File's basename, extension and filename (basename.extension)
    are aviable respectively as 'basename', 'extension' and 'filename'.
    This is the only rename command which can affect file's extension
    """
    return lambda: writer.rename_format(ctx.obj['renamed'], ctx.obj['fields'], ctx.obj['vars'], template)


### infolding ###

@cli.command('folder-name')
@click.argument('name')
@click.pass_context
def cli_infold_name(ctx, name):
    """Infold every file into a folder called <name> and inserted into the current parent folder"""
    return lambda: group.infold_name(ctx.obj['renamed'], name)

@cli.command('folder-template')
@click.argument('template')
@click.option('--joinchar', default=' ', show_default=True, help="the character used to join group fields")
@click.pass_context
def cli_infold_template(ctx, template, joinchar):
    """
    Associate to each file a folder which name is constructed basing on a string template.
    File's group can be accessed through the "group" variable and other file's variables are aviable via their names.
    """
    return lambda: group.infold_template(ctx.obj['renamed'], ctx.obj['fields'],  ctx.obj['groups'], template, ctx.obj['vars'], joinchar)


@cli.command('apply')
@click.pass_context
def cli_apply(ctx):
    """Rename and infold selected files"""
    return lambda: writer.rewrite(ctx.obj['files'], ctx.obj['renamed'])

if __name__ == "__main__":
    cli(obj={})
