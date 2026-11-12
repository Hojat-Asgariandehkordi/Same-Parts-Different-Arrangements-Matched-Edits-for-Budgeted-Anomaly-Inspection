"""Recover plotted data and photo crops from the original draft's figures.

The draft's region-overlap curve (guidance_maps.svg) and collateral curves
(collateral.svg) were never printed as numbers. This script reads their
vector geometry, maps it back to data units with the tick labels, and writes
scripts/recovered.json. Values are accurate to the SVG precision (~0.1 pt);
replace them with the analysis output when available.

It also extracts the embedded photo/map rasters (figures/orig/*.svg) into
figures/assets/ so the rebuilt figures can reuse them. The originals are
small (82-159 px); see REVISION_NOTES.md for how to export full resolution.

Usage: python -I scripts/recover_vector.py figures/orig
"""
import base64
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

S = "{http://www.w3.org/2000/svg}"
XL = "{http://www.w3.org/1999/xlink}href"


def path_points(d):
    toks = re.findall(r"[MLZCQ]|-?[\d.]+(?:e-?\d+)?", d)
    pts, buf = [], []
    for t in toks:
        if t in "MLZCQ":
            continue
        buf.append(float(t))
        if len(buf) == 2:
            pts.append(tuple(buf))
            buf = []
    return pts


def load(svg):
    raw = Path(svg).read_text()

    # tag each tick group with the numeric label found in its text comment
    def tag(m):
        gid, body = m.group(1), m.group(2)
        c = re.search(r"<!-- ([^>]*?) -->", body)
        if c:
            lab = c.group(1).strip().replace("−", "-").replace("%", "")
            try:
                float(lab)
                return f'<g id="{gid}" data-label="{lab}">' + body
            except ValueError:
                pass
        return m.group(0)

    raw = re.sub(r'<g id="((?:x|y)tick_\d+)">(.*?<!--.*?-->)', tag, raw, flags=re.S)
    return ET.fromstring(raw.encode())


def tick_map(axis_g, use_x):
    pts = []
    for tg in axis_g.iter(S + "g"):
        if not re.match(r"[xy]tick_\d+", tg.get("id", "")):
            continue
        txt = tg.find(".//" + S + "text")
        use = tg.find(".//" + S + "use")
        if txt is None or use is None or not (txt.text or "").strip():
            continue
        lab = txt.text.strip().replace("\u2212", "-").replace("%", "")
        try:
            pts.append((float(use.get("x" if use_x else "y")), float(lab)))
        except ValueError:
            continue
    pts.sort()
    (p0, v0), (p1, v1) = pts[0], pts[-1]
    return lambda p: v0 + (p - p0) * (v1 - v0) / (p1 - p0)


def axes_data(root, axes_id, y_from=None):
    ax = next(g for g in root.iter(S + "g") if g.get("id") == axes_id)
    axes = [g for g in ax if g.get("id", "").startswith("matplotlib.axis")]
    fx = tick_map(axes[0], True)
    # a panel with a shared, unlabelled y axis borrows the y map of y_from
    fy = tick_map(axes[1], False) if y_from is None else y_from
    out = []
    out_fy = fy
    for g in ax:
        gid = g.get("id", "")
        if not (gid.startswith("line2d") or gid.startswith("FillBetween")
                or gid.startswith("PolyCollection")):
            continue
        use = g.find(".//" + S + "use")
        ox, oy = (float(use.get("x", 0)), float(use.get("y", 0))) if use is not None else (0, 0)
        for p in g.iter(S + "path"):
            pts = path_points(p.get("d", ""))
            if p.get("id"):  # a <defs> marker path placed by <use x= y=>
                pts = [(x + ox, y + oy) for x, y in pts]
            if len(pts) < 5:
                continue
            st = p.get("style", "")
            col = re.search(r"stroke: (#[0-9a-f]{6})", st) or re.search(r"fill: (#[0-9a-f]{6})", st)
            out.append({"id": gid, "color": col.group(1) if col else None,
                        "xy": [[round(fx(x), 5), round(fy(y), 5)] for x, y in pts]})
    return out, out_fy


def extract_images(svg, dest):
    raw = Path(svg).read_text()
    imgs = re.findall(r'data:image/png;base64,([A-Za-z0-9+/=\s]+)"', raw)
    names = []
    for i, b in enumerate(imgs):
        name = dest / f"{Path(svg).stem}_{i}.png"
        # matplotlib stores SVG rasters bottom-up and flips them with
        # transform="scale(1 -1)"; save them in display orientation
        from io import BytesIO
        from PIL import Image
        im = Image.open(BytesIO(base64.b64decode(re.sub(r"\s", "", b))))
        im.transpose(Image.FLIP_TOP_BOTTOM).save(name)
        names.append(name.name)
    return names


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "figures/orig")
    region, _ = axes_data(load(src / "guidance_maps.svg"), "axes_3")
    col = load(src / "collateral.svg")
    c_or, fy = axes_data(col, "axes_1")
    c_ex, _ = axes_data(col, "axes_2", y_from=fy)
    out = {"region_curve": region, "collateral_oracle": c_or, "collateral_extracted": c_ex}
    Path("scripts/recovered.json").write_text(json.dumps(out, indent=1))
    for k, v in out.items():
        print(k)
        for l in v:
            print("  ", l["id"], l["color"], len(l["xy"]), l["xy"][0], l["xy"][-1])
    dest = Path("figures/assets")
    dest.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.svg")):
        print(f.name, extract_images(f, dest))
