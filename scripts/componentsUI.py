import streamlit as st
from streamlit_extras.colored_header import colored_header
memory = st.session_state

def displayOffer(data,score):
    if memory.showScores and type(score)==float:
        st.header(f"{(score//0.1)/10}" + "% - " + data["title"][0]["value"],divider="green")
    else:
        st.header(data['title'][0]["value"],divider="green")

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


def displayProfile(profil):
    
    try:
        st.header(f'Offres Personnalisées pour {displayName(profil)}',divider="red")
    except:
        st.header(f'Offres Personnalisées pour {profil["id"]} (Pas de nom)',divider="red")

    with st.sidebar:
        colored_header(
                label="Profil",
                description="",
                color_name="red-80",)
        try:
            st.info(profil["personalData"][0]["email"][0]["value"])
        except:
            st.info("Pas d'adresse email")
        try:
            town,url = st.columns([3,1])
            town.info(memory.profil["personalData"][0]["location"][0]["city"][0]["value"] + ", " + memory.profil["personalData"][0]["location"][0]["postalcode"][0]["value"])
            longitude,lattitude = memory.profil["personalData"][0]["location"][0]["geolocation"][0]["value"].split(",")
            url.link_button("🌎",f"https://www.google.com/maps?q={lattitude},{longitude}",use_container_width=True)
        except:
            try:
                town,url = st.columns([3,1])
                town.info(memory.profil["personalData"][0]["location"][0]["city"][0]["value"])
                longitude,lattitude = memory.profil["personalData"][0]["location"][0]["geolocation"][0]["value"].split(",")
                url.link_button("🌎",f"https://www.google.com/maps?q={lattitude},{longitude}",use_container_width=True)
            except:
                st.info("Pas d'adresse")
        colored_header(
                label="Expérience",
                description="",
                color_name="red-80",)
        if profil["experience"]:
            for experience in profil["experience"]:
                job,duration = st.columns([3,1])
                if len(experience["title"])>0:
                    job.info(experience["title"][0]["value"])
                    duration.success(experience["duration"][0]["value"])
        else:
            st.warning("Pas d'expérience")


def displayName(user):
    try:
        return user["personalData"][0]["given"][0]["value"].capitalize() + " " + user["personalData"][0]["family"][0]["value"].capitalize() 
    except:
        return user["id"]
    
def format_address(user):
    try:
        return user["address"][0]["city"][0]["value"] + ", " + user["address"][0]["postalcode"][0]["value"]
    except:
        return "Address not specified"