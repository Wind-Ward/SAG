import numpy as np
from gensim.models import word2vec
import logging
try:
    import cPickle as pickle
except ImportError:
    import pickle
from DataPreProcessing import DataPreProcessing
from operator import itemgetter, attrgetter

file_name = "data/1_test.xml"
POS_tag = ["m", "w", "g", "c", "o", "p", "z", "q", "un", "e", "r", "x", "d", "t", "h", "k", "y", "u", "s", "uj",
               "ul","r", "eng"]

def cos_distance(vector1,vector2):
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


def store_word2vec_calc(file="data/raw.txt"):
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
    sentences = word2vec.Text8Corpus(file)  # 加载语料
    model = word2vec.Word2Vec(sentences, size=300,min_count=1)
    fw = open("data/cache/word2vec_model", "wb")
    pickle.dump(model, fw)
    fw.close()


def grab_word2vec_calc():
    fr = open("data/cache/word2vec_model", "rb")
    model = pickle.load(fr)
    fr.close()
    return model


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
        self.tag_number=20
        #self.comment_popularity=[]
        self.T=20

    #check
    def _initialize_vertice(self,word_2_vec):
        lines,self.vocabulary_list,self.vocabulary_size,self.vocabulary=DataPreProcessing()._proxy_(file_name,POS_tag)
        self.N=len(lines)
        for index,line in enumerate(lines):
            v=Vertice()
            v.S.add(index)
            v.time,v.index,v.comment =line["time"],index,line["text"][:]
            #calc mean sentence vector by word2vec
            total=np.zeros(300)
            #print(line["text"])
            for item in line["text"]:
                total+=word_2_vec[item]
            v.sentence_vec=total/len(line["text"])
            self.vertice_list.append(v)
        #print(self.vertice_list)
        return self.vertice_list


    def _initialize_edge(self):
        for i,vertice in enumerate(self.vertice_list):
            for j in range(i+1,len(self.vertice_list)):
                e=Edge()
                e.x=i
                e.y=j
                e.w=cos_distance(vertice.sentence_vec,self.vertice_list[j].sentence_vec)\
                    *np.exp(-1*self.gamma_t*(np.abs(vertice.time-self.vertice_list[j].time)))
                print(e.w)
                if e.w>=0.3:
                    self.edge_list.append(e)
                    self.edge_dict[str(i)+","+str(j)]=e
        self.edge_list=sorted(self.edge_list,key=attrgetter('w'),reverse=True)
        # print("haha")
        # for item in self.edge_list:
        #     print(item.w)
        #     print(item.x)
        #     print(item.y)
        # #print(self.edge_list)
        # print("hehe")


    def initialize(self):
        word_2_vec = grab_word2vec_calc()
        self._initialize_vertice(word_2_vec)
        self._initialize_edge()


    def _calc_S_size(self):
        S_dict={}

        for vertice in self.vertice_list:
            print("vertice.S")
            print(list(vertice.S))
            _key=",".join([str(v) for v in sorted(list(vertice.S))])
            if _key in S_dict:
                S_dict[_key] +=1
            else:
                S_dict[_key]=1
        print (S_dict)
        return S_dict

    def _calc_popularity(self):
        comment_popularity=[]
        S_dict=self._calc_S_size()
        #print(len(S_dict))
        #print(list(S_dict.values()))
        total=1
        for item in S_dict.values():
            total*=item

        _denumberator=np.power(total,1/len(S_dict))
        #print(_denumberator)
        for vertice in self.vertice_list:
            comment_popularity.append(len(vertice.S)/_denumberator)
        print("popularity")
        print(comment_popularity)
        return np.array(comment_popularity)



    def _cacl_M_n(self):
        m=np.zeros((self.N,self.N))
        for i in range(0,self.N):
            for j in range(0,self.N):
                if self.vertice_list[i].S == self.vertice_list[j].S and i!=j:
                    if str(i)+","+str(j) in self.edge_dict:
                        m[i][j]=self.edge_dict[str(i)+","+str(j)].w
                    elif str(j)+","+str(i) in self.edge_dict:
                        m[i][j] = self.edge_dict[str(j) + "," + str(i)].w
        print("m")
        print(m)
        return m


    def _calc_I(self,m):
        I=np.zeros((2*self.T+1,self.N))
        I[0,:]=1

        for k in range(1,self.T+1):
            for i in range(self.N-1,-1,-1):
                if i==self.N-1:
                    I[2 * k - 1][i] = I[2 * k - 2][i]
                else:
                    total=0
                    for j in range(i+1,self.N):
                        total+=m[i][j]*I[2*k-1][j]
                    I[2 * k - 1][i] = I[2 * k - 2][i]+total

            for i in range(0,self.N):
                if i==0:
                    I[2*k][i]=I[2*k-1][i]/(I[2*k-1][i])
                else:
                    total=0
                    for j in range(0,i):
                        total+=m[j][i]*I[2*k][j]
                    I[2*k][i]=I[2*k-1][i]/(I[2*k-1][i]+total)
        print("I")
        print(I)
        print("I[20]")
        print(I[self.T*2])
        return I[self.T*2]


    def _calc_SW_IDF(self,W):
        result=[]
        for i in range(0,self.vocabulary_size):
            sum_w_j=0
            #print(self.vocabulary_size)
            for j in range(0,self.N):
                if self.vocabulary_list[j][i]>0:
                    sum_w_j+=W[j]
            #print(i)
            #print(self.vocabulary_list.shape)
            result.append((np.log(self.N/(1+np.sum(self.vocabulary_list[:,i])))*sum_w_j,i))
        return result

    def _tag_extraction(self):
        self.initialize()
        for i,edge in enumerate(self.edge_list):
            print("haha")
            print(self.vertice_list[edge.x].S)
            print(self.vertice_list[edge.y].S)
            print("hehe")
            s_all=list(self.vertice_list[edge.x].S | self.vertice_list[edge.y].S)
            #print(s_all)
            total=0.0
            for i,item in enumerate(s_all):
                for j in range(i+1,len(s_all)):
                    i_j=str(item)+","+str(s_all[j])
                    j_i = str(s_all[j]) + "," + str(item)
                    if i_j in self.edge_dict:
                        total+=self.edge_dict[i_j].w
                    elif j_i in self.edge_dict:
                        total += self.edge_dict[j_i].w

            if total/(len(s_all)*((len(s_all)-1)/2))>self.rio:
                self.vertice_list[edge.x].S|=set(s_all)
                self.vertice_list[edge.y].S|=set(s_all)

        m=self._cacl_M_n()
        P=self._calc_popularity()
        I=self._calc_I(m)
        W=P*I
        result=self._calc_SW_IDF(W)
        self._display_tag(result)

    def _display_tag(self,result):
        with open("data/result.txt","w") as f:
            # for item in sorted(result,key=lambda x:x[0],reverse=True)[:self.tag_number]:
            #print(sorted(result, key=lambda x: x[0], reverse=True))
            for item in sorted(result, key=lambda x: x[0], reverse=True)[:self.tag_number]:
                f.write(list(self.vocabulary.keys())[item[1]])
                f.write("\n")


if __name__ == '__main__':

    #store_word2vec_calc()
    SAGModel()._tag_extraction()



