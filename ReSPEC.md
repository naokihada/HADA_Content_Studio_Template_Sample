# ReSPEC — Local Sample

**Review date:** 2026-11-02
**Package role:** sample
**Template version:** 0.1.0
**Declared fictional character:** Cute Elf Girl

## Observed implementation

- Exactly one persistent character record exists. The chibi version 0.2.0 keeps the
  same character ID and named identity anchors. The first chibi request did not shorten
  the proportions enough; its source and prompt history remain local as a style study,
  while version 0.2.0 is the chibi used in the infographic.
- A clothing item, item variant, outfit, and character-item relationship are stored
  independently. The infographic shows that one reusable item can link to multiple
  characters.
- Four private source masters and their prompt-resolution records are retained locally.
  No raw master or exact prompt is included in the infographic.
- The Japanese capability infographic is preserved as a source master and has two
  watermarked derivatives. Website output is 1600 x 2320 PNG; social output is
  497 x 720 JPEG. All five derivative records have clean metadata scans and remain
  ready for human review.
- The local Sample has no publication record and did not upload or publish anything.

## Validation

- 12/12 unit tests pass.
- The Sample role validator passes; all character, item, prompt, source, and derivative
  references resolve.
- Repeated infographic-source renders matched byte-for-byte before the temporary
  previews were removed.
- The Sample stays uncommitted at its original Git commit.