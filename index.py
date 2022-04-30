import math
from os import nice
from socket import ntohl
import sys
#from xml.dom.minidom import Element
import re
import file_io
import xml.etree.ElementTree as et
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words('english'))
from nltk.stem import PorterStemmer
nltk_test = PorterStemmer()
from math import log

class Indexer:
    
    def __init__(self,xml,titles,docs,words):
        self.xml = xml
        # the entire job of indexer is to create 3 dictionaries
        # have helper functions that do everything for you
        # call the helper functions in the constructor
        # after you've called all of the helper function
        root: et.Element = et.parse(self.xml).getroot()
        
        self.id_to_title_dict = {}
        self.title_to_id_dict = {}
        self.id_to_page_ranks_dict = {}
        self.word_to_id_to_rel_dict = {}
        self.word_to_id_frequency_dict = {}
        self.id_to_max_freq = {}
        self.term_frequency_dict = {}

        # dict to record links for PageRank
        self.id_to_links_dict = {}

        # dict for inverse frequency
        self.word_to_inv_freq = {}
        self.parsing()

        self.titles = file_io.write_title_file(titles, self.id_to_title_dict)
        self.docs = file_io.write_docs_file(docs, self.id_to_page_ranks_dict)
        self.words = file_io.write_words_file(words, self.word_to_id_to_rel_dict)

    def id_to_title(self, page):
        self.id_to_title_dict[page.find('id').text] = page.find('title').text

    def title_to_id(self, page):
        self.title_to_id_dict[page.find('title').text] = page.find('id').text

    def id_to_page_ranks(self):
        for page in self.root.findall("page"):
            self.id_to_page_ranks_dict[page.find('id').text] = page.find('t').text

    def tokenization(self, text, id):
        n_regex = r"\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+"
        page_tokens = re.findall(n_regex, text)
        # print('page tokens')
        # print(page_tokens)
        new_list = []

        # removing stop words and stem
        for words in page_tokens:
            if re.match(r"\[\[[^\[]+?\]\]", words):
                new_word = words[2:-2]
                if ':' in new_word:
                    self.id_to_links_dict[id] = new_word
                    #processed_word = list(map(str.split(' '),new_word.split(':')))
                    processed_word = new_word.replace(':',' ').split(' ')
                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            new_list.append(stem_word)
                            self.record_frequency(id,stem_word)

                elif '|' in new_word:
                    split_word = new_word.split('|')
                    self.id_to_links_dict[id] = split_word[0]
                    processed_word = split_word[1].split(' ')
                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            new_list.append(stem_word)
                            self.record_frequency(id,stem_word)

                else:
                    self.id_to_links_dict[id] = new_word
                    processed_word = new_word.split(' ')
                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            new_list.append(stem_word)
                            self.record_frequency(id,stem_word)

            else:
                if words not in STOP_WORDS:
                    new_list.append(nltk_test.stem(words))
                    self.record_frequency(id,nltk_test.stem(words))

       #print(new_list)

        

    def record_frequency(self,id,word):
        if word in self.word_to_id_frequency_dict.keys():
            if id in self.word_to_id_frequency_dict[word].keys():
            #if id in self.id_to_frequency_dict.keys:
                self.word_to_id_frequency_dict[word][id] += 1
                #self.id_to_frequency_dict[id] = self.id_to_frequency_dict.get(id) + 1
            else:
                self.word_to_id_frequency_dict[word][id] = 1
                #self.id_to_frequency_dict[id] = 1
        else:
            #self.id_to_frequency_dict[id] = 1
            self.word_to_id_frequency_dict[word] = {}
            self.word_to_id_frequency_dict[word][id] = 1
        
        # id to frequency of most frequently occurring word on page
        if id in self.id_to_max_freq:
            if self.word_to_id_frequency_dict[word][id] > self.id_to_max_freq[id]:
                self.id_to_max_freq[id] = self.word_to_id_frequency_dict[word][id]
        else:
            self.id_to_max_freq[id] = self.word_to_id_frequency_dict[word][id]


    def add_link(self,id,word):
        if id in self.id_to_links_dict.keys():
            self.id_to_links_dict[id].add(word)
        else:
            self.id_to_links_dict[id] = set(word)

    def term_frequency(self):
        for word in self.word_to_id_frequency_dict.keys():
            for id in self.term_frequency_dict[word].keys():
                self.term_frequency_dict[word][id] = self.term_frequency_dict[word][id]/self.id_to_max_freq[id]

    def inverse_doc_frequency(self):
        n = len(self.id_to_title_dict.keys())
        for word in self.word_to_id_frequency_dict.keys():
            num_docs = len(self.word_to_id_frequency_dict.get(word).keys())
            idf = log(n/num_docs)
            self.word_to_inv_freq[word] = idf
    
    def word_to_id_rel_helper(self,word):
        id_to_rel = {}
        for id in self.term_frequency_dict.get(word).keys():
            #print("WHY")
            #print(self.term_frequency_dict.get(word))
            id_to_rel[id] = self.term_frequency_dict.get(word).get(id) * self.word_to_inv_freq.get(word)
        return id_to_rel

    def word_to_id_rel(self):
        for word in self.word_to_id_frequency_dict.keys():
            self.word_to_id_to_rel_dict[word] = self.word_to_id_rel_helper(word)
    

    def parsing(self):
        root = et.parse(self.xml).getroot()
        for page in root.findall("page"):
            # populating self.id_to_title_dict
            self.id_to_title(page)
            self.title_to_id(page)

        for page in root.findall("page"):
            # tokenization
            title = page.find('title').text.strip()
            text = page.find('text').text.strip()
            id = int(page.find('id').text)
            self.tokenization(title + ' ' + text, id)
        print('word_to_id_frequency_dict')
        print(self.word_to_id_frequency_dict)
        self.term_frequency_dict = self.word_to_id_frequency_dict.copy()
        self.term_frequency()
        print('self.term_frequency_dict')
        print(self.term_frequency_dict)
        self.inverse_doc_frequency()
        print('word_to_inv_freq')
        print(self.word_to_inv_freq)
        self.word_to_id_rel()
        print('word_to_id_rel')
        print(self.word_to_id_to_rel_dict)
        #return self.term_frequency_dict



