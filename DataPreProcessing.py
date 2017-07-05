# -*- coding: utf-8 -*-

import numpy as np
import copy
from ReadBulletScreen import BulletScreen
from collections import OrderedDict
try:
    import cPickle as pickle
except ImportError:
    import pickle

# def grab_slice_number(self):
#         fr = open("data/var/slice_number", "rb")
#         slice_number = pickle.load(fr)
#         fr.close()
#         return slice_number
#

class DataPreProcessing(object):
    def __init__(self):
        self.docSet=[]
        self.docSize=[]



    def _proxy_(self, file_name, POS_tag):
        self.lines, vocabulary = BulletScreen().run(file_name, POS_tag)
        vocabulary_list=[]
        _vocabulary=copy.copy(vocabulary)
        for line in self.lines:
            for item in line["text"]:
                if item in _vocabulary:
                    _vocabulary[item]=1
            vocabulary_list.append(list(_vocabulary.values()))
        self.print_raw_comment(self.lines)
        return self.lines,np.array(vocabulary_list),len(vocabulary),vocabulary



    def print_raw_comment(self,lines):
        with open("data/raw.txt","w") as f:
            for line in lines:
                f.write(" ".join(line["text"])+"\n")



# def store_docset(docSet):
#         fw = open("data/cache/docSet", "wb")
#         pickle.dump(docSet, fw)
#         fw.close()



if __name__=="__main__":

    file_name = "data/danmu/1.xml"
    POS_tag = ["m", "w", "g", "c", "o", "p", "z", "q", "un", "e", "r", "x", "d", "t", "h", "k", "y", "u", "s", "uj",
               "ul","r", "eng"]
    lines=DataPreProcessing()._proxy_(file_name,POS_tag)

    # lines
    # [{'lineno': 2041, 'time': 0, 'text': ['小伙伴', '你们好']}, {'lineno': 2729, 'time': 0, 'text': ['伪装', '着看', '完']}, {'lineno': 4227, 'time': 0, 'text': ['僵尸', '极品']},


