import elasticsearch
import torch

def getProfilVectors(id:str,es:elasticsearch.Elasticsearch,index:str)->torch.Tensor:
    query = {  "match": {
            "_id": id}}
    res = es.search(index=index, query=query, source=[f"experience__occupation__vector__{i}" for i in range(10)])["hits"]["hits"]
    return [res[0]["_source"][vecteur] for vecteur in res[0]["_source"].keys()]

