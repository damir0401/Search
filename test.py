import pytest
from index import *
from file_io import *

def test_parsing():
    indexer = Indexer("wiki_test.xml","titles.txt", "docs.txt","words.txt")
    assert indexer.parsing() == "s"
    


