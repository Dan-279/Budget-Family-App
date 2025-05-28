
import streamlit as st
import pandas as pd
import os
import json
from datetime import date, datetime
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Budget Familial Avancé", layout="centered")

st.title("📦 Budget Familial par Enveloppes - Version Complète")

# --- Sélection du mois ---
st.sidebar.header("📅 Mois de suivi")
selected_month = st.sidebar.selectbox(
    "Choisissez un mois :", 
    ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
     "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
)

data_file = f"budget_data_{selected_month.lower()}.json"

# --- Chargement des transactions existantes ---
if os.path.exists(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        st.session_state["transactions"] = json.load(f)
else:
    st.session_state["transactions"] = []

# --- Entrée des revenus ---
st.header("💰 Revenus mensuels")
salaire1 = st.number_input("Salaire - Parent 1 (€)", min_value=0, step=50)
salaire2 = st.number_input("Salaire - Parent 2 (€)", min_value=0, step=50)
revenu_sec = st.number_input("Revenus secondaires (€)", min_value=0, step=10)
aides = st.number_input("Allocations / Aides (€)", min_value=0, step=10)

revenus_total = salaire1 + salaire2 + revenu_sec + aides
st.markdown(f"**Total revenus : {revenus_total:,.0f} €**")

# --- Configuration des enveloppes ---
st.sidebar.header("🗂️ Paramètres des Enveloppes")
default_envelopes = {
    "Loyer": 1100,
    "Courses alimentaires": 500,
    "Transport": 150,
    "Loisirs": 200,
    "Santé": 100,
    "Épargne": 300,
    "Autres": 100
}

envelopes = {}
st.sidebar.markdown("**Définissez vos enveloppes mensuelles (€)**")
for name, default in default_envelopes.items():
    envelopes[name] = st.sidebar.number_input(f"{name}", min_value=0, value=default, step=10)

# --- Formulaire de transaction ---
st.header("➕ Ajouter une transaction")
with st.form("transaction_form"):
    t_date = st.date_input("Date", value=date.today())
    t_category = st.selectbox("Catégorie", list(envelopes.keys()))
    t_amount = st.number_input("Montant (€)", min_value=0.0, step=1.0)
    t_description = st.text_input("Description (facultatif)")
    submitted = st.form_submit_button("Ajouter")

    if submitted:
        st.session_state["transactions"].append({
            "Date": str(t_date),
            "Catégorie": t_category,
            "Montant (€)": t_amount,
            "Description": t_description
        })
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(st.session_state["transactions"], f, ensure_ascii=False, indent=2)
        st.success("Transaction ajoutée et sauvegardée.")

# --- Affichage des transactions ---
st.header("📋 Transactions")
if st.session_state["transactions"]:
    df = pd.DataFrame(st.session_state["transactions"])
    df["Montant (€)"] = pd.to_numeric(df["Montant (€)"])
    df["Date"] = pd.to_datetime(df["Date"])
    st.dataframe(df)

    # Résumé des dépenses
    summary = df.groupby("Catégorie")["Montant (€)"].sum().reindex(envelopes.keys(), fill_value=0)
    balances = {cat: envelopes[cat] - summary[cat] for cat in envelopes}

    st.header("📊 Solde des Enveloppes")
    total_depenses = 0
    for cat, budget in envelopes.items():
        spent = summary[cat]
        remaining = balances[cat]
        total_depenses += spent
        st.markdown(f"**{cat}** : {spent:,.0f} € dépensés sur {budget} € → **Reste : {'🔴' if remaining < 0 else '🟢'} {remaining:,.0f} €**")

    # Graphique en camembert
    st.subheader("📈 Répartition des dépenses")
    fig, ax = plt.subplots()
    summary_plot = summary[summary > 0]
    ax.pie(summary_plot, labels=summary_plot.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Épargne possible
    st.header("💾 Épargne possible")
    economie = revenus_total - total_depenses
    if economie < 0:
        st.error(f"🔴 Vous dépensez {abs(economie):,.0f} € de plus que vos revenus.")
    elif economie < 100:
        st.warning(f"⚠️ Épargne faible : {economie:,.0f} €")
    else:
        st.success(f"🟢 Épargne possible ce mois-ci : {economie:,.0f} €")

    # Export section
    st.header("📤 Exporter un récapitulatif")
    export_type = st.selectbox("Choisissez le format :", ["Résumé texte (.txt)", "CSV complet (.csv)"])

    if st.button("📄 Générer le fichier"):
        if export_type == "Résumé texte (.txt)":
            buffer = StringIO()
            buffer.write(f"RÉCAPITULATIF - {selected_month.upper()}\n\n")
            buffer.write(f"Revenus totaux : {revenus_total:.2f} €\n")
            buffer.write(f"Dépenses totales : {total_depenses:.2f} €\n")
            buffer.write(f"Épargne possible : {economie:.2f} €\n\n")
            buffer.write("Dépenses par catégorie :\n")
            for cat, amt in summary.items():
                buffer.write(f"- {cat} : {amt:.2f} €\n")
            st.download_button("📥 Télécharger le résumé (.txt)", buffer.getvalue(), file_name="recapitulatif.txt")

        elif export_type == "CSV complet (.csv)":
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Télécharger le CSV", csv, file_name="transactions.csv", mime="text/csv")
else:
    st.info("Aucune transaction enregistrée pour ce mois.")
