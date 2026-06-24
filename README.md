# Trading Chatbot — MLOps Project

Chatbot d'analyse boursière en temps réel, propulsé par Llama3 (via Ollama) et tracké avec MLflow.

## Objectif

Projet MLOps complet démontrant :
- La collecte de données financières en temps réel
- L'intégration d'un LLM local (Llama3)
- Le tracking d'expériences avec MLflow

## Architecture

yfinance (données réelles)

↓

chatbot.py (Python)

↓

Ollama + Llama3 (LLM local)

↓

MLflow (tracking & observabilité)

## Stack technique

- Python 3.x
- Ollama + Llama3
- yfinance
- MLflow
- requests

## Lancement
##  Lancer l'appli

### Prérequis
ollama run llama3

### Option 1 — Sans Docker
streamlit run app.py

### Option 2 — Avec Docker
docker run -p 8501:8501 trading-chatbot

### Puis ouvrir
http://localhost:8501

##  Lancer l'appli

### 1. Installer les dépendances (à faire une seule fois seulement)
pip install -r requirements.txt

### 2. Terminal 1 — Lancer Ollama
ollama run llama3

### 3. Terminal 2 — Lancer l'interface web
cd Mon_Chatbot
streamlit run app.py

### 4. Ouvrir dans le navigateur
http://localhost:8501

### 5. Terminal 3 — Visualiser les runs MLflow (optionnel)
cd Mon_Chatbot
mlflow ui
→ http://127.0.0.1:5000

## 💬 Exemples d'utilisation

Analyse AAPL
Analyse TSLA
Compare MSFT et NVDA

## Auteure

Serine Nehal — Étudiante ingénieure ISEP 