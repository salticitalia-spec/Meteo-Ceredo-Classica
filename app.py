import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- UTILS & DATI ---
def get_santo(data_obj):
    # Database dinamico per il periodo corrente (Marzo)
    santi = {
        "03-15": "S. Zaccaria",
        "03-16": "S. Eriberto",
        "03-17": "S. Patrizio",
        "03-18": "S. Cirillo",
        "03-19": "S. Giuseppe (Papà)",
        "03-20": "S. Claudia",
        "03-21": "S. Benedetto",
        "03-22": "S. Lea",
        "03-23": "S. Turibio",
        "03-24": "S. Caterina di Svezia",
        "03-25": "Annunciazione"
    }
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

giorni_ita = {
    "Monday": "LUNEDÌ", "Tuesday": "MARTEDÌ", "Wednesday": "MERCOLEDÌ",
    "Thursday": "GIOVEDÌ", "Friday": "VENERDÌ", "Saturday": "SABATO", "Sunday": "DOMENICA"
}

mesi_ita = {
    "March": "MARZO", "April": "APRILE", "May": "MAGGIO"
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
        border-radius: 15px; text-align: center; margin-bottom: 25px;
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
        padding: 15px 10px; border-bottom: 1px solid #222;
    }
    .sector-name { font-size: 18px; font-weight: 900; letter-spacing: 1px; }
    .sector-perc { font-size: 26px; font-weight: 900; }
    .sun-info { font-size: 11px; color: #FFFF00 !important; display: block; font-weight: bold; }
    
    [data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI API ---
@st.cache_data(ttl=3600)
def get_all_data():
    lat, lon = 45.6117, 10.9710
    # Forecast
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration,shortwave_radiation_sum&timezone=Europe%2FRome"
    
    # Historico (ultimi 10 giorni)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=precipitation,windspeed_10m,shortwave_radiation&daily=precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    
    return requests.get(url_fc).json(), requests.get(url_hist).json()

try:
    data_fc, data_hist = get_all_data()
    curr = data_fc['current_weather']
except:
    st.error("Errore nel recupero dati. Riprova tra poco.")
    st.stop()

# --- HEADER ---
st.markdown("""
    <div class="main-banner">
        <div class="banner-content">
            <div class="banner-title">CEREDOLESO PRO</div>
            <div class="banner-subtitle">Precision Drying Analytics</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- MOSTRO BOVINO INDEX (SPOSTATO IN ALTO PER PRIORITÀ) ---
st.header("🐂 MOSTRO BOVINO INDEX")

def get_bovino_score(day_offset, boost):
    # Logica di decadimento pioggia: quella recente conta di più
    rain_hist = data_hist['daily']['precipitation_sum']
    weighted_rain_hist = (rain_hist[-1] * 1.5) + (rain_hist[-2] * 1.2) + sum(rain_hist[:-2])
    
    # Ore di sole totali (storico + previsione)
    h_sun = sum(data_hist['daily']['sunshine_duration']) / 3600
    f_rain = sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    f_sun = sum(data_fc['daily']['sunshine_duration'][:day_offset+1]) / 3600
    
    # Calcolo bias (Asciugatura vs Bagnatura)
    bias = ((h_sun + f_sun) * 0.005 * boost) - ((weighted_rain_hist + f_rain) * 0.15)
    return np.clip(bias, -0.35, 0.15)

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
            
            # Colore dinamico in base alla percentuale
            color = "#00FF00" if min_p > 75 else "#FFFF00" if min_p > 55 else "#FF3131"
            
            st.markdown(f"""
                <div class="bovino-row">
                    <div><span class="sector-name">{nome}</span><span class="sun-info">{sun_time}</span></div>
                    <span class="sector-perc" style="color:{color};">{min_p}-{max_p}%</span>
                </div>
            """, unsafe_allow_html=True)

st.write("---")

# --- ORA ATTUALE ---
st.markdown(f"""
    <div class="current-meteo">
        <div style="margin-bottom: 15px;">
            <div style="font-size: 55px; font-weight: 900; line-height:1;">{curr['temperature']}°</div>
            <span class="label-desc">Temperatura Attuale</span>
        </div>
        <div>
            <div style="font-size: 22px; color: #00FF00 !important; font-weight: 900;">💨 {curr['windspeed']} km/h</div>
            <span class="label-desc">Vento al Settore</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- PREVISIONI 3 GIORNI ---
st.subheader("📅 Meteo Settimanale")
for i in range(3):
    data_obj = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d')
    g_ita = giorni_ita.get(data_obj.strftime('%A'), data_obj.strftime('%A'))
    m_ita = mesi_ita.get(data_obj.strftime('%B'), data_obj.strftime('%B'))
    data_testo = f"{g_ita} {data_obj.strftime('%d')} {m_ita}"
    
    st.markdown(f"""
        <div class="daily-card">
            <span class="daily-title">{data_testo}</span>
            <span class="santo-text">✨ {get_santo(data_obj)}</span>
            <div style="display: flex; justify-content: space-between; margin-top:10px;">
                <div style="text-align:center;"><span class="stat-lab">Max</span><span class="stat-val" style="color:#FF3131;">{data_fc['daily']['temperature_2m_max'][i]}°</span></div>
                <div style="text-align:center;"><span class="stat-lab">Pioggia</span><span class="stat-val" style="color:#00FFFF;">{data_fc['daily']['precipitation_sum'][i]}mm</span></div>
                <div style="text-align:center;"><span class="stat-lab">Vento</span><span class="stat-val" style="color:#00FF00;">{data_fc['daily']['wind_speed_10m_max'][i]}k/h</span></div>
                <div style="text-align:center;"><span class="stat-lab">Sole</span><span class="stat-val" style="color:#FFFF00;">{round(data_fc['daily']['sunshine_duration'][i]/3600, 1)}h</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- GRAFICI ---
with st.expander("📊 VEDI DETTAGLI GRAFICI"):
    st.subheader("Analisi Previsioni (72h)")
    df_fc = pd.DataFrame({
        'Data': pd.to_datetime(data_fc['hourly']['time'][:72]),
        'Pioggia (x10)': [x * 10 for x in data_fc['hourly']['precipitation'][:72]],
        'Irragg. (W/50)': [x / 50 for x in data_fc['hourly']['shortwave_radiation'][:72]],
        'Vento (km/h)': data_fc['hourly']['windspeed_10m'][:72]
    }).set_index('Data')
    st.line_chart(df_fc, color=["#00FFFF", "#FFFF00", "#00FF00"])

    st.subheader("Storico Precipitazioni (10gg)")
    df_hist = pd.DataFrame({
        'Data': pd.to_datetime(data_hist['hourly']['time']),
        'Pioggia (mm)': data_hist['hourly']['precipitation']
    }).set_index('Data')
    st.bar_chart(df_hist, color="#00FFFF")

st.write("---")
if st.button("🔄 AGGIORNA DATI REAL-TIME"):
    st.cache_data.clear()
    st.rerun()
