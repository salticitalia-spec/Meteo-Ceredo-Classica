import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Meteo Ceredo", page_icon="🧗")

# CSS per migliorare l'estetica delle previsioni
st.markdown("""
    <style>
    .forecast-box { background-color: #262730; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧗 Meteo Ceredo Classica")

lat, lon = 45.6117, 10.9710

# 1. FUNZIONE UNICA PER TUTTI I DATI
def get_all_data():
    # Previsioni attuali, orarie e giornaliere
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=Europe%2FRome"
    # Storico pioggia
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=Europe%2FRome"
    
    return requests.get(url).json(), requests.get(url_hist).json()

data, hist = get_all_data()

# --- SEZIONE 1: METEO ATTUALE ---
curr = data['current_weather']
col1, col2 = st.columns(2)
col1.metric("Temp. Attuale", f"{curr['temperature']} °C")
col2.metric("Vento", f"{curr['windspeed']} km/h")

# --- SEZIONE 2: PROSSIME ORE (Orizzontale) ---
st.write("---")
st.subheader("⏳ Prossime Ore")
h_time, h_temp, h_prob = data['hourly']['time'], data['hourly']['temperature_2m'], data['hourly']['precipitation_probability']
now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
idx = h_time.index(now_str) if now_str in h_time else 0

cols_h = st.columns(4)
for i in range(4):
    f_idx = idx + (i + 1)
    cols_h[i].markdown(f"**{h_time[f_idx][-5:]}**\n\n{h_temp[f_idx]}°\n\n💧{h_prob[f_idx]}%")

# --- SEZIONE 3: PREVISIONI 3 GIORNI (Novità!) ---
st.write("---")
st.subheader("📅 Prossimi 3 Giorni")
d_time = data['daily']['time']
d_max = data['daily']['temperature_2m_max']
d_min = data['daily']['temperature_2m_min']
d_code = data['daily']['weathercode']

# Dizionario icone meteo semplici
icons = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 51: "🌦️", 61: "🌧️", 71: "❄️", 95: "⛈️"}

cols_d = st.columns(3)
for i in range(1, 4): # Partiamo da domani (1) a tra 3 giorni (3)
    giorno = datetime.strptime(d_time[i], '%Y-%m-%d').strftime('%a %d')
    icona = icons.get(d_code[i], "☁️")
    with cols_d[i-1]:
        st.markdown(f"""
        <div class="forecast-box">
            <b>{giorno}</b><br>
            <span style='font-size: 25px;'>{icona}</span><br>
            <small>↑{d_max[i]}° ↓{d_min[i]}°</small>
        </div>
        """, unsafe_allow_html=True)

# --- SEZIONE 4: STORICO PIOGGIA ---
st.write("---")
st.subheader("💧 Pioggia ultimi 5 giorni (mm)")
df_rain = pd.DataFrame({
    'Giorno': [d[-5:] for d in hist['daily']['time']], 
    'Pioggia (mm)': hist['daily']['precipitation_sum']
})
st.bar_chart(data=df_rain, x='Giorno', y='Pioggia (mm)', color="#4caf50")

if st.button("🔄 AGGIORNA"):
    st.rerun()
