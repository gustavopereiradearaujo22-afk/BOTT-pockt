# ===========================
#        app.py
# ===========================

from flask import Flask, jsonify, send_from_directory
from pocketoptionapi.stable_api import PocketOption
import time, threading, json

# ========= CONFIGURAÇÃO =========

# Cole aqui o seu SSID de sessão da Pocket Option
SSID = "SEU_SSID_AQUI"
# True para demo, False para real
DEMO = True

# Intervalo entre sinais (em segundos)
INTERVAL = 60

# =================================

# Conexão com a Pocket Option via API não oficial
api = PocketOption(SSID, DEMO)
connected = api.connect()

print("Conectado à Pocket Option:", connected)

# Inicia o app Flask
app = Flask(__name__, static_folder="../frontend")

# Função para buscar candles e gerar sinal
def fetch_candles(asset="BTCUSD", timeframe=60):
    try:
        candles = api.get_candles(asset, timeframe)
        return candles
    except Exception as e:
        print("Erro ao puxar candles:", e)
        return []

def analyze_signal(candles):
    if len(candles) < 2:
        return "SEM DADOS"
    # Compara fechamento atual vs anterior
    last_close = float(candles[-1]["close"])
    prev_close = float(candles[-2]["close"])
    return "CALL" if last_close > prev_close else "PUT"

def save_signal(signal):
    with open("data.json", "w") as f:
        json.dump({"signal": signal}, f)

# Loop do BOT (roda em thread separada)
def bot_loop():
    while True:
        candles = fetch_candles()
        signal = analyze_signal(candles)
        print("Sinal atual:", signal)
        save_signal(signal)
        time.sleep(INTERVAL)

# Inicia o thread do BOT
threading.Thread(target=bot_loop, daemon=True).start()

# API para o painel buscar o sinal
@app.route("/api/signal")
def api_signal():
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return jsonify({"signal": "ERRO"})

# Endpoint para servir a interface web
@app.route("/")
def panel():
    return send_from_directory("../frontend", "index.html")

if __name__ == "__main__":
    print("API Flask rodando...")
    app.run(debug=True, host="0.0.0.0")
