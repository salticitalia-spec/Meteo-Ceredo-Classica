import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- PARAMETRI DI SOGLIA ---
THRESHOLD_LOW = 6500   
THRESHOLD_HIGH = 12000 
CORR_VAJO = 0.8 

# --- FUNZIONI LOGICHE ---
def get_weather_icon(code):
    if code in [0, 1]: return "☀️" 
    if code in [2, 3]: return "⛅" 
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    if code in [71, 73, 75, 77, 85, 86]: return "❄️"
    if code in [95, 96, 99]: return "⚡"
    return "☁️"

def get_rain_start(hourly_data, start_index):
    day_rain = hourly_data[start_index : start_index + 24]
    for hour, mm in enumerate(day_rain):
        if mm > 0.1:
            return f"{hour}:00"
    return None

def calcola_percepita(T, rh):
    if T < 21: return T 
    hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (rh * 0.094))
    return round(hi, 1)

def get_santo(data_obj):
    santi = {
        "03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio",
        "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia",
        "03-21": "S. Benedetto"
    }
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

giorni_ita = {"Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì", 
              "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"}

def calcola_stato_parete(data_hist):
    try:
        p = data_hist['hourly']['precipitation']
        recent, medium, remote = sum(p[-72:]), sum(p[-168:-72]), sum(p[-240:-168])
        carico = (recent * 1.0) + (medium * 0.7) + (remote * 0.4)
        if carico < 5: return "SECCO ☀️", "#00FFFF", "Ottimo ovunque, anche su Peci & Ostramandra."
        elif carico < 18: return "UMIDO 💧", "#FFFF00", "Mangiafuoco e Torre OK. Peci & Ostramandra: canne umide."
        else: return "BAGNATO ⚠️", "#FF3131", "Saturazione bosco. Peci & Ostramandra impraticabile."
    except: return "N.D.", "#333", "Errore calcolo."

# --- STILE CSS ---
st.markdown('''
<style>
    .stApp { background-color: #000000; }
    .main-banner {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("icona.png");
        background-size: cover; background-position: center;
        padding: 35px; border-radius: 15px; border: 1px solid #333;
        text-align: center; margin-bottom: 25px;
    }
    .info-block {
        background-color: #0a0a0a; border: 1px solid #222;
        padding: 25px; border-radius: 18px; text-align: center; margin-bottom: 20px;
    }
    .temp-main { font-size: 55px; font-weight: 200; margin: 10px 0; color: #ffffff; }
    .temp-perc { font-size: 17px; color: #FFFF00; font-weight: 300; margin-bottom: 15px; }
    .rain-alert { 
        color: #FF3131; font-size: 12px; font-weight: bold; 
        border: 1px solid #FF3131; padding: 6px; border-radius: 8px; 
        display: inline-block; margin: 12px 0; text-transform: uppercase;
    }
    h3 { color: #00FFFF !important; text-transform: uppercase; letter-spacing: 2px; font-weight: 300; }
</style>
''', unsafe_allow_html=True)

# --- DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    url_fc = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
              "&current_weather=true&hourly=temperature_2m,relativehumidity_2m,"
              "precipitation,shortwave_radiation,weathercode&daily=temperature_2m_max,"
              "precipitation_sum,shortwave_radiation_sum,weathercode&timezone=Europe%2FRome")
    s_date = (datetime.now() - timedelta(days=10)).date().isoformat()
    e_date = datetime.now().date().isoformat()
    url_hi = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
              f"&start_date={s_date}&end_date={e_date}&hourly=precipitation,"
              "windspeed_10m,shortwave_radiation&timezone=Europe%2FRome")
    return requests.get(url_fc).json(), requests.get(url_hi).json()

try:
    dfc, dhi = get_weather_data()
    curr, now = dfc['current_weather'], datetime.now()
    c_temp, c_hum = curr["temperature"], dfc['hourly']['relativehumidity_2m'][now.hour]
    c_rain = dfc['daily']['precipitation_sum'][0]
    percepita = calcola_percepita(c_temp, c_hum)
    d_str = f"{giorni_ita.get(now.strftime('%A'))}, {now.strftime('%d')} Marzo"
except:
    st.error("Dati temporaneamente non disponibili."); st.stop()

# --- HEADER ---
st.markdown('<div class="main-banner"><h1 style="color:#00FFFF; margin:0; font-weight:300; letter-spacing:5px;">CEREDOLESO PRO</h1></div>', unsafe_allow_html=True)

# BLOCCO OGGI
rain_now_time = get_rain_start(dfc['hourly']['precipitation'], 0)
rain_html = f"<div class='rain-alert'>🌧️ INIZIO PIOGGIA: ORE {rain_now_time}</div>" if rain_now_time else ""

