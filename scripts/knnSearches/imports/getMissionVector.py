import elasticsearch
import torch

def getMissionVector(id:str,es:elasticsearch.Elasticsearch,index:str)->torch.Tensor:
    query = {"match": {
            "_id": id }}
    res = es.search(index=index, query=query, source=["vector"])["hits"]["hits"]
    return res[0]["_source"]["vector"]