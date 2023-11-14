import argparse
import elasticsearch
import pandas as pd
from .imports.ESquery import get_geo_matching_users,construct_profile_search_request
from .imports.getMissionVector import getMissionVector
from .imports.computeScore import compute_scores
from .imports.outputFormat import outputFormat
import json
import streamlit as st
import time
# Input - ID de la mission
# Output - ID des profils + scores


def J2Psearch(id:str,n:int,geo)->pd.DataFrame:

    es =  elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)       
    vec = getMissionVector(id,es,st.secrets["jobIndex"])

    if geo:
        with st.spinner("Récupération des Users dans la région ..."):
            geo_ids = get_geo_matching_users(es,st.secrets["profilIndex"],geo)
            st.warning("La recherche par location dans ce sens peut présenter des erreurs.")
        if len(geo_ids)==0:
            st.warning("Pas d'users dans votre région")

    requests = []
    for i in range(0, 3):
        header,body = construct_profile_search_request(vec,f"experience__occupation__vector__{i}",st.secrets["profilIndex"],n)
        if geo and len(geo_ids)>0:
                body["knn"]["filter"] =  {"bool": {"must": [ {"ids": {"values": geo_ids}}]}}
                body["size"] = min(len(geo_ids),n)            
        requests.append(json.dumps(header))  # Header is added as a JSON string
        requests.append(json.dumps(body))  # Body is added as a JSON string

    # Join the requests with newline characters and add a final newline character at the end
    with st.spinner("Calcul des meilleurs profils ..."):
        msearch_request_body = '\n'.join(requests) + '\n'

    # Perform the multi-search request
    msearch_response = es.msearch(body=msearch_request_body)

    hits = [hit for response in msearch_response['responses'] for hit in response["hits"]["hits"]]

    scores = compute_scores(hits,n)
    return scores.loc[:,["_id","_score","city"]]




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that takes an argument.")
    parser.add_argument("id", type=str, help="The id of the mission")
    parser.add_argument("n", type=int, help="The number of profiles to return")
    args = parser.parse_args()

    print(json.dumps(J2Psearch(args.id,args.n)))

