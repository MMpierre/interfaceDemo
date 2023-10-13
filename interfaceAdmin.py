import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runP2Jsearch import P2Jsearch
from scripts.graphQL_Profils import fetch_profil_data
from scripts.graphQL_Jobs import fetch_mission_data
from streamlit_echarts import st_echarts
import random
######################################### CONFIGURATION ##############################################################

#shorten session state method
memory = st.session_state
st.set_page_config(layout="wide")
memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout


######################################### AFFICHAGE ##############################################################
def load_profiles():
    with st.spinner("Récupération des profils"):
        memory.profiles = [profil for profil in fetch_profil_data()["data"]["User"]]


def displayProfile():
    
    st.selectbox("Profil",memory.profiles,0,label_visibility="hidden",format_func=lambda x : x["id"],key="profil")

    st.header(f'Offres Personnalisées pour {memory.profil["id"]}',divider="red")
    st.sidebar.title("Interface Administrateur")
    st.sidebar.image("ressources/logoMM.png")
    with st.sidebar:
        colored_header(
                label="Expérience",
                description="",
                color_name="red-80",)
        job,duration = st.columns([4,1])
        for experience in memory.profil["experience"]:
            if len(experience["title"])>0:
                job.info(experience["title"][0]["value"])
                duration.success(experience["duration"][0]["value"])
        st.button("Rafraichir les profils")
        
    

# MATCHING ##############################################################

def parseOffer(offer:dict):
    options = [offer["city"],offer["education"],offer["experience"]]
    return options


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
    st_echarts(options=options,height="200px",key=str(i)+"chart")

def displayOffers(job_offerings):
    for i,offer in enumerate(job_offerings):
        with st.container():
            data = fetch_mission_data(mission_id=offer["id"])["data"]["missionsProman"]["Mission"][0]  
            colored_header(f"Mission #{i} : " + data["title"],"","blue-30")
            mission,card = st.columns([7,1])
            with mission:  
                desc,url = st.columns([9,1])
                with desc.expander("Description",expanded=False):
                    st.markdown(data["description"][0]["value"],unsafe_allow_html=True) 
                    desc.info("Adresse de la mission")
                url.link_button("URL Proman",data["url"][0]["value"])
                url.info("Agence de la mission")
            with card:
                score = 100 * (offer["score"]-70) / 25
                scoreCard(score,i)



def app():
    if "authorized" not in st.session_state:
        st.session_state["authorized"] = False
    
    if st.session_state["authorized"] == False:
        userPassword = st.text_input("Rentrez le Mot de Passe","")
        if userPassword == st.secrets["password"]:
            st.session_state["authorized"] = True
            st.button("Accéder à l'interface")
    else:
        load_profiles()
        displayProfile()
    

        # Call your job matching function and store the results
        try:
            job_offerings = ast.literal_eval(P2Jsearch("mirrored/"  + memory.profil["id"],10))  
            displayOffers(job_offerings) 
        except:
            st.error("Le profil n'est pas présent sur ElasticSearch")

        

if __name__ == "__main__":
    app()
