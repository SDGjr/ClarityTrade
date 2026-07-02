import yfinance as yf
import pandas as pd

# Descarga el historial de precios de Apple de los últimos 3 meses
simbolo = "AAPL"
datos = yf.download(simbolo, period="3mo", interval="1d")

# === Cálculo del RSI ===
def calcular_rsi(precios, periodo=14):
    delta = precios.diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)

    media_ganancia = ganancia.rolling(window=periodo).mean()
    media_perdida = perdida.rolling(window=periodo).mean()

    rs = media_ganancia / media_perdida
    rsi = 100 - (100 / (1 + rs))
    return rsi

datos['RSI'] = calcular_rsi(datos['Close'])

# === Cálculo de medias móviles ===
datos['MA_20'] = datos['Close'].rolling(window=20).mean()  # promedio de 20 días
datos['MA_50'] = datos['Close'].rolling(window=50).mean()  # promedio de 50 días

# Toma el dato más reciente
# Toma el dato más reciente y convierte a número simple
ultimo = datos.iloc[-1]
precio_actual = float(ultimo['Close'].iloc[0]) if hasattr(ultimo['Close'], 'iloc') else float(ultimo['Close'])
rsi_actual = float(ultimo['RSI'].iloc[0]) if hasattr(ultimo['RSI'], 'iloc') else float(ultimo['RSI'])
ma20 = float(ultimo['MA_20'].iloc[0]) if hasattr(ultimo['MA_20'], 'iloc') else float(ultimo['MA_20'])
ma50 = float(ultimo['MA_50'].iloc[0]) if hasattr(ultimo['MA_50'], 'iloc') else float(ultimo['MA_50'])

print(f"=== Análisis técnico de {simbolo} ===\n")
print(f"Precio actual: ${precio_actual:.2f}")
print(f"RSI actual: {rsi_actual:.2f}")
print(f"Media móvil 20 días: ${ma20:.2f}")
print(f"Media móvil 50 días: ${ma50:.2f}")
print()

if rsi_actual > 70:
    print("→ RSI indica: SOBRECOMPRADA (posible señal de venta, puede estar cara)")
elif rsi_actual < 30:
    print("→ RSI indica: SOBREVENDIDA (posible señal de compra, puede estar barata)")
else:
    print("→ RSI indica: NEUTRAL (sin señal clara)")

if ma20 > ma50:
    print("→ Tendencia: ALCISTA (la media corta está por encima de la larga)")
else:
    print("→ Tendencia: BAJISTA (la media corta está por debajo de la larga)")