import os  # ClarityTrade v3
import anthropic
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

st.set_page_config(page_title="ClarityTrade", page_icon=None, layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1A1A2E; border-right: 1px solid #2D2D4A; }
.logo-container { display: flex; align-items: center; gap: 10px; padding: 8px 0 24px; }
.logo-icon { width: 32px; height: 32px; background: #7C3AED; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.logo-text { color: #F0EEFF; font-size: 18px; font-weight: 600; }
.metric-card { background: #1A1A2E; border: 1px solid #2D2D4A; border-radius: 10px; padding: 14px 18px; }
.metric-label { color: #8B8BAA; font-size: 11px; margin-bottom: 4px; }
.metric-value { color: #F0EEFF; font-size: 20px; font-weight: 600; }
.rec-card { background: #1A1A2E; border: 1px solid #2D1B69; border-radius: 10px; padding: 18px 22px; margin: 16px 0; }
.news-card { background: #1A1A2E; border: 1px solid #2D2D4A; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }
.badge-buy { background: #0D2B1A; color: #4ADE80; padding: 3px 10px; border-radius: 5px; font-size: 11px; }
.badge-sell { background: #2B0D0D; color: #F87171; padding: 3px 10px; border-radius: 5px; font-size: 11px; }
.badge-hold { background: #1A1A0D; color: #FACC15; padding: 3px 10px; border-radius: 5px; font-size: 11px; }
.section-label { color: #8B8BAA; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M2 14L7 8L10 11L13 6L16 8" stroke="#F0EEFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="16" cy="8" r="2" fill="#A78BFA"/>
            </svg>
        </div>
        <span class="logo-text">ClarityTrade</span>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "",
        ["Inicio", "Análisis", "Noticias", "Acerca de"],
        label_visibility="collapsed"
    )

# ============================================================
# PÁGINA: INICIO
# ============================================================
if pagina == "Inicio":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <div style='display:inline-block; background:#2D1B69; color:#A78BFA; font-size:12px; padding:5px 16px; border-radius:20px; border:1px solid #7C3AED; margin-bottom:16px;'>
            Inteligencia financiera en tiempo real
        </div>
        <h1 style='color:#F0EEFF; font-size:32px; font-weight:600; margin-bottom:12px; line-height:1.3;'>
            Toma decisiones de inversión<br>con datos, no con intuición
        </h1>
        <p style='color:#8B8BAA; font-size:15px; max-width:520px; margin:0 auto 28px; line-height:1.7;'>
            ClarityTrade analiza precios, indicadores técnicos y noticias del mercado global
            para darte recomendaciones claras y precisas sobre cuándo comprar, esperar o vender.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div style='color:#A78BFA; font-size:22px; margin-bottom:10px;'>📈</div>
            <div style='color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:6px;'>Indicadores técnicos</div>
            <div style='color:#8B8BAA; font-size:12px; line-height:1.6;'>Índice de Fuerza Relativa, MACD, Bandas de Bollinger y medias móviles en tiempo real.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div style='color:#A78BFA; font-size:22px; margin-bottom:10px;'>📰</div>
            <div style='color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:6px;'>Análisis de noticias</div>
            <div style='color:#8B8BAA; font-size:12px; line-height:1.6;'>Sentimiento del mercado basado en noticias financieras globales actualizadas.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div style='color:#A78BFA; font-size:22px; margin-bottom:10px;'>🤖</div>
            <div style='color:#F0EEFF; font-size:14px; font-weight:600; margin-bottom:6px;'>IA integrada</div>
            <div style='color:#8B8BAA; font-size:12px; line-height:1.6;'>Análisis descriptivo generado por inteligencia artificial en español natural.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Usa el menú de la izquierda para ir a **Análisis** y comenzar a analizar cualquier acción, divisa o materia prima.")

# ============================================================
# PÁGINA: ANÁLISIS
# ============================================================
elif pagina == "Análisis":
    st.markdown("<div class='section-label'>Análisis de mercado</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        simbolo = st.text_input("Símbolo", value="AAPL", placeholder="AAPL, TSLA, MSFT, EUR=X, GC=F...")
    with col2:
        nombre_empresa = st.text_input("Empresa / Activo", value="Apple")

    analizar = st.button("Analizar", type="primary")

    if analizar or simbolo:
        with st.spinner(f"Analizando {simbolo}..."):
            datos = yf.download(simbolo, period="3mo", interval="1d", progress=False)
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
            bb_med = v(ultimo['BB_media'])

            fecha_desde = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            resultado = newsapi.get_everything(
                q=f'"{nombre_empresa}" AND (earnings OR stock OR shares OR revenue)',
                language="en",
                sort_by="publishedAt",
                from_param=fecha_desde,
                page_size=10
            )
            noticias = resultado.get('articles', [])
            puntajes = [TextBlob(n['title']).sentiment.polarity for n in noticias]
            sentimiento = sum(puntajes) / len(puntajes) if puntajes else 0.0

            puntos = 0
            razones = []

            if rsi < 30:
                puntos += 2
                razones.append(f"Índice de Fuerza Relativa (RSI) en {rsi:.1f} — zona de sobreventa, señal de compra")
            elif rsi > 70:
                puntos -= 2
                razones.append(f"Índice de Fuerza Relativa (RSI) en {rsi:.1f} — zona de sobrecompra, señal de venta")
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
                decision, badge_class = "COMPRAR", "badge-buy"
                confianza = min(50 + puntos * 10, 90)
                precio_objetivo = precio * 1.05
            elif puntos <= -2:
                decision, badge_class = "VENDER", "badge-sell"
                confianza = min(50 + abs(puntos) * 10, 90)
                precio_objetivo = precio * 0.95
            else:
                decision, badge_class = "MANTENER / ESPERAR", "badge-hold"
                confianza = 50
                precio_objetivo = precio

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Precio actual", f"${precio:.2f}")
        m2.metric("Índ. Fuerza Relativa (RSI)", f"{rsi:.1f}")
        m3.metric("Conv./Div. Medias (MACD)", f"{macd:.2f}")
        m4.metric("Bandas de Bollinger (BB)", f"${bb_inf:.2f} — ${bb_sup:.2f}")

        st.markdown(f"""
        <div class="rec-card">
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <div style='color:#8B8BAA; font-size:11px; margin-bottom:4px;'>Recomendación</div>
                    <div style='color:#A78BFA; font-size:22px; font-weight:600;'>{decision}</div>
                </div>
                <div style='text-align:right;'>
                    <div style='color:#8B8BAA; font-size:11px; margin-bottom:4px;'>Precio entrada</div>
                    <div style='color:#F0EEFF; font-size:18px; font-weight:600;'>${precio:.2f}</div>
                </div>
                <div style='text-align:right;'>
                    <div style='color:#8B8BAA; font-size:11px; margin-bottom:4px;'>Precio objetivo</div>
                    <div style='color:#F0EEFF; font-size:18px; font-weight:600;'>${precio_objetivo:.2f}</div>
                </div>
                <div style='text-align:right;'>
                    <div style='color:#8B8BAA; font-size:11px; margin-bottom:4px;'>Confianza</div>
                    <div style='color:#F0EEFF; font-size:18px; font-weight:600;'>{confianza}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-label'>Razones del análisis</div>", unsafe_allow_html=True)
        for r in razones:
            st.markdown(f"— {r}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Análisis de ClarityTrade</div>", unsafe_allow_html=True)
        with st.spinner("Generando análisis..."):
            cliente_ai = anthropic.Anthropic(api_key=get_secret("ANTHROPIC_API_KEY"))
            prompt = f"""Eres un analista financiero experto. Analiza estos datos de {nombre_empresa} ({simbolo}) y genera un párrafo de análisis profesional en español, claro y directo, de máximo 4 oraciones. Sin formato markdown, sin asteriscos, sin símbolos. Solo texto plano fluido.

Datos: Precio ${precio:.2f}, RSI {rsi:.1f}, Tendencia {'alcista' if ma20 > ma50 else 'bajista'}, MACD {'positivo' if macd > macd_sig else 'negativo'} ({macd:.2f}), Bollinger {'bajo banda inferior' if precio < bb_inf else 'sobre banda superior' if precio > bb_sup else 'dentro de bandas'}, Sentimiento {'positivo' if sentimiento > 0.1 else 'negativo' if sentimiento < -0.1 else 'neutral'}, Recomendación: {decision} con {confianza}% confianza."""

            mensaje = cliente_ai.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(mensaje.content[0].text)

        st.divider()
        st.markdown("<div class='section-label'>Gráfico de precios — últimos 3 meses</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=datos.index, open=datos['Open'].squeeze(), high=datos['High'].squeeze(), low=datos['Low'].squeeze(), close=close, name="Precio"))
        fig.add_trace(go.Scatter(x=datos.index, y=datos['MA_20'], name="MA 20 días", line=dict(color="#A78BFA", width=1.5)))
        fig.add_trace(go.Scatter(x=datos.index, y=datos['MA_50'], name="MA 50 días", line=dict(color="#7C3AED", width=1.5)))
        fig.update_layout(xaxis_rangeslider_visible=False, height=420, template="plotly_dark", paper_bgcolor="#0F0F1A", plot_bgcolor="#0F0F1A")
        st.plotly_chart(fig, use_container_width=True)

        col_rsi, col_macd = st.columns(2)
        with col_rsi:
            st.markdown("<div class='section-label'>Índice de Fuerza Relativa (RSI)</div>", unsafe_allow_html=True)
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=datos.index, y=datos['RSI'], name="RSI", line=dict(color="#A78BFA", width=2)))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#F87171", annotation_text="Sobrecompra (70)")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#4ADE80", annotation_text="Sobreventa (30)")
            fig_rsi.update_layout(height=260, template="plotly_dark", paper_bgcolor="#0F0F1A", plot_bgcolor="#0F0F1A", yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_rsi, use_container_width=True)

        with col_macd:
            st.markdown("<div class='section-label'>Conv./Div. de Medias Móviles (MACD)</div>", unsafe_allow_html=True)
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=datos.index, y=datos['MACD'], name="MACD", line=dict(color="#A78BFA", width=2)))
            fig_macd.add_trace(go.Scatter(x=datos.index, y=datos['MACD_signal'], name="Señal", line=dict(color="#F0EEFF", width=1.5)))
            fig_macd.add_trace(go.Bar(x=datos.index, y=datos['MACD_hist'], name="Histograma", marker_color=['#4ADE80' if val > 0 else '#F87171' for val in datos['MACD_hist']]))
            fig_macd.update_layout(height=260, template="plotly_dark", paper_bgcolor="#0F0F1A", plot_bgcolor="#0F0F1A")
            st.plotly_chart(fig_macd, use_container_width=True)

        st.markdown("<div class='section-label'>Bandas de Bollinger (BB)</div>", unsafe_allow_html=True)
        fig_bb = go.Figure()
        fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_superior'], name="Banda superior", line=dict(color="#F87171", width=1, dash="dash")))
        fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_media'], name="Media", line=dict(color="#A78BFA", width=1)))
        fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_inferior'], name="Banda inferior", line=dict(color="#4ADE80", width=1, dash="dash"), fill='tonexty', fillcolor='rgba(74,222,128,0.05)'))
        fig_bb.add_trace(go.Scatter(x=datos.index, y=close, name="Precio", line=dict(color="#F0EEFF", width=2)))
        fig_bb.update_layout(height=320, template="plotly_dark", paper_bgcolor="#0F0F1A", plot_bgcolor="#0F0F1A")
        st.plotly_chart(fig_bb, use_container_width=True)

        st.divider()
        st.markdown("<div class='section-label'>Noticias relacionadas</div>", unsafe_allow_html=True)
        if noticias:
            for noticia in noticias[:5]:
                s = TextBlob(noticia['title']).sentiment.polarity
                badge = "badge-buy" if s > 0.1 else ("badge-sell" if s < -0.1 else "badge-hold")
                badge_text = "Positivo" if s > 0.1 else ("Negativo" if s < -0.1 else "Neutral")
                imagen_url = noticia.get('urlToImage', '')
                url_noticia = noticia.get('url', '')
                titulo = noticia['title']
                descripcion = noticia.get('description', '')
                fuente = noticia['source']['name']
                with st.container():
                    ci, ct = st.columns([1, 4])
                    with ci:
                        if imagen_url:
                            st.image(imagen_url, width=120)
                    with ct:
                        st.markdown(f"**{titulo}**")
                        if descripcion:
                            st.markdown(f"<span style='color:#8B8BAA; font-size:13px;'>{descripcion[:150]}...</span>", unsafe_allow_html=True)
                        st.markdown(f"<span class='{badge}'>{badge_text}</span> <span style='color:#8B8BAA; font-size:12px;'>— {fuente}</span>", unsafe_allow_html=True)
                        st.markdown(f"[Leer artículo completo]({url_noticia})")
                    st.divider()
        else:
            st.info("No se encontraron noticias recientes.")

# ============================================================
# PÁGINA: NOTICIAS
# ============================================================
elif pagina == "Noticias":
    st.markdown("<div class='section-label'>Mercado global</div>", unsafe_allow_html=True)
    st.markdown("### Noticias financieras globales")

    categoria = st.selectbox("Categoría", ["Todas", "Acciones", "Divisas", "Materias primas", "Criptomonedas"])

    queries = {
        "Todas": "stock market OR finance OR investing OR economy",
        "Acciones": "stock market earnings shares equity",
        "Divisas": "forex currency exchange rate dollar euro",
        "Materias primas": "commodities oil gold silver wheat",
        "Criptomonedas": "bitcoin ethereum cryptocurrency crypto"
    }

    with st.spinner("Cargando noticias..."):
        fecha_desde = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        resultado = newsapi.get_everything(
            q=queries[categoria],
            language="en",
            sort_by="publishedAt",
            from_param=fecha_desde,
            page_size=15
        )
        noticias_globales = resultado.get('articles', [])

    if noticias_globales:
        for noticia in noticias_globales[:10]:
            s = TextBlob(noticia['title']).sentiment.polarity
            badge = "badge-buy" if s > 0.1 else ("badge-sell" if s < -0.1 else "badge-hold")
            badge_text = "Positivo" if s > 0.1 else ("Negativo" if s < -0.1 else "Neutral")
            imagen_url = noticia.get('urlToImage', '')
            url_noticia = noticia.get('url', '')
            titulo = noticia['title']
            descripcion = noticia.get('description', '')
            fuente = noticia['source']['name']
            with st.container():
                ci, ct = st.columns([1, 4])
                with ci:
                    if imagen_url:
                        st.image(imagen_url, width=120)
                with ct:
                    st.markdown(f"**{titulo}**")
                    if descripcion:
                        st.markdown(f"<span style='color:#8B8BAA; font-size:13px;'>{descripcion[:150]}...</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='{badge}'>{badge_text}</span> <span style='color:#8B8BAA; font-size:12px;'>— {fuente}</span>", unsafe_allow_html=True)
                    st.markdown(f"[Leer artículo completo]({url_noticia})")
                st.divider()
    else:
        st.info("No se encontraron noticias recientes.")

# ============================================================
# PÁGINA: ACERCA DE
# ============================================================
elif pagina == "Acerca de":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Sobre ClarityTrade")
    st.markdown("""
    ClarityTrade es un sistema de análisis predictivo para mercados financieros que combina
    datos de precios en tiempo real, indicadores técnicos y análisis de sentimiento de noticias
    para generar recomendaciones claras de compra, espera o venta.
    """)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div style='color:#A78BFA; font-size:13px; font-weight:600; margin-bottom:8px;'>Fuentes de datos</div>
            <div style='color:#8B8BAA; font-size:12px; line-height:1.8;'>Finnhub API<br>Yahoo Finance<br>NewsAPI<br>FRED (Fed EE.UU.)</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div style='color:#A78BFA; font-size:13px; font-weight:600; margin-bottom:8px;'>Tecnología</div>
            <div style='color:#8B8BAA; font-size:12px; line-height:1.8;'>Python 3.14<br>Streamlit<br>Claude AI (Anthropic)<br>Plotly</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div style='color:#A78BFA; font-size:13px; font-weight:600; margin-bottom:8px;'>Indicadores</div>
            <div style='color:#8B8BAA; font-size:12px; line-height:1.8;'>RSI (14 períodos)<br>MACD (12/26/9)<br>Bandas de Bollinger<br>Medias móviles 20/50</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style='color:#8B8BAA; font-size:12px; text-align:center; padding:8px 0;'>
        ClarityTrade es una herramienta de análisis informativo. No constituye asesoramiento financiero.
        Siempre consulta con un profesional antes de tomar decisiones de inversión.
    </div>
    """, unsafe_allow_html=True)