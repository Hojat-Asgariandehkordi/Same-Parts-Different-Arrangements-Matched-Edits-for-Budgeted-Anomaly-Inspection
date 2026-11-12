"""Result figures of the main paper. All numbers come from scripts/data.py.

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
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

C = style.C
A = style.FIG / "assets"


def rgb(name):
    return np.asarray(Image.open(A / f"{name}.png").convert("RGB"))


def map_cmap():
    bar = rgb("guidance_maps_2")[5]  # middle row of the draft's colour bar
    return ListedColormap(bar / 255.0)


# ---------------------------------------------------------------------------
def guidance():
    """Fig.: maps with queues, region curve and recall-cost operating points."""
    fig = plt.figure(figsize=(style.FULL, 1.85))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1.25, 1.25], wspace=0.42,
                          left=0.01, right=0.995, top=0.86, bottom=0.2)
    for k, (asset, queued, cut, title) in enumerate([
            ("guidance_maps_0", D.MAP_QUEUED_RELEASED, D.MAP_CUTOFF["released"], "Released map"),
            ("guidance_maps_1", D.MAP_QUEUED_FOOTPRINT, D.MAP_CUTOFF["footprint"], "Footprint map, seed 1")]):
        ax = fig.add_subplot(gs[k])
        im = rgb(asset)
        ax.imshow(im, extent=(0, 1, 1, 0), interpolation="lanczos")
        for cells, col, ls in ((queued, C["queued"], "-"), (D.MAP_TARGETS, C["target"], "-")):
            for c, r in cells:
                x0, x1 = D.CELL_X[c], D.CELL_X[c + 1]
                y0, y1 = D.CELL_Y[r], D.CELL_Y[r + 1]
                ax.add_patch(Rectangle((x0 + .006, y0 + .006), x1 - x0 - .012, y1 - y0 - .012,
                                       fc="none", ec=col, lw=1.1, ls=ls))
        ax.set_xlim(0, 1)
        ax.set_ylim(D.CELL_Y[-1] + 0.04, D.CELL_Y[0] - 0.04)
        ax.axis("off")
        ax.set_title(title, fontsize=8)
        n_q = len(queued)
        ax.text(0.5, D.CELL_Y[-1] + 0.07, f"cutoff $t_c$ = {cut:.3f}; {n_q} untouched queued",
                ha="center", va="top", fontsize=6.6)
        style.panel(ax, "abcd"[k], x=0.0, y=1.06)
    # colour bar under (a)-(b)
    cax = fig.add_axes([0.06, 0.06, 0.3, 0.03])
    cax.imshow(np.linspace(0, 1, 256)[None], aspect="auto", cmap=map_cmap(), extent=(0, 1, 0, 1))
    cax.set_yticks([])
    cax.set_xticks([0, 0.5, 1])
    cax.tick_params(length=2, pad=1)
    cax.set_xlabel("map score", fontsize=6.6, labelpad=1)

    # (c) region curve, RECOVERED from the draft figure
    ax = fig.add_subplot(gs[2])
    rec = D.recovered()["region_curve"]
    names = {"#345c84": ("Released", C["released"], "-"),
             "#16826f": ("Footprint, seed 1", C["footprint"], "-"),
             "#9b4865": ("Footprint, seed 2", C["footprint2"], "--")}
    for l in rec:
        lab, col, ls = names[l["color"]]
        xy = np.array(l["xy"])
        area = np.trapezoid(xy[:, 1], xy[:, 0]) / 5
        ax.plot(xy[:, 0], xy[:, 1], color=col, ls=ls, lw=1.3, label=f"{lab} ({area:.1f})")
    ax.set_xlim(0, 5)
    ax.set_ylim(45, 101)
    ax.set_xlabel("False cell rate (%)")
    ax.set_ylabel("Target-cell recall (%)")
    ax.legend(loc="lower right", frameon=False, fontsize=6.2, handlelength=1.6,
              title="area to 5%", title_fontsize=6.2)
    ax.set_title("Low-FPR region curve", fontsize=8)
    style.panel(ax, "c", x=-0.18)

    # (d) recall versus untouched cells at the three development cutoffs
    ax = fig.add_subplot(gs[3])
    pol = [("Released, max", C["released"], "o", "Released"),
           ("Class-wide, seed 1", C["classwide"], "s", "Class-wide, s1"),
           ("Footprint, seed 1", C["footprint"], "D", "Footprint, s1"),
           ("Footprint, seed 2", C["footprint2"], "^", "Footprint, s2")]
    for name, col, mk, lab in pol:
        r95, u95 = D.INSPECTION_EXTRACTED[name]["rec"], D.INSPECTION_EXTRACTED[name]["unt"]
        r98, u98, rc, uc = D.OPERATING_EXTRACTED[name]
        pts = sorted([(uc, rc), (u95, r95), (u98, r98)])
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=0.8, alpha=0.6)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], mk, color=col, ms=4, label=lab,
                mec="white", mew=0.4)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xlim(0, 15)
    ax.set_xticks([0, 0.5, 1, 5, 13])
    ax.set_xticklabels(["0", "0.5", "1", "5", "13"])
    ax.set_ylim(35, 102)
    ax.set_xlabel("Untouched cells queued per fault")
    ax.set_ylabel("Target recall (%)")
    ax.set_title("Three development cutoffs", fontsize=8)
    ax.legend(loc="lower right", frameon=False, fontsize=6.2, handlelength=1.0)
    style.panel(ax, "d", x=-0.18)
    style.save(fig, "guidance_maps")


# ---------------------------------------------------------------------------
def forest():
    """Fig.: paired differences, footprint minus each comparator (from the supplement)."""
    rows = []
    for inp in ("Extracted", "Oracle"):
        for comp in ("released", "classwide"):
            for seed in (1, 2):
                rows.append((inp, seed, comp, D.DELTAS[(inp, seed, comp)]))
    for seed in (1, 2):
        rows.append(("Extracted", seed, "upstream", D.DELTAS_UPSTREAM[("Extracted", seed, "classwide")]))
    fig, axs = plt.subplots(1, 3, figsize=(style.FULL, 2.05), sharey=True,
                            gridspec_kw=dict(wspace=0.08, left=0.255, right=0.99, top=0.84, bottom=0.17))
    ys = []
    y = 0
    labels = []
    for k, (inp, seed, comp, d) in enumerate(rows):
        if k in (4, 8):
            y += 0.7
        ys.append(y)
        cname = {"released": "vs. released", "classwide": "vs. class-wide",
                 "upstream": "vs. class-wide, upstream-only"}[comp]
        labels.append(f"{inp}, seed {seed}  {cname}")
        y += 1
    ys = -np.array(ys)
    cols = {"released": C["released"], "classwide": C["classwide"], "upstream": "#8a6bb5"}
    for ax, key, xl, guard in zip(axs, ("unt", "rec", "sham"),
                                  ("Untouched cells per fault", "Target recall (pp)",
                                   "Valid-sham alerts (pp)"),
                                  (-1.0, -5.0, 5.0)):
        ax.axvline(0, color="#999999", lw=0.7)
        ax.axvline(guard, color="#999999", lw=0.7, ls=":")
        for yy, (inp, seed, comp, d) in zip(ys, rows):
            e, lo, hi = d[key]
            style.errbar(ax, yy, e, lo, hi, cols[comp], horizontal=True, ms=3.6,
                         marker="o" if inp == "Extracted" else "s", mec="white", mew=0.3)
        ax.set_xlabel(xl)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    axs[0].set_xlim(-14, 1)
    axs[1].set_xlim(-8, 8)
    axs[2].set_xlim(-22, 22)
    axs[0].text(-1.0, 0.65, "useful: $-1$", fontsize=6, ha="center", color="#555555")
    axs[1].text(-5.0, 0.65, "floor: $-5$", fontsize=6, ha="center", color="#555555")
    axs[2].text(5.0, 0.65, "guard: $+5$", fontsize=6, ha="center", color="#555555")
    axs[0].set_yticks(ys)
    axs[0].set_yticklabels(labels, fontsize=6.6)
    for t, (inp, seed, comp, d) in zip(axs[0].get_yticklabels(), rows):
        t.set_color(cols[comp])
    fig.text(0.255, 0.955, "Footprint minus comparator, paired 95% intervals (4,000 photo resamples); "
             "circles = extracted maps, squares = oracle maps", fontsize=6.8, va="bottom")
    style.save(fig, "paired_forest")


# ---------------------------------------------------------------------------
def collateral():
    """Fig.: share of untouched cells whose released map changes by >= a cutoff."""
    rec = D.recovered()
    fig, axs = plt.subplots(1, 2, figsize=(style.COL, 1.45), sharey=True,
                            gridspec_kw=dict(wspace=0.1, left=0.14, right=0.99, top=0.86, bottom=0.27))
    names = {"#c75e39": ("Fault", C["fault"]), "#325a87": ("Vacancy only", C["vacancy"]),
             "#178277": ("Valid sham", C["sham"])}
    for ax, key, title in zip(axs, ("collateral_oracle", "collateral_extracted"),
                              ("Oracle maps", "Extracted maps")):
        lines = [l for l in rec[key] if l["id"].startswith("line2d")]
        bands = [l for l in rec[key] if l["id"].startswith("Fill")]
        for ln, bd in zip(lines, bands):
            lab, col = names[ln["color"]]
            b = np.array(bd["xy"])
            ax.fill(b[:, 0], b[:, 1], color=col, alpha=0.22, lw=0)
            xy = np.array(ln["xy"])
            ax.plot(xy[:, 0], xy[:, 1], color=col, lw=1.3, label=lab)
        ax.axvline(0.5, color="#999999", lw=0.6, ls=":")
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.5, 1])
        ax.set_xticklabels(["0", "0.5", "1"])
        ax.set_ylim(-0.02, 1.03)
        ax.set_title(title, fontsize=7.6, pad=2)
        ax.set_xlabel("Cutoff on |change|", fontsize=7)
    axs[0].set_ylabel("Untouched cells", fontsize=7)
    axs[1].legend(frameon=False, fontsize=6, loc="center left", bbox_to_anchor=(0.0, 0.45),
                  handlelength=1.2)
    style.save(fig, "collateral")


# ---------------------------------------------------------------------------
def branches():
    """Fig.: which SALAD branch separates fault from valid sham (pushpins, juice)."""
    fig = plt.figure(figsize=(style.FULL, 1.75))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.25, 1.15, 1.15, 0.95], wspace=0.4,
                          left=0.0, right=0.99, top=0.84, bottom=0.2)
    # (a) juice edit, photos from the draft's figure
    sub = gs[0].subgridspec(2, 3, height_ratios=[2.1, 1], hspace=0.05, wspace=0.08)
    for j, title in enumerate(["Source", "Valid sham", "Fault"]):
        ax = fig.add_subplot(sub[0, j])
        ax.imshow(rgb(f"juice_rule_{2 * j}"), interpolation="lanczos")
        ax.set_title(title, fontsize=7, pad=2)
        ax.axis("off")
        ax2 = fig.add_subplot(sub[1, j])
        ax2.imshow(rgb(f"juice_rule_{2 * j + 1}"), interpolation="lanczos")
        ax2.axis("off")
        if j == 0:
            style.panel(ax, "a", x=0.1, y=1.12)
    br = ["Composition", "Local RGB", "Global RGB", "Fusion"]
    xs = np.arange(len(br))
    wid = 0.26
    for k, (dd, n, title) in enumerate([(D.FULL_PUSHPIN, D.N_PUSHPIN, "Pushpins: alerts of 138"),
                                       (D.JUICE, D.N_JUICE, "Juice: alerts of 89")]):
        ax = fig.add_subplot(gs[1 + k])
        for j, (arm, col) in enumerate((("src", C["source"]), ("sham", C["sham"]),
                                        ("fault", C["fault"]))):
            v = [100 * dd[b][arm] / n for b in br]
            ax.bar(xs + (j - 1) * wid, v, wid, color=col,
                   label={"src": "Source", "sham": "Valid sham", "fault": "Fault"}[arm])
        ax.set_xticks(xs)
        ax.set_xticklabels(["Comp.", "Local\nRGB", "Global\nRGB", "Fusion"], fontsize=6.6)
        ax.set_ylim(0, 132)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_ylabel("Scenes alerted (%)")
        ax.set_title(title, fontsize=8)
        style.panel(ax, "bc"[k], x=-0.2)
        if k == 0:
            ax.legend(frameon=False, fontsize=6, loc="upper left", ncol=3, handlelength=0.8,
                      columnspacing=0.6, borderaxespad=0.1)
    ax = fig.add_subplot(gs[3])
    for j, b in enumerate(br):
        e, lo, hi = D.JUICE[b]["gap"]
        style.errbar(ax, j, e, lo, hi, C["released"], ms=3.8)
        ax.text(j + 0.16, e, f"{e:+.1f}", fontsize=6, va="center")
    ax.axhline(0, color="#999999", lw=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(["Comp.", "Local\nRGB", "Global\nRGB", "Fusion"], fontsize=6.6)
    ax.set_xlim(-0.5, 3.6)
    ax.set_ylim(-20, 100)
    ax.set_ylabel("Fault $-$ sham (pp)")
    ax.set_title("Juice: alert gap", fontsize=8)
    style.panel(ax, "d", x=-0.25)
    style.save(fig, "branches")


# ---------------------------------------------------------------------------
def graph():
    """Fig.: graph check (GlaS), redrawn from the draft's graph_audit figure."""
    fig, axs = plt.subplots(1, 3, figsize=(style.FULL, 1.45),
                            gridspec_kw=dict(wspace=0.55, left=0.12, right=0.99, top=0.82, bottom=0.27,
                                             width_ratios=[1, 1, 1.1]))
    names = list(D.GRAPH_RANK)
    ys = -np.arange(len(names))
    for ax, dd, title in ((axs[0], D.GRAPH_RANK, "Rank in the edited graph"),
                          (axs[1], D.GRAPH_RESPONSE, "Rank by matched response")):
        for y, n in zip(ys, names):
            e, lo, hi = dd[n]
            col = C["classwide"] if n == "Masked GNN" else C["released"]
            style.errbar(ax, y, e, lo, hi, col, horizontal=True, ms=3.6)
            ax.text(min(hi, 99) + 2, y, f"{e:.1f}", va="center", fontsize=6.4, color=col)
        ax.axvline(50, color="#999999", lw=0.6, ls=":")
        ax.set_xlim(45, 112)
        ax.set_xticks([50, 75, 100])
        ax.set_yticks(ys)
        ax.set_yticklabels(names if ax is axs[0] else [], fontsize=6.8)
        ax.set_xlabel("Target AUROC (%)")
        ax.set_title(title, fontsize=8)
        ax.tick_params(axis="y", length=0)
    style.panel(axs[0], "a", x=-0.05)
    style.panel(axs[1], "b", x=-0.05)
    ax = axs[2]
    keys = list(D.GRAPH_TOP4)
    cols = [C["classwide"], C["released"], C["footprint"]]
    for j, (k, col) in enumerate(zip(keys, cols)):
        e, lo, hi = D.GRAPH_TOP4[k]
        ax.barh(-j, e, color=col, height=0.6)
        ax.errorbar(e, -j, xerr=[[e - lo], [hi - e]], color="black", elinewidth=1.1, capsize=2.5,
                    capthick=1.1)
        ax.text(hi + 2, -j, f"{e:.1f}", va="center", fontsize=6.4)
    ax.set_yticks(-np.arange(len(keys)))
    ax.set_yticklabels(keys, fontsize=6.8)
    ax.set_xlim(0, 110)
    ax.set_xlabel("GNN top-four recovery (%)")
    ax.set_title("What drives the GNN response", fontsize=8)
    ax.tick_params(axis="y", length=0)
    style.panel(ax, "c", x=-0.05)
    style.save(fig, "graph_audit")


