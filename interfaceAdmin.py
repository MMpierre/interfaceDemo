import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runP2Jsearch import P2Jsearch
from scripts.graphQL_Profils import fetch_profiles
from scripts.graphQL_Jobs import fetch_mission_data
from streamlit_echarts import st_echarts
import random
######################################### CONFIGURATION ##############################################################

#shorten session state method
memory = st.session_state
st.set_page_config(layout="wide")
memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout


######################################### AFFICHAGE ##############################################################

@st.cache_data(ttl=600)
def load_profiles():
    return fetch_profiles(memory.es)

def displayName(user):
    try:
        return user["personalData"][0]["given"][0]["value"].capitalize() + " " + user["personalData"][0]["family"][0]["value"].capitalize() 
    except:
        return user["id"]

def displayProfile():
    memory.profiles = load_profiles()
    st.selectbox("Profil",memory.profiles,5,label_visibility="hidden",format_func=lambda x: displayName(x) ,key="profil")
    try:
        st.title(f'Offres Personnalisées pour {memory.profil["personalData"][0]["given"][0]["value"].capitalize()  + " " + memory.profil["personalData"][0]["family"][0]["value"].capitalize()}')
    except:
        st.title(f'Offres Personnalisées pour {memory.profil["id"]} (Pas de nom)')
    st.sidebar.title("Interface Administrateur")
    st.sidebar.image("ressources/logoMM.png")
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
                job,duration = st.columns([4,1])
                if len(experience["title"])>0:
                    job.info(experience["title"][0]["value"])
                    duration.success(experience["duration"][0]["value"])
        else:
            st.warning("Pas d'expérience")
        
    

# MATCHING ##############################################################


def score_to_color(score:str)->str:
    cmap = plt.get_cmap('RdYlGn')  # Get the colormap in reverse order
    norm_score = score / 100.0  # Normalize score to range [0,1]
    rgb = cmap(norm_score)[:3]  # Get RGB values, ignore alpha    
    rgb = [int(255*val) for val in rgb]  # Convert RGB to 8-bit color (0-255)
    return '#{:02x}{:02x}{:02x}'.format(*rgb)  # Convert to hexadecimal

def scoreCard(score,i):

    options = {
    "series": [ {
        "type": 'gauge',
        "axisLine": {
            "lineStyle": {
            "width": 20,
            "color": [
                [0.3, '#b01735'],
                [0.7, '#f77823'],
                [1, '#2b8a08']
            ]
            }
        },
        "pointer": {
            "itemStyle": {
            "color": '#000'
            }
        },
        "axisTick": {
            "distance": -23,
            "length": 8,
            "lineStyle": {
            "color": '#fff',
            "width": 1
            }
        },
        "splitLine": {
            "distance": -25,
            "length": 30,
            "lineStyle": {
            "color": '#fff',
            "width": 2
            }
        },
        "axisLabel": {
            "color": 'inherit',
            "distance": -23,
            "fontSize": 10
        },
        "detail": {
            "valueAnimation": True,
            "formatter": '{value}%',
            "color": 'auto',
            "fontSize": 20
        },
        "data": [
            {
            "value": str(score)[:4]
            }]}]}
    st_echarts(options=options,height="150px",key=str(i)+"chart")

def displayOffers(job_offerings):
    
    b = next((idx for idx, item in enumerate(job_offerings) if 100 * (item["score"]-72.25) / 25 < 70), None)

    # Find the index where the "score" goes below 65
    c = next((idx for idx, item in enumerate(job_offerings) if 100 * (item["score"]-72.25) / 25 < 65), None)

    # Create the tuple (a, b, c)
    seuil = (0, b, c)
    for i,offer in enumerate(job_offerings):

        if i == seuil[0]:
            with st.expander("Seuil de confiance 1",expanded=True):
                st.success("Voici les missions les plus proches des expériences rapportées par le client.")
        if i == seuil[1]:
            with st.expander("Seuil de confiance 2",expanded=True):
                st.warning("En dessous de ce seuil, les offres sont moins proches et sont plus des possiblités de transition proches de l'expérience client")
        elif i == seuil[2]:
            with st.expander("Seuil de confiance 3",expanded=True):
                st.error("Enfin, les offres ci-dessous sont encore plus éloignées mais peuvent néanmoins être intéressantes pour discussion avec le client")

        with st.container():
            data = fetch_mission_data(mission_id=offer["id"])["_source"]

            score = 100 * (offer["score"]-72.25) / 25
            if score > 70:
                colored_header(data["title__value"],"","green-50")
            elif score > 65:
                colored_header(data["title__value"],"","orange-50")
            else:
                colored_header(data["title__value"],"","red-50")

            mission,card = st.columns([7,1])
            with mission:  
                desc,url = st.columns([9,1])
                with desc.expander("Description",expanded=False):
                    st.markdown(data["description__value"],unsafe_allow_html=True) 
                url.link_button("URL Proman",data["url__value"])
                ad,w,l,ag = st.columns([3,3,3,1])
                try:
                    ad.info(data["address__city__0"].capitalize() + ", " + data["address__postalcode__0"])
                except:
                    ad.info("Adresse non précisée")
                try:
                    w.info(data["contract__workTime"])
                except:
                    w.info("Type de contrat non précisé")
                try:
                    l.info(data["contract__contractLengthValue"]+ " " + data["contract__contractLengthUnit"])
                except:
                    l.info("Durée contrat non précisée")
                try:
                    ag.info(data["agency"][0][7:])
                except:
                    ag.info("Agence non précisée")

            with card:
                # scoreCard(score,i)
                st.metric("Score",f"{(score // 0.1)/10} %")



def app():
    if "authorized" not in st.session_state:
        st.session_state["authorized"] = False
    
    if st.session_state["authorized"] == False:
        userPassword = st.text_input("Rentrez le Mot de Passe","")
        if userPassword == st.secrets["password"]:
            st.session_state["authorized"] = True
            st.rerun()
    else:
        load_profiles()
        displayProfile()
        if len(memory.profil["personalData"][0]["location"][0]["geolocation"])>0:
            # job_offerings = ast.literal_eval(P2Jsearch("mirrored/"  + memory.profil["id"],10,geo=memory.profil["personalData"][0]["location"][0]["geolocation"][0]["value"].split(","),distance=memory.profil["personalData"][0]["preferredDistance"][0]["value"])) 
            job_offerings = ast.literal_eval(P2Jsearch("mirrored/"  + memory.profil["id"],10,len(memory.profil["experience"]),None,None))   
        else:
            job_offerings = ast.literal_eval(P2Jsearch("mirrored/"  + memory.profil["id"],10,len(memory.profil["experience"]),None,None))

        displayOffers(job_offerings) 

        

if __name__ == "__main__":
    app()
