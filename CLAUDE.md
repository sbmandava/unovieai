# Unovie.AI website — build & deploy guide

Static marketing site for **Unovie.AI** (an edge-AI engineering studio). No framework, no
bundler — hand-authored + Python-generated HTML. Repo: `github.com/sbmandava/unovieai`,
deploys straight from `main`.

## Layout / source of truth
| Path | Authored how | Notes |
|------|--------------|-------|
| `index.html` | **hand-authored** | Homepage = the design system of record: nav, hero, the **Solutions card grid**, footer. |
| `build_pages.py` | the generator | Produces `solutions/*`, `platform/*`, `about.html`. Also `assets/site.{css,js}` **on first run only**. |
| `assets/site.css`, `assets/site.js` | **live source** | Shared styles/scripts. The generator will NOT overwrite these once the homepage is slimmed — **edit them directly**. |
| `solutions/*.html` (9), `platform/*.html` (5), `device-platform.html`, `why-unovie.html`, `about.html` | **generated** | Do not hand-edit — change `build_pages.py` and regenerate. `device-platform.html` is one page with tabs (one per `DEVP` entry); panels switch via `.tab`/`.tpanel` in `site.js`. |
| `contact.html`, `resources/edge-ai-models.html`, `resources/edge-ai-whitepaper.html` | **hand-authored standalone** | Not produced by the generator. Have their own inline `<style>`/theme script. |

Solution slugs: `maritime-digital-twin`, `connected-vehicle-twin`, `corporate-travel-sales`,
`smart-factory-floor`, `smart-warehouse`, `osha-compliance`, `food-safety`,
`batch-optimization`, `remote-expertise`.

## Build
```bash
python3 build_pages.py        # run from repo root; idempotent — safe to re-run
```
`ROOT` self-locates (the script's own dir). Seeing `note: index.html already slimmed;
reusing existing assets/site.{css,js}` is **normal** — it means it's reusing the live assets.

## Where to change what
- **New/changed solution or platform page** → edit the `SOL` / `PLATP` lists in `build_pages.py`, then regenerate.
- **Homepage Solutions cards** (order, `NN /` numbering, blurbs) → edit `index.html` directly (these cards are not generated).
- **Footer** (all generated pages) → `FOOTER()` in `build_pages.py`.
- **CSS / JS** → `assets/site.css`, `assets/site.js` directly.
- **contact / resources pages** → edit those files directly.

## Content rules — IMPORTANT
- Solution pages are **anonymized** customer projects. **Never** include identifying names:
  company/customer names, vessel names, vehicle makes/models, airline names, account names,
  partners/competitors, product codenames (e.g. `C2C`, `MarineTwin`, `TwinVin`, `MARSX`,
  `Easybiz`, `Komodo`), or `Snapdragon`/SoC model numbers.
- **Studio descriptor:** always write the studio's offering as **"custom Edge-AI Agentic Systems"** (capitalized as a branded term) — never "custom edge-AI systems".
- **Positioning:** Unovie is **founder-led by visionary-caliber founders** who also ship. Frame the market as a third path between (a) slow multi-year SI transformation and (b) abstract big-vision consulting — Unovie = vision **and** execution **and** ownership. Don't name competitors (no Infosys / Hang Ten / Sikka / their client logos).
- `Qualcomm` appears **only** in the partner ticker (`NVIDIA · AMD · Qualcomm · Siemens · GE`) —
  keep it there, don't add it elsewhere. **Exception:** the **Device Platform** tabs name real
  vendor silicon by design (NVIDIA AGX Thor / DGX Spark, Qualcomm QCS6490, AMD Ryzen AI Max+ 395) —
  this was explicitly requested. Still anonymize *third-party box/mini-PC product names* (e.g. the
  "GTR9 Pro" the AMD specs came from) — refer to the device generically.
- Device illustrations live in `assets/images/{slug}.png`: monochrome **periwinkle `#6468ac`** line
  art, transparent background, trimmed and centered on a uniform **820×440** canvas (see the Pillow
  pipeline used to generate them — luminance-key the source, recolor, fit-and-center).
- Source projects (`/opt/projects/qualcomm/*`, `/opt/projects/unovie/sales-mca`,
  `/opt/projects/unovie/sales-intel`) are **read-only reference** — never edit them.

## Theme
- Default: **light on desktop, dark on mobile/touch** — `matchMedia('(max-width:768px),
  (hover:none) and (pointer:coarse)')`. Set **inline in `<head>`** (`<script data-theme-init>`)
  before first paint, so there's no flash. The toggle persists in `localStorage`
  (`uvTheme` for the main site; `bookTheme` / `wpTheme` for the resources pages).
- No `prefers-color-scheme` anywhere — the default is device-based, not OS-based.
- Generated pages get the inline bootstrap automatically (it's in `HEAD()`). Hand-authored
  pages (`index.html`, `contact.html`, `resources/*`) each carry their own copy in `<head>`.
- The `data-theme-init` attribute matters: it keeps the homepage-slimming regex (which matches
  a bare `<script>`) from clobbering the inline theme script.

## Typography
- `.lead` max-width is `72ch`.

## Pre-deploy checklist
1. `python3 build_pages.py`
2. Anonymization sweep — grep the HTML for customer/codename tokens (should be clean).
3. Link check — every internal `href`/`src` resolves.
4. (optional) preview: `python3 -m http.server 8080` → http://localhost:8080/

## Deploy (git)
Repo is owned by `vdesibabu`. Pushes use a **repo deploy key over SSH**, via an SSH host alias
that dodges a global `insteadOf` rewrite in `~/.gitconfig`.

- Remote: `git@github-deploy:sbmandava/unovieai.git`
- `~/.ssh/config` has: `Host github-deploy` → `HostName github.com`,
  `IdentityFile /home/vdesibabu/.ssh/unovieai_deploy`, `IdentitiesOnly yes`.
- Deploy:
  ```bash
  git add -A && git commit -m "…" && git push origin main
  ```
  Commits go **straight to `main`** (static site, no PR flow).
- **Do not** use `git@github.com:` directly — the global `~/.gitconfig` rewrites it to HTTPS
  (which has no stored credential and fails). The `github-deploy` alias avoids the rewrite.
- Auth sanity check: `ssh -T github-deploy` → `Hi sbmandava/unovieai! You've successfully authenticated…`

## Gotchas
- Don't commit `.claude/` (Claude "mind" memory + lock), `__pycache__/`, or `.DS_Store` — see `.gitignore`.
- An `unoweb` auto-committer may exist on this host; the repo is `vdesibabu`-owned now, so git
  operations should run as `vdesibabu` with the deploy key (as above), not as `unoweb`.
