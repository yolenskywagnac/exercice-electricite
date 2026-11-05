from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")

@st.cache_data
def charger_donnees():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")

df = charger_donnees()

st.markdown(
    "Ce tableau de bord présente l'analyse de deux années de relevés d'électricité (2024-2025) dans 12 quartiers de Port-au-Prince, Delmas, Pétion-Ville et Cap-Haïtien. "
    "Il permet d'éclairer la direction sur les déterminants majeurs de la consommation : suit-elle les vagues de chaleur ou la disponibilité du réseau électrique ?"
)
brut = pd.read_csv(DOSSIER / "consommation_brut.csv")
st.write(f"Le fichier brut compte {len(brut)} lignes.")
st.dataframe(brut.head(10), hide_index=True)
