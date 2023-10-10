import argparse
import elasticsearch
import yaml
import pandas as pd
from .imports.P2J_imports import getProfilVectors,compute_scores
# Input - ID de la mission
# Output - ID des profils + scores


####PARAMETERS######

EB = 2  # Experience bonus (%)
RB = 2  # Recency bonus (%)
SB = 2  # Secondary jobs bonus (%)




def J2Psearch(id:str,n:int)->pd.DataFrame:
    query = {"match_all": {}}

    config = yaml.safe_load(open("config.yaml", 'r'))
    es = elasticsearch.Elasticsearch(cloud_id=config["elastic_search"]["cloud_id"], api_key=(config["elastic_search"]["api_key_1"],config["elastic_search"]["api_key_2"]),request_timeout=300)  # 5 minute timeout
    
    vecs = getProfilVectors(id,es,config["elastic_search"]["profilIndex"])

    res = []
    # filter = {"bool": {
    #                 "must": [
    #                     {"geo_distance": { "distance": DISTANCEMAX+"km",
    #                                  "location": {
    #                                         "lon": LONGITUDE,
    #                                         "lat": LATTITUDE }    }},  
    #                     {"range": { "experienceMinimum": {
    #                                  "lt": EXPERIENCE } }},
    #                     {"range": { "educationLevel": {
    #                                   "lte" : EDUCATION}} }]} }
    for vec in vecs:
        knn = {"field": f"vector",
                "query_vector": vec,
                "k": 50,
                "num_candidates": 50}
        res += es.search(index=config["elastic_search"]["jobIndex"], query=query, source=["id"], knn = knn,size=50)["hits"]["hits"]
    return compute_scores(res,n)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that takes an argument.")
    parser.add_argument("id", type=str, help="The id of the profile")
    parser.add_argument("n", type=int, help="The number of profiles to return")
    args = parser.parse_args()

    print(J2Psearch(args.id,args.n))

