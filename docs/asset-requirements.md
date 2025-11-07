## Asset Handoff Requirements

A concise checklist for providing images/assets so they can be placed into this repo without delay.

### Accepted delivery forms
- **Absolute path** on the local machine (e.g., `/Users/you/image.png`)
- **HTTPS URL** to the file
- **Base64 text** of the file (chat-only transfer)
- Not accepted: chat UI “preview” thumbnails (these are not real file bytes)

### Default repo location and naming
- **Path**: `docs/architecture/`
- **Filename**: lowercase, kebab-case, no spaces, ≤ 80 chars  
  Example: `modular-ai-framework-diagram.png`

### Formats and limits
- **Preferred**: PNG or SVG; **Allowed**: JPG/JPEG
- **Max size**: 2 MB (optimize if larger)
- **Recommended width**: ~1024 px for README display

### Metadata to provide
- **Alt text**: short, descriptive (required)
- **Caption**: optional
- **License/rights**: confirm you have rights to embed

### README linkage
- Use a **relative path**: `docs/architecture/<filename>`
- Default placement: README “Core Architecture” section unless otherwise specified

### Validation criteria
- File exists at the target path
- README renders the image
- No sensitive EXIF/metadata included

### Examples
- Copy from local path (macOS/Linux):
  - `cp "/absolute/source.png" "docs/architecture/modular-ai-framework-diagram.png"`
- Save from base64 (macOS):
  - `cat image.b64 | base64 -D > "docs/architecture/modular-ai-framework-diagram.png"`
- Save from base64 (Linux):
  - `base64 -d image.b64 > "docs/architecture/modular-ai-framework-diagram.png"`

### Notes
- If a non-default location or filename is required, specify it explicitly with the request.


