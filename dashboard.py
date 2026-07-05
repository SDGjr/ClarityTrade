import os  # ClarityTrade v4
import anthropic
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from newsapi import NewsApiClient
from textblob import TextBlob

load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except:
        return os.getenv(key)

newsapi = NewsApiClient(api_key=get_secret("NEWS_API_KEY"))

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(page_title="ClarityTrade", page_icon=None, layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1A1A2E; border-right: 1px solid #2D2D4A; }
[data-testid="stSidebarNav"] { display: none; }
.metric-card { background: #1A1A2E; border: 1px solid #2D2D4A; border-radius: 10px; padding: 14px 18px; }
.rec-card { background: #1A1A2E; border: 1px solid #2D1B69; border-radius: 10px; padding: 18px 22px; margin: 16px 0; }
.news-card { background: #1A1A2E; border: 1px solid #2D2D4A; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }
.badge-buy { background: #0D2B1A; color: #4ADE80; padding: 3px 10px; border-radius: 5px; font-size: 11px; }
.badge-sell { background: #2B0D0D; color: #F87171; padding: 3px 10px; border-radius: 5px; font-size: 11px; }
.badge-hold { background: #1A1A0D; color: #FACC15; padding: 3px 10px; border-radius: 5px; font-size: 11px; }
.section-label { color: #8B8BAA; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; }
.live-badge { display: inline-flex; align-items: center; gap: 6px; background: #0D2B1A; color: #4ADE80; font-size: 11px; padding: 4px 10px; border-radius: 20px; border: 1px solid #4ADE80; }
.dot-bg { background-image: radial-gradient(circle, #2D2D4A 1px, transparent 1px); background-size: 24px 24px; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATOS: ACTIVOS
# ============================================================
ACCIONES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon",
    "TSLA": "Tesla", "NVDA": "NVIDIA", "META": "Meta", "NFLX": "Netflix",
    "JPM": "JPMorgan", "V": "Visa", "JNJ": "Johnson & Johnson", "WMT": "Walmart",
    "MA": "Mastercard", "PG": "Procter & Gamble", "UNH": "UnitedHealth",
    "HD": "Home Depot", "BAC": "Bank of America", "XOM": "ExxonMobil",
    "CVX": "Chevron", "LLY": "Eli Lilly", "AVGO": "Broadcom", "COST": "Costco",
    "MRK": "Merck", "PEP": "PepsiCo", "KO": "Coca-Cola", "ABBV": "AbbVie",
    "ORCL": "Oracle", "CRM": "Salesforce", "AMD": "AMD", "INTC": "Intel"
}

DIVISAS = {
    "EURUSD=X": "EUR/USD", "GBPUSD=X": "GBP/USD", "USDJPY=X": "USD/JPY",
    "USDCHF=X": "USD/CHF", "AUDUSD=X": "AUD/USD", "USDCAD=X": "USD/CAD",
    "NZDUSD=X": "NZD/USD", "USDCOP=X": "USD/COP", "USDMXN=X": "USD/MXN",
    "USDBRL=X": "USD/BRL", "USDCLP=X": "USD/CLP", "USDARS=X": "USD/ARS",
    "USDCNY=X": "USD/CNY", "USDINR=X": "USD/INR", "USDRUB=X": "USD/RUB",
    "USDTRY=X": "USD/TRY", "USDZAR=X": "USD/ZAR", "USDSGD=X": "USD/SGD",
    "USDHKD=X": "USD/HKD", "USDKRW=X": "USD/KRW", "EURGBP=X": "EUR/GBP",
    "EURJPY=X": "EUR/JPY", "GBPJPY=X": "GBP/JPY", "EURCHF=X": "EUR/CHF"
}

MATERIAS_PRIMAS = {
    "GC=F": "Oro", "SI=F": "Plata", "CL=F": "Petróleo WTI", "BZ=F": "Petróleo Brent",
    "NG=F": "Gas Natural", "HG=F": "Cobre", "PL=F": "Platino", "PA=F": "Paladio",
    "ZW=F": "Trigo", "ZC=F": "Maíz", "ZS=F": "Soja", "KC=F": "Café",
    "CT=F": "Algodón", "SB=F": "Azúcar", "CC=F": "Cacao", "OJ=F": "Jugo de Naranja",
    "LBS=F": "Madera", "LE=F": "Ganado vacuno", "HE=F": "Cerdo",
    "RB=F": "Gasolina", "HO=F": "Aceite calefacción", "ALI=F": "Aluminio",
    "ZR=F": "Arroz", "ZO=F": "Avena", "GF=F": "Ganado de engorde",
    "LH=F": "Panza de cerdo", "ZL=F": "Aceite de soja", "ZM=F": "Harina de soja",
    "UX=F": "Uranio", "MHO=F": "Acero"
}

CRIPTOS_BINANCE = {
    "BTCUSDT": "Bitcoin", "ETHUSDT": "Ethereum", "BNBUSDT": "BNB",
    "SOLUSDT": "Solana", "XRPUSDT": "XRP", "ADAUSDT": "Cardano",
    "DOGEUSDT": "Dogecoin", "AVAXUSDT": "Avalanche", "MATICUSDT": "Polygon",
    "DOTUSDT": "Polkadot", "SHIBUSDT": "Shiba Inu", "LTCUSDT": "Litecoin",
    "LINKUSDT": "Chainlink", "UNIUSDT": "Uniswap", "ATOMUSDT": "Cosmos",
    "XLMUSDT": "Stellar", "ETCUSDT": "Ethereum Classic", "ALGOUSDT": "Algorand",
    "VETUSDT": "VeChain", "FILUSDT": "Filecoin", "TRXUSDT": "TRON",
    "NEARUSDT": "NEAR Protocol", "AAVEUSDT": "Aave", "MKRUSDT": "Maker"
}

# ============================================================
# FUNCIONES DE DATOS
# ============================================================
@st.cache_data(ttl=60)
def get_precio_finnhub(simbolo):
    try:
        key = get_secret("FINNHUB_API_KEY")
        r = requests.get(f"https://finnhub.io/api/v1/quote?symbol={simbolo}&token={key}", timeout=5)
        d = r.json()
        return {"precio": d.get("c", 0), "cambio_pct": d.get("dp", 0), "open": d.get("o", 0)}
    except:
        return None

@st.cache_data(ttl=60)
def get_precio_yahoo(simbolo):
    try:
        ticker = yf.Ticker(simbolo)
        hist = ticker.history(period="2d")
        if len(hist) >= 2:
            precio_actual = float(hist['Close'].iloc[-1])
            precio_anterior = float(hist['Close'].iloc[-2])
            cambio_pct = ((precio_actual - precio_anterior) / precio_anterior) * 100
            return {"precio": precio_actual, "cambio_pct": cambio_pct}
        return None
    except:
        return None

@st.cache_data(ttl=60)
def get_precio_binance(simbolo):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={simbolo}", timeout=5)
        d = r.json()
        return {
            "precio": float(d.get("lastPrice", 0)),
            "cambio_pct": float(d.get("priceChangePercent", 0))
        }
    except:
        return None

@st.cache_data(ttl=60)
def get_tasa_conversion(de, a):
    try:
        simbolo = f"{de}{a}=X"
        ticker = yf.Ticker(simbolo)
        hist = ticker.history(period="1d")
        if len(hist) > 0:
            return float(hist['Close'].iloc[-1])
        return None
    except:
        return None

def render_tarjeta_activo(simbolo, nombre, precio_data, categoria):
    if not precio_data or precio_data.get("precio", 0) == 0:
        return
    precio = precio_data["precio"]
    cambio = precio_data.get("cambio_pct", 0)
    color = "#4ADE80" if cambio >= 0 else "#F87171"
    signo = "+" if cambio >= 0 else ""
    if precio > 1000:
        precio_str = f"${precio:,.2f}"
    elif precio > 1:
        precio_str = f"${precio:.4f}" if precio < 10 else f"${precio:.2f}"
    else:
        precio_str = f"${precio:.6f}"

    st.markdown(f"""
    <div class="metric-card" style="margin-bottom:8px; cursor:pointer;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
            <div>
                <div style="color:#F0EEFF; font-size:13px; font-weight:600;">{simbolo.replace('=X','').replace('USDT','')}</div>
                <div style="color:#8B8BAA; font-size:11px;">{nombre}</div>
            </div>
            <div style="color:{color}; font-size:12px; font-weight:500;">{signo}{cambio:.2f}%</div>
        </div>
        <div style="color:#F0EEFF; font-size:18px; font-weight:600;">{precio_str}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 16px 0 24px; display:flex; align-items:center; gap:10px;">
        <div style="width:32px; height:32px; background:#7C3AED; border-radius:8px; display:flex; align-items:center; justify-content:center;">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M2 14L7 8L10 11L13 6L16 8" stroke="#F0EEFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="16" cy="8" r="2" fill="#A78BFA"/>
            </svg>
        </div>
        <span style="color:#F0EEFF; font-size:18px; font-weight:600;">ClarityTrade</span>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "",
        ["Inicio", "Mercado Live", "Análisis", "Noticias", "Calculadora", "Acerca de"],
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="position:absolute; bottom:20px; left:0; right:0; padding:0 16px;">
        <div style="background:#1A1A2E; border:1px solid #2D2D4A; border-radius:8px; padding:10px 12px; text-align:center;">
            <div style="color:#8B8BAA; font-size:10px; margin-bottom:4px;">Puedes ocultar este menú</div>
            <div style="color:#A78BFA; font-size:11px;">← Desliza para ocultar</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PÁGINA: INICIO
# ============================================================
if pagina == "Inicio":
    st.markdown("""
    <div class="dot-bg" style="padding: 60px 20px 40px; text-align:center; border-radius:16px; margin-bottom:24px;">
        <div style="display:inline-block; background:#2D1B69; color:#A78BFA; font-size:12px; padding:5px 16px; border-radius:20px; border:1px solid #7C3AED; margin-bottom:20px;">
            Inteligencia financiera en tiempo real
        </div>
        <h1 style="color:#F0EEFF; font-size:36px; font-weight:600; margin-bottom:14px; line-height:1.3;">
            Toma decisiones de inversión<br>con datos, no con intuición
        </h1>
        <p style="color:#8B8BAA; font-size:15px; max-width:560px; margin:0 auto; line-height:1.8;">
            ClarityTrade analiza precios en tiempo real, indicadores técnicos y noticias 
            del mercado global para darte recomendaciones claras sobre cuándo comprar, esperar o vender.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:24px 16px;">
            <div style="font-size:28px; margin-bottom:12px;">📈</div>
            <div style="color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:8px;">Mercado Live</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.6;">Precios en tiempo real de acciones, divisas, materias primas y criptomonedas.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver mercado", key="btn_mercado", use_container_width=True):
            st.session_state.pagina = "Mercado Live"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:24px 16px;">
            <div style="font-size:28px; margin-bottom:12px;">🔍</div>
            <div style="color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:8px;">Análisis profundo</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.6;">RSI, MACD, Bollinger, sentimiento de noticias y análisis generado por IA.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Analizar activo", key="btn_analisis", use_container_width=True):
            st.session_state.pagina = "Análisis"
            st.rerun()

    with c3:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:24px 16px;">
            <div style="font-size:28px; margin-bottom:12px;">💱</div>
            <div style="color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:8px;">Calculadora</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.6;">Convierte entre divisas, criptomonedas y materias primas con tasas en tiempo real.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir calculadora", key="btn_calc", use_container_width=True):
            st.session_state.pagina = "Calculadora"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_n, col_a = st.columns(2)
    with col_n:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:20px 16px;">
            <div style="font-size:24px; margin-bottom:10px;">📰</div>
            <div style="color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:6px;">Noticias globales</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.6;">BBC, Reuters, CNN, CNBC, The Guardian y más.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver noticias", key="btn_noticias", use_container_width=True):
            st.session_state.pagina = "Noticias"
            st.rerun()

    with col_a:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:20px 16px;">
            <div style="font-size:24px; margin-bottom:10px;">ℹ️</div>
            <div style="color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:6px;">Acerca de ClarityTrade</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.6;">Tecnología, fuentes de datos y nota legal.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Más información", key="btn_acerca", use_container_width=True):
            st.session_state.pagina = "Acerca de"
            st.rerun()

# ============================================================
# PÁGINA: MERCADO LIVE
# ============================================================
elif pagina == "Mercado Live":
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;">
        <h2 style="color:#F0EEFF; font-size:22px; font-weight:600; margin:0;">Mercado live</h2>
        <span class="live-badge">● En vivo · actualiza cada 60s</span>
    </div>
    """, unsafe_allow_html=True)

    tab = st.selectbox("Categoría", ["Acciones", "Divisas", "Materias primas", "Criptomonedas"])

    if tab == "Acciones":
        st.markdown("<div class='section-label'>Acciones globales</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (simbolo, nombre) in enumerate(ACCIONES.items()):
            with cols[i % 4]:
                data = get_precio_finnhub(simbolo)
                if data:
                    render_tarjeta_activo(simbolo, nombre, data, "accion")
                    if st.button(f"Analizar", key=f"act_{simbolo}"):
                        st.session_state.analizar_simbolo = simbolo
                        st.session_state.analizar_nombre = nombre
                        st.session_state.pagina = "Análisis"
                        st.rerun()

    elif tab == "Divisas":
        st.markdown("<div class='section-label'>Pares de divisas</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (simbolo, nombre) in enumerate(DIVISAS.items()):
            with cols[i % 4]:
                data = get_precio_yahoo(simbolo)
                if data:
                    render_tarjeta_activo(simbolo, nombre, data, "divisa")
                    if st.button(f"Analizar", key=f"div_{simbolo}"):
                        st.session_state.analizar_simbolo = simbolo
                        st.session_state.analizar_nombre = nombre
                        st.session_state.pagina = "Análisis"
                        st.rerun()

    elif tab == "Materias primas":
        st.markdown("<div class='section-label'>Materias primas</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (simbolo, nombre) in enumerate(MATERIAS_PRIMAS.items()):
            with cols[i % 4]:
                data = get_precio_yahoo(simbolo)
                if data:
                    render_tarjeta_activo(simbolo, nombre, data, "materia")
                    if st.button(f"Analizar", key=f"mat_{simbolo}"):
                        st.session_state.analizar_simbolo = simbolo
                        st.session_state.analizar_nombre = nombre
                        st.session_state.pagina = "Análisis"
                        st.rerun()

    elif tab == "Criptomonedas":
        st.markdown("<div class='section-label'>Criptomonedas — datos: Binance</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (simbolo, nombre) in enumerate(CRIPTOS_BINANCE.items()):
            with cols[i % 4]:
                data = get_precio_binance(simbolo)
                if data:
                    render_tarjeta_activo(simbolo, nombre, data, "cripto")
                    if st.button(f"Analizar", key=f"cri_{simbolo}"):
                        cripto_yf = simbolo.replace("USDT", "-USD")
                        st.session_state.analizar_simbolo = cripto_yf
                        st.session_state.analizar_nombre = nombre
                        st.session_state.pagina = "Análisis"
                        st.rerun()

    if st.button("Actualizar precios"):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# PÁGINA: ANÁLISIS
# ============================================================
elif pagina == "Análisis":
    st.markdown("<h2 style='color:#F0EEFF; font-size:22px; font-weight:600; margin-bottom:20px;'>Análisis de mercado</h2>", unsafe_allow_html=True)

    simbolo_default = st.session_state.get("analizar_simbolo", "")
    nombre_default = st.session_state.get("analizar_nombre", "")

    if not simbolo_default:
        st.markdown("""
        <div style="text-align:center; padding:40px 20px; background:#1A1A2E; border-radius:12px; border:1px solid #2D2D4A; margin-bottom:24px;">
            <div style="font-size:40px; margin-bottom:16px;">🔍</div>
            <div style="color:#F0EEFF; font-size:18px; font-weight:600; margin-bottom:8px;">Analiza cualquier activo</div>
            <div style="color:#8B8BAA; font-size:13px; line-height:1.7; max-width:400px; margin:0 auto;">
                Ingresa el símbolo de una acción, divisa o materia prima para obtener 
                un análisis completo con indicadores técnicos, noticias y recomendación de IA.
            </div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        simbolo = st.text_input("Símbolo del activo", value=simbolo_default,
                                 placeholder="AAPL, TSLA, EURUSD=X, GC=F, BTC-USD...")
    with col2:
        nombre_empresa = st.text_input("Nombre del activo", value=nombre_default,
                                        placeholder="Apple, Tesla, Euro/Dólar...")

    st.markdown("""
    <div style="background:#1A1A2E; border:1px solid #2D2D4A; border-radius:8px; padding:10px 14px; margin-bottom:16px;">
        <span style="color:#8B8BAA; font-size:12px;">
            Los indicadores técnicos (RSI, MACD, Bandas de Bollinger) se calculan con datos históricos 
            de los últimos 3 meses de cierre diario. El precio actual es en tiempo real.
        </span>
    </div>
    """, unsafe_allow_html=True)

    analizar = st.button("Analizar", type="primary")

    if analizar and simbolo:
        if "analizar_simbolo" in st.session_state:
            del st.session_state["analizar_simbolo"]
            del st.session_state["analizar_nombre"]

        with st.spinner(f"Analizando {simbolo}..."):
            datos = yf.download(simbolo, period="3mo", interval="1d", progress=False)

            if datos.empty:
                st.error("No se encontraron datos para ese símbolo. Verifica que sea correcto.")
                st.stop()

            close = datos['Close'].squeeze()
            delta = close.diff()
            ganancia = delta.where(delta > 0, 0)
            perdida = -delta.where(delta < 0, 0)
            rs = ganancia.rolling(14).mean() / perdida.rolling(14).mean()
            datos['RSI'] = 100 - (100 / (1 + rs))
            datos['MA_20'] = close.rolling(20).mean()
            datos['MA_50'] = close.rolling(50).mean()
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            datos['MACD'] = ema12 - ema26
            datos['MACD_signal'] = datos['MACD'].ewm(span=9, adjust=False).mean()
            datos['MACD_hist'] = datos['MACD'] - datos['MACD_signal']
            datos['BB_media'] = close.rolling(20).mean()
            datos['BB_superior'] = datos['BB_media'] + 2 * close.rolling(20).std()
            datos['BB_inferior'] = datos['BB_media'] - 2 * close.rolling(20).std()

            ultimo = datos.iloc[-1]
            def v(x):
                return float(x.iloc[0]) if hasattr(x, 'iloc') else float(x)

            precio = v(ultimo['Close'])
            rsi = v(ultimo['RSI'])
            ma20 = v(ultimo['MA_20'])
            ma50 = v(ultimo['MA_50'])
            macd = v(ultimo['MACD'])
            macd_sig = v(ultimo['MACD_signal'])
            bb_sup = v(ultimo['BB_superior'])
            bb_inf = v(ultimo['BB_inferior'])

            fecha_desde = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            resultado = newsapi.get_everything(
                q=f'"{nombre_empresa}" AND (earnings OR stock OR shares OR revenue OR market)',
                language="en",
                sort_by="publishedAt",
                from_param=fecha_desde,
                page_size=10,
                sources="bbc-news,reuters,cnn,cnbc,the-guardian-uk,associated-press,the-wall-street-journal,bloomberg,financial-times,marketwatch"
            )
            noticias = resultado.get('articles', [])
            if not noticias:
                resultado2 = newsapi.get_everything(
                    q=f'"{nombre_empresa}" AND (stock OR market OR price)',
                    language="en",
                    sort_by="publishedAt",
                    from_param=fecha_desde,
                    page_size=10
                )
                noticias = resultado2.get('articles', [])

            puntajes = [TextBlob(n['title']).sentiment.polarity for n in noticias]
            sentimiento = sum(puntajes) / len(puntajes) if puntajes else 0.0

            puntos = 0
            razones = []

            if rsi < 30:
                puntos += 2
                razones.append(f"Índice de Fuerza Relativa (RSI) en {rsi:.1f} — zona de sobreventa")
            elif rsi > 70:
                puntos -= 2
                razones.append(f"Índice de Fuerza Relativa (RSI) en {rsi:.1f} — zona de sobrecompra")
            else:
                razones.append(f"Índice de Fuerza Relativa (RSI) neutral en {rsi:.1f}")

            if ma20 > ma50:
                puntos += 1
                razones.append("Tendencia alcista — media móvil de 20 días por encima de la de 50 días")
            else:
                puntos -= 1
                razones.append("Tendencia bajista — media móvil de 20 días por debajo de la de 50 días")

            if macd > macd_sig:
                puntos += 1
                razones.append(f"MACD positivo — momentum alcista ({macd:.2f} sobre señal {macd_sig:.2f})")
            else:
                puntos -= 1
                razones.append(f"MACD negativo — momentum bajista ({macd:.2f} bajo señal {macd_sig:.2f})")

            if precio < bb_inf:
                puntos += 2
                razones.append("Precio bajo la Banda de Bollinger inferior — posible rebote al alza")
            elif precio > bb_sup:
                puntos -= 2
                razones.append("Precio sobre la Banda de Bollinger superior — posible corrección")
            else:
                razones.append(f"Precio dentro de las Bandas de Bollinger (${bb_inf:.2f} — ${bb_sup:.2f})")

            if sentimiento > 0.1:
                puntos += 1
                razones.append(f"Noticias con sentimiento positivo ({sentimiento:.2f})")
            elif sentimiento < -0.1:
                puntos -= 1
                razones.append(f"Noticias con sentimiento negativo ({sentimiento:.2f})")
            else:
                razones.append(f"Noticias con sentimiento neutral ({sentimiento:.2f})")

            if puntos >= 2:
                decision, color_dec = "COMPRAR", "#4ADE80"
                confianza = min(50 + puntos * 10, 90)
                precio_objetivo = precio * 1.05
            elif puntos <= -2:
                decision, color_dec = "VENDER", "#F87171"
                confianza = min(50 + abs(puntos) * 10, 90)
                precio_objetivo = precio * 0.95
            else:
                decision, color_dec = "MANTENER / ESPERAR", "#FACC15"
                confianza = 50
                precio_objetivo = precio

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Precio actual", f"${precio:,.4f}" if precio < 10 else f"${precio:,.2f}")
        m2.metric("RSI (14 períodos)", f"{rsi:.1f}")
        m3.metric("MACD", f"{macd:.4f}" if abs(macd) < 1 else f"{macd:.2f}")
        m4.metric("Bandas Bollinger", f"${bb_inf:.2f} — ${bb_sup:.2f}")

        st.markdown(f"""
        <div class="rec-card">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                <div>
                    <div style="color:#8B8BAA; font-size:11px; margin-bottom:4px;">Recomendación</div>
                    <div style="color:{color_dec}; font-size:24px; font-weight:600;">{decision}</div>
                </div>
                <div>
                    <div style="color:#8B8BAA; font-size:11px; margin-bottom:4px;">Precio de entrada</div>
                    <div style="color:#F0EEFF; font-size:20px; font-weight:600;">${precio:,.2f}</div>
                </div>
                <div>
                    <div style="color:#8B8BAA; font-size:11px; margin-bottom:4px;">Precio objetivo</div>
                    <div style="color:#F0EEFF; font-size:20px; font-weight:600;">${precio_objetivo:,.2f}</div>
                </div>
                <div>
                    <div style="color:#8B8BAA; font-size:11px; margin-bottom:4px;">Confianza</div>
                    <div style="color:#F0EEFF; font-size:20px; font-weight:600;">{confianza}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-label'>Razones del análisis</div>", unsafe_allow_html=True)
        for r in razones:
            st.markdown(f"— {r}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Análisis de ClarityTrade</div>", unsafe_allow_html=True)
        with st.spinner("Generando análisis con IA..."):
            cliente_ai = anthropic.Anthropic(api_key=get_secret("ANTHROPIC_API_KEY"))
            prompt = f"""Eres un analista financiero experto. Analiza {nombre_empresa} ({simbolo}) y genera exactamente un párrafo de máximo 4 oraciones en español. Sin markdown, sin asteriscos, sin símbolos especiales. Solo texto plano profesional que explique la situación actual y qué debería considerar un inversor.

Datos: Precio ${precio:.4f}, RSI {rsi:.1f}, Tendencia {'alcista' if ma20 > ma50 else 'bajista'}, MACD {'positivo' if macd > macd_sig else 'negativo'}, Bollinger {'bajo banda inferior' if precio < bb_inf else 'sobre banda superior' if precio > bb_sup else 'dentro de bandas'}, Sentimiento noticias {'positivo' if sentimiento > 0.1 else 'negativo' if sentimiento < -0.1 else 'neutral'}, Recomendación: {decision} con {confianza}% confianza."""

            msg = cliente_ai.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(msg.content[0].text)

        st.divider()
        st.markdown("<div class='section-label'>Gráfico de precios — últimos 3 meses</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=datos.index,
            open=datos['Open'].squeeze(),
            high=datos['High'].squeeze(),
            low=datos['Low'].squeeze(),
            close=close, name="Precio",
            increasing_line_color="#4ADE80",
            decreasing_line_color="#F87171"
        ))
        fig.add_trace(go.Scatter(x=datos.index, y=datos['MA_20'], name="MA 20 días", line=dict(color="#A78BFA", width=1.5)))
        fig.add_trace(go.Scatter(x=datos.index, y=datos['MA_50'], name="MA 50 días", line=dict(color="#7C3AED", width=1.5)))
        fig.update_layout(
            xaxis_rangeslider_visible=False, height=480,
            template="plotly_dark", paper_bgcolor="#1A1A2E",
            plot_bgcolor="#1A1A2E", margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        col_rsi, col_macd = st.columns(2)
        with col_rsi:
            st.markdown("<div class='section-label'>Índice de Fuerza Relativa (RSI)</div>", unsafe_allow_html=True)
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=datos.index, y=datos['RSI'], name="RSI", line=dict(color="#A78BFA", width=2), fill='tozeroy', fillcolor='rgba(124,58,237,0.08)'))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#F87171", annotation_text="Sobrecompra (70)")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#4ADE80", annotation_text="Sobreventa (30)")
            fig_rsi.update_layout(height=280, template="plotly_dark", paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E", yaxis=dict(range=[0, 100]), margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_rsi, use_container_width=True)

        with col_macd:
            st.markdown("<div class='section-label'>Conv./Div. de Medias Móviles (MACD)</div>", unsafe_allow_html=True)
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=datos.index, y=datos['MACD'], name="MACD", line=dict(color="#A78BFA", width=2)))
            fig_macd.add_trace(go.Scatter(x=datos.index, y=datos['MACD_signal'], name="Señal", line=dict(color="#F0EEFF", width=1.5)))
            fig_macd.add_trace(go.Bar(x=datos.index, y=datos['MACD_hist'], name="Histograma", marker_color=['#4ADE80' if val > 0 else '#F87171' for val in datos['MACD_hist']]))
            fig_macd.update_layout(height=280, template="plotly_dark", paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_macd, use_container_width=True)

        st.markdown("<div class='section-label'>Bandas de Bollinger (BB)</div>", unsafe_allow_html=True)
        fig_bb = go.Figure()
        fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_superior'], name="Banda superior", line=dict(color="#F87171", width=1, dash="dash")))
        fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_media'], name="Media", line=dict(color="#A78BFA", width=1)))
        fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_inferior'], name="Banda inferior", line=dict(color="#4ADE80", width=1, dash="dash"), fill='tonexty', fillcolor='rgba(74,222,128,0.05)'))
        fig_bb.add_trace(go.Scatter(x=datos.index, y=close, name="Precio", line=dict(color="#F0EEFF", width=2)))
        fig_bb.update_layout(height=340, template="plotly_dark", paper_bgcolor="#1A1A2E", plot_bgcolor="#1A1A2E", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_bb, use_container_width=True)

        st.divider()
        st.markdown("<div class='section-label'>Noticias relacionadas</div>", unsafe_allow_html=True)
        if noticias:
            for noticia in noticias[:6]:
                s = TextBlob(noticia['title']).sentiment.polarity
                badge = "badge-buy" if s > 0.1 else ("badge-sell" if s < -0.1 else "badge-hold")
                badge_text = "Positivo" if s > 0.1 else ("Negativo" if s < -0.1 else "Neutral")
                imagen_url = noticia.get('urlToImage') or ''
                url_noticia = noticia.get('url', '#')
                titulo = noticia['title']
                descripcion = noticia.get('description') or ''
                fuente = noticia['source']['name']
                with st.container():
                    ci, ct = st.columns([1, 4])
                    with ci:
                        if imagen_url and imagen_url.startswith('http'):
                            try:
                                st.image(imagen_url, width=120)
                            except:
                                st.markdown("""<div style="width:120px;height:80px;background:#2D2D4A;border-radius:8px;display:flex;align-items:center;justify-content:center;"><span style="color:#8B8BAA;font-size:20px;">📰</span></div>""", unsafe_allow_html=True)
                        else:
                            st.markdown("""<div style="width:120px;height:80px;background:#2D2D4A;border-radius:8px;display:flex;align-items:center;justify-content:center;"><span style="color:#8B8BAA;font-size:20px;">📰</span></div>""", unsafe_allow_html=True)
                    with ct:
                        st.markdown(f"**{titulo}**")
                        if descripcion:
                            st.markdown(f"<span style='color:#8B8BAA; font-size:13px;'>{descripcion[:160]}...</span>", unsafe_allow_html=True)
                        st.markdown(f"<span class='{badge}'>{badge_text}</span> <span style='color:#8B8BAA; font-size:12px;'>— {fuente}</span>", unsafe_allow_html=True)
                        st.markdown(f"[Leer artículo completo]({url_noticia})")
                    st.divider()
        else:
            st.info("No se encontraron noticias recientes para este activo.")

# ============================================================
# PÁGINA: NOTICIAS
# ============================================================
elif pagina == "Noticias":
    st.markdown("<h2 style='color:#F0EEFF; font-size:22px; font-weight:600; margin-bottom:20px;'>Noticias financieras globales</h2>", unsafe_allow_html=True)

    categoria = st.selectbox("Categoría", ["Todas", "Acciones y mercados", "Divisas", "Materias primas", "Criptomonedas", "Economía global"])

    queries = {
        "Todas": "stock market OR finance OR investing OR economy OR crypto",
        "Acciones y mercados": "stock market earnings shares equity Wall Street",
        "Divisas": "forex currency exchange rate dollar euro pound",
        "Materias primas": "commodities oil gold silver wheat copper",
        "Criptomonedas": "bitcoin ethereum cryptocurrency crypto blockchain",
        "Economía global": "economy GDP inflation interest rates Federal Reserve"
    }

    FUENTES = "bbc-news,reuters,cnn,cnbc,the-guardian-uk,associated-press,the-wall-street-journal,marketwatch,financial-times,bloomberg"

    with st.spinner("Cargando noticias..."):
        fecha_desde = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        try:
            resultado = newsapi.get_everything(
                q=queries[categoria],
                language="en",
                sort_by="publishedAt",
                from_param=fecha_desde,
                page_size=20,
                sources=FUENTES
            )
            noticias_globales = resultado.get('articles', [])
        except:
            resultado = newsapi.get_everything(
                q=queries[categoria],
                language="en",
                sort_by="publishedAt",
                from_param=fecha_desde,
                page_size=20
            )
            noticias_globales = resultado.get('articles', [])

    st.markdown(f"<div class='section-label'>{len(noticias_globales)} noticias encontradas</div>", unsafe_allow_html=True)

    if noticias_globales:
        for noticia in noticias_globales:
            s = TextBlob(noticia['title']).sentiment.polarity
            badge = "badge-buy" if s > 0.1 else ("badge-sell" if s < -0.1 else "badge-hold")
            badge_text = "Positivo" if s > 0.1 else ("Negativo" if s < -0.1 else "Neutral")
            imagen_url = noticia.get('urlToImage') or ''
            url_noticia = noticia.get('url', '#')
            titulo = noticia['title']
            descripcion = noticia.get('description') or ''
            fuente = noticia['source']['name']
            fecha = noticia.get('publishedAt', '')[:10]
            with st.container():
                ci, ct = st.columns([1, 4])
                with ci:
                    if imagen_url and imagen_url.startswith('http'):
                        try:
                            st.image(imagen_url, width=120)
                        except:
                            st.markdown("""<div style="width:120px;height:80px;background:#2D2D4A;border-radius:8px;display:flex;align-items:center;justify-content:center;"><span style="color:#8B8BAA;font-size:20px;">📰</span></div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("""<div style="width:120px;height:80px;background:#2D2D4A;border-radius:8px;display:flex;align-items:center;justify-content:center;"><span style="color:#8B8BAA;font-size:20px;">📰</span></div>""", unsafe_allow_html=True)
                with ct:
                    st.markdown(f"**{titulo}**")
                    if descripcion:
                        st.markdown(f"<span style='color:#8B8BAA; font-size:13px;'>{descripcion[:180]}...</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='{badge}'>{badge_text}</span> <span style='color:#8B8BAA; font-size:12px;'>— {fuente} · {fecha}</span>", unsafe_allow_html=True)
                    st.markdown(f"[Leer artículo completo]({url_noticia})")
                st.divider()
    else:
        st.info("No se encontraron noticias recientes.")

# ============================================================
# PÁGINA: CALCULADORA
# ============================================================
elif pagina == "Calculadora":
    st.markdown("<h2 style='color:#F0EEFF; font-size:22px; font-weight:600; margin-bottom:20px;'>Calculadora de conversión</h2>", unsafe_allow_html=True)

    tipo = st.selectbox("Tipo de conversión", ["Divisas", "Criptomonedas a USD", "Materias primas a USD"])

    col1, col2, col3 = st.columns([2, 1, 2])

    if tipo == "Divisas":
        monedas = ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD", "COP", "MXN",
                   "BRL", "CLP", "ARS", "CNY", "INR", "RUB", "TRY", "ZAR", "SGD", "HKD", "KRW"]
        with col1:
            moneda_de = st.selectbox("De", monedas, index=0)
            monto = st.number_input("Monto", min_value=0.0, value=1.0, step=0.01)
        with col2:
            st.markdown("<br><br><div style='text-align:center; color:#A78BFA; font-size:24px;'>→</div>", unsafe_allow_html=True)
        with col3:
            moneda_a = st.selectbox("A", monedas, index=1)

        if st.button("Convertir", type="primary"):
            with st.spinner("Obteniendo tasa de cambio..."):
                if moneda_de == moneda_a:
                    tasa = 1.0
                elif moneda_de == "USD":
                    tasa = get_tasa_conversion("USD", moneda_a)
                elif moneda_a == "USD":
                    tasa_inv = get_tasa_conversion("USD", moneda_de)
                    tasa = 1 / tasa_inv if tasa_inv else None
                else:
                    tasa_de = get_tasa_conversion("USD", moneda_de)
                    tasa_a = get_tasa_conversion("USD", moneda_a)
                    tasa = (tasa_a / tasa_de) if tasa_de and tasa_a else None

            if tasa:
                resultado_calc = monto * tasa
                st.markdown(f"""
                <div class="rec-card" style="text-align:center; padding:28px;">
                    <div style="color:#8B8BAA; font-size:13px; margin-bottom:8px;">Resultado</div>
                    <div style="color:#F0EEFF; font-size:32px; font-weight:600; margin-bottom:8px;">
                        {monto:,.2f} {moneda_de} = <span style="color:#A78BFA;">{resultado_calc:,.4f} {moneda_a}</span>
                    </div>
                    <div style="color:#8B8BAA; font-size:13px;">Tasa: 1 {moneda_de} = {tasa:.6f} {moneda_a}</div>
                    <div style="color:#8B8BAA; font-size:11px; margin-top:8px;">Tasa en tiempo real · Fuente: Yahoo Finance</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("No se pudo obtener la tasa de cambio. Intenta de nuevo.")

    elif tipo == "Criptomonedas a USD":
        criptos = {k.replace("USDT", ""): v for k, v in CRIPTOS_BINANCE.items()}
        with col1:
            cripto = st.selectbox("Criptomoneda", list(criptos.keys()))
            monto = st.number_input("Cantidad", min_value=0.0, value=1.0, step=0.001)
        with col2:
            st.markdown("<br><br><div style='text-align:center; color:#A78BFA; font-size:24px;'>→</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div style='color:#F0EEFF; font-size:14px; padding-top:8px;'>USD (Dólares)</div>", unsafe_allow_html=True)

        if st.button("Convertir", type="primary"):
            with st.spinner("Obteniendo precio..."):
                data = get_precio_binance(f"{cripto}USDT")
            if data:
                resultado_calc = monto * data['precio']
                st.markdown(f"""
                <div class="rec-card" style="text-align:center; padding:28px;">
                    <div style="color:#8B8BAA; font-size:13px; margin-bottom:8px;">Resultado</div>
                    <div style="color:#F0EEFF; font-size:32px; font-weight:600; margin-bottom:8px;">
                        {monto:,.6f} {cripto} = <span style="color:#A78BFA;">${resultado_calc:,.2f} USD</span>
                    </div>
                    <div style="color:#8B8BAA; font-size:13px;">Precio: 1 {cripto} = ${data['precio']:,.2f} USD</div>
                    <div style="color:#8B8BAA; font-size:11px; margin-top:8px;">Precio en tiempo real · Fuente: Binance</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("No se pudo obtener el precio. Intenta de nuevo.")

    elif tipo == "Materias primas a USD":
        materias = {v: k for k, v in MATERIAS_PRIMAS.items()}
        with col1:
            materia = st.selectbox("Materia prima", list(materias.keys()))
            monto = st.number_input("Cantidad (unidades del contrato)", min_value=0.0, value=1.0, step=0.01)
        with col2:
            st.markdown("<br><br><div style='text-align:center; color:#A78BFA; font-size:24px;'>→</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div style='color:#F0EEFF; font-size:14px; padding-top:8px;'>USD (Dólares)</div>", unsafe_allow_html=True)

        if st.button("Convertir", type="primary"):
            with st.spinner("Obteniendo precio..."):
                data = get_precio_yahoo(materias[materia])
            if data:
                resultado_calc = monto * data['precio']
                st.markdown(f"""
                <div class="rec-card" style="text-align:center; padding:28px;">
                    <div style="color:#8B8BAA; font-size:13px; margin-bottom:8px;">Resultado</div>
                    <div style="color:#F0EEFF; font-size:32px; font-weight:600; margin-bottom:8px;">
                        {monto:,.2f} unidades de {materia} = <span style="color:#A78BFA;">${resultado_calc:,.2f} USD</span>
                    </div>
                    <div style="color:#8B8BAA; font-size:13px;">Precio: 1 unidad = ${data['precio']:,.2f} USD</div>
                    <div style="color:#8B8BAA; font-size:11px; margin-top:8px;">Precio de cierre más reciente · Fuente: Yahoo Finance</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("No se pudo obtener el precio. Intenta de nuevo.")

# ============================================================
# PÁGINA: ACERCA DE
# ============================================================
elif pagina == "Acerca de":
    st.markdown("<h2 style='color:#F0EEFF; font-size:22px; font-weight:600; margin-bottom:20px;'>Sobre ClarityTrade</h2>", unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-card" style="margin-bottom:16px; padding:20px 24px;">
        <div style="color:#F0EEFF; font-size:15px; font-weight:600; margin-bottom:10px;">¿Qué es ClarityTrade?</div>
        <div style="color:#8B8BAA; font-size:13px; line-height:1.8;">
            ClarityTrade es un sistema de análisis predictivo para mercados financieros que combina 
            datos de precios en tiempo real, indicadores técnicos y análisis de sentimiento de noticias 
            para generar recomendaciones claras de compra, espera o venta sobre acciones, divisas, 
            materias primas y criptomonedas.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div style="color:#A78BFA; font-size:13px; font-weight:600; margin-bottom:10px;">Fuentes de datos</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.9;">
                Finnhub API — acciones<br>
                Yahoo Finance — divisas y materias primas<br>
                Binance API — criptomonedas<br>
                NewsAPI — noticias globales
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div style="color:#A78BFA; font-size:13px; font-weight:600; margin-bottom:10px;">Tecnología</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.9;">
                Python 3.14<br>
                Streamlit<br>
                Claude AI (Anthropic)<br>
                Plotly · Pandas
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div style="color:#A78BFA; font-size:13px; font-weight:600; margin-bottom:10px;">Fuentes de noticias</div>
            <div style="color:#8B8BAA; font-size:12px; line-height:1.9;">
                BBC News · Reuters · CNN<br>
                CNBC · The Guardian<br>
                Associated Press<br>
                Wall Street Journal · Bloomberg
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1A1A0D; border:1px solid #3D3A00; border-radius:10px; padding:20px 24px;">
        <div style="color:#FACC15; font-size:13px; font-weight:600; margin-bottom:10px;">Aviso legal importante</div>
        <div style="color:#D4C570; font-size:12px; line-height:1.9;">
            ClarityTrade es una herramienta tecnológica de análisis informativo y no constituye 
            asesoramiento financiero, inversión, corretaje ni ningún tipo de consejo profesional 
            en materia financiera o bursátil.<br><br>
            De conformidad con la normativa colombiana vigente — incluyendo la Ley 964 de 2005, 
            la regulación de la Superintendencia Financiera de Colombia (SFC) y las normas del 
            mercado de valores — la prestación de asesoramiento financiero profesional requiere 
            autorización y registro ante las entidades competentes.<br><br>
            Las recomendaciones generadas por ClarityTrade son el resultado de algoritmos 
            automatizados basados en indicadores técnicos e históricos y no reemplazan el criterio 
            de un asesor financiero certificado. Antes de tomar cualquier decisión de inversión, 
            consulta con un profesional habilitado.<br><br>
            <strong style="color:#FACC15;">El uso de esta herramienta es bajo tu exclusiva responsabilidad.</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)