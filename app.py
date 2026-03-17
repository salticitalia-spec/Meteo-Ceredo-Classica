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

# --- FUNZIONE CALCOLO PERCEPITA (HEAT INDEX) ---
def calcola_percepita(T, rh):
    if T < 21:
        return T 
    hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (rh * 0.094))
    return round(hi, 1)

# --- UTILS ---
def get_santo(data_obj):
    santi = {"03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio", "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia", "03-21": "S. Benedetto"}
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

giorni_ita = {"Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì", "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"}
mesi_ita = {"March": "Marzo", "April": "Aprile", "May": "Maggio"}

def calcola_stato_parete(data_hist):
    try:
        pioggia_oraria = data_hist['hourly']['precipitation']
        recent = sum(pioggia_oraria[-72:])     
        medium = sum(pioggia_oraria[-168:-72])  
        remote = sum(pioggia_oraria[-240:-168]) 
        carico_idrico = (recent * 1.0) + (medium * 0.7) + (remote * 0.4)
        
        if carico_idrico < 5:
            return "SECCO ☀️", "#00FFFF", "Ottimo ovunque, anche su Peci & Ostramandra."
        elif carico_idrico < 18:
            return "UMIDO 💧", "#FFFF00", "Mangiafuoco e Torre OK. Peci & Ostramandra: canne umide."
        else:
            return "BAGNATO ⚠️", "#FF3131", "Saturazione bosco. Peci & Ostramandra impraticabile."
    except:
        return "N.D.", "#333", "Errore sensori."

# --- STILE CSS ---
st.markdown('''
<style>
.stApp { background-color: #000000 !important; }
h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
.main-banner { background: linear-gradient(90deg, #000 0%, #00FFFF 50%, #000 100%); padding: 1px; border-radius: 10px; margin-bottom: 25px; }
.banner-content { background-color: #000; padding: 12px; border-radius: 9px; text-align: center; }
.banner-title { font-size: 24px; font-weight: 300; letter-spacing: 5px; margin: 0; text-transform: uppercase; }
.info-block { background-color: #000000; border: 1px solid #333; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
.temp-main { font-size: 52px; font-weight: 200; line-height: 1.0; margin: 10px 0; }
.temp-perceived { font-size: 16px; color: #FFA500 !important; margin-bottom: 15px; font-weight: 300; }
.forecast-card { background-color: #050505; border: 1px solid #222; padding: 15px; border-radius: 10px; margin-bottom: 8px; }
.hum-alert { font-size: 11px; color: #FFA500; text-transform: uppercase; margin-top: 8px; font-weight: bold; }
.legenda-kj { font-size: 10px; color: #666; margin-bottom: 15px; border-left: 2px solid #333; padding-left: 10px; }
[data-testid="stChart"] { border: 1px solid #222; border-radius: 8px; padding: 10px; background-color: #020202; }
</style>
''', unsafe_allow_html=True)

# --- RECUPERO DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    url_fc = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
              "&hourly=temperature_2m,relativehumidity_2m,precipitation,shortwave_radiation"
              "&daily=temperature_2m_max,precipitation_sum,shortwave_radiation_sum"
              "&timezone=Europe%2FRome")
    
    start_d = (datetime.now() - timedelta(days=10)).date().isoformat()
    end_d = datetime.now().date().isoformat()
    url_hi = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
              f"&start_date={start_d}&end_date={end_d}"
              "&hourly=precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome")
    
    return requests.get(url_fc).json(), requests.get(url_hi).json()

try:
    dfc, dhi = get_weather_data()
    curr, now = dfc['current_weather'], datetime.now()
    curr_temp = curr["temperature"]
    curr_hum = dfc['hourly']['relativehumidity_2m'][now.hour]
    percepita = calcola_percepita(curr_temp, curr_hum)
    d_str = f"{giorni_ita.get(now.strftime('%A'))}, {now.strftime('%d')} {mesi_ita.get(now.strftime('%B'))}"
except:
    st.error("Errore nel caricamento dati API"); st.stop()

# --- HEADER ---
st.markdown('<div class="main-banner"><div class="banner-content"><div class="banner-title">Meteo Ceredoleso Pro</div></div></div>', unsafe_allow_html=True)

# Alert
afa_warning = "🔥 AFA ELEVATA - GRIP SCARSO" if percepita > 30 else ""
hum_warning = "⚠️ RISCHIO CONDENSA VAJO" if curr_hum > 75 else ""
alert_text = afa_warning if afa_warning else hum_warning

