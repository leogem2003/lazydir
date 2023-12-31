import sys
import glob
import os

try:
    from lazydir import reader
except ImportError:
    sys.path.append("./")
    from lazydir import reader

DIR = "./test/test_files/read/"
FILES = [os.path.basename(file) for file in glob.glob(DIR+'*')] #["test1.txt", "test2.txt", "f1.docx", "f1.doc"]

def test_exact():
    assert set(reader.exact(FILES, "test1.txt")) == {"test1.txt"}

def test_contains():
    assert(set(reader.contains(FILES, "test"))) == {"test1.txt", "test2.txt"}

def test_extension_extact():
    assert set(reader.extension_exact(FILES, "txt")) == {"test1.txt", "test2.txt"}

def test_extension_contains():
    assert set(reader.extension_contains(FILES, "doc")) == {"f1.docx", "f1.doc"}

def test_starts_with():
    assert set(reader.starts_with(FILES, 't')) == {"test1.txt", "test2.txt"}

def test_ends_with():
    assert set(reader.ends_with(FILES, '1')) == {"test1.txt", "f1.docx", "f1.doc"}

def test_select_glob():
    assert set((os.path.basename(file) for file in reader.select_glob(DIR, "test*"))) == {"test1.txt", "test2.txt"}

def test_match():
    assert set(reader.match(FILES, r"test\d.*")) == {"test1.txt", "test2.txt"}

def test_search():
    assert set(reader.search(FILES, r"\d\.txt")) == {"test1.txt", "test2.txt"}
