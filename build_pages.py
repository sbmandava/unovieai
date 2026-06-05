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

# Google Analytics 4 (gtag.js). The config <script> carries a data-ga attribute so the
# homepage-slimming regex (which matches a bare <script>) never touches it.
GA = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-590ZL8SE2M"></script>
<script data-ga>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-590ZL8SE2M');</script>"""

def HEAD(base,title,desc):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{GA}
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
    <div class="drop"><button data-cursor>Device Platform ▾</button><div class="menu">
      <a href="{base}device/nvidia-agx-thor.html"><span class="ic">01</span><span><span class="t">NVIDIA AGX Thor</span><br><span class="s">Blackwell robotics &amp; physical-AI edge</span></span></a>
      <a href="{base}device/nvidia-dgx-spark.html"><span class="ic">02</span><span><span class="t">NVIDIA DGX Spark</span><br><span class="s">Grace-Blackwell desktop AI supercomputer</span></span></a>
    </div></div>
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
  <a href="{base}device/nvidia-agx-thor.html"><span class="mono">04</span><br>NVIDIA AGX Thor</a>
  <a href="{base}device/nvidia-dgx-spark.html"><span class="mono">05</span><br>NVIDIA DGX Spark</a>
  <a href="{base}resources/edge-ai-models.html" target="_blank"><span class="mono">06</span><br>Research</a>
  <a href="{h}#contact" style="color:var(--accent)"><span class="mono">07</span><br>Start a project →</a>
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
    <a href="{base}platform/gpu-microcloud.html">GPU MicroCloud</a><a href="{base}platform/gpu-edgegateway.html">GPU EdgeGateway</a>
    <a href="{base}platform/edge-security-intelligence.html">Edge Security Intelligence</a></div>
  <div class="fcol"><h4>Device Platform</h4>
    <a href="{base}device/nvidia-agx-thor.html">NVIDIA AGX Thor</a><a href="{base}device/nvidia-dgx-spark.html">NVIDIA DGX Spark</a></div>
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
  "Unovie helps you own your enterprise context foundation — on your terms, with your data — to power the AI-native initiatives ahead. A domain ontology, a knowledge graph and vector memory become one living model of your world: you can buy the models and the agents, but the context — the boundary that makes you a coherent system — is yours to build, woven from open standards, on-prem. Custom models read your documents, telemetry and records into a typed graph; agents reason over it; your teams query it in plain language. And leaked context — vectors handed to models you do not own — is a business liability and a governance violation.",
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
  "An agent-first, signal-driven gateway built on one routing contract: signals become projections, projections drive decisions, decisions choose the model — across a mesh of local, private and frontier models. Session-aware routing keeps multi-turn agents coherent, sandboxed runtimes keep tools safe, and every policy change is shadow-tested before it goes live. OpenAI- and Anthropic-compatible, multimodal, governed like production, on hardware you own.",
  [("OpenAI<span class='s'>+Anthropic</span>","compatible"),("signal→model","one routing contract"),("session-aware","agentic routing")],
  ("Route, reason, act",[("/route","Signal-driven routing","Intent, complexity, modality and risk become projections and policy bands, then route across a local-to-frontier mesh — reasoning only when it pays.",["intent","projections","when-to-reason"]),
   ("/session","Session-aware agentic routing","Stateful guards keep multi-turn agents coherent: hard locks block unsafe model switches mid-tool-loop, weighing quality gap, prefix locality and turn priors.",["SAAR","tool-loop locks","continuity"]),
   ("/sandbox","Sandboxed &amp; governed","Tools and code run in policy-governed MicroVM sandboxes — no unauthorized file, credential or network access.",["MicroVM","policy-as-code","no-exfil"])]),
  ("Signal to decision",[("Signal","Score intent, risk, modality, context."),("Project","Normalise into policy bands."),("Decide","Pick model, agent or tool."),("Serve","Sandboxed, observed, metered.")]),
  "Serve models <span class='serif' style='color:var(--steel)'>safely.</span>"),
 ("edge-security-intelligence","Platform","IT/OT Edge Security <span class='serif' style='color:var(--steel)'>Intelligence</span>",
  "A GPU-native SIEM that detects threats while the data is still moving. Instead of collecting logs and correlating them later, it tokenizes, classifies and enriches every event in flight on the GPU — semantic AI detection, not regex chains — then indexes to a sharded, authenticated store. Tens of thousands of events per second on a single edge node, on-prem.",
  [("21K<span class='o'>+</span>","events / sec, peak"),("semantic","AI, not regex"),("single-node","on-prem")],
  ("Detection at ingest",[("/inflight","Detection in the data path","Events are tokenized, classified and scored on the GPU as they stream in — alerts fire near ingestion, not after a delayed search job.",["in-flight","low-latency","streaming"]),
   ("/semantic","Semantic threat detection","A BERT classifier reads intent and meaning in raw log text, catching threats that static rules and regex miss.",["BERT","intent","beyond-regex"]),
   ("/resilient","Hardened &amp; bounded","A dead-letter queue protects failed batches, retention keeps storage bounded, and authenticated, sharded indexing keeps search fast.",["DLQ","retention","auth"])]),
  ("Log to incident",[("Ingest","Logs land in a Kafka stream."),("Batch","Workers tokenize on the GPU."),("Classify","BERT inference scores intent."),("Index","Enriched incidents to search.")]),
  "Detect threats <span class='serif' style='color:var(--steel)'>in the data path.</span>"),
]

def platx(arch_title, arch_cards, num_title, specs):
    return (f'<section><div class="wrap">{shead("03","Architecture",arch_title)}{disc(arch_cards)}</div></section>'
            f'<section><div class="wrap">{shead("04","By the numbers",num_title)}{metrics(specs)}</div></section>')