def pageRanker(page_dict):
    pages = list (page_dict.keys())
    EPS = 0.15
    n = len(pages)
    rankingPrev = [0] * n
    rankingCurr = [1/n] * n
    while eDistance(rankingPrev, rankingCurr) > EPS:
        rankingCurr = rankingPrev
        for j in len(pages):
            rankingCurr[j] = 0
            for k in pages:
                rankingCurr[j] = rankingCurr[j] + weightPage(j, k) * rankingPrev[k]

def eDistance(rp, rc):
    termSquares = [0] * len(rp)
    for i in range(len(rp)):
        termSquares.append((rc[i] - rp[i])^2)
    return math.sqrt(sum(termSquares))
    

def weightPage(k, j, pages):
    weight = 0
    EPS = 0.15
    nk = pagesContaining(pages)
    if doesLink(k, j):
        weight = (EPS / len(pages)) + (1 - EPS)(1/nk)
    else: 
        weight = (EPS / len(pages))
    return weight
        

def doesLink(k, j, id_l_dict) -> bool:
    dl = False
    for id in id_l_dict[k]:
        if id == j:
            dl = True
    return dl
    pass

def pagesContaining(pages, j):
    nk = 0
    for page in pages:
        if doesLink(page, j):
            nk += 1
    return nk



if __name__ == "main":
    xml_filepath = sys.argv[1]
    titles_filepath = sys.argv[2]
    docs_filepath = sys.argv[3]
    words_filepath = sys.argv[4]
    print(len(sys.argv))
    if len(sys.argv)-1 != 4:
        print("Try passing in 3 arguments")
    Indexer(xml_filepath,titles_filepath,docs_filepath,words_filepath)

            