#!/usr/bin/env bash
# Rebuild every figure and both PDFs.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I scripts/recover_vector.py figures/orig
python3 -I scripts/fig_schematic.py
python3 -I scripts/fig_results.py
python3 -I scripts/fig_supplement.py
latexmk -pdf -interaction=nonstopmode main.tex supplement.tex