import math as _mth
def _pt(r,deg):
    a=_mth.radians(deg); return (round(500+r*_mth.cos(a),1), round(300+r*_mth.sin(a),1))
_kp=['<svg class="kgviz" viewBox="0 0 1000 640" role="img" aria-label="An ontology core wrapped in a living knowledge graph and a context membrane of ontology, identifiers, rules, meaning and processes; external forces (market, customers, change, regulation, competitors, exceptions, attackers, agents) flow in at the gates. Your context is your membrane.">',
     '<defs><radialGradient id="kgcore" cx="50%" cy="42%" r="62%"><stop offset="0%" stop-color="#c4b5fd"/><stop offset="55%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6d28d9"/></radialGradient></defs>']
# external forces flowing inward toward the membrane
for _i,(_nm,_ang) in enumerate([("Market",-90),("Customers",-45),("Attackers",0),("Regulation",45),("Agents",90),("Exceptions",135),("Competitors",180),("Change",-135)]):
    _ax,_ay=_pt(252,_ang); _bx,_by=_pt(214,_ang); _lx,_ly=_pt(276,_ang)
    _kp.append(f'<line class="xline" x1="{_ax}" y1="{_ay}" x2="{_bx}" y2="{_by}"/>')
    _kp.append(f'<circle class="xpkt" r="3.5"><animateMotion dur="{round(2.0+0.13*_i,2)}s" begin="{round(0.12*_i,2)}s" repeatCount="indefinite" path="M{_ax},{_ay} L{_bx},{_by}"/></circle>')
    _kp.append(f'<text class="xlbl" x="{_lx}" y="{_ly+4}">{_nm}</text>')
# radial knowledge graph (web ring + spokes + nodes)
_NODES=[_pt(118,_i*30-90) for _i in range(12)]
for _i in range(12):
    _x1,_y1=_NODES[_i]; _x2,_y2=_NODES[(_i+1)%12]; _kp.append(f'<line class="kweb" x1="{_x1}" y1="{_y1}" x2="{_x2}" y2="{_y2}"/>')
for _x,_y in _NODES: _kp.append(f'<line class="kspoke" x1="500" y1="300" x2="{_x}" y2="{_y}"/>')
for _i,(_x,_y) in enumerate(_NODES):
    _kp.append(f'<circle class="knode" cx="{_x}" cy="{_y}" r="{10 if _i%2==0 else 6}" style="animation-delay:{round(_i*0.16,2)}s"/>')
# glowing ontology core
_kp.append('<circle class="kglow" cx="500" cy="300" r="46"/><circle class="kcore" cx="500" cy="300" r="40"/>')
# membrane ring: 5 labeled segments (curved text)
for _i,(_nm,_mid) in enumerate([("ONTOLOGY",-90),("IDENTIFIERS",-18),("RULES",54),("MEANING",126),("PROCESSES",198)]):
    _x0,_y0=_pt(190,_mid-29); _x1,_y1=_pt(190,_mid+29)
    _kp.append(f'<path class="memb" d="M{_x0},{_y0} A190,190 0 0 1 {_x1},{_y1}"/>')
    if _mth.sin(_mth.radians(_mid))>0.2:
        _px0,_py0=_pt(190,_mid+29); _px1,_py1=_pt(190,_mid-29); _sw=0
    else:
        _px0,_py0=_pt(190,_mid-29); _px1,_py1=_pt(190,_mid+29); _sw=1
    _kp.append(f'<path id="kseg{_i}" d="M{_px0},{_py0} A190,190 0 0 {_sw} {_px1},{_py1}" fill="none"/>')
    _kp.append(f'<text class="mlbl"><textPath href="#kseg{_i}" startOffset="50%">{_nm}</textPath></text>')
_kp.append('</svg>')
KG_SVG="".join(_kp)

ESI_SVG = """<svg class="stviz" viewBox="0 0 1000 380" role="img" aria-label="Animated telecom and satellite media: feeds beamed to an edge GPU and scored across a grid of live streams">
<circle class="wave" cx="150" cy="120" r="30" style="animation-delay:0s"/><circle class="wave" cx="150" cy="120" r="30" style="animation-delay:1s"/><circle class="wave" cx="150" cy="120" r="30" style="animation-delay:2s"/>
<circle class="dish" cx="150" cy="120" r="24"/><line x1="150" y1="120" x2="174" y2="96" stroke="var(--steel)" stroke-width="2"/><circle cx="174" cy="96" r="4" fill="var(--steel)"/>
<line class="beam" x1="172" y1="134" x2="430" y2="200"/><circle class="pkt" r="4"><animateMotion dur="2.2s" repeatCount="indefinite" path="M172,134 L430,200"/></circle>
<rect class="egpu" x="360" y="166" width="150" height="72" rx="12"/>
<line class="beam" x1="510" y1="190" x2="630" y2="120"/><line class="beam" x1="510" y1="202" x2="630" y2="196"/><line class="beam" x1="510" y1="214" x2="630" y2="272"/>
<circle class="pkt" r="4"><animateMotion dur="2s" begin=".4s" repeatCount="indefinite" path="M510,202 L630,196"/></circle><circle class="pkt" r="4"><animateMotion dur="2.4s" begin=".9s" repeatCount="indefinite" path="M510,190 L630,120"/></circle>
<rect class="tile" x="630" y="96" width="78" height="58" rx="7" style="animation-delay:.1s"/><rect class="tile lit" x="726" y="96" width="78" height="58" rx="7" style="animation-delay:.7s"/><rect class="tile" x="822" y="96" width="78" height="58" rx="7" style="animation-delay:.4s"/><rect class="tile" x="630" y="170" width="78" height="58" rx="7" style="animation-delay:1.1s"/><rect class="tile" x="726" y="170" width="78" height="58" rx="7" style="animation-delay:.3s"/><rect class="tile lit" x="822" y="170" width="78" height="58" rx="7" style="animation-delay:.9s"/><rect class="tile lit" x="630" y="244" width="78" height="58" rx="7" style="animation-delay:.6s"/><rect class="tile" x="726" y="244" width="78" height="58" rx="7" style="animation-delay:1.3s"/><rect class="tile" x="822" y="244" width="78" height="58" rx="7" style="animation-delay:.2s"/>
<rect class="scan" x="626" y="92" width="10" height="214" rx="4"/>
<text class="lbl" x="150" y="170">Satellite</text><text class="lbl hl" x="435" y="207">Edge GPU</text><text class="lbl" x="765" y="326">Live streams</text>
</svg>"""

