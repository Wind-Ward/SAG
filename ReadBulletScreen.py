# -*- coding: utf-8 -*-

import re
import jieba
import jieba.posseg as pseg
import copy



class BulletScreen(object):
    def __init__(self):
        self.stop_words= set([
                    " ","the","of","is","and","to","in","that","we","for",\
                    "an","are","by","be","as","on","with","can","if","from","which","you",
                    "it","this","then","at","have","all","not","one","has","or","that","什么","一个"
                    ])

    #处理停用词
    '''
        *function name : load_stop_words
        *输入参数:
        	-file : 停用词表文件
        *函数功能:
        	-读取停用词文件，添加停用词
        '''
    def load_stop_words(self,file="data/metadata/stopWords.txt"):
        f = open(file)
        content = f.read()
        words = content.split('\n')
        for w in words:
            self.stop_words.add(w.strip())



    '''
        *function name : sliceWithTime
        *输入参数:
        	-file_name : 要分析的视频的文件名
        	-POS_tag:用于jieba分词的词性过滤
        *输出:
        	-lines:  返回格式：[{'text': [u'伪装', u'着看', u'完', u'僵尸', u'王'], 'lineno': 2729, 'time': 0}, {'text': [u'欢乐颂', u'取', u'汁源', u'诚信', u'发'],'lineno': 5307, 'time': 0},
        	        每一个弹幕为对一个dict，记录了弹幕所在视频文件中的行号（lineno），在弹幕中出现的时间（time），以及内容（text）
        	-vocabulary: 返回的一个单词表（用于以后的分析）
        *函数功能:
        	-将弹幕文件中的有效弹幕提取出来，提取出的有效弹幕已经排序、分词完毕
        '''
    def read(self,file_name,POS_tag):
        f = open(file_name, "r")
        tempLine=[]
        vocabulary = {}
        jieba.load_userdict("data/metadata/user_dict.txt")
        for lineNo,line in enumerate(f.readlines()):
            pattern=re.compile("^<d p=\"(.+)\">(.+)</d>")
            m=pattern.match(line)
            if m:
                temp={"time":int(float(m.group(1).split(',')[0])), \
                                   "text":[word  for word,flag in pseg.cut(m.group(2))  \
                                           if word not in self.stop_words and flag not in \
                                           POS_tag ],
                                   "lineno":lineNo+1}


                #提取有效弹幕 有效弹幕为长度>3的弹幕
                if len(temp["text"])>1:
                    tempLine.append(temp)
                    for item in temp["text"]:
                        if item not in vocabulary:
                            vocabulary[item]=0

        lines=sorted(tempLine, key= lambda e:(e.__getitem__('time')))
        return lines,vocabulary

    '''
        *function name : sliceWithTime
        *输入参数:
        	-file_name : 要分析的视频的文件名
        	-POS_tag:用于jieba分词的词性过滤
        *输出:
        	-lines:  返回格式：[{'text': [u'伪装', u'着看', u'完', u'僵尸', u'王'], 'lineno': 2729, 'time': 0}, {'text': [u'欢乐颂', u'取', u'汁源', u'诚信', u'发'],'lineno': 5307, 'time': 0},
        	        每一个弹幕为对一个dict，记录了弹幕所在视频文件中的行号（lineno），在弹幕中出现的时间（time），以及内容（text）
        	-vocabulary: 返回的一个单词表（用于以后的分析）
        *函数功能:
        	-执行self.load_stop_words()以及self.read(file_name,POS_tag)函数
    '''
    def run(self,file_name,POS_tag):
        self.load_stop_words()
        return  self.read(file_name,POS_tag)



if __name__=="__main__":
    # 所要分析的弹幕文件
    file_name = "data/1.xml"
    # 采用词性过滤的方式来过滤对弹幕挖掘没有实际意义的词 具体可查 http://www.cnblogs.com/adienhsuan/p/5674033.html
    POS_tag = ["m", "w", "g", "c", "o", "p", "z", "q", "un", "e", "r", "x", "d", "t", "h", "k", "y", "u", "s", "uj",
               "ul",
               "r", "eng"]
    print(BulletScreen().run(file_name,POS_tag))
    #lines
    #[{'lineno': 2041, 'time': 0, 'text': ['小伙伴', '你们好']}, {'lineno': 2729, 'time': 0, 'text': ['伪装', '着看', '完']}, {'lineno': 4227, 'time': 0, 'text': ['僵尸', '极品']},



