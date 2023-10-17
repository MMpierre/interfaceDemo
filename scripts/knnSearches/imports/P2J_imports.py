import elasticsearch
import torch
import pandas as pd

def getProfilVectors(id:str,es:elasticsearch.Elasticsearch,index:str)->torch.Tensor:
    query = {  "match": {
            "_id": id}}
    res = es.search(index=index, query=query, source=[f"experience__occupation__vector__{i}" for i in range(10)])["hits"]["hits"]
    return [res[0]["_source"][vecteur] for vecteur in res[0]["_source"].keys()]

#Formattage pour la sortie
def outputFormat(res:pd.DataFrame)->str:
    results = []
    for _,row in res.iterrows():
        result = {"id" : row["_id"],
                  "score" : row["_score"]}
        results.append(result)
    return(str(results))



def compute_scores(l:list,n:int)->pd.DataFrame:
    df = pd.DataFrame(l)
    df["_score"] *= 50
    return outputFormat(df.sort_values('_score',ascending=False).drop_duplicates(["_id"])[:n])