MC_SVG = """<svg class="mcviz" viewBox="0 0 1000 420" role="img" aria-label="Animated distributed micro-cloud: GPU nodes in a mesh sharing intelligence through a control plane">
<line class="link" x1="650" y1="210" x2="575" y2="340"/><line class="link" x1="575" y1="340" x2="425" y2="340"/><line class="link" x1="425" y1="340" x2="350" y2="210"/><line class="link" x1="350" y1="210" x2="425" y2="80"/><line class="link" x1="425" y1="80" x2="575" y2="80"/><line class="link" x1="575" y1="80" x2="650" y2="210"/>
<line class="link lit" x1="650" y1="210" x2="500" y2="210"/><line class="link lit" x1="575" y1="340" x2="500" y2="210"/><line class="link lit" x1="425" y1="340" x2="500" y2="210"/><line class="link lit" x1="350" y1="210" x2="500" y2="210"/><line class="link lit" x1="425" y1="80" x2="500" y2="210"/><line class="link lit" x1="575" y1="80" x2="500" y2="210"/>
<circle class="pkt" r="4"><animateMotion dur="1.8s" repeatCount="indefinite" path="M425,80 L500,210"/></circle><circle class="pkt" r="4"><animateMotion dur="2s" begin=".5s" repeatCount="indefinite" path="M500,210 L650,210"/></circle><circle class="pkt" r="4"><animateMotion dur="2.2s" begin="1s" repeatCount="indefinite" path="M575,340 L500,210"/></circle><circle class="pkt" r="4"><animateMotion dur="2.4s" begin=".3s" repeatCount="indefinite" path="M650,210 L575,340"/></circle><circle class="pkt" r="4"><animateMotion dur="2.1s" begin=".8s" repeatCount="indefinite" path="M425,80 L575,80"/></circle>
<g class="gnode" style="animation-delay:0s"><rect class="gbox" x="608" y="182" width="84" height="56" rx="9"/><rect class="slice" x="618" y="220" width="18" height="8" rx="2"/><rect class="slice" x="641" y="220" width="18" height="8" rx="2"/><rect class="slice" x="664" y="220" width="18" height="8" rx="2"/></g>
<g class="gnode" style="animation-delay:.2s"><rect class="gbox" x="533" y="312" width="84" height="56" rx="9"/><rect class="slice" x="543" y="350" width="18" height="8" rx="2"/><rect class="slice" x="566" y="350" width="18" height="8" rx="2"/><rect class="slice" x="589" y="350" width="18" height="8" rx="2"/></g>
<g class="gnode" style="animation-delay:.4s"><rect class="gbox" x="383" y="312" width="84" height="56" rx="9"/><rect class="slice" x="393" y="350" width="18" height="8" rx="2"/><rect class="slice" x="416" y="350" width="18" height="8" rx="2"/><rect class="slice" x="439" y="350" width="18" height="8" rx="2"/></g>
<g class="gnode" style="animation-delay:.6s"><rect class="gbox" x="308" y="182" width="84" height="56" rx="9"/><rect class="slice" x="318" y="220" width="18" height="8" rx="2"/><rect class="slice" x="341" y="220" width="18" height="8" rx="2"/><rect class="slice" x="364" y="220" width="18" height="8" rx="2"/></g>
<g class="gnode" style="animation-delay:.8s"><rect class="gbox" x="383" y="52" width="84" height="56" rx="9"/><rect class="slice" x="393" y="90" width="18" height="8" rx="2"/><rect class="slice" x="416" y="90" width="18" height="8" rx="2"/><rect class="slice" x="439" y="90" width="18" height="8" rx="2"/></g>
<g class="gnode" style="animation-delay:1s"><rect class="gbox" x="533" y="52" width="84" height="56" rx="9"/><rect class="slice" x="543" y="90" width="18" height="8" rx="2"/><rect class="slice" x="566" y="90" width="18" height="8" rx="2"/><rect class="slice" x="589" y="90" width="18" height="8" rx="2"/></g>
<circle class="hub" cx="500" cy="210" r="24"/><text class="lbl hl" x="500" y="214">Control</text><text class="lbl" x="425" y="392">GPU node</text>
</svg>"""

