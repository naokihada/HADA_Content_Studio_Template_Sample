# Prompt archive and review checklist

Use this workflow for every new infographic image prompt in a project that sets
`prompt_review_required: true`. It reviews the prompt before external image generation;
it does not call an image model or guarantee the resulting image.

This MAX5 workflow scores the prompt text only. It does not score or approve the
generated image. The post-generation review uses the separate fixed criteria and gates
in [the infographic review checklist](INFOGRAPHIC_REVIEW_CHECKLIST.md); never invent or
change those image criteria, weights, or score cutoffs.

The first authorized image-generation call is the intended production attempt, not a
disposable trial. Prepare and review the prompt to satisfy the fixed image criteria
below before calling the image service. Do not knowingly generate from a prompt with a
missing requirement or unresolved review finding. If the first result fails a hard gate,
record and report the failure; do not present that failure as expected or acceptable.
Generation is non-deterministic, so this preparation cannot promise a particular output.

## 1. Agree and save the brief

Confirm the intended result, audience, facts or source material, number of images,
composition, character and reference constraints, and exclusions with the user. Save
the agreed brief before drafting the prompt:

```text
projects/<domain>/<project-id>/productions/infographic/prompts/<prompt-id>.brief.md
```

Hash the saved brief and record its project-relative path and SHA-256 in the review
record. The brief is the agreed input; do not add unconfirmed project facts during
prompt drafting.

For the content proposal that feeds this brief, use the
[infographic proposal guideline](INFOGRAPHIC_PROPOSAL_GUIDELINE.md): state the exact
planned page-equivalent count and outline every page with its takeaway, three or more
unique information points, explanatory relationship, memory cue, evidence status, and
visual placement. A planned page is one SEU, not one output file; all planned pages may
be composed on one canvas unless the owner requests otherwise.

For a multi-output series, also read the project's
`extensions.content_studio.series_layout` setting. Record the effective orientation,
layout variation and any custom rule, additional shared elements, and next-page
anticipation in the brief.
The proposal and every selected page prompt must specify a page composition and reading
path consistent with the configured variation rule; under the default `maximum` rule,
each page must use a distinct dominant composition. Include the required page handoff
when enabled. Each output page must independently meet the four-SEU and
twelve-information-point minimum. Do not pool content requirements across the series or
silently replace project settings with the template defaults.

For every new infographic prompt, use `profiles/prompts/infographic-defaults.yaml`;
multi-output series use `profiles/prompts/infographic-series-defaults.yaml`. Read
`extensions.content_studio.character_visual_defaults.female_character`, include its
effective values in the brief and project/request prompt layer, and apply the female
character age, presentation, outfit, pants, outerwear, summer clothing, and swimwear
defaults wherever relevant. Explicit character canon, user instructions, and project
overrides take precedence over template defaults. Existing profile paths remain
available to validate historical prompt resolutions.

## 2. Put the fixed image requirements in the prompt

Before drafting candidate 1, outline at least four distinct, complete slide-equivalent
units (SEUs). Each SEU must carry a separate takeaway, at least three non-redundant
information units including that takeaway, an explicit explanatory relationship, and
a static memory cue. The whole infographic therefore needs at least 12 unique
information units, four explanatory relationships, and four memory cues. Do not count
repeated, decorative, or invented material. The infographic is a static memory aid:
exclude quizzes, exercises, fill-in-the-blank items, questions that request a response,
self-checks, and answer keys. If the agreed subject cannot support four accurate SEUs,
stop and report the shortfall before image generation.

The prompt must also explicitly require the same character in all three forms:

- one full-body view;
- one face close-up;
- one clearly recognizable chibi depiction.

Preserve the same identity anchors across all forms. The full-body and face close-up
must differ meaningfully in outfit, pose, and art style, and occupy clearly separate
areas with strong whitespace or another clear visual break. They must not read as one
connected or zoomed character composition.

When a female character is used, include the effective project wardrobe settings before
candidate 1: age/adult status, presentation, ordinary outfit, allowed pants and outerwear
contexts, summer short-sleeve target, and swimwear default where relevant. Under defaults,
use the adult 18-year-old female university-student presentation; dresses or one-piece
outfits; the specified uniform/fieldwork/special-attire exceptions for trousers and
outerwear; an open-front outer layer only with an above-knee skirt outside those contexts;
a one-piece competitive swimsuit for swimming; and about one-third short-sleeved summer
looks across distinct outfits. When the user has not specified an override, apply these
defaults even if the request says nothing about wardrobe.

The image-review score uses this fixed 100-point rubric. Put these priorities into the
prompt direction; do not ask an evaluator to invent weights or an image pass score.

