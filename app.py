import streamlit as st
import yfinance as yf
import requests
import mlflow
import time
import pandas as pd

st.set_page_config(page_title="Trading Chatbot", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Trading Chatbot")
st.caption("Analyse boursière en temps réel propulsée par Llama3")

with st.sidebar:
    st.header("💼 Portefeuille Virtuel")
    if "cash" not in st.session_state:
        st.session_state.cash = 10000.0
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = {}

    st.metric("💰 Cash disponible", f"{st.session_state.cash:.2f} $")

    st.subheader("Acheter une action")
    ticker_input = st.selectbox("Action", ["AAPL","TSLA","MSFT","GOOGL","AMZN","META","NVDA"])
    quantite = st.number_input("Quantité", min_value=1, max_value=100, value=1)

    if st.button("Acheter 🟢"):
        stock = yf.Ticker(ticker_input)
        prix = stock.history(period="1d").iloc[-1]["Close"]
        cout = prix * quantite
        if cout <= st.session_state.cash:
            st.session_state.cash -= cout
            if ticker_input in st.session_state.portfolio:
                st.session_state.portfolio[ticker_input]["quantite"] += quantite
            else:
                st.session_state.portfolio[ticker_input] = {"quantite": quantite, "prix_achat": prix}
            st.success(f"Acheté {quantite} {ticker_input} à {prix:.2f}$")
        else:
            st.error("Cash insuffisant !")

    if st.button("Vendre 🔴"):
        if ticker_input in st.session_state.portfolio:
            stock = yf.Ticker(ticker_input)
            prix = stock.history(period="1d").iloc[-1]["Close"]
            gain = prix * quantite
            st.session_state.cash += gain
            st.session_state.portfolio[ticker_input]["quantite"] -= quantite
            if st.session_state.portfolio[ticker_input]["quantite"] <= 0:
                del st.session_state.portfolio[ticker_input]
            st.success(f"Vendu {quantite} {ticker_input} à {prix:.2f}$")
        else:
            st.error("Action non possédée !")

    st.subheader("📊 Mes positions")
    if st.session_state.portfolio:
        for t, v in st.session_state.portfolio.items():
            stock = yf.Ticker(t)
            prix_actuel = stock.history(period="1d").iloc[-1]["Close"]
            perf = ((prix_actuel - v["prix_achat"]) / v["prix_achat"]) * 100
            st.metric(f"{t} x{v['quantite']}", f"{prix_actuel:.2f}$", f"{perf:+.2f}%")
    else:
        st.info("Aucune position")

st.subheader("📊 Graphique en temps réel")
ticker_chart = st.selectbox("Choisir une action", ["AAPL","TSLA","MSFT","GOOGL","AMZN","META","NVDA"], key="chart")
periode = st.radio("Période", ["5d", "1mo", "3mo", "6mo"], horizontal=True)
stock_data = yf.Ticker(ticker_chart).history(period=periode)
st.line_chart(stock_data["Close"])

st.subheader("💬 Chat avec l'IA")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation" not in st.session_state:
    st.session_state.conversation = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Analyse AAPL, Compare TSLA et MSFT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    tickers = ["AAPL","TSLA","MSFT","GOOGL","AMZN","META","NVDA"]
    context = ""
    ticker_detecte = None
    metrics = {}

    for word in prompt.upper().split():
        if word in tickers:
            ticker_detecte = word
            stock = yf.Ticker(word)
            hist = stock.history(period="5d")
            if not hist.empty:
                last = hist.iloc[-1]
                first = hist.iloc[0]
                cours = last["Close"]
                variation = ((last["Close"] - first["Open"]) / first["Open"]) * 100
                volume = hist["Volume"].mean()
                haut = hist["High"].max()
                bas = hist["Low"].min()
                moyenne = hist["Close"].mean()
                tendance = "haussière 📈" if cours > moyenne else "baissière 📉"
                context = (
                    f"\n[Données {word} : Cours {cours:.2f}$ | "
                    f"Variation {variation:+.2f}% | "
                    f"Haut {haut:.2f}$ | Bas {bas:.2f}$ | "
                    f"Tendance {tendance}]"
                )
                metrics = {
                    "cours_actuel": cours,
                    "variation_pct": variation,
                    "volume_moyen": volume,
                    "plus_haut": haut,
                    "plus_bas": bas
                }

    st.session_state.conversation.append({
        "role": "user",
        "content": prompt + context
    })

    system_prompt = {
        "role": "system",
        "content": "Tu es un assistant spécialisé en trading et analyse boursière. Réponds en français."
    }

    with st.chat_message("assistant"):
        with st.spinner("Analyse en cours..."):
            debut = time.time()
            try:
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "llama3",
                        "messages": [system_prompt] + st.session_state.conversation,
                        "stream": False
                    }
                )
                answer = response.json()["message"]["content"]
                duree = time.time() - debut
            except:
                answer = "❌ Ollama n'est pas lancé. Lance `ollama run llama3` dans un terminal."
                duree = 0
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.conversation.append({"role": "assistant", "content": answer})

    if ticker_detecte and metrics:
        mlflow.set_experiment("trading-chatbot")
        with mlflow.start_run():
            mlflow.log_param("ticker", ticker_detecte)
            mlflow.log_param("question", prompt)
            for k, v in metrics.items():
                mlflow.log_metric(k, v)
            mlflow.log_metric("duree_reponse_sec", duree)
            mlflow.log_text(answer, "reponse_ia.txt")