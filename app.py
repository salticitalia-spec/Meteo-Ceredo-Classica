import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Meteo Ceredo", page_icon="🧗")

st.title("🧗 Meteo Ceredo Classica")

lat, lon = 45.6117, 10.9710

# 1. FUNZIONE METEO ATTUALE E PREVISIONI
def get_forecast():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability&timezone=Europe%2FRome"
    res = requests.get(url).json()
    return res

# 2. FUNZIONE STORICO PIOGGIA
def get_rain_history():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=Europe%2FRome"
    return requests.get(url).json()['daily']

# ESECUZIONE
data = get_forecast()
curr = data['current_weather']

# VISUALIZZAZIONE ATTUALE
col1, col2 = st.columns(2)
col1.metric("Temp. Attuale", f"{curr['temperature']} °C")
col2.metric("Vento", f"{curr['windspeed']} km/h")

# 3. NUOVA SEZIONE: PREVISIONI PROSSIME ORE
st.write("---")
st.subheader("⏳ Previsioni Prossime Ore")

# Estraiamo i dati orari
hourly_time = data['hourly']['time']
hourly_temp = data['hourly']['temperature_2m']
hourly_rain = data['hourly']['precipitation_probability']

# Troviamo l'indice dell'ora attuale
now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
try:
    idx = hourly_time.index(now_str)
except:
    idx = 0

# Mostriamo le prossime 4 ore in colonne
cols = st.columns(4)
for i in range(4):
    future_idx = idx + (i + 1)
    ora = hourly_time[future_idx][-5:]
    temp = hourly_temp[future_idx]
    prob = hourly_rain[future_idx]
    cols[i].markdown(f"**{ora}**\n\n{temp}°C\n\n💧{prob}%")

# STORICO PIOGGIA (quello che avevi già)
st.write("---")
st.subheader("💧 Pioggia ultimi 5 giorni (mm)")
rain_history = get_rain_history()
df_rain = pd.DataFrame({
    'Giorno': [d[-5:] for d in rain_history['time']], 
    'Pioggia (mm)': rain_history['precipitation_sum']
})
st.bar_chart(data=df_rain, x='Giorno', y='Pioggia (mm)')

if st.button("AGGIORNA"):
    st.rerun()
