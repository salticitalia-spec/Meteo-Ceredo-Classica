import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import os

# --- CONFIGURAZIONE ---
if os.path.exists("icona.png"):
    img_icona = Image.open("icona.png")
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon=img_icona, layout="centered")
else:
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗")

st.title("🧗 Meteo Ceredo Classica")

lat, lon = 45.6117, 10.9710

def get_weather_info(code):
    mapping = {
        0: ("☀️", "Sereno"), 1: ("🌤️", "Quasi Sereno"), 2: ("⛅", "Poco Nuvoloso"),
        3: ("☁️", "Nuvoloso"), 45: ("🌫️", "Nebbia"), 51: ("🌦️", "Pioviggine"),
        61: ("🌧️", "Pioggia"), 63: ("🌧️", "Pioggia Forte"), 95: ("⛈️", "Temporale")
    }
    return mapping.get(code, ("☁️", "Nuvole"))

def get_all_data():
    # Previsioni
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability,weathercode&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=Europe%2FRome"
    
    # Storico pioggia ultimi 10 giorni
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10) # <--- Cambiato a 10
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=Europe%2FRome"
    
    return requests.get(url).json(), requests.get(url_hist).json()

data, hist = get_all_data()

# --- ATTUALE ---
curr = data['current_weather']
icon, desc = get_weather_info(curr['weathercode'])
st.subheader(f"Ora: {desc} {icon}")
c1, c2 = st.columns(2)
c1.metric("Temperatura", f"{curr['temperature']} °C")
c2.metric("Vento", f"{curr['windspeed']} km/h")

# --- PROSSIME ORE ---
st.write("---")
st.subheader("⏳ Previsioni Orarie")
h_time, h_temp, h_prob = data['hourly']['time'], data['hourly']['temperature_2m'], data['hourly']['precipitation_probability']
now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
idx = h_time.index(now_str) if now_str in h_time else 0
cols_h = st.columns(5)
for i in range(5):
    f_idx = idx + (i + 1)
    cols_h[i].markdown(f"**{h_time[f_idx][-5:]}**\n\n{h_temp[f_idx]}°\n\n💧{h_prob[f_idx]}%")

# --- 3 GIORNI ---
st.write("---")
st.subheader("📅 Tendenza 3 Giorni")
d_t, d_max, d_min, d_c = data['daily']['time'], data['daily']['temperature_2m_max'], data['daily']['temperature_2m_min'], data['daily']['weathercode']
cols_d = st.columns(3)
for i in range(1, 4):
    giorno = datetime.strptime(d_t[i], '%Y-%m-%d').strftime('%a %d')
    ico, txt = get_weather_info(d_c[i])
    cols_d[i-1].markdown(f"<div style='background:#f0f2f6;padding:10px;border-radius:10px;text-align:center;color:black;'><b>{giorno}</b><br>{ico}<br>{txt}<br><span style='color:red;'>{d_max[i]}°</span> <span style='color:blue;'>{d_min[i]}°</span></div>", unsafe_allow_html=True)

# --- NUOVO STORICO 10 GIORNI ---
st.write("---")
pioggia_totale = sum(hist['daily']['precipitation_sum'])
st.subheader(f"💧 Piovosità ultimi 10 giorni")
st.info(f"Accumulo totale: **{pioggia_totale:.1f} mm**")

df_rain = pd.DataFrame({
    'Giorno': [datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m') for d in hist['daily']['time']], 
    'mm': hist['daily']['precipitation_sum']
})
st.bar_chart(data=df_rain, x='Giorno', y='mm', color="#4682B4")

if st.button("🔄 AGGIORNA"):
    st.rerun()
