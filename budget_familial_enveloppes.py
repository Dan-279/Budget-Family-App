
import streamlit as st
import pandas as pd
from datetime import date
from io import StringIO
import json
import base64

st.set_page_config(page_title="Budget Familial - Multi-utilisateur", layout="centered")

st.title("📦 Budget Familial par Enveloppes")

# JavaScript for localStorage sync
st.markdown("""
<script>
const key = "budget_familial_data";
function loadLocalStorage() {
    const stored = localStorage.getItem(key);
    if (stored) {
        window.parent.postMessage({ type: "LOAD_DATA", data: stored }, "*");
    }
}
function saveLocalStorage(data) {
    localStorage.setItem(key, data);
}
window.addEventListener("message", (event) => {
    if (event.data.type === "SAVE_DATA") {
        saveLocalStorage(event.data.data);
    }
});
window.onload = loadLocalStorage;
</script>
""", unsafe_allow_html=True)

# Session state structure
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}

# Username
st.header("👤 Informations utilisateur")
username = st.text_input("Votre nom ou pseudo", value=st.session_state["user_data"].get("username", ""))

# Envelopes
default_envelopes = {
    "Loyer": 1100,
    "Courses alimentaires": 500,
    "Transport": 150,
    "Loisirs": 200,
    "Santé": 100,
    "Épargne": 300,
    "Autres": 100
}
st.sidebar.header("🗂️ Paramètres des enveloppes")
envelopes = {}
for cat, val in default_envelopes.items():
    envelopes[cat] = st.sidebar.number_input(f"{cat}", min_value=0, value=val, step=10)

# Income
st.header("💰 Revenus")
salaire1 = st.number_input("Salaire - Parent 1", min_value=0)
salaire2 = st.number_input("Salaire - Parent 2", min_value=0)
revenu_sec = st.number_input("Revenus secondaires", min_value=0)
aides = st.number_input("Allocations / Aides", min_value=0)
revenus_total = salaire1 + salaire2 + revenu_sec + aides

# Transactions
if "transactions" not in st.session_state["user_data"]:
    st.session_state["user_data"]["transactions"] = []

st.header("➕ Ajouter une transaction")
with st.form("transaction_form"):
    t_date = st.date_input("Date", value=date.today())
    t_category = st.selectbox("Catégorie", list(envelopes.keys()))
    t_amount = st.number_input("Montant", min_value=0.0)
    t_description = st.text_input("Description")
    submit = st.form_submit_button("Ajouter")
    if submit:
        st.session_state["user_data"]["transactions"].append({
            "Date": str(t_date),
            "Catégorie": t_category,
            "Montant": t_amount,
            "Description": t_description
        })

# Display
df = pd.DataFrame(st.session_state["user_data"]["transactions"])
if not df.empty:
    df["Montant"] = pd.to_numeric(df["Montant"])
    st.dataframe(df)

    # Résumé
    summary = df.groupby("Catégorie")["Montant"].sum().reindex(envelopes.keys(), fill_value=0)
    total_spent = summary.sum()
    epargne = revenus_total - total_spent

    st.subheader("📊 Récapitulatif")
    st.markdown(f"**Revenus totaux :** {revenus_total} €")
    st.markdown(f"**Dépenses totales :** {total_spent} €")
    st.markdown(f"**Épargne possible :** {'🔴' if epargne < 0 else '🟢'} {epargne} €")

    # HTML recap
    if st.button("🖨️ Voir un récapitulatif imprimable"):
        recap_html = f"""<html><head><title>Récapitulatif</title></head><body>
        <h1>Récapitulatif de {username}</h1>
        <p><strong>Revenus totaux :</strong> {revenus_total} €</p>
        <p><strong>Dépenses totales :</strong> {total_spent} €</p>
        <p><strong>Épargne possible :</strong> {epargne} €</p>
        <h2>Dépenses par catégorie :</h2>
        <ul>
        {"".join([f"<li>{cat}: {val} €</li>" for cat, val in summary.items()])}
        </ul>
        </body></html>"""
        b64 = base64.b64encode(recap_html.encode()).decode()
        st.markdown(f'<a href="data:text/html;base64,{b64}" download="recapitulatif.html" target="_blank">📥 Télécharger en HTML</a>', unsafe_allow_html=True)

# Export/Import
st.header("📤 Sauvegarder / Charger")
export_data = {
    "username": username,
    "revenus": [salaire1, salaire2, revenu_sec, aides],
    "transactions": st.session_state["user_data"]["transactions"]
}
export_json = json.dumps(export_data, indent=2)
st.download_button("💾 Exporter (.json)", export_json, file_name="budget_data.json")

upload = st.file_uploader("📂 Importer un fichier .json", type=["json"])
if upload:
    content = json.load(upload)
    st.session_state["user_data"] = content
    st.markdown("<script>setTimeout(() => window.location.reload(), 100);</script>", unsafe_allow_html=True)
    st.success("Import réussi ! L'application va se recharger...")

# Save user data to localStorage
save_payload = json.dumps(st.session_state["user_data"])
st.markdown(f"<script>window.parent.postMessage({{type: 'SAVE_DATA', data: `{save_payload}`}}, '*');</script>", unsafe_allow_html=True)
