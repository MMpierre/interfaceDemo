import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runJ2Psearch import J2Psearch
from scripts.getProfilData import fetch_data_by_id
from scripts.getMissionData import fetch_mission_by_id,fetch_all_missions
from scripts.componentsUI import *
from time import time
memory = st.session_state
######################################### AFFICHAGE ##############################################################

@st.cache_data(ttl=3600)
def load_missions():
    return [x for x in fetch_all_missions(memory.es)]

def parseAndFetch(profiles):
    alldatas = []
    allscores = []
    for id in memory.data["userLiked"]:
        profiles.loc[profiles["_id"] == "mirrored/" + id["id"],"_score"] += 10 
    
    profiles['Is_Duplicate'] = profiles.duplicated(subset='_id', keep=False)
    profiles = profiles.drop_duplicates(subset="_id")
    with st.spinner(f"Chargement des Profils Proposées"):
            datas = fetch_data_by_id([id.replace("mirrored/","") for i,id in profiles["_id"].items()])


    alldatas.append(datas)
    allscores.append(profiles.loc[:,"_score"])

    #With multiple relevant experiences
    alldatas.append([data for data,flag in zip(datas,profiles["Is_Duplicate"]) if flag])
    allscores.append(profiles.loc[profiles["Is_Duplicate"],"_score"])    


    #In the same city
    city = memory.data['missionAddress'][0]['city'][0]['value'].capitalize()
    if city in set(profiles["city"].str.capitalize()):
        alldatas.append([data for data,flag in zip(datas,profiles["city"].str.capitalize()==city) if flag])
        allscores.append(profiles.loc[profiles["city"].str.capitalize()==city,"_score"])
    else:
        alldatas.append([])
        allscores.append([])

    # Liked Missions
    if len(memory.data["userLiked"])==0:
        alldatas.append([])
        allscores.append([])
    else:
        with st.spinner(f"Chargement des Mission Likées"):
            datas = fetch_data_by_id([mission["id"] for mission in memory.data["userLiked"]])      
        alldatas.append(datas)
        allscores.append(len(memory.data["userLiked"]) * ["❤"])
    return alldatas,allscores

def displayUsers(profiles):

    alldatas,allscores = parseAndFetch(profiles)
    tabs = st.tabs(["Profils proposés"] + [f"Users avec expériences multiples" ] + [f"Users à {memory.data['missionAddress'][0]['city'][0]['value'].capitalize()}"] +[f"Users ayant liké ({len(memory.data['userLiked'])})"])

    with tabs[1]:
        st.warning("L'intérêt de cette section est de ressortir les profils qui ont plusieurs expériences qui ont matché. Cependant avec le peu de profils sur la base actuelle, toutes les expériences rentrent dans le top10  ")
    for tab,datas,scores in zip(tabs,alldatas,allscores):
        with tab:
            [displayUser(data,score)for data,score in zip(datas,scores)]



def J2P():
    
    memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout
    memory.missions = load_missions()

    _,middle,_ = st.columns([1,2,1])
    middle.header("Choisissez une mission",divider="red")
    l,r = middle.columns([1,2])
    agencies = sorted(set([mission["agency__id"][7:] for mission in memory.missions if "agency__id" in mission]))
    agency = l.selectbox("Agence",["Toutes Agences"] + agencies,0,label_visibility="collapsed")
    if agency == "Toutes Agences":
        missions = memory.missions
    else:
        missions = [mission for mission in memory.missions if "agency__id" in mission and mission["agency__id"][7:]==agency]
    r.selectbox("Missions",missions,0,label_visibility="collapsed",format_func=lambda x: displayTitle(x),key="mission")
    with st.spinner("Récupération des informations de la mission"):
        memory.data = fetch_mission_by_id(memory.mission["id"])[0]
    displayMission(memory.data)
        
    if len(memory.data["missionAddress"])>0 and len(memory.data["missionAddress"][0]["geolocation"])>0:
        profiles = J2Psearch(memory.mission["id"],memory.n,memory.data["missionAddress"][0]["geolocation"][0]["value"].split(","))
    else:
        profiles = J2Psearch(memory.mission["id"],memory.n,None)

    displayUsers(profiles) 


        

if __name__ == "__main__":
    J2P()
