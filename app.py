import streamlit as st  # <--- QUESTA RIGA DEVE ESSERE LA PRIMA
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- PARAMETRI ---
THRESHOLD_LOW, THRESHOLD_HIGH, CORR_VAJO = 6500, 12000, 0.8

# --- CSS (CON HEADER +20%) ---
st.markdown('''
<style>
    .stApp { background-color: #000; }
    .main-banner {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("icona.png");
        background-size: cover; background-position: center;
        padding: 18px 5px; border-radius: 12px; border: 1px solid #1a1a1a;
        text-align: center; margin-bottom: 25px;
        display: flex; justify-content: center; align-items: center;
    }
    .title-wrapper { display: flex; flex-direction: column; align-items: flex-end; }
    
    /* Ceredoleso ~14.5px */
    .title-ceredoleso { 
        color: #0FF !important; 
        font-weight: 100 !important; 
        font-size: 14.5px; 
        letter-spacing: 5px; 
        margin: 0; 
        text-transform: uppercase; 
        line-height: 1; 
        font-family: sans-serif;
    }
    
    /* PRO ~11px */
    .title-pro { 
        color: #0FF !important; 
        font-weight: 100 !important; 
        font-size: 11px; 
        letter-spacing: 3px; 
        margin-top: 3px; 
        text-transform: uppercase; 
        opacity: 0.8; 
        font-family: sans-serif;
    }
    
    /* ... resto del CSS ... */
</style>
''', unsafe_allow_html=True)

# ... resto del codice ...
