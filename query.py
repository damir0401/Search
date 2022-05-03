import file_io
from turtle import distance
from xmlrpc.client import Boolean
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words('english'))
from nltk.stem import PorterStemmer
import sys
stemmer = PorterStemmer()


class Querier:

    def __init__(self,pagerank,titleIndex,documentIndex,wordIndex):
        self.pagerank = pagerank
        self.id_to_title_dict = {}
        self.id_to_page_ranks_dict = {}
        self.word_to_id_to_rel_dict = {}
        self.id_to_rel_dict = {}

        #self.id_to_rel()

    

        self.titleIndex = file_io.read_title_file(titleIndex, self.id_to_title_dict)
        print(self.id_to_title_dict)
        self.docs = file_io.read_docs_file(documentIndex, self.id_to_page_ranks_dict)
        print(self.id_to_page_ranks_dict)
        #print("seeing the word index", wordIndex)
        self.wordIndex = file_io.read_words_file(wordIndex, self.word_to_id_to_rel_dict)
        print(self.wordIndex)

        #exit()
        #self.query()
    
    # pagerank: bool, titleIndex: dict, docIndex: dict, wordIndex: dict
    def query(self):
        while True:
            phrase = input("search phrase:")
            if phrase == "quit":
                exit()  
            word_list = phrase.split(" ")
            self.id_to_rel(self.stem_list(word_list))
            self.handle_printing(self.ranking_rel())
  

    def stem_list(self,word_list):
        new_list = []
        for word in word_list:
                if not(word in STOP_WORDS):
                    word_list.remove(word)
                new_list.append(stemmer.stem(word))
        return new_list

    
    def scoring_rel(self,id,word_list):
        sum = 0
        if self.pagerank:
            for word in word_list:
                sum = sum + self.word_to_id_to_rel_dict[word][id] * self.id_to_page_ranks_dict[id]
        else:
            for word in word_list:
                sum = sum + self.word_to_id_to_rel_dict[word][id]

    def id_to_rel(self,word_list):
        for id in self.id_to_title_dict:
            self.id_to_rel_dict[id] = self.scoring_rel(id,word_list)
    
    def return_val(self,tuple):
        return tuple[1]

    def ranking_rel(self):
        #print(list(self.id_to_rel_dict.items()).sort(reverse=True, key=self.return_val))
        
        # print('the dictionary in the method', self.id_to_rel_dict)
        return list(self.id_to_rel_dict.items()).sort(reverse=True, key=self.return_val)


    def handle_printing(self, curr_list):
        print("Checking the element" , curr_list)
        num_element = min(10, len(curr_list))
        for i in range(num_element):
            print("\t" + f"{i+1} " + self.id_to_title_dict[curr_list[i]])

    
    ##### with pagerank

    # def scoring_rel_pagerank(self,id,word_list):
    #     sum = 0
    #     for word in word_list:
    #         sum = sum + self.word_to_id_to_rel_dict[word][id] + self.id_to_page_ranks_dict[id]

    # def ranking_rel_pagerank(self):
    #     return 



    # def query(titleIndex: dict, docIndex: dict, wordIndex: dict):
    #     while True:
    #         phrase = input("search phrase:")
    #         word_list = phrase.split(" ")
    #         stemmer = PorterStemmer()
    #         for word in word_list:
    #             if not(word in STOP_WORDS):
    #                 word_list.remove(word)
    #             stemmer.stem(word)
    #         if phrase == ":quit":
    #             exit()


if __name__ == "__main__":
    if len(sys.argv) == 5:
        page_rank = sys.argv[1]
        title_index = sys.argv[2]
        document_index = sys.argv[3]
        word_index = sys.argv[4]
        q = Querier(True,title_index,document_index,word_index)
    elif len(sys.argv) == 4:
        title_index = sys.argv[1]
        document_index = sys.argv[2]
        word_index = sys.argv[3]
        q = Querier(False,title_index,document_index,word_index)
    else:
        print("Try passing in 3 or 4 arguments")
    q.query()
    #Querier(title_index,document_index,word_index)