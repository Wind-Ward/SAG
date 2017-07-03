# -*- coding: utf-8 -*-

import numpy as np
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


    def addRestComment(self):
        doc=[]
        while (len(self.lines) != 0):
                doc.append(self.lines[0]["text"])
                self.lines.pop(0)
        self.docSet.append(doc)


    def sliceWithTime(self,timeInterval,file_name,time_length,POS_tag):
        self.lines,vocabulary=BulletScreen().run(file_name,POS_tag)
        preTime=0
        lastTime=preTime+timeInterval
        for index in range(int(time_length/timeInterval)):
            doc =[]
            number=0
            while(len(self.lines)!=0):
                if self.lines[0]["time"] <=lastTime:
                    doc.append(self.lines[0]["text"])
                    self.lines.pop(0)
                    number+=1
                else:
                    preTime=lastTime
                    lastTime=preTime+timeInterval
                    self.docSet.append(doc)
                    self.docSize.append(number)
                    doc=[]
                    break

        self.addRestComment()
        return self.docSet,self.docSize


def print_raw_comment(docSet):
    with open("data/raw.txt","w") as f:
        for shot in docSet:
            for comment in shot:
                f.write(" ".join(comment)+"\n")


def store_docset(docSet):
        fw = open("data/cache/docSet", "wb")
        pickle.dump(docSet, fw)
        fw.close()


#返回格式
#[[u'伪装', u'着看', u'完', u'僵尸', u'王', u'欢乐颂', u'取', u'汁源', u'诚信', u'发', u'全集', u'私', u'私', u'威信', u'来来来', u'欢乐颂', u'全集', u'超清', u'微信', u'欢乐颂',
if __name__=="__main__":
    #时间片大小、单位秒
    timeInterval = 100
    # 所要分析的弹幕文件
    file_name = "data/1.xml"
    # 所要分析弹幕文件的时间长度
    time_length = 2582
    # 采用词性过滤的方式来过滤对弹幕挖掘没有实际意义的词 具体可查 http://www.cnblogs.com/adienhsuan/p/5674033.html
    POS_tag = ["m", "w", "g", "c", "o", "p", "z", "q", "un", "e", "r", "x", "d", "t", "h", "k", "y", "u", "s", "uj",
               "ul","r", "eng"]
    docSet,docSize=DataPreProcessing().sliceWithTime(timeInterval,file_name,time_length,POS_tag)
    print(docSize)
    print_raw_comment(docSet)
    store_docset(docSet)
    print(docSet)



