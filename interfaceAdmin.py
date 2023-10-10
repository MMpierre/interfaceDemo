import streamlit as st
from streamlit_extras.colored_header import colored_header
import ast
import matplotlib.pyplot as plt
import elasticsearch
from scripts.knnSearches.runP2Jsearch import J2Psearch
from scripts.graphQL_Profils import fetch_profil_data
import webbrowser
from streamlit_echarts import st_echarts
import random
######################################### CONFIGURATION ##############################################################

#shorten session state method
memory = st.session_state
st.set_page_config(layout="wide")
memory.es = elasticsearch.Elasticsearch(cloud_id=st.secrets["cloud_id"], api_key=(st.secrets["api_key_1"],st.secrets["api_key_2"]),request_timeout=300)  # 5 minute timeout


st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 250px;
            font-size: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

######################################### AFFICHAGE ##############################################################
def load_profiles():
    memory.profiles = [profil for profil in fetch_profil_data()["data"]["User"] if len(profil["personalData"])>0 and len(profil["personalData"][0]["email"])>0]


def display_interface():
    st.selectbox("Profil",memory.profiles,0,label_visibility="hidden",format_func=lambda x : x["personalData"][0]["email"][0]["value"],key="profil")
    st.header(f'Offres Personnalisées pour {memory.profil["personalData"][0]["email"][0]["value"]}',divider="red")

def load_sidebar():
    st.sidebar.title("Interface Administrateur")
    st.sidebar.image("ressources/logoMM.png")
    with st.sidebar:
        colored_header(
                    label="Profil",
                    description="",
                    color_name="red-80",)
        st.info("Benedict Cumberbatch")
        st.info(memory.profil["personalData"][0]["email"][0]["value"])
        colored_header(
                label="Expérience",
                description="",
                color_name="red-80",)
        job,duration = st.columns([4,1])
        for experience in memory.profil["experience"]:
            job.info(experience["title"][0]["value"])
            duration.success(f'Na')
        colored_header(
                label="Education",
                description="",
                color_name="red-80",)      
        st.info("BTS") 
        
    

# MATCHING ##############################################################

def parseOffer(offer:dict):
    options = [offer["city"],offer["education"],offer["experience"]]
    return options

def getMissionData(id:str)->dict:
    query = {  "match": {
            "referencenumber": id}}
    res = memory.es.search(index=st.secrets["jobIndex"], query=query, source=["id","title","url","city","description","agency_code"])["hits"]["hits"][0]["_source"]
    return res

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
        with st.form(f"Offre n°{i}"):
            mission,card = st.columns([5,1])
            with mission:  
                data = getMissionData(offer["id"])
                colored_header(data["title"],"","blue-30")
                with st.expander("Description",expanded=False):
                    st.markdown(data["description"])

                ville,agence,url = st.columns([2,2,1])
                ville.info(data["city"])
                agence.info(data["agency_code"])  
                if url.form_submit_button("URL Proman"): webbrowser.open(data["url"])
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
    else:
        load_profiles()
        display_interface()
        memory.n = random.randint(1,500)
        load_sidebar()
        # Call your job matching function and store the results
        job_offerings = ast.literal_eval(J2Psearch(memory.n,10))
        displayOffers(job_offerings)


        

if __name__ == "__main__":
    app()
