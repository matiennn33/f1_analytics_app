import pandas as pd
import numpy as np

def fmt_time(seconds):
    """Converte secondi (float) in stringa MM:SS.mmm"""
    if seconds is None or pd.isna(seconds):
        return "N/A"
    
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

def fmt_delta(seconds):
    """Converte delta secondi in stringa +S.mmm"""
    if seconds is None or pd.isna(seconds):
        return "-"
    sign = "+" if seconds > 0 else ""
    return f"{sign}{seconds:.3f}s"