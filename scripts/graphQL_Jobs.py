import requests
import streamlit as st
import json

def fetch_mission_data(mission_id):
    url = "https://app-dev-wyew76oo4a-ew.a.run.app/graphql"

    query = """
            query User($missionsPromanId: [ID]) {
              missionsProman(id: $missionsPromanId) {
                Mission {
                  id
                  title {
                    ... on String_xsd {
                      value
                    }
                  }
                  url {
                    value
                  }
                  description {
                    value
                  }
                }
              }
            }
    """

    variables = {
        "missionsPromanId": [mission_id]
    }

    response = requests.post(
        url,
        json={"query": query, "variables": variables}
    )

    if response.status_code == 200:
        data = response.json()
        return(data)
    else:
        print(f"Query failed with status code {response.text}")

if __name__ == "__main__":
    mission_id = input("Enter the Mission ID: ")
    fetch_mission_data(mission_id)
