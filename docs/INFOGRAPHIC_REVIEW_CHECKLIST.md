# Infographic Content and Image Review

Use this standard for every new Content Studio infographic. An infographic is a static
memory aid and reference: it organizes knowledge so the viewer can recall it later. It
is not a worksheet, lesson exercise, or test.

The MAX5 workflow in [PROMPT_REVIEW_CHECKLIST.md](PROMPT_REVIEW_CHECKLIST.md) checks
the prompt before generation. It does not evaluate the generated image. This checklist
is the fixed post-generation standard. Do not let an evaluator invent or change its
criteria, weights, hard gates, or score cutoff.

Before drafting the prompt, prepare a decision-ready, page-by-page outline using the
[infographic proposal guideline](INFOGRAPHIC_PROPOSAL_GUIDELINE.md). State the exact
number of planned page-equivalents (at least four); each page-equivalent is one SEU,
even if the final output combines all of them on one canvas.

## Content plan: at least four slide-equivalent units

Outline at least **four distinct, complete slide-equivalent units (SEUs)** before
generation. Each SEU is one self-contained information module with:

1. One distinct concept, distinction, process, cause, or take-away.
2. At least three countable, non-redundant information units in total, including the
   take-away.
3. An explicit explanatory relationship, such as why, how, when, condition,
   cause-and-effect, contrast, or category membership.
4. At least one static memory cue, such as a diagram, comparison, visual grouping,
   mnemonic, or complete worked reference example.

The minimum is therefore four complete SEUs, at least 12 unique information units,
four explanatory relationships, and four memory cues. Count an idea only once across
the whole image. Headings, repeated statements, decorative art, and character
illustrations do not count. A static example may count only for the unique information
it contributes; it must be complete and must not ask the viewer to solve it.

Exclude quizzes, exercises, fill-in-the-blank items, questions that request a viewer
response, self-checks, and answer keys. Declarative headings and informative process
sequences are allowed. Do not pad a small topic with repetitions or invented facts. If
the brief cannot support four accurate SEUs, report the shortfall and expand the scope
or split it into multiple infographics before generation. Keep text readable by
expanding the canvas or splitting content into panels/images rather than shrinking it.

## Required character depictions

Show the same character in at least three clearly distinguishable depictions:

- one full-body view;
- one face close-up;
- one clearly recognizable chibi depiction.

Preserve the character's identity anchors across all depictions. The full-body and face
close-up views must meaningfully differ in outfit, pose, and art style. Give them
strongly separate areas with clear whitespace or another clear visual break. A thin
divider or small gutter between immediately adjacent views is not enough. Do not make
them look like one continuous zoomed-in/zoomed-out character panel.

## Female-character appearance and wardrobe defaults

When the image contains a female character, read the effective project setting at
`extensions.content_studio.character_visual_defaults.female_character`. Check against
the explicit character canon and user instructions first, then project overrides, then
the defaults. If using defaults, confirm an adult age of 18 and the neat, refined,
beautiful female university-student presentation; ordinary outfits are dresses or
one-piece garments; trousers appear only for a uniform, fieldwork, or special attire;
and outerwear appears only in those contexts or as an open-front layer with an above-
knee skirt. Swimming defaults to a one-piece competitive swimsuit. For a production or
series, count distinct outfit looks once and compare the short-sleeved summer looks with
the configured target (about one-third by default). Record any explicit override and
visible evidence. This is a policy-conformance gate; it adds no rubric points and changes
none of the fixed score weights.

## Additional review for a multi-output series

Read the effective project setting at `extensions.content_studio.series_layout`. Across
the series, verify that every output uses the configured portrait/landscape orientation.
Unless the project explicitly lists additional shared elements, orientation is the only
visual/layout element to standardize. Compare all output pages together and confirm that
their dominant compositions and reading paths vary at the configured level; under the
default `maximum` setting, each should have a distinct composition. Record any exception
and its content/readability reason. When next-page anticipation is `required`, each
non-final page needs a page-specific visual handoff, and the final page needs a clear
close. Handoffs must not turn into questions, tests, or withheld explanations.

This is a series-level policy check in addition to each image's fixed rubric. It does
not add score points, change the rubric weights, or waive any per-image requirement.

## Fixed 100-point image rubric

