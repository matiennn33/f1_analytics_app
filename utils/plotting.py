import plotly.graph_objects as go
import fastf1.plotting

SAME_TEAM_SECOND_DRIVER_COLOR = '#FFBF00'

def get_driver_color(driver, session):
    """
    Recupera il colore ufficiale del pilota dalla sessione FastF1.
    In caso di errore, restituisce il bianco (#FFFFFF).
    """
    try: 
        return fastf1.plotting.get_driver_color(driver, session=session)
    except Exception:
        return '#FFFFFF'

def get_driver_colors(drivers, session):
    """
    Restituisce un dizionario {driver: color} per la lista di piloti.
    Se due piloti dello stesso team vengono comparati, il secondo pilota
    ottiene il colore #FFBF00.
    """
    colors = {}
    seen_teams = {}
    for driver in drivers:
        try:
            team = fastf1.plotting.get_team_name_by_driver(driver, session=session)
        except Exception:
            team = None
        if team and team in seen_teams:
            colors[driver] = SAME_TEAM_SECOND_DRIVER_COLOR
        else:
            colors[driver] = get_driver_color(driver, session)
            if team:
                seen_teams[team] = driver
    return colors

def get_team_color(team, session):
    """
    Recupera il colore ufficiale del team.
    In caso di errore, restituisce un grigio neutro (#808080).
    """
    try: 
        return fastf1.plotting.get_team_color(team, session=session)
    except Exception:
        return '#808080'

def apply_plotly_style(fig, title=""):
    """
    Applica il design system 'Pro Analytics' a un grafico Plotly.
    Configura i font Geist, le trasparenze e il layout della legenda.
    """
    # Nomi delle famiglie di font come definite in app.py
    FONT_SANS = "Space Grotesk, sans-serif"
    FONT_MONO = "Geist Mono, monospace"

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        
        # Configurazione Font Globale
        font=dict(
            family=FONT_SANS, 
            color="#ededed", 
            size=12
        ),
        
        # Titolo del Grafico
        title=dict(
            text=title, 
            font=dict(size=20, family=FONT_SANS, weight=700),
            y=0.96,
            x=0.01,
            xanchor='left'
        ),
        
        # Margini ottimizzati per lo scroll della pagina
        margin=dict(l=60, r=20, t=80, b=60),
        
        # Legenda orizzontale compatta (Geist Mono per un look tecnico)
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1, 
            bgcolor='rgba(0,0,0,0)',
            font=dict(family=FONT_MONO, size=11)
        ),
        
        # Hover Label personalizzato (Tooltip)
        hoverlabel=dict(
            bgcolor="#121212",
            font=dict(family=FONT_MONO, size=13),
            bordercolor="#27272a"
        ),
        
        # Modalità di interazione
        hovermode='x unified'
    )

    # Configurazione Asse X (Geist Mono per i numeri/distanza)
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False, 
        showline=False, # Nessuna riga pesante in basso
        tickfont=dict(family=FONT_MONO),
        title_font=dict(family=FONT_SANS, size=11, color="#71717a")
    )
    
    # Configurazione Asse Y (Griglia visibile Geist Mono)
    fig.update_yaxes(
        showgrid=True, 
        gridcolor="rgba(255, 255, 255, 0.03)", # Griglia glassmorphism
        zeroline=False, 
        showline=False, # Nessuna riga laterale 
        tickfont=dict(family=FONT_MONO),
        title_font=dict(family=FONT_SANS, size=11, color="#71717a")
    )
    
    return fig
