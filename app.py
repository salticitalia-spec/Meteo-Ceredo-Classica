# --- CSS AGGIORNATO (HEADER +20%) ---
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
    
    /* Ceredoleso aumentato di un ulteriore 20% (~14.5px) */
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
    
    /* PRO aumentato proporzionalmente (~11px) */
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
    
    .info-card {
        background-color: #0c0c0c; border: 1px solid #222;
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 15px;
    }
    .date-text { font-size: 18px; font-weight: bold; color: #fff; }
    .t-main { font-size: 45px; font-weight: bold; color: #fff; margin: 5px 0; }
    .t-perc { font-size: 14px; color: #FF0; margin-bottom: 10px; font-weight: 300; }
    .rain-tag { color: #F31; font-size: 11px; font-weight: bold; border: 1px solid #F31; padding: 4px 10px; border-radius: 5px; display: inline-block; margin: 10px 0; }
    .val-box { display: flex; justify-content: center; gap: 15px; font-size: 17px; margin-top: 10px; }
    [data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color:#020202; }
</style>
''', unsafe_allow_html=True)

# --- BLOCCO HEADER ---
st.markdown(f'''
<div class="main-banner">
    <div class="title-wrapper">
        <div class="title-ceredoleso">Ceredoleso</div>
        <div class="title-pro">PRO</div>
    </div>
</div>
''', unsafe_allow_html=True)
