import plotly.graph_objects as go
import fastf1.plotting

# Yellow used when a second driver from the same team is selected for comparison
SAME_TEAM_SECONDARY_COLOR = "#FFD700"


def get_comparison_colors(drivers: list, session) -> dict:
    """
    Return {driver: color} for a multi-driver comparison context.
    If two selected drivers belong to the same team, the second one
    gets SAME_TEAM_SECONDARY_COLOR (yellow) so the traces stay distinct.
    """
    seen_teams: dict = {}
    colors: dict = {}
    for drv in drivers:
        try:
            team = fastf1.plotting.get_team_name_by_driver(drv, session)
        except Exception:
            team = None
        if team and team in seen_teams:
            colors[drv] = SAME_TEAM_SECONDARY_COLOR
        else:
            colors[drv] = get_driver_color(drv, session)
            if team:
                seen_teams[team] = drv
    return colors


def get_driver_color(driver, session):
    """
    Recupera il colore ufficiale del pilota dalla sessione FastF1.
    In caso di errore, restituisce il bianco (#FFFFFF).
    """
    try: 
        return fastf1.plotting.get_driver_color(driver, session=session)
    except Exception:
        return '#FFFFFF'

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

        # Global font — monospace everywhere for a sharp technical look
        font=dict(
            family=FONT_MONO,
            color="#e4e4e7",
            size=12,
        ),

        # Chart title — prominent, left-aligned, high contrast
        title=dict(
            text=title,
            font=dict(size=15, family=FONT_MONO, color="#ffffff"),
            y=0.97,
            x=0.01,
            xanchor="left",
            yanchor="top",
            pad=dict(t=6, l=4),
        ),

        # Tighter margins: title is small, no need for 80px top
        margin=dict(l=60, r=24, t=64, b=52),

        # Compact horizontal legend
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_MONO, size=11, color="#d4d4d8"),
            itemsizing="constant",
        ),

        # Tooltip
        hoverlabel=dict(
            bgcolor="#18181b",
            font=dict(family=FONT_MONO, size=12, color="#f4f4f5"),
            bordercolor="#3f3f46",
            namelength=-1,
        ),

        hovermode="x unified",
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
