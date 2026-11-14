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
    fig = plt.figure(figsize=(style.FULL, 2.05))
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
    fig, axs = plt.subplots(1, 2, figsize=(style.COL, 1.62), sharey=True,
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
        style.panel(ax, "ab"[k], x=-0.02, y=1.06)
    axs[0].set_ylabel("untouched compartments\nwith a change > cutoff", fontsize=7.5)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=3, frameon=False, fontsize=7.5, bbox_to_anchor=(0.58, 1.0),
               handlelength=1.4, columnspacing=1.0)
    style.save(fig, "collateral")


# ---------------------------------------------------------------------------
def guidance():
    """Fig. 5 (one column): maps with queues, compartment ROC, recall vs. cost at three cutoffs."""
    fig = plt.figure(figsize=(style.COL, 3.3))
    top = fig.add_gridspec(1, 2, left=0.01, right=0.99, top=0.94, bottom=0.68, wspace=0.08)
    for k, (asset, queued, cut, title) in enumerate([
            ("guidance_maps_0", D.MAP_QUEUED_RELEASED, D.MAP_CUTOFF["released"], "Released"),
            ("guidance_maps_1", D.MAP_QUEUED_FOOTPRINT, D.MAP_CUTOFF["footprint"], "Footprint, seed 1")]):
        ax = fig.add_subplot(top[k])
        v = style.score_map_values(asset, "draft")
        ax.imshow(v, cmap=GREY, vmin=0, vmax=1, extent=(0, 1, 1, 0), interpolation="nearest")
        for c, r in queued:
            cell_box(ax, D.CELL_X, D.CELL_Y, c, r, C["queued"], inset=0.012)
        for c, r in D.MAP_TARGETS:
            cell_box(ax, D.CELL_X, D.CELL_Y, c, r, C["target"], "-", inset=0.012)
        ax.set_xlim(0, 1)
        ax.set_ylim(D.CELL_Y[-1] + 0.02, D.CELL_Y[0] - 0.02)
        no_frame(ax)
        ax.set_title(title, fontsize=8, pad=2)
        ax.text(0.5, D.CELL_Y[-1] + 0.05, f"$t_c$ = {cut:.3f}: {len(queued)} untouched queued",
                ha="center", va="top", fontsize=7.5, color=C["queued"] if queued else C["footprint"])
        style.panel(ax, "ab"[k], x=0.08, y=1.0)
    cax = fig.add_axes([0.62, 0.615, 0.3, 0.017])
    cax.imshow(np.linspace(0, 1, 128)[None], cmap=GREY, aspect="auto", extent=(0, 1, 0, 1))
    cax.set_yticks([])
    cax.set_xticks([0, 0.5, 1])
    cax.set_xticklabels(["0", "0.5", "1"])
    cax.tick_params(length=2, pad=1)
    cax.text(-0.04, 0.5, "score $S$", transform=cax.transAxes, ha="right", va="center", fontsize=7.5)

    bot = fig.add_gridspec(1, 3, width_ratios=[1.0, 0.82, 0.36], left=0.13, right=0.99, top=0.5,
                           bottom=0.27, wspace=0.12)
    # (c) compartment ROC (recovered curves; legend areas from Tab. 1)
    ax = fig.add_subplot(bot[0])
    rec = D.recovered()["region_curve"]
    names = {"#345c84": ("released", C["released"], "-", "Released, max"),
             "#16826f": ("footprint, s1", C["footprint"], "-", "Footprint, seed 1"),
             "#9b4865": ("footprint, s2", C["footprint"], "--", "Footprint, seed 2")}
    for l in rec:
        lab, col, ls, key = names[l["color"]]
        xy = np.array(l["xy"])
        ax.plot(xy[1:, 0], xy[1:, 1], color=col, ls=ls, lw=1.3,
                label=f"{D.INSPECTION_EXTRACTED[key]['area']:.1f}")
    ax.set_xlim(0, 5)
    ax.set_ylim(20, 101)
    ax.set_xlabel("false-compartment rate (%)")
    ax.set_ylabel("target recall (%)")
    ax.legend(loc="lower right", frameon=False, fontsize=7, handlelength=1.5, title="area to 5%",
              title_fontsize=7)
    ax.set_title("Compartment ROC", fontsize=8)
    style.panel(ax, "c", x=-0.3, y=1.04)
    # (d) recall versus cost at three development cutoffs, broken x axis
    axl, axr = fig.add_subplot(bot[1]), fig.add_subplot(bot[2])
    pol = [("Released, max", C["released"], False), ("Class-wide, seed 1", C["classwide"], False),
           ("Class-wide, seed 2", C["classwide"], True), ("Footprint, seed 1", C["footprint"], False),
           ("Footprint, seed 2", C["footprint"], True)]
    mk = {"cost": "s", "95": "o", "98": "^"}
    for name, col, hollow in pol:
        r95, u95 = D.INSPECTION_EXTRACTED[name]["rec"], D.INSPECTION_EXTRACTED[name]["unt"]
        r98, u98, rc, uc = D.OPERATING_EXTRACTED[name]
        for (u, r, m) in ((uc, rc, mk["cost"]), (u95, r95, mk["95"]), (u98, r98, mk["98"])):
            for a_ in (axl, axr):
                a_.plot(u, r, m, color=col, mfc="white" if hollow else col, mew=1.0, ms=4.2, zorder=4)
    for a_, lim in ((axl, (-0.05, 1.05)), (axr, (10.8, 13.3))):
        a_.set_xlim(*lim)
        a_.set_ylim(20, 101)
        a_.axhline(95, color="#bbbbbb", lw=0.6, ls=":", zorder=1)
    axl.set_xticks([0, 0.5, 1])
    axl.set_xticklabels(["0", "0.5", "1"])
    axr.set_xticks([11, 13])
    axr.spines["left"].set_visible(False)
    axr.tick_params(axis="y", left=False, labelleft=False)
    axr.set_facecolor("none")
    d = 0.03
    for a_, xs in ((axl, (1 - d, 1 + d)), (axr, (-d * 2.3, d * 2.3))):
        a_.plot(xs, (-0.03, 0.03), transform=a_.transAxes, color="black", lw=0.7, clip_on=False)
    axl.spines["right"].set_visible(False)
    axl.set_yticklabels([])
    axl.set_xlabel("untouched per fault", x=0.7)
    axl.set_title("Recall vs. cost", fontsize=8, x=0.7)
    axr.text(11.9, 91.5, "95%", fontsize=7, color="#888888", ha="center", va="top")
    style.panel(axl, "d", x=-0.06, y=1.04)
    hs = [Line2D([], [], color=C["released"], lw=2.0, label="released"),
          Line2D([], [], color=C["classwide"], lw=2.0, label="class-wide"),
          Line2D([], [], color=C["footprint"], lw=2.0, label="footprint"),
          Line2D([], [], color="#555555", ls="--", lw=1.2, label="seed 2 (dashed / hollow)"),
          Line2D([], [], color="#555555", marker="s", ls="", ms=4, label="fixed-cost cutoff"),
          Line2D([], [], color="#555555", marker="o", ls="", ms=4, label="95% cutoff"),
          Line2D([], [], color="#555555", marker="^", ls="", ms=4, label="98% cutoff")]
    fig.legend(handles=hs, loc="lower center", bbox_to_anchor=(0.53, 0.0), ncol=3, frameon=False,
               fontsize=7, handlelength=1.4, columnspacing=0.8, labelspacing=0.2)
    style.save(fig, "guidance_maps")


