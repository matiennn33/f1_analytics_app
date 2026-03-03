import streamlit as st

def render():
    st.markdown('<div style="padding: 40px 0;"><h1 style="color: #21C55E;">Documentation</h1><p style="color: #a1a1aa; font-size: 1.2rem;">Guida operativa all\'utilizzo della piattaforma.</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #121212; border: 1px solid #27272a; border-radius: 12px; padding: 30px; margin-bottom: 20px;">
        <h3 style="color: #fff;">1. Inizializzazione Sessione</h3>
        <p style="color: #71717a;">Dalla Home Page, cliccare su "Initialize Uplink" per accedere alla Dashboard. Utilizzare la sidebar laterale per impostare Anno, Gran Premio e Sessione (FP1, Qualifiche, Gara).</p>
        <h3 style="color: #fff; margin-top: 20px;">2. Sincronizzazione</h3>
        <p style="color: #71717a;">Premere "Load Session". Attendere il completamento del download e del parsing dei dati in memoria (Cache attiva per ridurre i tempi nei caricamenti successivi).</p>
        <h3 style="color: #fff; margin-top: 20px;">3. Selezione Piloti</h3>
        <p style="color: #71717a;">Utilizzare il dropdown multiselect per scegliere fino a 2 piloti da comparare nei grafici sovrapposti.</p>
        <h3 style="color: #fff; margin-top: 20px;">4. Navigazione Tabs</h3>
        <p style="color: #71717a;">Spostarsi tra le sezioni "Telemetry Analysis" (giro secco e dinamica), "Race History" (passo gara e passo corretto) e "Strategy & Tyres" (stint e usura) tramite la barra di navigazione superiore.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Torna alla Home"):
        st.session_state['current_route'] = 'landing'
        st.rerun()