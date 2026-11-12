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

# one colour per policy, used in every figure
C = {
    "released": "#3b5b92",   # navy
    "released99": "#7f93b8", # light navy
    "classwide": "#c0603a",  # orange
    "footprint": "#1b8a6b",  # teal
    "footprint2": "#6cc3a6", # light teal
    "fault": "#c0603a",
    "vacancy": "#3b5b92",
    "sham": "#1b8a6b",
    "source": "#8c8c8c",
    "target": "#22b8d6",     # cyan boxes
    "queued": "#f29e38",     # orange boxes
    "grey": "#555555",
    "light": "#d9d9d9",
}


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
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
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


def errbar(ax, x, y, lo, hi, color, horizontal=False, ms=4.5, marker="o", **kw):
    """Point with a thick, capped 95% interval."""
    if horizontal:
        ax.errorbar(y, x, xerr=[[y - lo], [hi - y]], fmt=marker, color=color, ms=ms,
                    elinewidth=1.4, capsize=3, capthick=1.4, **kw)
    else:
        ax.errorbar(x, y, yerr=[[y - lo], [hi - y]], fmt=marker, color=color, ms=ms,
                    elinewidth=1.4, capsize=3, capthick=1.4, **kw)


def panel(ax, letter, x=-0.02, y=1.02):
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontweight="bold",
            fontsize=9, ha="right", va="bottom")


def save(fig, name):
    out = FIG / f"{name}.pdf"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out)
