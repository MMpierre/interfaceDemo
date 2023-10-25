import argparse
import elasticsearch
import pandas as pd
from .imports.P2J_imports import getProfilVectors,compute_scores
import streamlit as st
# Input - ID de la mission
# Output - ID des profils + scores


####PARAMETERS######

EB = 2  # Experience bonus (%)
RB = 2  # Recency bonus (%)
SB = 2  # Secondary jobs bonus (%)



def P2Jsearch(id:str,n:int,expected:int,geo:tuple,distance:int)->pd.DataFrame:

    es =  elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)      
    vecs = getProfilVectors(id,es,st.secrets["profilIndex"])
    if len(vecs)>0:
        if len(vecs)<expected:
            st.warning(f'Attention ! nous avons récupéré uniquement {len(vecs)} vecteur(s) pour {expected} expériences')
        

        hits = []
        aggs = []
        for vec in vecs:
            query = {"match_all": {}}
            knn = {"field": "vector",
                    "query_vector": vec,
                    "k": 50,
                    "num_candidates": 50}
            if geo:
                filter = {"bool": {
                            "must": [
                                {"geo_distance": { "distance": distance,
                                                    "geolocation": {
                                                            "lon": geo[0],
                                                            "lat": geo[1] }}}
                                                            ]}}
                
                res = es.search(index=st.secrets["jobIndex"], query=query, source=["id"],post_filter=filter, knn = knn,size=50)["hits"]["hits"]
            else:
                res = es.search(index=st.secrets["jobIndex"], query=query, source=["id"], knn = knn,size=50)
                hits += res["hits"]["hits"]

        return compute_scores(hits,n)
    else:
        st.error("Pas de vecteur pour ce profil sur ElasticSearch")
        return("[]")

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that takes an argument.")
    parser.add_argument("id", type=str, help="The id of the profile")
    parser.add_argument("n", type=int, help="The number of profiles to return")
    args = parser.parse_args()

    print(P2Jsearch("mirrored/" + args.id,args.n))

