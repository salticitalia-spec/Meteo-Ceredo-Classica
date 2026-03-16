import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- DATABASE SANTI DINAMICO ---
def get_santo(data_obj):
    santi = {
        "03-16": "S. Eriberto",
        "03-17": "S. Patrizio",
        "03-18": "S. Cirillo",
        "03-19": "S. Giuseppe (Festa del Papà)",
        "03-20": "S. Claudia",
        "03-21": "S. Benedetto",
        "03-22": "S. Lea",
        "03-23": "S. Turibio",
        "03-24": "S. Caterina di Svezia",
        "03-25": "Annunciazione del Signore"
    }
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

# --- DIZIONARI TRADUZIONE ---
giorni_ita = {
    "Monday": "LUNEDÌ", "Tuesday": "MARTEDÌ", "Wednesday": "MERCOLEDÌ",
    "Thursday": "GIOVEDÌ", "Friday": "VENERDÌ", "Saturday": "SABATO", "Sunday": "DOMENICA"
}

mesi_ita = {
    "January": "GENNAIO", "February": "FEBBRAIO", "March": "MARZO",
    "April": "APRILE", "May": "MAGGIO", "June": "GIUGNO",
    "July": "LUGLIO", "August": "AGOSTO", "September": "SETTEMBRE",
    "October": "OTTOBRE", "November": "NOVEMBRE", "December": "DICEMBRE"
}

