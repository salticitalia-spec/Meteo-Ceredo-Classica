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

# --- STILE CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #000000 !important; }}
    h1, h2, h3, h4, p, span, div {{ color: #FFFFFF !important; font-family: 'Inter', sans-serif; }}
    
    .main-banner {{
        background: linear-gradient(90deg, #000 0%, #00FFFF 50%, #000 100%);
        padding: 1px; border-radius: 10px; margin-bottom: 25px;
    }}
    .banner-content {{ background-color: #000; padding: 12px; border-radius: 9px; text-align: center; }}
    .banner-title {{ font-size: 22px; font-weight: 300; letter-spacing: 5px; margin: 0; }}
    .banner-desc {{ font-size: 11px; color: #00FFFF !important; font-weight: 300; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }}
    
    .info-block {{
        background-color: #000000; border: 1px solid #333; padding: 20px;
        border-radius: 12px; text-align: center; margin-bottom: 30px;
    }}
    .temp-main {{ font-size: 52px; font-weight: 200; line-height: 1.2; margin: 10px 0; }}
    
    .forecast-card {{
        background-color: #050505; border: 1px solid #222; padding: 15px;
        border-radius: 10px; margin-bottom: 8px;
    }}
    
    .legenda-container {{
        display: flex; justify-content: space-around; padding: 10px;
        background-color: #080808; border: 1px solid #222; border-radius: 8px;
        margin-bottom: 15px;
    }}
    .legenda-item {{ font-size: 9px; text-transform: uppercase; letter-spacing: 1px; font-weight: 400; }}
    .dot {{ height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }}

    .irr-low {{ color: #FF3131 !important; }}      
    .irr-mid {{ color: #FFFF00 !important; }}      
    .irr-high {{ color: #00FFFF !important; font-weight: 600 !important; }} 

    [data-testid="stChart"] {{ border: 1px solid #222; border-radius: 8px; padding: 10px; background-color: #020202; }}
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation&daily=temperature_2m_max,precipitation_sum,windspeed_10m_max,shortwave_radiation_sum&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

try:
    data_fc, data_hist = get_weather_data()
    curr = data_fc['current_weather']
    now = datetime.now()
    data_str = f"{giorni_ita.get(now.strftime('%A'))}, {now.strftime('%d')} {mesi_ita.get(now.strftime('%B'))}"
except:
    st.error("Errore API.")
    st.stop()

# --- HEADER ---
st.markdown('<div class="main-banner"><div class="banner-content"><div class="banner-title">CEREDOLESO PRO</div><div class="banner-desc">previsioni meteo falesia di ceredo</div></div></div>', unsafe_allow_html=True)

# --- REAL-TIME ---
st.markdown(f"""
    <div class="info-block">
        <div style="font-size: 14px; font-weight: 300; color: #AAA !important;">{data_str}</div>
        <div style="font-size: 10px; color: #00FFFF !important; text-transform: uppercase; letter-spacing: 2px;">✨ {get_santo(now)}</div>
        <div class="temp-main">{curr['temperature']}°</div>
        <div style="font-size: 18px; color: #00FF00 !important; font-weight: 300;">💨 {curr['windspeed']} <span style="font-size:12px;">km/h</span></div>
    </div>
""", unsafe_allow_html=True)

# --- PREVISIONI 3 GIORNI ---
st.subheader("Prossimi 3 Giorni")

st.markdown(f"""
    <div class="legenda-container">
        <div class="legenda-item"><span class="dot" style="background-color: #00FFFF;"></span>Asciugatura Rapida</div>
        <div class="legenda-item"><span class="dot" style="background-color: #FFFF00;"></span>Standard</div>
        <div class="legenda-item"><span class="dot" style="background-color: #FF3131;"></span>Lenta/Umidità</div>
    </div>
""", unsafe_allow_html=True)

# CICLO FOR CON INDENTAZIONE CORRETTA
for i in range(3):
    d_obj = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d')
    d_label = f"{giorni_ita.get(d_obj.strftime('%A'))} {d_obj.strftime('%d')}"
    
    # CORREZIONE: Moltiplico MJ per 1000 per ottenere KJ
    irraggiamento_kj = int(data_fc['daily']['shortwave_radiation_sum'][i] * 1000)
    
    if irraggiamento_kj < THRESHOLD_LOW:
        irr_class = "irr-low"
    elif irraggiamento_kj > THRESHOLD_HIGH:
        irr_class = "irr-high"
    else:
        irr_class = "irr-mid"
    
    st.markdown(f"""
        <div class="forecast-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 16px; font-weight: 400;">{d_label}</span>
                    <span style="color:#00FFFF; font-size:10px; margin-left:10px; font-weight:300;">{get_santo(d_obj)}</span>
                </div>
                <div style="text-align: right;">
                    <span style="color:#FF3131; font-weight:300; font-size:18px;">Max {data_fc['daily']['temperature_2m_max'][i]}°</span>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px; border-top: 1px solid #111; padding-top: 8px;">
                <div style="text-align:center;"><span style="font-size: 9px; color: #555; text-transform: uppercase; font-weight: bold;">Pioggia</span><span style="font-size: 16px; font-weight: 300; display: block; color:#00FFFF;">{data_fc['daily']['precipitation_sum'][i]}mm</span></div>
                <div style="text-align:center;"><span style="font-size: 9px; color: #555; text-transform: uppercase; font-weight: bold;">Vento Max</span><span style="font-size: 16px; font-weight: 300; display: block; color:#00FF00;">{data_fc['daily']['windspeed_10m_max'][i]}k/h</span></div>
                <div style="text-align:center;"><span style="font-size: 9px; color: #555; text-transform: uppercase; font-weight: bold;">Irragg. Totale</span><span class="stat-val {irr_class}">{irraggiamento_kj} <span style="font-size:9px;">KJ/m²</span></span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- ANALISI STORICA ---
st.write("---")
st.subheader("Analisi Storica 10 GG")
df_hist = pd.DataFrame({
    'Data': pd.to_datetime(data_hist['hourly']['time']),
    'Pioggia': [x * 10 for x in data_hist['hourly']['precipitation']],
    'Vento': data_hist['hourly']['windspeed_10m'],
    'Irragg': [x / 50 for x in data_hist['hourly']['shortwave_radiation']]
}).set_index('Data')
st.line_chart(df_hist, color=["#00FFFF", "#00FF00", "#FFFF00"])

if st.button("Aggiorna"):
    st.cache_data.clear()
    st.rerun()
