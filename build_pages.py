#!/usr/bin/env python3
# Builds shared assets + sub-pages for the Unovie.AI site, reusing the homepage design system.
import re, os
ROOT=os.path.dirname(os.path.abspath(__file__))
idx=open(f"{ROOT}/index.html",encoding="utf-8").read()

# ---- 1) extract CSS + JS from the homepage into shared assets ----
# Bare <style>/<script> blocks only exist on the un-slimmed homepage (first run).
# Once slimmed they become <link>/<script src=...>, so these match None and we
# leave the existing assets/ as the source of truth.
_m_css=re.search(r"<style>(.*?)</style>", idx, re.S)
_m_js =re.search(r"<script>(.*?)</script>", idx, re.S)

SUBCSS = """
/* ---------- sub-page additions ---------- */
.phero{padding:148px 0 30px}
.crumb{font-family:var(--mono);font-size:12px;color:var(--fg-dim);margin-bottom:24px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.crumb a{color:var(--fg-mut)}.crumb a:hover{color:var(--accent)}.crumb .sep{color:var(--line-2)}
.phero h1{font-size:clamp(40px,6.4vw,86px)}
.phero .lead{margin:26px 0 32px}
.acard[data-href]{cursor:pointer}
.kgrid{display:grid;gap:14px;margin-top:40px}
@media(min-width:640px){.kgrid{grid-template-columns:repeat(3,1fr)}}
.ktile{border:1px solid var(--line);border-radius:var(--r);padding:22px;background:var(--surface)}
.ktile .big{font-family:var(--disp);font-weight:800;font-size:clamp(30px,4vw,46px);letter-spacing:-.03em;color:var(--fg)}
.ktile .big .o{color:var(--accent)} .ktile .big .s{color:var(--steel)}
.ktile .lab{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--fg-dim);margin-top:8px}
"""
DATAHREF="""
// clickable cards
document.querySelectorAll('[data-href]').forEach(el=>el.addEventListener('click',e=>{if(e.target.closest('a'))return;location.href=el.dataset.href;}));
"""
os.makedirs(f"{ROOT}/assets",exist_ok=True)
if _m_css and _m_js:
    open(f"{ROOT}/assets/site.css","w",encoding="utf-8").write(_m_css.group(1)+SUBCSS)
    open(f"{ROOT}/assets/site.js","w",encoding="utf-8").write(_m_js.group(1)+DATAHREF)
else:
    print("note: index.html already slimmed; reusing existing assets/site.{css,js}")

# ---- 2) slim the homepage: link assets, make cards clickable ----
idx=re.sub(r"<style>.*?</style>", '<link rel="stylesheet" href="assets/site.css">', idx, flags=re.S, count=1)
idx=re.sub(r"<script>.*?</script>", '<script src="assets/site.js"></script>', idx, flags=re.S, count=1)
ACC={"--w:78%":"smart-factory-floor","--w:62%":"smart-warehouse","--w:72%":"osha-compliance",
     "--w:74%":"vision-intelligence","--w:70%":"batch-optimization","--w:66%":"remote-expertise"}
for w,slug in ACC.items():
    idx=idx.replace(f'<div class="acard rv" style="{w}">',
                    f'<div class="acard rv" data-href="solutions/{slug}.html" data-cursor style="{w}">',1)
PLAT={"Edge Data Fabric":"edge-data-fabric","Edge Streaming Intelligence":"edge-streaming-analytics",
      "GPU MicroCloud":"gpu-microcloud","GPU EdgeGateway":"gpu-edgegateway"}
for name,slug in PLAT.items():
    idx=idx.replace(f'href="#contact" data-cursor><div><div class="t">{name}</div>',
                    f'href="platform/{slug}.html" data-cursor><div><div class="t">{name}</div>',1)
open(f"{ROOT}/index.html","w",encoding="utf-8").write(idx)

# ---- 3) shared chrome (base = "" for root, "../" for subdirs) ----
# Inline theme bootstrap (runs in <head>, before first paint → no flash).
# Default: light on desktop, dark on mobile/touch. A saved toggle (uvTheme) always wins.
# The `data-theme-init` attribute keeps the homepage-slimming regex (bare <script>) from matching it.
THEMEINIT = "<script data-theme-init>(function(){try{var s=localStorage.getItem('uvTheme');if(s==='light'||s==='dark'){document.documentElement.setAttribute('data-theme',s);return;}}catch(e){}var m=false;try{m=matchMedia('(max-width:768px), (hover:none) and (pointer:coarse)').matches;}catch(e){}document.documentElement.setAttribute('data-theme',m?'dark':'light');})();</script>"

