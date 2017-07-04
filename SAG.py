import numpy as np
from gensim.models import word2vec
import logging
try:
    import cPickle as pickle
except ImportError:
    import pickle
from DataPreProcessing import DataPreProcessing
from operator import itemgetter, attrgetter

file_name = "data/1.xml"
POS_tag = ["m", "w", "g", "c", "o", "p", "z", "q", "un", "e", "r", "x", "d", "t", "h", "k", "y", "u", "s", "uj",
               "ul","r", "eng"]

# def grab_docset():
#         fr = open("data/cache/docset", "rb")
#         docset = pickle.load(fr)
#         fr.close()
#         return docset



def cos_distance(vector1,vector2):
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

class Vertice(object):
    def __init__(self):
        self.S=set()
        self.time=None
        self.index=0
        self.comment=None
        self.sentence_vec=None

class Edge(object):
    def __init__(self):
        self.x=None
        self.y=None
        self.w=None

class SAGModel(object):

    def __init__(self):
        self.vertice_list=[]
        self.edge_list=[]
        self.edge_dict={}
        self.gamma_t=0.11
        self.rio=0.36
        #self.comment_popularity=[]



    def word2vec_calc(self,file="data/raw.txt"):
        logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
        sentences = word2vec.Text8Corpus(file)  # 加载语料
        model = word2vec.Word2Vec(sentences, size=300,min_count=1)
        return model


    def _initialize_vertice(self,word_2_vec):
        lines,self.vocabulary_list=DataPreProcessing()._proxy_(file_name,POS_tag)
        self.N=len(lines)
        for index,line in enumerate(lines):
            v=Vertice()
            v.S.add(index)
            v.time,v.index,v.comment =line["time"],index,line["text"][:]
            #calc mean sentence vector by word2vec
            total=np.zeros(300)
            for item in line["text"]:
                total+=word_2_vec[item]
            v.sentence_vec=total/len(line["text"])
            self.vertice_list.append(v)

        return self.vertice_list


    def _initialize_edge(self):
        for i,vertice in enumerate(self.vertice_list):
            for j in range(i+1,len(self.vertice_list)):
                e=Edge()
                e.x=i
                e.y=j
                e.w=cos_distance(vertice.sentence_vec,self.vertice_list[j].sentence_vec)\
                    *np.exp(-1*self.gamma_t*(np.abs(vertice.time-self.vertice_list[j].time)))
                if e.w>=0.3:
                    self.edge_list.append(e)
                    self.edge_dict[str(i)+","+str(j)]=e
        self.edge_list=sorted(self.edge_list,key=attrgetter('w'),reverse=True)

    def initialize(self):
        word_2_vec = self.word2vec_calc()
        self._initialize_vertice(word_2_vec)
        self._initialize_edge()


    def _calc_S_size(self):
        S_dict={}
        for vertice in self.vertice_list:
            _key=",".join([str(v) for v in list(vertice.S)])
            if _key in S_dict:
                S_dict[_key] +=1
            else:
                S_dict[_key]=0
        return S_dict

    def _calc_popularity(self):
        comment_popularity=[]
        S_dict=self._calc_S_size()
        total=1
        for item in S_dict.values():
            total*=item
        _denumberator=np.power(total,1/len(S_dict))
        for vertice in self.vertice_list:
            comment_popularity.append(len(vertice.S)/_denumberator)
        return np.array(comment_popularity)


    def _cacl_M_n(self):
        m=np.zeros((self.N,self.N))
        for i in range(0,self.N):
            for j in range(0,self.N):
                if self.vertice_list[i].S == self.vertice_list[j].S and i!=j:
                    if str(i)+","+str(j) in self.edge_dict:
                        m[i][j]=self.edge_dict[str(i)+","+str(j)].w


    def _calc_I(self):
        I=np.ones(21,self.N)
        for k in range(1,11):
            for i in range(self.N-1,-1,-1):
                if i==self.N-1:
                    I[2 * k - 1][i] = I[2 * k - 2][i]
                else:
                    total=0
                    for j in range(i+1,self.N):
                        total+=self.m[i][j]*I[2*k-1][j]
                    I[2 * k - 1][i] = I[2 * k - 2][i]+total

            for i in range(0,self.N):
                if i==0:
                    I[2*k][i]=I[2*k-1][i]/(I[2*k-1][i])
                else:
                    total=0
                    for j in range(1,i):
                        total+=self.m[j][i]*I[2*k][j]
                    I[2*k][i]=I[2*k-1][i]/(I[2*k-1][i]+total)

        return I[20]

    def _calc_SW_IDF(self):




    def _tag_extraction(self):
        self.initialize()
        for i,edge in enumerate(self.edge_list):
            s_all=list(self.vertice_list[edge.x].S|self.vertice_list[edge.y].S)
            total=0.0
            for i,item in enumerate(s_all):
                for j in range(i+1,len(s_all)):
                    i_j=str(i)+","+str(j)
                    if i_j in self.edge_dict:
                        total+=self.edge_dict[i_j].w
            if total/(len(s_all)*((len(s_all)-1)/2))>self.rio:
                self.vertice_list[edge.x].S=s_all
                self.vertice_list[edge.y].S=s_all

        self._cacl_M_n()
        P=self._calc_popularity()
        I=self._calc_I()
        W=P*I
        self._calc_SW_IDF()







if __name__ == '__main__':
    SAGModel()._tag_extraction()



