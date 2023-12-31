import sys
import glob
import os

try:
    from lazydir import group
except ImportError:
    sys.path.append("./")
    from lazydir import group

DIR = "./test/test_files/extract/"
FILES = sorted((os.path.basename(file) for file in glob.glob(DIR+'*'))) #["f1.txt", "f2.txt", "f1.docx", "Multiple words.txt"]

def test_name():
    expected_res = ('f1', 'f2', 'f1', 'Multiple words')
    assert sorted((group.extract_name(FILES))) == sorted(expected_res)

def test_ext():
    expected_res = ('docx', 'txt', 'txt', 'txt')
    assert sorted(group.extract_ext(FILES)) == sorted(expected_res)

def test_nth_letters():
    expected_res = ('1.docx', '1.txt', '2.txt', 'ultipl')
    assert sorted(group.extract_nth_letters(FILES, 1, 6)) == sorted(expected_res)

def test_last_letters():
    expected_res = ('f1', 'f1', 'f2', 'ds')
    assert sorted(group.extract_last_letters(FILES, 2)) == sorted(expected_res)

def test_match():
    expected_res = ('f1', 'f1', 'f2', '')
    assert sorted(group.extract_match(FILES, r'f\d')) == sorted(expected_res)

def test_search():
    expected_res = ('1', '1', '2', '')
    assert sorted(group.extract_search(FILES, r'\d')) == sorted(expected_res)

def test_position():
    expected_res = ['1', '2', '3', '4']
    assert group.extract_position(sorted(FILES)) == expected_res

def test_group_index():
    expected_res = ['2', '1', '1', '1']
    print(FILES)
    file_attrs = [ (f, [attr,]) for f, attr in zip(FILES, group.extract_nth_letters(FILES)) ]
    g = group.collapse_groups(file_attrs)
    assert group.extract_group_index(FILES, g, reverse=True) == expected_res

def test_sub_index():
    expected_res = ['1','1', '2', '3']
    print(FILES)
    file_attrs = [ (f, [attr,]) for f, attr in zip(FILES, group.extract_nth_letters(FILES)) ]
    g = group.collapse_groups(file_attrs)
    assert group.extract_sub_index(FILES, g, start=1) == expected_res
