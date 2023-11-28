import streamlit as st
st.set_page_config(layout="wide")
from P2J import P2J 
from J2P import J2P
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
memory = st.session_state

def connect2sheets():
    with st.spinner("Connexion au serveur ..."):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_creds"], scope)
        client = gspread.authorize(creds)
        st.session_state.sheet = client.open("promanFeedback").sheet1

def main():
    st.sidebar.title("Interface Administrateur")
    st.sidebar.image("ressources/logoMM.png")
    # Create a page selector
    if "authorized" not in memory:
            memory["authorized"] = False
            memory.page = ''
        
    if memory["authorized"] == False:
        userPassword = st.text_input("Rentrez le Mot de Passe","")
        if userPassword == st.secrets["password"]:
            memory["authorized"] = True
            st.rerun()
        elif userPassword != "":
            st.warning("Mot de passe erroné")
    else:           
        # Authenticate with Google Sheets
        if "sheet" not in st.session_state:
            connect2sheets()
        l,r = st.sidebar.columns(2)
        if l.button("Profil > Mission",use_container_width=True) : memory.page = "Interface Profil > Mission"
        if r.button("Mission > Profil",use_container_width=True) : memory.page = "Interface Mission > Profil"
        with st.sidebar.expander("Paramètres",expanded=False),st.form("settings"):
            st.header("Paramètre admin",divider="red")
            st.slider("Eclatage des scores",0,10,9,1,key="SC")
            st.checkbox("Afficher les pourcentages",value=True,key="showScores")
            st.number_input('Nombre de résultats à afficher',1,25,10,1,key="n")
            st.form_submit_button("Appliquer",use_container_width=True)
        if st.sidebar.button("Clear Cache",use_container_width=True) : st.cache_data.clear()
        st.sidebar.divider()
        # Direct to the appropriate page
        if memory.page == "Interface Profil > Mission":
            P2J()
        elif memory.page == "Interface Mission > Profil":
            J2P()


    
       
if __name__ == "__main__":
    main()
