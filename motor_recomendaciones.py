import os
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient
from textblob import TextBlob

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))


def analizar_sentimiento_noticias(nombre_empresa):
    """Busca noticias recientes y calcula el sentimiento promedio."""
    fecha_desde = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

    resultado = newsapi.get_everything(
        q=f'"{nombre_empresa}" AND (earnings OR stock OR shares OR revenue)',
        language="en",
        sort_by="publishedAt",
        from_param=fecha_desde,
        page_size=15
    )

    if resultado['totalResults'] == 0:
        return 0.0, 0  # sentimiento neutral si no hay noticias

    puntajes = []
    for noticia in resultado['articles']:
        analisis = TextBlob(noticia['title'])
        puntajes.append(analisis.sentiment.polarity)

    promedio = sum(puntajes) / len(puntajes)
    return promedio, len(puntajes)


def calcular_indicadores_tecnicos(simbolo):
    """Descarga precios y calcula RSI + medias móviles."""
    datos = yf.download(simbolo, period="3mo", interval="1d", progress=False)

    delta = datos['Close'].diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    media_ganancia = ganancia.rolling(window=14).mean()
    media_perdida = perdida.rolling(window=14).mean()
    rs = media_ganancia / media_perdida
    datos['RSI'] = 100 - (100 / (1 + rs))

    datos['MA_20'] = datos['Close'].rolling(window=20).mean()
    datos['MA_50'] = datos['Close'].rolling(window=50).mean()

    ultimo = datos.iloc[-1]

    def valor(x):
        return float(x.iloc[0]) if hasattr(x, 'iloc') else float(x)

    return {
        'precio': valor(ultimo['Close']),
        'rsi': valor(ultimo['RSI']),
        'ma20': valor(ultimo['MA_20']),
        'ma50': valor(ultimo['MA_50'])
    }


def generar_recomendacion(simbolo, nombre_empresa):
    """Combina noticias + indicadores técnicos en una recomendación final."""

    print(f"Analizando {nombre_empresa} ({simbolo})...\n")

    sentimiento, num_noticias = analizar_sentimiento_noticias(nombre_empresa)
    tecnico = calcular_indicadores_tecnicos(simbolo)

    precio = tecnico['precio']
    rsi = tecnico['rsi']
    ma20 = tecnico['ma20']
    ma50 = tecnico['ma50']

    # === Sistema de puntuación: cada señal aporta puntos ===
    puntos = 0
    razones = []

    # Señal de RSI
    if rsi < 30:
        puntos += 2
        razones.append(f"RSI en {rsi:.1f} indica sobreventa (señal de COMPRA)")
    elif rsi > 70:
        puntos -= 2
        razones.append(f"RSI en {rsi:.1f} indica sobrecompra (señal de VENTA)")
    else:
        razones.append(f"RSI en {rsi:.1f} es neutral")

    # Señal de tendencia (medias móviles)
    if ma20 > ma50:
        puntos += 1
        razones.append("Tendencia alcista (MA20 > MA50)")
    else:
        puntos -= 1
        razones.append("Tendencia bajista (MA20 < MA50)")

    # Señal de sentimiento de noticias
    if sentimiento > 0.1:
        puntos += 1
        razones.append(f"Sentimiento de noticias positivo ({sentimiento:.2f}, basado en {num_noticias} noticias)")
    elif sentimiento < -0.1:
        puntos -= 1
        razones.append(f"Sentimiento de noticias negativo ({sentimiento:.2f}, basado en {num_noticias} noticias)")
    else:
        razones.append(f"Sentimiento de noticias neutral ({sentimiento:.2f}, basado en {num_noticias} noticias)")

    # === Decisión final basada en el puntaje total ===
    if puntos >= 2:
        decision = "COMPRAR"
        confianza = min(50 + puntos * 10, 90)
        precio_entrada = precio
        precio_objetivo = precio * 1.05  # objetivo: +5%
    elif puntos <= -2:
        decision = "VENDER"
        confianza = min(50 + abs(puntos) * 10, 90)
        precio_entrada = precio
        precio_objetivo = precio * 0.95  # objetivo: -5%
    else:
        decision = "MANTENER / ESPERAR"
        confianza = 50
        precio_entrada = precio
        precio_objetivo = precio

    # === Resultado final ===
    print("=" * 60)
    print(f"RECOMENDACIÓN PARA {nombre_empresa} ({simbolo})")
    print("=" * 60)
    print(f"\nDecisión: {decision}")
    print(f"Precio actual: ${precio:.2f}")
    print(f"Precio de entrada sugerido: ${precio_entrada:.2f}")
    print(f"Precio objetivo de venta: ${precio_objetivo:.2f}")
    print(f"Nivel de confianza: {confianza}%")
    print(f"\nRazones del análisis:")
    for razon in razones:
        print(f"  • {razon}")
    print()


# === Ejecuta el análisis para Apple ===
generar_recomendacion("AAPL", "Apple")