# -*- coding: utf-8 -*-
from DataPreProcessing import DataPreProcessing
from gensim.models import word2vec
import logging
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

POS_tag = ["m", "w", "g", "c", "o", "p", "z", "q", "un", "e", "r", "x", "d", "t", "h", "k", "y", "u", "s", "uj",
           "ul", "r", "eng"]

def print_all_raw(root="data/danmu"):
    with open("data/raw_all.txt","w") as f:
        for i in os.listdir(root):
            print("i")
            print(i)
            lines,vocabulary_list,vocabulary_size,vocabulary= DataPreProcessing()._proxy_("data/danmu/"+i, POS_tag)
            for line in lines:
                f.write(" ".join(line["text"]) + "\n")

def store_word2vec_calc(file="data/raw_all.txt"):
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
    sentences = word2vec.Text8Corpus(file)  # 加载语料
    model = word2vec.Word2Vec(sentences, size=300,min_count=1)
    fw = open("data/cache/word2vec_model", "wb")
    pickle.dump(model, fw)
    fw.close()


if __name__ == '__main__':
    #print_all_raw()
    store_word2vec_calc()
