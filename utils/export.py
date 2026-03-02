import io
import matplotlib.pyplot as plt

def convert_fig_to_bytes(fig, fmt='png', dpi=300):
    """
    Converte una figura Matplotlib in un buffer di bytes per il download.
    Supporta 'png' o 'jpg'.
    """
    buf = io.BytesIO()
    
    # Imposta parametri di salvataggio
    save_args = {
        'format': fmt,
        'dpi': dpi,
        'facecolor': fig.get_facecolor(),
        'bbox_inches': 'tight'
    }
    
    # Se è jpg (jpeg), non supporta la trasparenza, quindi impostiamo lo sfondo
    if fmt == 'jpg' or fmt == 'jpeg':
        save_args['facecolor'] = '#030D14' # Colore di sfondo scuro dell'app
    
    fig.savefig(buf, **save_args)
    buf.seek(0)
    return buf