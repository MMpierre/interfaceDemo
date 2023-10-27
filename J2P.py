import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runJ2Psearch import J2Psearch
from scripts.getProfilData import fetch_data_by_id
from scripts.getMissionData import fetch_mission_data,fetch_all_missions

import random
######################################### CONFIGURATION ##############################################################

#shorten session state method
memory = st.session_state
memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout


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
    st.selectbox("Missions",memory.missions,5,label_visibility="collapsed",format_func=lambda x: displayTitle(x),key="mission")
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
    
def displayOffers(profiles):
    
    b = next((idx for idx, item in enumerate(profiles) if item["score"]< 70), None)

    # Find the index where the "score" goes below 65
    c = next((idx for idx, item in enumerate(profiles) if item["score"]< 65), None)

    # Create the tuple (a, b, c)
    seuil = (0, b, c)
    for i,profil in enumerate(profiles):

        if i == seuil[0]:
            with st.expander("Seuil de confiance 1",expanded=True):
                st.success("Voici les missions les plus proches des expériences rapportées par le client.")
        if i == seuil[1]:
            with st.expander("Seuil de confiance 2",expanded=True):
                st.warning("En dessous de ce seuil, les offres sont moins proches et sont plus des possiblités de transition proches de l'expérience client")
        if i == seuil[2]:
            with st.expander("Seuil de confiance 3",expanded=True):
                st.error("Enfin, les offres ci-dessous sont encore plus éloignées mais peuvent néanmoins être intéressantes pour discussion avec le client")

        with st.container():
            data = fetch_data_by_id(profil["id"][9:])

            score = profil["score"]
            if score > 70:
                colored_header(displayName(data),"","green-50")
            elif score > 65:
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
    memory.missions = load_missions()
    displayMission()
    profiles = ast.literal_eval(J2Psearch(memory.mission["id"],10)) 
    

    displayOffers(profiles) 

        

if __name__ == "__main__":
    J2P()
