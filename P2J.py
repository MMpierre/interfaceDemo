import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runP2Jsearch import P2Jsearch,P2Jsearch_Liked
from scripts.getProfilData import fetch_profiles,fetch_data_by_id
from scripts.getMissionData import fetch_mission_by_id
from streamlit_echarts import st_echarts
#shorten session state method
memory = st.session_state

######################################### AFFICHAGE ##############################################################

@st.cache_data(ttl=3600)
def load_profiles():
    return fetch_profiles(memory.es)

def displayName(user):
    try:
        return user["personalData"][0]["given"][0]["value"].capitalize() + " " + user["personalData"][0]["family"][0]["value"].capitalize() 
    except:
        return user["id"]

def displayProfile():
    st.header("Choisissez un profil",divider="red")
    st.selectbox("Profil",memory.profiles,5,label_visibility="collapsed",format_func=lambda x: displayName(x) ,key="profil_id")
    with st.spinner("Chargement du Profil"):
        memory.profil = fetch_data_by_id([memory.profil_id["id"]])[0]
    try:
        st.title(f'Offres Personnalisées pour {memory.profil["personalData"][0]["given"][0]["value"].capitalize()  + " " + memory.profil["personalData"][0]["family"][0]["value"].capitalize()}')
    except:
        st.title(f'Offres Personnalisées pour {memory.profil["id"]} (Pas de nom)')

    with st.sidebar:
        colored_header(
                label="Profil",
                description="",
                color_name="red-80",)
        try:
            st.info(memory.profil["personalData"][0]["email"][0]["value"])
        except:
            st.info("Pas d'adresse email")
        try:
            st.info(memory.profil["personalData"][0]["location"][0]["city"][0]["value"])
        except:
            st.info("Pas d'adresse")
        colored_header(
                label="Expérience",
                description="",
                color_name="red-80",)
        if memory.profil["experience"]:
            for experience in memory.profil["experience"]:
                job,duration = st.columns([3,1])
                if len(experience["title"])>0:
                    job.info(experience["title"][0]["value"])
                    duration.success(experience["duration"][0]["value"])
        else:
            st.warning("Pas d'expérience")
        
    

# MATCHING ##############################################################
def displayOffer(offer,data):
    score = offer["score"]
    if score > 70:
        colored_header(data["title"][0]["value"],"","green-50")
    elif score > 65:
        colored_header(data["title"][0]["value"],"","orange-50")
    else:
        colored_header(data["title"][0]["value"],"","red-50")

    mission,card = st.columns([7,1])
    with mission:  
        desc,url = st.columns([9,1])
        with desc.expander("Description",expanded=False):
            st.markdown(data["description"][0]["value"],unsafe_allow_html=True) 
        url.link_button("URL Proman",data["url"][0]["value"])
        ad,w,l,ag = st.columns([3,3,3,1])
        try:
            ad.info(data["missionAddress"][0]["city"][0]["value"].capitalize() + ", " + data["missionAddress"][0]["postalcode"][0]["value"])
        except:
            ad.info("Adresse non précisée")
        try:
            w.info(data["contract"][0]["workTime"][0]["value"])
        except:
            w.info("Type de contrat non précisé")
        try:
            l.info(data["contract"][0]["contractLengthValue"][0]["value"]+ " " + data["contract"][0]["contractLengthUnit"][0]["value"])
        except:
            l.info("Durée contrat non précisée")
        try:
            ag.info(data["agency"][0]["prefLabel"][0]["value"][-5:])
        except:
            ag.info("404")

    with card:
        st.metric("Score",f"{(score // 0.1)/10} %",label_visibility='collapsed')
        if len(memory.profil["favoriteMissions"])>0:
            for fmission in memory.profil["favoriteMissions"]:
                if fmission["id"] == offer["id"]:
                    st.success("Missions likée")

def displayOffers(job_offerings):
    
    b = next((idx for idx, item in enumerate(job_offerings) if item["score"]< 70), None)

    # Find the index where the "score" goes below 65
    c = next((idx for idx, item in enumerate(job_offerings) if item["score"]< 65), None)

    # Create the tuple (a, b, c)
    seuil = (0, b, c)
    with st.spinner("Chargement des mission"):
        datas = fetch_mission_by_id([offer["id"] for offer in job_offerings])
        
    for i,(offer,data) in enumerate(zip(job_offerings,datas)):

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
           displayOffer(offer,data)


def P2J():
    #shorten session state method
    memory = st.session_state
    memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout
    memory.profiles = load_profiles()
    displayProfile()

   
    tabs = st.tabs(["Missions Proposées",f"Mission Likées ({len(memory.profil['favoriteMissions'])})"])
    with tabs[0]:
        with st.spinner("Calcul des scores ..."):
            if len(memory.profil["personalData"][0]["location"][0]["geolocation"])>0:
                job_offerings = ast.literal_eval(P2Jsearch("mirrored/"  + memory.profil["id"],memory.n,len(memory.profil["experience"]),geo=memory.profil["personalData"][0]["location"][0]["geolocation"][0]["value"].split(","),distance=memory.profil["personalData"][0]["preferredDistance"][0]["value"])) 
            else:
                job_offerings = ast.literal_eval(P2Jsearch("mirrored/"  + memory.profil["id"],memory.n,len(memory.profil["experience"]),None,None))
        displayOffers(job_offerings) 
    with tabs[1]:
        if len(memory.profil["favoriteMissions"])==0:
            st.warning("Cet utilisateur n'a pas de missions likées")
        else:
            with st.spinner("Calcul des scores ..."):
                job_offerings = ast.literal_eval(P2Jsearch_Liked("mirrored/"  + memory.profil["id"],min(memory.n,len(memory.profil["favoriteMissions"])),len(memory.profil["experience"]),[mission["id"] for mission in memory.profil["favoriteMissions"]]))
            displayOffers(job_offerings)
        

if __name__ == "__main__":
    P2J()
