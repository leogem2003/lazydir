# lazydir v1.1.0

## What is lazydir?

lazydir is a CLI program  designed to perform authomatic operations on your files.

## How it works

lazydir is based on six main commands which are "select", "extract", "sort", "group", "rename" and "infold" and their subcommands.
Each stage of file's processing is subdivided into these commands: file's selections, info extraction, sorting, grouping, renaming and infolding. Whilst selection must be performed only once before every other command, all the remaining commands can be performed several times.
It can work only on a single directory.

## select
The `select` command is used to select files from a specified directory. For instance, `lazydir select --dir "./dir/subdir/"` will select all the files contained in "./dir/subdir". In fact, by default the select command loads all files into the directory, and its subcommands are used to restrict file's selection.
By default, the result of every subcommand is intersecated with the others, so the selected files will be the ones that will satisfy all specified conditions. This behaviour can be modified with the usage of logic connectors: after one of these is inserted, all the following subcommands will be interpreted through this new connector. The aviable connectors are *and*, *or*, *not*, *xor*, and there can be more than one connector in a single expression.
For instance, `lazydir select contains 'a' contains 'b' or contains 'c' not contains 'd'` will select the files that contains in their name both 'a' and 'b' in their name or contains the letter 'c' and don't contains the letter 'd'. The corresponding expression would be like (('a' && 'b') || 'c') && !'d'). Logic expressions are evalued from left to right without the possibility os specifying thifferent orders of evaluation.

## extract
The `extract` command can extract some informations about selected files. Each extracted field represents a column in a kind of table in which extracted informations are associated to each file. Every column can be given a name through the *--var* option aviable in each subcommand.
For instance `lazydir select extract name --var "filename"` will extract the filename of each file naming that specific field "filename". Field names are useful for referring to those fields in other commands. See *sort*, *group*, *rename* and *infold* for more informations about accessing to extracted data. The *extract* command can be performed several times and it will add the new data to the previous one non-destructively.

## sort
The `sort` command is used to define an ordering for selected files. By default, all the files are loaded through `glob.glob("*")` and saved in the exact order the glob function returns them. You can sort files only using extracted fields. You can specify more than one field used for sorting and they will be evalued in the order they appear in the command.
For instance, `lazydir select extract ctime -v "ctime" name -v "name" sort by -v "ctime" -v "name"` will first extract the creation date and the name of each file and then use them for sortinf. All the files will be sorted by they ctime first and then by their name. In the case a fields is unnamed, you can access it through its absolute index in the field table, the previous command would then become: `lazydir select extract ctime name sort by -i 0 -i 1` or `lazydir select extract ctime name sort by --slice 0 1`. To pass all extracted values in the order of extraction, you can use the `--all` option. Sorting can be performed several times and every of them will modify the previous ordering.

## group
The `group` command is used to group files based on a certain pool of properties. It is based on the extracted values. You can perform grouping more than once and each time the new groups will overwrite the previous ones. Groups comes in handy for infolding and indexing. You can extract group-specific attributes like *group-index* and *subindex*.
Group uses the *using* subcommand to specify grouping fields, following the same rules as specified in the *sort by* command.
For instance, `lazydir select extract ctime -v "ctime" group using -v "ctime"` will group together all the files created the same day.

## rename
The `rename` command is able to change files names. It can performs operations on the file name such as *replace* or *capitalise* or insert other informations using extracted fields through the *format* subcommand, which can also access to a certain set of pre-selected attributes. You can't change file's path through the *rename* command.
For instance, `lazydir select extract ctime -v "ctime" sort by -v "ctime" extract position -v "pos" rename format "{pos}-{filename}"`, will sort all the files by their creation time, then assign them an index based on this sorting and rename them using this position and their previous name.

## infold
The `infold` command can change file's path but only creating subfolders of the current folder. It is based on two subcommands: *folder-name* which puts all selected files in a folder of given name and *folder-template* that enables to compose the folder using extracted values in a format string. Because folders usually coencide with groups, the group name, joined with a specified character, is aviable through the {group} variable. Several folders can be applied various times and they will result in new subdirectories of the latest created.
For instance, `lazydir select infold folder-name 'A', folder-name 'B' extract first-letter -v "fl" infold folder-template "letter {fl}"` will put all selected files in the directories ./A/B/ and then create a folder named with their first letter (all files sharing the same first letter will be put in the same folder). The final structure will be then ./A/B/letter {fl}/.
To make changes effective, infold has also the *apply* subcommand which applies all the changes _removing_ previous files.
It is suggested to keep a backup of the original files in the case of bugs that may lead to the loss of your data.

## installation
To install, from this directory, run `pip install ../lazydir`. Then lazydir will be aviable through the command *lazydir*.

## Changelog
### v1.1.0
- Added grouping feature in exctraction regexp operations
