"""Fig. 1 (teaser schematic) and Fig. 2 (pipeline).

Trays are drawn exactly (5 columns x 3 rows, one pin per compartment) because
the BioRender generator drew 3x4 trays. From the BioRender art
(figures/biorender/pipeline.jpg, https://app.biorender.com/illustrations/d6cd7a9c81d719adaeed28c0)
we reuse only the camera, the two network blocks, the alarm gate and the
inspector; every label is typeset here in Times.
Run: python -I scripts/fig_schematic.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style  # noqa: E402

style.setup()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

C = style.C
NCOL, NROW = 5, 3
PIN = "#f2b01e"
TRAY = "#2b2b2e"
CELL = "#3a3a3f"
rng = np.random.default_rng(7)
# fixed pin pose per cell: offset inside the cell and angle
POSE = {(c, r): (rng.uniform(-0.18, 0.18), rng.uniform(-0.15, 0.15), rng.uniform(0, 180))
        for c in range(NCOL) for r in range(NROW)}


def pin(ax, x, y, s, ang, color=PIN, z=5):
    a = np.deg2rad(ang)
    dx, dy = np.cos(a) * s, np.sin(a) * s
    ax.plot([x - dx, x + dx * 0.4], [y - dy, y + dy * 0.4], color="#7a6a4a", lw=0.6, zorder=z)
    ax.plot([x + dx * 0.15, x + dx * 0.55], [y + dy * 0.15, y + dy * 0.55], color=color, lw=2.2,
            solid_capstyle="butt", zorder=z + 1)
    ax.add_patch(Rectangle((x + dx * 0.55 - s * 0.16, y + dy * 0.55 - s * 0.16), s * 0.32, s * 0.32,
                           angle=0, color=color, zorder=z + 1))


def tray(ax, x0, y0, w, pins=None, heat=None, cmap=None, targets=(), dashed=(), queued=(),
         extra=None, missing=(), label=None, faint=False):
    """Draw a 5x3 tray with lower-left corner (x0, y0) and width w.

    pins: cells with their normal pin (default all); extra: {cell: n extra pins};
    heat: 5x3 array in [0,1] drawn as cell colour; targets/dashed/queued: cell boxes.
    """
    h = w * NROW / NCOL
    cw, ch = w / NCOL, h / NROW
    ax.add_patch(FancyBboxPatch((x0 - cw * 0.08, y0 - ch * 0.08), w + cw * 0.16, h + ch * 0.16,
                                boxstyle="round,pad=0,rounding_size=%.3f" % (cw * 0.15),
                                fc="#bdbdbd" if not faint else "#e0e0e0", ec="none", zorder=1))
    for c in range(NCOL):
        for r in range(NROW):
            cx, cy = x0 + c * cw, y0 + (NROW - 1 - r) * ch
            fc = CELL if heat is None else cmap(heat[r, c])
            ax.add_patch(Rectangle((cx + cw * 0.04, cy + ch * 0.04), cw * 0.92, ch * 0.92,
                                   fc=fc, ec="none", zorder=2))
            mx, my = cx + cw / 2, cy + ch / 2
            ox, oy, ang = POSE[(c, r)]
            if (c, r) not in missing and (pins is None or (c, r) in pins):
                pin(ax, mx + ox * cw, my + oy * ch, cw * 0.32, ang)
            for k in range((extra or {}).get((c, r), 0)):
                pin(ax, mx - ox * cw * 0.6 + 0.12 * cw, my - 0.22 * ch, cw * 0.32, ang + 70)
            box = None
            if (c, r) in targets:
                box = dict(ec=C["target"], ls="-")
            if (c, r) in dashed:
                box = dict(ec=C["target"], ls=(0, (2, 1.2)))
            if (c, r) in queued:
                box = dict(ec=C["queued"], ls="-")
            if box:
                ax.add_patch(Rectangle((cx + cw * 0.06, cy + ch * 0.06), cw * 0.88, ch * 0.88,
                                       fc="none", lw=1.3, zorder=8, **box))
    if label:
        ax.text(x0 + w / 2, y0 + h + ch * 0.35, label, ha="center", va="bottom", fontsize=8)
    return h


def arrow(ax, p0, p1, color="#555555", lw=1.0, rad=0.0, z=9):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=7, lw=lw,
                                 color=color, connectionstyle=f"arc3,rad={rad}", zorder=z))


def teaser():
    fig = plt.figure(figsize=(style.FULL, 2.25))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 33)
    ax.axis("off")
    w = 11.4

    # (a) matched edits ------------------------------------------------------
    ax.text(0.5, 31.6, "(a) Matched edits of one held-out photo", fontweight="bold", fontsize=8.5)
    src, dst = (1, 1), (2, 1)   # the pin of cell (col 1, row 1) moves to its right neighbour
    y = 16.4
    xs = [0.6, 12.9, 25.2, 37.5]
    cw = w / NCOL
    ch = cw
    tray(ax, xs[0], y, w, label="Source")
    tray(ax, xs[1], y, w, missing=[src], label="Valid sham")
    tray(ax, xs[2], y, w, missing=[src], extra={dst: 1}, targets=[dst], dashed=[src], label="Fault")
    tray(ax, xs[3], y, w, missing=[src], dashed=[src], label="Vacancy only")
    sx = xs[1] + (src[0] + 0.5) * cw
    sy = y + (NROW - 1 - src[1] + 0.5) * ch
    ox, oy, ang = POSE[src]
    # sham: the same pin, displaced inside its own cell (same distance as the fault move)
    pin(ax, sx - 0.25 * cw, sy - 0.2 * ch, cw * 0.32, ang + 70)
    arrow(ax, (sx + ox * cw, sy + oy * ch + 0.5), (sx - 0.2 * cw, sy - 0.05 * ch), color="white", lw=0.8)
    fx = xs[2] + (src[0] + 0.5) * cw
    arrow(ax, (fx - 0.2 * cw, sy), (fx + cw * 0.75, sy), color="white", lw=0.9)
    notes = ["one pin per cell", "pin moved within\nits own cell (valid)",
             "same move into the\noccupied neighbour", "pin removed:\nthe vacancy alone"]
    for x, n in zip(xs, notes):
        ax.text(x + w / 2, y - 1.0, n, ha="center", va="top", fontsize=6.8, color="#333333",
                linespacing=1.05)
    ax.text(24.6, 6.4, "Same cutout, background fill and displacement in every arm. The vacated and\n"
                       "recipient cells (cyan) are the two compartments an inspector must check.",
            ha="center", va="center", fontsize=6.8, style="italic", color="#333333", linespacing=1.1)

    # divider
    ax.plot([50.2, 50.2], [2, 31], color="#cccccc", lw=0.6)

    # (b) supervision -> queue ----------------------------------------------
    ax.text(51.2, 31.6, "(b) After an alert: which compartments are queued?", fontweight="bold",
            fontsize=8.5)
    cmap = plt.get_cmap("magma")
    w2 = 9.6
    rows = [(19.0, "Class-wide target", "every pin of the class\nis marked anomalous",
             True, "2 targets + 11 untouched cells"),
            (4.6, "Footprint target", "only the pasted pin\nis marked anomalous",
             False, "2 targets + 0 untouched cells")]
    for yy, title, sub, broad, qtxt in rows:
        # training target: binary mask drawn as white pins on black
        h = w2 * NROW / NCOL
        cw2 = w2 / NCOL
        ax.add_patch(Rectangle((52.0, yy), w2, h, fc="black", ec="#888888", lw=0.5, zorder=1))
        for c in range(NCOL):
            for r in range(NROW):
                ox, oy, ang = POSE[(c, r)]
                cx = 52.0 + (c + 0.5 + ox) * cw2
                cy = yy + (NROW - 1 - r + 0.5 + oy) * cw2
                on = broad or (c, r) == dst
                if broad or (c, r) == dst:
                    pin(ax, cx, cy, cw2 * 0.32, ang, color="white" if on else "#333333")
        ax.text(52.0 + w2 / 2, yy + h + 0.5, title, ha="center", va="bottom", fontsize=7.6,
                fontweight="bold")
        ax.text(52.0 + w2 / 2, yy - 0.5, sub, ha="center", va="top", fontsize=6.4, color="#333333",
                linespacing=1.0)
        arrow(ax, (63.0, yy + h / 2), (67.6, yy + h / 2))
        ax.text(65.3, yy + h / 2 + 0.6, "fine-tune", ha="center", va="bottom", fontsize=6.2)
        # test map on the fault, per-cell maximum score
        heat = np.full((NROW, NCOL), 0.08)
        if broad:
            heat = np.array([[.72, .66, .80, .70, .62], [.75, .88, .93, .69, .71], [.64, .70, .77, .68, .73]])
        heat[src[1], src[0]] = 0.95
        heat[dst[1], dst[0]] = 0.97
        targ = [src, dst]
        queued = [(c, r) for c in range(NCOL) for r in range(NROW)
                  if (c, r) not in targ and heat[r, c] >= 0.66]
        tray(ax, 68.4, yy, w2, heat=heat, cmap=cmap, missing=[src], extra={dst: 1},
             targets=targ, queued=queued)
        ax.text(68.4 + w2 / 2, yy + h + 0.5, "score map on the fault", ha="center", va="bottom",
                fontsize=7)
        arrow(ax, (79.0, yy + h / 2), (83.0, yy + h / 2))
        ax.text(81.0, yy + h / 2 + 0.6, r"$g\geq t_c$", ha="center", va="bottom", fontsize=7)
        col = C["classwide"] if broad else C["footprint"]
        ax.text(83.6, yy + h / 2 + 1.3, "inspection queue", fontsize=7, va="bottom")
        ax.text(83.6, yy + h / 2, qtxt, fontsize=7, va="center", color=col, fontweight="bold")
        ax.text(83.6, yy + h / 2 - 1.3, "long queue at 95% recall" if broad else
                "short queue at 95% recall", fontsize=6.6, va="top", color="#333333")
    # legend for boxes
    ax.add_patch(Rectangle((84.0, 1.2), 1.2, 1.0, fc="none", ec=C["target"], lw=1.2))
    ax.text(85.6, 1.7, "target cell", fontsize=6.4, va="center")
    ax.add_patch(Rectangle((91.0, 1.2), 1.2, 1.0, fc="none", ec=C["queued"], lw=1.2))
    ax.text(92.6, 1.7, "queued untouched", fontsize=6.4, va="center")
    style.save(fig, "teaser")


def icon(name, box, thr=236):
    """Crop a BioRender element and make its near-white background transparent."""
    im = Image.open(style.FIG / "biorender" / "pipeline.jpg").convert("RGB").crop(box)
    a = np.asarray(im).astype(float)
    alpha = np.where(a.min(axis=2) > thr, 0, 255).astype(np.uint8)
    return np.dstack([a.astype(np.uint8), alpha])


def pipeline():
    fig = plt.figure(figsize=(style.FULL, 1.55))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 22.5)
    ax.axis("off")
    H = 22.5 / 1.55 * 6.875 / 100  # aspect: data units per x unit

    def place(img, x, y, wdt):
        hh = wdt * img.shape[0] / img.shape[1] / H
        ax.imshow(img, extent=(x, x + wdt, y, y + hh), zorder=3, interpolation="lanczos")
        return hh

    cam = icon("camera", (70, 88, 132, 182))
    place(cam, 0.6, 10.5, 4.6)
    photo = np.asarray(Image.open(style.FIG / "assets" / "pushpin_intervention_2.png").convert("RGB"))
    place(photo, 5.6, 8.6, 11.0)
    ax.text(11.1, 6.9, "RGB photo $x_i$", ha="center", va="top", fontsize=7)
    ax.text(11.1, 4.9, "(held-out, edited)", ha="center", va="top", fontsize=6.4, color="#444444")
    arrow(ax, (17.0, 12.3), (19.0, 12.3))

    un1 = icon("unet1", (190, 255, 262, 335))
    place(un1, 19.3, 9.5, 5.2)
    ax.text(21.9, 6.9, "part extractor", ha="center", va="top", fontsize=7)
    ax.text(21.9, 4.9, "(U-Net, or oracle)", ha="center", va="top", fontsize=6.4, color="#444444")
    arrow(ax, (25.0, 12.3), (27.0, 12.3))

    # part map: dark background with orange pins (schematic 6-class map)
    w = 10.0
    h = w * NROW / NCOL / H * (1 / 1)
    cw = w / NCOL
    ax.add_patch(Rectangle((27.4, 8.6), w, w * 3 / 5 / H, fc="#1d2a4d", ec="none", zorder=2))
    hh = w * 3 / 5 / H
    for c in range(NCOL):
        for r in range(NROW):
            ox, oy, ang = POSE[(c, r)]
            pin(ax, 27.4 + (c + 0.5 + ox) * cw, 8.6 + (NROW - 1 - r + 0.5 + oy) * hh / NROW, cw * 0.3,
                ang, color="#f08a3c")
    ax.text(32.4, 6.9, "part map $m_i$", ha="center", va="top", fontsize=7)
    ax.text(32.4, 4.9, "(6 classes)", ha="center", va="top", fontsize=6.4, color="#444444")
    arrow(ax, (38.0, 12.3), (40.0, 12.3))

    un2 = icon("unet2", (437, 255, 510, 335))
    place(un2, 40.3, 9.5, 5.2)
    ax.text(42.9, 6.9, "composition", ha="center", va="top", fontsize=7)
    ax.text(42.9, 4.9, "branch (SALAD)", ha="center", va="top", fontsize=6.4, color="#444444")
    arrow(ax, (46.0, 12.3), (48.0, 12.3))

    gm = np.asarray(Image.open(style.FIG / "assets" / "guidance_maps_0.png").convert("RGB"))
    gm = gm[24:116, :, :]  # tray region of the released map
    place(gm, 48.3, 8.6, 10.0)
    ax.text(53.3, 6.9, "score map $S_i$", ha="center", va="top", fontsize=7)
    ax.text(53.3, 4.9, r"(pixels in $[0,1]$)", ha="center", va="top", fontsize=6.4, color="#444444")
    arrow(ax, (58.9, 12.3), (60.9, 12.3))

    gate = icon("gate", (683, 245, 762, 328))
    place(gate, 61.1, 9.6, 5.6)
    ax.text(63.9, 6.9, "scene gate", ha="center", va="top", fontsize=7)
    ax.text(63.9, 4.9, r"$\max S_i > t_s$ ?", ha="center", va="top", fontsize=6.6)
    arrow(ax, (67.3, 12.3), (69.3, 12.3))

    # cell scores as bars with the cutoff
    bx = 69.8
    sc = np.array([.98, .96, .41, .35, .31, .28, .22, .2, .18, .15, .12, .1, .08, .06, .05])
    for k, s in enumerate(sc):
        col = C["target"] if k < 2 else ("#bbbbbb")
        ax.add_patch(Rectangle((bx + k * 0.62, 8.8), 0.5, s * 8.5, fc=col, ec="none", zorder=3))
    ax.plot([bx - 0.3, bx + 15 * 0.62], [8.8 + 0.6 * 8.5] * 2, color=C["queued"], lw=1.0, ls="--")
    ax.text(bx + 15 * 0.62 + 0.2, 8.8 + 0.6 * 8.5, "$t_c$", fontsize=7, va="center", color=C["queued"])
    ax.text(bx + 5.0, 6.9, "15 cell scores", ha="center", va="top", fontsize=7)
    ax.text(bx + 5.0, 4.9, r"$g$ = maximum in cell $e$", ha="center", va="top", fontsize=6.4)
    arrow(ax, (80.6, 12.3), (82.6, 12.3))

    insp = icon("inspector", (952, 210, 1012, 422))
    place(insp, 90.6, 4.6, 4.6)
    ax.text(86.6, 15.5, r"queue $Q_i$", ha="center", va="bottom", fontsize=7)
    ax.text(86.6, 13.3, r"$\{e: g\geq t_c\}$", ha="center", va="bottom", fontsize=6.6)
    ax.text(86.6, 9.6, "recall $R$,\ncost $C$", ha="center", va="top", fontsize=6.6, linespacing=1.0)
    ax.text(96.2, 2.6, "inspector", ha="center", va="top", fontsize=6.4, color="#444444")
    # bracket for what we change
    ax.annotate("", xy=(40.0, 20.0), xytext=(46.4, 20.0),
                arrowprops=dict(arrowstyle="-", color=C["footprint"], lw=1.0))
    ax.text(43.2, 20.4, "we fine-tune its training target", ha="center", va="bottom", fontsize=6.6,
            color=C["footprint"])
    ax.annotate("", xy=(61.0, 20.0), xytext=(80.0, 20.0),
                arrowprops=dict(arrowstyle="-", color=C["released"], lw=1.0))
    ax.text(70.5, 20.4, r"cutoffs $t_s$, $t_c$ fixed on development photos", ha="center", va="bottom",
            fontsize=6.6, color=C["released"])
    style.save(fig, "pipeline")


if __name__ == "__main__":
    teaser()
    pipeline()
