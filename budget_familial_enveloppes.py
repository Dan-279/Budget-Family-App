
import streamlit as st
import pandas as pd
from datetime import date, datetime
import json
import base64
import html
import matplotlib.pyplot as plt

st.set_page_config(page_title="Budget Familial - Multi-utilisateur", layout="centered")

st.title("📦 Budget Familial par Enveloppes")

st.markdown("### 🔁 **Recharger l'interface manuellement**")
st.markdown("*Utilisez ce bouton si vos données ne s’affichent pas immédiatement après un import.*")
if st.button("🔄 Rafraîchir maintenant"):
    st.experimental_rerun()


current_month = datetime.now().strftime("%Y-%m")

# Safe initialization
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {
        "transactions": [],
        "username": "",
        "history": {},
        "debts": []
    }

# Username input
st.header("👤 Informations utilisateur")
username = st.text_input("Votre nom ou pseudo", value=st.session_state["user_data"].get("username", ""))
st.session_state["user_data"]["username"] = username

# Envelope setup
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

# Income input
st.header("💰 Revenus")
salaire1 = st.number_input("Salaire - Parent 1", min_value=0)
salaire2 = st.number_input("Salaire - Parent 2", min_value=0)
revenu_sec = st.number_input("Revenus secondaires", min_value=0)
aides = st.number_input("Allocations / Aides", min_value=0)
revenus_total = salaire1 + salaire2 + revenu_sec + aides

# Add transaction
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

# Add debt entry
st.header("💳 Dettes / Prêts")
with st.expander("Ajouter une dette ou un prêt"):
    with st.form("debt_form"):
        debt_name = st.text_input("Nom de la dette")
        debt_total = st.number_input("Montant total de la dette", min_value=0)
        debt_paid = st.number_input("Montant remboursé ce mois-ci", min_value=0)
        debt_submit = st.form_submit_button("Ajouter cette dette")
        if debt_submit and debt_name:
            st.session_state["user_data"]["debts"].append({
                "Nom": debt_name,
                "Montant total": debt_total,
                "Payé ce mois": debt_paid,
                "Mois": current_month
            })

# Display transactions
df = pd.DataFrame(st.session_state["user_data"]["transactions"])
if not df.empty:
    df["Montant"] = pd.to_numeric(df["Montant"])
    st.dataframe(df)

    # Summary with pie chart
    summary = df.groupby("Catégorie")["Montant"].sum().reindex(envelopes.keys(), fill_value=0)
    total_spent = summary.sum()
    epargne = revenus_total - total_spent

    # Log history
    
if "history" not in st.session_state["user_data"]:
    st.session_state["user_data"]["history"] = {}
if current_month not in st.session_state["user_data"]["history"]:

        st.session_state["user_data"]["history"][current_month] = {
            "revenus": revenus_total,
            "dépenses": float(total_spent),
            "épargne": float(epargne)
        }

    st.subheader("📊 Récapitulatif")
    st.markdown(f"Revenus totaux : {revenus_total} EUR")
    st.markdown(f"Dépenses totales : {total_spent} EUR")
    st.markdown(f"Épargne possible : {epargne} EUR")

    # Pie chart
    fig, ax = plt.subplots()
    labels = list(summary.index) + ["Épargne"]
    sizes = list(summary.values) + [max(epargne, 0)]
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # Debt display
    if st.session_state["user_data"]["debts"]:
        st.subheader("💳 Dettes en cours")
        for d in st.session_state["user_data"]["debts"]:
            st.markdown(f"**{d['Nom']}** – Total: {d['Montant total']} € – Remboursé ce mois: {d['Payé ce mois']} €")

    
