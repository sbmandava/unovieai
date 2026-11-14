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
| `resources/medsdlc-html/` | **self-contained sub-site** | "Agentic SDLC for Regulated MedTech" — its own `build.py`, theme, nav and `assets/`. Don't regenerate from the main `build_pages.py`. Each page carries the Unovie GA tag, favicons (`../../assets/...`) and a `← Unovie.AI` back link in its `.topbar`. Linked from the Research dropdown + footer. |

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

## Platform restructure (November 2026)
- **Platform** = two product pages, `platform/agentmesh.html` and `platform/agentnexus.html`, built by `product_page()` in `build_pages.py` (hero with an operator-HMI illustration, Operator HMI showcase, sections, "Runs on" hardware). The five old capability pages were removed; `_redirects` (Cloudflare Pages) sends their URLs to AgentMesh / AgentNexus.
- **Hardware** lives under the Platform menu and on `device-platform.html` (tabs from `DEVP`, Industry 4.0 content from `DEV_EXTRA` / `DEV_SIGNALS`). One purpose per device: AMD Ryzen AI Max+ 395 = sovereign plant intelligence; NVIDIA Jetson AGX Thor = robotics & DeepVision for fabs; NVIDIA DGX Spark = AI engineering lab; Qualcomm QCS6490 = remote & mobile assets.
- **Illustrations** live in `assets/images/sketch/` (periwinkle `#6468ac` line art on white). The HMI screens are rendered from the deck's HMI SVGs with project names replaced by Unovie terms.
- `resources/agentnexus-architecture.html` is hand-authored in the whitepaper theme (toolbar, PDF, light/dark).
- **Terminology:** use Unovie platform names (Sovereign Pod, Unovie Gateway, Signal Encoders, Vector Memory, Unovie Decision Engine, Unovie Reasoning Model, skill adapters, Kiln, Evidence Log, Unovie Agent Runtime, Unovie Model Router, Mesh Arbiter, Lane A / Lane B). **Never name open-source projects** on the site (e.g. vLLM, LanceDB, Gemma, Kubernetes).
- Unmeasured numbers carry "target", "estimate" or "vendor spec"; industry-signal claims are labelled "vendor-reported" and never name third-party companies.

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

## Deep-tech repositioning (November 2026)
- Audience: next-generation, sensor-/AI-/robot-heavy manufacturing (battery, chip fabs & suppliers, space & aerospace, robotics & autonomous systems, defense & dual-use, advanced energy). No brownfield/legacy-plant framing.
- **Solution pages retired:** `solutions/*` removed; `SOL` is emptied in `build_pages.py` (`RETIRED_SOL`), old URLs 301 via `_redirects`. The homepage `#accelerators` grid is now "Agentic jobs" (hand-authored in `index.html`); nav label "Agentic jobs".
- Messaging rules: "CNCF-conformant" (Certified Kubernetes) — never "CNCF certified/compliant"; security is "designed against NIST SP 800-53 / NIST AI RMF", never "compliant/certified". Founders have 20+ years each; company is 4 years old.
- CTA everywhere: "Pilot on your line". Pilot form (`form.pilotform`, homepage + contact) builds a mailto in `site.js` — no backend.
- Homepage hero: live AgentMesh console (`.meshviz`, `site.js`) — 512 channels = watching + retrying + 15 flagged + 8 offline, always summing to 512.
- Strategy doc of record: `/opt/projects/unovie/mini/research_notes/website-gtm-strategy.md`.
