"""
Centralized configuration for F1 Telemetry Analytics App
"""

# === UI / STYLING ===
COLORS = {
    "bg_card": "#121212",
    "border": "#27272a",
    "text_muted": "#a1a1aa",
    "text_white": "#ffffff",
    "bg_dark": "#0a0a0a",
    "accent_green": "#21C55E",
    "accent_red": "#ef4444",
}

FONTS = {
    "mono": "'Geist Mono', monospace",
    "sans": "'Space Grotesk', sans-serif",
}

# === TELEMETRY ANALYSIS ===
TELEMETRY_CONFIG = {
    "smoothing_window": 10,
    "num_microsectors": 40,  # Reduced from 80 for performance
    "g_force_clip_threshold": 5.5,  # G-force clipping threshold
    "corner_penalty_threshold": 2.2,  # G-force for corner detection
}

# === ERS MODEL (2026) ===
ERS_CONFIG = {
    "capacity_kj": 4400,  # Total capacity in kJ
    "efficiency": 0.97,  # Efficiency multiplier
    "high_speed_threshold": 355,  # Speed threshold for recovery limit
    "low_speed_threshold": 290,  # Low speed recovery threshold
    "max_recovery_kw": 120,  # Max recovery power (kW)
    "deployment_kw": 350,  # Max deployment power (kW)
}

# === BRAKE PRESSURE ESTIMATION ===
BRAKE_CONFIG = {
    "drag_coefficient": 0.0008,
    "dt_default": 0.001,  # Default time delta if none found
}

# === ADVANCED METRICS ===
METRICS_CONFIG = {
    "full_throttle_weight": 0.7,
    "coasting_weight": 0.3,
    "throttle_full_threshold": 99,
    "throttle_partial_threshold": 95,
    "corner_speed_low": 125,  # km/h
    "corner_speed_high": 210,  # km/h
    "speed_vmax_proximity": 0.98,  # 98% of max speed
}

# === TEAM LOGOS MAPPING ===
TEAM_LOGOS = {
    "MCLAREN": "MCLAREN.png",
    "RED BULL RACING": "RED BULL RACING.png",
    "FERRARI": "FERRARI.png",
    "MERCEDES": "MERCEDES.png",
    "RACING BULLS": "RB.png",
    "AUDI": "AUDI.png",
    "ALPINE": "ALPINE.png",
    "ASTON MARTIN": "ASTON MARTIN.png",
    "HAAS F1 TEAM": "HAAS.png",
    "CADILLAC": "CADILLAC.png",
    "KICK SAUBER": "KICK SAUBER.png",
    "WILLIAMS": "WILLIAMS.png",
}

LOGO_PATH = "logos"
LOGO_DEFAULT_ICON = "fa-car"

# === SESSION CONFIG ===
SESSION_CONFIG = {
    "max_drivers_comparison": 4,
    "default_drivers_to_show": 2,
    "cache_expiry_hours": 24,
}

# === ERROR MESSAGES (USER-FRIENDLY) ===
ERROR_MESSAGES = {
    "api_offline": "🔴 API offline. Verifica la connessione a internet.",
    "data_load_failed": "❌ Impossibile caricare i dati telemetrici. Riprova tra un momento.",
    "session_not_found": "⚠️ Sessione non trovata. Seleziona un anno/GP/sessione validi.",
    "invalid_drivers": "⚠️ Seleziona almeno 1 pilota, massimo 4.",
    "no_telemetry_data": "📊 Dati telemetrici non disponibili per questa sessione.",
    "missing_columns": "⚠️ Colonne telemetriche mancanti. Alcuni grafici potrebbero essere vuoti.",
}

# === YEAR RANGE ===
F1_YEAR_RANGE = range(2026, 2018, -1)
