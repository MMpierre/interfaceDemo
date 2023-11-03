import requests
import streamlit as st
from elasticsearch import Elasticsearch

def fetch_profiles(es)->list:
    ids = fetch_all_ids(es)
    data = []
    for id in ids :
        try:
            data.append(fetch_data_by_id(id)) 
        except:
            st.toast(f"Attention, l'id '{id}' n'est pas sur le graphQl")

    return data

def fetch_all_ids(es):
    # Initial search
    query = {
            "bool": {
                "filter": {
                    "exists": {
                        "field": "experience__occupation__vector__0"
                    }
                }
            }
        }
    
    res = es.search(index=st.secrets["profilIndex"],size=100,source=["_id"], query=query,scroll='1m')
    scroll_id = res['_scroll_id']
    scroll_size = len(res['hits']['hits'])
    
    all_ids = [profile["_id"][9:] for profile in res["hits"]["hits"]]
    # Continue scrolling until no more results
    while scroll_size > 0:
        res = es.scroll(scroll_id=scroll_id, scroll='1m')
        all_ids.extend([profile["_id"] for profile in res["hits"]["hits"]])
        scroll_size = len(res['hits']['hits'])
    
    return all_ids



def fetch_data_by_id(user_id:str):
    url = st.secrets["graphQL"]
    detailed_query = """query User($userId: [ID]) {
                            User(id: $userId) {
                               id
                               personalData {
                                   email { value }
                                   family { value }
                                   given { value }
                                   location {
                                       geolocation { value }
                                       city { value }
                                       postalcode { value }
                                   }
                                   preferredDistance { value }
                               }
                               favoriteMissions {
                                    id
                                    title {
                                        value
                                    }
                                    url {
                                        value
                                    }
                                }
                               experience {
                                   title {
                                       ... on String_xsd { value }
                                   }
                                   duration { value }
                               }
                           }
                       }"""

    variables = {"userId": user_id}
    
    response = requests.post(url, json={"query": detailed_query, "variables": variables})

    if response.status_code == 200:
        data = response.json()
        return data["data"]["User"][0]
    else:
        print(f"Query failed with status code {response.text}")



if __name__ == "__main__":
        print(fetch_profiles(Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300) ))

