import requests
import streamlit as st
import json

def fetch_mission_data(mission_id):
    url = st.secrets["graphQL"]

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
          description {
            value
          }
          }
          url {
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
        print(json.dumps(data, indent=4))
    else:
        print(f"Query failed with status code {response.status_code}")

if __name__ == "__main__":
    mission_id = input("Enter the Mission ID: ")
    fetch_mission_data(mission_id)
