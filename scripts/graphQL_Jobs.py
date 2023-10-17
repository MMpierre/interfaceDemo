import requests
import streamlit as st
import json
import elasticsearch

# def fetch_mission_data(mission_id):
#     url = "https://app-dev-wyew76oo4a-ew.a.run.app/graphql"

#     query = """
#             query User($missionsPromanId: [ID]) {
#               missionsProman(id: $missionsPromanId) {
#                 Mission {
#                   id
#                   title {
#                     ... on String_xsd {
#                       value
#                     }
#                   }
#                   url {
#                     value
#                   }
#                   description {
#                     value
#                   }
#                 }
#               }
#             }
#     """

#     variables = {
#         "missionsPromanId": [mission_id]
#     }

#     response = requests.post(
#         url,
#         json={"query": query, "variables": variables}
#     )

#     if response.status_code == 200:
#         data = response.json()
#         return(data)
#     else:
#         print(f"Query failed with status code {response.text}")

def fetch_mission_data(mission_id):
    es =  elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)    

    query = {  "match": {
            "_id": mission_id}}
    res = es.search(index=st.secrets["jobIndex"], query=query, source=["title__value","description__value","member_of","url__value",])["hits"]["hits"][0]
    return res

if __name__ == "__main__":
    mission_id = input("Enter the Mission ID: ")
    fetch_mission_data(mission_id)
