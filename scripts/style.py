"""Shared figure style: Times (TeX Gyre Termes) text, STIX math, TrueType embedding.

matplotlib cannot embed the CFF-flavoured TeX Gyre .otf files as Type 42, so the
first call converts them to TrueType in scripts/fonts/ (git-ignored).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
FONT_DIR = HERE / "fonts"
GYRE = Path("/usr/share/texmf/fonts/opentype/public/tex-gyre")

# column widths of the CVPR template, in inches
COL = 3.25
FULL = 6.875

# One system for every figure (see REVISION_NOTES.md):
#  models     released grey, class-wide purple, footprint green;
#             seed 1 = filled marker / solid line, seed 2 = hollow / dashed
#  edit types source light grey, sham blue, fault vermilion, vacancy ochre
#  overlays   target cyan (solid recipient, dashed vacated), queued orange;
#             reserved: never used for data
#  score maps greyscale (black = 0, white = 1)
C = {
    "released": "#4d4d4d",
    "classwide": "#7b5ea7",
    "footprint": "#1b8a6b",
    "upstream": "#b07aa1",
    "source": "#a0a0a0",
    "sham": "#3d7dc4",
    "fault": "#d55e00",
    "vacancy": "#b58a1a",
    "target": "#00b4d8",
    "queued": "#f28e2b",
    "train": "#1b8a6b",      # "what we change"
    "calib": "#3d5a99",      # "fixed on development data"
    "alarm": "#c0392b",
    "grey": "#555555",
    "light": "#d9d9d9",
    "pin": "#e8c547",
}
SCORE_CMAP = "gray"

def _otf_to_ttf(src, dst):
    from fontTools.ttLib import TTFont
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    f = TTFont(src)
    gs = f.getGlyphSet()
    glyf = {}
    for name in f.getGlyphOrder():
        pen = TTGlyphPen(gs)
        gs[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
        glyf[name] = pen.glyph()
    from fontTools.ttLib import newTable
    t = newTable("glyf"); t.glyphs = glyf; t.glyphOrder = f.getGlyphOrder()
    f["glyf"] = t
    f["loca"] = newTable("loca")
    f["maxp"].tableVersion = 0x00010000
    for k in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs",
              "maxInstructionDefs", "maxStackElements", "maxSizeOfInstructions",
              "maxComponentElements", "maxPoints", "maxContours",
              "maxCompositePoints", "maxCompositeContours", "maxComponentDepth"):
        setattr(f["maxp"], k, 0 if k != "maxZones" else 1)
    f["head"].glyphDataFormat = 0
    del f["CFF "]
    if "VORG" in f:
        del f["VORG"]
    f["post"].formatType = 2.0
    f["post"].extraNames = []
    f["post"].mapping = {}
    f["post"].glyphOrder = f.getGlyphOrder()
    f.sfntVersion = "\x00\x01\x00\x00"
    f.save(dst)


def setup():
    FONT_DIR.mkdir(exist_ok=True)
    for st in ("regular", "bold", "italic", "bolditalic"):
        dst = FONT_DIR / f"texgyretermes-{st}.ttf"
        if not dst.exists():
            _otf_to_ttf(GYRE / f"texgyretermes-{st}.otf", dst)
        font_manager.fontManager.addfont(str(dst))
    # drop the system CFF copies so matplotlib picks the TrueType ones
    font_manager.fontManager.ttflist = [
        f for f in font_manager.fontManager.ttflist
        if not (f.name == "TeX Gyre Termes" and f.fname.endswith(".otf"))]
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "TeX Gyre Termes", "Times", "Nimbus Roman"],
        "mathtext.fontset": "stix",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "mathtext.default": "it",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "lines.linewidth": 1.2,
        "savefig.dpi": 400,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


def errbar(ax, x, y, lo, hi, color, horizontal=False, ms=4.5, marker="o", hollow=False, **kw):
    """Point with a thick, capped 95% interval; hollow=True for seed 2 / flagged rows."""
    mfc = "white" if hollow else color
    if horizontal:
        ax.errorbar(y, x, xerr=[[y - lo], [hi - y]], fmt=marker, color=color, ms=ms, mfc=mfc,
                    elinewidth=1.4, capsize=3, capthick=1.4, **kw)
    else:
        ax.errorbar(x, y, yerr=[[y - lo], [hi - y]], fmt=marker, color=color, ms=ms, mfc=mfc,
                    elinewidth=1.4, capsize=3, capthick=1.4, **kw)


def sprite(name):
    """RGBA sprite cut from the BioRender icon sheet (near-white made transparent)."""
    import numpy as np
    from PIL import Image
    boxes = {"pin": (355, 40, 668, 158)}
    im = Image.open(FIG / "biorender" / "sprites.jpg").convert("RGB").crop(boxes[name])
    a = np.asarray(im).astype(float)
    alpha = np.clip((250 - a.min(axis=2)) * 8, 0, 255).astype(np.uint8)
    return np.dstack([a.astype(np.uint8), alpha])


def score_map_values(asset, kind):
    """Scores recovered from a draft raster by inverting its colour map (median error ~1 grey level).

    kind = "draft" uses the draft's colour bar (guidance_maps_2), "magma" matplotlib's magma.
    """
    import numpy as np
    from PIL import Image
    from matplotlib import colormaps
    im = np.asarray(Image.open(FIG / "assets" / f"{asset}.png").convert("RGB")).astype(float)
    if kind == "draft":
        lut = np.asarray(Image.open(FIG / "assets" / "guidance_maps_2.png").convert("RGB"))[5] / 255.0
    else:
        lut = colormaps["magma"](np.linspace(0, 1, 256))[:, :3]
    flat = im.reshape(-1, 3)
    out = np.empty(len(flat))
    for i in range(0, len(flat), 4096):
        d = ((flat[i:i + 4096, None, :] - lut[None] * 255) ** 2).sum(-1)
        out[i:i + 4096] = d.argmin(1) / (len(lut) - 1)
    return out.reshape(im.shape[:2])


def panel(ax, letter, x=-0.02, y=1.02):
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontweight="bold",
            fontsize=9, ha="right", va="bottom")


def checkmin(fig, minimum=7.0):
    """Fail loudly if any visible text in the figure is below `minimum` pt."""
    from matplotlib.text import Text
    small = [(t.get_text(), round(t.get_fontsize(), 1)) for t in fig.findobj(Text)
             if t.get_text().strip() and t.get_visible() and t.get_fontsize() < minimum - 1e-6]
    if small:
        raise SystemExit(f"text below {minimum} pt: {small[:8]}")


def save(fig, name, minimum=7.0):
    checkmin(fig, minimum)
    out = FIG / f"{name}.pdf"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out)
