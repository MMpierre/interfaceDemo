# Third-party imports
import elasticsearch
import streamlit as st
from streamlit_extras.colored_header import colored_header

# Local application/library specific imports
from scripts.knnSearches.runP2Jsearch import P2Jsearch, P2Jsearch_Liked
from scripts.getProfilData import fetch_profiles, fetch_data_by_id
from scripts.getMissionData import fetch_mission_by_id
from scripts.componentsUI import *
#shorten session state method
memory = st.session_state

@st.cache_data(ttl=3600)
def load_profiles():
    return fetch_profiles(memory.es)
        
def getAllData(job_offerings):
    alldatas = []
    allscores = []
    total = 1 + len(memory.profil['experience']) +  int(len(memory.profil["favoriteMissions"] )>0)
    # TOP 3
    with st.spinner(f"(1/{total}) - Chargement des Mission Proposées"):
        datas = fetch_mission_by_id([id for i,id in job_offerings.loc[:3,"_id"].items()])
    alldatas.append(datas[:3])
    allscores.append(job_offerings.loc[:3,"_score"][:3])
    # Mission Specific
    for i in range(len(memory.profil["experience"])):
        with st.spinner(f"({i+2}/{total}) - Récupération des missions pour {memory.profil['experience'][i]['title'][0]['value']}"):
            datas = fetch_mission_by_id([id for i,id in job_offerings.loc[job_offerings["exp"]==i,"_id"].items()])
        alldatas.append(datas)

        allscores.append(job_offerings.loc[job_offerings["exp"]==i,"_score"])

    # Liked Missions
    if len(memory.profil["favoriteMissions"])==0:
        alldatas.append([])
        allscores.append([])
    else:
        with st.spinner(f"({2+len(memory.profil['experience'])}/{total}) - Chargement des Mission Likées"):
            datas = fetch_mission_by_id([mission["id"] for mission in memory.profil["favoriteMissions"]])      
        alldatas.append(datas)
        allscores.append(len(memory.profil["favoriteMissions"]) * ["❤"])
    return alldatas,allscores

def displayOffers(job_offerings):

    alldatas,allscores = getAllData(job_offerings)
    tabs = st.tabs(["Missions proposées"] + [f"Missions proche de {experience['title'][0]['value']}" for experience in memory.profil["experience"]] + [f"Missions Likées ({len(memory.profil['favoriteMissions'])})"])


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
        job_offerings = P2Jsearch("mirrored/"  + memory.profil["id"],memory.n,len(memory.profil["experience"]),geo=memory.profil["personalData"][0]["location"][0]["geolocation"][0]["value"].split(","),distance=memory.profil["personalData"][0]["preferredDistance"][0]["value"])
    else:
        job_offerings = P2Jsearch("mirrored/"  + memory.profil["id"],memory.n,len(memory.profil["experience"]),None,None)
    
    displayOffers(job_offerings) 


if __name__ == "__main__":
    P2J()
