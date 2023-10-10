import requests
import json

def fetch_profil_data():
    url = "https://app-dev-wyew76oo4a-ew.a.run.app/graphql?explorerURLState=N4IgJg9gxgrgtgUwHYBcQC4QEcYIE4CeABAKoDO+RwAOkkaRXlbffQJZgusAO+ZESAIYAbACKCUg5nVb0EcQW2HTZsgG4jcXWQF9tRPTMM6QAGhAa8bQQCNhCMhhAgdQA"
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }

    query = """query User {
        User{
          personalData {
            email {
              value
            }
          }
          experience {
            title {
              ... on String_xsd {
                value
              }
            }
          }
        }
      }
    """

    response = requests.post(
        url,
        json={"query": query}
    )

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Query failed with status code {response.status_code}")

if __name__ == "__main__":
    profiles = fetch_profil_data()
    print(profiles)

