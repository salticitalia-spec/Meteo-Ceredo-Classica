import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import os

# --- CONFIGURAZIONE ---
if os.path.exists("icona.png"):
    img_icona = Image.open("icona.png")
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon=img_icona, layout="centered")
else:
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗")

st.title("🧗 Meteo Ceredo - Mostro Bovino")

lat, lon = 45.6117, 10.9710

def get_weather_info(code):
    mapping = {
        0: ("☀️", "Sereno"), 1: ("🌤️", "Quasi Sereno"), 2: ("⛅", "Poco Nuvoloso"),
        3: ("☁️", "Nuvoloso"), 45: ("🌫️", "Nebbia"), 51: ("🌦️", "Pioviggine"),
        61: ("🌧️", "Pioggia"), 63: ("🌧️", "Pioggia Forte"), 95: ("⛈️", "Temporale")
    }
    return mapping.get(code, ("☁️", "Nuvole"))

def get_all_data():
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability,weathercode&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,sunshine_duration,wind_speed_10m_max&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,sunshine_duration,wind_speed_10m_max&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data_fc, data_hist = get_all_data()

# --- FUNZIONE CALCOLO INDEX ---
def get_bovino_for_day(day_offset, h_data, f_data):
    # day_offset: 0=Oggi, 1=Domani, ecc.
    # Sommiamo pioggia passata + previsione fino al giorno X
    rain_past = sum(h_data['daily']['precipitation_sum'])
    rain_future = sum(f_data['daily']['precipitation_sum'][:day_offset+1])
    sun_past = sum(h_data['daily']['sunshine_duration']) / 3600
    sun_future = sum(f_data['daily']['sunshine_duration'][:day_offset+1]) / 3600
    
    total_rain = rain_past + rain_future
    total_sun = sun_past + sun_future
    
    bias = (total_sun * 0.005) - (total_rain * 0.12)
    return np.clip(bias, -0.25, 0.15)

# --- SETTORI ---
settori_base = {
    "Mangiafuoco": (75, 5), "Ceredoleso": (77, 3), "Supercanna": (70, 5),
    "Mondo Cano": (70, 5), "Del Peci": (67, 4), "Ostramandra": (60, 6)
}

# --- UI: PREVISIONI METEO 3 GIORNI ---
st.subheader("📅 Previsioni Meteo")
cols_m = st.columns(3)
for i in range(3):
    giorno = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d')
    ico, txt = get_weather_info(data_fc['daily']['weathercode'][i])
    t_max = data_fc['daily']['temperature_2m_max'][i]
    t_min = data_fc['daily']['temperature_2m_min'][i]
    with cols_m[i]:
        st.markdown(f"""<div style='background:#1E1E1E;padding:10px;border-radius:10px;text-align:center;'>
        <b>{giorno}</b><br><span style='font-size:25px;'>{ico}</span><br><small>{txt}</small><br>
        <span style='color:#FF4B4B;'>{t_max}°</span> <span style='color:#00ACF2;'>{t_min}°</span></div>""", unsafe_allow_html=True)

st.write("---")

# --- UI: MOSTRO BOVINO INDEX (OGGI, DOMANI, DOPODOMANI) ---
st.header("🐂 Mostro Bovino Index")
tabs = st.tabs(["Oggi", "Domani", "Dopodomani"])

for day in range(3):
    with tabs[day]:
        bias = get_bovino_for_day(day, data_hist, data_fc)
        cols = st.columns(2)
        for i, (nome, params) in enumerate(settori_base.items()):
            prob_base = params[0] + (bias * 100)
            min_p, max_p = int(prob_base - params[1]), int(prob_base + params[1])
            min_p, max_p = np.clip([min_p, max_p], 0, 100)
            color = "#28a745" if min_p > 70 else "#fd7e14" if min_p > 50 else "#dc3545"
            with cols[i % 2]:
                st.markdown(f"""<div style='background:#262730;padding:12px;border-radius:10px;margin-bottom:10px;border-left:5px solid {color};'>
                <h4 style='margin:0;font-size:16px;'>{nome}</h4>
                <p style='font-size:20px;margin:0;color:{color};font-weight:bold;'>{min_p}-{max_p}%</p>
                </div>""", unsafe_allow_html=True)

# --- STORICO ---
with st.expander("📊 Storico 10gg (Pioggia, Sole, Vento)"):
    df = pd.DataFrame({
        'Giorno': [d[-5:] for d in data_hist['daily']['time']],
        'Pioggia (mm)': data_hist['daily']['precipitation_sum'],
        'Sole (ore)': [round(s/3600,1) for s in data_hist['daily']['sunshine_duration']]
    })
    st.bar_chart(df, x='Giorno', y='Pioggia (mm)')
    st.area_chart(df, x='Giorno', y='Sole (ore)')

if st.button("🔄 AGGIORNA"):
    st.rerun()
