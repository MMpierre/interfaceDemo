import requests
import streamlit as st
import json
from elasticsearch import Elasticsearch


def fetch_all_missions(es):
    # Initial search
    query = {
            "bool": {
                "filter": {
                    "exists": {
                        "field": "vector"
                    }
                }
            }
        }
    
    res = es.search(index=st.secrets["jobIndex"],size=100,source=["id","title__value"], query=query,scroll='1m')
    scroll_id = res['_scroll_id']
    scroll_size = len(res['hits']['hits'])
    
    all_missions = [profile["_source"] for profile in res["hits"]["hits"]]
    # Continue scrolling until no more results
    # while scroll_size > 0:
    #     res = es.scroll(scroll_id=scroll_id, scroll='1m')
    #     all_missions.extend([profile["_id"] for profile in res["hits"]["hits"]])
    #     scroll_size = len(res['hits']['hits'])
    
    return all_missions

def fetch_mission_data(mission_id,es):

    query = {  "match": {
            "_id": mission_id}}
    res = es.search(index=st.secrets["jobIndex"], query=query, source_excludes=["vector"])["hits"]["hits"][0]["_source"]
    return res

if __name__ == "__main__":
    print(fetch_all_missions(Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)))
