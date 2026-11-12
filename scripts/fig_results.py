"""Result figures of the main paper (Figs. 3-8). All numbers come from scripts/data.py.

Colour system (style.C): models released grey / class-wide purple / footprint green,
seed 2 hollow or dashed; edit types source grey / sham blue / fault vermilion /
vacancy ochre; cyan = target and orange = queued untouched are overlays only;
score maps in greyscale. No text below 7 pt (style.save checks this).
Run: python -I scripts/fig_results.py
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
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

C = style.C
A = style.FIG / "assets"
GREY = plt.get_cmap(style.SCORE_CMAP)
DASH = (0, (2.2, 1.4))


def rgb(name):
    return np.asarray(Image.open(A / f"{name}.png").convert("RGB"))


def cell_box(ax, xs, ys, c, r, col, ls="-", lw=1.4, inset=0.008):
    x0, x1, y0, y1 = xs[c], xs[c + 1], ys[r], ys[r + 1]
    ax.add_patch(Rectangle((x0 + inset, y0 + inset), x1 - x0 - 2 * inset, y1 - y0 - 2 * inset,
                           fc="none", ec=col, lw=lw, ls=ls, zorder=5))


def no_frame(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


# ---------------------------------------------------------------------------
def photos():
    """Fig. 3: real matched edits (oracle maps) and the per-compartment change of the released map."""
    fig = plt.figure(figsize=(style.FULL, 2.25))
    gs = fig.add_gridspec(2, 5, width_ratios=[1, 1, 1, 1, 0.06], wspace=0.05, hspace=0.42,
                          left=0.075, right=0.955, top=0.86, bottom=0.08)
    heads = ["Source", "Valid sham", "Fault", r"Fault: $|\Delta S|$ per compartment"]
    rows = ["Typical fault\n(median effect)", "Sham that\nraises an alarm"]
    for i, row in enumerate(D.PHOTO_ROWS):
        delta = style.score_map_values(f"pushpin_intervention_{4 * i + 3}", "magma")
        H, W = delta.shape
        for j in range(4):
            ax = fig.add_subplot(gs[i, j])
            if j < 3:
                ax.imshow(rgb(f"pushpin_intervention_{4 * i + j}"), extent=(0, 1, 1, 0), aspect="auto",
                          interpolation="lanczos")
            else:
                ax.add_patch(Rectangle((0, 0), 1, 1, fc="#bdbdbd", ec="none"))
                for r in range(3):
                    for c in range(5):
                        y0, y1 = int(D.PHOTO_Y[r] * H) + 3, int(D.PHOTO_Y[r + 1] * H) - 3
                        x0, x1 = int(D.PHOTO_X[c] * W) + 3, int(D.PHOTO_X[c + 1] * W) - 3
                        v = float(np.median(delta[y0:y1, x0:x1]))
                        X0, X1, Y0, Y1 = D.PHOTO_X[c], D.PHOTO_X[c + 1], D.PHOTO_Y[r], D.PHOTO_Y[r + 1]
                        ax.add_patch(Rectangle((X0 + .005, Y0 + .01), X1 - X0 - .01, Y1 - Y0 - .02,
                                               fc=GREY(v), ec="none"))
                        ax.text((X0 + X1) / 2, (Y0 + Y1) / 2, f"{v:.2f}", ha="center", va="center",
                                fontsize=7, color="black" if v > 0.55 else "white")
            ax.set_xlim(0, 1)
            ax.set_ylim(1, 0)
            no_frame(ax)
            if j in (0, 1):   # the pin that moves (no target here)
                cell_box(ax, D.PHOTO_X, D.PHOTO_Y, *row["src"], "white", DASH, lw=1.2)
            else:
                cell_box(ax, D.PHOTO_X, D.PHOTO_Y, *row["src"], C["target"], DASH)
                cell_box(ax, D.PHOTO_X, D.PHOTO_Y, *row["dst"], C["target"], "-")
            if i == 0:
                ax.set_title(heads[j], fontsize=8, pad=3)
            if j < 3:
                s, a = row["score"][j], row["alert"][j]
                ax.text(0.0, -0.04, f"max $S$ = {s:.3f}" + ("   alarm" if a else "   no alarm"),
                        transform=ax.transAxes, va="top", fontsize=7.5,
                        color=C["alarm"] if a else "#333333", fontweight="bold" if a else "normal")
            if j == 0:
                ax.set_ylabel(rows[i], fontsize=7.5, labelpad=3)
    cax = fig.add_subplot(gs[:, 4])
    cax.imshow(np.linspace(1, 0, 128)[:, None], cmap=GREY, aspect="auto", extent=(0, 1, 0, 1))
    cax.set_xticks([])
    cax.yaxis.tick_right()
    cax.set_yticks([0, 0.5, 1])
    cax.set_ylabel(r"$|\Delta S|$", fontsize=7.5, rotation=90, labelpad=2)
    cax.yaxis.set_label_position("right")
    fig.text(0.075, 0.965, f"Released composition branch, oracle maps: alarm if max $S > t_s$ = "
             f"{D.T_S['oracle']:.3f}", fontsize=7.5, va="top")
    style.save(fig, "matched_photos")


# ---------------------------------------------------------------------------
def collateral():
    """Fig. 4: share of untouched compartments whose released map changes by more than a cutoff."""
    rec = D.recovered()
    fig, axs = plt.subplots(1, 2, figsize=(style.COL, 1.75), sharey=True,
                            gridspec_kw=dict(wspace=0.12, left=0.2, right=0.98, top=0.74, bottom=0.24))
    names = {"#c75e39": ("Fault", C["fault"]), "#325a87": ("Vacancy only", C["vacancy"]),
             "#178277": ("Valid sham", C["sham"])}
    for k, (ax, key, title) in enumerate(zip(axs, ("collateral_oracle", "collateral_extracted"),
                                             ("Oracle maps", "Extracted maps"))):
        lines = [l for l in rec[key] if l["id"].startswith("line2d")]
        bands = [l for l in rec[key] if l["id"].startswith("Fill")]
        for ln, bd in zip(lines, bands):
            lab, col = names[ln["color"]]
            b = np.array(bd["xy"])
            ax.fill(b[:, 0], b[:, 1], color=col, alpha=0.22, lw=0)
            xy = np.array(ln["xy"])
            ax.plot(xy[:, 0], xy[:, 1], color=col, lw=1.4, label=lab)
        ax.axvline(0.5, color="#999999", lw=0.6, ls=":")
        ax.text(0.52, 0.55, "0.5", fontsize=7, color="#666666")
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.5, 1])
        ax.set_xticklabels(["0", "0.5", "1"])
        ax.set_ylim(-0.02, 1.03)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0", "50%", "100%"])
        ax.set_title(title, fontsize=8, pad=2)
        ax.set_xlabel(r"cutoff on $|\Delta S|$", fontsize=7.5)
        style.panel(ax, "ab"[k], x=0.02, y=1.0)
    axs[0].set_ylabel("untouched compartments\nwith a change > cutoff", fontsize=7.5)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=3, frameon=False, fontsize=7.5, bbox_to_anchor=(0.58, 1.0),
               handlelength=1.4, columnspacing=1.0)
    style.save(fig, "collateral")


# ---------------------------------------------------------------------------
def guidance():
    """Fig. 5: maps with queues, compartment ROC, and recall-cost at the three cutoffs."""
    fig = plt.figure(figsize=(style.FULL, 2.25))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1.2, 1.75], wspace=0.42,
                          left=0.005, right=0.995, top=0.86, bottom=0.2)
    for k, (asset, queued, cut, title) in enumerate([
            ("guidance_maps_0", D.MAP_QUEUED_RELEASED, D.MAP_CUTOFF["released"], "Released"),
            ("guidance_maps_1", D.MAP_QUEUED_FOOTPRINT, D.MAP_CUTOFF["footprint"], "Footprint, seed 1")]):
        ax = fig.add_subplot(gs[k])
        v = style.score_map_values(asset, "draft")
        Hh, Ww = v.shape
        ax.imshow(v, cmap=GREY, vmin=0, vmax=1, extent=(0, 1, 1, 0), interpolation="nearest")
        for r in range(3):
            for c in range(5):
                x0, x1, y0, y1 = D.CELL_X[c], D.CELL_X[c + 1], D.CELL_Y[r], D.CELL_Y[r + 1]
                m = v[int(y0 * Hh):int(y1 * Hh), int(x0 * Ww):int(x1 * Ww)].max()
                ax.text(x0 + 0.015, y1 - 0.015, f"{m:.2f}", fontsize=7, ha="left", va="bottom",
                        color="black", zorder=7,
                        bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.3))
        for c, r in queued:
            cell_box(ax, D.CELL_X, D.CELL_Y, c, r, C["queued"], inset=0.012)
        for c, r in D.MAP_TARGETS:
            cell_box(ax, D.CELL_X, D.CELL_Y, c, r, C["target"], "-", inset=0.012)
        ax.set_xlim(0, 1)
        ax.set_ylim(D.CELL_Y[-1] + 0.02, D.CELL_Y[0] - 0.02)
        no_frame(ax)
        ax.set_title(title, fontsize=8, pad=3)
        ax.text(0.5, D.CELL_Y[-1] + 0.05, f"$t_c$ = {cut:.3f}: {len(queued)} untouched queued",
                ha="center", va="top", fontsize=7.5,
                color=C["queued"] if queued else C["footprint"])
        style.panel(ax, "ab"[k], x=0.0, y=1.02)
    cax = fig.add_axes([0.07, 0.07, 0.24, 0.035])
    cax.imshow(np.linspace(0, 1, 128)[None], cmap=GREY, aspect="auto", extent=(0, 1, 0, 1))
    cax.set_yticks([])
    cax.set_xticks([0, 0.5, 1])
    cax.tick_params(length=2, pad=1)
    cax.text(-0.04, 0.5, "score $S$", transform=cax.transAxes, ha="right", va="center", fontsize=7.5)

    # (c) compartment ROC (recovered curves; legend areas from Tab. 1)
    ax = fig.add_subplot(gs[2])
    rec = D.recovered()["region_curve"]
    names = {"#345c84": ("Released", C["released"], "-", "Released, max"),
             "#16826f": ("Footprint, s1", C["footprint"], "-", "Footprint, seed 1"),
             "#9b4865": ("Footprint, s2", C["footprint"], "--", "Footprint, seed 2")}
    for l in rec:
        lab, col, ls, key = names[l["color"]]
        xy = np.array(l["xy"])
        ax.plot(xy[1:, 0], xy[1:, 1], color=col, ls=ls, lw=1.4,
                label=f"{lab}: {D.INSPECTION_EXTRACTED[key]['area']:.1f}")
    ax.set_xlim(0, 5)
    ax.set_ylim(20, 101)
    ax.set_xlabel("false-compartment rate (%)")
    ax.set_ylabel("target recall (%)")
    ax.legend(loc="lower right", frameon=False, fontsize=7, handlelength=1.6, title="area up to 5%",
              title_fontsize=7)
    ax.set_title("Compartment ROC (test sweep)", fontsize=8)
    style.panel(ax, "c", x=-0.3, y=1.04)

    # (d) recall versus cost at the three development cutoffs, broken x axis
    sub = gs[3].subgridspec(1, 2, width_ratios=[2.3, 1], wspace=0.06)
    axl, axr = fig.add_subplot(sub[0]), fig.add_subplot(sub[1])
    pol = [("Released, max", C["released"], False), ("Class-wide, seed 1", C["classwide"], False),
           ("Class-wide, seed 2", C["classwide"], True), ("Footprint, seed 1", C["footprint"], False),
           ("Footprint, seed 2", C["footprint"], True)]
    mk = {"cost": "s", "95": "o", "98": "^"}
    for name, col, hollow in pol:
        r95, u95 = D.INSPECTION_EXTRACTED[name]["rec"], D.INSPECTION_EXTRACTED[name]["unt"]
        r98, u98, rc, uc = D.OPERATING_EXTRACTED[name]
        for (u, r, m) in ((uc, rc, mk["cost"]), (u95, r95, mk["95"]), (u98, r98, mk["98"])):
            for a in (axl, axr):
                a.plot(u, r, m, color=col, mfc="white" if hollow else col, mew=1.1, ms=4.8, zorder=4)
    for a, lim in ((axl, (-0.05, 1.05)), (axr, (11.0, 13.25))):
        a.set_xlim(*lim)
        a.set_ylim(35, 102)
        a.axhline(95, color="#bbbbbb", lw=0.6, ls=":", zorder=1)
    axl.set_xticks([0, 0.5, 1])
    axl.set_xticklabels(["0", "0.5", "1"])
    axr.set_xticks([11, 12, 13])
    axr.spines["left"].set_visible(False)
    axr.set_facecolor("none")
    axl.set_zorder(3)
    axl.set_facecolor("none")
    axr.tick_params(axis="y", left=False, labelleft=False)
    d = 0.02
    for a, xs in ((axl, (1 - d, 1 + d)), (axr, (-d * 2.3, d * 2.3))):
        a.plot(xs, (-0.03, 0.03), transform=a.transAxes, color="black", lw=0.7, clip_on=False)
    axl.spines["right"].set_visible(False)
    axl.set_ylabel("target recall (%)")
    axl.set_xlabel("untouched compartments queued per fault", x=0.72)
    axl.set_title("Recall vs. cost, three cutoffs", fontsize=8, x=0.68)
    axl.text(0.02, 95.8, "95%", fontsize=7, color="#888888")
    style.panel(axl, "d", x=-0.2, y=1.04)
    hs = [Line2D([], [], color=C["released"], marker="o", ls="", ms=4.5, label="released"),
          Line2D([], [], color=C["classwide"], marker="o", ls="", ms=4.5, label="class-wide"),
          Line2D([], [], color=C["footprint"], marker="o", ls="", ms=4.5, label="footprint"),
          Line2D([], [], color="#555555", marker="o", mfc="white", ls="", ms=4.5, label="hollow: seed 2"),
          Line2D([], [], color="#555555", marker="s", ls="", ms=4.5, label="fixed-cost cutoff"),
          Line2D([], [], color="#555555", marker="o", ls="", ms=4.5, label="95% cutoff"),
          Line2D([], [], color="#555555", marker="^", ls="", ms=4.5, label="98% cutoff")]
    axl.legend(handles=hs, loc="upper left", bbox_to_anchor=(0.46, 0.8), frameon=False, fontsize=7,
               ncol=1, handletextpad=0.2, labelspacing=0.18, borderaxespad=0.1)
    style.save(fig, "guidance_maps")


# ---------------------------------------------------------------------------
def forest():
    """Fig. 6: paired differences, footprint minus each comparator."""
    groups = [("Extracted maps", [("Extracted", s, c) for c in ("classwide", "released") for s in (1, 2)]),
              ("Oracle maps", [("Oracle", s, c) for c in ("classwide", "released") for s in (1, 2)]),
              ("Upstream-only, extracted", [("Extracted", s, "upstream") for s in (1, 2)])]
    rows, ys, heads = [], [], []
    y = 0
    for g, items in groups:
        heads.append((y, g))
        y += 1
        for it in items:
            rows.append(it)
            ys.append(y)
            y += 1
        y += 0.35
    ys = -np.array(ys)
    cols = {"released": C["released"], "classwide": C["classwide"], "upstream": C["upstream"]}
    fig, axs = plt.subplots(1, 3, figsize=(style.FULL, 2.3), sharey=True,
                            gridspec_kw=dict(wspace=0.1, left=0.235, right=0.99, top=0.9, bottom=0.2))
    spec = (("unt", "$\\Delta$ untouched compartments / fault", -1.0, "useful: $\\leq -1$",
             "← fewer (better)", (-14.5, 1.5)),
            ("rec", "$\\Delta$ target recall (pp)", -5.0, "floor: $-5$", "higher is better →", (-8, 8)),
            ("sham", "$\\Delta$ sham alarm rate (pp)", 5.0, "guard: $+5$", "← fewer (better)", (-22, 26)))
    for k, (ax, (key, xl, thr, tl, better, lim)) in enumerate(zip(axs, spec)):
        ax.axvline(0, color="#999999", lw=0.7)
        ax.axvline(thr, color="#777777", lw=0.8, ls=":")
        ax.text(thr, ys.min() - 1.0, (tl + " ") if key == "unt" else (" " + tl), fontsize=7,
                ha="right" if key == "unt" else "left", va="center", color="#555555")
        ax.set_ylim(ys.min() - 1.5, 0.6)
        for yy, (inp, seed, comp) in zip(ys, rows):
            d = D.DELTAS_UPSTREAM[(inp, seed, "classwide")] if comp == "upstream" else D.DELTAS[(inp, seed, comp)]
            e, lo, hi = d[key]
            bad = (key == "sham" and lo > thr) or (key == "rec" and hi < thr) or (key == "unt" and hi > thr)
            style.errbar(ax, yy, e, lo, hi, cols[comp], horizontal=True, ms=4, hollow=seed == 2)
            if bad:
                ax.text(hi + 0.8, yy, "above guard", fontsize=7, va="center", color=C["alarm"])
        ax.set_xlim(*lim)
        ax.set_xlabel(xl)
        ax.text(0.5, -0.28, better, transform=ax.transAxes, ha="center", fontsize=7, color="#666666")
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        style.panel(ax, "abc"[k], x=0.06, y=1.07)
    labels = []
    for inp, seed, comp in rows:
        t = {"released": f"seed {seed} vs. released", "classwide": f"seed {seed} vs. class-wide",
             "upstream": f"seed {seed} vs. class-wide"}[comp]
        if inp == "Extracted" and comp == "classwide":
            t = "primary: " + t
        if comp == "upstream" and seed == 1:
            t += " †"
        labels.append(t)
    axs[0].set_yticks(ys)
    axs[0].set_yticklabels(labels, fontsize=7.5)
    for t, (inp, seed, comp) in zip(axs[0].get_yticklabels(), rows):
        t.set_color(cols[comp])
        if inp == "Extracted" and comp == "classwide":
            t.set_fontweight("bold")
    for yy, g in heads:
        axs[0].text(-0.03, -yy, g, transform=axs[0].get_yaxis_transform(), ha="right", va="center",
                    fontsize=7.5, fontweight="bold")
    style.save(fig, "paired_forest")


# ---------------------------------------------------------------------------
def branches():
    """Fig. 7: which SALAD branch separates a fault from a valid sham."""
    fig = plt.figure(figsize=(style.FULL, 2.05))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.3, 1.15, 1.15, 1.2], wspace=0.45,
                          left=0.0, right=0.99, top=0.78, bottom=0.2)
    sub = gs[0].subgridspec(2, 3, height_ratios=[2.1, 1], hspace=0.12, wspace=0.08)
    tags = [("Source", "cherry icon"), ("Valid sham", "same type"), ("Fault", "other type")]
    for j, (title, tag) in enumerate(tags):
        ax = fig.add_subplot(sub[0, j])
        ax.imshow(rgb(f"juice_rule_{2 * j}"), interpolation="lanczos")
        ax.set_title(title, fontsize=7.5, pad=2, color={0: "#333333", 1: C["sham"], 2: C["fault"]}[j])
        ax.axis("off")
        ax2 = fig.add_subplot(sub[1, j])
        ax2.imshow(rgb(f"juice_rule_{2 * j + 1}"), interpolation="lanczos")
        ax2.axis("off")
        ax2.text(0.5, -0.12, tag, transform=ax2.transAxes, ha="center", va="top", fontsize=7)
        if j == 0:
            style.panel(ax, "a", x=0.1, y=1.12)
    fig.text(0.005, 0.03, "liquid: cherry in all three", fontsize=7, color="#444444")
    br = ["Composition", "Local RGB", "Global RGB", "Fusion"]
    ticks = ["Compo-\nsition", "Local\nRGB", "Global\nRGB", "Fusion"]
    xs = np.arange(len(br))
    wid = 0.26
    for k, (dd, n, title) in enumerate([(D.FULL_PUSHPIN, D.N_PUSHPIN, f"Pushpins (n = {D.N_PUSHPIN})"),
                                       (D.JUICE, D.N_JUICE, f"Juice (n = {D.N_JUICE})")]):
        ax = fig.add_subplot(gs[1 + k])
        for j, arm in enumerate(("src", "sham", "fault")):
            v = [100 * dd[b][arm] / n for b in br]
            ax.bar(xs + (j - 1) * wid, v, wid, color={"src": C["source"], "sham": C["sham"],
                                                      "fault": C["fault"]}[arm])
        ax.axhline(10, color="black", lw=0.7, ls="--")
        ax.set_xticks(xs)
        ax.set_xticklabels(ticks, fontsize=7)
        ax.set_ylim(0, 105)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_ylabel("scenes with an alarm (%)")
        ax.set_title(title, fontsize=8)
        style.panel(ax, "bc"[k], x=-0.22)
    hs = [Patch(color=C["source"], label="source"), Patch(color=C["sham"], label="valid sham"),
          Patch(color=C["fault"], label="fault"),
          Line2D([], [], color="black", ls="--", lw=0.7, label="10% normal cutoff")]
    fig.legend(handles=hs, loc="upper center", ncol=4, frameon=False, fontsize=7.5,
               bbox_to_anchor=(0.6, 1.0), handlelength=1.4, columnspacing=1.0)
    ax = fig.add_subplot(gs[3])
    for j, b in enumerate(br):
        e, lo, hi = D.JUICE[b]["gap"]
        style.errbar(ax, j, e, lo, hi, "black", ms=4)
        ax.text(j, hi + 3, f"{e:+.1f}".replace("-", "\u2212"), fontsize=7, va="bottom", ha="center")
    ax.axhline(0, color="#999999", lw=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(ticks, fontsize=7)
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(-20, 110)
    ax.set_ylabel("fault $-$ sham alarms (pp)")
    ax.set_title("Juice: fault vs. sham", fontsize=8)
    ax.text(0.5, -0.38, "higher = separates the rule", transform=ax.transAxes, ha="center", fontsize=7,
            color="#666666")
    style.panel(ax, "d", x=-0.28)
    style.save(fig, "branches")


# ---------------------------------------------------------------------------
def graph():
    """Fig. 8: graph check (GlaS)."""
    fig, axs = plt.subplots(1, 3, figsize=(style.FULL, 1.7),
                            gridspec_kw=dict(wspace=0.5, left=0.15, right=0.99, top=0.84, bottom=0.27,
                                             width_ratios=[1, 0.85, 1.1]))
    acc = C["alarm"]
    names = list(D.GRAPH_RANK)
    ys = -np.arange(len(names))
    ax = axs[0]
    for y, n in zip(ys, names):
        e, lo, hi = D.GRAPH_RANK[n]
        col = acc if n == "Masked GNN" else "#333333"
        style.errbar(ax, y, e, lo, hi, col, horizontal=True, ms=3.8)
        ax.text(hi + 1.5, y, f"{e:.1f}", va="center", fontsize=7, color=col)
    ax.annotate("", xy=(89.6, -1.5), xytext=(75.5, -1.5),
                arrowprops=dict(arrowstyle="->", color=C["footprint"], lw=0.9))
    ax.text(82.5, -1.58, "+15.3", fontsize=7, color=C["footprint"], ha="center", va="top")
    ax.set_xlim(50, 102)
    ax.set_xticks([50, 75, 100])
    ax.set_yticks(ys)
    ax.set_yticklabels(names, fontsize=7.5)
    ax.set_xlabel("edited-graph AUROC (%)")
    ax.set_title("Rank the switched pairs", fontsize=8)
    ax.tick_params(axis="y", length=0)
    style.panel(ax, "a", x=-0.02, y=1.08)
    ax = axs[1]
    for y, n in zip(ys, names):
        v = D.GRAPH_RESPONSE[n]
        if v is None:
            ax.plot(50, y, "o", mfc="white", mec="#999999", ms=3.8)
            ax.text(53, y, "50 by construction", va="center", fontsize=7, color="#888888")
        else:
            e, lo, hi = v
            style.errbar(ax, y, e, lo, hi, acc, horizontal=True, ms=3.8)
            ax.text(lo - 2, y, f"{e:.1f}", va="center", ha="right", fontsize=7, color=acc)
    ax.axvline(50, color="#bbbbbb", lw=0.6, ls=":")
    ax.set_xlim(45, 102)
    ax.set_xticks([50, 75, 100])
    ax.set_yticks(ys)
    ax.set_yticklabels([])
    ax.set_xlabel("response AUROC (%)")
    ax.set_title("Rank by change", fontsize=8)
    ax.tick_params(axis="y", length=0)
    style.panel(ax, "b", x=-0.06, y=1.08)
    ax = axs[2]
    keys = list(D.GRAPH_TOP4)
    for j, k in enumerate(keys):
        e, lo, hi = D.GRAPH_TOP4[k]
        ax.barh(-j, e, color=acc if j == 0 else "#9a9a9a", height=0.6)
        ax.errorbar(e, -j, xerr=[[e - lo], [hi - e]], color="black", elinewidth=1.1, capsize=2.5,
                    capthick=1.1)
        ax.text(hi + 3, -j, f"{e:.1f}", va="center", fontsize=7)
    ax.set_yticks(-np.arange(len(keys)))
    ax.set_yticklabels(["as fitted", "degree inputs\nheld fixed", "refit, mean\naggregation"], fontsize=7.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("masked GNN top-four recovery (%)")
    ax.set_title("What drives the GNN response", fontsize=8)
    ax.tick_params(axis="y", length=0)
    style.panel(ax, "c", x=-0.02, y=1.08)
    style.save(fig, "graph_audit")


if __name__ == "__main__":
    photos()
    collateral()
    guidance()
    forest()
    branches()
    graph()
