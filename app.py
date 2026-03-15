import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗")

# Stile CSS per icone e box in stile 3B Meteo
st.markdown("""
    <style>
    .forecast-box { 
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        color: #31333f;
        border: 1px solid #d1d5db;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧗 Meteo Ceredo Classica")

lat, lon = 45.6117, 10.9710

# Dizionario icone e testi stile 3B Meteo
def get_weather_info(code):
    mapping = {
        0: ("☀️", "Sereno", "#FFD700"),
        1: ("🌤️", "Quasi Sereno", "#FFE4B5"),
        2: ("⛅", "Poco Nuvoloso", "#E6E6FA"),
        3: ("☁️", "Nuvoloso", "#D3D3D3"),
        45: ("🌫️", "Nebbia", "#F5F5F5"),
        51: ("🌦️", "Pioviggine", "#ADD8E6"),
        61: ("🌧️", "Pioggia", "#87CEEB"),
        63: ("🌧️", "Pioggia Forte", "#4682B4"),
        71: ("❄️", "Neve", "#FFFFFF"),
        80: ("🌦️", "Rovescio", "#00BFFF"),
        95: ("⛈️", "Temporale", "#708090")
    }
    return mapping.get(code, ("☁️", "Nuvole", "#D3D3D3"))

def get_all_data():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability,weathercode&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=Europe%2FRome"
    return requests.get(url).json(), requests.get(url_hist).json()

data, hist = get_all_data()

# --- METEO ATTUALE ---
curr = data['current_weather']
icon, desc, color = get_weather_info(curr['weathercode'])
st.subheader(f"Situazione Attuale: {desc}")
col1, col2, col3 = st.columns(3)
col1.metric("Temperatura", f"{curr['temperature']} °C")
col2.metric("Vento", f"{curr['windspeed']} km/h")
col3.markdown(f"<div style='font-size: 50px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)

# --- PROSSIME ORE ---
st.write("---")
st.subheader("⏳ Previsioni Orarie")
h_time = data['hourly']['time']
h_temp = data['hourly']['temperature_2m']
h_prob = data['hourly']['precipitation_probability']
h_code = data['hourly']['weathercode']

now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
idx = h_time.index(now_str) if now_str in h_time else 0

cols_h = st.columns(5)
for i in range(5):
    f_idx = idx + (i + 1)
    h_icon, _, _ = get_weather_info(h_code[f_idx])
    with cols_h[i]:
        st.markdown(f"**{h_time[f_idx][-5:]}**")
        st.write(h_icon)
        st.write(f"{h_temp[f_idx]}°")
        st.caption(f"💧{h_prob[f_idx]}%")

# --- PROSSIMI 3 GIORNI ---
st.write("---")
st.subheader("📅 Tendenza 3 Giorni")
d_time, d_max, d_min, d_code = data['daily']['time'], data['daily']['temperature_2m_max'], data['daily']['temperature_2m_min'], data['daily']['weathercode']

cols_d = st.columns(3)
for i in range(1, 4):
    giorno = datetime.strptime(d_time[i], '%Y-%m-%d').strftime('%a %d')
    icona, testo, _ = get_weather_info(d_code[i])
    with cols_d[i-1]:
        st.markdown(f"""
        <div class="forecast-box">
            <small>{giorno}</small><br>
            <span style='font-size: 30px;'>{icona}</span><br>
            <b>{testo}</b><br>
            <span style='color: #d32f2f;'>{d_max[i]}°</span> / <span style='color: #1976d2;'>{d_min[i]}°</span>
        </div>
        """, unsafe_allow_html=True)

# --- STORICO PIOGGIA ---
st.write("---")
st.subheader("💧 Pioggia caduta (ultimi 5gg)")
df_rain = pd.DataFrame({
    'Giorno': [d[-5:] for d in hist['daily']['time']], 
    'mm': hist['daily']['precipitation_sum']
})
st.bar_chart(data=df_rain, x='Giorno', y='mm', color="#4682B4")

if st.button("🔄 AGGIORNA"):
    st.rerun()