GW_SVG = """<svg class="gwviz" viewBox="0 0 1000 430" role="img" aria-label="A control plane and a data plane around a self-improving router core, with feature modules above and a research loop below that closes back to the core">
<circle class="gwglow" cx="500" cy="202" r="72"/>
<rect class="gwbox" x="64" y="150" width="150" height="150" rx="14"/><text class="tlbl hl" x="139" y="140">CONTROL PLANE</text>
<circle class="gwnode" cx="86" cy="184" r="5" style="animation-delay:0s"/><text class="lbl sm" x="152" y="188">Policies</text>
<circle class="gwnode" cx="86" cy="212" r="5" style="animation-delay:.3s"/><text class="lbl sm" x="152" y="216">Identities</text>
<circle class="gwnode" cx="86" cy="240" r="5" style="animation-delay:.6s"/><text class="lbl sm" x="152" y="244">API keys</text>
<circle class="gwnode" cx="86" cy="268" r="5" style="animation-delay:.9s"/><text class="lbl sm" x="152" y="272">Guardrails</text>
<rect class="gwbox" x="786" y="150" width="150" height="150" rx="14"/><text class="tlbl hl" x="861" y="140">DATA PLANE</text>
<circle class="gwnode st" cx="808" cy="184" r="5" style="animation-delay:.2s"/><text class="lbl sm" x="876" y="188">Fast inference</text>
<circle class="gwnode st" cx="808" cy="212" r="5" style="animation-delay:.5s"/><text class="lbl sm" x="876" y="216">Model routing</text>
<circle class="gwnode st" cx="808" cy="240" r="5" style="animation-delay:.8s"/><text class="lbl sm" x="876" y="244">Observability</text>
<circle class="gwnode st" cx="808" cy="268" r="5" style="animation-delay:1.1s"/><text class="lbl sm" x="876" y="272">Cost-aware</text>
<line class="gwlink" x1="214" y1="212" x2="405" y2="202"/><line class="gwlink" x1="595" y1="202" x2="786" y2="212"/>
<circle class="pkt" r="4"><animateMotion dur="2.2s" repeatCount="indefinite" path="M214,212 L405,202"/></circle><circle class="pkt" r="4"><animateMotion dur="2.6s" begin=".9s" repeatCount="indefinite" path="M214,212 L405,202"/></circle>
<circle class="pkt st" r="4"><animateMotion dur="2.2s" begin=".4s" repeatCount="indefinite" path="M595,202 L786,212"/></circle><circle class="pkt st" r="4"><animateMotion dur="2.6s" begin="1.3s" repeatCount="indefinite" path="M595,202 L786,212"/></circle>
<line class="gwlink" x1="380" y1="104" x2="470" y2="162"/><line class="gwlink" x1="460" y1="104" x2="490" y2="162"/><line class="gwlink" x1="540" y1="104" x2="510" y2="162"/><line class="gwlink" x1="620" y1="104" x2="530" y2="162"/>
<circle class="gwnode" cx="380" cy="100" r="5" style="animation-delay:.1s"/><text class="tlbl" x="380" y="86">SAAR</text>
<circle class="gwnode" cx="460" cy="100" r="5" style="animation-delay:.5s"/><text class="tlbl" x="460" y="86">Evals</text>
<circle class="gwnode" cx="540" cy="100" r="5" style="animation-delay:.9s"/><text class="tlbl" x="540" y="86">CLI-first</text>
<circle class="gwnode" cx="620" cy="100" r="5" style="animation-delay:1.3s"/><text class="tlbl" x="620" y="86">Router models</text>
<rect class="gwcore" x="405" y="164" width="190" height="78" rx="16"/>
<text class="lbl hl" x="500" y="197" style="font-size:13px">Self-improving</text><text class="lbl hl" x="500" y="217" style="font-size:13px">Router</text>
<path class="gwloop" d="M377,318 H623 Q650,318 650,345 Q650,372 623,372 H377 Q350,372 350,345 Q350,318 377,318 Z"/>
<circle class="gwnode st" cx="410" cy="318" r="4.5" style="animation-delay:0s"/><circle class="gwnode st" cx="470" cy="318" r="4.5" style="animation-delay:.4s"/><circle class="gwnode st" cx="530" cy="318" r="4.5" style="animation-delay:.8s"/><circle class="gwnode st" cx="590" cy="318" r="4.5" style="animation-delay:1.2s"/>
<line class="gwlink" x1="500" y1="242" x2="500" y2="318"/>
<circle class="pkt" r="4"><animateMotion dur="1.7s" repeatCount="indefinite" path="M500,242 L500,318"/></circle>
<circle class="pkt st" r="4.5"><animateMotion dur="6s" repeatCount="indefinite" path="M377,318 H623 Q650,318 650,345 Q650,372 623,372 H377 Q350,372 350,345 Q350,318 377,318 Z"/></circle>
<text class="tlbl" x="500" y="398">research loop &#8594; closes the loop</text>
</svg>"""