# --- STILE CSS HIGH-CONTRAST ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; }
    
    .main-banner {
        background: linear-gradient(90deg, #111 0%, #00FFFF 50%, #111 100%);
        padding: 2px; border-radius: 15px; margin-bottom: 20px;
    }
    .banner-content {
        background-color: #000; padding: 20px; border-radius: 13px; text-align: center;
    }
    .banner-title { font-size: 32px; font-weight: 900; letter-spacing: 2px; margin: 0; }
    .banner-subtitle {
        font-size: 12px; color: #00FFFF !important; text-transform: uppercase;
        letter-spacing: 4px; margin-top: 5px;
    }

    .current-meteo {
        background-color: #000000; border: 3px solid #FFFFFF; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    
    .label-desc {
        font-size: 10px; color: #AAA !important; text-transform: uppercase;
        letter-spacing: 2px; font-weight: bold; display: block; margin-top: 5px;
    }
    
    .daily-card {
        background-color: #0a0a0a; border: 1px solid #333; padding: 15px;
        border-radius: 12px; margin-bottom: 8px;
    }
    .daily-title { font-size: 19px; font-weight: 900; color: #FFFFFF !important; margin: 0; }
    .santo-text {
        font-size: 10px; color: #00FFFF !important; text-transform: uppercase;
        letter-spacing: 3px; display: block; margin-bottom: 12px; font-weight: bold;
    }
    
    .stat-val { font-size: 20px; font-weight: 900; display: block; }
    .stat-lab { font-size: 10px; color: #AAA; text-transform: uppercase; font-weight: bold; }

    .bovino-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 8px; border-bottom: 1px solid #222;
    }
    .sector-name { font-size: 17px; font-weight: 900; }
    .sector-perc { font-size: 24px; font-weight: 900; }
    .sun-info { font-size: 11px; color: #FFFF00 !important; display: block; font-weight: bold; }
    
    [data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI API ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration,shortwave_radiation_sum&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=precipitation,windspeed_10m,shortwave_radiation&daily=precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

try:
    data_fc, data_hist = get_all_data()
    curr = data_fc['current_weather']
except:
    st.error("Errore API. Controlla la connessione.")
    st.stop()

# --- BANNER ---
st.markdown("""
    <div class="main-banner">
        <div class="banner-content">
            <div class="banner-title">CEREDOLESO PRO</div>
            <div class="banner-subtitle">Precision Drying Analytics</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 1. ORA ATTUALE CON DESCRIZIONI ---
st.markdown(f"""
    <div class="current-meteo">
        <div style="margin-bottom: 15px;">
            <div style="font-size: 50px; font-weight: 900; line-height:1;">{curr['temperature']}°</div>
            <span class="label-desc">Temperatura Attuale</span>
        </div>
        <div>
            <div style="font-size: 20px; color: #00FF00 !important; font-weight: 900;">💨 {curr['windspeed']} km/h</div>
            <span class="label-desc">Velocità Vento</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 2. PREVISIONI 3 GIORNI ---
st.subheader("📅 Previsioni Settimanali")
for i in range(3):
    data_obj = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d')
    g_ita = giorni_ita[data_obj.strftime('%A')]
    m_ita = mesi_ita[data_obj.strftime('%B')]
    data_testo = f"{g_ita} {data_obj.strftime('%d')} {m_ita}"
    santo = get_santo(data_obj)
    
    st.markdown(f"""
        <div class="daily-card">
            <span class="daily-title">{data_testo}</span>
            <span class="santo-text">{santo}</span>
            <div style="display: flex; justify-content: space-between;">
                <div style="text-align:center;"><span class="stat-lab">Max</span><span class="stat-val" style="color:#FF3131;">{data_fc['daily']['temperature_2m_max'][i]}°</span></div>
                <div style="text-align:center;"><span class="stat-lab">Pioggia</span><span class="stat-val" style="color:#00FFFF;">{data_fc['daily']['precipitation_sum'][i]}mm</span></div>
                <div style="text-align:center;"><span class="stat-lab">Vento</span><span class="stat-val" style="color:#00FF00;">{data_fc['daily']['wind_speed_10m_max'][i]}k/h</span></div>
                <div style="text-align:center;"><span class="stat-lab">Irragg.</span><span class="stat-val" style="color:#FFFF00;">{round(data_fc['daily']['shortwave_radiation_sum'][i]/1000,2)}MJ</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 3. ANALISI COMBINATA PREVISIONI (72h) ---
st.subheader("📊 Analisi Combinata (Previsioni 72h)")
st.markdown("<b style='color:#00FFFF;'>■ Pioggia (mm x10)</b> | <b style='color:#FFFF00;'>■ Irragg. (W/50)</b> | <b style='color:#00FF00;'>■ Vento (km/h)</b>", unsafe_allow_html=True)
df_fc = pd.DataFrame({
    'Data': pd.to_datetime(data_fc['hourly']['time'][:72]),
    'Pioggia (x10)': [x * 10 for x in data_fc['hourly']['precipitation'][:72]],
    'Irragg. (W/50)': [x / 50 for x in data_fc['hourly']['shortwave_radiation'][:72]],
    'Vento (km/h)': data_fc['hourly']['windspeed_10m'][:72]
}).set_index('Data')
st.line_chart(df_fc, color=["#00FFFF", "#FFFF00", "#00FF00"])

st.write("---")

# --- 4. ANALISI STORICA (10 GIORNI) ---
st.subheader("📊 Analisi Storica (Ultimi 10 Giorni)")
st.markdown("<b style='color:#00FFFF;'>■ Pioggia (mm x10)</b> | <b style='color:#FFFF00;'>■ Irragg. (W/50)</b> | <b style='color:#00FF00;'>■ Vento (km/h)</b>", unsafe_allow_html=True)
df_hist = pd.DataFrame({
    'Data': pd.to_datetime(data_hist['hourly']['time']),
    'Pioggia (x10)': [x * 10 for x in data_hist['hourly']['precipitation']],
    'Irragg. (W/50)': [x / 50 for x in data_hist['hourly']['shortwave_radiation']],
    'Vento (km/h)': data_hist['hourly']['windspeed_10m']
}).set_index('Data')
st.line_chart(df_hist, color=["#00FFFF", "#FFFF00", "#00FF00"])

st.write("---")

# --- 5. MOSTRO BOVINO INDEX (IN FONDO) ---
st.header("🐂 MOSTRO BOVINO INDEX")
def get_bovino_score(day_offset, boost):
    h_rain = sum(data_hist['daily']['precipitation_sum'])
    h_sun = sum(data_hist['daily']['sunshine_duration']) / 3600
    f_rain = sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    f_sun = sum(data_fc['daily']['sunshine_duration'][:day_offset+1]) / 3600
    bias = ((h_sun + f_sun) * 0.005 * boost) - ((h_rain + f_rain) * 0.14)
    return np.clip(bias, -0.30, 0.15)

settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.40, "Sole: 09:30 → 13:30"),
    ("🎋 SUPERCANNA", 70, 5, 1.28, "Sole: 10:30 → 15:00"),
    ("🧠 CEREDOLESO", 77, 3, 1.10, "Sole: 12:00 → 16:00"),
    ("🏺 OSTRAMANDRA", 60, 6, 0.80, "Sole: 13:30 → 16:30")
]

tabs = st.tabs(["OGGI", "DOMANI", "DOPODOMANI"])
for day in range(3):
    with tabs[day]:
        for nome, base, toll, boost, sun_time in settori:
            bias = get_bovino_score(day, boost)
            prob = int(base + (bias * 100))
            min_p, max_p = np.clip([prob-toll, prob+toll], 0, 100)
            color = "#00FF00" if min_p > 70 else "#FFFF00" if min_p > 50 else "#FF3131"
            st.markdown(f"""
                <div class="bovino-row">
                    <div><span class="sector-name">{nome}</span><span class="sun-info">{sun_time}</span></div>
                    <span class="sector-perc" style="color:{color};">{min_p}-{max_p}%</span>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
if st.button("🔄 AGGIORNA DATI"):
    st.rerun()