st.markdown(f'''
<div class="info-block">
    <div style="color:#888; font-size:15px;">Oggi - {d_str}</div>
    <div style="color:#00FFFF; font-size:12px; margin-bottom:12px; letter-spacing:1px;">✨ {get_santo(now)}</div>
    <div style="font-size:50px;">{get_weather_icon(curr.get("weathercode", 0))}</div>
    <div class="temp-main">{c_temp}°</div>
    <div class="temp-perc">Percepita: {percepita}°</div>
    <div style="display:flex; justify-content:center; gap:25px; margin-top:10px; font-size:18px;">
        <div style="color:#00FF00;">💨 {curr["windspeed"]} <span style="font-size:10px;">km/h</span></div>
        <div style="color:#FFFF00;">💧 {c_hum}% <span style="font-size:10px;">UR</span></div>
        <div style="color:#00FFFF;">🌧️ {c_rain} <span style="font-size:10px;">mm</span></div>
    </div>
    {rain_html}
    <div style="font-size:12px; color:#FFFF00; text-transform:uppercase; margin-top:12px; font-weight:bold;">
        { "🔥 AFA ELEVATA - GRIP SCARSO" if percepita > 30 else ("⚠️ RISCHIO CONDENSA VAJO" if c_hum > 75 else "") }
    </div>
</div>
''', unsafe_allow_html=True)

# MOSTRO BOVINO
st_t, st_c, st_d = calcola_stato_parete(dhi)
st.markdown(f'''
<div style="border:1px solid {st_c}; padding:18px; border-radius:15px; text-align:center; margin-bottom:30px; background-color: rgba(0,0,0,0.3);">
    <div style="font-size:10px; color:#666; text-transform:uppercase; letter-spacing:1px;">Mostro Bovino Index (Stato Parete)</div>
    <div style="font-size:26px; color:{st_c}; font-weight:bold; margin:5px 0;">{st_t}</div>
    <div style="font-size:13px; color:#999;">{st_d}</div>
</div>
''', unsafe_allow_html=True)

# PREVISIONI 3 GIORNI
st.subheader("Prossimi 3 Giorni")
for i in range(1, 4):
    d_obj = datetime.strptime(dfc['daily']['time'][i], '%Y-%m-%d')
    irr_v = int(dfc['daily']['shortwave_radiation_sum'][i] * 1000 * CORR_VAJO)
    
    if irr_v < THRESHOLD_LOW: s_c, s_t = "#FF3131", "Rischio Condensa"
    elif irr_v > THRESHOLD_HIGH: s_c, s_t = "#00FFFF", "Asciugatura Rapida"
    else: s_c, s_t = "#FFFF00", "Asciugatura Lenta"
        
    max_t = dfc['daily']['temperature_2m_max'][i]
    hum_i = int(np.mean(dfc['hourly']['relativehumidity_2m'][i*24:(i+1)*24]))
    p_max = calcola_percepita(max_t, hum_i)
    rain_i_time = get_rain_start(dfc['hourly']['precipitation'], i*24)
    rain_i_html = f"<div class='rain-alert'>🌧️ INIZIO PIOGGIA: ORE {rain_i_time}</div>" if rain_i_time else ""

    st.markdown(f'''
    <div class="info-block" style="border: 1px solid #222;">
        <div style="font-size:20px; font-weight:bold;">{giorni_ita.get(d_obj.strftime('%A'))} {d_obj.strftime('%d')}</div>
        <div style="color:#00FFFF; font-size:11px; margin-bottom:8px;">✨ {get_santo(d_obj)}</div>
        <div style="font-size:40px;">{get_weather_icon(dfc['daily']['weathercode'][i])}</div>
        <div class="temp-main" style="font-size:48px;">{max_t}°</div>
        <div class="temp-perc">Percepita: {p_max}°</div>
        <div style="display:flex; justify-content:center; gap:30px; margin-top:10px; font-size:17px;">
            <div style="color:#00FFFF;">🌧️ {dfc['daily']['precipitation_sum'][i]}mm</div>
            <div style="color:#FFFF00;">💧 {hum_i}% UR</div>
        </div>
        {rain_i_html}
        <div style="margin-top:12px; color:{s_c}; font-weight:bold; font-size:12px; text-transform:uppercase;">{s_t}</div>
    </div>
    ''', unsafe_allow_html=True)

# STORICO
st.write("---")
st.subheader("Storico 10 Giorni")
try:
    h = dhi['hourly']
    df_h = pd.DataFrame({
        'Pioggia': [x*10 for x in h['precipitation']],
        'Vento': h['windspeed_10m'],
        'Asciugatura': [x/50 for x in h['shortwave_radiation']]
    }, index=pd.to_datetime(h['time']))
    st.line_chart(df_h, color=["#00FFFF", "#00FF00", "#FFFF00"])
except: st.warning("Grafico non disponibile.")

if st.button("🔄 Aggiorna Meteo"):
    st.cache_data.clear()
    st.rerun()
