import math
from os import nice
from socket import ntohl
import sys
import re
from tokenize import Number
from typing import Set
from xml.dom.minidom import Element
from xmlrpc.client import Boolean
import file_io
import xml.etree.ElementTree as et
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words('english'))
from nltk.stem import PorterStemmer
nltk_test = PorterStemmer()
from math import log


class Indexer:
    '''
    This is a class that contains code for indexing the XML file
    '''

    def __init__(self,xml,titles,docs,words):
        '''
        Initialization method for Indexer class.
        '''
        # xml
        self.xml = xml

        # dict to map id to titles
        self.id_to_title_dict = {}

        # dict to map titles to id
        self.title_to_id_dict = {}

        # dict to map id to pageranks
        self.id_to_page_ranks_dict = {}

        # dict to map word to dict of id to relevance scores
        self.word_to_id_to_rel_dict = {}

        # dict to map word to id frequency
        self.word_to_id_frequency_dict = {}

        # dict to map id to max frequency
        self.id_to_max_freq = {}

        # dict to map term to its frequency
        self.term_frequency_dict = {}

        # dict to record links for PageRank
        self.id_to_links_dict = {}

        # dict for inverse frequency
        self.word_to_inv_freq = {}

        # dict for weights
        self.id_to_weights_dict = {}

        self.parsing()
        self.calculate_weight()
        self.pageRank()

        # writing to files
        self.titles = file_io.write_title_file(titles, self.id_to_title_dict)
        self.docs = file_io.write_docs_file(docs, self.id_to_page_ranks_dict)
        self.words = \
            file_io.write_words_file(words, self.word_to_id_to_rel_dict)

    def id_to_title(self, page) -> None:
        '''
        Does not return anything. It populates the id_to_title_dict dictionary

        Parameters: 
        page - a single page in the XML file

        Returns: 
        None
        '''
        self.id_to_title_dict[int(float(page.find('id').text.strip()))] = \
            page.find('title').text.strip()

    def title_to_id(self, page) -> None:
        '''
        Does not return anything. It populates the title_to_id_dict dictionary

        Parameters: 
        page - a single page in the XML file

        Returns: 
        None
        '''
        self.title_to_id_dict[page.find('title').text.strip()] = \
            int(float(page.find('id').text.strip()))

    def id_to_links(self) -> None:
        '''
        Does not return anything. It populates the id_to_links_dict dictionary

        Parameters: 
        None

        Returns: 
        None
        '''
        for id in self.id_to_title_dict.keys():
            self.id_to_links_dict[id] = set([])

    def item_remove(self,i,new_list) -> Set:
        '''
        It removes the item from the list and returns the list

        Parameters: 
        i - item to remove
        new_list - a list

        Returns: 
        a set without given item
        '''
        l = set([])
        for item in new_list:
            if item != i:
                l.add(item)
        return l

    def filter_helper(self,title) -> Boolean:
        '''
        Returns a boolean if the title in the keys of title_to_id_dict 
        dictionary

        Parameters: 
        title - a string(title)

        Returns: 
        A boolean if the title in the keys of title_to_id_dict dictionary
        '''
        return title in self.title_to_id_dict.keys()

    def id_to_links_processing(self) -> None:
        '''
        Processes the id_to_link_dict. For example, if the link does not have
        links, the function populates it with all of the pages, except itself

        Parameters:
        None

        Returns: 
        None
        '''
        for id in self.id_to_title_dict.keys():
            for title in self.id_to_links_dict[id]:
                self.id_to_links_dict[id] = \
                    set(filter(self.filter_helper,self.id_to_links_dict[id]))
            if len(self.id_to_links_dict[id]) == 0 or \
                (len(self.id_to_links_dict[id]) == 1 \
                    and self.id_to_title_dict[id] in self.id_to_links_dict[id]):
                self.id_to_links_dict[id] = \
                    self.item_remove(self.id_to_title_dict[id], \
                    list(self.title_to_id_dict.keys()))
            elif len(self.id_to_title_dict[id]) != 0 \
                and self.id_to_title_dict[id] in self.id_to_links_dict[id]:
                l = self.id_to_links_dict[id]
                self.id_to_links_dict[id] = self.item_remove(id,l)


    def tokenization(self, text, id) -> None:
        '''
        Processing documents into essential terms(tokenizes the given text, and 
        stems)

        Parameters:
        text - id + text of documents
        id - id of a document

        Returns: 
        None
        '''
        n_regex = r"\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+"
        page_tokens = [x for x in re.findall(n_regex, text.strip()) \
            if x != "" or x != "\n" or x !=" "]
        # removing stop words and stem
        
        for words in page_tokens:
            if re.match(r"\[\[[^\[]+?\]\]", words):
                new_word = words[2:-2].strip()
                if '|' in new_word:
                    split_word = new_word.split('|')
                    self.id_to_links_dict[id].add(split_word[0])
                    processed_word = [x for x in \
                        re.findall(n_regex, split_word[1].strip()) \
                            if x != "" or x != "\n" or x !=" "]
                    
                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            self.record_frequency(id,stem_word)
                else:
                    self.id_to_links_dict[id].add(new_word)
                    processed_word = [x for x in \
                        re.findall(n_regex, new_word.strip()) \
                            if x != "" or x != "\n" or x !=" "]

                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            self.record_frequency(id,stem_word)

            else:
                if words not in STOP_WORDS:
                    self.record_frequency(id,nltk_test.stem(words))

    def record_frequency(self,id,word) -> None:
        '''
        Records frequency of the term and populates word_to_id_frequency_dict.
        It also records the max frequency for each document.

        Parameters:
        id - id of a document
        word - term

        Returns: 
        None
        '''
        if word in self.word_to_id_frequency_dict.keys():
            if id in self.word_to_id_frequency_dict[word].keys():
                self.word_to_id_frequency_dict[word][id] += 1
            else:
                self.word_to_id_frequency_dict[word][id] = 1
        else:
            self.word_to_id_frequency_dict[word] = {}
            self.word_to_id_frequency_dict[word][id] = 1
        
        # id to frequency of most frequently occurring word on page
        if id in self.id_to_max_freq:
            if self.word_to_id_frequency_dict[word][id] > \
                self.id_to_max_freq[id]:
                self.id_to_max_freq[id] = \
                    self.word_to_id_frequency_dict[word][id]
        else:
            self.id_to_max_freq[id] = self.word_to_id_frequency_dict[word][id]

    def term_frequency(self) -> None:
        '''
        Calculates term frequency

        Parameters:
        None

        Returns: 
        None
        '''
        for word in self.word_to_id_frequency_dict.keys():
            for id in self.term_frequency_dict[word].keys():
                self.term_frequency_dict[word][id] = \
                    self.term_frequency_dict[word][id]/self.id_to_max_freq[id]

    def inverse_doc_frequency(self) -> None:
        '''
        Calculates inverse doc frequency

        Parameters:
        None

        Returns: 
        None
        '''
        n = len(self.id_to_title_dict.keys())
        for word in self.word_to_id_frequency_dict.keys():
            num_docs = len(self.word_to_id_frequency_dict.get(word).keys())
            idf = log(n/num_docs)
            self.word_to_inv_freq[word] = idf
    
    def word_to_id_rel_helper(self,word) -> None:
        '''
        Populates id_to_rel dictionary, which will be used to populate
        word_to_id_rel_dict

        Parameters:
        word - a term

        Returns: 
        None
        '''
        id_to_rel = {}
        for id in self.term_frequency_dict.get(word).keys():
            id_to_rel[id] = \
                self.term_frequency_dict.get(word).get(id) * \
                    self.word_to_inv_freq.get(word)
        return id_to_rel

    def word_to_id_rel(self) -> None:
        '''
        Populates word_to_id_rel_dict

        Parameters:
        None

        Returns: 
        None
        '''
        for word in self.word_to_id_frequency_dict.keys():
            self.word_to_id_to_rel_dict[word] = self.word_to_id_rel_helper(word)
    

    def parsing(self) -> None:
        '''
        Parses the XML file(processing of documents into essential terms)

        Parameters:
        None

        Returns: 
        None
        '''
        root: Element = et.parse(self.xml).getroot()
        for page in root.findall("page"):
            # populating self.id_to_title_dict
            self.id_to_title(page)
            self.title_to_id(page)
        self.id_to_links()
        for page in root.findall("page"):
            # tokenization
            title = page.find('title').text.strip()
            text = page.find('text').text.strip() 
            id = int(float(page.find('id').text.strip()))
            self.tokenization(title + ' ' + text, id)
        self.id_to_links_processing()
        self.term_frequency_dict = self.word_to_id_frequency_dict.copy()
        self.term_frequency()
        self.inverse_doc_frequency()
        self.word_to_id_rel()

    def pageRank(self) -> None:
        '''
        Calculates pagerank for each document

        Parameters:
        None

        Returns: 
        None
        '''
        delta = 0.001 
        rPrev = {}
        n = len(self.id_to_title_dict.keys())
        for id in self.id_to_title_dict.keys():
            rPrev[id] = 0
            self.id_to_page_ranks_dict[id] = 1/n

        while self.rDistance(rPrev,self.id_to_page_ranks_dict) > delta:
            rPrev = self.id_to_page_ranks_dict.copy()
            for j in self.id_to_title_dict.keys():
                self.id_to_page_ranks_dict[j] = 0
                for k in self.id_to_title_dict.keys():
                    self.id_to_page_ranks_dict[j] = \
                        self.id_to_page_ranks_dict[j] + \
                            self.id_to_weights_dict[k,j] * rPrev[k]

    def rDistance(self,rPrev,rCurr) -> Number:
        '''
        Determines the distance between two iterations

        Parameters:
        rPrev - previous page ranking
        rCurr - current page ranking

        Returns: 
        A number(distance) 
        '''
        sum = 0
        for key in rCurr.keys():
            sum = sum + (rCurr[key] - rPrev[key])**2
        return math.sqrt(sum)

    def calculate_weight(self) -> None:
        '''
        Calculates weights of the links

        Parameters:
        None

        Returns: 
        None
        '''
        EPS = 0.15
        for k in self.id_to_title_dict.keys():
            for j in self.id_to_title_dict.keys():
                if self.id_to_title_dict[j] in self.id_to_links_dict[k]:
                    self.id_to_weights_dict[k,j] = \
                        EPS/len(self.id_to_title_dict.keys()) + \
                            (1-EPS)/(len(self.id_to_links_dict[k]))
                else:
                    self.id_to_weights_dict[k,j] = \
                        EPS/len(self.id_to_title_dict)


if __name__ == "__main__":
    '''
        Main method of Indexer class. If user passes less or more than 3 input 
        words, prints out the informative message

        Parameters:
        None

        Returns: 
        None
        '''
    xml_filepath = sys.argv[1]
    titles_filepath = sys.argv[2]
    docs_filepath = sys.argv[3]
    words_filepath = sys.argv[4]
    if len(sys.argv)-1 != 4:
        print("Try passing in 3 arguments")
    Indexer(xml_filepath,titles_filepath,docs_filepath,words_filepath)

            