# ---------------------------------------------------------------------------
def forest():
    """Fig. 6 (one column): paired differences on extracted maps, footprint minus each comparator.

    Oracle-map rows are in supplement Tab. 3 and quoted in the text.
    """
    groups = [("Rule-aware fine-tuning", [("Extracted", s_, c) for c in ("classwide", "released") for s_ in (1, 2)]),
              ("Upstream-only continuation", [("Extracted", s_, "upstream") for s_ in (1, 2)])]
    rows, ys, heads = [], [], []
    y = 0
    for g, items in groups:
        heads.append((y, g))
        y += 1
        for it in items:
            rows.append(it)
            ys.append(y)
            y += 1
        y += 0.3
    ys = -np.array(ys)
    cols = {"released": C["released"], "classwide": C["classwide"], "upstream": C["upstream"]}
    fig, axs = plt.subplots(1, 3, figsize=(style.COL, 2.1), sharey=True,
                            gridspec_kw=dict(wspace=0.14, left=0.355, right=0.985, top=0.86, bottom=0.17))
    spec = (("unt", "$\\Delta$ untouched", -1.0, (-14.5, 1.5), [-10, 0]),
            ("rec", "$\\Delta$ recall (pp)", -5.0, (-8, 8), [-5, 0, 5]),
            ("sham", "$\\Delta$ sham (pp)", 5.0, (-22, 22), [-20, 0, 20]))
    for k, (ax, (key, xl, thr, lim, tk)) in enumerate(zip(axs, spec)):
        ax.axvline(0, color="#999999", lw=0.7)
        ax.axvline(thr, color="#777777", lw=0.8, ls=":")
        for yy, (inp, seed, comp) in zip(ys, rows):
            d = D.DELTAS_UPSTREAM[(inp, seed, "classwide")] if comp == "upstream" else D.DELTAS[(inp, seed, comp)]
            e, lo, hi = d[key]
            style.errbar(ax, yy, e, lo, hi, cols[comp], horizontal=True, ms=3.6, hollow=seed == 2)
        ax.set_xlim(*lim)
        ax.set_xticks(tk)
        ax.set_xlabel(xl, fontsize=7.5)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    labels = []
    for inp, seed, comp in rows:
        t = {"released": f"seed {seed} vs. released", "classwide": f"seed {seed} vs. class-wide",
             "upstream": f"seed {seed} vs. class-wide"}[comp]
        if comp == "upstream" and seed == 1:
            t += " \u2020"
        labels.append(t)
    axs[0].set_yticks(ys)
    axs[0].set_yticklabels(labels, fontsize=7.5)
    for t, (inp, seed, comp) in zip(axs[0].get_yticklabels(), rows):
        t.set_color(cols[comp])
        if comp == "classwide":
            t.set_fontweight("bold")
    for yy, g in heads:
        axs[0].text(-0.06, -yy, g, transform=axs[0].get_yaxis_transform(), ha="right", va="center",
                    fontsize=7.5, fontstyle="italic")
    style.save(fig, "paired_forest")


