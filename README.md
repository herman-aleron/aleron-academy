# Aleron Academy — landing pages

Two landing pages for fire-proof.co.uk, prepared for Tilda (block T123 "Embed HTML code").

| Page | Tilda URL | Files |
|---|---|---|
| Free webinar "How to Get Into Fire Stopping" | /webinar | `tilda/webinar/` |
| Fire Stopping & Fire Door courses | /courses | `tilda/courses/` |

- `T123_<page>_inline.html` — paste-and-go, photos embedded.
- `T123_<page>.html` — light version, photos loaded from `images/`; replace `__IMG_BASE__` with the URL of that folder.
- How to install, pixel events, form setup: [`tilda/README.md`](tilda/README.md).
- `src/` — source pages with `{{IMAGE}}` placeholders and the build script that produces the Tilda blocks.

Leads from both forms are emailed to academy@aleron.co.uk (FormSubmit; activate once, see tilda/README.md).
