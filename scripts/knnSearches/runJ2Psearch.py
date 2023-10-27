import torch
import argparse
import elasticsearch
import yaml
import pandas as pd
from .imports.getMissionVector import getMissionVector
from .imports.computeScore import compute_scores_J2P
from .imports.outputFormat import outputFormat
import json
import streamlit as st
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

    for i in range (1,4):

        knn = {"field": f"experience__occupation__vector__{i}",
                "query_vector": vec,
                "k": 50,
                "num_candidates": 50}
        res += es.search(index=st.secrets["profilIndex"], query=query, source=["id"], knn = knn,size=50)["hits"]["hits"]
    scores = compute_scores_J2P(res,n)
    return outputFormat(scores)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that takes an argument.")
    parser.add_argument("id", type=str, help="The id of the mission")
    parser.add_argument("n", type=int, help="The number of profiles to return")
    args = parser.parse_args()

    print(json.dumps(J2Psearch(args.id,args.n)))