# ---------------------------------------------------------------------------
def branches():
    """Fig. 7 (one column): which SALAD branch separates a fault from a valid sham."""
    fig = plt.figure(figsize=(style.COL, 2.9))
    gs = fig.add_gridspec(2, 2, left=0.13, right=0.99, top=0.89, bottom=0.12, wspace=0.5, hspace=0.72)
    sub = gs[0, 0].subgridspec(2, 3, height_ratios=[2.1, 1], hspace=0.1, wspace=0.06)
    tags = [("Source", "cherry"), ("Valid sham", "same"), ("Fault", "other")]
    for j, (title, tag) in enumerate(tags):
        ax = fig.add_subplot(sub[0, j])
        ax.imshow(rgb(f"juice_rule_{2 * j}"), interpolation="lanczos")
        ax.set_title(title, fontsize=7, pad=2, color={0: "#333333", 1: C["sham"], 2: C["fault"]}[j])
        ax.axis("off")
        ax2 = fig.add_subplot(sub[1, j])
        ax2.imshow(rgb(f"juice_rule_{2 * j + 1}"), interpolation="lanczos")
        ax2.axis("off")
        ax2.text(0.5, -0.12, tag, transform=ax2.transAxes, ha="center", va="top", fontsize=7)
        if j == 0:
            style.panel(ax, "a", x=-0.05, y=1.2)
    br = ["Composition", "Local RGB", "Global RGB", "Fusion"]
    ticks = ["Comp.", "Local", "Global", "Fusion"]
    xs = np.arange(len(br))
    wid = 0.27
    for k, (dd, n, title, cell) in enumerate([(D.FULL_PUSHPIN, D.N_PUSHPIN, f"Pushpins (n = {D.N_PUSHPIN})", gs[0, 1]),
                                             (D.JUICE, D.N_JUICE, f"Juice (n = {D.N_JUICE})", gs[1, 0])]):
        ax = fig.add_subplot(cell)
        for j, arm in enumerate(("src", "sham", "fault")):
            v = [100 * dd[b_][arm] / n for b_ in br]
            ax.bar(xs + (j - 1) * wid, v, wid, color={"src": C["source"], "sham": C["sham"],
                                                      "fault": C["fault"]}[arm])
        ax.axhline(10, color="black", lw=0.7, ls="--")
        ax.set_xticks(xs)
        ax.set_xticklabels(ticks, fontsize=7, rotation=30, ha="right", rotation_mode="anchor")
        ax.set_ylim(0, 105)
        ax.set_yticks([0, 50, 100])
        ax.set_ylabel("alarmed (%)")
        ax.set_title(title, fontsize=8, pad=3)
        style.panel(ax, "bc"[k], x=-0.36, y=1.06)
    ax = fig.add_subplot(gs[1, 1])
    for j, b_ in enumerate(br):
        e, lo, hi = D.JUICE[b_]["gap"]
        style.errbar(ax, j, e, lo, hi, "black", ms=3.6)
        ax.text(j, hi + 4, f"{e:+.1f}".replace("-", "\u2212"), fontsize=7, va="bottom", ha="center")
    ax.axhline(0, color="#999999", lw=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(ticks, fontsize=7, rotation=30, ha="right", rotation_mode="anchor")
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(-20, 112)
    ax.set_yticks([0, 50, 100])
    ax.set_ylabel("fault $-$ sham (pp)")
    ax.set_title("Juice: alarm gap", fontsize=8, pad=3)
    style.panel(ax, "d", x=-0.3, y=1.04)
    hs = [Patch(color=C["source"], label="source"), Patch(color=C["sham"], label="valid sham"),
          Patch(color=C["fault"], label="fault"),
          Line2D([], [], color="black", ls="--", lw=0.7, label="10% normal cutoff")]
    fig.legend(handles=hs, loc="upper center", ncol=4, frameon=False, fontsize=7,
               bbox_to_anchor=(0.55, 1.0), handlelength=1.2, columnspacing=0.7)
    style.save(fig, "branches")


# ---------------------------------------------------------------------------
def graph():
    """Fig. 8 (one column): graph check (GlaS)."""
    fig = plt.figure(figsize=(style.COL, 2.45))
    gs = fig.add_gridspec(2, 2, left=0.33, right=0.97, top=0.92, bottom=0.12, wspace=0.28, hspace=0.75,
                          height_ratios=[1.35, 0.85])
    acc = "black"
    names = list(D.GRAPH_RANK)
    ys = -np.arange(len(names))
    ax = fig.add_subplot(gs[0, 0])
    for y, n in zip(ys, names):
        e, lo, hi = D.GRAPH_RANK[n]
        col = acc if n == "Masked GNN" else "#8a8a8a"
        style.errbar(ax, y, e, lo, hi, col, horizontal=True, ms=3.4)
    ax.annotate("", xy=(90.2, -1.5), xytext=(74.9, -1.5),
                arrowprops=dict(arrowstyle="->", color=C["calib"], lw=1.0))
    ax.text(82.5, -1.62, "+15.3", fontsize=7, color=C["calib"], ha="center", va="top")
    ax.set_xlim(55, 100)
    ax.set_xticks([60, 80, 100])
    ax.set_yticks(ys)
    ax.set_yticklabels(names, fontsize=7.5)
    ax.set_xlabel("AUROC (%)")
    ax.set_title("Edited graph", fontsize=8, pad=3)
    ax.tick_params(axis="y", length=0)
    style.panel(ax, "a", x=-0.02, y=1.03)
    ax = fig.add_subplot(gs[0, 1])
    for y, n in zip(ys, names):
        v = D.GRAPH_RESPONSE[n]
        if v is None:
            ax.plot(50, y, "o", mfc="white", mec="#999999", ms=3.4)
        else:
            e, lo, hi = v
            style.errbar(ax, y, e, lo, hi, acc, horizontal=True, ms=3.4)
    ax.text(53, -1.5, "50 by\nconstruction", fontsize=7, color="#888888", va="center")
    ax.axvline(50, color="#bbbbbb", lw=0.6, ls=":")
    ax.set_xlim(45, 102)
    ax.set_xticks([50, 75, 100])
    ax.set_yticks(ys)
    ax.set_yticklabels([])
    ax.set_xlabel("AUROC (%)")
    ax.set_title("By change", fontsize=8, pad=3)
    ax.tick_params(axis="y", length=0)
    style.panel(ax, "b", x=-0.08, y=1.03)
    ax = fig.add_subplot(gs[1, :])
    keys = list(D.GRAPH_TOP4)
    for j, k in enumerate(keys):
        e, lo, hi = D.GRAPH_TOP4[k]
        ax.barh(-j, e, color=acc if j == 0 else "#a8a8a8", height=0.6)
        ax.errorbar(e, -j, xerr=[[e - lo], [hi - e]], color="#444444", elinewidth=1.1, capsize=2.5,
                    capthick=1.1)
        ax.text(hi + 2, -j, f"{e:.1f}", va="center", fontsize=7)
    ax.set_yticks(-np.arange(len(keys)))
    ax.set_yticklabels(["GNN as fitted", "degree inputs fixed", "refit, mean aggregation"], fontsize=7.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("masked GNN top-four recovery (%)")
    ax.tick_params(axis="y", length=0)
    style.panel(ax, "c", x=-0.02, y=1.05)
    style.save(fig, "graph_audit")


if __name__ == "__main__":
    photos()
    collateral()
    guidance()
    forest()
    branches()
    graph()
