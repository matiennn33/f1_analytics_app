import io
import zipfile
import matplotlib.pyplot as plt


def convert_fig_to_bytes(fig, fmt='png', dpi=300):
    """Convert a Matplotlib figure to bytes (PNG or JPG)."""
    buf = io.BytesIO()
    save_args = {
        'format': fmt,
        'dpi': dpi,
        'facecolor': fig.get_facecolor(),
        'bbox_inches': 'tight',
    }
    if fmt in ('jpg', 'jpeg'):
        save_args['facecolor'] = '#030D14'
    fig.savefig(buf, **save_args)
    buf.seek(0)
    return buf


def _render_plotly_fig(fig, fmt: str, width: int = 1400, height: int = 750, scale: float = 1.5) -> bytes:
    """Render a Plotly figure to raw bytes using kaleido."""
    return fig.to_image(format=fmt, width=width, height=height, scale=scale)


def build_charts_pdf(figs: list, filenames: list = None) -> bytes:
    """
    Render a list of Plotly figures as PNG pages and bundle them into a
    multi-page PDF using Pillow.  Returns raw PDF bytes.
    """
    from PIL import Image
    images = []
    for i, fig in enumerate(figs):
        try:
            png = _render_plotly_fig(fig, 'png')
            img = Image.open(io.BytesIO(png)).convert('RGB')
            images.append(img)
        except Exception:
            pass  # Skip figures that fail to render

    if not images:
        return b""

    pdf_buf = io.BytesIO()
    images[0].save(
        pdf_buf,
        format='PDF',
        save_all=True,
        append_images=images[1:],
        resolution=150,
    )
    pdf_buf.seek(0)
    return pdf_buf.read()


def build_charts_zip(figs: list, filenames: list = None, fmt: str = 'png') -> bytes:
    """
    Render each Plotly figure to the given format (png/jpg/svg) and pack them
    into a ZIP archive.  Returns raw ZIP bytes.
    """
    if filenames is None:
        filenames = [f"chart_{i+1}" for i in range(len(figs))]

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, fig in zip(filenames, figs):
            try:
                img_fmt = 'jpeg' if fmt == 'jpg' else fmt
                data = _render_plotly_fig(fig, img_fmt)
                ext = 'jpg' if fmt == 'jpg' else fmt
                zf.writestr(f"{name}.{ext}", data)
            except Exception:
                pass
    zip_buf.seek(0)
    return zip_buf.read()


def build_laps_csv(laps) -> bytes:
    """Return the laps DataFrame as UTF-8 CSV bytes."""
    cols = [c for c in [
        'Driver', 'Team', 'LapNumber', 'LapTime', 'Sector1Time', 'Sector2Time',
        'Sector3Time', 'Compound', 'TyreLife', 'Stint', 'SpeedI1', 'SpeedI2',
        'SpeedFL', 'SpeedST', 'IsPersonalBest', 'TrackStatus',
    ] if c in laps.columns]
    return laps[cols].to_csv(index=False).encode('utf-8')
