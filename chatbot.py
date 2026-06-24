import requests
import yfinance as yf
import mlflow
import time

conversation = []

# Configuration MLflow
mlflow.set_experiment("trading-chatbot")

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    if hist.empty:
        return None, {}

    last = hist.iloc[-1]
    first = hist.iloc[0]

    cours_actuel = last['Close']
    variation = ((last['Close'] - first['Open']) / first['Open']) * 100
    volume_moyen = hist['Volume'].mean()
    plus_haut = hist['High'].max()
    plus_bas = hist['Low'].min()
    moyenne = hist['Close'].mean()
    tendance = "haussière" if cours_actuel > moyenne else "baissière"

    texte = (
        f"Action {ticker} sur 5 jours :\n"
        f"- Cours actuel : {cours_actuel:.2f}$\n"
        f"- Variation semaine : {variation:+.2f}%\n"
        f"- Plus haut : {plus_haut:.2f}$ | Plus bas : {plus_bas:.2f}$\n"
        f"- Volume moyen : {volume_moyen:,.0f} actions\n"
        f"- Tendance : {tendance}"
    )

    # Données à logger dans MLflow
    metrics = {
        "cours_actuel": cours_actuel,
        "variation_pct": variation,
        "volume_moyen": volume_moyen,
        "plus_haut": plus_haut,
        "plus_bas": plus_bas,
    }

    return texte, metrics

system_prompt = {
    "role": "system",
    "content": "Tu es un assistant spécialisé en trading et analyse boursière. Réponds en français."
}

print("Chatbot Trading démarré. Tape 'exit' pour quitter.")

while True:
    question = input("\nToi : ")

    if question.lower() in ["exit", "quit"]:
        break

    words = question.upper().split()
    tickers = ["AAPL","TSLA","MSFT","GOOGL","AMZN","META","NVDA"]
    context = ""
    ticker_detecte = None
    metrics = {}

    for word in words:
        if word in tickers:
            ticker_detecte = word
            data, metrics = get_stock_data(word)
            if data:
                context = f"\n[Données en temps réel : {data}]"

    conversation.append({
        "role": "user",
        "content": question + context
    })

    # Mesure du temps de réponse
    debut = time.time()

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3",
            "messages": [system_prompt] + conversation,
            "stream": False
        }
    )

    duree = time.time() - debut
    answer = response.json()["message"]["content"]
    print("\nIA :", answer)

    conversation.append({
        "role": "assistant",
        "content": answer
    })

    # Log MLflow uniquement si une action a été détectée
    if ticker_detecte and metrics:
        with mlflow.start_run():
            mlflow.log_param("ticker", ticker_detecte)
            mlflow.log_param("question", question)
            for key, value in metrics.items():
                mlflow.log_metric(key, value)
            mlflow.log_metric("duree_reponse_sec", duree)
            mlflow.log_text(answer, "reponse_ia.txt")
        print(f"\n✅ Analyse loggée dans MLflow ({duree:.1f}s)")