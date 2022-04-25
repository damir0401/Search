from turtle import distance
from xmlrpc.client import Boolean
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words('english'))
from nltk.stem import PorterStemmer


def query(pagerank: bool, titleIndex: dict, docIndex: dict, wordIndex: dict):
    while True:
        phrase = input("search phrase:")
        word_list = phrase.split(" ")
        stemmer = PorterStemmer()
        for word in word_list:
            if not(word in STOP_WORDS):
                word_list.remove(word)
            stemmer.stem(word)
        if phrase == ":quit":
            exit()    
    pass

def query(titleIndex: dict, docIndex: dict, wordIndex: dict):
    while True:
        phrase = input("search phrase:")
        word_list = phrase.split(" ")
        stemmer = PorterStemmer()
        for word in word_list:
            if not(word in STOP_WORDS):
                word_list.remove(word)
            stemmer.stem(word)
        if phrase == ":quit":
            exit()