# Infographic Proposal Guideline

Use this guideline whenever proposing or planning a new infographic. The proposal is a
content and visual plan that makes the scope reviewable before prompt drafting. It does
not generate an image or replace the prompt and image reviews.

## Page-equivalent plan

State an exact number of planned pages, with a minimum of **four**. In this plan, one
page is one complete slide-equivalent unit (SEU); it is not one final image file or one
physical output page. Unless the owner asks for multiple outputs, the planned pages may
be arranged together on one infographic canvas. Choose the count from the actual scope
and list every planned page. Do not write only “four or more” or leave later pages
unspecified.

For each planned page/SEU, provide:

1. **Title or focus:** a concise subject that distinguishes the page from the others.
2. **Takeaway:** one clear, declarative point the reader should remember.
3. **Key information:** at least three specific, countable, non-redundant information
   points, including the takeaway. Names of topics or labels alone do not count.
4. **Explanation:** how the points relate, such as why, how, when, under what condition,
   cause and effect, contrast, or category membership.
5. **Memory cue:** a static diagram, comparison, visual grouping, mnemonic, or complete
   solved reference example that makes the relationship easier to recall.
6. **Evidence status:** known source(s), user-stated decision, or clearly identified
   unresolved fact. Do not present an inference or proposal as a verified fact.
7. **Visual placement:** a brief indication of how the information will be grouped or
   read on the final canvas.

Across the proposal, count each information point once. The minimum is four complete
SEUs, 12 unique information points, four explanatory relationships, and four memory
cues. Do not inflate those totals with repeated, decorative, unsupported, or invented
material. If the scope cannot support the proposed count accurately, state the shortfall
and offer a specific expansion or split before drafting a prompt.

## Overall proposal requirements

State the working title, audience, purpose, scope, intended language, planned page count,
and intended final output count. Show how the pages connect into one coherent reading
order. The proposal must be specific enough that the owner can judge both content
coverage and visual direction without having to ask what a page will contain.

Treat the infographic as a static memory aid. Exclude quizzes, exercises, fill-in-the-
blank items, response questions, self-checks, and answer keys. A complete, solved
reference example is allowed only as explanation or a memory cue; it must not ask the
reader to solve it.

## Multi-output series layout

Apply this section when a production is a sequence of separate infographic outputs.
Series output pages are distinct from SEUs: an SEU is a complete knowledge unit, while
an output page is one finished image or page in the sequence.

Read `extensions.content_studio.series_layout` from the mini-project settings. If it is
absent, select one orientation for the series and use these defaults: `maximum` layout
variation, no additional shared visual elements, and required next-page anticipation.
Project settings override these defaults. For `layout_variation: custom`, provide a
non-empty `layout_variation_details` rule. State the effective settings in the proposal.

List every final output page and assign its SEUs to it. Each infographic output still
needs at least four complete SEUs and twelve unique information points; never pool
these minimums across the series.

For every output page in the series, specify its content focus, dominant composition,
focal placement, reading path, and page-specific visual handoff to the next output.
Under `maximum` variation, give each page a distinct dominant composition and reading
path; avoid repeating page skeletons, panel maps, character placement, or other design
elements unless the project explicitly permits that shared element or a documented
content/readability constraint requires an exception. Keep the selected portrait or
landscape orientation constant across the series. Do not add recurring title bars,
color systems, grids, or other visual furniture by habit: these require an explicit
project setting.

Make the next output feel worth seeing through a visual preview or transition into its
subject. Do not turn the handoff into a question, quiz, exercise, or withheld explanation.
Every output page must remain factually complete within its own scope; give the final
page a clear close. The orientation, settings, and page-by-page layout decisions must
also appear in the exact prompt and be checked before generation.

## Character and composition plan

Every infographic proposal includes the same character in three distinct depictions:
full body, face close-up, and chibi. State the identity anchors to preserve across all
depictions. Give full-body and face close-up views separate, clearly bounded areas with
strong whitespace or another clear visual break. Specify a meaningful change in outfit,
pose, and art style between those two views. Do not connect them into one zoomed
character composition. Reserve deliberate visual presence for the character; information
density must not erase the character's appeal. If no character has been selected, record
that selection as a material unresolved decision and do not present the proposal as
ready for prompt drafting.

For a female character, read `extensions.content_studio.character_visual_defaults.female_character`.
Use explicit character canon and direct user instructions first, project overrides next,
and template defaults when no value is set. The defaults are an adult 18-year-old neat,
refined, beautiful female university student; ordinary outfits are dresses or one-piece
garments; trousers are limited to uniforms, fieldwork, or special attire; and outerwear
is disallowed except in those contexts or as an open-front layer with an above-knee
skirt. Swimming defaults to a one-piece competitive swimsuit. Across the distinct outfit
looks planned for a production or series, target about one-third short-sleeved summer
clothing. Count unique looks once, not repeated depictions. State the effective values
and any override in the proposal, and ensure the full-body and face-close-up outfits
remain distinct under these rules.

## Fixed image-review target

Shape the visual proposal around the fixed post-generation rubric; do not invent or
change weights or acceptance cutoffs.