| Criterion | Points | Evidence to score |
| --- | ---: | --- |
| Character appeal | 30 | 12: expressive, appealing design and face. 10: strong, deliberate character presence. 8: memorable pose, outfit, and styling while preserving identity. |
| Content richness | 30 | 12: four distinct, complete SEUs. 10: clear explanations and relationships. 8: accurate, specific, non-redundant information. |
| Layout and readability | 20 | 8: reading hierarchy and navigation. 6: spacing, separation, and grouping. 6: balanced placement of information and character. |
| Memory-support design | 10 | Visual cues, diagrams, comparisons, and groupings help recall the stated relationships without asking the viewer to perform a task. |
| Text and technical fidelity | 10 | 6: text is accurate and readable at intended display size. 4: image is clear and technically clean. |

Score each criterion with visible evidence and give the total out of 100. An equivalent
score out of 10 may be shown by dividing the total by ten. Do not apply the prompt
review's 90-point threshold to the generated image. Do not invent an image acceptance
cutoff. A failed hard gate means reject; otherwise report the score and leave final
acceptance to the project owner.

## Non-compensating hard gates

Any failure blocks acceptance, regardless of the weighted total:

- The infographic contains any practice, quiz, response question, blank, self-check, or
  answer key listed above.
- It has fewer than four complete SEUs or relies on duplicated, decorative, inaccurate,
  or invented material to reach the minimum.
- It is missing the full-body, face close-up, or chibi depiction.
- The character's stable identity cannot be recognized across depictions.
- The full-body and face close-up do not vary outfit, pose, and art style.
- Effective female-character appearance and wardrobe settings are not followed where applicable.
- A factual/source error or materially unreadable text remains.
- The full-body and face close-up visually merge into one connected composition. Set
  **Layout and readability to 0/20** and reject it, regardless of other points.

State each gate as pass/fail and cite visible evidence. For a connected-layout failure,
identify the two affected views and explain what makes them read as one composition.

## Review record

Save a Markdown report at `assets/generations/<generation-id>/image-review.md`, beside
`provenance.yaml`, before marking a generated image accepted or exporting it. Include:

```markdown
# Infographic image review

- Generation ID:
- Source image SHA-256:
- Prompt review ID:
- Review date:

## Planned SEUs
- Planned page-equivalent count:
- SEU-1: takeaway; information units; relationship; memory cue
- SEU-2: takeaway; information units; relationship; memory cue
- SEU-3: takeaway; information units; relationship; memory cue
- SEU-4: takeaway; information units; relationship; memory cue
- Add one SEU entry for each planned page-equivalent beyond four.

## Scores
- Character appeal: __/30 — evidence:
- Content richness: __/30 — evidence:
- Layout and readability: __/20 — evidence:
- Memory-support design: __/10 — evidence:
- Text and technical fidelity: __/10 — evidence:
- Total: __/100 (__/10)

## Hard gates
- No practice/test content: pass/fail — evidence:
- Four complete SEUs: pass/fail — evidence:
- Full-body, face close-up, and chibi shown: pass/fail — evidence:
- Same-character identity preserved: pass/fail — evidence:
- Outfit, pose, and art style differ between full-body and close-up: pass/fail — evidence:
- No connected full-body/close-up composition: pass/fail — evidence:
- Accurate and readable: pass/fail — evidence:
- Female-character visual defaults/overrides followed when applicable: pass/fail — evidence:
- Unique short-sleeve summer outfits: __ / __; configured target:
- Swimwear default/override followed when applicable: pass/fail — evidence:

## Series policy review (complete for multi-output series)
- Effective settings: orientation; layout variation/details; additional shared elements; next-page anticipation
- All pages use the configured orientation: pass/fail — evidence:
- Every output independently meets its SEU and information-point minimum: pass/fail — evidence:
- Page compositions and reading paths vary as configured: pass/fail — evidence:
- Any repeated layout element is explicitly configured or documented as necessary: pass/fail — evidence:
- Required next-page handoffs and final-page close are present: pass/fail — evidence:
- Series policy gate: pass/fail

## Result
- Gate result: pass/fail
- Owner acceptance: pending/accepted/rejected
- Notes:
```

This is a review record, not a prompt or a source of facts. Do not change or backdate
reviews after acceptance; append a new review if a new generated version is evaluated.
