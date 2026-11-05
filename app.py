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

st.sidebar.header("Filtres")

communes_toutes = sorted(df["commune"].unique())
communes_sel = st.sidebar.multiselect(
    "Communes :",
    options=communes_toutes,
    default=communes_toutes,
)

annees_toutes = sorted(df["annee"].unique(), reverse=True)
annee_sel = st.sidebar.selectbox(
    "Année :",
    options=annees_toutes,
    index=annees_toutes.index(2025) if 2025 in annees_toutes else 0,
)

if not communes_sel:
    st.warning(" Veuillez sélectionner au moins une commune dans la barre latérale pour afficher les données.")
    st.stop()

df_filtre = df[(df["annee"] == annee_sel) & (df["commune"].isin(communes_sel))]
df_communes = df[df["commune"].isin(communes_sel)]

brut = pd.read_csv(DOSSIER / "consommation_brut.csv")
st.write(f"Le fichier brut compte {len(brut)} lignes.")
st.dataframe(brut.head(10), hide_index=True)
