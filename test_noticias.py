import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from newsapi import NewsApiClient
from textblob import TextBlob

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

fecha_desde = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

# Búsqueda más específica, pero sin restringir dominios
resultado = newsapi.get_everything(
    q='"Apple" AND (earnings OR stock OR shares OR revenue OR iPhone)',
    language="en",
    sort_by="publishedAt",
    from_param=fecha_desde,
    page_size=10
)

print(f"Se encontraron {resultado['totalResults']} noticias relevantes. Mostrando hasta 10:\n")

if resultado['totalResults'] == 0:
    print("No se encontraron noticias con estos filtros. Intenta ampliar las fuentes o el rango de fechas.")
else:
    puntajes = []
    for noticia in resultado['articles']:
        titulo = noticia['title']
        analisis = TextBlob(titulo)
        polaridad = analisis.sentiment.polarity
        puntajes.append(polaridad)

        if polaridad > 0.1:
            sentimiento = "POSITIVO"
        elif polaridad < -0.1:
            sentimiento = "NEGATIVO"
        else:
            sentimiento = "NEUTRAL"

        print(f"Título: {titulo}")
        print(f"Sentimiento: {sentimiento} (puntaje: {polaridad:.2f})")
        print(f"Fuente: {noticia['source']['name']}")
        print("-" * 60)

    if puntajes:
        promedio = sum(puntajes) / len(puntajes)
        print(f"\nSENTIMIENTO GENERAL DEL MERCADO SOBRE APPLE: {promedio:.2f}")
        if promedio > 0.1:
            print("→ Tendencia: POSITIVA")
        elif promedio < -0.1:
            print("→ Tendencia: NEGATIVA")
        else:
            print("→ Tendencia: NEUTRAL")
            