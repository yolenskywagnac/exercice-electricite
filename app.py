from pathlib import Path
import matplotlib.pyplot as plt
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Quartiers et abonnés",
    "Évolution temporelle",
    "Chaleur ou courant ?",
    "Coupures de courant",
    "Relevés exceptionnels",
])

with tab1:
    st.markdown("### Consommation moyenne par abonné selon le type et le quartier")
    st.info(
        "Les quartiers commerciaux consomment en moyenne **393.2 kWh** par abonné contre **117.4 kWh** pour les quartiers résidentiels. "
        "En tête du classement se distinguent le **Centre-ville (468.7 kWh)**, **Place Saint-Pierre (458.3 kWh)** et **Delmas 33 (374.4 kWh)**."
    )

    col_chart1, col_chart2 = st.columns([1, 2])
    with col_chart1:
        moy_type = df_communes.groupby("type")["kwh_par_abonne"].mean().round(1)
        fig_type, ax_type = plt.subplots(figsize=(4, 3.5))
        ax_type.bar(moy_type.index, moy_type.values, color=["#ff7f0e", "#1f77b4"])
        ax_type.set_ylabel("kWh / abonné")
        ax_type.set_title("Moyenne par type de quartier")
        for i, v in enumerate(moy_type.values):
            ax_type.text(i, v + 5, f"{v:.1f}", ha="center", fontweight="bold")
        fig_type.tight_layout()
        st.pyplot(fig_type)
        plt.close(fig_type)

    with col_chart2:
        classement_q = (
            df_communes.groupby("quartier")["kwh_par_abonne"]
            .mean()
            .round(1)
            .sort_values()
        )
        fig_q, ax_q = plt.subplots(figsize=(6, 3.5))
        ax_q.barh(classement_q.index, classement_q.values, color="#2ca02c")
        ax_q.set_xlabel("kWh / abonné")
        ax_q.set_title("Classement des quartiers")
        for i, v in enumerate(classement_q.values):
            ax_q.text(v + 5, i, f"{v:.1f}", va="center", fontsize=8)
        fig_q.tight_layout()
        st.pyplot(fig_q)
        plt.close(fig_q)


with tab2:
    st.markdown("### Évolution annuelle et mensuelle de la consommation")
    st.info(
        "Entre 2024 et 2025, **Cap-Haïtien** est en tête de la progression avec une hausse de **+22.4 %** (de 4.59 à 5.62 millions de kWh), "
        "tandis que **Delmas** enregistre la plus faible variation avec **+1.1 %**."
    )

    evol_commune = (
        df_communes.groupby(["mois", "commune"])["kwh_par_abonne"]
        .mean()
        .unstack()
    )
    fig_evol, ax_evol = plt.subplots(figsize=(10, 4))
    for c in evol_commune.columns:
        ax_evol.plot(evol_commune.index, evol_commune[c], marker="o", label=c)
    ax_evol.set_title("Consommation moyenne par abonné, mois par mois (2024-2025)")
    ax_evol.set_xlabel("Mois")
    ax_evol.set_ylabel("kWh / abonné")
    ax_evol.tick_params(axis="x", rotation=45)
    ax_evol.legend(title="Commune")
    ax_evol.grid(True, linestyle="--", alpha=0.5)
    fig_evol.tight_layout()
    st.pyplot(fig_evol)
    plt.close(fig_evol)

