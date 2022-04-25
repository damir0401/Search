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
        # self.id_to_page_ranks_dict = {}
        self.word_to_id_to_rel_dict = {}


        self.titles = file_io.write_title_file(titles, self.id_to_title_dict)
        self.docs = file_io.write_docs_file(docs, self.id_to_page_ranks_dict)
        self.words = file_io.write_words_file(words, self.word_to_id_to_rel_dict)

    def id_to_title(self, page):
        # for page in self.findall("page"):
        self.id_to_title_dict[page.find('id')] = page.find('title')

    #write from title to id
    def title_to_id(self, page):
        # for page in self.findall("page"):
        self.title_to_id_dict[page.find('title')] = page.find('id')

    def id_to_page_ranks(self):
        for page in self.root.findall("page"):
            self.id_to_page_ranks_dict[page.find('id')] = page.find('t')

    def tokenization(self, text):
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        page_tokens = re.findall(n_regex, text)
        new_list = []

        # removing stop words and stem
        for words in page_tokens:
            if(re.match(r"\[\[[^\[]+?\]\]", words)):
                ...
                if()
                # write logic for links
            else:
                if(words not in STOP_WORDS):
                #if(STOP_WORDS.issuperset(words)):
                    #page_tokens.remove(words)
                    new_list.append(self.ntlk_test.stem(words))
            # else:
            #     self.ntlk_test.stem(words)


    #def detect_link(self):
        



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
            self.tokenization(title + ' ' + text)

            # stemming




            tokenization(text)
            print(self.id_to_title_dict)
            # title = page.find('title').text.strip()
            # text = page.find('text').text.strip()
            # id = int(page.find('id').text)
    
    

def pageRanker(pages):
    EPS = 0.15
    n = len(pages)
    rankingPrev = [0] * n
    rankingCurr = [1/n] * n
    while distance(rankingPrev, rankingCurr) > EPS:
        rankingCurr = rankingPrev
        for j in pages:
            rankingCurr[j] = 0
            for k in pages:
                rankingCurr[j] = rankingCurr[j] + weightPage(j, k) * rankingPrev[k]
    pass

def weightPage(k, j, pages):
    weight = 0
    EPS = 0.15
    nk = pagesContaining(pages)
    if doesLink(k, j):
        weight = (EPS / len(pages)) + (1 - EPS)(1/nk)
    else: 
        weight = (EPS / len(pages))
    return weight
        

def doesLink(k, j) -> Boolean:
    pass

def pagesContaining(pages):
    nk = 0
    for page in pages:
        if False == True:
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

            