| Criterion | Points | Proposal direction |
| --- | ---: | --- |
| Character appeal | 30 | Expressive face and appeal (12); strong, deliberate character presence (10); memorable pose, outfit, and styling while preserving identity (8). |
| Content richness | 30 | Four distinct, complete SEUs (12); clear explanations and relationships (10); accurate, specific, non-redundant information (8). |
| Layout and readability | 20 | Reading hierarchy and navigation (8); spacing, separation, and grouping (6); balanced placement of information and character (6). |
| Memory-support design | 10 | Static visual cues, diagrams, comparisons, and groupings that support recall. |
| Text and technical fidelity | 10 | Accurate, readable text at intended display size (6); clear, technically clean image (4). |

The image has non-compensating gates: at least four complete SEUs; no practice/test
content; all three character depictions with identity preserved; varied outfit, pose,
and art style between full-body and close-up; accurate information; readable text; and
separate full-body and close-up layouts. If the full-body and face close-up merge into
one composition, layout scores 0/20 and the image fails its gate. The image has no
90-point pass threshold; record gate evidence and leave final acceptance to the project
owner. The separate 90/100 threshold applies to prompt text only.

Prepare the first authorized generation as the intended production attempt. Do not
propose a disposable first draft of the image or proceed with a below-threshold prompt.
Generation requires a validated `selected_pass` review with all critical checks passing
and every content and visual gate represented in the exact prompt. If the generated
image still fails a gate, reject it, record visible evidence, and report the failure;
automatic retries are not allowed. A later attempt requires an owner-directed next
step and a new prompt review.

## Proposal format

Use this structure and replace every placeholder with concrete content. Add a page
section for every planned SEU; do not stop at four when the subject needs more.

```markdown
# Infographic proposal: <working title>

- Audience: <specific audience>
- Purpose: <what the infographic should help the audience understand or recall>
- Scope: <included subject and boundaries>
- Language: <language>
- Planned page-equivalents (SEUs): <exact integer, at least 4>
- Final output: <one canvas or the explicitly requested number of outputs>
- Reading order: <how the page-equivalents connect>

## Series layout (only for multiple output pages)
- Orientation: <portrait or landscape, fixed for this series>
- Layout variation: <maximum or custom, with the exact custom rule>
- Additional shared elements: <only those explicitly listed in project settings>
- Next-page anticipation: <required, optional, or disabled>
- Output page 1: <content focus; its SEUs; dominant composition; focal placement; reading path; handoff>
- Output page 2: <its SEUs; distinct page-specific layout and handoff; continue for every output>

## Page 1 — <specific focus>
- Takeaway: <one declarative point>
- Key information:
  1. <specific, countable point>
  2. <specific, countable point>
  3. <specific, countable point>
- Explanation: <relationship among the points>
- Memory cue: <static visual cue>
- Evidence: <source, user decision, or unresolved item>
- Visual placement: <grouping or reading direction>

## Page 2 — <specific focus>
- Takeaway: <one declarative point>
- Key information:
  1. <specific, countable point>
  2. <specific, countable point>
  3. <specific, countable point>
- Explanation: <relationship among the points>
- Memory cue: <static visual cue>
- Evidence: <source, user decision, or unresolved item>
- Visual placement: <grouping or reading direction>

## Page 3 — <specific focus>
- Takeaway: <one declarative point>
- Key information:
  1. <specific, countable point>
  2. <specific, countable point>
  3. <specific, countable point>
- Explanation: <relationship among the points>
- Memory cue: <static visual cue>
- Evidence: <source, user decision, or unresolved item>
- Visual placement: <grouping or reading direction>

## Page 4 — <specific focus>
- Takeaway: <one declarative point>
- Key information:
  1. <specific, countable point>
  2. <specific, countable point>
  3. <specific, countable point>
- Explanation: <relationship among the points>
- Memory cue: <static visual cue>
- Evidence: <source, user decision, or unresolved item>
- Visual placement: <grouping or reading direction>

## Character and visual direction
- Identity anchors: <stable features>
- Full-body view: <outfit, pose, and style>
- Face close-up: <distinct outfit, pose, and style; clearly separate area>
- Chibi depiction: <recognizable same character>
- Female-character settings: <effective project values/overrides, or not applicable>
- Distinct outfit looks: <list contexts and outfits; note pants/outerwear exceptions>
- Summer short-sleeve target: <count/total distinct looks, approximately one-third by default>
- Swimming outfit: <configured default or explicit override, when relevant>
- Layout: <information hierarchy and separation>

## Exclusions and unresolved decisions
- Exclusions: <explicitly excluded content>
- Decisions needed: <only material unresolved items>
```

## Internal application

Apply this structure by default when the owner asks for an infographic proposal, plan,
or production. Do not require the owner to invoke the guideline by name or restate its
criteria. Present the page count, page-by-page points, visual direction, and only
material unresolved decisions as the natural proposal; do not add an announcement about
internal checks. A proposal must not imply that the image has already been generated,
reviewed, or accepted.

See [the infographic content and image review checklist](INFOGRAPHIC_REVIEW_CHECKLIST.md)
for the complete SEU, character, scoring, and hard-gate review record, and
[the prompt review checklist](PROMPT_REVIEW_CHECKLIST.md) for the separate MAX5 prompt
review before generation.
