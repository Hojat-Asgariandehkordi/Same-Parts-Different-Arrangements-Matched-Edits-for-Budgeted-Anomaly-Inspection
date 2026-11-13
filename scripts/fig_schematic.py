"""Fig. 1 (teaser) and Fig. 2 (pipeline).

BioRender art used (all labels are typeset here in Times):
  figures/biorender/edits.jpg    four matched trays, https://app.biorender.com/illustrations/89279b87d8b90f86021b6c98
                                 (drawn 3 wide x 5 tall; each tray is rotated 90 deg to the real 5x3 layout)
  figures/biorender/sprites.jpg  pushpin sprite, https://app.biorender.com/illustrations/34d915d6560d8c96482046fe
  figures/biorender/pipeline.jpg network-block icons, https://app.biorender.com/illustrations/d6cd7a9c81d719adaeed28c0
Trays in Fig. 1(b) and Fig. 2 are drawn in code with the sprite so that the
5x3 compartment count and the moved pins are exact.
Run: python -I scripts/fig_schematic.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data as D  # noqa: E402
import style  # noqa: E402

style.setup()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

C = style.C
NC, NR = 5, 3
PIN = style.sprite("pin")
GREY = plt.get_cmap(style.SCORE_CMAP)
rng = np.random.default_rng(11)
POSE = {(c, r): (rng.uniform(-0.12, 0.12), rng.uniform(-0.1, 0.1), rng.uniform(-60, 60))
        for c in range(NC) for r in range(NR)}
# the running fault, as in the BioRender trays after rotation: the pin of the
# centre compartment (col 2, row 1) moves up into (col 2, row 0)
VAC, REC = (2, 1), (2, 0)


def pin_img(angle, white=False):
    im = Image.fromarray(PIN).rotate(angle, expand=True, resample=Image.BICUBIC)
    a = np.asarray(im).copy()
    if white:
        a[..., :3] = 255
    return a


def draw_pin(ax, x, y, length, angle, white=False, alpha=1.0, z=6):
    a = pin_img(angle, white)
    h, w = a.shape[:2]
    s = length / PIN.shape[1]
    ax.imshow(a, extent=(x - w * s / 2, x + w * s / 2, y - h * s / 2, y + h * s / 2),
              zorder=z, alpha=alpha, interpolation="lanczos")


def tray(ax, x0, y0, w, pins, fill=None, outline=None, mask=False, frame=True):
    """5x3 tray at lower-left (x0, y0), width w (data units = inches).

    pins: {cell: [(dx, dy, angle), ...]}; fill: {cell: grey value 0..1};
    outline: {cell: (colour, linestyle)}; mask: white pins on black (training target).
    """
    cw = w / NC
    h = cw * NR
    if frame:
        ax.add_patch(FancyBboxPatch((x0 - .03, y0 - .03), w + .06, h + .06,
                                    boxstyle="round,pad=0,rounding_size=0.05",
                                    fc="black" if mask else "#9a9a9a", ec="none", zorder=1))
    for c in range(NC):
        for r in range(NR):
            cx, cy = x0 + c * cw, y0 + (NR - 1 - r) * cw
            if mask:
                fc = "black"
            elif fill is not None:
                fc = GREY(fill[(c, r)])
            else:
                fc = "#2e2e31"
            ax.add_patch(Rectangle((cx + .012, cy + .012), cw - .024, cw - .024, fc=fc, ec="none", zorder=2))
            for dx, dy, ang in pins.get((c, r), []):
                draw_pin(ax, cx + cw * (0.5 + dx), cy + cw * (0.5 + dy), cw * 0.62, ang, white=mask,
                         alpha=0.55 if (fill is not None and not mask) else 1.0)
            if outline and (c, r) in outline:
                col, ls = outline[(c, r)]
                ax.add_patch(Rectangle((cx + .03, cy + .03), cw - .06, cw - .06, fc="none", ec=col,
                                       lw=1.5, ls=ls, zorder=9))
    return h


def vac_mark(ax, x0, y0, w):
    """Vacated footprint in a training mask: a grey pin (marked in both policies)."""
    cw = w / NC
    c, r = VAC
    a = pin_img(POSE[VAC][2], white=True)
    a[..., :3] = 150
    hh, ww = a.shape[:2]
    s = cw * 0.62 / PIN.shape[1]
    x = x0 + (c + 0.5) * cw
    y = y0 + (NR - 1 - r + 0.5) * cw
    ax.imshow(a, extent=(x - ww * s / 2, x + ww * s / 2, y - hh * s / 2, y + hh * s / 2), zorder=7)


def layout(kind):
    """Pins per cell for the source / fault arrangement."""
    p = {k: [v] for k, v in POSE.items()}
    if kind == "fault":
        p[VAC] = []
        p[REC] = [(-0.18, 0.12, POSE[REC][2]), (0.12, -0.16, POSE[VAC][2] + 25)]
    return p


def arrow(ax, p0, p1, color="#444444", lw=1.0, ls="-", rad=0.0, z=10, ms=8):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw, ls=ls,
                                 color=color, connectionstyle=f"arc3,rad={rad}", zorder=z))


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# ---------------------------------------------------------------------------
def teaser():
    W, H = style.FULL, 2.95
    fig, ax = canvas(W, H)

    # (a) BioRender matched trays, rotated to 5x3 --------------------------
    ax.text(0.02, H - 0.05, "(a) Matched edits (illustration)", fontweight="bold", fontsize=9,
            va="top")
    ax.text(0.02, H - 0.24, "same pin  ·  same cutout and fill  ·  same distance", fontsize=7.5,
            va="top", style="italic", color="#333333")
    art = Image.open(style.FIG / "biorender" / "edits.jpg").convert("RGB")
    boxes = [(10, 108, 256, 458), (263, 108, 510, 458), (516, 108, 762, 458), (769, 108, 1015, 458)]
    tw = 1.36
    pos = [(0.12, 1.65), (1.82, 1.65), (0.12, 0.38), (1.82, 0.38)]
    labels = [("Source", "one pin per compartment", "no target", "#333333"),
              ("Valid sham (allowed)", "moved within its compartment", "no target", C["sham"]),
              ("Fault (breaks the rule)", "same move into the neighbour", "2 targets", C["fault"]),
              ("Vacancy only", "pin removed", "1 target", C["vacancy"])]
    for (bx, by), b, (t1, t2, t3, col) in zip(pos, boxes, labels):
        im = np.asarray(art.crop(b).transpose(Image.ROTATE_90))
        th = tw * im.shape[0] / im.shape[1]
        ax.imshow(im, extent=(bx, bx + tw, by, by + th), zorder=2, interpolation="lanczos")
        ax.text(bx, by - 0.04, t1, fontsize=8, fontweight="bold", color=col, va="top")
        ax.text(bx, by - 0.2, t2 if t3 == "no target" else f"{t2}; {t3}", fontsize=7.5, va="top",
                color="#333333")
    ax.plot([3.42, 3.42], [0.1, H - 0.1], color="#cccccc", lw=0.6)

    # (b) what the inspector receives ---------------------------------------
    x0 = 3.55
    ax.text(x0, H - 0.05, "(b) After an alarm on the fault: which compartments are opened?",
            fontweight="bold", fontsize=9, va="top")
    fault = layout("fault")
    targets = {VAC: (C["target"], (0, (2.2, 1.4))), REC: (C["target"], "-")}
    rows = [(1.72, "Class-wide target", "every pin of the class marked", True),
            (0.56, "Footprint target", "only the pasted pin marked", False)]
    mw = 0.98
    for y, title, sub, broad in rows:
        # training target on the same edited tray (vacated footprint marked in both)
        mpins = {k: (v if broad else []) for k, v in fault.items()}
        if not broad:
            mpins[REC] = [fault[REC][1]]
        h = tray(ax, x0 + 0.02, y, mw, mpins, mask=True)
        vac_mark(ax, x0 + 0.02, y, mw)
        ax.text(x0 + 0.02, y + h + 0.08, title, fontsize=8, fontweight="bold", va="bottom",
                color=C["classwide"] if broad else C["footprint"])
        ax.text(x0 + 0.02, y - 0.05, "training mask $y$: " + sub, fontsize=7.5, va="top")
        ax.text(x0 + 0.02, y - 0.2, "(grey: vacated spot, marked in both)", fontsize=7, va="top",
                color="#555555")
        arrow(ax, (x0 + mw + 0.08, y + h / 2), (x0 + mw + 0.34, y + h / 2))
        # test-time compartment scores (schematic) and the queue
        vals = {}
        for c in range(NC):
            for r in range(NR):
                vals[(c, r)] = (0.66 + 0.18 * ((c * 7 + r * 3) % 5) / 4) if broad else 0.04 + 0.02 * ((c + r) % 3)
        vals[VAC], vals[REC] = (0.97, 0.94) if broad else (0.86, 0.72)
        if broad:   # two untouched compartments stay below t_c: 11 of 13 queued, as measured (11.07)
            vals[(0, 2)], vals[(4, 0)] = 0.45, 0.52
        tc = 0.6
        out = dict(targets)
        for k, v in vals.items():
            if k not in targets and v >= tc:
                out[k] = (C["queued"], "-")
        mx = x0 + mw + 0.42
        tray(ax, mx, y, mw, fault, fill=vals, outline=out)
        ax.text(mx, y + h + 0.08, "compartment scores at test", fontsize=7.5, va="bottom")
        n_q = sum(1 for k in out if k not in targets)
        arrow(ax, (mx + mw + 0.08, y + h / 2), (mx + mw + 0.34, y + h / 2))
        ax.text(mx + mw + 0.21, y + h / 2 + 0.05, r"$g\geq t_c$", fontsize=7.5, ha="center", va="bottom")
        # queue as a 5x3 block of 15 boxes
        qx = mx + mw + 0.42
        bw = 0.135
        for k in range(15):
            col = C["target"] if k < 2 else (C["queued"] if k < 2 + n_q else "white")
            ax.add_patch(Rectangle((qx + (k % 5) * bw, y + h - 0.02 - (k // 5 + 1) * bw), bw * .86, bw * .86,
                                   fc=col, ec="#888888", lw=0.4, zorder=3))
        ax.text(qx, y + h + 0.08, "compartments opened", fontsize=7.5, va="bottom")
        ax.text(qx, y + h - 0.12 - 3 * bw, f"{2 + n_q} of 15", fontsize=9, fontweight="bold", va="top",
                color=C["classwide"] if broad else C["footprint"])
        ax.text(qx, y + h - 0.33 - 3 * bw, f"2 targets + {n_q} untouched", fontsize=7.5, va="top")
    # legend + colour bar
    ly = 0.08
    ax.add_patch(Rectangle((x0 + 0.02, ly), 0.12, 0.09, fc="none", ec=C["target"], lw=1.4))
    ax.text(x0 + 0.18, ly + 0.045, "target", fontsize=7.5, va="center")
    ax.add_patch(Rectangle((x0 + 0.62, ly), 0.12, 0.09, fc="none", ec=C["queued"], lw=1.4))
    ax.text(x0 + 0.78, ly + 0.045, "queued untouched", fontsize=7.5, va="center")
    cb = np.linspace(0, 1, 128)[None]
    ax.imshow(cb, cmap=GREY, extent=(x0 + 1.95, x0 + 2.95, ly, ly + 0.09), aspect="auto", zorder=3)
    ax.add_patch(Rectangle((x0 + 1.95, ly), 1.0, 0.09, fc="none", ec="#666666", lw=0.4, zorder=4))
    ax.text(x0 + 1.9, ly + 0.045, "score 0", fontsize=7.5, ha="right", va="center")
    ax.text(x0 + 3.0, ly + 0.045, "1", fontsize=7.5, va="center")
    ax.plot([x0 + 1.95 + 0.6] * 2, [ly - 0.02, ly + 0.11], color=C["queued"], lw=1.0, zorder=5)
    ax.text(x0 + 2.55, ly + 0.12, "$t_c$", fontsize=7.5, ha="center", va="bottom")
    style.save(fig, "teaser")


# ---------------------------------------------------------------------------
def icon(box, thr=236):
    im = Image.open(style.FIG / "biorender" / "pipeline.jpg").convert("RGB").crop(box)
    a = np.asarray(im).astype(float)
    alpha = np.where(a.min(axis=2) > thr, 0, 255).astype(np.uint8)
    return np.dstack([a.astype(np.uint8), alpha])


def place(ax, img, x, y, w, z=3):
    h = w * img.shape[0] / img.shape[1]
    ax.imshow(img, extent=(x, x + w, y, y + h), zorder=z, interpolation="lanczos")
    return h


def label(ax, x, y, t1, t2=None, col="black"):
    ax.text(x, y, t1, fontsize=7.5, ha="center", va="top", color=col)
    if t2:
        ax.text(x, y - 0.15, t2, fontsize=7, ha="center", va="top", color="#444444")


def part_map_from_photo(photo):
    """Illustrative part map of the running photo: pins (orange) by colour, tray (grey) by brightness."""
    a = photo.astype(int)
    pin = (a[..., 0] > 150) & (a[..., 1] > 100) & (a[..., 2] < 110)
    tray_px = (a.mean(-1) > 105) & ~pin
    out = np.zeros(a.shape, np.uint8)
    out[:] = (29, 42, 77)
    out[tray_px] = (150, 160, 175)
    out[pin] = (240, 138, 60)
    return out


def pipeline():
    W, H = style.FULL, 2.45
    fig, ax = canvas(W, H)
    photo = np.asarray(Image.open(style.FIG / "assets" / "pushpin_intervention_2.png").convert("RGB"))
    row = D.PHOTO_ROWS[0]
    vac, rec = row["src"], row["dst"]
    iw = 0.86
    yb = 0.55   # bottom lane baseline

    # ---- training lane (top) --------------------------------------------
    ax.add_patch(FancyBboxPatch((0.03, 1.53), 3.62, 0.88, boxstyle="round,pad=0,rounding_size=0.05",
                                fc="#eef6f2", ec=C["train"], lw=0.8, zorder=0))
    ax.text(0.1, 2.37, "Training: only the target mask $y$ changes", fontsize=8, fontweight="bold",
            color=C["train"], va="top")
    tr = layout("fault")
    w0 = 0.78
    h0 = tray(ax, 0.18, 1.65, w0, tr, fill={k: 0.08 for k in POSE})
    ax.text(0.18 + w0 / 2, 1.63, "synthetic edit", fontsize=7.5, ha="center", va="top")
    arrow(ax, (1.0, 1.65 + h0 / 2), (1.2, 1.65 + h0 / 2))
    ww = 0.58
    for k, (nm, broad) in enumerate((("class-wide", True), ("footprint", False))):
        mp = {kk: (v if broad else []) for kk, v in tr.items()}
        if not broad:
            mp[REC] = [tr[REC][1]]
        xx = 1.24 + k * 0.82
        hh = tray(ax, xx, 1.79, ww, mp, mask=True)
        vac_mark(ax, xx, 1.79, ww)
        ax.text(xx + ww / 2, 1.75, nm, fontsize=7.5, ha="center", va="top",
                color=C["classwide"] if broad else C["footprint"], fontweight="bold")
    ax.text(1.24 + 0.58 + 0.12, 1.79 + hh / 2, "or", fontsize=7.5, ha="center", va="center")
    arrow(ax, (2.68, 1.65 + h0 / 2), (2.88, 1.65 + h0 / 2))
    ax.text(3.27, 1.97, "loss (Eq. 4),\n800 steps", fontsize=7.5, ha="center", va="center", linespacing=1.0)

    # ---- calibration box (top right) ------------------------------------
    ax.add_patch(FancyBboxPatch((3.78, 1.53), 3.06, 0.88, boxstyle="round,pad=0,rounding_size=0.05",
                                fc="#eef1f8", ec=C["calib"], lw=0.8, zorder=0))
    ax.text(3.86, 2.37, "Fixed on development data (never on test)", fontsize=8, fontweight="bold",
            color=C["calib"], va="top")
    ax.text(3.86, 2.17, "$t_s$: 63rd smallest maximum of 69 normal photos\n"
                       "      ($\\leq$10% of normal trays raise an alarm)\n"
                       "$t_c$: highest cutoff that finds 95% of the\n"
                       "      targets of 69 matched development faults",
            fontsize=7.5, va="top", linespacing=1.15)

    # ---- test lane (bottom) ---------------------------------------------
    ax.text(0.06, 1.42, "Test-time inspection", fontsize=8, fontweight="bold", va="top")
    x = 0.06
    ph = place(ax, photo, x, yb, iw)
    for (c, r), ls in ((vac, (0, (2, 1.2))), (rec, "-")):
        X0, X1 = D.PHOTO_X[c], D.PHOTO_X[c + 1]
        Y0, Y1 = D.PHOTO_Y[r], D.PHOTO_Y[r + 1]
        ax.add_patch(Rectangle((x + X0 * iw, yb + ph * (1 - Y1)), (X1 - X0) * iw, (Y1 - Y0) * ph,
                               fc="none", ec=C["target"], lw=1.1, ls=ls, zorder=6))
    label(ax, x + iw / 2, yb - 0.05, "photo $x_i$ (a fault)", "held-out, edited")
    arrow(ax, (x + iw + 0.03, yb + ph / 2), (x + iw + 0.15, yb + ph / 2))
    un1 = icon((190, 255, 262, 335))
    x = x + iw + 0.17
    place(ax, un1, x, yb + 0.02, 0.33)
    label(ax, x + 0.17, yb - 0.05, "U-Net", "extractor")
    arrow(ax, (x + 0.36, yb + ph / 2), (x + 0.48, yb + ph / 2))
    x = x + 0.5
    pmap = part_map_from_photo(photo)
    place(ax, pmap, x, yb, iw)
    label(ax, x + iw / 2, yb - 0.05, "part map $m_i$")
    # oracle bypass
    arrow(ax, (x - 0.02, yb - 0.38), (x + 0.06, yb + 0.04), ls=(0, (3, 2)), color="#666666")
    ax.text(x - 1.35, yb - 0.46, "oracle: same edit applied to the released label map",
            fontsize=7, va="center", ha="left", color="#555555")
    arrow(ax, (x + iw + 0.03, yb + ph / 2), (x + iw + 0.15, yb + ph / 2))
    un2 = icon((437, 255, 510, 335))
    x = x + iw + 0.17
    place(ax, un2, x, yb + 0.02, 0.33)
    ax.add_patch(Rectangle((x - 0.04, yb - 0.01), 0.41, 0.46, fc="none", ec=C["train"], lw=1.0, zorder=4))
    label(ax, x + 0.17, yb - 0.05, "composition", "branch $f$")
    arrow(ax, (x + 0.17, 1.53), (x + 0.17, yb + 0.47), color=C["train"], lw=1.0)
    ax.text(x + 0.22, 1.45, "fine-tuned\nweights", fontsize=7, color=C["train"], va="top", linespacing=1.0)
    arrow(ax, (x + 0.38, yb + ph / 2), (x + 0.5, yb + ph / 2))
    x = x + 0.52
    # running-example compartment scores: 2 targets + 3 untouched above t_c (the Eq. 3 example)
    vals = {k: 0.12 + 0.08 * ((k[0] * 5 + k[1] * 3) % 4) for k in POSE}
    vals[vac], vals[rec] = 0.97, 0.93
    for k, v in zip(((1, 0), (1, 1), (3, 2)), (0.74, 0.69, 0.66)):
        vals[k] = v
    tc = 0.6
    gw = 0.86
    gh = tray(ax, x, yb, gw, {}, fill=vals)
    for (c, r), v in vals.items():
        cw = gw / NC
        ax.text(x + (c + .5) * cw, yb + (NR - 1 - r + .5) * cw, f"{v:.2f}"[1:], fontsize=7, ha="center",
                va="center", color="black" if v >= 0.5 else "white", zorder=10)
    label(ax, x + gw / 2, yb - 0.05, "compartment scores", "$g_i(e)$ = max of $S_i$ in $e$")
    arrow(ax, (x + gw + 0.03, yb + gh / 2), (x + gw + 0.13, yb + gh / 2))
    # gate diamond
    x = x + gw + 0.15
    dw, dh = 0.5, 0.42
    cy = yb + gh / 2
    ax.add_patch(Polygon([(x, cy), (x + dw / 2, cy + dh / 2), (x + dw, cy), (x + dw / 2, cy - dh / 2)],
                         closed=True, fc="#fdecea", ec=C["alarm"], lw=1.0, zorder=3))
    ax.text(x + dw / 2, cy, r"max $S_i$" + "\n" + r"$>t_s$?", fontsize=7, ha="center", va="center",
            linespacing=1.0, zorder=4)
    arrow(ax, (x + dw / 2, cy - dh / 2), (x + dw / 2, yb - 0.3), color=C["alarm"])
    ax.text(x + dw / 2 + 0.04, cy - dh / 2 - 0.02, "no", fontsize=7, color=C["alarm"], va="top")
    ax.text(x + dw / 2, yb - 0.33, "$Q_i=\\varnothing$: tray not\nopened, targets missed", fontsize=7,
            ha="center", va="top", color=C["alarm"], linespacing=1.0)
    arrow(ax, (x + dw, cy), (x + dw + 0.15, cy), color=C["alarm"])
    ax.text(x + dw + 0.02, cy + 0.03, "yes", fontsize=7, color=C["alarm"], va="bottom")
    # queue
    x = x + dw + 0.17
    out = {vac: (C["target"], (0, (2.2, 1.4))), rec: (C["target"], "-")}
    for k, v in vals.items():
        if k not in out and v >= tc:
            out[k] = (C["queued"], "-")
    tray(ax, x, yb, gw, {}, fill={k: 0.92 for k in vals}, outline=out)
    label(ax, x + gw / 2, yb - 0.05, r"queue $Q_i=\{e: g_i(e)\geq t_c\}$")
    ax.text(x + gw / 2, yb - 0.21, "$R$ = 2/2,  $C$ = 3 untouched", fontsize=7.5, ha="center", va="top",
            color=C["queued"])
    # dashed calibration arrows
    arrow(ax, (5.0, 1.53), (x - dw / 2 - 0.15, cy + dh / 2 + 0.02), ls=(0, (3, 2)), color=C["calib"])
    arrow(ax, (6.2, 1.53), (x + gw / 2, yb + gh + 0.03), ls=(0, (3, 2)), color=C["calib"])
    style.save(fig, "pipeline")


if __name__ == "__main__":
    teaser()
    pipeline()