SEC_SVG = """<svg class="secviz" viewBox="0 0 1000 470" role="img" aria-label="Five nested concentric layers protected by a shield: Business Contexts at the core, then Business Data, Edge Agents, Sensors, and an outer Shield deflecting threats and DDoS">
<circle class="lshield" cx="500" cy="230" r="204" stroke="#22d3ee"/>
<circle class="lring" cx="500" cy="230" r="164" stroke="#f59e0b"/>
<circle class="lring" cx="500" cy="230" r="124" stroke="#a78bfa"/>
<circle class="lring" cx="500" cy="230" r="84" stroke="#38bdf8"/>
<line class="spoke" x1="500" y1="230" x2="664" y2="230"/><line class="spoke" x1="500" y1="230" x2="384" y2="346"/><line class="spoke" x1="500" y1="230" x2="616" y2="114"/>
<circle class="ipkt" r="3.5" style="fill:#34d399"><animateMotion dur="2.5s" repeatCount="indefinite" path="M500,230 L664,230"/></circle><circle class="ipkt" r="3.5" style="fill:#34d399"><animateMotion dur="2.9s" begin=".6s" repeatCount="indefinite" path="M500,230 L616,114"/></circle><circle class="ipkt" r="3.5" style="fill:#34d399"><animateMotion dur="2.7s" begin="1.2s" repeatCount="indefinite" path="M500,230 L384,346"/></circle>
<circle class="ldot" cx="664" cy="230" r="6" fill="#f59e0b" style="animation-delay:0s"/><circle class="ldot" cx="336" cy="230" r="6" fill="#f59e0b" style="animation-delay:.5s"/><circle class="ldot" cx="616" cy="346" r="6" fill="#f59e0b" style="animation-delay:.9s"/><circle class="ldot" cx="384" cy="346" r="6" fill="#f59e0b" style="animation-delay:.3s"/>
<circle class="src" cx="90" cy="70" r="7" style="animation-delay:0s"/><circle class="src" cx="910" cy="70" r="7" style="animation-delay:.3s"/><circle class="src" cx="60" cy="230" r="7" style="animation-delay:.6s"/><circle class="src" cx="940" cy="230" r="7" style="animation-delay:.2s"/><circle class="src" cx="120" cy="400" r="7" style="animation-delay:.5s"/><circle class="src" cx="880" cy="400" r="7" style="animation-delay:.8s"/><circle class="src" cx="330" cy="420" r="7" style="animation-delay:.4s"/><circle class="src" cx="670" cy="420" r="7" style="animation-delay:.9s"/>
<circle class="tpkt" r="3.5"><animateMotion dur="1.7s" repeatCount="indefinite" path="M90,70 L310,156"/></circle><circle class="tpkt" r="3.5"><animateMotion dur="1.9s" begin=".2s" repeatCount="indefinite" path="M910,70 L690,156"/></circle><circle class="tpkt" r="3.5"><animateMotion dur="1.5s" begin=".4s" repeatCount="indefinite" path="M60,230 L296,230"/></circle><circle class="tpkt" r="3.5"><animateMotion dur="1.8s" begin=".1s" repeatCount="indefinite" path="M940,230 L704,230"/></circle><circle class="tpkt" r="3.5"><animateMotion dur="1.6s" begin=".5s" repeatCount="indefinite" path="M120,400 L314,313"/></circle><circle class="tpkt" r="3.5"><animateMotion dur="1.9s" begin=".7s" repeatCount="indefinite" path="M880,400 L686,313"/></circle><circle class="tpkt" r="3.5"><animateMotion dur="1.6s" begin=".3s" repeatCount="indefinite" path="M330,420 L364,382"/></circle><circle class="tpkt" r="3.5"><animateMotion dur="1.8s" begin=".6s" repeatCount="indefinite" path="M670,420 L636,382"/></circle>
<circle class="impact" cx="310" cy="156" r="7" style="animation-delay:0s"/><circle class="impact" cx="690" cy="156" r="7" style="animation-delay:.5s"/><circle class="impact" cx="296" cy="230" r="7" style="animation-delay:.9s"/><circle class="impact" cx="314" cy="313" r="7" style="animation-delay:.3s"/><circle class="impact" cx="636" cy="382" r="7" style="animation-delay:.7s"/>
<circle class="lcore" cx="500" cy="230" r="44" stroke="#34d399"/>
<text class="llbl" x="500" y="46" fill="#22d3ee">Shield</text>
<text class="llbl" x="500" y="86" fill="#f59e0b">Sensors</text>
<text class="llbl" x="500" y="126" fill="#a78bfa">Edge Agents</text>
<text class="llbl" x="500" y="166" fill="#38bdf8">Business Data</text>
<text class="llbl" x="500" y="226" fill="#34d399">Business</text><text class="llbl" x="500" y="242" fill="#34d399">Contexts</text>
</svg>"""

