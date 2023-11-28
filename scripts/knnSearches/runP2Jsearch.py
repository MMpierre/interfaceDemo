import argparse
import elasticsearch
import pandas as pd
from .imports.getProfilVectors import getProfilVectors
from .imports.computeScore import compute_scores
from .imports.outputFormat import outputFormat
from .imports.ESquery import *
import streamlit as st
import json

@st.cache_data(ttl=600,show_spinner=False)
def P2Jsearch(id:str, n:int, expected:int, geo:tuple, distance:int) -> pd.DataFrame:
    es = getElasticClient()
    vecs = getProfilVectors(id, es, st.secrets["profilIndex"],expected)

    if len(vecs) > 0:
        requests = []
        if geo:
            with st.spinner("Récupération des missions dans la région ..."):
                geo_ids = get_geo_matching_missions(es,st.secrets["jobIndex"],geo,distance)
            if len(geo_ids)==0:
                st.warning("Pas d'offres dans votre région")

        for vec in vecs:
            header, body = construct_mission_search_request(vec,st.secrets["jobIndex"],n)
            if geo and len(geo_ids)>0:
                body["knn"]["filter"] =  {"bool": {"must": [ {"ids": {"values": geo_ids}}]}}
                body["size"] = min(len(geo_ids),n)
            requests.append(json.dumps(header))
            requests.append(json.dumps(body))
        
        # Join the requests with newline characters and add a final newline character at the end
        msearch_request_body = '\n'.join(requests) + '\n'
        with st.spinner("Calcul des meilleures offres ..."):
            # Perform the multi-search request
            msearch_response = es.msearch(body=msearch_request_body)

        hits = [hit for response in msearch_response['responses'] for hit in response["hits"]["hits"]]
     
        score_df = compute_scores(hits,n)
        return score_df.loc[:,["_id","_score","exp","city"]]
    else:
        st.error("Pas de vecteur pour ce profil sur ElasticSearch")
        return None
  
def P2Jsearch_Liked(id:str,n:int,expected:int,likedIds:list)->pd.DataFrame:

    es = getElasticClient()
    vecs = getProfilVectors(id,es,st.secrets["profilIndex"],expected)
    if len(vecs)>0:
        

        requests = []
        for vec in vecs:
            header,body = construct_mission_search_request(vec,st.secrets["jobIndex"],n)
            body["query"] = {"bool": {"must": [ {"ids": {"values": likedIds}}]}}
            requests.append(json.dumps(header))
            requests.append(json.dumps(body))
        msearch_request_body = '\n'.join(requests) + '\n'
        
        # Perform the multi-search request
        msearch_response = es.msearch(body=msearch_request_body)

        hits = [hit for response in msearch_response['responses'] for hit in response["hits"]["hits"]]

        score_df = compute_scores(hits,n)
        return score_df.loc[:,["_id","_score","exp"]]
    else:
        st.error("Pas de vecteur pour ce profil sur ElasticSearch")
        return("[]")

def getElasticClient():
    return elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)   
      
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that takes an argument.")
    parser.add_argument("id", type=str, help="The id of the profile")
    parser.add_argument("n", type=int, help="The number of profiles to return")
    args = parser.parse_args()

    print(P2Jsearch("mirrored/" + args.id,args.n))