| Criterion | Points | Required emphasis |
| --- | ---: | --- |
| Character appeal | 30 | Expressive, appealing presentation and face (12); strong, deliberate character presence (10); memorable pose, outfit, and styling while preserving identity (8). |
| Content richness | 30 | Four distinct, complete SEUs (12); clear explanations and relationships (10); accurate, specific, non-redundant information (8). |
| Layout and readability | 20 | Reading hierarchy and navigation (8); spacing, separation, and grouping (6); balanced placement of information and character (6). |
| Memory-support design | 10 | Static visual cues, diagrams, comparisons, and groupings that help recall the stated relationships. |
| Text and technical fidelity | 10 | Accurate, readable text at intended display size (6); clear, technically clean image (4). |

These image gates are non-compensating; a high weighted score cannot waive a failure:

- No practice, quiz, response question, blank, self-check, or answer key.
- At least four complete SEUs; no duplicated, decorative, inaccurate, or invented
  material used to reach the minimum.
- Full-body, face close-up, and chibi depictions are all present and clearly distinct.
- The same character remains recognizable across all depictions.
- Outfit, pose, and art style differ between the full-body and face close-up views.
- No factual/source errors or materially unreadable text.
- The full-body and face close-up views do not merge into one connected composition.
  If they do, Layout and readability is 0/20 and the image fails its gate.

There is no 90-point image acceptance threshold. Record each gate as pass/fail with
visible evidence. If no gate fails, report the score; the project owner makes the final
acceptance decision. The 90/100 threshold below applies to prompt candidates only.

## 3. Create a fixed rubric and candidate 1

Create one rubric from the brief. Use unique criterion IDs, include the
`instruction_clarity` criterion for tie-breaking, assign integer weights that sum to
100, and keep those criteria and weights unchanged for every candidate in this review.
Include these non-compensating critical checks with the exact IDs shown:

- `factual_accuracy`: factual or source accuracy;
- `explicit_constraints`: compliance with explicit user constraints;
- `contradictions`: absence of contradictory instructions.

Draft candidate 1 and store its complete text and SHA-256 in the review YAML. Evaluate
it against every rubric criterion. Record points, evidence, and a finding ID plus a
concrete finding for every criterion that did not receive its full weight. Record each
critical-check result and evidence. A critical-check failure caps the effective total
score at 89, regardless of the raw rubric sum. Save the brief, candidate 1, and review
YAML immediately with `status: in_progress`, before drafting a revision. After every
evaluation, append that candidate to the same review file without changing any earlier
candidate text, score, or evidence.

## 4. Revise from the previous findings

The pass threshold is **90/100, inclusive**. If the candidate is below 90, create the
next candidate from the immediately preceding one. The review record must identify the
prior candidate and map every prior finding ID to a specific change. Do not make an
unrelated rewrite in place of addressing those findings. Re-score with the same rubric.

Candidate 1 counts toward the maximum of five; at most four revisions are allowed. Stop
on the first candidate at 90 or higher if every critical check passes. If all five
candidates remain below 90, select the highest-scoring candidate, preserve the actual
score, and report that it missed the threshold. This below-threshold archive selection
is for audit only and does not authorize image generation. Do not submit a below-
threshold prompt as a disposable first attempt. For a tie, prefer fewer unsupported
assumptions and clearer instructions, and record the reason for the selection. Never
raise a score just to pass.

## 5. Record evaluator identity

For every evaluation, record the provider, API model ID, displayed model name, reasoning
strength, and evaluation timestamp as exposed by the runtime. Use `unknown` or
`not_exposed` for unavailable metadata; do not infer a model ID from a preference or
configuration. Do not switch to another evaluator automatically. If the evaluator is
unavailable or its observable identity changes during the review, stop and mark the
review `halted_evaluator_unavailable` or `halted_model_change`. Do not select a final
prompt or generate an image from a halted review.

## 6. Save the selected prompt before generation

For a completed review, save only the selected candidate's exact text, with no title,
code fence, or added commentary, to:

```text
projects/<domain>/<project-id>/productions/infographic/prompts/<prompt-id>.prompt.md
```

Use canonical UTF-8 text and LF line endings. Its text and SHA-256 must match the
selected candidate. Keep the review YAML beside it as
`<prompt-id>.prompt-review.yaml`. It stores the brief hash, fixed rubric, all candidate
text and hashes, scores and evidence, revision links and changes, evaluator metadata,
selection, and final prompt path/hash. Link the review to the matching immutable prompt
resolution record; the resolver remains the record of layered inputs and references.
The generation record separately stores available non-secret image-service arguments,
the argument file path/hash, provider details, and generated image hash. Do not put
credentials in any prompt or argument archive.

