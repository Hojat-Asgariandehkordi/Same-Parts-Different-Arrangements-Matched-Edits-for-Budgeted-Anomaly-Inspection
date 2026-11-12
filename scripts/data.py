"""Every number plotted in the paper, with its source.

Sources are the LaTeX tables shipped with the draft (tables/*.tex) and, where
a value was only drawn and never printed, scripts/recovered.json (read back
from the original vector figures by recover_vector.py; flagged RECOVERED).
Intervals are 95% bootstrap intervals over original photos (4,000 draws)
unless stated otherwise.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Pushpin inspection, extracted maps. Source: tables/inspection_extracted.tex
# keys: sham/source alerts (of 138), top2 (%), marks to both, recall at the
# locked 95% cutoff (%), untouched cells queued per fault, region area (%)
INSPECTION_EXTRACTED = {
    "Released, max":        dict(src=5,  sham=7,  top2=77.5, both=2.43,  rec=95.7, unt=11.07, area=81.6),
    "Released, 99th pct.":  dict(src=5,  sham=7,  top2=87.0, both=2.32,  rec=96.0, unt=11.41, area=77.3),
    "Class-wide, seed 1":   dict(src=12, sham=19, top2=0.0,  both=15.00, rec=97.1, unt=13.00, area=39.3),
    "Footprint, seed 1":    dict(src=6,  sham=9,  top2=87.7, both=2.13,  rec=95.3, unt=0.20,  area=96.3),
    "Class-wide, seed 2":   dict(src=19, sham=22, top2=0.0,  both=15.00, rec=96.4, unt=13.00, area=39.4),
    "Footprint, seed 2":    dict(src=21, sham=20, top2=74.6, both=2.28,  rec=96.0, unt=0.45,  area=89.6),
}

# Alternative operating points, extracted. Source: tables/other_queues.tex
# (98% recall cutoff and 0.5-cost cutoff, both set on development)
OPERATING_EXTRACTED = {
    #                       rec98  unt98  cost_rec cost_unt
    "Released, max":       (98.9, 12.56, 81.9, 0.30),
    "Released, 99th pct.": (98.9, 12.62, 75.7, 0.17),
    "Class-wide, seed 1":  (97.5, 13.00, 39.5, 0.65),
    "Footprint, seed 1":   (97.5, 0.22, 100.0, 0.38),
    "Class-wide, seed 2":  (97.8, 13.00, 39.1, 0.64),
    "Footprint, seed 2":   (98.2, 0.57, 98.2, 0.57),
}

# Paired differences, footprint minus comparator (estimate, lo, hi).
# Source: tables/inspection_deltas.tex (seed 3407 = seed 1, 3419 = seed 2).
# Untouched in cells per fault; the rest in percentage points.
DELTAS = {
    ("Extracted", 1, "released"):  dict(unt=(-10.88, -11.56, -10.12), rec=(-0.4, -3.6, 3.3), sham=(1.4, -3.6, 7.2),  area=(14.7, 10.8, 18.6)),
    ("Extracted", 1, "classwide"): dict(unt=(-12.80, -12.87, -12.72), rec=(-1.8, -4.7, 1.1), sham=(-7.2, -13.8, -0.0), area=(57.0, 53.5, 60.5)),
    ("Extracted", 2, "released"):  dict(unt=(-10.62, -11.31, -9.86),  rec=(0.4, -2.9, 3.6),  sham=(9.4, 2.2, 16.7),  area=(8.0, 3.3, 13.0)),
    ("Extracted", 2, "classwide"): dict(unt=(-12.55, -12.65, -12.45), rec=(-0.4, -3.6, 2.9), sham=(-1.4, -9.4, 6.5),  area=(50.3, 46.1, 54.6)),
    ("Oracle", 1, "released"):     dict(unt=(-10.30, -11.05, -9.49),  rec=(0.7, -2.5, 4.0),  sham=(-9.4, -15.9, -2.9), area=(14.0, 9.9, 18.1)),
    ("Oracle", 1, "classwide"):    dict(unt=(-12.80, -12.86, -12.73), rec=(0.0, -3.3, 2.9),  sham=(-4.3, -11.6, 2.9), area=(55.6, 51.8, 59.2)),
    ("Oracle", 2, "released"):     dict(unt=(-10.04, -10.80, -9.21),  rec=(0.7, -2.5, 4.0),  sham=(-10.9, -19.6, -2.9), area=(7.5, 2.5, 12.6)),
    ("Oracle", 2, "classwide"):    dict(unt=(-12.54, -12.64, -12.42), rec=(0.0, -3.3, 3.3),  sham=(-9.4, -17.4, -1.4), area=(48.7, 44.3, 53.1)),
}

# Upstream-only continuation, footprint minus class-wide, extracted.
# Source: tables/inspection_deltas_upstream.tex
DELTAS_UPSTREAM = {
    ("Extracted", 1, "classwide"): dict(unt=(-4.28, -4.93, -3.66), rec=(-1.1, -2.9, 0.7), sham=(2.2, -4.3, 8.7)),
    ("Extracted", 2, "classwide"): dict(unt=(-4.43, -5.14, -3.72), rec=(-0.7, -2.2, 0.7), sham=(1.4, -3.6, 6.5)),
}

# Primary contrast on the two fixed photo halves (63 / 75 photos).
# Source: tables/queue_halves.tex (rule-aware, extracted)
HALVES = {1: ((-12.87, -12.95, -12.79), (-12.75, -12.85, -12.63)),
          2: ((-12.63, -12.76, -12.51), (-12.48, -12.63, -12.32))}

# Recall at an equal realized cost (descriptive test sweep, extracted).
# Source: tables/realized_cost.tex  (estimate, lo, hi) in %
REALIZED = {
    "Released, max":       {0.30: (81.9, 77.5, 85.5), 0.50: (82.6, 79.0, 86.6)},
    "Released, 99th pct.": {0.30: (77.5, 73.2, 81.5), 0.50: (77.9, 73.6, 81.9)},
    "Footprint, seed 1":   {0.30: (99.6, 96.7, 100.0), 0.50: (100.0, 100.0, 100.0)},
    "Footprint, seed 2":   {0.30: (88.4, 64.9, 96.0), 0.50: (97.1, 94.2, 99.6)},
}

# Full SALAD on matched pushpins, extracted interface: alerts out of 138.
# Source: tables/full_pushpin.tex
FULL_PUSHPIN = {
    "Composition": dict(src=5,  sham=7,   fault=138),
    "Local RGB":   dict(src=9,  sham=128, fault=138),
    "Global RGB":  dict(src=84, sham=102, fault=106),
    "Fusion":      dict(src=75, sham=130, fault=138),
}
N_PUSHPIN = 138

# Juice bottles: alerts out of 89 and fault-minus-sham alert gap (pp).
# Source: tables/juice.tex
JUICE = {
    "Composition": dict(src=4, sham=4,  fault=4,  gap=(0.0, 0.0, 0.0)),
    "Local RGB":   dict(src=6, sham=28, fault=25, gap=(-3.4, -12.4, 5.6)),
    "Global RGB":  dict(src=9, sham=14, fault=89, gap=(84.3, 76.4, 91.0)),
    "Fusion":      dict(src=7, sham=18, fault=89, gap=(79.8, 70.8, 87.6)),
}
N_JUICE = 89

# Graph check. Edited-state target AUROC with donor-paired CIs.
# Source: tables/graph_main.tex (GlaS, original length tier)
GRAPH_RANK = {
    "Geometry only":      (64.0, 57.1, 70.6),
    "Distance + spacing": (90.2, 88.4, 91.7),
    "Pair MLP":           (91.5, 89.1, 93.6),
    "Masked GNN":         (82.5, 78.3, 86.5),
}
# Response AUROC (|change in probability|). Source: tables/graph_main.tex,
# tables/degree.tex. Point values only where the table gives no interval.
GRAPH_RESPONSE = {
    "Geometry only":      (50.0, 50.0, 50.0),
    "Distance + spacing": (50.0, 50.0, 50.0),
    "Pair MLP":           (50.0, 50.0, 50.0),
    "Masked GNN":         (98.5, 97.6, 99.3),
}
# Top-four recovery of the GNN response, GlaS original length.
# Source: tables/degree.tex and tables/graph_mean.tex
GRAPH_TOP4 = {
    "Full response":         (87.5, 82.4, 92.4),
    "Degree inputs fixed":   (33.7, 25.9, 40.8),
    "Refit, mean messages":  (46.6, 40.5, 52.4),
}
GRAPH_TOP4_HVSMR = {
    "Full response":       (67.4, 58.5, 76.3),
    "Degree inputs fixed": (41.9, 34.7, 49.2),
}


def recovered():
    """RECOVERED curves from the original vector figures (see recover_vector.py)."""
    return json.loads((HERE / "recovered.json").read_text())

# Cell grid of the guidance-map panels (photo 058, the median released
# fault-minus-sham case; figures/selection.json), as fractions of the 139-px
# raster. RECOVERED from figures/orig/guidance_maps.svg.
_X0, _W = 10.826, 100.08
_Y0 = 25.056
CELL_X = [(x - _X0) / _W for x in (13.9, 33.0, 51.8, 70.5, 89.2, 107.9)]
CELL_Y = [(y - _Y0) / _W for y in (30.4, 60.8, 90.1, 119.3)]   # top to bottom
MAP_TARGETS = [(2, 2), (3, 2)]          # (col, row from top)
MAP_QUEUED_RELEASED = [(c, r) for c in range(5) for r in range(3) if (c, r) not in MAP_TARGETS]
MAP_QUEUED_FOOTPRINT = []
MAP_CUTOFF = {"released": 0.588, "footprint": 0.229}   # printed in the draft's Fig. 2

# Matched-photo figure (draft figure pushpin_intervention). Cell grid as
# fractions of the 159x94 raster, boxes and the printed scene scores.
# RECOVERED from figures/orig/pushpin_intervention.svg.
PHOTO_X = [0.033, 0.224, 0.41, 0.597, 0.784, 0.97]
PHOTO_Y = [0.062, 0.364, 0.654, 0.944]
PHOTO_ROWS = [
    # title, vacated cell, recipient cell (col, row), scene scores src/sham/fault, alerts
    dict(title="Median paired effect", src=(0, 0), dst=(0, 1),
         score=(0.147, 0.147, 1.000), alert=(False, False, True)),
    dict(title="First alerted sham", src=(2, 2), dst=(1, 2),
         score=(0.292, 0.278, 0.999), alert=(True, True, True)),
]

# Class-wide seed 2 at the three cutoffs (tables/inspection_extracted.tex and
# tables/other_queues.tex) is already in INSPECTION_EXTRACTED / OPERATING_EXTRACTED.
# Scene cutoffs t_s (tables/thresholds.tex, released): oracle 0.15802, extracted 0.17097.
T_S = {"oracle": 0.15802, "extracted": 0.17097}

# Graph readouts incl. typed distance, GlaS original-length tier (tables/graph_main.tex).
GRAPH_RANK = {
    "Geometry only":           (64.0, 57.1, 70.6),
    "Typed distance":          (74.9, 70.8, 78.9),
    "Distance + local spacing": (90.2, 88.4, 91.7),
    "Pair MLP":                (91.5, 89.1, 93.6),
    "Masked GNN":              (82.5, 78.3, 86.5),
}
GRAPH_RESPONSE = {   # None = 50 by construction (probability cannot change)
    "Geometry only": None, "Typed distance": None, "Distance + local spacing": None,
    "Pair MLP": None, "Masked GNN": (98.5, 97.6, 99.3),
}
