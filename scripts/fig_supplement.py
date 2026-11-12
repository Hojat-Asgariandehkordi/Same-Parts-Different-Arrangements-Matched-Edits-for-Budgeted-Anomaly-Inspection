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
    fig, axs = plt.subplots(1, 5, figsize=(style.FULL, 1.7),
                            gridspec_kw=dict(wspace=0.06, left=0.0, right=1, top=0.76, bottom=0.0))
    for k, (ax, (kind, case)) in enumerate(zip(axs, CASES)):
        im = np.asarray(Image.open(style.FIG / "assets" / f"screw_discordant_{k}.png").convert("RGB"))
        ax.imshow(im, interpolation="nearest")
        ax.set_title(f"case {case}", fontsize=8)
        ax.axis("off")
    for x0, x1, t in ((0.0, 0.395, "alarm under the grid summary only"),
                      (0.405, 1.0, "alarm under the centroid-pair summary only")):
        fig.add_artist(plt.Line2D([x0 + 0.01, x1 - 0.01], [0.9, 0.9], color="black", lw=0.7))
        fig.text((x0 + x1) / 2, 0.92, t, ha="center", va="bottom", fontsize=8)
    style.save(fig, "screw_discordant")


if __name__ == "__main__":
    screw()
