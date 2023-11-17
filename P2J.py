# Third-party imports
import elasticsearch
import streamlit as st

# Local application/library specific imports
from scripts.knnSearches.runP2Jsearch import P2Jsearch
from scripts.getProfilData import fetch_profiles, fetch_data_by_id
from scripts.getMissionData import fetch_mission_by_id
from scripts.componentsUI import *
#shorten session state method
memory = st.session_state

@st.cache_data(ttl=3600)
def load_profiles():
    return fetch_profiles(memory.es)
        
def parseAndFetch(job_offerings):
    alldatas = []
    allscores = []
    tabs = []
    for id in memory.profil["favoriteMissions"]:
        job_offerings.loc[job_offerings["_id"] == id["id"],"_score"] += 10 
    job_offerings = job_offerings.sort_values(by="_score",ascending=False)
    with st.spinner(f"Chargement des Mission Proposées"):
        datas = fetch_mission_by_id([id for i,id in job_offerings["_id"].items()])
   
    # TOP 3
    alldatas.append(datas[:3])
    allscores.append(job_offerings.loc[:3,"_score"][:3])
    tabs.append("Missions proposées")
    ####################################
    datas = datas[3:]
    job_offerings = job_offerings.loc[3:,:]
    ####################################
    # Mission Specific
    for i in range(max(job_offerings["exp"])+1):
        alldatas.append([data for data,flag in zip(datas,job_offerings["exp"]==i) if flag])
        allscores.append(job_offerings.loc[job_offerings["exp"]==i,"_score"])
        tabs.append(f"Missions proche de {memory.profil['experience'][i]['title'][0]['value']}")

    if len(memory.profil["personalData"][0]["location"]) > 0 and len(memory.profil["personalData"][0]["location"][0]["city"]) > 0 :
        city = memory.profil["personalData"][0]["location"][0]["city"][0]["value"]

        if city in set(job_offerings["city"].str.capitalize()):
            alldatas.append([data for data,flag in zip(datas,job_offerings["city"].str.capitalize()==city) if flag])
            allscores.append(job_offerings.loc[job_offerings["city"].str.capitalize()==city,"_score"])
            tabs.append(f'Missions à {city}')

    # Liked Missions
    if len(memory.profil["favoriteMissions"])==0:
        alldatas.append([])
        allscores.append([])
    else:
        with st.spinner(f"Chargement des Mission Likées"):
            datas = fetch_mission_by_id([mission["id"] for mission in memory.profil["favoriteMissions"]])      
        alldatas.append(datas)
        allscores.append(len(memory.profil["favoriteMissions"]) * ["❤"])
    tabs.append(f"Missions Likées ({len(memory.profil['favoriteMissions'])})")

    return alldatas,allscores,tabs

def displayOffers(job_offerings):

    alldatas,allscores,tabs = parseAndFetch(job_offerings)
    
    tabs = st.tabs(tabs)

    for tab,datas,scores in zip(tabs,alldatas,allscores):
        with tab:
            [displayOffer(data,score)for data,score in zip(datas,scores)]

        
        


def P2J():
    
    memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout
    memory.profiles = load_profiles()
    
    _,middle,_ = st.columns(3)
    middle.header("Choisissez un profil",divider="red")
    middle.selectbox("Profil",memory.profiles,label_visibility="collapsed",format_func=lambda x: displayName(x) ,key="profil_id")
    with st.spinner("Chargement du Profil"):
        memory.profil = fetch_data_by_id([memory.profil_id["id"]])[0]
    displayProfile(memory.profil)


    if len(memory.profil["personalData"][0]["location"])>0 and len(memory.profil["personalData"][0]["location"][0]["geolocation"])>0:
        job_offerings = P2Jsearch("mirrored/"  + memory.profil["id"],memory.n,min(3,len(memory.profil["experience"])),geo=memory.profil["personalData"][0]["location"][0]["geolocation"][0]["value"].split(","),distance=memory.profil["personalData"][0]["preferredDistance"][0]["value"])
    else:
        job_offerings = P2Jsearch("mirrored/"  + memory.profil["id"],memory.n,min(3,len(memory.profil["experience"])),None,None)
    
    displayOffers(job_offerings) 


if __name__ == "__main__":
    P2J()
