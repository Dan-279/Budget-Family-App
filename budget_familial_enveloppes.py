
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Budget Familial - Enveloppes", layout="centered")

st.title("📦 Budget Familial par Enveloppes")
st.markdown("Planifiez vos dépenses en créant des enveloppes budgétaires, puis ajoutez vos transactions pour suivre vos finances manuellement.")

# Sidebar: Envelopes setup
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

# Session state to store transactions
if "transactions" not in st.session_state:
    st.session_state["transactions"] = []

# New transaction form
st.header("➕ Ajouter une transaction")
with st.form("transaction_form"):
    date = st.date_input("Date")
    category = st.selectbox("Catégorie", list(envelopes.keys()))
    amount = st.number_input("Montant (€)", min_value=0.0, step=1.0)
    description = st.text_input("Description (facultatif)")
    submitted = st.form_submit_button("Ajouter")

    if submitted:
        st.session_state["transactions"].append({
            "Date": date,
            "Catégorie": category,
            "Montant (€)": amount,
            "Description": description
        })
        st.success("Transaction ajoutée avec succès.")

# Display transactions
st.header("📋 Transactions")
if st.session_state["transactions"]:
    df = pd.DataFrame(st.session_state["transactions"])
    st.dataframe(df)

    # Summarize spending per envelope
    summary = df.groupby("Catégorie")["Montant (€)"].sum().reindex(envelopes.keys(), fill_value=0)
    balances = {cat: envelopes[cat] - summary[cat] for cat in envelopes}

    st.header("📊 Solde des Enveloppes")
    for cat, budget in envelopes.items():
        spent = summary[cat]
        remaining = balances[cat]
        st.markdown(f"**{cat}** : {spent:,.0f} € dépensés sur {budget} € → **Reste : {'🔴' if remaining < 0 else '🟢'} {remaining:,.0f} €**")
else:
    st.info("Aucune transaction enregistrée.")
