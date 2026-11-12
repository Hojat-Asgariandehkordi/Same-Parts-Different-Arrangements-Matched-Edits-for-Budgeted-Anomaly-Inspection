# Figure review: "Same Parts, Different Arrangements"

Reviewer stance: first-time reader, CVPR area chair. I checked every figure as a 200-dpi PNG, as zoomed crops of the vector PDFs, and in context in `main.pdf` (pages 1, 3, 4, 5, 7, 8). The figures are placed at about 1:1 scale (scale factor 0.975 to 1.016; the supplement screw figure is at 0.878). For that reason, the font sizes below are the sizes **at print**, taken from the span sizes in the PDF (PyMuPDF) times the placement scale.

Numbering: Fig. 1 teaser, 2 pipeline, 3 matched_photos, 4 collateral, 5 guidance_maps, 6 paired_forest, 7 branches, 8 graph_audit, S screw_discordant.

---

## 0. Urgency ranking

| Rank | Figure | Why |
|---|---|---|
| 1 | **Fig. 5 guidance_maps** | Carries the main result. The curves in (c) are "recovered from the draft's figure" (digitised), and its legend says 89.7 where Table 1 says 89.6. Panel (d) has an unlabelled non-linear x-axis, points that are not identified by cutoff, and lines joining discrete operating points. Its colours clash with Fig. 4. |
| 2 | **Fig. 1 teaser** | Being re-illustrated. The class-wide mask shows the *source* layout, not the fault layout. In the class-wide map the unqueued cells look *hotter* than the queued ones. Queue membership is drawn as one merged orange blob. Pins are the same orange as "queued". |
| 3 | **Fig. 2 pipeline** | Being re-illustrated. Its example images don't match each other: the photo shows a fault in col 1, the part map shows a clean tray, and the score map lights a different cell. The "no alarm → Q=∅" branch is missing, and so is the oracle bypass. The bar chart shows the *ideal* queue, which contradicts the paper's main finding for the released model. |
| 4 | **Fig. 4 collateral** | Its curves are also digitised from the draft. The legend sits on top of the blue curve. The y-label "Untouched cells" is wrong: the axis is a share, not a count. Its colours mean something else in Figs. 5–7. |
| 5 | **Fig. 3 matched_photos** | The cyan box on the *sham* contradicts "cyan = target" from Fig. 1, since a sham has T = ∅. The heat maps have no colour bar and use a third score colour map. There is no movement cue. Its "median" photo is not the same as Fig. 5's "median" photo. |
| 6 | **Fig. 6 paired_forest** | There are no panel letters. The guard violation (seed 2 vs released, +9.4 [2.2, 16.7]) is not flagged, the pre-specified primary rows are not marked, and the failed-competence upstream control is not marked. There is no "better" direction, and the row labels are redundant. |
| 7 | **Fig. 7 branches** | Data labels in (d) collide with the error bars. There is no 10% reference line in (b,c), even though fusion alarms on 54% of sources. The sham and source bottles look identical. Titles mix counts and %. |
| 8 | **Fig. 8 graph_audit** | Panel (b) plots three trivially-50 values as if they were estimates. The colours are arbitrary, and the text's "+15.3 points" can't be read from the figure. |
| 9 | Supp. screw_discordant | There is no class legend, no RGB reference and no annotation of the fragments the caption describes. |

---

## 1. Cross-figure issues (fix these first, as one system)

