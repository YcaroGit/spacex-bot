import yfinance as yf
import requests
import json
import os
from datetime import datetime

# ======================
# CONFIG
# ======================
TOKEN = "8441294799:AAFuMBzxuF4FOrIFmcM9Ml_3xWZnr76k63U"
CHAT_ID = "6374435559"
TICKER = "SPCX"
ARCHIVO = "datos.json"

# ======================
# TELEGRAM
# ======================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# ======================
# PRECIO
# ======================
data = yf.Ticker(TICKER).history(period="1d")

if data.empty:
    print("Sin datos")
    exit()

precio = float(data["Close"].iloc[-1])

# ======================
# ESTADO SEGURO
# ======================
estado_default = {
    "maximo": precio,
    "a5": False,
    "a10": False,
    "a15": False
}

if os.path.exists(ARCHIVO):
    try:
        estado = json.load(open(ARCHIVO, "r"))

        for k in estado_default:
            if k not in estado:
                estado[k] = estado_default[k]

    except:
        estado = estado_default
else:
    estado = estado_default

# ======================
# MÁXIMO
# ======================
maximo = estado["maximo"]

if precio > maximo:
    estado["maximo"] = precio
    estado["a5"] = False
    estado["a10"] = False
    estado["a15"] = False
    maximo = precio

caida = ((maximo - precio) / maximo) * 100

# ======================
# ALERTAS
# ======================
alerta = None

if caida >= 15 and not estado["a15"]:
    alerta = "🚨 ALERTA 15%"
    estado["a15"] = True

elif caida >= 10 and not estado["a10"]:
    alerta = "🚨 ALERTA 10%"
    estado["a10"] = True

elif caida >= 5 and not estado["a5"]:
    alerta = "🚨 ALERTA 5%"
    estado["a5"] = True

# ======================
# GUARDAR
# ======================
json.dump(estado, open(ARCHIVO, "w"))

# ======================
# MENSAJE
# ======================
hora = datetime.now().strftime("%H:%M")

mensaje = f"""
📊 {TICKER}

💰 Precio: {precio:.2f}
📉 Caída: {caida:.2f}%
📈 Máximo: {maximo:.2f}
🕒 {hora}
"""

# ======================
# ENVÍO
# ======================
if alerta:
    enviar(f"{alerta}\n{mensaje}")

# SIEMPRE ENVÍA AL EJECUTAR
enviar("📲 Bot ejecutado\n" + mensaje)

print("OK")