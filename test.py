import pytest
from index import *
from file_io import *

def test_parsing():
    indexer = Indexer("wiki_test.xml","titles.txt","docs.txt","words.txt")
    assert 'student' in indexer.term_frequency_dict
    
def test_term_frequency():
    indexer = Indexer("wiki_test.xml","titles.txt","docs.txt","words.txt")
    #assert 'area' in indexer.parsing()
    #print(indexer.term_frequency_dict)
    #print(indexer.term_frequency_dict.get('area'))
    assert indexer.term_frequency_dict.get('area').get(0) == 1/5

def test_term_frequency1():
    indexer = Indexer("wikis/test_tf_idf.xml","titles.txt","docs.txt","words.txt")
    assert indexer.term_frequency_dict.get('dog').get(1) == 1

