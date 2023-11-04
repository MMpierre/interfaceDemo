import argparse
import elasticsearch
import pandas as pd
from .imports.getMissionVector import getMissionVector
from .imports.computeScore import compute_scores
from .imports.outputFormat import outputFormat
import json
import streamlit as st
import time
# Input - ID de la mission
# Output - ID des profils + scores


def J2Psearch(id:str,n:int)->pd.DataFrame:
    
    res = []
    query = {"match_all": {}}

    es =  elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)       
    vec = getMissionVector(id,es,st.secrets["jobIndex"])
    
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

    for i in range (0,3):

        knn = {"field": f"experience__occupation__vector__{i}",
                "query_vector": vec,
                "k": n,
                "num_candidates": n}
        # getOtherScores(es.search(index=st.secrets["profilIndex"], query=query, source=["id"], knn = knn)["hits"]["hits"],es,st.secrets["profilIndex"],vec,n,i)
        res += es.search(index=st.secrets["profilIndex"], query=query, source=["id"], knn = knn)["hits"]["hits"]

    scores = compute_scores(res,n)
    return outputFormat(scores)

from elasticsearch import Elasticsearch

def getOtherScores(search_results, es, index, vec, n,numero):
    extended_results = {}
    
    for result in search_results:
        user_id = result["_source"]["id"]
        scores = {}
        
        for i in set([0,1,2]).difference(set([numero])): 
            knn = {
                "field": f"experience__occupation__vector__{i}",
                "query_vector": vec,
                "k": 1,
                "num_candidates": 1
            }
            query = { "match": {
                        "_id": user_id}} # Query by ID
            
            # Run the search
            res = es.search(index=index, query=query, knn=knn)
            
            # Store the similarity score for this particular field
            if res["hits"]["hits"]:
                scores[f"vector__{i}"] = res["hits"]["hits"][0]["_score"]
        
        # Store the additional similarity results for this user_id
        extended_results[user_id] = scores
    
    return extended_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that takes an argument.")
    parser.add_argument("id", type=str, help="The id of the mission")
    parser.add_argument("n", type=int, help="The number of profiles to return")
    args = parser.parse_args()

    print(json.dumps(J2Psearch(args.id,args.n)))

