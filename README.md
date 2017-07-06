# SAG
* SW-IDF(Semantic Weight-Inverse Document Frequency) generates corresponding semantic association graph (SAG) using semantic similarities and timestamps of the time-sync comments to extract videos tags from online video.
* The original paper is as follow:[***ROWDSOURCED TIME-SYNC VIDEO TAGGING USING SEMANTIC ASSOCIATION GRAPH***](http://csc.sjtu.edu.cn/doc/2017-3.pdf)
* The idea of paper is novel by using word2vec to cluster similar semantic TSC.And the result in my experiment is ok,however, this model costs much time to analysis TSCs.
* I have implemented several models which were used to extract topic or representative comment from TSCs.No one could work very well in real production environment. The next job is a long way to go.
## Dependency
* python3
* gensim
* jieba

## Run
```
python DAtaPreProcessing.py
python AllWord2Vec.py
python SAG.py
```
## Caveat
*This is a school project.If you have any question,please contact me by E-mail!*

## Author
WindWard <xuan619@sina.com>



