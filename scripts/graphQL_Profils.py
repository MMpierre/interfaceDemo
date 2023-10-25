import requests
import streamlit as st

def fetch_names_ids():
    url = st.secrets["graphQL"]
    id_query = """query User($pagination: paginationInput) {
                     User(pagination: $pagination) {
                               id
                               personalData {
                                   family { value }
                                   given { value }
                                   }
                     }
                 }"""

    all_ids = []
    all_names = []
    limit = 10
    page = 1

    while True:
        
        variables = {"pagination": {"limit": limit, "page": page}}
        response = requests.post(url, json={"query": id_query, "variables": variables})

        if response.status_code != 200:
            print(f"Query failed with status code {response.status_code}")
            break

        data = response.json()
        
        for user in data["data"]["User"]:
            name = ""
            if len(user["personalData"])>0:
                if user["personalData"][0]["family"]:
                    name += user["personalData"][0]["family"][0]["value"].capitalize()
                name += " " 
                if  user["personalData"][0]["given"]:
                    name += user["personalData"][0]["given"][0]["value"].capitalize()
            if len(name)>5:
                all_names.append(name) 
                all_ids.append(user["id"])

        if len(data["data"]["User"]) < limit:
            break

        page += 1

    return all_ids,all_names


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
                               favoriteMissions { id }
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
        return data
    else:
        print(f"Query failed with status code {response.text}")


if __name__ == "__main__":
    print(fetch_all_ids())

