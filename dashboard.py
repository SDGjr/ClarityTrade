import os
import anthropic
from datetime import datetime, timedelta
from dotenv import load_dotenv, dotenv_values
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from newsapi import NewsApiClient
from textblob import TextBlob

load_dotenv()
env = dotenv_values("C:/Users/sarch/trading-ai/.env")
newsapi = NewsApiClient(api_key=env.get("NEWS_API_KEY"))

st.set_page_config(page_title="ClarityTrade", page_icon="📊", layout="wide")
st.title("📊 ClarityTrade")
st.markdown("### Inteligencia financiera en tiempo real — análisis predictivo basado en datos del mercado global.")

col1, col2 = st.columns([2, 1])
with col1:
    simbolo = st.text_input("Símbolo de la acción", value="AAPL")
with col2:
    nombre_empresa = st.text_input("Nombre de la empresa", value="Apple")

analizar = st.button("🔍 Analizar", type="primary")

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
            page_size=15
        )
        noticias = resultado.get('articles', [])
        puntajes = [TextBlob(n['title']).sentiment.polarity for n in noticias]
        sentimiento = sum(puntajes) / len(puntajes) if puntajes else 0.0

        puntos = 0
        razones = []

        if rsi < 30:
            puntos += 2
            razones.append(f"RSI {rsi:.1f} — sobreventa (señal de COMPRA)")
        elif rsi > 70:
            puntos -= 2
            razones.append(f"RSI {rsi:.1f} — sobrecompra (señal de VENTA)")
        else:
            razones.append(f"RSI neutral ({rsi:.1f})")

        if ma20 > ma50:
            puntos += 1
            razones.append("Tendencia alcista (MA20 > MA50)")
        else:
            puntos -= 1
            razones.append("Tendencia bajista (MA20 < MA50)")

        if macd > macd_sig:
            puntos += 1
            razones.append(f"MACD alcista ({macd:.2f} > {macd_sig:.2f})")
        else:
            puntos -= 1
            razones.append(f"MACD bajista ({macd:.2f} < {macd_sig:.2f})")

        if precio < bb_inf:
            puntos += 2
            razones.append("Precio bajo Bollinger inferior — posible rebote")
        elif precio > bb_sup:
            puntos -= 2
            razones.append("Precio sobre Bollinger superior — posible corrección")
        else:
            razones.append(f"Precio dentro de Bollinger (${bb_inf:.2f} — ${bb_sup:.2f})")

        if sentimiento > 0.1:
            puntos += 1
            razones.append(f"Noticias positivas ({sentimiento:.2f})")
        elif sentimiento < -0.1:
            puntos -= 1
            razones.append(f"Noticias negativas ({sentimiento:.2f})")
        else:
            razones.append(f"Noticias neutrales ({sentimiento:.2f})")

        if puntos >= 2:
            decision, color, emoji = "COMPRAR", "green", "🟢"
            confianza = min(50 + puntos * 10, 90)
            precio_objetivo = precio * 1.05
        elif puntos <= -2:
            decision, color, emoji = "VENDER", "red", "🔴"
            confianza = min(50 + abs(puntos) * 10, 90)
            precio_objetivo = precio * 0.95
        else:
            decision, color, emoji = "MANTENER / ESPERAR", "orange", "🟡"
            confianza = 50
            precio_objetivo = precio

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Precio actual", f"${precio:.2f}")
    m2.metric("RSI", f"{rsi:.1f}")
    m3.metric("MACD", f"{macd:.2f}")
    m4.metric("Bollinger", f"${bb_inf:.2f} — ${bb_sup:.2f}")

    st.divider()
    st.markdown(f"## {emoji} Recomendación: **:{color}[{decision}]**")
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(f"**Precio de entrada:** ${precio:.2f}")
        st.markdown(f"**Precio objetivo:** ${precio_objetivo:.2f}")
        st.markdown(f"**Confianza:** {confianza}%")
        st.progress(confianza / 100)
    with r2:
        st.markdown("**Razones:**")
        for r in razones:
            st.markdown(f"• {r}")

    st.divider()
    st.subheader("🤖 Análisis de ClarityTrade")
    with st.spinner("Generando análisis inteligente..."):
        cliente_ai = anthropic.Anthropic(api_key=env.get("ANTHROPIC_API_KEY"))
        prompt = f"""Eres un analista financiero experto. Analiza estos datos de {nombre_empresa} ({simbolo}) y genera un párrafo de análisis profesional en español, claro y directo, de máximo 4 oraciones. MUY IMPORTANTE: no uses ningún formato markdown, sin asteriscos, sin ##, sin negritas, sin cursivas, sin símbolos especiales. Solo texto plano fluido que explique la situación actual y qué debería considerar un inversor.

Datos:
- Precio actual: ${precio:.2f}
- RSI: {rsi:.1f} ({'sobrevendida' if rsi < 30 else 'sobrecomprada' if rsi > 70 else 'neutral'})
- Tendencia: {'alcista' if ma20 > ma50 else 'bajista'} (MA20: ${ma20:.2f}, MA50: ${ma50:.2f})
- MACD: {'positivo' if macd > macd_sig else 'negativo'} ({macd:.2f} vs señal {macd_sig:.2f})
- Bollinger: precio {'bajo banda inferior' if precio < bb_inf else 'sobre banda superior' if precio > bb_sup else 'dentro de bandas'} (${bb_inf:.2f} — ${bb_sup:.2f})
- Sentimiento noticias: {'positivo' if sentimiento > 0.1 else 'negativo' if sentimiento < -0.1 else 'neutral'} ({sentimiento:.2f})
- Recomendación: {decision} con {confianza}% de confianza"""

        mensaje = cliente_ai.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        analisis_ia = mensaje.content[0].text
        st.markdown(f"_{analisis_ia}_")

    st.divider()
    st.subheader("📊 Precio — últimos 3 meses")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=datos.index, open=datos['Open'].squeeze(), high=datos['High'].squeeze(), low=datos['Low'].squeeze(), close=close, name="Precio"))
    fig.add_trace(go.Scatter(x=datos.index, y=datos['MA_20'], name="MA 20", line=dict(color="orange", width=1.5)))
    fig.add_trace(go.Scatter(x=datos.index, y=datos['MA_50'], name="MA 50", line=dict(color="blue", width=1.5)))
    fig.update_layout(xaxis_rangeslider_visible=False, height=450, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 RSI")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=datos.index, y=datos['RSI'], name="RSI", line=dict(color="purple", width=2)))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="70")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="30")
    fig_rsi.update_layout(height=250, template="plotly_dark", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_rsi, use_container_width=True)

    st.subheader("📊 MACD")
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=datos.index, y=datos['MACD'], name="MACD", line=dict(color="blue", width=2)))
    fig_macd.add_trace(go.Scatter(x=datos.index, y=datos['MACD_signal'], name="Señal", line=dict(color="orange", width=1.5)))
    fig_macd.add_trace(go.Bar(x=datos.index, y=datos['MACD_hist'], name="Histograma", marker_color=['green' if val > 0 else 'red' for val in datos['MACD_hist']]))
    fig_macd.update_layout(height=300, template="plotly_dark")
    st.plotly_chart(fig_macd, use_container_width=True)

    st.subheader("📊 Bandas de Bollinger")
    fig_bb = go.Figure()
    fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_superior'], name="Superior", line=dict(color="red", width=1, dash="dash")))
    fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_media'], name="Media", line=dict(color="orange", width=1)))
    fig_bb.add_trace(go.Scatter(x=datos.index, y=datos['BB_inferior'], name="Inferior", line=dict(color="green", width=1, dash="dash"), fill='tonexty', fillcolor='rgba(0,100,0,0.05)'))
    fig_bb.add_trace(go.Scatter(x=datos.index, y=close, name="Precio", line=dict(color="white", width=2)))
    fig_bb.update_layout(height=350, template="plotly_dark")
    st.plotly_chart(fig_bb, use_container_width=True)

    st.divider()
    st.subheader("📰 Noticias recientes")
    if noticias:
        for noticia in noticias[:5]:
            s = TextBlob(noticia['title']).sentiment.polarity
            icono = "🟢" if s > 0.1 else ("🔴" if s < -0.1 else "🟡")
            imagen_url = noticia.get('urlToImage', '')
            url_noticia = noticia.get('url', '')
            fuente = noticia['source']['name']
            titulo = noticia['title']
            descripcion = noticia.get('description', '')
            with st.container():
                col_img, col_texto = st.columns([1, 3])
                with col_img:
                    if imagen_url:
                        st.image(imagen_url, width=200)
                with col_texto:
                    st.markdown(f"#### {icono} {titulo}")
                    if descripcion:
                        st.markdown(f"{descripcion}")
                    st.markdown(f"*Fuente: {fuente}*")
                    st.markdown(f"[📖 Leer artículo completo]({url_noticia})")
                st.divider()
    else:
        st.info("No se encontraron noticias recientes.")