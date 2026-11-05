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

st.subheader(f"Indicateurs clés ({annee_sel})")
col1, col2, col3 = st.columns(3)

kwh_total_m = df_filtre["kwh"].sum() / 1e6
kwh_abonne_moy = df_filtre["kwh_par_abonne"].mean()
heures_courant_moy = df_filtre["heures_courant"].mean()

col1.metric("Consommation totale", f"{kwh_total_m:.2f} M kWh")
col2.metric("Consommation moyenne / abonné", f"{kwh_abonne_moy:.1f} kWh")
col3.metric("Heures de courant moyennes / jour", f"{heures_courant_moy:.1f} h")

st.markdown("---")
