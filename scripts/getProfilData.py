import requests
import streamlit as st
from elasticsearch import Elasticsearch

def fetch_profiles(es, batch_size=15) -> list:
    ids = fetch_all_ids(es)
    data = []
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        try:
            data.extend(fetch_reduced_data_by_ids(batch_ids))  # Note the plural 'ids'
        except Exception as e:
            print(f"An error occurred: {e}")

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
    
    res = es.search(index=st.secrets["profilIndex"],size=100,source=["_id"], query=query,scroll='1m',)
    scroll_id = res['_scroll_id']
    scroll_size = len(res['hits']['hits'])
    print(res)
    all_ids = [profile["_id"][9:] for profile in res["hits"]["hits"]]
    # Continue scrolling until no more results
    while scroll_size > 0:
        res = es.scroll(scroll_id=scroll_id, scroll='1m')
        all_ids.extend([profile["_id"][9:] for profile in res["hits"]["hits"]])
        scroll_size = len(res['hits']['hits'])
    all_ids.reverse()
    return all_ids




def fetch_reduced_data_by_ids(user_ids: list) -> list:
    url = st.secrets["graphQL"]
    detailed_query = """
    query Users($userIds: [ID]) {
        User(id: $userIds) {
            id
            personalData {
                family { value }
                given { value }
            }
        }
    }"""

    variables = {"userIds": user_ids}
    try:
        response = requests.post(url, json={"query": detailed_query, "variables": variables},timeout=60)
    except requests.Timeout:
        st.error("Il y a l'air d'avoir un problème avec le grapqhQL")
    if response.status_code == 200:
        data = response.json()
        return data["data"]["User"]
    else:
        print(f"Query failed with status code {response.text}")
        return []


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
        return data["data"]["User"]
    else:
        print(f"Query failed with status code {response.text}")



if __name__ == "__main__":
        # print(fetch_profiles(Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300) ))
        print(fetch_all_ids(Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)))