1. **The same three colours mean different things in different figures.** Red-orange (#C25F3A-ish), navy blue (#3D5A99) and green (#1B8A6B) are reused:
   - Fig. 4: red = *Fault*, blue = *Vacancy only*, green = *Valid sham*.
   - Fig. 7: red = *Fault*, green = *Valid sham*, grey = Source; (d) blue = everything.
   - Figs. 5c/d and 6: blue = *Released*, red = *Class-wide*, green = *Footprint*.
   - Fig. 8: red = masked GNN / full response, blue = degree fixed, green = refit (no meaning).
   - Fig. 1: red-orange text = class-wide queue, green text = footprint.
   - Fig. S: blue title = grid only, red title = pairs only.
   - Orange (#F0A030) = queued untouched in Figs. 1 and 5. The pins in Fig. 1 and the high end of the score colour map in Fig. 5 are almost the same orange.
   - The cyan target outline (#22B5D6) is close to the cyan-blue middle of the Fig. 5 score colour map.

   **Fix:** Define two separate palettes and a reserved overlay pair, and use them in every figure:
   - *Models:* Released = dark grey #4D4D4D, Class-wide = purple #7B5EA7, Footprint = green #1B8A6B. For the two seeds, use a solid line/filled marker (s1) and a dashed line/hollow marker (s2), *not* a lighter tint; the mint s2 colour fails contrast on white.
   - *Edit types:* Source = light grey #A0A0A0, Valid sham = blue #3D7DC4, Fault = vermilion #D55E00, Vacancy = ochre #B58A1A.
   - *Overlays (reserved, never used for data):* target = cyan #00B4D8 solid (recipient) / dashed (vacated); queued-untouched = orange #F28E2B, thick per-cell outline.
   - *Score maps:* use **one** sequential greyscale map (black→white) in Figs. 1, 2, 3 and 5. Cyan and orange overlays then pop, and nothing in the map can be mistaken for an overlay. Every map gets a colour bar labelled "score S (0–1)", or "|ΔS|" in Fig. 3.
   - Fig. 8 has no model/edit semantics, so draw it in single neutral black/grey with an accent on the masked GNN only.
2. **"cell" vs "compartment".** Figs. 1, 2, 4, 5 and 6 say "cell"; the abstract, the text and every caption say "compartment". Use "compartment" in the figures, or put "compartment (cell)" in Fig. 1 once and then use "compartment" everywhere. Axis labels like "Untouched cells queued per fault" should read "Untouched compartments queued per fault".
3. **"alert" vs "alarm".** Figs. 3, 6, 7 and S say "alert", while the text and Eq. (1) say "alarm". Pick "alarm".
4. **"Fault" vs "Placement fault".** Fig. 3's header says "Placement fault"; everything else says "Fault". Use "Fault".
5. **Digitised curves.** The captions of Fig. 4 ("Curves recovered from the analysis figure of the draft") and Fig. 5c ("curves recovered from the draft's figure") admit that plotted data was re-traced from an image. This is a scientific-integrity red flag for an AC, and it already produces a number mismatch (Fig. 5c legend 89.7 vs Table 1 89.6). **Regenerate both from the per-photo/per-compartment scores** and delete those caption clauses.
6. **Subscripts are too small.** At print, t_c, t_s, x_i, m_i and S_i subscripts are **4.6–4.9 pt** (Figs. 1, 2, 5). Typeset maths at ≥ 7 pt base so subscripts are ≥ 5.5 pt, or write "t_c" as a ≥ 7 pt label.
7. **Small text.** 6.0–6.2 pt text appears in Fig. 1 (legend, "fine-tune", mask captions), Fig. 4 (legend), Fig. 5 (both legends), Fig. 6 (threshold labels) and Fig. 7 (legend and data labels, 5.9 pt). Raise all of it to ≥ 7 pt. The body caption is 9 pt; 7–8 pt in-figure text is the target.
8. **Panel letters** are missing in Figs. 1(b)-internal, 3, 4 and 6. Fig. 6 is referenced as a whole but has three distinct metrics, so add (a)(b)(c). Fig. 4's two panels need (a) Oracle and (b) Extracted.
9. **No "which direction is better" cues** on any difference axis (Figs. 6 and 7d). Add small arrow annotations under the axes.
10. **Example inconsistency between Figs. 3 and 5.** Both captions claim to show "the photo/fault with the median released fault-minus-sham difference", but they are different trays: Fig. 3's targets are r1c1/r2c1, and Fig. 5's are r3c3/r3c4. Presumably one is oracle and one is extracted. Either use the same photo in both, or say "median on oracle maps" / "median on extracted maps" in each caption.

---

## 2. Per-figure review

### Fig. 1 — teaser (`teaser.png`)

**Intended message:** The same pixel move is either harmless (sham) or a fault that fixes exactly two compartments to check. A detector trained with class-wide targets makes the inspector check almost the whole tray, while footprint targets cut the queue to just the two targets.

**10-second test:** Partial. Panel (a)'s "same move, different meaning" comes across. Panel (b)'s takeaway is carried almost entirely by the coloured *text* "2 targets + 11 untouched" vs "2 targets + 0", not by the graphics: the reader can't count queued cells in the map.

**Problems**
- **Scientific inaccuracy, class-wide mask.** In (b) the class-wide target image puts one pin in each of the 15 compartments of an evenly spaced layout, including r2c2. That is the *source* arrangement. The fault arm has r2c2 empty and two pins in r2c3, and the footprint mask beside it does sit at the r2c3 position. So the two masks are drawn for different scenes. Draw the class-wide mask on the same edited tray: r2c2 empty, two pins in r2c3, all 15 pins white.
- **Misleading encoding in the class-wide score map.** The two *unqueued* untouched cells (r1c5, r3c1; RGB ≈ (228, 78, 100)) are drawn in a darker, more saturated crimson than the queued ones (≈ (249, 121, 92)). In any warm sequential map, darker red reads as *higher* score, which says the cells that were *not* queued scored higher. There is no colour key.
- **Queued membership is a merged orange "gutter" blob**, not per-cell outlines. The 11 queued cells can't be counted, and the boundary between queued and not queued is a thin grey edge. The legend shows an orange *outline* square, which doesn't match the fill style used.
- **Pins are the same orange-yellow (#F0A818) as "queued untouched".** In the footprint row this makes pins in untouched cells look queued.
- The footprint score map (navy background) and the class-wide map (salmon) use different backgrounds and no scale. Navy vs salmon reads as "different map type", not "low vs high score".
- **Sham arm:** the white triangle "arrow" has no stem, so its direction is unclear. The moved pin's head sits on the r2c1/r2c2 divider, so a reader may read the sham as a *cross-compartment* move.
- **Fault arm:** the two pins in the recipient overlap, and at print size (each tray ≈ 0.85 in wide, a pin head ≈ 0.04 in) they look like one pin. The white arrow lies on top of the vacated cell's dashed box.
- **Legend collision:** "target cell" runs into the orange swatch of "queued untouched" (no gap). Legend text is 6.2 pt.
- "fine-tune" is 6.0 pt, mask descriptions 6.2 pt, "long/short queue at 95% recall" 6.4 pt, and the t_c subscript 4.8 pt.
- Panel (a) has ~0.35 in of empty space between the panel title and the column headers, while the trays themselves are tiny. The italic note under (a) repeats the caption.
- *g* in "g ≥ t_c" is not defined anywhere in the figure or the Fig. 1 caption.
- Vocabulary: "cell" (figure) vs "compartment" (caption); "arm" (figure) is never defined.
- The caption says "(b) A detector trained to mark every pin…lights up the whole tray." The figure shows 2 untouched cells *not* lit, so the caption and the figure disagree. Either say "almost the whole tray" or draw 13/13, which matches Fig. 5a.

**Fixes (if kept as a matplotlib/vector figure until the re-illustration lands)**
- Redraw the class-wide mask for the fault layout.
- Draw score maps in greyscale with a 3-stop colour bar (0, t_c, 1). Draw queued cells as a 1.5-pt orange *outline per cell* and targets as a 1.5-pt cyan outline. Draw unqueued untouched cells with no outline.
- Recolour pins to the photo's yellow-gold, or to neutral light grey in the schematic, so they are never confused with the overlay orange.
- Legend: 7 pt, 4 mm gap between entries, below the (b) maps spanning their width.
- Enlarge the trays: drop the italic note (it is in the caption) and use the freed height to scale panel (a) by ~1.4×.

**What the illustration artist should draw differently (Fig. 1 re-illustration)**
1. **One tray, one story.** Use a single, *larger* hero tray (≥ 1.6 in wide) in a realistic but simplified style: grey plastic dividers, clearly separated pins. Use the **same** fault instance throughout (a) and (b), so the eye follows one pin.
2. **Make the move visible.** In each arm, show the pin's original position as a 30%-opacity "ghost" and draw a curved arrow with a stem from ghost to new position.
   - Sham: the arrow stays inside the compartment; mark it with a green check and the label "still 1 pin per compartment".
   - Fault: the arrow crosses the divider; mark it with a red ✗. The recipient shows **two clearly separated pins**, and the vacated compartment shows a visible empty floor.
   - Vacancy: ghost only, with "removed".
   - Put a small "same cutout · same fill · same distance" ruler/icon strip under all arms, replacing the italic sentence.
3. **Targets only where they exist.** Cyan solid = recipient, cyan dashed = vacated, on Fault (2) and Vacancy (1). Explicitly *no* box on Source/Sham, with a tiny "no target" tag.
4. **Panel (b) as "what the inspector receives".** For each training target:
   - The training mask overlaid on the same edited tray: class-wide = *all 15 pins* filled magenta; footprint = *only the moved pin* filled. The contrast "every pin vs one pin" must be visible at a glance.
   - Then the test-time score map in greyscale.
   - Then the output: a **checklist/clipboard of compartments** to open, drawn as the 5×3 grid with ticked boxes. Class-wide: 2 cyan + 11–13 orange ticks with a counter "inspect 13 compartments". Footprint: 2 cyan ticks, "inspect 2". A queue-length bar (13 vs 2 boxes stacked) would make the cost legible without reading numbers.
5. Optionally anchor with the measured numbers, small ("measured: 11.07 → 0.20–0.45 untouched at 95% recall"). The caption currently says "Schematic", which leaves the reader without the headline number.
6. Keep the left/right split, but drop the vertical rule and use panel letters (a)/(b) at 9 pt bold. All text ≥ 7 pt.

---

### Fig. 2 — pipeline (`pipeline.png`)

**Intended message:** Photo → part map (extracted or oracle) → composition score map → scene alarm → per-compartment max → threshold t_c → queue → (R, C). Only the composition branch's *training target* changes, and both cutoffs come from development data.

**10-second test:** The left-to-right chain is readable. The decision logic (gate yes/no, what the queue contains, where R and C come from) and the "what we change" message are not.

**Problems**
- **The example images are mutually inconsistent.**
  - The RGB photo shows a fault: r1c1 is empty, and r2c1 has two pins, one lying horizontally and one vertical.
  - The part map shows a *clean* tray with one pin per compartment, evenly spaced, and only one class (pin) on navy. It shows no tray, no dividers and no other classes, even though the label says "6 classes".
  - The score map is a tinted copy of a photo with pins visible, not a heat map. Its single bright block sits at **r3c3**, unrelated to the fault in column 1.
  - A careful reader will conclude that the pipeline is broken.
- **The bar chart shows 2 cyan bars above t_c and 13 grey bars below**, i.e. the ideal footprint outcome (cost 0). As the generic pipeline, this contradicts the paper's central finding that the released detector queues ~11 untouched compartments. Untouched bars above t_c should be orange in at least one variant.
- **The t_c line is orange**, the same colour as "queued untouched" in Figs. 1 and 5. Use dark grey dashed and label it "t_c".
- **The gate has no branches.** "max S_i > t_s ?" is a question with no yes/no outputs. Eq. (2)'s "otherwise ∅", i.e. "tray not opened → targets missed", is the subtle part of the protocol and isn't drawn.
- **The oracle path isn't drawn.** "(U-Net, or oracle)" under the extractor implies the oracle is a model, but in the caption the oracle *bypasses* the photo: it edits the released label map directly.
- The green bracket "we fine-tune its training target" floats above the composition icon. It should show *what* changes (class-wide vs footprint mask). As worded it reads as if the target is fine-tuned rather than the network.
- "queue Q_i {e : g ≥ t_c}" and "recall R, cost C" float in white space with no box, and R and C have no definition cue (targets in queue / untouched in queue).
- **Mixed visual styles:** a photo-real BioRender inspector (≈ 12% of the figure width), a camera clip-art, a siren/barrier icon, flat U-Net glyphs and blurry raster images. The "inspector" label is detached ~0.25 in below the figure. The camera has no label.
- The RGB photo is a low-resolution, blurry raster (soft edges at print); it reads as AI-generated rather than an MVTec LOCO photo.
- Text sizes: the sublabels are 6.4 pt and the subscripts 4.6–4.9 pt (x_i, m_i, S_i, t_s, t_c), which is illegible.
- "15 cell scores / g = maximum in cell e": Eq. (2) uses g_i(e); be consistent.

**Fixes (current figure)**
- Use the *same* fault example in all four images: photo, part map (all 6 classes with a mini key), greyscale score map, and per-compartment bars.
- Make the bars match that score map: 2 cyan target bars, untouched bars above t_c in orange, below in grey.
- Add a "no" arrow from the gate to a small box "Q = ∅ (tray not opened; targets missed)".
- Draw the oracle as a dashed bypass arrow from "released label + same edit" into the part map.
- Remove the inspector figure, or shrink it to a 0.3-in flat icon.
- Raise all text to ≥ 7 pt.

**What the illustration artist should draw differently (Fig. 2 re-illustration)**
1. **Two horizontal lanes.**
   - *Top, "Training (changed)":* a SALAD synthetic edit of a part map → **target mask, shown as two stacked alternatives: class-wide (all pins) vs footprint (pasted pin only)**, with a green highlight on the *mask* box only → composition U-Net. Label it "only y changes; inputs, steps and weights identical".
   - *Bottom, "Test-time inspection (fixed)":* the existing chain.
   - Connect the lanes with a vertical "weights" arrow into the composition box.
2. **One running example.** The same edited tray (one empty compartment, one doubled) appears as photo → part map → score map → 5×3 grid of compartment maxima. The grid is shaded by score, with the t_c cut shown as cells above/below. It ends in the queue grid with cyan targets and orange queued cells, so the reader sees R = 2/2 and C = number of orange cells *computed on the picture*. Replace the abstract bar chart with this 5×3 grid. Alternatively keep a sorted bar chart, but label each bar with its compartment and colour by status.
3. **Gate as a diamond** with "yes → compartments scored" and "no → nothing queued (targets count as missed)".
4. **Calibration side panel (blue).** A small box "development data: 69 normal photos → t_s (90% normal no-alarm); 69 matched faults → t_c (95% target recall)", with dashed blue arrows into the gate and the threshold. Text-only brackets above the chain are easy to miss.
5. **Extractor fork.** "U-Net (extracted; realistic)" vs "move released label (oracle)" as two parallel arrows merging into the part map.
6. **Consistent flat icon style** (no photo-real human). End with a compact "inspector opens Q" icon and the formulas R = |Q∩T|/|T| and C = |Q∖T| right beside it.
7. Typography: labels ≥ 7.5 pt, maths ≥ 7 pt base, consistent colours (green = "what we change", blue = "fixed on development data", cyan/orange for overlays only).

---

### Fig. 3 — matched_photos

**Intended message:** On real photos, sham and fault move the same pixels, but the fault makes the released map change *across the whole tray*.

**10-second test:** No. The reader sees four columns of nearly identical trays and must hunt for the moved pin; the right-column heat maps have no scale. "Median paired effect" / "First alerted sham" are opaque row names.

**Problems**
- **A solid cyan box on the valid sham** contradicts Fig. 1, where cyan = target compartment and a sham has T = ∅. In the Source column the cyan box marks "the pin that will move", a third meaning.
- **No colour bar** on the |S^fault − S^source| maps. The top row looks purple (~0.3–0.6 in magma) and the bottom row uniformly peach, and we can't tell whether the rows share a scale. The bottom row's message ("every compartment changes") depends entirely on that. This is also a third score colour map (magma) after Fig. 1's reds and Fig. 5's navy→cream.
- There is no movement cue (ghost or arrow), so the sham move in the top row (r1c1, pin moved up) is hard to see at print size.
- The scene scores are shown but **t_s isn't**, so the reader can't tell why 0.292 and 0.278 alarm. State "alarm if > t_s = 0.xxx" once in the header.
- The bottom row's purpose ("the source also alarms, so sham alarms are partly not about the edit") is only in the caption. Show it with a small "source already alarms" tag.
- The header "Placement fault" is inconsistent with "Fault" elsewhere. "|fault − source|, cell maxima" needs a symbol (|ΔS| per compartment).
- The heat maps are rectangular with a thick black frame, while the trays are rounded and offset, so the grid doesn't align with the photos visually.
- The rotated row labels (8.1 pt) take 0.15 in of width for jargon. Rename them "Typical fault (median effect)" and "Sham that alarms".
- The geometry is correct: I verified top row source/sham r1c1, fault vacated r1c1 → recipient r2c1; bottom row r3c3 → r3c2. Dashed/solid placement in the heat maps matches the photos.

**Fixes**
- On Source/Sham use a **white dashed** outline (or a grey arrow) for "moved pin". Reserve cyan for Fault targets only.
- Add a shared vertical colour bar "|ΔS| (0–1)" right of the 4th column, use greyscale, and print the per-compartment value (6.5–7 pt) in each heat-map cell.
- Add 1-pt arrows from ghost to new position on Sham and Fault.
- Add "t_s = …" to the column header row. Colour alarm text with a consistent alarm colour (not the class-wide red-orange).
- Crop the heat maps to the tray extent so the grid lines up with the photos.
- Use the same photo as Fig. 5(a,b), or justify the difference in the caption.

---

### Fig. 4 — collateral

**Intended message:** For a fault, almost every untouched compartment changes (≈90% at |ΔS| ≥ 0.5); for a vacancy or sham almost none does. So the extra pin, not the hole, lights up the tray.

**10-second test:** Mostly yes: the red curve is high and the others low. The y-axis label misleads, though.

**Problems**
- **Y-label "Untouched cells" with range 0–1** reads as a count. It is a share. Use "Share of 13 untouched compartments changed".
- **The legend overlaps the blue curve** in the right panel: the blue vacancy curve descends through the legend handles at x ≈ 0.1. Legend text is 6.1 pt.
- **Curves are digitised** ("recovered from the analysis figure of the draft"); see cross-figure item 5. The 0.05-step piecewise-linear shape, with a sharp drop to 0 at 0.95, also looks like a coarse re-trace.
- The dotted 0.5 line is unlabelled in the plot; it only appears in the caption.
- Colours (red fault / blue vacancy / green sham) conflict with Figs. 5–6 (red class-wide / blue released / green footprint).
- Tick formats are inconsistent (y "0.0, 0.5, 1.0" vs x "0, 0.5, 1"). The x-label "Cutoff on |change|" has no symbol or units; use "|ΔS| cutoff (score units)".
- There are no panel letters, and the shared y-axis is not shown as shared (the right panel has ticks but no label, which is fine, but add (a)/(b)).

**Fixes:** Regenerate from data. Put the legend above both panels in 3 columns, at 7 pt. Relabel y. Label the dotted line "0.5 (text summary)" at 6.5–7 pt beside it. Apply the edit-type palette from section 1. Optionally annotate the three values at 0.5 (90.3 / 2.9 / 0.7%) directly on the curves so the figure matches the text.

---

### Fig. 5 — guidance_maps (most urgent)

**Intended message:** At the locked 95% cutoff, the released map queues every compartment while the footprint map queues only the targets, and this holds at every development cutoff (recall high, cost near 0).

**10-second test:** (a) vs (b) works: orange everywhere vs cyan only. (c) and (d) don't: the reader can't tell which point is which cutoff, and the x-scale in (d) is deceptive.

**Problems**
- **(c) digitised curves**, and the **legend's "Footprint, seed 2 (89.7)" disagrees with Table 1 (89.6)**.
- **(c) omits class-wide**, which is present in (d) and in Table 1 (area 39.3). The panel title "Low-FPR region curve" is jargon. The y-label "Target-cell recall" differs from (d)'s "Target recall". The y-axis starts at 45 with no break mark, so all curves are clipped at the bottom.
- **(d) x-axis is non-linear without saying so.** Ticks 0, 0.5, 1, 5, 13 are spaced so that 0→1 occupies ~half the axis and 1→13 the other half (symlog). The "13" tick label is crowded against the right spine, and the released point at ≈12.6 and the class-wide square at 13 overlap and are clipped by the axes edge.
- **(d) lines connect the three discrete cutoffs.** This implies interpolation along a curve that was never measured.
- **(d) points aren't identified**: the reader can't tell which marker is fixed-cost, 95% or 98%. The caption names the three cutoffs but the figure gives no mapping.
- **(d) has class-wide seed 1 only**, without seed 2 (Table 1 has both). Footprint s2 is mint-green, low contrast on white.
- **(a)/(b) score colour map**: navy → blue → purple → orange → cream. The orange band (0.7–0.9) collides with the orange queued outlines, and the blue band (~0.3) collides with the cyan target outlines. Panel (b) is almost uniformly dark; the target cells sit at ~0.25 (just above t_c = 0.229) and are barely visible, so the reader can't *see* that the footprint map still alarms.
- **(a) adjacent orange outlines merge** into a thick lattice, so per-cell membership is less clear than separate outlines would be.
- The aspect ratio of the maps (≈ square 256×256) differs from the photos in Fig. 3 (≈ 2:1), so a reader may wonder whether this is the same tray geometry.
- Text: legends 6.1 pt, t_c subscript 4.6 pt. The colour bar under (a,b) adds a whole row of height; a vertical bar right of (b) would save ~0.25 in.
- The caption says "(a,b) Extracted maps of the fault with the median released fault-minus-sham difference", but this is a different tray from Fig. 3's "median" (see cross-figure item 10).

**Fixes**
- Regenerate (c) from data; fix 89.7 → 89.6 (or fix the table). Add the class-wide curves (dotted). Rename it "Compartment ROC, FPR ≤ 5%". Start y at 0, or add an axis-break glyph.
- (d):
  - Use a broken x-axis: [0, 1.2] linear + break + [10, 13.5] linear. Or use a symlog axis with a visible "symlog" note and ticks at 0, 0.25, 0.5, 1, 2, 5, 10, 13 and minor gridlines.
  - Remove the connecting lines.
  - Encode the cutoff by marker *fill*, or annotate each point with a 6.5–7 pt tag "FC", "95", "98"; keep the model by colour.
  - Add class-wide s2 and footprint s2 with hollow markers.
  - Add the 95% recall guide line (light grey) and a "← better / ↑ better" corner annotation.
  - Extend xlim to 13.6 so the points are not clipped.
- (a,b): greyscale map. Print the per-cell maximum (6.5 pt) inside each cell, so (b)'s "targets at 0.25 > t_c 0.229" is legible. Draw outlines per cell with a 1-pt inset so neighbours don't merge.
- Use the same palette as Fig. 6 (models) and keep it disjoint from Fig. 4.

---

### Fig. 6 — paired_forest

**Intended message:** Footprint beats both comparators by ≫ 1 compartment on cost, without crossing the recall floor or the sham guard.

**10-second test:** The cost panel reads quickly. The recall and sham panels require reading the caption to know which direction is bad and which rows are the pre-specified test.

**Problems**
- There are no panel letters, although the text discusses metrics separately.
- **The guard violation is not flagged.** "Extracted, seed 2 vs released" has a sham Δ of +9.4 [2.2, 16.7], entirely above the +5 guard, yet it is drawn exactly like every other row. The text discusses it, so the figure should show it too.
- **The pre-specified primary contrast is not marked.** Per Sec. 3.5 it is "extracted, footprint vs class-wide". Readers will compare against "released" first.
- **The upstream-only seed-1 control failed the competence check** (Sec. 4.3), but its rows look identical to seed 2's.
- There is no "better" direction: lower is better in panels 1 and 3, higher in panel 2.
- **Redundant encodings.** The row labels repeat "Extracted…" and "Oracle…" while the marker shape *also* encodes interface (circles/squares), and that is explained only in a 7-pt header sentence. The labels take ~25% of the figure width and contain double spaces ("seed 1  vs. released").
- The header sentence (7 pt) duplicates the caption; remove it.
- The threshold labels ("useful: −1", "floor: −5", "guard: +5") are 6.0 pt.
- The class-wide intervals in panel 1 are so tight they render as bare dots at the far-left spine, nearly touching the axis. Add xlim padding to −14.
- The x-labels lack "Δ": "Untouched cells per fault" should be "Δ untouched compartments / fault"; "Valid-sham alerts (pp)" should be "Δ sham alarm rate (pp)".

**Fixes**
- Add (a)(b)(c).
- Group rows under bold 7-pt group headers ("Extracted maps", "Oracle maps", "Upstream-only continuation (extracted)"). Shorten the rows to "s1 vs released", "s1 vs class-wide", etc., and drop the circle/square encoding.
- Add a star or bold label to the two primary rows.
- Draw intervals that cross a threshold with hollow markers plus a red "violates guard" tag. Mark the failed-control row with "†" (with a footnote in the caption).
- Add "← fewer (better)" under (a), "better →" under (b) and "← fewer false alarms" under (c), at 6.5–7 pt grey.
- Raise the threshold labels to 7 pt and place them at the top of their lines.
- Use the model palette (released grey / class-wide purple), so red is never used for a comparator.

---

### Fig. 7 — branches

**Intended message:** Under the tray rule, the composition branch separates fault from sham while the local RGB branch (and so fusion) fires on shams. Under the juice rule, only the global RGB branch separates them.

**10-second test:** Partly. The striking bars (local RGB / fusion sham ≈ 93–94%) come across. The juice story needs (c)+(d), and (a) doesn't show *what* is wrong in the fault.

**Problems**
- **(a) Source and Valid sham look identical**: the same cherry icon is pasted from a disjoint bank, and the difference is invisible at print. The fault is only obvious because of the banana. Nothing says the liquid is cherry, so "fault" depends on knowing the rule.
- (a) The bottle photos are low-res and blurry; the zoom strip is pixelated.
- **(d) data labels collide.** "+84.3" sits against the Fusion error bar region, "+0.0" touches its marker, and "-3.4" uses a hyphen rather than a minus while "+" is used elsewhere. Labels are 5.9 pt.
- **(b)/(c) have no 10% reference line**, although the caption says each branch is set "at its own 10% normal cutoff". Pushpin fusion alarms on **54% of sources**, global RGB on 61%, and local RGB on 6.5%. Without a 10% line, the reader can't see that the extracted interface breaks the calibration. Say this in the caption.
- (b) The legend (5.9 pt) sits inside the axes just above the 100% fault bars; this is tight. The legend is shared with (c) but placed only in (b).
- The titles say "alerts of 138" / "of 89" (counts) while the axes are in %.
- "Comp." is abbreviated, while the text uses "composition".
- (d) has all-blue markers, and blue = Released in Figs. 5–6. There is no pushpin counterpart to (d), so the two rules can't be compared on the same summary.
- Bar colours (grey/green/red = source/sham/fault) agree with Fig. 4 but disagree with Figs. 5–6; see section 1.

**Fixes**
- (a): Add a thin white outline around the pasted label region in the sham/fault, a tag "liquid: cherry" on all three bottles, and "same type" / "different type" tags under the zoom strip.
- Put a shared legend above (b,c), 3 columns, 7 pt. Add a grey dashed line at 10% labelled "normal cutoff (10%)".
- Retitle "Pushpins (n = 138)" and "Juice (n = 89)".
- (d): Show both rules (pushpin as circles, juice as squares). Place the value labels to the *left* of the markers or above the CI caps with a 2-pt offset. Use a real minus sign, 7-pt labels and black markers.
- Write "Composition" in full (rotate the tick labels 0°, two lines).

---

### Fig. 8 — graph_audit

**Intended message:** The masked GNN's response to switches rides on a degree pathway; holding degree inputs or refitting with mean aggregation removes most of it.

**10-second test:** (c) works. (b) looks like four measured results, three of which coincide exactly at 50.

**Problems**
- **(b) plots "50.0 by construction" as estimates**, with markers and zero-width intervals in the same style as real estimates. That is misleading.
- **The text and figure don't map.** The text's "adding local gland spacing to typed centroid distance improves the edited-graph AUROC by **15.3** points" can't be found in (a), where "Geometry only" 64.0 → "Distance + spacing" 90.2 is a 26.2-point gap. Either the 15.3 comes from another table row (tables/switches.tex "Original length") or "Geometry only" ≠ "typed centroid distance". Rename the rows to the text's terms, or cite the supplement table in the caption.
- Colours: in (a,b) red = masked GNN and blue = others; in (c) red/blue/green have no semantic meaning and clash with the model palette elsewhere.
- (c) The value labels sit on the CI caps ("87.5" touches its cap).
- (a) and (b) both say "Target AUROC (%)" but measure different things (edited-graph rank vs response rank). The titles help, but the x-labels should differ.
- The axis ranges vary: (a) ~45–110, (b) 50–110, (c) 0–110. There is space past 100, which wastes ink.
- There is no schematic of a degree-preserving switch. One 0.6-in inset would make Sec. 6 understandable without reading it.

**Fixes**
- (b): Draw the three trivial rows as hollow grey markers with the text "fixed at 50 (cannot change)". Keep the masked GNN as the only filled marker.
- Single neutral colour; accent the masked GNN only.
- Put labels right of the CI cap with a 2-pt pad.
- x-labels: "Edited-graph AUROC (%)" and "Response AUROC (%)"; xlim [40, 100] / [45, 100] / [0, 100].
- Add a tiny inset: two edges removed (dashed red) and two added (solid), with node degrees unchanged.

---

### Fig. S — screw_discordant (supplement)

**Intended message:** Five discordant cases, where predicted fragments and merges make the counts differ from the physical inventory.

**10-second test:** No. Without a class legend or the RGB photo, the reader sees five orange squares with blue blobs.

**Problems**
- There is no class key: screws, nuts and washers are all the *same* light blue, so the screw/nut distinction that matters for the rule is invisible.
- The "thin fragments around the bag" and "merged foreground" named in the caption aren't marked. Fragments along the bag edge are 1–2 px slivers at 0.878× scale.
- The title colours (blue "Grid only" vs red-orange "Pairs only") are unexplained and reuse the model colours.
- There is no RGB reference, no predicted vs true counts, and no indication of what the "grid" and "pair" summaries are.
- Case 113 has a dark vertical line artefact on the right bag edge, which is unexplained.

**Fixes:** Add an RGB row above each map. Use a distinct colour per part class with a 7-pt legend. Add arrows/circles on the fragments and merges, and a per-case caption line "pred: 3 screws, 2 nuts · true: 2 screws, 2 nuts". Group the two kinds of case under two bracketed headers ("alert under grid only" / "alert under pair summary only") instead of colour-coded titles.

---

## 3. Caption–figure mismatches (checklist)

| Figure | Caption says | Figure shows |
|---|---|---|
| 1(b) | class-wide "lights up the whole tray" | 2 untouched cells not queued (11/13) |
| 1(b) | (implicit) masks of the fault | class-wide mask shows the source layout |
| 2 | "We change only the training target (green)" | green bracket over the network; no target drawn |
| 3 | median released fault-minus-sham photo | a different tray from Fig. 5's "median" photo |
| 3 | solid cyan marks the moved pin's compartment (sham) | conflicts with Fig. 1's cyan = target; T = ∅ for a sham |
| 4, 5c | curves recovered from the draft | digitised data in a final paper |
| 5c | — | 89.7 in the legend vs 89.6 in Table 1 |
| 5d | three cutoffs (fixed cost, 95%, 98%) | points not identified; class-wide s2 missing |
| 6 | thresholds pre-specified | a violation (seed 2 vs released, sham) is drawn like a pass |
| 7 | "at its own 10% normal cutoff" | no 10% line; sources alarm at 54–61% |
| 8 / text | +15.3 points from adding spacing | 64.0 → 90.2 (26.2) in (a) |
| S | fragments and merged foreground | nothing marked |
