# Image asset lifecycle

Install the pinned dependencies with `python -m pip install -r tools/requirements.txt`.
Provide a project-owned transparent logo at the path named by the export profile before
running an export. The reusable example profiles refer to
`assets/branding/watermark.png`; the Template does not ship a personal brand logo.

## 1. Keep generated sources

After reviewing an image, explicitly choose whether it is an accepted master or a
discard candidate. Intake copies the original PNG/JPEG bytes and leaves the input where
it is. It never edits or deletes the input, and it refuses an existing target:

```powershell
python tools/intake_asset.py `
  --source C:/path/to/generated-image.png `
  --generation-id elf-reference-gen-v1 `
  --asset-id elf-reference `
  --asset-version 0.1.0 `
  --prompt-resolution-id elf-reference-prompt-v1 `
  --provider "OpenAI ImageGen" `
  --generated-at 2026-11-02T12:00:00Z `
  --disposition accepted `
  --reviewer "local-sample-reviewer" `
  --reviewed-at 2026-11-02T12:05:00Z
```

Accepted files go to `assets/masters/<asset-id>/<version>/`; candidates go to
`assets/discard_candidates/<asset-id>/<version>/`. Nothing is automatically removed.
Generation records under `assets/generations/<generation-id>/` link the source hash,
review decision, and exact prompt resolution. Use a new asset version for every new
accepted source; existing sources and records are never overwritten.

## 2. Make a destination derivative

Only an accepted master can be exported. The tool always re-encodes it, applies the
configured logo watermark, checks the resulting file, and writes the image and record
under the infographic production's `exports/` folder:

```powershell
python tools/export_image.py `
  --generation-id elf-reference-gen-v1 `
  --derivative-id elf-reference-social-v1 `
  --profile profiles/exports/social.example.yaml
```

The social example downsizes to fit 720 × 720 pixels and writes a lossy JPEG using its
profile quality. The website example preserves pixel dimensions and writes PNG. These
values are editable examples; use a new profile version when changing a processing
policy. The exporter does not upload files. A clean derivative is marked
`ready_for_human_review`, which means the profile and metadata checks passed; a person
still decides whether to publish it.

The output scanner permits only structural PNG chunks and standard JFIF JPEG framing.
It blocks EXIF, XMP, IPTC, comments, ICC profiles, thumbnails, unexpected chunks, and
unexpected application segments. Any scan failure is retained in the derivative
sidecar as `blocked`, and the publication recorder rejects it. The scan does not detect
or claim to remove signals encoded in image pixels.

## 3. Record a completed publication

After manually publishing a checked derivative, record the location and timestamp. This
command writes local metadata only and has no network or publishing capability:

```powershell
python tools/record_publication.py `
  --id elf-reference-social-post-v1 `
  --derivative-record projects/fantasy/example/productions/infographic/exports/elf-reference-social-v1.yaml `
  --destination "Social platform" `
  --published-at 2026-11-02T13:00:00Z `
  --public-url https://example.com/post/123
```

The record is linked to the exact derivative ID, path, hash, production, and profile
version. It cannot refer to a source master or discard candidate.
