import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- PARAMETRI DI SOGLIA ---
THRESHOLD_LOW = 7000   
THRESHOLD_HIGH = 13500 

# --- UTILS ---
def get_santo(data_obj):
    santi = {
        "03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio",
        "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia",
        "03-21": "S. Benedetto"
    }
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

giorni_ita = {"Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì", "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"}
mesi_ita = {"March": "Marzo", "April": "Aprile", "May": "Maggio"}

# --- MOSTRO BOVINO INDEX (MODELLO BOSCO) ---
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
css_style = f'''
<style>
.stApp {{ background-color: #000000 !important; }}
h1, h2, h3, h4, p, span, div {{ color: #FFFFFF !important; font-family: 'Inter', sans-serif; }}
.main-banner {{ background: linear-gradient(90deg, #000 0%, #00FFFF 50%, #000 100%); padding: 1px; border-radius: 10px; margin-bottom: 25px; }}
.banner-content {{ background-color: #000; padding: 12px; border-radius: 9px; text-align: center; }}
.banner-title {{ font-size: 24px; font-weight: 300; letter-spacing: 5px; margin: 0; text-transform: uppercase; }}
.info-block {{ background-color: #000000; border: 1px solid #333; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; }}
.temp-main {{ font-size: 52px; font-weight: 200; line-height: 1.2; margin: 10px 0; }}
.forecast-card {{ background-color: #050505; border: 1px solid #222; padding: 15px; border-radius: 10px; margin-bottom: 8px; }}
.irr-low {{ color: #FF3131 !important; }}      
.irr-mid {{ color: #FFFF00 !important; }}      
.irr-high {{ color: #00FFFF !important; font-weight: 600 !important; }} 
.hum-alert {{ font-size: 10px; color: #FFA500; text-transform: uppercase; margin-top: 5px; font-weight: bold; }}
[data-testid="stChart"] {{ border: 1px solid #222; border-radius: 8px; padding: 10px; background-color: #020202; }}
</style>
'''
st.markdown(css_style, unsafe_allow_html=True)

# --- RECUPERO DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    url_fc = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
              f"&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation,windspeed_10m,shortwave_radiation"
              f"&daily=temperature_2m_max,precipitation_sum,windspeed_10m_max,shortwave_radiation_sum"
              f"&timezone=Europe%2FRome")
    start_d = (datetime.now().date() - timedelta(days=10)).isoformat()
    end_d = datetime.now().date().isoformat()
    url_hi = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
              f"&start_date={start_d}&end_date={end_d}&hourly=precipitation,windspeed_10m,shortwave_radiation"
              f"&timezone=Europe%2FRome")
    return requests.get(url_fc).json(), requests.get(url_hi).json()

try:
    dfc, dhi = get_weather_data()
    curr, now = dfc['current_weather'], datetime.now()
    # Recupero umidità attuale (l'API current_weather non la dà sempre, la prendiamo dall'hourly)
    idx_now = now.hour
    curr_hum = dfc['hourly']['relativehumidity_2m'][idx_now]
    d_str = f"{giorni_ita.get(now.strftime('%A'))}, {now.strftime('%d')} {mesi_ita.get(now.strftime('%B'))}"
except:
    st.error("Errore API"); st.stop()

# --- HEADER ---
st.markdown('<div class="main-banner"><div class="banner-content"><div class="banner-title">Meteo Ceredoleso Pro</div></div></div>', unsafe_allow_html=True)

# --- REAL-TIME ---
hum_warning = "⚠️ Rischio Condensa Vajo" if curr_hum > 80 else ""
st.markdown(f'''
    <div class="info-block">
        <div style="font-size:14px;color:#AAA!important;">{d_str}</div>
        <div style="font-size:10px;color:#00FFFF!important;letter-spacing:2px;">✨ {get_santo(now)}</div>
        <div class="temp-main">{curr["temperature"]}°</div>
        <div style="display:flex; justify-content:center; gap:20px; font-size:18px;">
            <div style="color:#00FF00!important;">💨 {curr["windspeed"]} <span style="font-size:10px;">km/h</span></div>
            <div style="color:#FFA500!important;">💧 {curr_hum}% <span style="font-size:10px;">UR</span></div>
        </div>
        <div class="hum-alert">{hum_warning}</div>
    </div>
''', unsafe_allow_html=True)

# --- MOSTRO BOVINO INDEX ---
st_t, st_c, st_d = calcola_stato_parete(dhi)
st.markdown(f'<div style="border:1px solid {st_c};padding:15px;border-radius:12px;text-align:center;margin-bottom:30px;"><div style="font-size:9px;color:#666;text-transform:uppercase;">Mostro Bovino Index (Modello Bosco)</div><div style="font-size:22px;color:{st_c};font-weight:bold;">{st_t}</div><div style="font-size:11px;color:#888;">{st_d}</div></div>', unsafe_allow_html=True)

# --- PREVISIONI 3 GIORNI ---
st.subheader("Prossimi 3 Giorni")
for i in range(3):
    d_obj = datetime.strptime(dfc['daily']['time'][i], '%Y-%m-%d')
    d_lab = f"{giorni_ita.get(d_obj.strftime('%A'))} {d_obj.strftime('%d')}"
    irr_v = int(dfc['daily']['shortwave_radiation_sum'][i] * 1000)
    i_cl = "irr-low" if irr_v < THRESHOLD_LOW else ("irr-high" if irr_v > THRESHOLD_HIGH else "irr-mid")
    
    # Media umidità giornaliera per la card (approssimata sulle 24h)
    start_idx, end_idx = i*24, (i+1)*24
    avg_hum = int(np.mean(dfc['hourly']['relativehumidity_2m'][start_idx:end_idx]))
    
    card_html = f'<div class="forecast-card">'
    card_html += f'<div style="display:flex;justify-content:space-between;"><span>{d_lab}</span><span style="color:#FF3131;">Max {dfc["daily"]["temperature_2m_max"][i]}°</span></div>'
    card_html += f'<div style="display:flex;justify-content:space-between;margin-top:8px;font-size:11px;">'
    card_html += f'<div style="text-align:center;"><span style="color:#555;font-size:9px;">PIOGGIA</span><br><span style="color:#00FFFF;">{dfc["daily"]["precipitation_sum"][i]}mm</span></div>'
    card_html += f'<div style="text-align:center;"><span style="color:#555;font-size:9px;">UMIDITÀ</span><br><span style="color:#FFA500;">{avg_hum}%</span></div>'
    card_html += f'<div style="text-align:center;"><span style="color:#555;font-size:9px;">IRRAGG.</span><br><span class="{i_cl}">{irr_v} KJ</span></div>'
    card_html += f'</div></div>'
    st.markdown(card_html, unsafe_allow_html=True)

# --- STORICO ---
st.write("---")
df_h = pd.DataFrame({'Data': pd.to_datetime(dhi['hourly']['time']), 'Pioggia': [x*10 for x in dhi['hourly']['precipitation']], 'Vento': dhi['hourly']['windspeed_10m'], 'Irragg': [x/50 for x in dhi['hourly']['shortwave_radiation']]}).set_index('Data')
st.line_chart(df_h, color=["#00FFFF", "#00FF00", "#FFFF00"])

if st.button("Aggiorna"):
    st.cache_data.clear(); st.rerun()
