import math
from os import nice
from socket import ntohl
import sys
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

        self.titles = file_io.write_title_file(titles, self.id_to_title_dict)
        self.docs = file_io.write_docs_file(docs, self.id_to_page_ranks_dict)
        self.words = file_io.write_words_file(words, self.word_to_id_to_rel_dict)

    def id_to_title(self, page):
        self.id_to_title_dict[int(page.find('id').text.strip())] = page.find('title').text.strip()

    def title_to_id(self, page):
        self.title_to_id_dict[page.find('title').text.strip()] = int(page.find('id').text.strip())

    def id_to_links(self):
        for id in self.id_to_title_dict.keys():
            self.id_to_links_dict[id] = set([])

    def item_remove(self,i,new_list):
        l = set([])
        for item in new_list:
            if item != i:
                l.add(item)
        return l

    def filter_helper(self,title):
        return title in self.title_to_id_dict.keys()

    def id_to_links_processing(self):
        for id in self.id_to_title_dict.keys():
            #filter(self.filter_helper,self.id_to_links_dict[id])
            #print('filter')
            #print(filter(self.filter_helper,self.id_to_links_dict[id]))
            #self.id_to_links_dict[id] = set(filter(self.filter_helper,self.id_to_links_dict[id]))
            for title in self.id_to_links_dict[id]:
                self.id_to_links_dict[id] = set(filter(self.filter_helper,self.id_to_links_dict[id]))
                # if title not in self.title_to_id_dict.keys():
                #     self.id_to_links_dict[id] = self.item_remove(id,title)
                    #self.id_to_links_dict[id].remove(title)

            if len(self.id_to_links_dict[id]) == 0 or (len(self.id_to_links_dict[id]) == 1 and self.id_to_title_dict[id] in self.id_to_links_dict[id]):
                self.id_to_links_dict[id] = self.item_remove(self.id_to_title_dict[id],list(self.title_to_id_dict.keys()))
            elif len(self.id_to_title_dict[id]) != 0 and self.id_to_title_dict[id] in self.id_to_links_dict[id]:
                l = self.id_to_links_dict[id]
                self.id_to_links_dict[id] = self.item_remove(id,l)


    # def stem_and_stop(self, word):

    #     if word.lower() in STOP_WORDS:
    #         return ""
    #     return nltk_test.stem(word.lower())

    def tokenization(self, text, id):
        n_regex = r"\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+"
        page_tokens = re.findall(n_regex, text)

        # removing stop words and stem


        # new_tokens = [self.stem_and_stop(x) for x in page_tokens]
        
        for words in page_tokens:
            if re.match(r"\[\[[^\[]+?\]\]", words):
                new_word = words[2:-2].strip()
                if ':' in new_word:
                    self.id_to_links_dict[id].add(new_word)
                    processed_word = new_word.replace(':',' ').split(' ')
                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            self.record_frequency(id,stem_word)

                elif '|' in new_word:
                    split_word = new_word.split('|')
                    self.id_to_links_dict[id].add(split_word[0])
                    processed_word = split_word[1].split(' ')
                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            self.record_frequency(id,stem_word)

                else:
                    self.id_to_links_dict[id].add(new_word)
                    processed_word = new_word.split(' ')
                    for word in processed_word:
                        if word not in STOP_WORDS:
                            stem_word = nltk_test.stem(word)
                            self.record_frequency(id,stem_word)

            else:
                if words not in STOP_WORDS:
                    self.record_frequency(id,nltk_test.stem(words))

        

    def record_frequency(self,id,word):
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
            if self.word_to_id_frequency_dict[word][id] > self.id_to_max_freq[id]:
                self.id_to_max_freq[id] = self.word_to_id_frequency_dict[word][id]
        else:
            self.id_to_max_freq[id] = self.word_to_id_frequency_dict[word][id]


    # def add_link(self,id,word):
    #     if id in self.id_to_links_dict.keys():
    #         self.id_to_links_dict[id].add(word)
    #     else:
    #         self.id_to_links_dict[id] = set(word)

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
            id_to_rel[id] = self.term_frequency_dict.get(word).get(id) * self.word_to_inv_freq.get(word)
        return id_to_rel

    def word_to_id_rel(self):
        for word in self.word_to_id_frequency_dict.keys():
            # if word != "" and word != " " and word != "\n":
            # print("fdkfmdkffd")
            self.word_to_id_to_rel_dict[word] = self.word_to_id_rel_helper(word)
    

    def parsing(self):
        root = et.parse(self.xml).getroot()
        #page = root.findall("page")
        for page in root.findall("page"):
            # populating self.id_to_title_dict
            self.id_to_title(page)
            self.title_to_id(page)

            #print(f"progress {i}/ {len(page)}")

        self.id_to_links()
        for page in root.findall("page"):
            # tokenization
            title = page.find('title').text.strip()
            text = page.find('text').text.strip() 
            #id = int(float(page.find('id').text.strip()))
            id = int(page.find('id').text)
            self.tokenization(title + ' ' + text, id)

        print('id_to_links_dict before')
        print(self.id_to_links_dict)

        self.id_to_links_processing()
        # print('word_to_id_frequency_dict')
        # print(self.word_to_id_frequency_dict)
        self.term_frequency_dict = self.word_to_id_frequency_dict.copy()
        self.term_frequency()
        # print('self.term_frequency_dict')
        # print(self.term_frequency_dict)
        self.inverse_doc_frequency()
        # print('word_to_inv_freq')
        # print(self.word_to_inv_freq)
        self.word_to_id_rel()
        # print('word_to_id_rel')
        # print(self.word_to_id_to_rel_dict)
        # print('id_to_links_dict after')
        # print(self.id_to_links_dict)
        print('word to id to rel')
        print(self.word_to_id_to_rel_dict)
    
    ###########

    def pageRank(self):
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
                    self.id_to_page_ranks_dict[j] = self.id_to_page_ranks_dict[j] + self.id_to_weights_dict[k,j] * rPrev[k]
        print('id_to_page_ranks')
        print(self.id_to_page_ranks_dict)


    def rDistance(self,rPrev,rCurr):
        sum = 0
        for key in rCurr.keys():
            sum = sum + (rCurr[key] - rPrev[key])**2
        return math.sqrt(sum)

    def calculate_weight(self):
        EPS = 0.15
        for k in self.id_to_title_dict.keys():
            for j in self.id_to_title_dict.keys():
                if self.id_to_title_dict[j] in self.id_to_links_dict[k]:
                    self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_links_dict[k]))
                else:
                    self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict)

    # Solution that works
    # def calculate_weight(self):
    #     for k in self.id_to_title_dict.keys():
    #         for j in self.id_to_title_dict.keys():
    #             if self.id_to_title_dict[j] in self.id_to_links_dict[k] and k != j:
    #                 self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_links_dict[k]))
    #             else:
    #                 if k != j and len(self.id_to_links_dict[k]) == 0:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_title_dict) - 1)
    #                 else:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict)

    

    # TA suggestion
    # def calculate_weight(self):
    #     for k in self.id_to_title_dict.keys():
    #         for j in self.id_to_title_dict.keys():
    #             if k == j:
    #                 self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict)
    #                 #self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_title_dict) - 1)

    #             elif k in self.id_to_links_dict and j in self.id_to_links_dict[k]:
    #                 self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_links_dict[k]))
    #             elif len(self.id_to_links_dict[k]) == 0:
    #                 print('HERE')
    #                 print(k)
    #                 self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_title_dict) - 1)
    #             else:
    #                 self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict)
    #         print('id to weightd')
    #         print(self.id_to_weights_dict)


                # if self.id_to_title_dict[j] in self.id_to_links_dict[k] and k != j:
                #     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_links_dict[k]))
                # else:
                #     if k != j and len(self.id_to_links_dict[k]) == 0:
                #         self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_title_dict) - 1)
                #     else:
                #         self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict)
        
        # print('id_to_weights_dict')
        # print(self.id_to_weights_dict)

    # PREVIOUS WEIGHTS
    # def calculate_weight(self):
    #     for k in self.id_to_title_dict.keys():
    #         for j in self.id_to_title_dict.keys():
    #             if self.id_to_title_dict[j] in self.id_to_links_dict[k] and k != j:
    #                 self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_links_dict[k]))
    #             else:
    #                 if k != j and len(self.id_to_links_dict[k]) == 0:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_title_dict) - 1)
    #                 else:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict)

    # def calculate_weight(self):
    #     print('self.id_to_links_dict')
    #     print(self.id_to_links_dict)
    #     for k in self.id_to_title_dict.keys():
    #         for j in self.id_to_title_dict.keys():
    #             if self.id_to_title_dict[k] in self.id_to_links_dict[j]:
    #                 if len(self.id_to_links_dict[k]) == 0:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_links_dict) - 1)
    #                 else:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/len(self.id_to_links_dict[k])
    #             else:
    #                 if len(self.id_to_links_dict[k]) == 0:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys()) + (1-EPS)/(len(self.id_to_links_dict) - 1)
    #                 else:
    #                     self.id_to_weights_dict[k,j] = EPS/len(self.id_to_title_dict.keys())
    #     print('id_to_weights_dict')
    #     print(self.id_to_weights_dict)

    # def hasLink(self,k):
    #     self.id_to_links_dict
    #     self.title_to_id_dict
    #     return self.id_to_title_dict[k] in 

