import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Meteo Ceredo", page_icon="🧗")

st.title("🧗 Meteo Ceredo Classica")

lat, lon = 45.6117, 10.9710

def get_current_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    return requests.get(url).json()['current_weather']

def get_rain_history():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=Europe%2FRome"
    return requests.get(url).json()['daily']

curr = get_current_weather()
st.metric("Temperatura Attuale", f"{curr['temperature']} °C")

st.write("---")
st.subheader("💧 Pioggia ultimi 5 giorni (mm)")
rain_data = get_rain_history()
df = pd.DataFrame({'Giorno': [d[-5:] for d in rain_data['time']], 'Pioggia (mm)': rain_data['precipitation_sum']})
st.bar_chart(data=df, x='Giorno', y='Pioggia (mm)')

if st.button("AGGIORNA"):
    st.rerun()
