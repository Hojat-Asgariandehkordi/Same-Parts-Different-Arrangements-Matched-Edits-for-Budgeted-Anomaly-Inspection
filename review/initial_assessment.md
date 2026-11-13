# Initial AC assessment: "Same Parts, Different Arrangements: Matched Edits for Budgeted Anomaly Inspection"

## Scores (0-10, internal)
| Criterion | Score |
|---|---|
| Originality and significance | 6 |
| Technical soundness | 6 |
| Strength of evidence | 5 |
| Clarity | 5 |
| Presentation (figures, tables, layout) | 6 |
| **Overall** | **5.5 (borderline)**; confidence 3.5/5 |

## 1. Contribution (one sentence)
The paper builds matched valid/invalid pin relocations on 138 MVTec LOCO pushpin photos, defines an inspection-cost metric (untouched compartments queued at a 95%-recall cutoff set on development data), and shows that SALAD's composition branch queues 11.07/13 untouched compartments because its class-wide training target is too broad. Marking only the pasted footprint cuts this to 0.20-0.45 (Tab. 1, Sec. 4.2).

## 2. Five most consequential objections
1. **The narrow scope limits how far the results generalise (b).** The main result uses one category (pushpins), one detector (SALAD, composition branch only) and synthetic composites. The Limitations section says the edits "are not physical rearrangements" (p.8, l.431-433), and native LOCO results are moved to the supplement. The juice experiment (Sec. 5) and the GlaS/HVSMR graphs (Sec. 6) only probe branch choice and a degree pathway. They do not test the cost claim. Reviewers will want the cost metric on at least one more detector (e.g. a component-based method [9,13,15,21]) and on native LOCO faults.
2. **The causal attribution rests on a weak control (b).** The prespecified class-wide control "fail[s] the competence criterion" (Sec. 4.2 "Class-wide control", l.331-332). Mechanistic claims therefore "rest on the continuation ... for which one seed passes" (l.436-438). In that continuation the reduction is only 11.50 -> 7.07 (Sec. 4.3), far from the 0.20 shown in the abstract. The abstract does not separate the effect of the target from the effect of rule-aware training edits.
3. **The abstract hides a trade-off in specificity and ranking (a/b).** For seed 2, sham alarms rise from 7 to 20 (+9.4 pp [2.2, 16.7], l.322-323), which is above the 5-point margin against the released model. Top-2 falls to 74.6%, below the released 77.5% (Tab. 1). The abstract still says "without losing any detection", and the conclusion says nothing about the sham increase. More seeds are needed (b), and the claims should be stated with this caveat (a).
4. **A trivial baseline undercuts significance (b).** Sec. 5 notes that "an explicit one-pin-per-compartment rule applied to the same extracted maps raises no sham alarm while detecting every fault" (l.366-369). Training also uses edits built from the test rule (l.427-431). Reviewers will ask what the learned head adds over the rule, and whether rule-aware training leaks the evaluation rule. The paper needs the rule's own R/C in Tab. 1 and a test on a rule the training did not see.
5. **The paper is diffuse, and Sec. 6 does not belong (a).** Sec. 6 adds histology and cardiac graphs, a masked GNN and degree-preserving switches. This is a different problem (link prediction) with its own claims, and it uses a page that the core evidence needs, such as the oracle table and the native-fault results. The contribution list (l.070-073) and the abstract's last sentence spread the paper's message thin.

## 3. Presentation problems
**Figures**
- Fig. 1 works as a graphical abstract: the matched edits are on the left and the two training targets with their queues are on the right. However, the "15 of 15" schematic exaggerates the measured 11.07, and the caption has to correct it. The small sub-captions in (a) run into each other: "...no target" and "moved within its compartment; no target" collide across the panel gap. The grey notes in (b) ("grey: vacated spot, marked in both") are about 6 pt.
- Orange has three meanings: "fault" (Figs. 1a, 4, 7), "queued untouched" (Figs. 1b, 5a) and the t_c marker. Purple/green for class-wide/footprint is consistent across Figs. 1, 5 and 6, but in Fig. 6 colour encodes the comparator rather than the method, and the upstream-only rows use a third mauve.
- Fig. 2: much of the text is tiny ("oracle: same edit applied to the released label map", the development-data box). The illustrative score grid is helpful.
- Fig. 3: the caption says "Top: median released fault-minus-sham difference", but the right-hand panel and the caption itself use |S^fault - S^source|. It needs to be clear whether the reference is the sham or the source.
- Fig. 5: the cell numbers in (a,b) are unreadable at print size. In (d), the legend uses a dark filled circle for both "released" and "95% cutoff", so shape and colour encodings clash. A hollow square near recall 39% is never explained in the text. The broken axis is hard to read.
- Fig. 6 is dense (three panels, 14 rows). It earns its space as the primary result, but the row labels are small.
- Fig. 8 (GlaS) does not earn its space in a pushpin-centred paper.

**Structure**
- Sec. 4 runs on bold paragraph lead-ins: "Implementation details", "Cost at calibrated operating points", "Source of the cost", "Other operating points", "Seed sensitivity", "Class-wide control". Sec. 2 has four more and Sec. 5 has two. This fragments the argument.
- The contribution bullets (l.059-073) repeat the abstract, and the Conclusion (Sec. 8) repeats both. The Conclusion ends on a general recommendation rather than a takeaway or an outlook.
- Secs. 5 and 6 read as appendices promoted into the main paper.

**Numbers**
- Most numbers agree across the abstract, Tab. 1, the text and the figures. I checked 11.07, 0.20/0.45, 7/9/20 shams, 77.5/87.7/74.6 top-2, and +84.3/+79.8/-3.4 in Fig. 7. Two minor discrepancies:
  - "10.88" (l.297) against 11.07 - 0.20 = 10.87 is a rounding difference.
  - "+9.4 points" for 87.0 - 77.5 = 9.5 (l.267) comes from unrounded counts.
- The abstract quotes "0.20 and 0.45", but the paper's own mechanistic estimate is 4.43 (Sec. 4.3). The abstract therefore overstates the target-only effect relative to the evidence.
- The oracle values (10.30, 10.04; l.304) cite a table that is only in the supplement.

**Undefined or overloaded symbols**
- i is overloaded: it indexes photos in Sec. 3 and nodes in d_i (Sec. 6, l.411). d_i, a_e and z_e are introduced only in passing.
- The weight 5 in Eq. 4 is not explained.
- j and g_j in Algorithm 1 are not tied to D's indexing in the text.
- "pp" is used before it is defined.
- t_s values differ between figures (0.158 in Fig. 3, oracle) with no note that they are per-interface.

## 4. Three highest-value non-scientific changes
1. **Restructure around the single claim.** Shrink Sec. 6 to a short paragraph, or move it to the supplement. Use the freed space to merge the bold mini-paragraphs of Sec. 4 into three connected subsections: diagnosis, cost, and attribution with its caveats. Pull the oracle table into the main paper.
2. **Revise the abstract and conclusion to state the caveats.** These are the seed-2 sham increase, the control that fails competence, the 4.43 continuation effect and the explicit-rule baseline. Replace the repetitive conclusion with a specific takeaway and a direction for future work.
3. **Fix the figure encodings.**
   - Assign one colour per meaning across all figures: fault vs. queued-untouched, method vs. comparator.
   - Fix the Fig. 3 caption (sham vs. source reference).
   - Enlarge or remove the cell numbers in Fig. 5a,b and redesign the Fig. 5d legend.
   - In Fig. 1, either use the measured 11 queued compartments in the schematic or label it "illustrative", and fix the colliding sub-captions.
