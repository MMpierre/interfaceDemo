import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runJ2Psearch import J2Psearch
from scripts.getProfilData import fetch_data_by_id
from scripts.getMissionData import fetch_mission_data,fetch_all_missions
from time import time
memory = st.session_state
######################################### AFFICHAGE ##############################################################

@st.cache_data(ttl=3600)
def load_missions():
    exclude = ["pm:MP801963-2023-10-04"]
    return [x for x in fetch_all_missions(memory.es) if x["id"] not in exclude]


st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 250px;
            font-size: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    
######################################### AFFICHAGE ##############################################################
def displayTitle(mission):
    try : 
        return mission["title__value"] + " - " + mission["address__city__0"].capitalize()
    except:
        return mission["title__value"] 
       
def displayMission():
    st.header("Choisissez une mission",divider="red")
    st.selectbox("Missions",memory.missions,0,label_visibility="collapsed",format_func=lambda x: displayTitle(x),key="mission")
    memory.data = fetch_mission_data(memory.mission["id"],memory.es)
    with st.expander("Description"):
        st.markdown(memory.data["description__value"],unsafe_allow_html=True)
    st.title(f'Profils Personnalisés pour {memory.mission["title__value"]}')
 
    with st.sidebar:
        colored_header(
                label="Mission",
                description="",
                color_name="red-80",)
        st.info(memory.data["agency__prefLabel"])
        st.info(f'{memory.data["address__city__0"]}, {memory.data["address__postalcode__0"]}')
        st.info("Durée : " + memory.data["contract__contractLengthValue"]+ " " + memory.data["contract__contractLengthUnit"])
        st.info("Contrat : " + memory.data["contract__workTime"])
        st.link_button("URL",memory.data["url__value"],use_container_width=True)
        
    

# MATCHING ##############################################################

def displayName(user):
    try:
        return user["personalData"][0]["given"][0]["value"].capitalize() + " " + user["personalData"][0]["family"][0]["value"].capitalize() 
    except:
        return user["id"]
    
def displayProfiles(profiles):
    with st.spinner("Récupération des profils"): 
        datas = fetch_data_by_id([profil["id"][9:] for profil in profiles])
        
    for i,(profil,data) in enumerate(zip(profiles,datas)):

        with st.container():

            score = profil["score"]
            if score > 80:
                colored_header(displayName(data),"","green-50")
            elif score > 70:
                colored_header(displayName(data),"","orange-50")
            else:
                colored_header(displayName(data),"","red-50")

            profil,card = st.columns([7,1])
            
            with profil:  
                jobs = st.columns(len(data["experience"]))
                for i,job in enumerate(jobs):
                    with job:
                        try:
                            st.info(data["experience"][i]["title"][0]["value"])
                            st.info(data["experience"][i]["duration"][0]["value"])
                        except:
                            st.warning("Pas d'informations")

                

            with card:
                # scoreCard(score,i)
                st.metric("Score",f"{(score // 0.1)/10} %")



def J2P():
        #shorten session state method
    memory = st.session_state
    memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout

    memory.missions = load_missions()
    displayMission()
    with st.spinner("Calcul des scores ..."):
        profiles = ast.literal_eval(J2Psearch(memory.mission["id"],10)) 

    displayProfiles(profiles) 

        

if __name__ == "__main__":
    J2P()