######

# def pageRanker(page_dict):
#     pages = list (page_dict.keys())
#     EPS = 0.15
#     n = len(pages)
#     rankingPrev = [0] * n
#     rankingCurr = [1/n] * n
#     while eDistance(rankingPrev, rankingCurr) > EPS:
#         rankingCurr = rankingPrev
#         for j in len(pages):
#             rankingCurr[j] = 0
#             for k in pages:
#                 rankingCurr[j] = rankingCurr[j] + weightPage(j, k) * rankingPrev[k]

# def eDistance(rp, rc):
#     termSquares = [0] * len(rp)
#     for i in range(len(rp)):
#         termSquares.append((rc[i] - rp[i])^2)
#     return math.sqrt(sum(termSquares))
    

# def weightPage(k, j, pages):
#     weight = 0
#     EPS = 0.15
#     nk = pagesContaining(pages)
#     if doesLink(k, j):
#         weight = (EPS / len(pages)) + (1 - EPS)(1/nk)
#     else: 
#         weight = (EPS / len(pages))
#     return weight
        

# def doesLink(k, j, id_l_dict) -> bool:
#     dl = False
#     for id in id_l_dict[k]:
#         if id == j:
#             dl = True
#     return dl

# def pagesContaining(pages, j):
#     nk = 0
#     for page in pages:
#         if doesLink(page, j):
#             nk += 1
#     return nk




if __name__ == "__main__":
    xml_filepath = sys.argv[1]
    titles_filepath = sys.argv[2]
    docs_filepath = sys.argv[3]
    words_filepath = sys.argv[4]
    print(len(sys.argv))
    if len(sys.argv)-1 != 4:
        print("Try passing in 3 arguments")
    Indexer(xml_filepath,titles_filepath,docs_filepath,words_filepath)

            