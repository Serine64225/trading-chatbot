# 📈 Trading Chatbot — MLOps Project

Chatbot d'analyse boursière en temps réel, propulsé par Llama3 (via Ollama) et tracké avec MLflow.

## 🎯 Objectif

Projet MLOps complet démontrant :
- La collecte de données financières en temps réel
- L'intégration d'un LLM local (Llama3)
- Le tracking d'expériences avec MLflow

## 🏗️ Architecture

yfinance (données réelles)

↓

chatbot.py (Python)

↓

Ollama + Llama3 (LLM local)

↓

MLflow (tracking & observabilité)

## 🛠️ Stack technique

- Python 3.x
- Ollama + Llama3
- yfinance
- MLflow
- requests

## 🚀 Lancement

### 1. Installer les dépendances
pip install -r requirements.txt

### 2. Lancer Ollama
ollama run llama3

### 3. Lancer le chatbot
python3 chatbot.py

### 4. Visualiser les runs MLflow
mlflow ui

## 💬 Exemples d'utilisation

Analyse AAPL
Compare TSLA et MSFT

## 👩‍💻 Auteure

Serine Nehal — Étudiante ingénieure ISEP (Génie Numérique)