# Finalization: paper 4, "Same Parts, Different Arrangements"

**Mode:** submission-length version checked against the official CVPR 2027 author kit (review mode). Everything up to and including the LLM statement fits in 8 pages; the references start on page 9.

**Constraint from the authors:** do not change the scientific content. Only the figures, structure and paragraphs were changed.

**One-sentence contribution (working note):** matched valid and invalid edits show that a logical anomaly detector which detects every fault still sends the inspector to almost every compartment, and that marking only the pasted part during training removes this cost.

## Initial independent assessment (fresh reviewer, rubric 0–10)
- **Overall:** about 5.5 (confidence 3.5/5).
- **Rubric scores:** originality 6, soundness 6, evidence 5, clarity 5, presentation 6.
- **Full report:** `review/initial_assessment.md`.

## Round 1: story and structure
- **Contributions:** now four connected sentences under "Our paper offers the following contributions", with short bold labels (evaluation design, diagnosis, remedy, transfer checks). The intro also states the two research questions explicitly.
- **Related work:** four mini-sections merged into two connected paragraphs.
  1. Detectors and synthetic supervision, ending with what this line of work leaves unresolved and what we study.
  2. Matched and counterfactual testing, calibration and graph masking.
- **Experiments:** all 7 bold lead-ins removed. Each is replaced by a transition sentence that leads into the paragraph. "Implementation details" is kept, as is standard for CVPR.
- **Limitations and conclusion:** merged into one Conclusion. It answers the introduction's questions, states the scope, and names three concrete next steps.
- **Abstract:** now states that one seed raises more false alarms on valid edits. This is evidence that materially affects the interpretation, and the reviewer flagged that it was missing.

## Round 2: figures, captions, consistency
- **One meaning per colour:** queued compartments changed from orange to pink. Orange had been too close to the vermilion used for faults (reviewer objection).
- **Fig. 1:** the class-wide schematic now queues 11 of 13 untouched compartments ("13 of 15 opened"), matching the measured 11.07; before, it showed 15 of 15. Panel (a) labels no longer collide.
- **Fig. 5:** the per-compartment numbers in (a,b) were unreadable at print size and were removed; the caption gives the cutoffs. Model colours in (d) are now swatches, so they are no longer confused with cutoff markers.
- **Captions:** Figs. 2, 3, 4, 6 and 8 now open with their takeaway. Fig. 3 says precisely how the photo was selected and what the right column shows.
- **Notation and terms:**
  - Graph nodes are now u and v. The letter i is reserved for photos, and z_e, a_e and d_u are defined.
  - Eq. 4's weight of 5 is explained, and "pp" is defined at first use.
  - "alert" and "cell" are replaced by "alarm" and "compartment" in every pushpin table file.
  - "locked" is replaced by "pre-specified".
- **Disclosure:** the LLM statement now says that parts of Figs. 1 and 2 were generated with BioRender, with labels typeset separately. This matches actual use. The captions also credit BioRender; add the named citation at camera-ready.
- **Number checks:** the reviewer's "10.88 vs. 10.87" is the paired estimate versus the difference of rounded means; both are correct. +9.4 = (20 − 7)/138. The abstract, text, Tab. 1, Fig. 5 and Fig. 6 agree.

## Objections that need new evidence, not writing (left for the group)
1. **Scope:** one category, one detector, and synthetic composites only. The smallest decisive test is physical rearrangements of a few real trays, scored with the same cutoffs.
2. **Mechanism:** the rule-aware class-wide controls fail the competence criterion, so attribution rests on the upstream continuation (11.50 → 7.07, seed 2). The decisive test is a second passing upstream seed, or a full retrain with footprint targets.
3. **Seed 2:** sham alarms rise to 20 (+9.4 pp versus the released model, within the pre-specified margin versus the control). A third seed would show whether this is variance.
4. **Graph section:** the reviewer judged it off-topic. Moving it to the supplement would free about two-thirds of a page for the oracle table; that is a content decision for the authors.
5. **An explicit rule is a strong baseline:** it is perfect when the rule is known. The paper reports this fairly. The framing (learned detectors must also cover unknown rules) could be stated earlier if the authors agree.

## Final independent assessment (fresh reviewer, same rubric)
- **Overall:** 6.2, up from about 5.5 (confidence 3/5). "Borderline, leaning weak accept."
- **Rubric scores:** originality 6.5, soundness 6.5, evidence 5.5, clarity 6.5, presentation 7.0.
- **Numbers:** they agree across the abstract, Fig. 1, Tab. 1, the text and supplement Tab. 3.
- **Full report:** `review/final_assessment.md`.

## Round 3: the reviewer's remaining fixable items
- **Fixed-cost cutoff:** stated in the main text as a strict comparison, matching the supplement. It was the only numerical-definition inconsistency.
- **Competence criterion:** now named explicitly in Sec. 3.5.
- **Conclusion:**
  - It no longer claims region overlap hides the cost; region overlap ranks, while the recall–cost pair states the cost.
  - The recommendation is scoped to settings where parts are tied to locations.
- **Fig. 5(d):** model colours are now lines, so they are not confused with the square marker. The caption notes that the two class-wide points overlap.
- **Fig. 4:** panel letters no longer collide with the 100% tick.
- **Fig. 8:** neutral grey and black; red no longer takes on a new meaning.
- **Fig. 1(a):** heading is now "illustration". BioRender's curved sham arrow is still there; the motion is a translation.

## Where this stops and why
All remaining major objections need new evidence, not writing (see the list above). Under the authors' instruction not to change the content, this is the strongest version the existing evidence supports. The internal target of 7.5 is not met. The obstacle is evidence breadth (one category, synthetic edits, two seeds, a failed primary control), not presentation.

The best next action is to score the two fine-tuned heads on native LOCO pushpin faults and a handful of physically rearranged trays, and add a third seed. This uses the same cutoffs and scripts; no new method is needed.
