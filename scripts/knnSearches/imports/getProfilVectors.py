import elasticsearch
import streamlit as st

def getProfilVectors(id:str,es:elasticsearch.Elasticsearch,index:str,expected):
    query = {  "match": {
            "_id": id}}
    res = es.search(index=index, query=query, source=[f"experience__occupation__vector__{i}" for i in range(3)])["hits"]["hits"]
    vecs = [res[0]["_source"][vecteur] for vecteur in res[0]["_source"].keys()]
    if len(vecs) < expected:
        st.warning(f'Attention ! nous avons récupéré uniquement {len(vecs)} vecteur(s) pour {expected} expériences')
    return vecs
