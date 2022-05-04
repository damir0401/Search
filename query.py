from tokenize import Number
from typing import List
import file_io
from turtle import distance
from xmlrpc.client import Boolean
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words('english'))
from nltk.stem import PorterStemmer
import sys
stemmer = PorterStemmer()


class Querier:
    '''
    This is a class that contains code for quering
    '''

    def __init__(self,pagerank,titleIndex,documentIndex,wordIndex):
        '''
        Initialization method for Indexer class.
        '''
        
        # a boolean whether user wants to include pagerank
        self.pagerank = pagerank

        # dict to map id to titles
        self.id_to_title_dict = {}

        # dict to map id to page ranks
        self.id_to_page_ranks_dict = {}

        # dict to map word to id to relevances
        self.word_to_id_to_rel_dict = {}

        # dict to map id to relevances
        self.id_to_rel_dict = {}

        # reading files populated by Indexer
        self.titleIndex = \
            file_io.read_title_file(titleIndex, self.id_to_title_dict)
        self.docs = \
            file_io.read_docs_file(documentIndex, self.id_to_page_ranks_dict)
        self.wordIndex = \
            file_io.read_words_file(wordIndex, self.word_to_id_to_rel_dict)
    
    def query(self) -> None:
        '''
        REPL. Prompts the user for input, then processes the input, 
        prints the result and repeats

        Parameters: 
        None

        Returns: 
        None
        '''
        while True:
            self.id_to_rel_dict = {}
            phrase = input("search phrase:")
            if phrase == ":quit":
                break 
            word_list = phrase.split(" ")
            new_word_list = self.stem_list(word_list)
            self.id_to_rel(new_word_list)
            self.handle_printing(self.ranking_rel())

    def stem_list(self,word_list) -> List:
        '''
        Stemming words of the input list of words

        Parameters: 
        None

        Returns: 
        None
        '''
        new_list = []
        for word in word_list:
            if word not in STOP_WORDS:
                new_list.append(stemmer.stem(word))
        return new_list

    
    def scoring_rel(self,id,word_list) -> Number:
        '''
        Computes relevance scores based on if pagerank was used and 
        word_to_id_to_rel_dict.

        Parameters: 
        id - id of a document
        word_list - a list of input words

        Returns: 
        The relevance score for each word
        '''
        sum = 0
        if self.pagerank:
            for word in word_list:
                if word in self.word_to_id_to_rel_dict:
                    if id in self.word_to_id_to_rel_dict[word].keys():
                        sum = sum + self.word_to_id_to_rel_dict[word][id] \
                            * self.id_to_page_ranks_dict[id]
                    else:
                        sum = sum
        else:
            for word in word_list:
                if word in self.word_to_id_to_rel_dict.keys():
                    if id in self.word_to_id_to_rel_dict[word].keys():
                        sum = sum + self.word_to_id_to_rel_dict[word][id]
                    else:
                        sum = sum
        return sum

    def id_to_rel(self,word_list) -> None:
        '''
        Populates id_to_rel dictionary after scoring relevance scores.
        It also prints 'No results', if the input words are not in the corpus

        Parameters: 
        word_list - a list of input words

        Returns: 
        None
        '''
        for id in self.id_to_title_dict:
            rel = self.scoring_rel(id, word_list)
            if rel != 0:
                self.id_to_rel_dict[id] = rel
        if len(self.id_to_rel_dict) == 0:
            print("No results")
    
    def return_val(self,tuple) -> Number:
        '''
        Returns the second value of a tuple of id and relevance scores

        Parameters: 
        tuple - tuple of id and relevance scores

        Returns: 
        Second value of a tuple
        '''
        return tuple[1]

    def ranking_rel(self) -> List:
        '''
        Returns sorted list of tuples of id and relevance scores in ascending
        order

        Parameters: 
        tuple

        Returns: 
        sorted list of tuples of id and relevance scores in ascending order
        '''
        return sorted(list(self.id_to_rel_dict.items()), \
            key=self.return_val,reverse=True)

    def handle_printing(self, curr_list) -> None:
        '''
        Prints the top 10 results

        Parameters: 
        curr_list - a sorted list tuples of id and relevance scores in 
        ascending order

        Returns: 
        None
        '''
        num_element = min(10, len(curr_list))
        for i in range(num_element):
            print("\t" + f"{i+1}" + " " + \
                self.id_to_title_dict[curr_list[i][0]])

    
if __name__ == "__main__":
    '''
        Main method of Querier class. If there are 5 arguments, then user
        wants to include pagerank in computing the rank. Otherwise, there will
        be 4 inputs. If user passes less or more than 3 or 4 input words,
        prints out the informative message

        Parameters:
        None

        Returns: 
        None
        '''
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