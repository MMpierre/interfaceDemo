import streamlit as st
st.set_page_config(layout="wide")
from P2J import P2J
from J2P import J2P

def main():
    st.sidebar.title("Interface Administrateur")
    st.sidebar.image("ressources/logoMM.png")
    # Create a page selector
    if "authorized" not in st.session_state:
            st.session_state["authorized"] = False
        
    if st.session_state["authorized"] == False:
        userPassword = st.text_input("Rentrez le Mot de Passe","")
        if userPassword == st.secrets["password"]:
            st.session_state["authorized"] = True
            st.rerun()
        elif userPassword != "":
            st.warning("Mot de passe erroné")
    else:           
        page_selector = st.sidebar.selectbox("Choisissez une page:", ["Interface Profil > Mission",  "Interface Mission > Profil"])
        st.sidebar.divider()
        # Direct to the appropriate page
        if page_selector == "Interface Profil > Mission":
            P2J()
        elif page_selector == "Interface Mission > Profil":
            J2P()


    
       
if __name__ == "__main__":
    main()