if __name__ == "__main__":
    guidance()
    forest()
    collateral()
    branches()
    graph()


def photos():
    """Fig.: real matched edits and the released composition response."""
    fig, axs = plt.subplots(2, 4, figsize=(style.FULL, 2.12),
                            gridspec_kw=dict(wspace=0.04, hspace=0.22, left=0.035, right=0.995,
                                             top=0.92, bottom=0.07))
    heads = ["Source", "Valid sham", "Placement fault", r"|fault $-$ source|, cell maxima"]
    for i, row in enumerate(D.PHOTO_ROWS):
        for j in range(4):
            ax = axs[i, j]
            ax.imshow(rgb(f"pushpin_intervention_{4 * i + j}"), extent=(0, 1, 1, 0),
                      interpolation="lanczos", aspect="auto")
            ax.set_xlim(0, 1)
            ax.set_ylim(1, 0)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
            boxes = []
            if j in (0, 1):
                boxes = [(row["src"], C["target"], "-")]
            else:
                boxes = [(row["src"], C["target"], (0, (2, 1.2))), (row["dst"], C["target"], "-")]
            for (c, r), col, ls in boxes:
                x0, x1 = D.PHOTO_X[c], D.PHOTO_X[c + 1]
                y0, y1 = D.PHOTO_Y[r], D.PHOTO_Y[r + 1]
                ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec=col, lw=1.2, ls=ls))
            if i == 0:
                ax.set_title(heads[j], fontsize=8, pad=3)
            if j < 3:
                s, a = row["score"][j], row["alert"][j]
                ax.text(0.0, -0.03, f"scene score {s:.3f}" + ("  (alert)" if a else ""),
                        transform=ax.transAxes, va="top", fontsize=6.6,
                        color=C["classwide"] if a else "#333333")
        axs[i, 0].set_ylabel(row["title"], fontsize=7)
    style.save(fig, "matched_photos")


if __name__ == "__main__":
    photos()
