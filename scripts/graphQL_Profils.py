import requests
import json
import streamlit as st
@st.cache_data(ttl=3600*24)
def fetch_profil_data():
    url = st.secrets["graphQL"]

    query = """query User($pagination: paginationInput) {
                          User(pagination: $pagination) {
                  id
                  personalData {
                    email {
                      value
                    }
                    family {
                      value
                    }
                    given {
                      value
                    }
                  }
                  experience {
                    title {
                      ... on String_xsd {
                        value
                      }
                    }
                    duration {
                      value
                    }
                  }
                }
              }
    """
    variables = {
    "pagination": {
        "limit": 150
       }
    }
    response = requests.post(
        url,
        json={"query": query,"variables":variables}
    )

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Query failed with status code {response.status_code}")

if __name__ == "__main__":
    profiles = fetch_profil_data()
    print(profiles)

