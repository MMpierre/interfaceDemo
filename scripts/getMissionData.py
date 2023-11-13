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
    
    res = es.search(index=st.secrets["jobIndex"],size=100,source=["id","title__value","address__city__0"], query=query,scroll='1m')
    scroll_id = res['_scroll_id']
    scroll_size = len(res['hits']['hits'])
    
    all_missions = [profile["_source"] for profile in res["hits"]["hits"]]
    # Continue scrolling until no more results
    while scroll_size > 0:
        res = es.scroll(scroll_id=scroll_id, scroll='1m')
        all_missions.extend([profile["_source"] for profile in res["hits"]["hits"]])
        scroll_size = len(res['hits']['hits'])
    return all_missions


def fetch_mission_by_id(mission_id:list):
    
    url = st.secrets["graphQL"]
    detailed_query = """query User($missionsPromanId: [ID], $pagination: paginationInput) {
                            missionsProman(id: $missionsPromanId, pagination: $pagination) {
                                Mission {
                                id
                                agency {
                                    prefLabel {
                                    value
                                    }
                                }
                                area {
                                    prefLabel {
                                    value
                                    }
                                }
                                userLiked{
                                    id
                                }
                                contract {
                                    contractLengthUnit {
                                    value
                                    }
                                    contractLengthValue {
                                    value
                                    }
                                }
                                description {
                                    value
                                }
                                title {
                                    value
                                }
                                missionAddress {
                                    city {
                                    value
                                    }
                                    postalcode {
                                    value
                                    }
                                    geolocation {
                                    value
                                    }
                                }
                                url {
                                    value
                                }
                                sector {
                                    prefLabel {
                                    value
                                    }
                                id
                                }
                                }
                            }
                            }"""

    variables = {"missionsPromanId": mission_id,  
                 "pagination": { 
                    "limit": len(mission_id)
                                }}
    
    response = requests.post(url, json={"query": detailed_query, "variables": variables})

    if response.status_code == 200:
        data = response.json()["data"]["missionsProman"]["Mission"]

        ordered_data = sorted(data, key=lambda x: mission_id.index(x["id"]))

        return ordered_data
    else:
        print(f"Query failed with status code {response.text}")

if __name__ == "__main__":
    print(fetch_mission_by_id("pm:MP809910-2023-09-26"))
