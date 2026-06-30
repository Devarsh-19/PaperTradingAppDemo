import threading
import websocket
import json

def on_open(ws):
    print("Connection opened")

def on_message(ws, message):
    data = json.loads(message)
    print("Price:", data.get("p"))

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, code, msg):
    print("Connection closed")

url = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade"

client = websocket.WebSocketApp(
    url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

wst = threading.Thread(target=client.run_forever, daemon=True)
wst.start()

wst.join()