if st.button("🖨️ Voir un récapitulatif imprimable"):
    transactions_html = "<h2>Transactions</h2><table border='1'><tr><th>Date</th><th>Catégorie</th><th>Montant</th><th>Description</th><th>Utilisateur</th></tr>"
    for t in st.session_state["user_data"]["transactions"]:
        transactions_html += f"<tr><td>{html.escape(t['Date'])}</td><td>{html.escape(t['Catégorie'])}</td><td>{t['Montant']} €</td><td>{html.escape(t['Description'])}</td><td>{html.escape(username)}</td></tr>"
    
    transactions_html += "</table>"

    # Income section
    income_html = "<h2>Revenus</h2><ul>"
    income_sources = [("Salaire - Parent 1", salaire1), ("Salaire - Parent 2", salaire2), 
                      ("Revenus secondaires", revenu_sec), ("Aides", aides)]
    for name, amount in income_sources:
        income_html += f"<li>{html.escape(name)} : {amount} €</li>"
    income_html += "</ul>"

    # Debt section
    debt_html = "<h2>Dettes / Prêts</h2><ul>"
    for d in st.session_state["user_data"].get("debts", []):
        debt_html += f"<li>{html.escape(d['Nom'])} – Total: {d['Montant total']} €, Remboursé ce mois: {d['Payé ce mois']} €</li>"
    debt_html += "</ul>"


        
    # Build income section
    income_sources = [("Salaire - Parent 1", salaire1), ("Salaire - Parent 2", salaire2),
                      ("Revenus secondaires", revenu_sec), ("Aides", aides)]
    income_html = "<h2>Revenus</h2><ul>" + "".join([f"<li>{html.escape(name)} : {amount} €</li>" for name, amount in income_sources]) + "</ul>"

    # Build debt section
    debt_html = "<h2>Dettes / Prêts</h2><ul>" + "".join(
        [f"<li>{html.escape(d['Nom'])} – Total: {d['Montant total']} €, Remboursé ce mois: {d['Payé ce mois']} €</li>" for d in st.session_state["user_data"].get("debts", [])]
    ) + "</ul>"

    # Build transaction section
    transactions_html = "<h2>Transactions</h2><table border='1'><tr><th>Date</th><th>Catégorie</th><th>Montant</th><th>Description</th><th>Utilisateur</th></tr>"
    for t in st.session_state["user_data"]["transactions"]:
        transactions_html += f"<tr><td>{html.escape(t['Date'])}</td><td>{html.escape(t['Catégorie'])}</td><td>{t['Montant']} €</td><td>{html.escape(t['Description'])}</td><td>{html.escape(username)}</td></tr>"
    transactions_html += "</table>"

    recap_html = f"""<html><head><meta charset='utf-8'><title>Recap</title></head><body>
    <h1>Recapitulatif de {html.escape(username)}</h1>
    <p>Revenus totaux : {revenus_total} EUR</p>
    <p>Dépenses totales : {total_spent} EUR</p>
    <p>Epargne possible : {epargne} EUR</p>
    <h2>Dépenses par catégorie :</h2>
    <ul>
    {"".join([f"<li>{html.escape(cat)}: {val} EUR</li>" for cat, val in summary.items()])}
    </ul>
    {income_html}
    {debt_html}
    {transactions_html}
    </body></html>"""

        <h1>Recapitulatif de {html.escape(username)}</h1>
        <p>Revenus totaux : {revenus_total} EUR</p>
        <p>Dépenses totales : {total_spent} EUR</p>
        <p>Epargne possible : {epargne} EUR</p>
        <h2>Dépenses par catégorie :</h2>
        <ul>
        {"".join([f"<li>{html.escape(cat)}: {val} EUR</li>" for cat, val in summary.items()])}
        </ul>
        </body></html>"""
        b64 = base64.b64encode(recap_html.encode()).decode()
        st.markdown(f'<a href="data:text/html;base64,{b64}" download="recapitulatif.html" target="_blank">📥 Télécharger en HTML</a>', unsafe_allow_html=True)

# Savings history chart
st.header("📈 Historique de l'épargne")
if st.session_state["user_data"]["history"]:
    hist_df = pd.DataFrame.from_dict(st.session_state["user_data"]["history"], orient="index")
    st.line_chart(hist_df["épargne"])

# Export/Import
st.header("📤 Sauvegarder / Charger")
export_data = {
    "username": username,
    "revenus": [salaire1, salaire2, revenu_sec, aides],
    "transactions": st.session_state["user_data"]["transactions"],
    "history": st.session_state["user_data"]["history"],
    "debts": st.session_state["user_data"]["debts"]
}
export_json = json.dumps(export_data, indent=2)
st.download_button("💾 Exporter (.json)", export_json, file_name="budget_data.json")

upload = st.file_uploader("📂 Importer un fichier .json", type=["json"])


if st.button("🔄 Rafraîchir manuellement"):
    st.experimental_rerun()

if upload:

    content = json.load(upload)
    st.session_state["user_data"] = content
    st.success("Import réussi ! Cliquez ci-dessous pour actualiser.")
    if st.button("🔄 Rafraîchir maintenant"):
        st.experimental_rerun()

    content = json.load(upload)
    st.session_state["user_data"] = content
    st.success("Import réussi ! Rechargez la page si besoin.")