The YAML record uses `schema_version: "0.1.0"`. While the loop is running, use
`status: in_progress`, `prompt_resolution_id: null`, and null selected-candidate,
prompt-path, and prompt-hash fields. After selection, update only the status and final
selection/link fields; keep all candidate records unchanged. While in progress, set
`selection_reason: "Review in progress."` to satisfy the record schema. The outline below shows
its required field names; replace every placeholder and provide complete rubric,
criteria, and critical-check entries before validation:

```yaml
id: <prompt-id>
work_id: <infographic-production-id>
work_kind: infographic
status: selected_pass # or selected_below_threshold / a halted status
brief_path: projects/<domain>/<project-id>/productions/infographic/prompts/<prompt-id>.brief.md
brief_sha256: sha256:<64 lowercase hex characters>
prompt_resolution_id: <selected-resolution-id>
passing_score: 90
score_max: 100
max_candidates: 5
rubric:
  - {id: factual_content, label: Factual content, weight: 30}
  - {id: requirements, label: Explicit requirements, weight: 25}
  - {id: instruction_clarity, label: Clear instructions, weight: 25}
  - {id: visual_direction, label: Visual direction, weight: 20}
candidates:
  - id: <prompt-id>-candidate-1
    number: 1
    exact_prompt: <complete prompt text>
    prompt_sha256: sha256:<hash of exact_prompt UTF-8 text>
    raw_score: <sum of criterion points>
    total_score: <raw score, capped at 89 if any critical check fails>
    revision_of: null
    addressed_findings: []
    changes: []
    criteria: # one entry per rubric criterion; each records points and evidence
      - {criterion_id: factual_content, points: <0-30>, evidence: <specific evidence>}
      - {criterion_id: requirements, points: <0-25>, evidence: <specific evidence>}
      - {criterion_id: instruction_clarity, points: <0-25>, evidence: <specific evidence>}
      - {criterion_id: visual_direction, points: <0-20>, evidence: <specific evidence>}
    critical_checks: # all three IDs are required
      - {id: factual_accuracy, passed: true, evidence: <evidence>}
      - {id: explicit_constraints, passed: true, evidence: <evidence>}
      - {id: contradictions, passed: true, evidence: <evidence>}
    unsupported_assumption_count: 0
    evaluator:
      provider: <runtime value, unknown, or not_exposed>
      api_model_id: <runtime value, unknown, or not_exposed>
      displayed_model_name: <runtime value, unknown, or not_exposed>
      reasoning_strength: <runtime value, unknown, or not_exposed>
    reviewed_at: <ISO-8601 timestamp with timezone>
selected_candidate_id: <candidate-id>
selected_prompt_path: projects/<domain>/<project-id>/productions/infographic/prompts/<prompt-id>.prompt.md
selected_prompt_sha256: sha256:<hash of exact selected prompt text>
selection_reason: <brief explanation>
```

Repeat the candidate structure for each revision, setting `revision_of` to the prior
candidate ID and listing each previous finding ID in both `addressed_findings` and
`changes`. A halted review has no selected candidate, prompt file, prompt hash, or
resolution ID; it records `halt_reason` and explains the stop in `selection_reason`.
For a model change, include the newly observed runtime values in `observed_evaluator`.

Run `python tools/validate.py` before external generation. If validation fails, fix the
archive record without rewriting an existing candidate; if the candidate text changes,
create a new candidate and update its review history. Do not ask the user to approve the
prompt again after the brief has been agreed. Do not begin generation until the review
archive validates and its status is `selected_pass`, the selected candidate scores at
least 90, every critical check passes, and the prompt explicitly includes the fixed
content and image gates above. A `selected_below_threshold` review is not generation-
eligible.

## 7. Make the first production attempt and retain the provenance

Use the selected prompt for one external production attempt. Do not make a knowingly
deficient first attempt, retry automatically, or silently switch models. Evaluate the
result against [the fixed image-review checklist](INFOGRAPHIC_REVIEW_CHECKLIST.md),
record visible evidence for every score and gate, and do not mark a gate-failing result
accepted. Preserve the review archive and report any failure; the policy does not treat
a failed first result as an acceptable trial. Any further generation requires an owner-
directed next step and a new prompt review. Record generated sources through
`tools/intake_asset.py` with both `--prompt-resolution-id` and `--prompt-review-id`.
Generation provenance holds provider/model details and the source image hash; the
review record holds the prompt and review history. Generated source images remain
private masters and are never published directly. The validator permits only one
generation intake record for a prompt review, but cannot detect unrecorded external calls.

## Historical records

Existing prompt resolutions and image-generation records that predate this gate remain
unchanged. Do not re-score them or describe them as pre-reviewed. A project without
`prompt_review_required: true` may retain those legacy records; new project examples
enable the gate.
