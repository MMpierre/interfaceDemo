import argparse
import elasticsearch
import pandas as pd
from .imports.getProfilVectors import getProfilVectors
from .imports.computeScore import compute_scores
from .imports.outputFormat import outputFormat
import streamlit as st
# Input - ID de la mission
# Output - ID des profils + scores




def P2Jsearch(id:str,n:int,expected:int,geo:tuple,distance:int)->pd.DataFrame:

    es = getElasticClient()
    vecs = getProfilVectors(id,es,st.secrets["profilIndex"])
    if len(vecs)>0:
        if len(vecs)<expected:
            st.warning(f'Attention ! nous avons récupéré uniquement {len(vecs)} vecteur(s) pour {expected} expériences')
        

        hits = []
        warning = False
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
                                                    "address__geolocation__0": {
                                                            "lon": geo[0],
                                                            "lat": geo[1] }}}
                                                            ]}}
                
                res = es.search(index=st.secrets["jobIndex"], query=query, source=["id"],post_filter=filter, knn = knn,size=50)
                if len(res["hits"]["hits"]) == 0:
                    res = es.search(index=st.secrets["jobIndex"], query=query, source=["id"], knn = knn,size=50)
                    if not(warning):
                        warning = True            
                        st.warning("Pas d'offres dans votre région")
                hits += res["hits"]["hits"]
            else:
                res = es.search(index=st.secrets["jobIndex"], query=query, source=["id"], knn = knn,size=50)
                hits += res["hits"]["hits"]
        score_df = compute_scores(hits,n)
        return outputFormat(score_df)
    else:
        st.error("Pas de vecteur pour ce profil sur ElasticSearch")
        return("[]")

  
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
                    "k": 50,
                    "num_candidates": 50}
            res = es.search(index=st.secrets["jobIndex"], query=query, source=["id"], knn = knn,size=50)
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