PLAT_EXTRA={
 "edge-data-fabric": (
   '<section><div class="wrap"><div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>The context membrane</div><h2 class="rv">Your context is your <span class="serif" style="color:var(--steel)">membrane.</span></h2></div><p class="lead rv">Your context is not a feature you bolt on — it is your model of your own world, the boundary that lets your organisation perceive, predict and act as one coherent system. An ontology core, a living knowledge graph, and a membrane of identifiers, rules, meaning and processes that lets the world in without losing what makes you you.</p></div><div class="kgwrap rv">' + KG_SVG + '<p class="kgquote rv">A context you can buy is a context your competitors can buy too.</p><p class="kgwarn rv">Leaked context — or vectors — to models you do not own is a business liability. A governance violation.</p><p class="kgsub rv">You can buy the models. You can buy the agents. The context — the boundary that defines you — you build and own, woven from open standards, on your terms. Outsource it, and you become a component in a system someone else defines.</p></div></div></section>'
   + f'<section><div class="wrap">{shead("03","Architecture","How the graph is built")}'
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
   '<section><div class="wrap"><div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>Live streams</div><h2 class="rv">From satellite to <span class="serif" style="color:var(--steel)">every screen.</span></h2></div><p class="lead rv">Telecom and satellite feeds land at the edge, get scored frame by frame, and serve verified media — at fleet scale.</p></div><div class="stwrap rv">' + ESI_SVG + '</div></div></section>'
   + f'<section><div class="wrap">{shead("03","Detection catalog","A model graph, not a single model")}'
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
   '<section><div class="wrap"><div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>Distributed by design</div><h2 class="rv">Many nodes, <span class="serif" style="color:var(--steel)">one intelligence.</span></h2></div><p class="lead rv">GPU nodes pool as one mesh — scheduled, partitioned and sharing state through a control plane. Workloads land anywhere; the cloud behaves as one.</p></div><div class="mcwrap rv">' + MC_SVG + '</div></div></section>'
   + f'<section><div class="wrap">{shead("03","Architecture","Inside the micro-cloud")}'
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
 "gpu-edgegateway": (
   '<section><div class="wrap"><div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>Control plane · data plane</div><h2 class="rv">A self-improving <span class="serif" style="color:var(--steel)">router.</span></h2></div><p class="lead rv">A control plane governs policy, identity and guardrails; a data plane serves fast, observable, cost-aware inference; and a self-improving router between them turns every request into a better next decision — research that closes the loop.</p></div><div class="gwwrap rv">' + GW_SVG + '</div></div></section>'
   + f'<section><div class="wrap">{shead("03","Architecture","Inside the gateway")}'
   + disc([
     ("/contract","One routing contract","Signals become projections, projections drive decisions, decisions choose the model — the same pipeline whether configured in YAML, the console, the CLI or Kubernetes.",["signals","projections","decisions"]),
     ("/mesh","Mixture-of-models mesh","Token- and capability-aware routing spans vLLM, local SLMs and frontier APIs with semantic caching; the classifiers run on OpenVINO, CUDA or ROCm — one control plane, any backend.",["vLLM","semantic cache","OpenVINO/CUDA/ROCm"]),
     ("/safe","Safety &amp; protocol","History-aware PII, jailbreak and prompt-injection scanning across every turn — behind an OpenAI- and Anthropic-compatible ingress with explicit, lossless translation.",["PII","jailbreak","OpenAI/Anthropic"]),
     ("/lifecycle","Shadow, activate, revert","Every routing policy is versioned and shadow-tested on replayed traffic before activation, with one-click rollback — routing never drifts silently.",["shadow","replay","rollback"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("04","Agent-first delivery","Multimodal in, action out")}'
   + disc([
     ("/multimodal","Every modality, one path","Text, voice, image and event inputs are normalised, routed to the right modality model, and turned into grounded responses or tool actions.",["text·voice·image","normalise","actions"]),
     ("/context","Long-context, calibrated","Online calibration learns token-estimate ratios from real responses, and domain compression profiles — coding, medical, security, multi-turn — extract signal without clipping long prompts.",["calibration","compression","long-context"]),
     ("/observe","Topology you can trace","A console traces every signal &#8594; projection &#8594; decision with replay-backed insights, and meters per-route latency, tokens and cost — every call accountable.",["topology","replay","metering"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("05","By the numbers","Governed like production")}'
   + metrics([("&lt;1<span class='o'>ms</span>","signal → decision"),("15<span class='s'>+</span>","signal families"),("shadow→activate","policy lifecycle")])
   + '</div></section>'
 ),
 "edge-security-intelligence": (
   '<section><div class="wrap"><div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>Edge defense</div><h2 class="rv">Threats stop <span class="serif" style="color:var(--steel)">at the edge.</span></h2></div><p class="lead rv">Five nested layers — business contexts at the core, then business data, edge agents and sensors — wrapped in one shield. DDoS floods and intrusions are detected and deflected before they ever reach the core.</p></div><div class="secwrap rv">' + SEC_SVG + '</div></div></section>'
   + f'<section><div class="wrap">{shead("03","Architecture","Inside the pipeline")}'
   + disc([
     ("/ingest","Streaming ingest","High-throughput Kafka in KRaft mode (no ZooKeeper) feeds parallel consumers — backpressure-safe at tens of thousands of events per second.",["Kafka","KRaft","parallel"]),
     ("/infer","GPU inference server","An inference server runs the detection model on the GPU in batches, so classification scales with parallelism instead of CPU cores.",["Triton","Morpheus","GPU batch"]),
     ("/enrich","Enrich &amp; index","Scores and metadata are attached, then incidents are written to an authenticated, multi-shard search index for fast investigation.",["enrichment","Elasticsearch","8-shard"]),
     ("/harden","Operational hardening","Dead-letter queue, health checks, retention enforcement and authentication keep the pipeline resilient and storage bounded.",["DLQ","healthchecks","retention"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("04","IT + OT coverage","One lens over both estates")}'
   + disc([
     ("/it","IT telemetry","Logs, endpoints, identity and network events are classified for intent — credential abuse, lateral movement and exfiltration patterns surfaced in flight.",["logs","identity","network"]),
     ("/ot","OT &amp; edge signals","Operational-technology and device telemetry are watched on the same pipeline, so anomalies on the plant floor and at the edge are caught beside IT threats.",["OT","ICS","device"]),
     ("/correlate","Unified incidents","IT and OT detections land in one store with shared scoring and timelines — correlation across both estates, not two disconnected tools.",["correlation","timeline","single-pane"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("05","By the numbers","Engineered for throughput")}'
   + metrics([("21K<span class='s'>+</span>","EPS peak"),("13.8K<span class='s'>+</span>","EPS sustained"),("~3<span class='o'>s</span>","AI inference latency")])
   + '</div></section>'
 ),
}
for s in PLATP: page(B,"platform",s[0],s[1],"Platform",s[2],s[3],s[4],s[5],s[6],s[7],PLAT_EXTRA.get(s[0],""))

# ----- DEVICE PLATFORM -----
DEVP=[
 ("nvidia-agx-thor","Device · Robotics edge","NVIDIA AGX <span class='serif' style='color:var(--accent)'>Thor</span>",
  "A Blackwell-class edge supercomputer for physical AI. NVIDIA Jetson AGX Thor packs up to 2,070 FP4 TFLOPS of generative-AI compute and 128 GB of unified memory into a power-configurable module small enough to live inside a robot, a vehicle or a machine — running several large models, vision and multi-sensor fusion at once, on-prem. We build, optimize and operate the full Unovie stack on Thor, so your edge agents run where the data is born.",
  [("2,070<span class='o'>TFLOPS</span>","FP4 AI compute"),("128<span class='o'>GB</span>","unified LPDDR5X"),("~7.5<span class='o'>&#215;</span>","vs Jetson Orin")],
  ("Physical AI at the edge",[("/blackwell","Blackwell on a module","A datacenter-class Blackwell GPU with FP4 and a transformer engine, packed into a module — generative and vision models that used to need a rack now run inside the machine.",["Blackwell","FP4","transformer-engine"]),
   ("/fusion","Multi-sensor, multi-model","A 14-core Arm Neoverse CPU and high-bandwidth memory run camera, lidar, radar and language models together, fused in real time for autonomy and inspection.",["sensor-fusion","multi-model","real-time"]),
   ("/safety","Partitioned &amp; safety-ready","MIG carves the GPU into isolated slices inside a configurable 40&#8211;130W envelope, with a functional-safety design for robots and autonomous machines.",["MIG","40&#8211;130W","safety"])]),
  ("Silicon to autonomy",[("Provision","Image Thor with the Unovie edge stack."),("Serve","Local models + Nexus context, on-device."),("Fuse","Vision, sensors and agents reason live."),("Act","Closed-loop control, fully on-prem.")]),
  "Run the model inside <span class='serif' style='color:var(--accent)'>the machine.</span>"),
 ("nvidia-dgx-spark","Device · Desktop supercomputer","NVIDIA DGX <span class='serif' style='color:var(--accent)'>Spark</span>",
  "A petaFLOP AI supercomputer that fits on a desk. NVIDIA DGX Spark pairs the GB10 Grace Blackwell Superchip with 128 GB of coherent unified memory and up to 1,000 TOPS of FP4 compute — enough to prototype, fine-tune and run models up to ~200B parameters locally, or ~405B across a linked pair. We run it as your private development and inference node: the full Unovie stack, your data, your room.",
  [("1<span class='o'>PFLOP</span>","FP4 AI compute"),("128<span class='o'>GB</span>","coherent memory"),("200<span class='o'>B</span>","params, local")],
  ("A supercomputer you own",[("/gb10","Grace Blackwell GB10","A 20-core Arm Grace CPU and a Blackwell GPU joined by NVLink-C2C share one coherent memory space — no PCIe copies between CPU and GPU.",["GB10","NVLink-C2C","coherent"]),
   ("/memory","128 GB for big models","Unified LPDDR5X holds models up to ~200B parameters; two units linked over ConnectX scale to ~405B — inference and fine-tuning without the cloud.",["200B local","405B linked","ConnectX"]),
   ("/stack","The full NVIDIA AI stack","Runs NIM microservices, CUDA frameworks and the same containers as DGX in the datacenter — develop locally, deploy to the edge unchanged.",["NIM","CUDA","portable"])]),
  ("Desk to deployment",[("Build","Prototype &amp; fine-tune locally on Spark."),("Ground","Wire in your Nexus context and data."),("Validate","Run the same containers as production."),("Promote","Ship unchanged to edge or MicroCloud.")]),
  "Your own AI supercomputer, <span class='serif' style='color:var(--accent)'>on your desk.</span>"),
]
DEV_EXTRA={
 "nvidia-agx-thor": platx("Built for the machine",[
   ("/compute","Blackwell GPU + Tensor Cores","2,560 CUDA cores and next-gen Tensor Cores with FP4 and a transformer engine for on-device generative AI.",["CUDA","Tensor","FP4"]),
   ("/cpu","14-core Arm Neoverse","A 14-core Arm Neoverse-V3AE cluster feeds the GPU and runs the control plane, sensors and OS.",["Neoverse-V3AE","14-core"]),
   ("/io","Sensor-grade I/O","High-speed camera, networking and PCIe lanes ingest many sensors at once with deterministic latency.",["MIPI/CSI","PCIe","10/25G"])],
   "By the numbers",[("2,070<span class='o'>TFLOPS</span>","FP4 (sparse)"),("128<span class='o'>GB</span>","LPDDR5X"),("273<span class='o'>GB/s</span>","memory bandwidth"),("40&#8211;130<span class='o'>W</span>","configurable")]),
 "nvidia-dgx-spark": platx("One coherent memory space",[
   ("/superchip","GB10 Grace Blackwell","Grace CPU and Blackwell GPU on one package, joined by NVLink-C2C at chip-to-chip bandwidth.",["GB10","NVLink-C2C"]),
   ("/memory","128 GB unified LPDDR5X","CPU and GPU address one coherent pool — no host-device copies, and room for ~200B-parameter models.",["unified","coherent","200B"]),
   ("/fabric","ConnectX scale-out","ConnectX networking links two Sparks into a single ~405B-parameter inference target.",["ConnectX","RDMA","405B"])],
   "By the numbers",[("1,000<span class='o'>TOPS</span>","FP4 AI"),("128<span class='o'>GB</span>","unified memory"),("20","Arm Grace cores"),("4<span class='o'>TB</span>","NVMe storage")]),
}
for s in DEVP: page(B,"device",s[0],s[1],"Device Platform",s[2],s[3],s[4],s[5],s[6],s[7],DEV_EXTRA.get(s[0],""))

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

# ---- sitemap.xml + robots.txt (Google indexing) ----
SITE="https://unovie.ai"
LASTMOD="2026-06-05"   # bump when content materially changes (kept fixed for idempotent builds)
def _u(path):  # path relative to site root; "" = homepage
    return SITE + "/" + path
_pages=["", "about.html", "contact.html",
        "resources/edge-ai-models.html", "resources/edge-ai-whitepaper.html"]
_pages += [f"solutions/{s[0]}.html" for s in SOL]
_pages += [f"platform/{s[0]}.html" for s in PLATP]
_pages += [f"device/{s[0]}.html" for s in DEVP]
def _prio(p):
    if p=="": return "1.0"
    if p.startswith(("solutions/","platform/","device/")): return "0.9"
    if p.startswith("resources/"): return "0.6"
    return "0.7"
_rows="\n".join(
    f'  <url><loc>{_u(p)}</loc><lastmod>{LASTMOD}</lastmod><changefreq>monthly</changefreq><priority>{_prio(p)}</priority></url>'
    for p in _pages)
open(f"{ROOT}/sitemap.xml","w",encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + _rows + '\n</urlset>\n')
open(f"{ROOT}/robots.txt","w",encoding="utf-8").write(
    "User-agent: *\nAllow: /\n\n# Machine-readable indexes for AI agents\n# llms.txt: https://unovie.ai/llms.txt\n# llms-full.txt: https://unovie.ai/llms-full.txt\n# vector index: https://unovie.ai/agents/index.json\n\nSitemap: https://unovie.ai/sitemap.xml\n")

# ---- vector-ready index for agents (llms.txt discovery + agents/index.json chunks) ----
import html as _htmlmod, json as _json
def _strip(s):
    s=re.sub(r'<(script|style|svg)\b[^>]*>.*?</\1>',' ',s,flags=re.S|re.I)
    s=re.sub(r'<[^>]+>',' ',s)
    return re.sub(r'\s+',' ',_htmlmod.unescape(s)).strip()
def _pagetitle(h):
    m=re.search(r'<title>(.*?)</title>',h,re.S); return _strip(m.group(1)) if m else "Unovie.AI"
def _firstsent(t):
    t=_strip(t); return re.split(r'(?<=[.!?])\s',t,1)[0]
def _ptype(p):
    return ("home" if p=="" else "solution" if p.startswith("solutions/") else "platform" if p.startswith("platform/") else "device" if p.startswith("device/")
            else "resource" if p.startswith("resources/") else "company")
# chunked records, one per <section>, from the rendered HTML (nav/footer/scripts/svg stripped)
records=[]
for p in _pages:
    fp=f"{ROOT}/index.html" if p=="" else f"{ROOT}/{p}"
    try: h=open(fp,encoding="utf-8").read()
    except OSError: continue
    title=_pagetitle(h); url=_u(p); typ=_ptype(p)
    secs=re.findall(r'<section\b[^>]*>(.*?)</section>', h, flags=re.S) or [h]
    n=0
    for sec in secs:
        hm=re.search(r'<h[1-3][^>]*>(.*?)</h[1-3]>',sec,re.S)
        head=_strip(hm.group(1)) if hm else ""
        text=_strip(sec)
        if len(text)<40: continue
        n+=1
        records.append({"id":f"{(p or 'home').replace('/','_').replace('.html','')}#{n}",
                        "url":url,"type":typ,"title":title,"section":head,"text":text})
os.makedirs(f"{ROOT}/agents",exist_ok=True)
open(f"{ROOT}/agents/index.json","w",encoding="utf-8").write(_json.dumps({
    "site":SITE,"name":"Unovie.AI",
    "description":"Vector-ready content index of unovie.ai for AI agents and RAG ingestion. Each record is an embeddable chunk: {id,url,type,title,section,text}.",
    "schema":{"record":["id","url","type","title","section","text"]},
    "generated_by":"build_pages.py","lastmod":LASTMOD,"count":len(records),"records":records},
    ensure_ascii=False,indent=1))
# llms-full.txt — the entire site as one markdown document (https://llmstxt.org)
_byurl={}
for _r in records: _byurl.setdefault(_r["url"],[]).append(_r)
_full=["# Unovie.AI — full content for AI agents",
       "",
       "> Complete text of unovie.ai, generated from the live site for RAG and agent ingestion. Sections map to page sections; the same content is available as structured JSON chunks at https://unovie.ai/agents/index.json"]
_seen=set()
for _p in _pages:
    _url=_u(_p)
    if _url in _seen: continue
    _seen.add(_url)
    _rs=_byurl.get(_url)
    if not _rs: continue
    _full.append(f"\n\n# {_rs[0]['title']}\nURL: {_url}")
    for _r in _rs:
        _full.append(f"\n## {_r['section']}\n{_r['text']}" if _r['section'] else f"\n{_r['text']}")
open(f"{ROOT}/llms-full.txt","w",encoding="utf-8").write("\n".join(_full)+"\n")

# llms.txt — agent discovery index (https://llmstxt.org)
_sol="\n".join(f"- [{_strip(s[2])}]({_u('solutions/'+s[0]+'.html')}): {_firstsent(s[3])}" for s in SOL)
_plat="\n".join(f"- [{_strip(s[2])}]({_u('platform/'+s[0]+'.html')}): {_firstsent(s[3])}" for s in PLATP)
_dev="\n".join(f"- [{_strip(s[2])}]({_u('device/'+s[0]+'.html')}): {_firstsent(s[3])}" for s in DEVP)
open(f"{ROOT}/llms.txt","w",encoding="utf-8").write(f"""# Unovie.AI

> AI-engineering studio that designs, builds and operates custom edge-AI systems — fixed scope, fixed cost, on hardware you own. Built on the Nexus Context Platform: a typed knowledge graph + vector memory, edge GPU serving, and self-learning agents, all on-prem.

## Solutions
{_sol}

## Platform
{_plat}

## Device Platform
{_dev}

## Resources
- [Edge AI Models — Field Guide]({_u('resources/edge-ai-models.html')}): a 25-chapter architect's eBook on how edge-AI models actually learn.
- [Frozen-Base Doctrine — Whitepaper]({_u('resources/edge-ai-whitepaper.html')}): adapting custom models on the edge without retraining.

## Company
- [About]({_u('about.html')}): an AI-engineering studio for Industry 4.0, built in Austin, Texas.
- [Contact]({_u('contact.html')}): start a project.

## Machine-readable
- [Full content (llms-full.txt)]({SITE}/llms-full.txt): the entire site as one markdown document for direct LLM/agent consumption.
- [Vector index (JSON)]({SITE}/agents/index.json): embeddable, chunked content records for RAG.
- [Sitemap]({SITE}/sitemap.xml)
""")

print(f"built: index + {len(SOL)} solutions + {len(PLATP)} platform + {len(DEVP)} device + about + assets + sitemap({len(_pages)}) + agents-index({len(records)} chunks) + llms.txt + llms-full.txt")
