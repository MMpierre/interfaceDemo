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
        memory.profiles = [profil for profil in fetch_profil_data()["data"]["User"] if len(profil["personalData"])>0 and len(profil["personalData"][0]["family"])>0]
        filtered_out = ["76c073a7-3ed8-444e-95ce-a238cfb4a44d","users/LoImF2RDvtI0JXuskGP8-","b5f34a89-3f57-4f51-b268-5c63f72af9b1","4ec49d23-4684-432f-b4a5-23f75e275c82","cb0404b9-fb75-4f40-99e7-82f2b8a21c50","4ef6c923-4330-4242-b06c-c6c55b53558a","user/fXhHv-yTaW","user/BmFAqbOudP"]
        memory.profiles = [profil for profil in memory.profiles if profil["id"] not in filtered_out and profil["personalData"][0]["family"][0]["value"] != "Doe" and profil["personalData"][0]["family"][0]["value"] != "Doe2"]

def displayProfile():
    st.selectbox("Profil",memory.profiles,3,label_visibility="hidden",format_func=lambda x :x["personalData"][0]["given"][0]["value"].capitalize() +" " +  x["personalData"][0]["family"][0]["value"].capitalize(),key="profil")
    st.title(f'Offres Personnalisées pour {memory.profil["personalData"][0]["given"][0]["value"].capitalize() +" " +  memory.profil["personalData"][0]["family"][0]["value"].capitalize()}')
    st.write(memory.profil["id"])
    st.sidebar.title("Interface Administrateur")
    st.sidebar.image("ressources/logoMM.png")
    with st.sidebar:
        colored_header(
                label="Profil",
                description="",
                color_name="red-80",)
        st.info(memory.profil["personalData"][0]["email"][0]["value"])
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
                st.error("Enfin les offres ci-dessous sont trop éloignées pour pouvoir faire un rapprochement avec le client. Elle ne seront pas affichées de son côté.")

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
                    desc.info("Adresse de la mission")
                url.link_button("URL Proman",data["url__value"])
                url.info(data["member_of"][0][7:])
            with card:
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
    
        job_offerings = ast.literal_eval(P2Jsearch("mirrored/"  + memory.profil["id"],10))  
        displayOffers(job_offerings) 

        

if __name__ == "__main__":
    app()
