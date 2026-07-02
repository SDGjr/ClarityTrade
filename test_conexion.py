import os
from dotenv import load_dotenv
import finnhub

# Carga las claves desde el archivo .env
load_dotenv()

# Conecta con Finnhub usando tu clave
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

# Pide el precio actual de Apple (símbolo: AAPL)
cotizacion = finnhub_client.quote("AAPL")

print("Conexión exitosa con Finnhub")
print(f"Precio actual de Apple (AAPL): ${cotizacion['c']}")
print(f"Cambio en el día: {cotizacion['dp']}%")