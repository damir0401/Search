import pytest
from index import *
from file_io import *
from query import Querier

# def test_parsing():
#     indexer = Indexer("wiki_test.xml","titles.txt","docs.txt","words.txt")
#     assert 'student' in indexer.term_frequency_dict
    
# def test_term_frequency():
#     indexer = Indexer("wiki_test.xml","titles.txt","docs.txt","words.txt")
#     #assert 'area' in indexer.parsing()
#     #print(indexer.term_frequency_dict)
#     #print(indexer.term_frequency_dict.get('area'))
#     assert indexer.term_frequency_dict.get('area').get(0) == 1/5

# def test_term_frequency1():
#     indexer = Indexer("wikis/test_tf_idf.xml","titles.txt","docs.txt","words.txt")
#     assert indexer.term_frequency_dict.get('dog').get(1) == 1

def test_page_rank():
    indexer = Indexer("wikis/PageRankExample1.xml","titles.txt","docs.txt","words.txt")
    assert (1, 1) in indexer.id_to_weights_dict


def test_page_rank1():
    indexer = Indexer("wikis/PageRankExample1.xml","titles.txt","docs.txt","words.txt")
    indexer.pageRank()
    assert 1 in indexer.id_to_page_ranks_dict
    #assert indexer.id_to_page_ranks_dict.get(1) == 0.4326


def test_page_rank2():
    indexer = Indexer("wikis/PageRankExample2.xml","titles.txt","docs.txt","words.txt")
    indexer.pageRank()
    assert 1 in indexer.id_to_page_ranks_dict

def test_page_rank3():
    indexer = Indexer("wikis/PageRankExample3.xml","titles.txt","docs.txt","words.txt")
    indexer.pageRank()
    assert 1 in indexer.id_to_page_ranks_dict

def test_page_rank4():
    indexer = Indexer("wikis/PageRankExample4.xml","titles.txt","docs.txt","words.txt")
    indexer.pageRank()
    assert 1 in indexer.id_to_page_ranks_dict

#DO NOT TOUCH
# def test_page_rank5():
#     indexer = Indexer("wikis/MedWiki.xml","titles.txt","docs.txt","words.txt")
#     indexer.pageRank()
#     assert '1' in indexer.id_to_page_ranks_dict

# def test_query():
#     indexer = Indexer("wikis/PageRankExample1.xml","titles.txt","docs.txt","words.txt")
#     querier = Querier(False,"titles.txt","docs.txt","words.txt")
#     #querier.id_to_rel()
#     assert 1 in querier.id_to_rel_dict

def test_indexer_links():
    indexer2 = Indexer("wiki_test.xml", "titles.txt", "docs.txt", "words.txt")
    assert indexer2.id_to_links_dict == {0: ['CS320', 'CS330'], 1: ['CS200', 'CS320']}
    indexer3 = Indexer("test_tf_idf.xml", "titles.txt", "docs.txt", "words.txt")
    assert indexer3.id_to_links_dict == {1: ['Page 2', 'Page 3'], 2: ['Page 1', 'Page 3'], 3: ['Page 1', 'Page 2']}
    
def test_word_to_id_rel():
    indexer3 = Indexer("wiki_test.xml", "titles.txt", "docs.txt", "words.txt")
    print('HERE')
    assert round(indexer3.word_to_id_to_rel_dict['week'][0], 5) == 0.13863
    assert round(indexer3.word_to_id_to_rel_dict['organ'][1], 5) == 0.09902
    assert round(indexer3.word_to_id_to_rel_dict['student'][1], 2) == 0.0
    assert round(indexer3.word_to_id_to_rel_dict['student'][1], 2) == 0.0
    assert round(indexer3.word_to_id_to_rel_dict['oper'][1], 5) == 0.09902
    assert round(indexer3.word_to_id_to_rel_dict['oper'][1], 5) == 0.09902

def test_word_to_inv_freq():
    indexer4 = Indexer("wiki_test.xml", "titles.txt", "docs.txt", "words.txt")
    assert round(indexer4.word_to_inv_freq['cs330'], 5) == 0.69315
    assert round(indexer4.word_to_inv_freq['teach'], 5) == 0.69315
    assert round(indexer4.word_to_inv_freq['processor'], 5) == 0.69315
    assert round(indexer4.word_to_inv_freq['multi'], 5) == 0.69315