with tab3:
    st.markdown("### Chaleur ou courant : qu'est-ce qui explique la consommation ?")

    # Quartiers résidentiels
    res = df_communes[df_communes["type"] == "Résidentiel"]
    corr_courant = res["kwh_par_abonne"].corr(res["heures_courant"])
    corr_temp = res["kwh_par_abonne"].corr(res["temperature_c"])

    st.info(
        f"Dans les quartiers résidentiels, la consommation par abonné présente une **forte corrélation positive de {corr_courant:.2f} avec les heures de courant**, "
        f"alors que la corrélation avec la température est quasi-nulle voire légèrement négative (**{corr_temp:.2f}**)."
    )

    fig_scatter, ax_scatter = plt.subplots(figsize=(8, 4))
    ax_scatter.scatter(
        res["heures_courant"],
        res["kwh_par_abonne"],
        color="#1f77b4",
        alpha=0.7,
        edgecolor="k",
    )
    ax_scatter.set_title("Quartiers résidentiels : Heures de courant vs Consommation par abonné")
    ax_scatter.set_xlabel("Heures de courant quotidiennes")
    ax_scatter.set_ylabel("kWh / abonné")
    ax_scatter.grid(True, linestyle="--", alpha=0.5)
    fig_scatter.tight_layout()
    st.pyplot(fig_scatter)
    plt.close(fig_scatter)

with tab4:
    st.markdown("### Distribution des heures de courant et coupures critiques")
    st.info(
        "C'est à **Cap-Haïtien** que les coupures sont les plus sévères avec une médiane de **10.0 heures** de courant par jour, "
        "contre **11.6 à 11.9 heures** dans les autres communes. En 2025, seuls **3 relevés** ont eu moins de 8 heures de courant : "
        "à **Carénage (7.3 h)**, **Delmas 33 (7.4 h)** et **Rue 15 (5.9 h)**."
    )

    col_hist1, col_hist2 = st.columns([1, 1])
    with col_hist1:
        if "Cap-Haïtien" in df_communes["commune"].values:
            cap_data = df_communes[df_communes["commune"] == "Cap-Haïtien"]
            fig_hist, ax_hist = plt.subplots(figsize=(5, 3.5))
            ax_hist.hist(
                cap_data["heures_courant"],
                bins=10,
                color="teal",
                edgecolor="black",
                alpha=0.8,
            )
            ax_hist.set_title("Distribution des heures de courant (Cap-Haïtien)")
            ax_hist.set_xlabel("Heures de courant / jour")
            ax_hist.set_ylabel("Nombre de relevés")
            ax_hist.grid(True, linestyle="--", alpha=0.5)
            fig_hist.tight_layout()
            st.pyplot(fig_hist)
            plt.close(fig_hist)
        else:
            st.write("Cap-Haïtien non sélectionné.")

    with col_hist2:
        stats_courant = (
            df_communes.groupby("commune")["heures_courant"]
            .agg(
                Médiane="median",
                Q1=lambda x: x.quantile(0.25),
                Q3=lambda x: x.quantile(0.75),
            )
            .round(1)
        )
        st.markdown("**Statistiques par commune (heures de courant) :**")
        st.dataframe(stats_courant)

with tab5:
    st.markdown("### Les records de consommation électrique")
    st.info(
        "Les 3 plus grosses consommations sont concentrées dans les quartiers commerciaux : "
        "**Delmas 33 en 2025-07 (742 780 kWh)**, **Centre-ville en 2024-11 (597 730 kWh)** et **Delmas 33 en 2025-09 (591 420 kWh)**."
    )

    top3_df = df_communes.nlargest(3, "kwh")[
        ["mois", "quartier", "commune", "type", "kwh"]
    ]
    fig_top, ax_top = plt.subplots(figsize=(7, 3.5))
    labels = [f"{r.quartier}\n({r.mois})" for _, r in top3_df.iterrows()]
    ax_top.bar(labels, top3_df["kwh"], color="#d62728")
    ax_top.set_ylabel("kWh")
    ax_top.set_title("Top 3 des consommations les plus élevées")
    for i, v in enumerate(top3_df["kwh"]):
        ax_top.text(
            i,
            v / 2,
            f"{v:,} kWh".replace(",", " "),
            ha="center",
            color="white",
            fontweight="bold",
        )
    fig_top.tight_layout()
    st.pyplot(fig_top)
    plt.close(fig_top)
    st.dataframe(top3_df, hide_index=True)
