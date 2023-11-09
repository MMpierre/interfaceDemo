import argparse
import elasticsearch
import pandas as pd
from .imports.getProfilVectors import getProfilVectors
from .imports.computeScore import compute_scores
from .imports.outputFormat import outputFormat
import streamlit as st
import json
# Input - ID de la mission
# Output - ID des profils + scores


def P2Jsearch(id:str, n:int, expected:int, geo:tuple, distance:int) -> pd.DataFrame:
    es = getElasticClient()
    vecs = getProfilVectors(id, es, st.secrets["profilIndex"])
    
    if len(vecs) > 0:
        if len(vecs) < expected:
            st.warning(f'Attention ! nous avons récupéré uniquement {len(vecs)} vecteur(s) pour {expected} expériences')
        
        requests = []
        for vec in vecs:
            header = {"index": st.secrets["jobIndex"]}
            body = {
                "query": {"match_all": {}},
                "_source": ["id"],
                "size": n,
                "knn": {
                    "field": "vector",
                    "query_vector": vec,
                    "k": n,
                    "num_candidates": n
                }
            }
            if geo:
                body["post_filter"] = {"bool": {
                            "must": [
                                {"geo_distance": { "distance": distance,
                                                    "address__geolocation__0": {
                                                            "lon": geo[0],
                                                            "lat": geo[1] }}}
                                                            ]}}
            requests.append(json.dumps(header))
            requests.append(json.dumps(body))
        
        # Join the requests with newline characters and add a final newline character at the end
        msearch_request_body = '\n'.join(requests) + '\n'
        
        # Perform the multi-search request
        msearch_response = es.msearch(body=msearch_request_body)
        
        if len(msearch_response["responses"][0]["hits"]["hits"])==0:
            warning = True
            st.warning("Pas d'offres dans votre région")
            body = {
                "query": {"match_all": {}},
                "_source": ["id"],
                "size": n,
                "knn": {
                    "field": "vector",
                    "query_vector": vec,
                    "k": n,
                    "num_candidates": n
                }
            }
            requests.append(json.dumps(header))
            requests.append(json.dumps(body))
            msearch_request_body = '\n'.join(requests) + '\n'
            msearch_response = es.msearch(body=msearch_request_body)
        hits = []
        for response in msearch_response['responses']:
            hits += response["hits"]["hits"]
            
        score_df = compute_scores(hits, n)
        return outputFormat(score_df)
    else:
        st.error("Pas de vecteur pour ce profil sur ElasticSearch")
        return pd.DataFrame()


  
def P2Jsearch_Liked(id:str,n:int,expected:int,likedIds:list)->pd.DataFrame:

    es = getElasticClient()
    vecs = getProfilVectors(id,es,st.secrets["profilIndex"])
    if len(vecs)>0:
        if len(vecs)<expected:
            st.warning(f'Attention ! nous avons récupéré uniquement {len(vecs)} vecteur(s) pour {expected} expériences')
        

        hits = []
        for vec in vecs:
            query = {"bool": {"must": [ {"ids": {"values": likedIds}}]}}

            knn = {"field": "vector",
                    "query_vector": vec,
                    "k": st.session_state.n,
                    "num_candidates": st.session_state.n}
            res = es.search(index=st.secrets["jobIndex"], query=query, source=["id"], knn = knn,size=st.session_state.n )
            hits += res["hits"]["hits"]
 
        score_df = compute_scores(hits,n)
        return outputFormat(score_df)
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

