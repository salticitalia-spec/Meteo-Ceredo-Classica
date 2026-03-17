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

# --- FUNZIONE MAPPA ICONE ---
def get_weather_icon(code):
    if code in [0, 1]: return "☀️" 
    if code in [2, 3]: return "⛅" 
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    if code in [71, 73, 75, 77, 85, 86]: return "❄️"
    if code in [95, 96, 99]: return "⚡"
    return "☁️"

# --- FUNZIONE INIZIO PIOGGIA ---
def get_rain_start(hourly_data, start_index):
    day_rain = hourly_data[start_index : start_index + 24]
    for hour, mm in enumerate(day_rain):
        if mm > 0.1:
            return f"{hour}:00"
    return None

# --- FUNZIONE CALCOLO PERCEPITA ---
def calcola_percepita(T, rh):
    if T < 21: return T 
    hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (rh * 0.094))
    return round(hi, 1)

# --- UTILS SANTI ---
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
.stApp { background-color: #000000 !important; }
h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
.main-banner { 
    background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("https://raw.githubusercontent.com/vostro-repo/main/ceredo_falesia_classica.jpg");
    background-size: cover; background-position: center; padding: 25px; border-radius: 12px; border: 1px solid #00FFFF; text-align: center; margin-bottom: 25px;
}
.banner-title { font-size: 26px; font-weight: 300; letter-spacing: 4px; text-transform: uppercase; margin: 0; color: #00FFFF !important; }
.info-block { background-color: #050505; border: 1px solid #333; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
.temp-main { font-size: 56px; font-weight: 200; line-height: 1.0; margin: 10px 0; color: #FFFFFF !important; }
.temp-perceived { font-size: 16px; color: #FFFF00 !important; margin-bottom: 15px; font-weight: 300; }
.hum-alert { font-size: 12px; color: #FFFF00; text-transform: uppercase; margin-top: 10px; font-weight: bold; }
.rain-warning { font-size: 12px; color: #FF3131; font-weight: bold; margin-top: 8px; border: 1px solid #FF3131; padding: 5px; border-radius: 6px; display: inline-block; }
.weather-icon-large { font-size: 45px; margin-bottom: 5px; }
[data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color: #020202; }
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
    st.error("Errore nel caricamento dei dati."); st.stop()

# --- HEADER ---
st.markdown(f'''
<div class="main-banner">
    <div class="banner-title">Meteo Ceredoleso Pro</div>
    <div style="font-size: 10px; color: #AAA; margin-top: 5px;">Falesia Classica</div>
</div>
''', unsafe_allow_html=True)

# Blocco Oggi
alert_text = "🔥 AFA ELEVATA - GRIP SCARSO" if percepita > 30 else ("⚠️ RISCHIO CONDENSA VAJO" if c_hum > 75 else "")
icon_today = get_weather_icon(curr.get("weathercode", 0))
rain_now = get_rain_start(dfc['hourly']['precipitation'], 0)
rain_now_info = f'<div class="rain-warning">🌧️ INIZIO PIOGGIA: ORE {rain_now}</div>' if rain_now else ""

st.markdown(f'''
<div class="info-block">
    <div style="font-size:14px; color:#AAA;">Oggi - {d_str}</div>
    <div style="font-size:10px; color:#00FFFF; letter-spacing:2px; margin-bottom:10px;">✨ {get_santo(now)}</div>
    <div class="weather-icon-large">{icon_today}</div>
    <div class="temp-main">{c_temp}°</div>
    <div class="temp-perceived">Percepita: {percepita}°</div>
    <div style="display:flex; justify-content:center; gap:20px; font-size:17px;">
        <div style="color:#00FF00;">💨 {curr["windspeed"]} <span style="font-size:10px;">km/h</span></div>
        <div style="color:#FFFF00;">💧 {c_hum}% <span style="font-size:10px;">UR</span></div>
        <div style="color:#00FFFF;">🌧️ {c_rain} <span style="font-size:10px;">mm</span></div>
    </div>
    {rain_now_info}
    <div class="hum-alert">{alert_text}</div>
</div>
''', unsafe_allow_html=True)

# --- MOSTRO BOVINO ---
st_t, st_c, st_d = calcola_stato_parete(dhi)
st.markdown(f'''
<div style="border:1px solid {st_c}; padding:15px; border-radius:12px; text-align:center; margin-bottom:30px;">
    <div style="font-size:9px; color:#666; text-transform:uppercase;">Mostro Bovino Index (Stato Parete)</div>
    <div style="font-size:22px; color:{st_c}; font-weight:bold;">{st_t}</div>
    <div style="font-size:11px; color:#888;">{st_d}</div>
</div>
''', unsafe_allow_html=True)

# --- PREVISIONI 3 GIORNI ---
st.subheader("Prossimi 3 Giorni")
for i in range(1, 4):
    d_obj = datetime.strptime(dfc['daily']['time'][i], '%Y-%m-%d')
    irr_v = int(dfc['daily']['shortwave_radiation_sum'][i] * 1000 * CORR_VAJO)
    
    if irr_v < THRESHOLD_LOW: status_color, status_text = "#FF3131", "Rischio Condensa"
    elif irr_v > THRESHOLD_HIGH: status_color, status_text = "#00FFFF", "Asciugatura Rapida"
    else: status_color, status_text = "#FFFF00", "Asciugatura Lenta"
        
    avg_hum = int(np.mean(dfc['hourly']['relativehumidity_2m'][i*24:(i+1)*24]))
    max_t = dfc['daily']['temperature_2m_max'][i]
    p_max = calcola_percepita(max_t, avg_hum)
    icon_day = get_weather_icon(dfc['daily']['weathercode'][i])
    rain_start = get_rain_start(dfc['hourly']['precipitation'], i*24)
    rain_info = f'<div class="rain-warning">🌧️ INIZIO PIOGGIA: ORE {rain_start}</div>' if rain_start else ""

    st.markdown(f'''
    <div class="info-block" style="border: 1px solid #222;">
        <div style="font-size:18px; font-weight:bold;">{giorni_ita.get(d_obj.strftime('%A'))} {d_obj.strftime('%d')}</div>
        <div style="font-size:10px; color:#00FFFF; letter-spacing:2px; margin-bottom:10px;">✨ {get_santo(d_obj)}</div>
        <div class="weather-icon-large" style="font-size:35px;">{icon_day}</div>
        <div class="temp-main" style="font-size:45px;">{max_t}°</div>
        <div class="temp-perceived">Percepita: {p_max}°</div>
        <div style="display:flex; justify-content:center; gap:25px; font-size:16px;">
            <div style="color:#00FFFF;">🌧️ {dfc["daily"]["precipitation_sum"][i]}mm</div>
            <div style="color:#FFFF00;">💧 {avg_hum}% UR</div>
        </div>
        {rain_info}
        <div style="margin-top:10px; font-size:11px; font-weight:bold; color:{status_color}; text-transform:uppercase;">
            {status_text}
        </div>
    </div>
    ''', unsafe_allow_html=True)

# --- STORICO ---
st.write("---")
st.subheader("Storico 10 Giorni")
try:
    h_data = dhi['hourly']
    df_h = pd.DataFrame({
        'Pioggia': [x*10 for x in h_data['precipitation']],
        'Vento': h_data['windspeed_10m'],
        'Asciugatura': [x/50 for x in h_data['shortwave_radiation']]
    }, index=pd.to_datetime(h_data['time']))
    st.line_chart(df_h, color=["#00FFFF", "#00FF00", "#FFFF00"])
except: st.warning("Dati storici in aggiornamento.")

if st.button("Aggiorna"):
    st.cache_data.clear()
    st.rerun()
