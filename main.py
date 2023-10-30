import streamlit as st
st.set_page_config(layout="wide")
from P2J import P2J
from J2P import J2P
memory = st.session_state

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
        l,r = st.sidebar.columns(2)
        if l.button("Profil > Mission",use_container_width=True) : memory.page = "Interface Profil > Mission"
        if r.button("Mission > Profil",use_container_width=True) : memory.page = "Interface Mission > Profil"
        with st.sidebar.expander("Scoring"),st.form("scoring"):
            st.header("Paramètre scoring",divider="red")
            st.slider("Scaling",0,10,5,1,key="SC")
            st.slider("Secondary Job Bonus",0.0,4.0,2.0,0.5,key='SB')
            st.slider("Experience Bonus",0.0,4.0,2.0,0.5,key="EB",disabled=True)
            st.slider("Liked Mission Bonus",0.0,4.0,2.0,0.5,key="LMB",disabled=True)
            st.form_submit_button("Recalculer",use_container_width=True)
        st.sidebar.divider()
        # Direct to the appropriate page
        if memory.page == "Interface Profil > Mission":
            P2J()
        elif memory.page == "Interface Mission > Profil":
            J2P()


def init_parameters(SC=5,EB=2,SB=2,LMB=2):
    memory.SC,memory.EB,memory.SB,memory.LMB = SC,EB,SB,LMB
    
    
       
if __name__ == "__main__":
    main()