st.markdown(f'''
<div class="info-block">
    <div style="font-size:14px;color:#AAA!important;">{d_str}</div>
    <div style="font-size:10px;color:#00FFFF!important;letter-spacing:2px;margin-bottom:10px;">✨ {get_santo(now)}</div>
    <div class="temp-main">{curr_temp}°</div>
    <div class="temp-perceived">Percepita: {percepita}°</div>
    <div style="display:flex; justify-content:center; gap:25px; font-size:18px;">
        <div style="color:#00FF00!important;">💨 {curr["windspeed"]} <span style="font-size:10px;">km/h</span></div>
        <div style="color:#FFA500!important;">💧 {curr_hum}% <span style="font-size:10px;">UR</span></div>
    </div>
    <div class="hum-alert">{alert_text}</div>
</div>
''', unsafe_allow_html=True)

# --- MOSTRO BOVINO INDEX (SETTORI) ---
st_t, st_c, st_d = calcola_stato_parete(dhi)
st.markdown(f'''
<div style="border:1px solid {st_c};padding:15px;border-radius:12px;text-align:center;margin-bottom:30px;">
    <div style="font-size:9px;color:#666;text-transform:uppercase;">Mostro Bovino Index (KJ/mq = Asciugatura)</div>
    <div style="font-size:22px;color:{st_c};font-weight:bold;">{st_t}</div>
    <div style="font-size:11px;color:#888;">{st_d}</div>
</div>
''', unsafe_allow_html=True)

# --- PREVISIONI ---
st.subheader("Prossimi 3 Giorni")
st.markdown(f'''
<div class="legenda-kj">
    <span style="color:#00FFFF;">● >{THRESHOLD_HIGH} KJ:</span> Rapida<br>
    <span style="color:#FFFF00;">● {THRESHOLD_LOW}-{THRESHOLD_HIGH} KJ:</span> Lenta<br>
    <span style="color:#FF3131;">● <{THRESHOLD_LOW} KJ:</span> Rischio condensa
</div>
''', unsafe_allow_html=True)

for i in range(3):
    d_obj = datetime.strptime(dfc['daily']['time'][i], '%Y-%m-%d')
    irr_v = int(dfc['daily']['shortwave_radiation_sum'][i] * 1000 * CORR_VAJO)
    i_cl = "irr-low" if irr_v < THRESHOLD_LOW else ("irr-high" if irr_v > THRESHOLD_HIGH else "irr-mid")
    avg_hum = int(np.mean(dfc['hourly']['relativehumidity_2m'][i*24:(i+1)*24]))
    max_t = dfc['daily']['temperature_2m_max'][i]
    perc_max = calcola_percepita(max_t, avg_hum)

    st.markdown(f'''
    <div class="forecast-card">
        <div style="display:flex;justify-content:space-between;">
            <span>{giorni_ita.get(d_obj.strftime('%A'))} {d_obj.strftime('%d')}</span>
            <span style="color:#FF3131;">Max {max_t}° (Perc. {perc_max}°)</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:11px;">
            <div style="text-align:center;"><span style="color:#555;font-size:9px;">PIOGGIA</span><br><span style="color:#00FFFF;">{dfc["daily"]["precipitation_sum"][i]}mm</span></div>
            <div style="text-align:center;"><span style="color:#555;font-size:9px;">UMIDITÀ</span><br><span style="color:#FFA500;">{avg_hum}%</span></div>
            <div style="text-align:center;"><span style="color:#555;font-size:9px;">IRRAGG.</span><br><span class="{i_cl}">{irr_v} KJ</span></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# --- STORICO 10 GIORNI ---
st.write("---")
st.subheader("Storico 10 Giorni")
try:
    df_h = pd.DataFrame({
        'Data': pd.to_datetime(dhi['hourly']['time']),
        'Pioggia (mm)': [x*10 for x in dhi['hourly']['precipitation']],
        'Vento (km/h)': dhi['hourly']['windspeed_10m'],
        'Asciugatura (KJ)': [x/50 for x in dhi['hourly']['shortwave_radiation']]
    }).set_index('Data')
    st.line_chart(df_h, color=["#00FFFF", "#00FF00", "#FFFF00"])
except:
    st.warning("Dati storici momentaneamente non disponibili")

if st.button("Aggiorna"):
    st.cache_data.clear()
    st.rerun()