def HEAD(base,title,desc):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="{base}assets/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="{base}assets/favicon.png"><link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Hanken+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/site.css">{THEMEINIT}</head><body>
<div class="grain"></div><div class="cur"></div><div class="cur-r"></div>'''

def NAV(base):
    h=base+"index.html"
    return f'''<header class="nav"><div class="wrap"><div class="row">
  <a class="brand" href="{h}"><img class="logo" src="{base}assets/images/logo.png" alt="Unovie.AI"></a>
  <nav class="navlinks">
    <a href="{h}#engineering">AI Engineering</a><a href="{h}#accelerators">Solutions</a>
    <a href="{h}#platform">Platform</a>
    <div class="drop"><button data-cursor>Research ▾</button><div class="menu">
      <a href="{base}resources/edge-ai-models.html" target="_blank" rel="noopener"><span class="ic">01</span><span><span class="t">Edge AI Models — Field Guide</span><br><span class="s">A 25-chapter architect's eBook</span></span></a>
      <a href="{base}resources/edge-ai-whitepaper.html" target="_blank" rel="noopener"><span class="ic">02</span><span><span class="t">Frozen-Base Doctrine — Whitepaper</span><br><span class="s">Training without retraining</span></span></a>
    </div></div>
  </nav>
  <a class="navcta" href="{h}#contact" data-cursor>Start a project <span class="ar">→</span></a>
  <button class="burger" id="burger" aria-label="Menu">☰</button>
</div></div></header>
<div class="mobile" id="mobile">
  <a href="{h}#engineering"><span class="mono">01</span><br>AI Engineering</a>
  <a href="{h}#accelerators"><span class="mono">02</span><br>Solutions</a>
  <a href="{h}#platform"><span class="mono">03</span><br>Platform</a>
  <a href="{base}resources/edge-ai-models.html" target="_blank"><span class="mono">04</span><br>Research</a>
  <a href="{h}#contact" style="color:var(--accent)"><span class="mono">05</span><br>Start a project →</a>
</div>'''

def FOOTER(base):
    h=base+"index.html"
    return f'''<footer><div class="wrap"><div class="fgrid">
  <div class="fcol fbrand"><a class="brand" href="{h}"><img class="logo" src="{base}assets/images/logo.png" alt="Unovie.AI"></a>
    <p>AI engineering as a service. We design, build, and operate custom edge-AI systems — on hardware you own.</p></div>
  <div class="fcol"><h4>Company</h4>
    <a href="{h}#engineering">AI Engineering</a><a href="{h}#delivery">How we deliver</a>
    <a href="{base}about.html">About</a><a href="{base}contact.html">Contact</a></div>
  <div class="fcol"><h4>Platform</h4>
    <a href="{base}platform/edge-data-fabric.html">Edge Data Fabric</a><a href="{base}platform/edge-streaming-analytics.html">Streaming Intelligence</a>
    <a href="{base}platform/gpu-microcloud.html">GPU MicroCloud</a><a href="{base}platform/gpu-edgegateway.html">GPU EdgeGateway</a></div>
  <div class="fcol"><h4>Research</h4>
    <a href="{base}resources/edge-ai-models.html" target="_blank">Field Guide (eBook)</a><a href="{base}resources/edge-ai-whitepaper.html" target="_blank">Whitepaper</a></div>
</div><div class="fbot"><span>© 2026 Unovie · EdgeAI Context Engineering</span><span>Engineered for the edge with NVIDIA · AMD · Qualcomm · Siemens · GE</span></div></div></footer>
<script src="{base}assets/site.js"></script></body></html>'''

def metrics(items):  # list of (value_html, label)
    cells="".join(f'<div class="ktile rv"><div class="big">{v}</div><div class="lab">{l}</div></div>' for v,l in items)
    return f'<div class="kgrid">{cells}</div>'
def disc(items):     # list of (ix, title, desc, [chips])
    out=[]
    for i,(ix,t,d,ch) in enumerate(items):
        g='var(--steel)' if i%2 else 'var(--accent)'
        chips="".join(f'<span class="chip">{c}</span>' for c in ch)
        out.append(f'<div class="dcard rv"><div class="glow" style="background:{g}"></div><div class="ix">{ix}</div><h3>{t}</h3><p>{d}</p><div class="spec">{chips}</div></div>')
    return f'<div class="disc">{"".join(out)}</div>'
def steps(items):    # list of (title, desc)
    out=[f'<div class="stage rv"><div class="ix">{i+1:02d}</div><h3>{t}</h3><p>{d}</p></div>' for i,(t,d) in enumerate(items)]
    return f'<div class="pipe" style="grid-template-columns:repeat(auto-fit,minmax(170px,1fr))">{"".join(out)}</div>'
def shead(num,label,title,lead=""):
    L=f'<p class="lead rv">{lead}</p>' if lead else ""
    return f'<div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>{num} — {label}</div><h2 class="rv">{title}</h2></div>{L}</div>'

def page(base, folder, slug, cat, crumb_cat, title_html, lead, kpis, feats, hows, cta_lead, extra=""):
    full = f"{ROOT}/{folder}" if folder else ROOT
    os.makedirs(full, exist_ok=True)
    head=HEAD(base, f"{re.sub('<[^>]+>','',title_html)} — Unovie.AI", lead[:150])
    body=f'''{NAV(base)}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="{base}index.html">Home</a><span class="sep">/</span><a href="{base}index.html#{'accelerators' if folder=='solutions' else 'platform'}">{crumb_cat}</a><span class="sep">/</span><span style="color:var(--fg-mut)">{re.sub('<[^>]+>','',title_html)}</span></div>
  <div class="tag rv">{cat}</div>
  <h1 class="rv" style="margin-top:18px">{title_html}</h1>
  <p class="lead rv">{lead}</p>
  <div class="cta rv"><a class="btn btn-acc" href="{base}index.html#contact" data-cursor>Start a project <span class="ar">→</span></a>
    <a class="btn btn-gh" href="{base}resources/edge-ai-models.html" target="_blank" data-cursor>Read the field guide</a></div>
  {metrics(kpis)}
