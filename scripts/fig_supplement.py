"""Supplement figure: screw-bag maps with discordant grid / pair alerts.

Redrawn in Times from the draft's rasters (figures/assets/screw_discordant_*.png);
case labels are taken from the draft figure.
Run: python -I scripts/fig_supplement.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style  # noqa: E402

style.setup()
import matplotlib.pyplot as plt  # noqa: E402

CASES = [("Grid only", "113"), ("Grid only", "120"), ("Pairs only", "060"),
         ("Pairs only", "121"), ("Pairs only", "065")]


def screw():
    fig, axs = plt.subplots(1, 5, figsize=(style.FULL, 1.5),
                            gridspec_kw=dict(wspace=0.06, left=0.0, right=1, top=0.86, bottom=0.0))
    for k, (ax, (kind, case)) in enumerate(zip(axs, CASES)):
        im = np.asarray(Image.open(style.FIG / "assets" / f"screw_discordant_{k}.png").convert("RGB"))
        ax.imshow(im, interpolation="nearest")
        ax.set_title(f"{kind}, case {case}", fontsize=8,
                     color=style.C["released"] if kind.startswith("Grid") else style.C["classwide"])
        ax.axis("off")
    style.save(fig, "screw_discordant")


if __name__ == "__main__":
    screw()
