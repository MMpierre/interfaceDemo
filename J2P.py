import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runJ2Psearch import J2Psearch,J2Psearch_liked
from scripts.getProfilData import fetch_data_by_id
from scripts.getMissionData import fetch_mission_by_id,fetch_all_missions
from time import time
memory = st.session_state
######################################### AFFICHAGE ##############################################################

@st.cache_data(ttl=3600)
def load_missions():
    return [x for x in fetch_all_missions(memory.es)]


css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:2rem;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)

    
######################################### AFFICHAGE ##############################################################
def displayTitle(mission):
    try : 
        return mission["title__value"] + " - " + mission["address__city__0"].capitalize()
    except:
        return mission["title__value"] 
       
def displayMission():
    st.header("Choisissez une mission",divider="red")
    st.selectbox("Missions",memory.missions,0,label_visibility="collapsed",format_func=lambda x: displayTitle(x),key="mission")
    memory.data = fetch_mission_by_id(memory.mission["id"])[0]
    with st.expander("Description"):
        st.markdown(memory.data["description"][0]["value"],unsafe_allow_html=True)
    st.title(f'Profils Personnalisés pour {memory.mission["title__value"]}')
 
    with st.sidebar:
        colored_header(
                label="Mission",
                description="",
                color_name="red-80",)
        
        try:
            st.info(memory.data["agency"][0]["prefLabel"][0]["value"])
        except:
            st.info("Pas de numéro d'agence")
        try:
            st.info(memory.data["missionAddress"][0]["city"][0]["value"].capitalize() + ", " + memory.data["missionAddress"][0]["postalcode"][0]["value"])
        except:
            st.info("Pas d'adresse")
        try:
            st.info("Durée : " + memory.data["contract"][0]["contractLengthValue"][0]["value"]+ " " + memory.data["contract"][0]["contractLengthUnit"][0]["value"])
        except:
            st.info("Pas de durée de contrat")
        try:
            st.info("Contrat : " + memory.data["contract"][0]["workTime"][0]["value"])
        except:
            st.info("Pas de type de contrat")
        try:
            st.link_button("URL",memory.data["url"][0]["value"],use_container_width=True)
        except:
            st.info("Pas de lien vers l'offre")
        
    

# MATCHING ##############################################################

def displayName(user):
    try:
        return user["personalData"][0]["given"][0]["value"].capitalize() + " " + user["personalData"][0]["family"][0]["value"].capitalize() 
    except:
        return user["id"]

def displayProfile(profil,data):

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
        st.metric("Score",f"{(score // 0.1)/10} %",label_visibility='collapsed')
        if data["id"] in memory.data["userLiked"]:
            st.success("Mission Likée")

def displayProfiles(profiles):
    with st.spinner("Récupération des profils"): 
        datas = fetch_data_by_id([profil["id"][9:] for profil in profiles])
    for i,(profil,data) in enumerate(zip(profiles,datas)):
        with st.container():
            displayProfile(profil,data)



def J2P():
        #shorten session state method
    memory = st.session_state
    memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout

    memory.missions = load_missions()
    displayMission()
    tabs = st.tabs(["Users proposés",f"Users ayant liké ({len(memory.data['userLiked'])})"])
    with tabs[0]:
        with st.spinner("Calcul des scores ..."):
            profiles = ast.literal_eval(J2Psearch(memory.mission["id"],memory.n)) 
        displayProfiles(profiles) 
    with tabs[1]:
        if len(memory.data["userLiked"])==0:
            st.warning("Aucun utilisateur n'a liké cette mission")
        else:
            with st.spinner("Calcul des scores ..."):
                profiles = ast.literal_eval(J2Psearch_liked(memory.mission["id"],min(len(memory.data["userLiked"]),memory.n),["mirrored/" + user["id"] for user in memory.data["userLiked"]])) 
            displayProfiles(profiles) 



        

if __name__ == "__main__":
    J2P()