</div></section>
<section><div class="wrap">{shead("01","What it does", feats[0])}{disc(feats[1])}</div></section>
<section><div class="wrap">{shead("02","How it works", hows[0])}{steps(hows[1])}</div></section>
{extra}
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Let's build</div>
  <h2 style="margin-top:16px">{cta_lead}</h2>
  <p class="lead">Turnkey Edge-AI — fixed time, fixed cost, full responsibility.</p>
  <div class="cta"><a class="btn btn-acc" href="mailto:suresh@unovie.com?subject=Project%20enquiry" data-cursor>Talk to our engineers <span class="ar">→</span></a>
    <a class="btn btn-gh" href="{base}index.html#accelerators" data-cursor>See all solutions</a></div>
</div></div></section>
{FOOTER(base)}'''
    open(f"{full}/{slug}.html","w",encoding="utf-8").write(head+body)

B="../"
# ----- SOLUTIONS -----
SOL=[
 ("smart-factory-floor","Manufacturing","Smart Factory <span class='serif' style='color:var(--accent)'>Floor</span>",
  "Vision-driven inspection and quality control that runs on the line, in real time, on hardware you own — no cloud round-trip, no data egress.",
  [("−30<span class='o'>%</span>","inspection errors"),("+25<span class='o'>%</span>","line speed"),("100<span class='o'>%</span>","on-prem"),],
  ("Inspection &amp; quality, automated",[("/vision","Real-time defect detection","Sub-second vision on the line catches defects humans miss at speed.",["camera→GPU","sub-second"]),
   ("/grading","Consistent QC grading","Eliminates inspector drift with a model that grades every unit identically.",["repeatable","auditable"]),
   ("/closed-loop","Stop-the-line alerts","Closed-loop alerting with full traceability when a defect threshold trips.",["alerting","trace"])]),
  ("From frame to action",[("Capture","Cameras stream to the on-prem GPU."),("Detect","Edge model flags defects per frame."),("Decide","Grade, route, or stop the line."),("Log","Every decision recorded for audit.")]),
  "Inspect every unit. <span class='serif' style='color:var(--accent)'>Perfectly.</span>"),
 ("smart-warehouse","Logistics","Smart <span class='serif' style='color:var(--accent)'>Warehouse</span>",
  "Edge-AI for inventory and movement: see stock in real time, optimize slotting, and cut stockouts — running where the cameras and sensors already are.",
  [("−20<span class='o'>%</span>","stockouts"),("+15<span class='o'>%</span>","fill rate"),("real-time","tracking")],
  ("Inventory you can actually see",[("/vision","Inventory vision","Continuous counts and location from existing cameras.",["counts","location"]),
   ("/slotting","Slotting optimization","Recommends placement to shorten pick paths.",["pick-path","yield"]),
   ("/trace","Track &amp; trace","End-to-end movement with tamper-evident logs.",["trace","audit"])]),
  ("Sense to optimize",[("Ingest","Cameras &amp; sensors → edge."),("Model","Count, locate, predict."),("Optimize","Slotting &amp; replenishment."),("Act","Alerts &amp; work orders.")]),
  "Never run out. <span class='serif' style='color:var(--accent)'>Or over.</span>"),
 ("osha-compliance","Safety","OSHA Compliance <span class='serif' style='color:var(--accent)'>Monitoring</span>",
  "AI-powered safety analytics that spot compliance risks — missing PPE, unsafe zones, hazards — and alert in real time, with an evidence trail.",
  [("−25<span class='o'>%</span>","OSHA fines"),("+30<span class='o'>%</span>","training done"),("real-time","alerts")],
  ("Safety, watched continuously",[("/ppe","PPE &amp; hazard detection","Detects missing protection and unsafe behaviour on camera.",["PPE","zones"]),
   ("/risk","Risk analytics","Trends incidents and near-misses into actionable risk.",["trends","near-miss"]),
   ("/evidence","Alerting &amp; evidence","Real-time alerts plus a defensible audit log.",["alerting","audit"])]),
  ("Monitor to audit",[("Monitor","Watch zones &amp; PPE."),("Detect","Flag risk events."),("Alert","Notify supervisors."),("Record","Immutable evidence log.")]),
  "Protect people. <span class='serif' style='color:var(--accent)'>Prove it.</span>"),
 ("vision-intelligence","OTT · Content Provider","Vision <span class='serif' style='color:var(--accent)'>Intelligence</span>",
  "Real-time computer vision for an OTT and pay-TV operator. Edge-AI watches every channel feed, identifies what is actually on screen frame by frame, and turns thousands of live streams into a continuously verified, audit-ready signal — on GPUs at the edge, in under a second.",
  [("96","channels per node, live"),("&lt;1<span class='o'>s</span>","feed to verified"),("−90<span class='o'>%</span>","manual QA effort")],
  ("See every stream, automatically",[("/detect","Live channel detection","GPU vision identifies the channel on every tile of every composite feed, with confidence and bounding box per frame.",["per-frame","confidence","bbox"]),
   ("/verify","Continuous QA &amp; compliance","Confirms each stream carries the right content and flags drift or outage in sub-second time, with annotated evidence for audit.",["MTTD↓","evidence","audit"]),
   ("/scale","Many feeds, one node","A zero-copy GPU pipeline decodes and scores dozens of 4K feeds per edge node — no raw video leaves the rack.",["zero-copy","4K","on-prem"])]),
  ("Stream to verified signal",[("Decode","RTSP feeds decode into GPU memory."),("Locate","Per-tile regions mapped once."),("Detect","GPU scores each region every frame."),("Publish","Detections stream to analytics &amp; alerts.")]),
  "Verify every channel, <span class='serif' style='color:var(--accent)'>in real time.</span>"),
 ("batch-optimization","Process · chem &amp; pharma","Batch Process <span class='serif' style='color:var(--accent)'>Optimization</span>",
  "Automate the optimization of batch processes in chemical and pharmaceutical manufacturing — higher quality, less waste, per batch.",
  [("+25<span class='o'>%</span>","product quality"),("−15<span class='o'>%</span>","waste"),("per-batch","tuning")],
  ("Tune every batch",[("/recipe","Recipe optimization","Recommends set-points from historical &amp; live data.",["set-points","yield"]),
   ("/drift","Drift detection","Catches process drift before it costs a batch.",["drift","SPC"]),
   ("/yield","Yield analytics","Attributes yield to controllable factors.",["yield","RCA"])]),
  ("Model to verify",[("Model","Learn the process envelope."),("Recommend","Optimal set-points."),("Apply","Operator-in-the-loop."),("Verify","Score against held-out.")]),
  "More yield. <span class='serif' style='color:var(--accent)'>Less waste.</span>"),
 ("remote-expertise","Workforce","Remote Expertise <span class='serif' style='color:var(--accent)'>Platform</span>",
  "Connect remote experts with on-site teams for real-time, grounded guidance — so knowledge scales without the travel.",
  [("+20<span class='o'>%</span>","worker output"),("−30<span class='o'>%</span>","on-site visits"),("real-time","guidance")],
  ("Expertise, on demand",[("/guide","Guided AR / voice","Step-by-step guidance overlaid where the work happens.",["AR","voice"]),
   ("/ground","Grounded retrieval","Answers cited to your manuals and records.",["RAG","cited"]),
   ("/capture","Session capture","Turns each session into reusable knowledge.",["capture","reuse"])]),
  ("Connect to capture",[("Connect","Link expert &amp; floor."),("Ground","Pull cited context."),("Guide","Real-time steps."),("Capture","Bank the knowledge.")]),
  "Your best expert, <span class='serif' style='color:var(--accent)'>everywhere.</span>"),
 ("maritime-digital-twin","Maritime · Oil &amp; Gas","Maritime <span class='serif' style='color:var(--accent)'>Digital Twin</span>",
  "A living digital twin for large tanker and LNG fleets. Edge-AI on every vessel watches vibration, acoustics, hull strain and the OT network, classifies anomalies before the satellite uplink, and turns condition evidence into deferred-maintenance and compliance decisions on shore.",
  [("−6<span class='o'> mo</span>","overhauls deferred on evidence"),("100<span class='o'>%</span>","classified on-vessel"),("800","vessels · one twin")],
  ("Intelligence at the waterline",[("/edge","Edge anomaly detection","Vibration, acoustic and strain models run on the vessel and classify faults before the uplink — so low-bandwidth links carry decisions, not raw signal.",["vibration","acoustic","strain"]),
   ("/cbm","Condition-based maintenance","Remaining-useful-life on rotating gear becomes defensible deferral evidence for class surveys, and auto-triggers spares procurement.",["RUL","deferral","spares"]),
   ("/cyber","OT cyber watch","An on-network sensor flags anomalous engine and automation commands, isolates the endpoint, and keeps a full forensic trail.",["OT IDS","isolate","forensics"])]),
  ("From sensor to shore decision",[("Sense","High-rate sensors on engine, hull and OT bus."),("Classify","Edge models score events on the vessel."),("Sync","Only decisions cross the satellite link."),("Act","Defer, procure, or isolate — with evidence.")]),
  "Run the fleet on <span class='serif' style='color:var(--accent)'>evidence.</span>"),
 ("connected-vehicle-twin","Automotive · Connected EV","Connected-Vehicle <span class='serif' style='color:var(--accent)'>Digital Twin</span>",
  "A VIN-level digital twin for multi-brand connected-EV fleets. As-ordered, as-built, as-operated and as-maintained data unify into one live view, with an in-vehicle AI assistant and battery diagnostics running on automotive-grade edge silicon and delivered over the air.",
  [("4.2<span class='o'>h</span>","average case resolution"),("98.7<span class='o'>%</span>","notification delivery"),("4","lifecycle states · one VIN")],
  ("One VIN, every dimension",[("/twin","Lifecycle digital twin","As-ordered, as-built, as-operated and as-maintained unified per VIN — live telemetry beside service, recall and warranty history.",["telemetry","BOM","history"]),
   ("/assist","In-vehicle AI assistant","A generative assistant and battery state-of-health diagnostics run on automotive edge SoCs, with new models pushed over the air.",["GenAI","battery SoH","OTA"]),
   ("/care","Context-aware customer care","Inbound contacts pop full vehicle context, next-best-action and consent state; video remote-assist and digital-key control close the loop.",["screen-pop","NBA","digital keys"])]),
  ("Signal to service",[("Connect","Vehicles stream telemetry and faults."),("Diagnose","Edge models score battery and systems."),("Enrich","Cases pop context and next action."),("Resolve","Remote command, dispatch, or OTA.")]),
  "Know every vehicle, <span class='serif' style='color:var(--accent)'>by VIN.</span>"),
 ("corporate-travel-sales","Go-to-market · Airline","Corporate-Travel <span class='serif' style='color:var(--accent)'>Sales Intelligence</span>",
  "An AI co-pilot for an airline corporate-sales team. It grounds each corporate account in live travel-demand signals, scores fit across seven airline-specific dimensions — network overlap, premium-cabin propensity, loyalty, travel-policy maturity and more — drafts a full opportunity plan with stakeholder map and competitive positioning, and surfaces the next best action across the whole book of business.",
  [("&lt;5<span class='o'> min</span>","meeting prep, from an hour"),("1<span class='o'>-day</span>","RFP turnaround, from five"),("2,000<span class='o'>+</span>","accounts, one book")],
  ("From signal to corporate deal",[("/signal","Travel-demand signal grounding","Hiring, expansion, earnings and RFP signals per account distil into issue, impact and opportunity a rep can act on.",["grounded","signals","RAG"]),
   ("/score","Airline-specific fit scoring","Seven weighted dimensions — network overlap, premium-cabin propensity, loyalty, policy maturity, buying intent and more — render an instant fit and propensity picture.",["7 axes","propensity","explainable"]),
   ("/leak","Share-of-wallet leakage","Route-level share against contracted commitment flags slipping accounts and the revenue at risk — before renewal.",["share","routes","at-risk"])]),
  ("Account to next move",[("Ground","Pull live demand signals."),("Score","Rank fit across seven axes."),("Plan","Draft the opportunity and stakeholders."),("Act","Surface the next best action.")]),
  "Win the <span class='serif' style='color:var(--accent)'>corporate</span> account."),
]
for s in SOL: page(B,"solutions",s[0],s[1],"Solutions",s[2],s[3],s[4],s[5],s[6],s[7])

# ----- PLATFORM -----
PLATP=[
 ("edge-data-fabric","Platform · Nexus","Edge Data <span class='serif' style='color:var(--steel)'>Fabric</span>",
  "A domain ontology, a knowledge graph and vector memory — one living context layer for everything you know. Custom models read your documents, telemetry and records, construct a typed graph of entities and relationships, and embed it for hybrid retrieval. Domain fine-tuned agents reason over it, and your teams query it in plain language. It grows continuously, versions every fact, and runs entirely on-prem.",
  [("ontology","domain-modelled"),("graph<span class='s'>+vector</span>","hybrid recall"),("0<span class='o'>B</span>","egress · on-prem")],
  ("Context that compounds",[("/ontology","A domain ontology","Your world modelled as typed entities and relationships — the who, what, when, where and why — so context is structured, not guessed.",["typed","relationships","semantic"]),
   ("/graph","Knowledge graph + vector","A graph store and vector memory side by side: subgraph traversal for structure, dense and sparse embeddings for meaning, fused into one answer.",["graph","vector","hybrid"]),
   ("/selfserve","Self-service by language","Teams author and query in natural language; domain fine-tuned agents plan, retrieve and act — no SQL, no data team in the loop.",["NL query","agents","no-code"])]),
  ("Documents in, decisions out",[("Extract","Parse docs, tables and signals."),("Construct","Build the typed graph."),("Index","Embed for graph + vector."),("Serve","Grounded answers &amp; agents.")]),
  "Know what you know — and <span class='serif' style='color:var(--steel)'>why.</span>"),
 ("edge-streaming-analytics","Platform","Edge Streaming <span class='serif' style='color:var(--steel)'>Intelligence</span>",
  "Real-time vision and audio intelligence over live streams, at fleet scale. A zero-copy GPU pipeline decodes hundreds of feeds straight into device memory, runs a catalog of detectors on every frame, and turns raw video into a verified, queryable signal — with sub-millisecond validation and an agent layer that reasons and acts on top. Proven on broadcast-grade media: 1,000+ concurrent 4K streams across racks of edge GPUs.",
  [("1,000<span class='s'>+</span>","4K streams, concurrent"),("&lt;1<span class='o'>ms</span>","high-frequency validation"),("128","streams / rack")],
  ("Vision and audio on every frame",[("/detect","A catalog of live detectors","Logos, freezes, macro-blocking, blank and splash screens, lip-sync and on-screen errors are scored per frame — video and audio anomalies caught the instant they appear.",["video","audio","per-frame"]),
   ("/read","Reads the screen, not just watches it","OCR and vision-language models extract guide data, clocks, version strings and error dialogs; object detectors track focus, icons and UI state.",["OCR/VLM","object-det","UI state"]),
   ("/act","Closes the loop","An agent layer plans and acts — driving devices through an IR / Bluetooth control plane and verifying every step against the live stream.",["agentic","device-control","verify"])]),
  ("Stream to decision",[("Decode","Feeds decode into GPU memory."),("Detect","A model graph scores every frame."),("Decide","Validate sub-ms; reason in minutes."),("Act","Drive devices, publish, alert.")]),
  "Real-time, <span class='serif' style='color:var(--steel)'>actually.</span>"),
 ("gpu-microcloud","Platform","GPU <span class='serif' style='color:var(--steel)'>MicroCloud</span>",
  "We stand up a full private cloud on your floor: racks of edge GPUs and servers, software-defined storage, a 10G fabric and a Kubernetes control plane — all on-prem. Workloads are scheduled and bin-packed across the pool, MIG carves each GPU into isolated slices, zero-trust policy gates every call, and every minute is metered for chargeback. Datacenter discipline, where your data lives.",
  [("Kubernetes","cloud-native, on-prem"),("MIG","hard isolation"),("metered","per-tenant chargeback")],
  ("Your GPUs, run like cloud",[("/schedule","Fair-share scheduling","A priority-and-quota scheduler places jobs across the pool, preempts politely, and keeps expensive silicon busy.",["queue","quota","preempt"]),
   ("/isolate","Hard multi-tenant isolation","MIG partitioning carves each GPU into isolated slices, so tenants share hardware without sharing blast radius.",["MIG","cgroups","secure"]),
   ("/meter","Metering &amp; chargeback","Per-tenant, per-job accounting turns shared capacity into auditable cost and showback reports.",["metering","showback","reports"])]),
  ("Pool to bill",[("Pool","Aggregate edge GPUs."),("Schedule","Place workloads."),("Isolate","Partition tenants."),("Meter","Account &amp; bill.")]),
  "Datacenter discipline, <span class='serif' style='color:var(--steel)'>on-prem.</span>"),
 ("gpu-edgegateway","Platform","GPU <span class='serif' style='color:var(--steel)'>EdgeGateway</span>",
  "A secure, OpenAI-compatible front door for every model at the perimeter. One endpoint authenticates each caller, applies per-route role rules, and load-balances by live token throughput across vLLM and Ollama backends — with an NVFP4 fast path for low-latency decode. Drop-in for any compatible client; governed like production.",
  [("OpenAI","compatible /v1"),("token-aware","load balancing"),("OIDC","per-route auth")],
  ("One endpoint, many models",[("/api","OpenAI-compatible surface","A drop-in /v1 endpoint — chat, completions, embeddings — so existing clients and SDKs work unchanged.",["/v1","streaming","SDK-drop-in"]),
   ("/auth","Identity &amp; routing","OIDC/JWT identity with per-route RBAC and quotas decides who reaches which model, and how often.",["OIDC","RBAC","quotas"]),
   ("/lb","Token-aware load balancing","Requests route by live KV-cache and token load across vLLM and Ollama backends, with an NVFP4 fast path.",["vLLM","Ollama","NVFP4"])]),
  ("Request to response",[("Authenticate","Validate identity &amp; role."),("Route","Pick the fastest healthy backend."),("Serve","NVFP4 fast path."),("Observe","Meter, trace &amp; log.")]),
  "Serve models <span class='serif' style='color:var(--steel)'>safely.</span>"),
]

def platx(arch_title, arch_cards, num_title, specs):
    return (f'<section><div class="wrap">{shead("03","Architecture",arch_title)}{disc(arch_cards)}</div></section>'
            f'<section><div class="wrap">{shead("04","By the numbers",num_title)}{metrics(specs)}</div></section>')

PLAT_EXTRA={
 "edge-data-fabric": (
   f'<section><div class="wrap">{shead("03","Architecture","How the graph is built")}'
   + disc([
     ("/parse","Custom extraction models","Document- and table-structure models parse PDFs, images and text; an LLM emits structured records that become typed nodes and edges.",["doc-parse","tables","LLM"]),
     ("/construct","Graph construction + embeddings","Records are de-duplicated, transformed and persisted to a fast embeddable graph store, with embedding models writing vectors beside every node.",["KG build","embeddings","transform"]),
     ("/retrieve","Hybrid fused retrieval","Traditional indices, text and sparse embeddings and subgraph traversal feed a tensor-based fused ranker and query-rewrite models — grounded Top-K, not guesses.",["fusion","rerank","query-rewrite"]),
     ("/version","Temporal &amp; governed","Graph OLTP keeps every node and edge temporally versioned with an immutable audit trail; columnar OLAP serves analytics — multi-tenant, OAuth2 / RBAC, zero-trust.",["temporal","audit","RBAC"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("04","Custom models","Models and agents, tuned to your domain")}'
   + disc([
     ("/models","A catalog of custom models","Document-parsing, embedding, NER and query-rewrite models, plus domain fine-tuned SLMs — trained on your domain, swappable and multi-model routed.",["fine-tuned SLM","NER","multi-model"]),
     ("/agents","Domain agent accelerators","Pre-built agents — diagnostics, differential, referral, next-best-action and triage — reason over the graph and call tools to act.",["agents","NBA","tools"]),
     ("/nlp","Natural-language self-service","Self-service portals let users ask, author and govern in plain language across chat, voice and app — every answer traceable to source.",["NL authoring","omni-channel","traceable"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("05","By the numbers","Built for scale")}'
   + metrics([("100<span class='s'>M</span>","object nodes"),("2.5<span class='s'>B</span>","relationships"),("260<span class='s'>+</span>","prebuilt connectors")])
   + '</div></section>'
 ),
 "edge-streaming-analytics": (
   f'<section><div class="wrap">{shead("03","Detection catalog","A model graph, not a single model")}'
   + disc([
     ("/anomaly","Video anomaly detection","Freezes (consecutive pixel-difference), macro-blocking and pixelation (block-variance + Sobel edge density), tearing and stutter — flagged inside the stream buffer.",["optical-flow","Sobel","block-variance"]),
     ("/logo","Logo &amp; UI object detection","An RF-DETR detector with a CLIP refiner confirms logos, app tiles and widgets with bounding-box precision.",["RF-DETR","CLIP","bbox"]),
     ("/ocr","OCR &amp; VLM reading","GPU OCR (docTR) and vision-language models read guide grids, clocks, version strings and error dialogs — signal-loss, auth and tune failures included.",["docTR","VLM","regex"]),
     ("/audio","Audio &amp; sync checks","Audio-presence and lip-sync checks run beside the video probe, so silent feeds and A/V drift are caught too.",["audio-probe","lip-sync","ffprobe"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("04","Architecture","Inside the pipeline")}'
   + disc([
     ("/pipeline","Zero-copy vision pipeline","GStreamer + DeepStream pull RTSP / H.265 into the GPU via NVDEC; composite grids map to regions once, then a swappable model graph scores each region every frame.",["GStreamer","DeepStream","NVDEC"]),
     ("/serverless","Serverless model serving","Detectors run as auto-scaling GPU functions (Nuclio) drawn from a continuously trained catalog — new models deploy without touching the pipeline.",["Nuclio","auto-scale","registry"]),
     ("/backbone","Event &amp; knowledge backbone","Detections stream over NATS JetStream into ClickHouse for sub-second OLAP, with a knowledge graph, vectors and a fine-tuned vision-action model driving next-best-action.",["NATS","ClickHouse","knowledge-graph"]),
     ("/learn","A closed training loop","Misses become flagged frames become new annotation tasks — captured, versioned in COCO and retrained, then promoted through a registry.",["CVAT","COCO","feedback"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("05","By the numbers","Engineered for density")}'
   + metrics([("~512","streams · 4 racks in parallel"),("&lt;50<span class='o'>ms</span>","inference / frame"),("30<span class='o'>fps</span>","sustained per stream")])
   + '</div></section>'
 ),
 "gpu-microcloud": (
   f'<section><div class="wrap">{shead("03","Architecture","Inside the micro-cloud")}'
   + disc([
     ("/compute","Heterogeneous compute pool","Edge GPUs, CPU servers and training boxes are pooled as one schedulable fabric — production racks plus a dedicated test / stage rack.",["edge GPU","servers","DGX"]),
     ("/orchestrate","Kubernetes control plane","A cloud-native control plane handles dynamic model deployment, job scheduling, capacity allocation and execution failover across namespaced dev / test / prod.",["Kubernetes","Helm","failover"]),
     ("/storage","Software-defined storage","CEPH block / file / object, an S3-compatible object store and NFS / iSCSI SAN give every workload durable, shared state — no external cloud.",["CEPH","S3","NFS/iSCSI"]),
     ("/partition","MIG slice fabric","Each GPU is partitioned into right-sized MIG instances and bin-packed by memory and NVLink topology — tenants share silicon, never blast radius.",["MIG","NVLink","bin-pack"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("04","Governance","Governed like a cloud region")}'
   + disc([
     ("/zerotrust","Zero-trust by default","Policy-as-code and OAuth2 / OpenID gate every call; per-tenant namespaces and RBAC separate workloads and data end to end.",["OPA","OAuth2/OIDC","RBAC"]),
     ("/observe","Deep observability","OpenTelemetry and eBPF trace every workload; metrics, logs and dashboards make utilization and cost visible in real time.",["OpenTelemetry","eBPF","Grafana"]),
     ("/data","Stateful data services","Cache, queue and database services run inside the cloud beside the compute, with columnar analytics for usage and reporting.",["Redis","PostgreSQL","ClickHouse"]),
     ("/meter","Metering &amp; chargeback","Per-tenant, per-job accounting turns shared capacity into auditable showback — quotas, reports and capacity planning.",["metering","quotas","showback"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("05","By the numbers","The fabric underneath")}'
   + metrics([("10<span class='o'>G</span>","overlay SAN + LAN"),("7<span class='s'>×</span>","MIG slices / GPU"),("3","namespaces · dev/test/prod")])
   + '</div></section>'
 ),
 "gpu-edgegateway": platx("Inside the gateway",[
   ("/gate","Auth &amp; policy gate","Every request is authenticated, rate-limited and policy-checked before it ever reaches a backend.",["JWT","rate-limit","policy"]),
   ("/route","Load-aware router","The router tracks per-backend token throughput and KV-cache pressure, steering traffic to the fastest healthy replica.",["KV-aware","health","failover"]),
   ("/observe","Full observability","Per-route latency, tokens and cost stream to metrics and traces — every call metered and accountable.",["metrics","tracing","metering"])],
   "Governed like production",[("&lt;1<span class='o'>ms</span>","auth overhead"),("vLLM<span class='s'>+Ollama</span>","backends"),("per-route","metering")]),
}
for s in PLATP: page(B,"platform",s[0],s[1],"Platform",s[2],s[3],s[4],s[5],s[6],s[7],PLAT_EXTRA.get(s[0],""))

# ----- ABOUT -----
about=f'''{HEAD("","About — Unovie.AI","An AI-engineering studio that designs, builds, and operates custom edge-AI systems.")}{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">About</span></div>
  <div class="tag rv">About <span class="o">·</span> Unovie.AI</div>
  <h1 class="rv" style="margin-top:18px">We engineer AI that <span class="serif" style="color:var(--accent)">ships.</span></h1>
  <p class="lead rv">Unovie is an AI-engineering studio for Industry 4.0. We take full responsibility for AI transformation — from architecture through POC and MVP to production readiness — on a foundation of frozen-base, self-improving edge systems that you own and can audit.</p>
  <div class="cta rv"><a class="btn btn-acc" href="index.html#contact" data-cursor>Start a project <span class="ar">→</span></a>
    <a class="btn btn-gh" href="resources/edge-ai-models.html" target="_blank" data-cursor>Read our field guide</a></div>
  {metrics([("4","engineering disciplines"),("5","-step methodology"),("fixed","time &amp; cost")])}
</div></section>
<section id="engineering"><div class="wrap">{shead("01","What we are good at","Four engineering disciplines.")}{disc([
  ("/model-engineering","Model Engineering","Self-learning loops and skill optimization that compound accuracy without retraining risk.",["verifiers","skill opt"]),
  ("/edge-efficiency","Edge Efficiency","Small models on Blackwell silicon — PLE-safe NVFP4, unified-memory budgeting.",["NVFP4","Jetson Thor"]),
  ("/opex-efficiency","Opex Efficiency","Capex, not a metered bill — marginal cost near electricity.",["on-prem","fixed cost"]),
  ("/reliable-hpc","Reliable HPC Systems","Gated, reversible, regression-safe — every change logged and revertible.",["gated","auditable"])])}</div></section>
<section id="delivery"><div class="wrap">{shead("02","How we deliver","A proven, success-based methodology.")}{steps([
  ("Assess &amp; plan","Workshops, ROI, value outcomes."),("Solution design","Roadmap &amp; reference architecture."),
  ("Build &amp; test","Data, models, testing, monitoring."),("Optimize","KPI tracking &amp; feedback loops."),("Train &amp; support","Enablement &amp; adoption.")])}</div></section>
<section><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Partners</div>
  <h2 style="margin-top:16px">Trusted with <span class="serif" style="color:var(--accent)">NVIDIA · AMD · Qualcomm · Siemens · GE.</span></h2>
  <p class="lead">Manufacturing · Logistics · Oil &amp; Gas · Food Processing. Bring us a problem; we will return a system.</p>
  <div class="cta"><a class="btn btn-acc" href="mailto:suresh@unovie.com" data-cursor>Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("")}'''
open(f"{ROOT}/about.html","w",encoding="utf-8").write(about)

print("built: index (slimmed) + 6 solutions + 4 platform + about + assets")
