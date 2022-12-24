import sys
import glob
import os

try:
    from fileconsole import writer, group
except ImportError:
    sys.path.append("./")

DIR = "./test/test_files/rename/"
FILES = [os.path.basename(file) for file in glob.glob(DIR+'*')] #["Abc.txt", "File 01.txt", "Multiple Words.txt"]

def test_replace():
    assert set(writer.replace(FILES, 'A', 'a')) == {"abc.txt", "File 01.txt", "Multiple Words.txt"}

def test_sub():
    assert set(writer.sub(FILES, 'A', 'a')) == {"abc.txt", "File 01.txt", "Multiple Words.txt"}

def test_capitalize():
    assert set(writer.capitalize(FILES, prev_char="Z")) == {"Abc.txt", "File 01.txt", "Multiple Words.txt"}

def test_upper():
    assert set(writer.upper(FILES)) == {"ABC.txt", "FILE 01.txt", "MULTIPLE WORDS.txt"}

def test_lower():
    assert set(writer.lower(FILES)) == {"abc.txt", "file 01.txt", "multiple words.txt"}

def test_format():
    assert set(writer.rename_format(FILES, [], [], "{basename}_templ.{extension}")) == {"Abc_templ.txt", "File 01_templ.txt", "Multiple Words_templ.txt"}