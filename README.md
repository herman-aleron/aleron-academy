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

## Live mode (auto-update from GitHub)

Tilda holds only a short loader (`tilda/loader_webinar.html`, `tilda/loader_courses.html`).
The loader fetches `live/<page>.html` from GitHub Pages on every visit, so a push to `main`
reaches fire-proof.co.uk in about 10 minutes without republishing in Tilda.

- Pages: https://herman-aleron.github.io/aleron-academy/ (Settings → Pages → Deploy from a branch → `main` / root)
- Rebuild after editing `src/`: `python3 src/build_tilda.py` (Tilda blocks) then `python3 src/build_live.py` (live files and loaders).
