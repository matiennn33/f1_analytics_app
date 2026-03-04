import streamlit as st

TRANSLATIONS: dict[str, dict[str, str]] = {
    "EN": {
        # Navbar
        "nav_features":       "Features",
        "nav_architecture":   "Architecture",
        "nav_documentation":  "Documentation",
        "nav_home":           "← Home",
        # Hero badge
        "badge": "High-Performance Analytics",
        # Hero headline
        "hero_line1": "Dominating",
        "hero_line2": "Telemetry Data",
        # Hero subline
        "hero_desc": (
            "Built for absolute optimisation. Analyse the metrics, decode the vehicle's limits "
            "and transform raw data into a clear competitive edge."
        ),
        # CTA button
        "cta_btn": "INITIALIZE UPLINK",
        # Stats
        "stat_1_label": "Grands Prix",
        "stat_2_label": "Data Points / Lap",
        "stat_3_label": "Analysis Modules",
        "stat_4_label": "Render Latency",
        # Bento
        "bento_1_title": "Vehicle Dynamics",
        "bento_1_desc":  "Millimetre-level analysis of pedal inputs, aero-mechanical balance and downforce distribution curves.",
        "bento_2_title": "Thermal Degradation",
        "bento_2_desc":  "Predictive tyre wear models, cliff detection and statistical regression of fuel-corrected race pace.",
        "bento_3_title": "Spatial Domain",
        "bento_3_desc":  "Micro-sector mapping to identify chronic performance losses and braking/traction zones.",
        "bento_4_title": "Strategy Optimizer",
        "bento_4_desc":  "Stint analysis, undercut window detection and multi-driver pit-stop sequence comparison on real pace.",
        "bento_5_title": "Multi-Session Diff",
        "bento_5_desc":  "Cross-session comparison of qualifying, race and practice to isolate setup evolution across the weekend.",
        "bento_6_title": "FastF1 Powered",
        "bento_6_desc":  "Official FIA LiveTiming stream data with intelligent local cache. Zero latency on subsequent loads.",
        # Mockup
        "mockup_stream": "LIVE_TELEMETRY_STREAM",
        "mockup_uplink_label": "Uplink Status",
        "mockup_uplink_status": "ACTIVE",
        # Footer
        "footer_by":       "Designed & built by",
        "footer_platform": "LC Telemetry Platform",
    },
    "IT": {
        # Navbar
        "nav_features":       "Funzionalità",
        "nav_architecture":   "Architettura",
        "nav_documentation":  "Documentazione",
        "nav_home":           "← Home",

        # Hero badge
        "badge": "Analisi ad Alte Prestazioni",

        # Hero headline
        "hero_line1": "Dominio dei",
        "hero_line2": "Dati Telemetrici",

        # Hero subline
        "hero_desc": (
            "Progettato per l'ottimizzazione assoluta. Analizza le metriche, interpreta i limiti "
            "del veicolo e trasforma i dati grezzi in un vantaggio competitivo concreto."
        ),

        # CTA button
        "cta_btn": "INIZIALIZZA COLLEGAMENTO",

        # Stats
        "stat_1_label": "Gran Premi",
        "stat_2_label": "Punti Dati / Giro",
        "stat_3_label": "Moduli di Analisi",
        "stat_4_label": "Latenza di Rendering",

        # Bento
        "bento_1_title": "Dinamica del Veicolo",
        "bento_1_desc":  "Analisi al millimetro degli input su pedale, del bilanciamento aerodinamico-meccanico e delle curve di distribuzione del carico aerodinamico.",

        "bento_2_title": "Degrado Termico",
        "bento_2_desc":  "Modelli predittivi di usura degli pneumatici, rilevamento del 'cliff' prestazionale e regressione statistica del passo gara corretto per il carburante.",

        "bento_3_title": "Dominio Spaziale",
        "bento_3_desc":  "Mappatura micro-settoriale per individuare perdite croniche di prestazione e analizzare zone di frenata e trazione.",

        "bento_4_title": "Ottimizzatore Strategico",
        "bento_4_desc":  "Analisi degli stint, identificazione delle finestre di undercut e confronto delle sequenze di pit-stop multi-pilota basato sul passo reale.",

        "bento_5_title": "Confronto Multi-Sessione",
        "bento_5_desc":  "Comparazione tra qualifiche, gara e prove libere per isolare l'evoluzione dell'assetto durante il weekend di gara.",

        "bento_6_title": "Powered by FastF1",
        "bento_6_desc":  "Dati ufficiali provenienti dal flusso FIA Live Timing con cache locale intelligente. Nessuna latenza nei caricamenti successivi.",

        # Mockup
        "mockup_stream": "FLUSSO_TELEMETRIA_LIVE",
        "mockup_uplink_label": "Stato Collegamento",
        "mockup_uplink_status": "ATTIVO",

        # Footer
        "footer_by":       "Progettato e sviluppato da",
        "footer_platform": "Piattaforma LC Telemetria",
    },
}


def t(key: str) -> str:
    """Return the translation for *key* in the user's currently selected language."""
    lang = st.session_state.get("lang", "EN")
    return TRANSLATIONS.get(lang, TRANSLATIONS["EN"]).get(key, key)
