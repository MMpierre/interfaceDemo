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
    requests = []
    for i in range(0, 3):
        header = {"index": st.secrets["profilIndex"]}
        body = {
            "query": query,
            "_source": ["id"],  # Assuming you only need the 'id' field
            "size": n,  # Ensure you only retrieve 'n' results
            "knn": {
                "field": f"experience__occupation__vector__{i}",
                "query_vector": vec,
                "k": n,
                "num_candidates": n
            }
        }
        requests.append(json.dumps(header))  # Header is added as a JSON string
        requests.append(json.dumps(body))  # Body is added as a JSON string

    # Join the requests with newline characters and add a final newline character at the end
    msearch_request_body = '\n'.join(requests) + '\n'

    # Perform the multi-search request
    res = es.msearch(body=msearch_request_body)

    # Parse the results
    # The response will contain a 'responses' array with individual search results
    all_hits = []
    for response in res['responses']:
        all_hits += response['hits']['hits']
    scores = compute_scores(all_hits,n)
    return outputFormat(scores)


def J2Psearch_liked(id:str,n:int,likedIds:list)->pd.DataFrame:
    
    res = []
    query = {"bool": {"must": [ {"ids": {"values": likedIds}}]}}

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
        
        res += es.search(index=st.secrets["profilIndex"], query=query, source=["id"], knn = knn)["hits"]["hits"]

    scores = compute_scores(res,n)
    return outputFormat(scores)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that takes an argument.")
    parser.add_argument("id", type=str, help="The id of the mission")
    parser.add_argument("n", type=int, help="The number of profiles to return")
    args = parser.parse_args()

    print(json.dumps(J2Psearch(args.id,args.n)))

