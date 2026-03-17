import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- PARAMETRI ---
THRESHOLD_LOW, THRESHOLD_HIGH, CORR_VAJO = 6500, 12000, 0.8

# --- FUNZIONI ---
def get_weather_icon(code):
    icons = {0: "☀️", 1: "☀️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️", 51: "🌧️", 53: "🌧️", 55: "🌧️", 61: "🌧️", 63: "🌧️", 65: "🌧️", 71: "❄️", 95: "⚡"}
    return icons.get(code, "☁️")

def get_rain_start(hourly_data, start_index):
    day_rain = hourly_data[start_index : start_index + 24]
    for hour, mm in enumerate(day_rain):
        if mm > 0.1: return f"{hour}:00"
    return None

def calcola_percepita(T, rh):
    if T < 21: return T
    return round(0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (rh * 0.094)), 1)

def get_santo(data_obj):
    santi = {"03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio", "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia", "03-21": "S. Benedetto"}
    return santi.get(data_obj.strftime("%m-%d"), "S. del Giorno")

# --- CSS (ANTI-BLOCCHI BIANCHI) ---
st.markdown('<style>.stApp{background-color:#000;}.main-banner{background:linear-gradient(rgba(0,0,0,0.7),rgba(0,0,0,0.7)),url("icona.png");background-size:cover;background-position:center;padding:35px;border-radius:15px;border:1px solid #333;text-align:center;margin-bottom:20px;}.info-card{background-color:#0c0c0c;border:1px solid #222;padding:20px;border-radius:15px;text-align:center;margin-bottom:15px;}.t-main{font-size:55px;font-weight:200;color:#fff;margin:5px 0;}.t-perc{font-size:16px;color:#FF0;margin-bottom:10px;}.rain-tag{color:#F31;font-size:11px;font-weight:bold;border:1px solid #F31;padding:4px 10px;border-radius:5px;display:inline-block;margin:10px 0;}.val-box{display:flex;justify-content:center;gap:15px;font-size:17px;margin-top:10px;}[data-testid="stChart"]{border:1px solid #222;border-radius:10px;padding:10px;background-color:#020202;}</style>', unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_data():
    lat, lon = 45.6117, 10.9710
    fc = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation,shortwave_radiation,weathercode,windspeed_10m&daily=temperature_2m_max,precipitation_sum,shortwave_radiation_sum,weathercode,windspeed_10m_max&timezone=Europe%2FRome").json()
    hi = requests.get(f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={(datetime.now()-timedelta(days=10)).date()}&end_date={datetime.now().date()}&hourly=precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome").json()
    return fc, hi

try:
    dfc, dhi = fetch_data()
    curr, now = dfc['current_weather'], datetime.now()
    c_temp, c_hum = curr["temperature"], dfc['hourly']['relativehumidity_2m'][now.hour]
    c_rain, c_code = dfc['daily']['precipitation_sum'][0], curr.get("weathercode", 0)
    percepita = calcola_percepita(c_temp, c_hum)
except:
    st.error("Errore API"); st.stop()

# --- HEADER ---
st.markdown('<div class="main-banner"><h1 style="color:#0FF;font-weight:200;letter-spacing:6px;margin:0;">CEREDOLESO PRO</h1></div>', unsafe_allow_html=True)

# --- BLOCCO OGGI ---
rain_t = get_rain_start(dfc['hourly']['precipitation'], 0)
rain_h = f'<div class="rain-tag">🌧️ INIZIO PIOGGIA: ORE {rain_t}</div>' if rain_t else ""
cond = "🔥 AFA ELEVATA" if percepita > 30 else ("⚠️ RISCHIO CONDENSA" if c_hum > 75 else "")

st.markdown(f'<div class="info-card"><div style="color:#777;font-size:14px;">Oggi - {now.strftime("%d %B")}</div><div style="color:#0FF;font-size:11px;margin-bottom:10px;">✨ {get_santo(now)}</div><div style="font-size:50px;">{get_weather_icon(c_code)}</div><div class="t-main">{c_temp}°</div><div class="t-perc">Percepita: {percepita}°</div><div class="val-box"><div style="color:#0F0;">💨 {curr["windspeed"]}kph</div><div style="color:#FF0;">💧 {c_hum}%</div><div style="color:#0FF;">🌧️ {c_rain}mm</div></div>{rain_h}<div style="font-size:11px;color:#FF0;font-weight:bold;margin-top:10px;">{cond}</div></div>', unsafe_allow_html=True)

# --- MOSTRO BOVINO ---
p_hist = dhi['hourly']['precipitation']
carico = (sum(p_hist[-72:]) * 1.0) + (sum(p_hist[-168:-72]) * 0.7)
m_t, m_c = ("SECCO ☀️", "#0FF") if carico < 5 else (("UMIDO 💧", "#FF0") if carico < 18 else ("BAGNATO ⚠️", "#F31"))
st.markdown(f'<div style="border:1px solid {m_c};padding:15px;border-radius:12px;text-align:center;margin-bottom:25px;"><div style="font-size:10px;color:#666;text-transform:uppercase;">Mostro Bovino Index</div><div style="font-size:24px;color:{m_c};font-weight:bold;">{m_t}</div></div>', unsafe_allow_html=True)

# --- PREVISIONI 3 GIORNI ---
st.subheader("Prossimi 3 Giorni")
for i in range(1, 4):
    d_obj = datetime.strptime(dfc['daily']['time'][i], '%Y-%m-%d')
    irr = int(dfc['daily']['shortwave_radiation_sum'][i] * 1000 * CORR_VAJO)
    s_c, s_t = ("#F31", "Rischio Condensa") if irr < THRESHOLD_LOW else (("#0FF", "Asciugatura Rapida") if irr > THRESHOLD_HIGH else ("#FF0", "Asciugatura Lenta"))
    max_t, hum_i = dfc['daily']['temperature_2m_max'][i], int(np.mean(dfc['hourly']['relativehumidity_2m'][i*24:(i+1)*24]))
    wind_i = dfc['daily']['windspeed_10m_max'][i]
    r_t = get_rain_start(dfc['hourly']['precipitation'], i*24)
    r_h = f'<div class="rain-tag">🌧️ INIZIO PIOGGIA: ORE {r_t}</div>' if r_t else ""
    
    st.markdown(f'<div class="info-card"><div style="font-size:18px;font-weight:bold;">{d_obj.strftime("%d %B")}</div><div style="color:#0FF;font-size:10px;margin-bottom:5px;">✨ {get_santo(d_obj)}</div><div style="font-size:40px;">{get_weather_icon(dfc["daily"]["weathercode"][i])}</div><div class="t-main" style="font-size:45px;">{max_t}°</div><div class="t-perc">Percepita: {calcola_percepita(max_t, hum_i)}°</div><div class="val-box"><div style="color:#0F0;">💨 {wind_i}kph</div><div style="color:#FF0;">💧 {hum_i}%</div><div style="color:#0FF;">🌧️ {dfc["daily"]["precipitation_sum"][i]}mm</div></div>{r_h}<div style="margin-top:10px;color:{s_c};font-weight:bold;font-size:11px;text-transform:uppercase;">{s_t}</div></div>', unsafe_allow_html=True)

# --- STORICO 10 GIORNI ---
st.write("---")
st.subheader("Storico 10 Giorni")
try:
    h = dhi['hourly']
    df_h = pd.DataFrame({'Pioggia (mmx10)': [x*10 for x in h['precipitation']], 'Vento (kph)': h['windspeed_10m'], 'Asciugatura': [x/50 for x in h['shortwave_radiation']]}, index=pd.to_datetime(h['time']))
    st.line_chart(df_h, color=["#00FFFF", "#00FF00", "#FFFF00"])
except: st.warning("Dati grafici non pronti.")

if st.button("Aggiorna Dati"):
    st.cache_data.clear()
    st.rerun()
