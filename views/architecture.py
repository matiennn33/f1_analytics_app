import streamlit as st

def render():
    st.markdown('<div style="padding: 40px 0;"><h1 style="color: #21C55E;">System Architecture</h1><p style="color: #a1a1aa; font-size: 1.2rem;">Infrastruttura tecnica e flussi dati.</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #121212; border: 1px solid #27272a; border-radius: 12px; padding: 30px; margin-bottom: 20px;">
        <h3 style="color: #fff;">Stack Tecnologico</h3>
        <ul style="color: #71717a; line-height: 1.8;">
            <li><strong style="color:#21C55E;">Frontend & Routing:</strong> Streamlit (Multipage state-based rendering).</li>
            <li><strong style="color:#21C55E;">Data Fetching:</strong> Libreria FastF1 API con caching locale per minimizzare la latenza.</li>
            <li><strong style="color:#21C55E;">Data Manipulation:</strong> Pandas e NumPy per elaborazione matriciale e regressioni lineari.</li>
            <li><strong style="color:#21C55E;">Visualizzazione:</strong> Plotly Graph Objects / Matplotlib per grafici interattivi.</li>
        </ul>
        <hr style="border-color: #27272a; margin: 20px 0;">
        <h3 style="color: #fff;">Flusso Dati</h3>
        <p style="color: #71717a;">
            L'Uplink API interroga i server Ergast e F1 Live Timing. I dati grezzi vengono decodificati, convertiti in DataFrame, allineati spazialmente per interpolazione (distanza) e passati ai moduli di rendering isolati (telemetry.py, race.py, strategy.py).
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Torna alla Home"):
        st.session_state['current_route'] = 'landing'
        st.rerun()