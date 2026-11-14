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
THEMEINIT = "<script data-theme-init>(function(){var m=false;try{m=matchMedia('(max-width:768px), (hover:none) and (pointer:coarse)').matches;}catch(e){}var s=null;try{s=m?sessionStorage.getItem('uvTheme'):localStorage.getItem('uvTheme');}catch(e){}document.documentElement.setAttribute('data-theme',(s==='light'||s==='dark')?s:(m?'dark':'light'));})();</script>"

# Google Analytics 4 (gtag.js). The config <script> carries a data-ga attribute so the
# homepage-slimming regex (which matches a bare <script>) never touches it.
GA = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-590ZL8SE2M"></script>
<script data-ga>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-590ZL8SE2M');</script>"""

NGBG = '<div class="ngbg" aria-hidden="true"></div>'

def HEAD(base,title,desc):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{GA}
<link rel="icon" href="{base}assets/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="{base}assets/favicon.png"><link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Hanken+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/site.css">{THEMEINIT}</head><body>
<div class="grain"></div><div class="cur"></div><div class="cur-r"></div>'''

def NAV(base):
    h=base+"index.html"
    return f'''<header class="nav"><div class="wrap"><div class="row">
  <a class="brand" href="{h}"><img class="logo" src="{base}assets/images/logo.png" alt="Unovie.AI"></a>
  <nav class="navlinks">
    <a href="{h}#accelerators">Agentic jobs</a>
    <div class="drop"><button data-cursor>Platform ▾</button><div class="menu">
      <a href="{base}platform/agentmesh.html"><span class="ic">01</span><span><span class="t">AgentMesh</span><br><span class="s">AI at the machine, next to the control system</span></span></a>
      <a href="{base}platform/agentnexus.html"><span class="ic">02</span><span><span class="t">AgentNexus</span><br><span class="s">Agents working across every site</span></span></a>
      <div class="msub">Hardware</div>
      <a href="{base}device-platform.html#ryzen-ai-max-395"><span class="ic">03</span><span><span class="t">AMD Ryzen AI Max+ 395</span><br><span class="s">Sovereign factory intelligence</span></span></a>
      <a href="{base}device-platform.html#agx-thor"><span class="ic">04</span><span><span class="t">NVIDIA Jetson AGX Thor</span><br><span class="s">Robotics &amp; DeepVision for fabs</span></span></a>
      <a href="{base}device-platform.html#dgx-spark"><span class="ic">05</span><span><span class="t">NVIDIA DGX Spark</span><br><span class="s">AI engineering lab &amp; training</span></span></a>
      <a href="{base}device-platform.html#qcs6490"><span class="ic">06</span><span><span class="t">Qualcomm QCS6490</span><br><span class="s">Mobile &amp; remote assets</span></span></a>
    </div></div>
    <div class="drop"><button data-cursor>Research ▾</button><div class="menu">
      <a href="{base}resources/agentnexus-architecture.html" target="_blank" rel="noopener"><span class="ic">01</span><span><span class="t">AgentNexus — Architecture Overview</span><br><span class="s">For architects and business leaders</span></span></a>
      <a href="{base}resources/edge-ai-models.html" target="_blank" rel="noopener"><span class="ic">02</span><span><span class="t">Edge AI Models — Field Guide</span><br><span class="s">A 25-chapter architect's eBook</span></span></a>
      <a href="{base}resources/edge-ai-whitepaper.html" target="_blank" rel="noopener"><span class="ic">03</span><span><span class="t">Frozen-Base Doctrine — Whitepaper</span><br><span class="s">Training without retraining</span></span></a>
      <a href="{base}gpu-edgegateway-whitepaper.html" target="_blank" rel="noopener"><span class="ic">04</span><span><span class="t">Edge-Native Economics — Whitepaper</span><br><span class="s">Predictable AI cost on owned silicon</span></span></a>
      <a href="{base}ai-soc-modernization-whitepaper.html" target="_blank" rel="noopener"><span class="ic">05</span><span><span class="t">AI SOC Modernization — Whitepaper</span><br><span class="s">Edge-native security for IT/OT</span></span></a>
    </div></div>
    <a href="{h}#engineering">AI Engineering</a>
    <a href="{base}why-unovie.html">Why Unovie</a>
  </nav>
  <a class="navcta" href="{h}#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
  <button class="burger" id="burger" aria-label="Menu">☰</button>
</div></div></header>
<div class="mobile" id="mobile">
  <a href="{base}platform/agentmesh.html"><span class="mono">01</span><br>AgentMesh</a>
  <a href="{base}platform/agentnexus.html"><span class="mono">02</span><br>AgentNexus</a>
  <a href="{h}#accelerators"><span class="mono">03</span><br>Agentic jobs</a>
  <a href="{base}device-platform.html"><span class="mono">04</span><br>Hardware</a>
  <a href="{base}why-unovie.html"><span class="mono">05</span><br>Why Unovie</a>
  <a href="{h}#engineering"><span class="mono">06</span><br>AI Engineering</a>
  <a href="{base}resources/agentnexus-architecture.html" target="_blank"><span class="mono">07</span><br>Architecture overview</a>
  <a href="{h}#contact" style="color:var(--accent)"><span class="mono">08</span><br>Pilot on your line →</a>
</div>'''

def FOOTER(base):
    h=base+"index.html"
    return f'''<footer><div class="wrap"><div class="fgrid">
  <div class="fcol fbrand"><a class="brand" href="{h}"><img class="logo" src="{base}assets/images/logo.png" alt="Unovie.AI"></a>
    <p>Agent-native industrial AI. We design, build, and operate custom Edge-AI Agentic Systems — on AMD or NVIDIA hardware you own.</p></div>
  <div class="fcol"><h4>Platform</h4>
    <a href="{base}platform/agentmesh.html">AgentMesh</a><a href="{base}platform/agentnexus.html">AgentNexus</a></div>
  <div class="fcol"><h4>Hardware</h4>
    <a href="{base}device-platform.html#ryzen-ai-max-395">AMD Ryzen AI Max+ 395</a><a href="{base}device-platform.html#agx-thor">NVIDIA Jetson AGX Thor</a><a href="{base}device-platform.html#dgx-spark">NVIDIA DGX Spark</a><a href="{base}device-platform.html#qcs6490">Qualcomm QCS6490</a></div>
  <div class="fcol"><h4>Company</h4>
    <a href="{base}why-unovie.html">Why Unovie</a><a href="{h}#engineering">AI Engineering</a><a href="{h}#delivery">How we deliver</a>
    <a href="{base}about.html">About</a><a href="{base}contact.html">Contact</a></div>
  <div class="fcol"><h4>Research</h4>
    <a href="{base}resources/agentnexus-architecture.html" target="_blank">AgentNexus Architecture</a><a href="{base}resources/edge-ai-models.html" target="_blank">Field Guide (eBook)</a><a href="{base}resources/edge-ai-whitepaper.html" target="_blank">Whitepaper</a><a href="{base}gpu-edgegateway-whitepaper.html" target="_blank">Edge-Native Economics</a><a href="{base}ai-soc-modernization-whitepaper.html" target="_blank">AI SOC Modernization</a></div>
</div><div class="fbot"><span>© 2026 Unovie · Agent-native industrial AI</span><span>Engineered for the edge with NVIDIA · AMD · Qualcomm · Siemens · GE</span></div></div></footer>
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
    body=f'''{NGBG if folder=='platform' else ''}{NAV(base)}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="{base}index.html">Home</a><span class="sep">/</span><a href="{base}index.html#{'accelerators' if folder=='solutions' else 'platform'}">{crumb_cat}</a><span class="sep">/</span><span style="color:var(--fg-mut)">{re.sub('<[^>]+>','',title_html)}</span></div>
  <div class="tag rv">{cat}</div>
  <h1 class="rv" style="margin-top:18px">{title_html}</h1>
  <p class="lead rv">{lead}</p>
  <div class="cta rv"><a class="btn btn-acc" href="{base}index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
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
  <div class="cta"><a class="btn btn-acc" href="/contact.html" data-m="moc.eivonu|snoitulos" data-subject="Project enquiry" data-cursor>Talk to our engineers <span class="ar">→</span></a>
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
RETIRED_SOL=[x[0] for x in SOL]; SOL=[]  # solution pages retired (deep-tech repositioning); URLs 301 via _redirects
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
  "Most gateways sit in front of the models and treat inference as a black box. This one is built from the inference engine out: one routing contract turns signals into projections, projections into decisions, and decisions into the model — across a mesh of local, private and frontier engines — while the prefix cache is protected, context is selected rather than pasted, and every turn takes the least-cost path that still meets the need. Session-aware across long-running agents, sandboxed for tool safety, and shadow-tested before any policy goes live. OpenAI- and Anthropic-compatible, multimodal, governed like production, on hardware you own.",
  [("signal→model","one routing contract"),("prefix-cache","reuse-protected"),("least cost","per-turn path")],
  ("Route, reason, act",[("/route","Signal-driven routing","Intent, complexity, modality and risk become projections and policy bands, then route across a local-to-frontier mesh — reasoning only when it pays.",["intent","projections","when-to-reason"]),
   ("/session","Session-aware agentic routing","Stateful guards keep multi-turn agents coherent: hard locks block unsafe model switches mid-tool-loop, weighing quality gap, prefix locality and turn priors.",["session-aware","tool-loop locks","continuity"]),
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
   '<section><div class="wrap"><div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>Control plane · data plane</div><h2 class="rv">A self-improving <span class="serif" style="color:var(--steel)">router.</span></h2></div><p class="lead rv">A control plane governs policy, identity and guardrails; a data plane serves fast, observable, cost-aware inference; and a self-improving router between them turns every request into a better next decision — protecting the prefix cache and selecting context so the work stays cheap as it grows.</p></div><div class="gwwrap rv">' + GW_SVG + '</div></div></section>'
   + f'<section><div class="wrap">{shead("03","Architecture","Inside the gateway")}'
   + disc([
     ("/contract","One routing contract","Signals become projections, projections drive decisions, decisions choose the model — the same pipeline whether configured in YAML, the console, the CLI or Kubernetes.",["signals","projections","decisions"]),
     ("/mesh","Mixture-of-models mesh","Token- and capability-aware routing spans self-hosted engines, local SLMs and frontier APIs with semantic caching; classifiers run on any accelerator — one control plane, any backend.",["self-hosted","semantic cache","any accelerator"]),
     ("/safe","Safety &amp; protocol","History-aware PII, jailbreak and prompt-injection scanning across every turn — behind an OpenAI- and Anthropic-compatible ingress with explicit, lossless translation.",["PII","jailbreak","OpenAI/Anthropic"]),
     ("/cache","Prefix-cache discipline","Stable prompt epochs, deterministic tool-schema ordering and bounded, append-only context keep reusable prefixes intact — so cached tokens are reused across a long session at a fraction of the price instead of re-billed every turn.",["prompt epochs","stable schema","cache reuse"]),
     ("/lifecycle","Shadow, activate, revert","Every routing policy is versioned and shadow-tested on replayed traffic before activation, with one-click rollback — routing never drifts silently.",["shadow","replay","rollback"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("04","Agent-first delivery","Multimodal in, action out")}'
   + disc([
     ("/multimodal","Every modality, one path","Text, voice, image and event inputs are normalised, routed to the right modality model, and turned into grounded responses or tool actions.",["text·voice·image","normalise","actions"]),
     ("/context","Context selected, not pasted","Graph-shaped code evidence, bounded tool output and domain-aware compression extract the signal a turn actually needs and drop the rest — fewer prompt and tool-output tokens, without losing continuity across a long task.",["select not paste","graph context","bounded output"]),
     ("/observe","Topology &amp; token ledger","A console traces every signal &#8594; projection &#8594; decision with replay, and a live ledger shows cache reuse, context savings and per-route latency, tokens and cost — spend is accountable while the task runs, not after.",["topology","savings ledger","metering"]),
   ]) + '</div></section>'
   + f'<section><div class="wrap">{shead("05","By the numbers","Governed like production")}'
   + metrics([("&lt;1<span class='o'>ms</span>","signal → decision"),("~90<span class='o'>%</span>","cached-token discount"),("least cost","per-turn path"),("shadow→activate","policy lifecycle")])
   + '</div></section>'
   + '<section><div class="wrap">' + shead("06","Further reading","Whitepapers for your team","The architecture and the economics behind this platform — read in the browser or export to PDF.")
   + '<div class="disc">'
   + '<a class="dcard rv" href="../gpu-edgegateway-whitepaper.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><div class="ix">/economics</div><h3>The Edge-Native Inference Gateway</h3><p>For infrastructure leaders: turning unpredictable, metered AI opex into fixed, predictable cost for the industrial edge.</p><div class="spec"><span class="chip">predictable cost</span><span class="chip">edge-native</span><span class="chip">PDF</span></div></a>'
   + '<a class="dcard rv" href="../resources/edge-ai-whitepaper.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--accent)"></div><div class="ix">/doctrine</div><h3>Training Without Retraining</h3><p>The frozen-base doctrine: adapting custom models on the edge through context and self-verification, not weight updates.</p><div class="spec"><span class="chip">frozen-base</span><span class="chip">on-device</span><span class="chip">PDF</span></div></a>'
   + '</div></div></section>'
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
   + '<section><div class="wrap">' + shead("06","Further reading","Whitepapers for your team","The architecture and the economics behind this platform — read in the browser or export to PDF.")
   + '<div class="disc">'
   + '<a class="dcard rv" href="../ai-soc-modernization-whitepaper.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><div class="ix">/ai-soc</div><h3>AI SOC Modernization</h3><p>For CISOs: an edge-native, identity-driven AI SOC for distributed IT/OT in the agentic era — detection at ingest, knowledge-graph context, autonomous response.</p><div class="spec"><span class="chip">IT/OT</span><span class="chip">identity-driven</span><span class="chip">PDF</span></div></a>'
   + '<a class="dcard rv" href="../gpu-edgegateway-whitepaper.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--accent)"></div><div class="ix">/economics</div><h3>The Edge-Native Inference Gateway</h3><p>Turning unpredictable, metered AI opex into fixed, predictable cost for the industrial edge.</p><div class="spec"><span class="chip">predictable cost</span><span class="chip">edge-native</span><span class="chip">PDF</span></div></a>'
   + '</div></div></section>'
 ),
}
SVG_MESH='<svg class="axviz" viewBox="0 0 1000 430" role="img" aria-label="AgentMesh: asset signals flow into the Sovereign Pod, which perceives, decides, reasons and adapts; Lane A acts directly on low-consequence outputs, Lane B raises an alarm and a request to the PLC or safety system and the operator; work orders go to the maintenance system and every decision is written to the Evidence Log."><defs><marker id="axh" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs><text x="20" y="22" class="l">ASSET SIGNALS</text><rect x="20" y="36" width="210" height="52" rx="10" class="bx"/><text x="34" y="60" class="t">Vibration · ultrasonic</text><text x="34" y="80" class="s">accelerometers, acoustic</text><line x1="230" y1="62" x2="288" y2="215" class="lk" marker-end="url(#axh)"/><rect x="20" y="100" width="210" height="52" rx="10" class="bx"/><text x="34" y="124" class="t">Electrical</text><text x="34" y="144" class="s">power quality, partial discharge</text><line x1="230" y1="126" x2="288" y2="215" class="lk" marker-end="url(#axh)"/><rect x="20" y="164" width="210" height="52" rx="10" class="bx"/><text x="34" y="188" class="t">Battery data</text><text x="34" y="208" class="s">cells, temperature, off-gas</text><line x1="230" y1="190" x2="288" y2="215" class="lk" marker-end="url(#axh)"/><rect x="20" y="228" width="210" height="52" rx="10" class="bx"/><text x="34" y="252" class="t">Test-rig channels</text><text x="34" y="272" class="s">pressure, strain, acoustics</text><line x1="230" y1="254" x2="288" y2="215" class="lk" marker-end="url(#axh)"/><rect x="20" y="292" width="210" height="52" rx="10" class="bx"/><text x="34" y="316" class="t">Weld current</text><text x="34" y="336" class="s">process signatures</text><line x1="230" y1="318" x2="288" y2="215" class="lk" marker-end="url(#axh)"/><rect x="20" y="356" width="210" height="52" rx="10" class="bx"/><text x="34" y="380" class="t">OT network · alarms</text><text x="34" y="400" class="s">control traffic, alarm floods</text><line x1="230" y1="382" x2="288" y2="215" class="lk" marker-end="url(#axh)"/><rect x="290" y="30" width="420" height="380" rx="14" class="bx-a"/><text x="310" y="56" class="l">AGENTMESH · SOVEREIGN POD · FACTORY NETWORK</text><rect x="310" y="70" width="380" height="66" rx="10" class="bx"/><text x="324" y="94" class="t">1 · Perceive</text><text x="324" y="114" class="s">Unovie Gateway (read-only) → Signal Encoders</text><rect x="310" y="154" width="380" height="66" rx="10" class="bx"/><text x="324" y="178" class="t">2 · Decide</text><text x="324" y="198" class="s">Vector Memory + Unovie Decision Engine</text><rect x="310" y="238" width="380" height="66" rx="10" class="bx"/><text x="324" y="262" class="t">3 · Reason</text><text x="324" y="282" class="s">Unovie Reasoning Model drafts root cause</text><rect x="310" y="322" width="380" height="66" rx="10" class="bx"/><text x="324" y="346" class="t">4 · Adapt</text><text x="324" y="366" class="s">Kiln: nightly, tested, signed</text><text x="310" y="402" class="s">air-gapped by default · 30 ms decision budget (target)</text><text x="770" y="22" class="l">OUTCOMES</text><rect x="770" y="36" width="210" height="70" rx="10" class="bx-a"/><text x="784" y="60" class="t">Lane A · acts directly</text><text x="784" y="80" class="s">reject gate · diverter</text><text x="784" y="98" class="s">IT-side quarantine</text><rect x="770" y="122" width="210" height="70" rx="10" class="bx-s"/><text x="784" y="146" class="t">Lane B · alarm + request</text><text x="784" y="166" class="s">PLC / safety system</text><text x="784" y="184" class="s">and operator decide</text><rect x="770" y="208" width="210" height="56" rx="10" class="bx"/><text x="784" y="232" class="t">Work order</text><text x="784" y="252" class="s">to SAP / Maximo</text><rect x="770" y="280" width="210" height="56" rx="10" class="bx"/><text x="784" y="304" class="t">Evidence Log</text><text x="784" y="324" class="s">signed record of every decision</text><line x1="690" y1="187" x2="768" y2="71" class="lk-a" marker-end="url(#axh)"/><line x1="690" y1="190" x2="768" y2="157" class="lk-s" marker-end="url(#axh)"/><line x1="690" y1="271" x2="768" y2="236" class="lk" marker-end="url(#axh)"/><line x1="690" y1="350" x2="768" y2="308" class="lk" marker-end="url(#axh)"/><text x="770" y="372" class="s">plant control stays with</text><text x="770" y="390" class="s">your PLCs and operators</text></svg>'
SVG_NEXUS='<svg class="axviz" viewBox="0 0 1000 430" role="img" aria-label="AgentNexus: AgentMesh pods at many sites connect to one AgentNexus rack, which runs agents in sealed sandboxes, the Unovie Model Router and models, the Kiln for new skill adapters, and a platform that copies data across shelves. Results go to IT systems; plant control stays at the plant."><defs><marker id="axh" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs><text x="20" y="22" class="l">SITES</text><rect x="20" y="40" width="190" height="64" rx="10" class="bx"/><text x="34" y="64" class="t">AgentMesh pod</text><text x="34" y="84" class="s">Site A · fast local loop</text><line x1="210" y1="72" x2="268" y2="215" class="lk" marker-end="url(#axh)" marker-start="url(#axh)"/><rect x="20" y="132" width="190" height="64" rx="10" class="bx"/><text x="34" y="156" class="t">AgentMesh pod</text><text x="34" y="176" class="s">Site B · fast local loop</text><line x1="210" y1="164" x2="268" y2="215" class="lk" marker-end="url(#axh)" marker-start="url(#axh)"/><rect x="20" y="224" width="190" height="64" rx="10" class="bx"/><text x="34" y="248" class="t">AgentMesh pod</text><text x="34" y="268" class="s">Site C · fast local loop</text><line x1="210" y1="256" x2="268" y2="215" class="lk" marker-end="url(#axh)" marker-start="url(#axh)"/><text x="20" y="330" class="s">… and every other site,</text><text x="20" y="348" class="s">over encrypted links</text><rect x="270" y="30" width="460" height="380" rx="14" class="bx-a"/><text x="290" y="56" class="l">AGENTNEXUS · CENTRAL CABINET · 0.5 s RESPONSE BUDGET</text><rect x="290" y="70" width="420" height="66" rx="10" class="bx-s"/><text x="304" y="94" class="t">Agents · Unovie Agent Runtime</text><text x="304" y="114" class="s">sealed sandboxes · sleep when idle · wake on demand</text><rect x="290" y="148" width="420" height="84" rx="10" class="bx"/><text x="304" y="172" class="t">Models · Unovie Model Router</text><text x="304" y="192" class="s">Unovie Decision Models pick the route</text><text x="304" y="210" class="s">Unovie Reasoning Model + skill adapters · Vector Memory</text><rect x="290" y="244" width="420" height="66" rx="10" class="bx"/><text x="304" y="268" class="t">Learning · Kiln</text><text x="304" y="288" class="s">new skill adapters: train → test → trial → switch on</text><rect x="290" y="322" width="420" height="66" rx="10" class="bx"/><text x="304" y="346" class="t">Platform · Mesh Arbiter</text><text x="304" y="366" class="s">12 shelves · one cluster · data copied across shelves</text><text x="790" y="22" class="l">BUSINESS</text><rect x="790" y="60" width="190" height="64" rx="10" class="bx"/><text x="804" y="84" class="t">IT systems</text><text x="804" y="104" class="s">SAP · Maximo · reports</text><rect x="790" y="170" width="190" height="64" rx="10" class="bx"/><text x="804" y="194" class="t">People</text><text x="804" y="214" class="s">engineers · operators</text><rect x="790" y="300" width="190" height="64" rx="10" class="bx-d"/><text x="804" y="326" class="t">Never moves</text><text x="804" y="346" class="s">equipment</text><line x1="730" y1="120" x2="788" y2="92" class="lk" marker-end="url(#axh)"/><line x1="730" y1="190" x2="788" y2="202" class="lk" marker-end="url(#axh)"/></svg>'
# ===================== MOCK: Unovie Platform (AgentMesh + AgentNexus) =====================
A="<span class='serif' style='color:var(--accent)'>"; T="<span class='serif' style='color:var(--steel)'>"; E="</span>"

def runs(items):  # (status, now?, title, text)
    cells="".join(f'<div class="run rv"><span class="st{" now" if now else ""}">{st}</span><h4>{t}</h4><p>{d}</p></div>' for st,now,t,d in items)
    return f'<div class="runs">{cells}</div>'
def diagram(svg, caption):
    return f'<div class="axwrap rv">{svg}</div><p class="lead rv" style="margin-top:14px;font-size:15px">{caption}</p>'
def sec(num,label,title,body,lead=""):
    return f'<section><div class="wrap">{shead(num,label,title,lead)}{body}</div></section>'

PLATP=[
 ("agentmesh","Platform · AgentMesh","Agent"+A+"Mesh"+E,
  "AgentMesh brings Agentic Physical AI into next-generation factories — battery lines, chip fabs and suppliers, space hardware, robotics and autonomous systems: it sits beside robots, tools and test systems and puts AI on the signals they produce — vibration, ultrasonic, electrical, battery and OT-network data — in a Sovereign Pod on the plant network. It spots what is going wrong inside a 30-millisecond decision budget, acts on its own only where the consequence is low, and sends anything safety-related to your PLC, safety system and operators as an alarm and a request. Every decision is written to a signed Evidence Log. Air-gapped by default, on AMD or NVIDIA hardware you own.",
  [("&lt;30<span class='o'>ms</span>","decision budget · target"),("0<span class='o'>B</span>","leaves the site by default"),("10","domain kits")],
  ("Four jobs at the machine",[
   ("/perceive","Perceive the asset's own signals","The Unovie Gateway reads sensors, data-acquisition boxes, historian tags and network traffic — read-only, with allow-listed protocols and an audit trail. Signal Encoders turn each window of signal into a compact fingerprint.",["vibration","electrical","battery","OT network"]),
   ("/decide","Decide, with a safety boundary","Vector Memory answers \"have we seen this before, and was it bad?\" The Unovie Decision Engine applies your rules and a small decision model, then picks a lane: Lane A acts directly on low-consequence outputs; Lane B raises an alarm and a request.",["Lane A","Lane B","rules + model"]),
   ("/reason","Explain it, and draft the work","After the event, the Unovie Reasoning Model pulls in equipment history, manuals and past failures, names the likely root cause and drafts the work order. It is never in the path that moves equipment.",["root cause","work orders","on-site model"]),
   ("/adapt","Improve every night, safely","The Kiln replays the day, proposes at most three playbook edits and keeps them only if they beat a held-out test. Model weights stay frozen in the field; every change is signed and can be rolled back.",["Kiln","held-out test","signed"])]),
  ("Signal to action",[("Sense","Read-only taps stream asset signals."),("Decide","Compare, apply rules, choose a lane."),("Act or request","Lane A acts; Lane B alarms and asks."),("Record","Evidence Log entry and a drafted work order.")]),
  "Put AI on "+A+"your equipment's signals."+E),
 ("agentnexus","Platform · AgentNexus","Agent"+A+"Nexus"+E,
  "AgentNexus is where your AI agents work across sites — gigafactories and storage fleets, factories and test stands, fabs and their suppliers, robot fleets and dual-use programs. One rack in a central cabinet hosts thousands of agents in sealed sandboxes, connects to every AgentMesh pod in your fleet, and turns plant events into cross-site analysis, maintenance plans and work orders — answering within half a second. It learns from what happens in production, tests every improvement before it goes live, and never moves plant equipment. On AMD or NVIDIA hardware you own.",
  [("0.5<span class='o'>s</span>","response budget · target"),("48","servers in one 42U rack"),("0","equipment it controls")],
  ("One rack, three layers",[
   ("/agents","Agents in sealed sandboxes","The Unovie Agent Runtime gives every agent its own sealed space. Idle agents are saved and put to sleep, then woken on any free server when they're needed — so one rack holds far more agents than it could keep running. Network access is allow-listed and passwords never reach the agent.",["sandboxed","sleep and wake","allow-listed"]),
   ("/models","One model family, specialised per job","The Unovie Model Router reads each request and, with the Unovie Decision Models, picks the model and the skill adapter. The Unovie Reasoning Model answers — a compact copy for speed, a full copy that takes skill adapters swapped in while it runs. Vector Memory powers search.",["model router","skill adapters","open weights"]),
   ("/learn","Gets better from production","Outcomes reported by agents and operators become training data. The Kiln trains new skill adapters on the rack, tests them on cases they have never seen, tries them on a slice of live traffic and switches them on only if they do better.",["train","test","trial","switch on"]),
   ("/resilient","Built to keep running","Twelve identical shelves of four servers run as one system. Important data is copied across shelves and the Mesh Arbiter moves work when a server or a whole shelf stops — losing capacity, not saved work.",["12 shelves","copied data","Mesh Arbiter"])]),
  ("Plant event to business action",[("Event","An AgentMesh pod sends what it found."),("Wake","The right agent wakes in its sandbox."),("Reason","Models compare across sites and history."),("Act","Work orders and reports reach IT systems.")]),
  "Run agents "+A+"across every site."+E),
 ("edge-streaming-analytics","Platform · Capability","Asset Signal "+T+"Intelligence"+E,
  "The signals that tell you an asset is failing are fast and specific: vibration and ultrasonic at up to 25.6 kHz, power-quality and partial-discharge waveforms, battery cell data, test-rig pressure and strain, weld current, control-system tags and network traffic. Asset Signal Intelligence reads them read-only, turns them into fingerprints and compares them with your plant's own history in real time. It is not video monitoring: imaging is used only as context.",
  [("25.6<span class='o'>kHz</span>","vibration sampling"),("read-only","plant connections"),("0","cameras required")],
  ("Signals, not screens",[
   ("/connect","Read-only plant connections","The Unovie Gateway connects to data-acquisition boxes, industrial protocols, historians and a network mirror port — read-only, with allow-listed protocols and an audit trail.",["DAQ","historian","mirror port"]),
   ("/encode","A fingerprint for every window","Signal Encoders built for each signal type turn raw waveforms into compact fingerprints, on the GPU or the NPU where it fits.",["spectral","signature","fingerprint"]),
   ("/memory","Seen this before?","Vector Memory finds the closest past patterns and what happened next, so a new fault is judged against your plant's own record, not a generic threshold.",["Vector Memory","history","labels"])]),
  ("Signal to fingerprint",[("Connect","Read-only taps on sensors and tags."),("Window","Buffer each channel in short windows."),("Encode","Turn windows into fingerprints."),("Compare","Match against the plant's history.")]),
  "Listen to "+T+"your assets."+E),
 ("edge-data-fabric","Platform · Capability","Unovie Context "+T+"Fabric"+E,
  "Your plant's own knowledge — assets, sensors, lines, procedures, past failures and work orders — modelled as a typed plant model, a knowledge graph and Vector Memory, on-prem. AgentMesh uses it to explain an event in seconds; AgentNexus uses it to reason across sites. You can buy models and agents; your context is the part only you can build, and it stays yours.",
  [("plant","model, typed"),("graph<span class='s'>+vector</span>","recall"),("0<span class='o'>B</span>","egress · on-prem")],
  ("Context that compounds",[
   ("/model","A plant model","Assets, lines, sensors, procedures and failure modes as typed entities and relationships — the what, where, when and why behind every signal.",["assets","procedures","failures"]),
   ("/graph","Knowledge graph + Vector Memory","Structure and meaning side by side: follow the links from a pump to its motor, its manual and its last failure, and find similar cases by meaning.",["graph","vector","both"]),
   ("/ask","Ask in plain language","Engineers and planners ask questions and get answers traced back to the source document or record — no query language, no data team in the loop.",["plain language","traceable","self-service"])]),
  ("Documents in, decisions out",[("Extract","Read manuals, records and tables."),("Build","Grow the plant model and graph."),("Index","Add meaning for search."),("Serve","Grounded answers for agents and people.")]),
  "Know your plant — and "+T+"why."+E),
 ("gpu-edgegateway","Platform · Capability","Unovie Model "+T+"Router"+E,
  "One address for every model request. The Unovie Model Router reads each request, asks the Unovie Decision Models which model and skill adapter fit, and sends it to the right server in your rack — a compact model for speed, a full model with a task-specific skill adapter when the job needs it. Safety checks run on every turn, routing rules are trialled on recorded traffic before they go live, and every route is traced and metered.",
  [("one","address for every agent"),("≤100<span class='o'>ms</span>","routing budget · target"),("trial → live","rule lifecycle")],
  ("Route, check, record",[
   ("/route","The right model, every time","Request type, difficulty and risk decide the route, so simple work stays fast and only hard work uses the bigger model.",["routing","skill adapters","cost-aware"]),
   ("/decide","Typed decisions, not guesses","The Unovie Decision Models answer fixed questions — which option, yes or no, how urgent — with a probability for each answer, in one quick pass.",["Decision Models","probabilities","fast"]),
   ("/govern","Safe and accountable","Sensitive data and unsafe requests are caught inline; every routing change is versioned, trialled and reversible.",["inline checks","versioned","reversible"])]),
  ("Request to answer",[("Read","Understand the request and its risk."),("Decide","Decision Models pick model and adapter."),("Serve","The chosen server answers."),("Record","Trace, cost and outcome logged.")]),
  "The right model, "+T+"every request."+E),
 ("edge-security-intelligence","Platform · Capability","OT Security "+T+"Intelligence"+E,
  "Threats on the plant network are caught while the data is still moving. Control traffic, logs and alarm streams are read in flight: unauthorized writes to controllers, unusual commands, alarm floods and lateral movement are flagged as they happen, and every finding becomes evidence for your cybersecurity plan and auditors. Delivered as the OT Network Watch and Alarm Flood Triage domain kits, on-prem.",
  [("in flight","not after the fact"),("read-only","network mirror"),("signed","evidence")],
  ("Detection on the plant network",[
   ("/writes","Unauthorized writes","Writes to controllers from unexpected sources or outside allowed windows are flagged at once, with the full context of who, what and when.",["controllers","allow-lists","context"]),
   ("/alarms","Alarm flood triage","When hundreds of alarms fire together, the first-out cause is found and ranked so operators see what started it.",["first-out","ranking","operators"]),
   ("/evidence","Evidence you can hand over","Every detection is recorded in the Evidence Log and summarised for cybersecurity plans and audits.",["Evidence Log","audit","plans"])]),
  ("Traffic to evidence",[("Mirror","Copy network traffic, read-only."),("Read","Understand control commands and alarms."),("Flag","Score what is unusual or unsafe."),("Record","Evidence and a clear summary.")]),
  "Secure the plant "+T+"network."+E),
 ("gpu-microcloud","Platform · Capability","Private AI "+T+"Rack"+E,
  "The platform under AgentNexus: twelve shelves of four servers in one 42U rack, run as a single system on your floor. Two network switches, fast cables inside each shelf, copies of important data on more than one shelf, and the Mesh Arbiter to move work when a server or a whole shelf stops. AMD or NVIDIA servers, shared fairly between teams and metered like cloud — without the cloud.",
  [("42U","12 shelves × 4 servers"),("1","system to run"),("2","switches · no single point")],
  ("Your AI servers, run like cloud",[
   ("/place","Work placed by role","Each server's role — answering, specialised answering, training — is a label, so capacity moves between jobs without reinstalling.",["roles","labels","no reinstall"]),
   ("/protect","Data protected across shelves","Records and saved agents are copied across shelves, so losing a server or a shelf loses capacity, not work.",["copies","shelves","recovery"]),
   ("/meter","Shared fairly, metered","Teams and sites get quotas; every job is accounted for, so shared capacity becomes clear cost.",["quotas","metering","showback"])]),
  ("Rack to service",[("Rack","Identical shelves, one design."),("Join","One system across all shelves."),("Protect","Data copied across shelves."),("Meter","Per-team accounting.")]),
  "AI capacity you "+T+"own."+E),
]

PLAT_EXTRA={
 "agentmesh": sec("03","Architecture","Inside the Sovereign Pod", diagram(SVG_MESH,"AgentMesh sits in the plant's industrial DMZ, reads asset signals read-only and keeps the fast loop local. Low-consequence actions happen directly; safety decisions stay with your PLC, safety system and operators."))
   + sec("04","Domain kits","Packaged for the assets you run", disc([
     ("/rotating","Rotating Equipment Health","Bearings, cavitation and imbalance on pumps, compressors, motors and drives — fault class, severity and a drafted work order.",["vibration","ultrasonic","work order"]),
     ("/battery","Battery Safety Fusion","Early warning of thermal-runaway precursors from battery data and off-gas sensors, as an alarm into the fire panel.",["BMS","off-gas","Lane B"]),
     ("/electrical","Electrical Health","Early signs of arcing and insulation failure in switchgear, transformers and inverters.",["partial discharge","power quality"]),
     ("/leak","Leak &amp; Energy Loss","Ranked leak lists with a value attached, from airborne ultrasonic, flow and pressure data.",["ultrasonic","flow","value"]),
     ("/test","Test Campaign Monitor","Anomaly flags to the test conductor during a run, and a drafted post-test report.",["pressure","strain","acoustics"]),
     ("/ot","OT Network Watch","Unauthorized writes and unusual commands on the plant network, with evidence for cybersecurity plans.",["control traffic","alarms","evidence"]),
   ]))
   + sec("05","Runs on","AMD or NVIDIA hardware you own", runs([
     ("Runs today",True,"AMD Ryzen AI Max+ 395","The reference Sovereign Pod: four nodes in 3U, quiet enough for a rack on the factory floor."),
     ("Available on",False,"NVIDIA Jetson AGX Thor","Robotics and DeepVision at the tool — inspection, robot cells and wafer handling in the fab."),
     ("Available on",False,"NVIDIA DGX Spark","The AI engineering lab — test stands, replay and a single-unit AgentMesh for a pilot."),
   ]) + '<p class="lead rv" style="font-size:15px;margin-top:16px">Same domain kits, same safety lanes, same Evidence Log on every platform. <a href="../device-platform.html" style="color:var(--accent)">Compare the hardware →</a></p>')
   + sec("06","Why teams choose it","Built for the plant, not the slide", disc([
     ("/control","Works with your control system","Lane A outputs and Lane B request registers fit how plants already run: the PLC, the safety system and the operator stay in charge.",["PLC","safety system","operator"]),
     ("/own","You own it","Off-the-shelf hardware, models that run without us, and an evidence pack and playbooks that belong to you.",["no lock-in","on-site","yours"]),
     ("/price","Priced per asset and kit","Value is measured in failures, leaks and scrap avoided — not in seats.",["per asset","per kit","outcomes"]),
   ])),
 "agentnexus": sec("03","Architecture","One rack for a fleet of plants", diagram(SVG_NEXUS,"AgentMesh keeps the fast loop at each plant. AgentNexus works at business speed across all of them, sends results to your business systems, and never moves plant equipment."))
   + sec("04","What it runs","Agents, models and learning in one place", disc([
     ("/runtime","Unovie Agent Runtime","Sealed sandboxes, sleep and wake on demand, allow-listed network access and no passwords in agents' hands.",["sandboxes","wake on demand"]),
     ("/router","Unovie Model Router + Decision Models","Picks the model and skill adapter for every request; small decision models answer typed questions with probabilities.",["routing","typed decisions"]),
     ("/reasoning","Unovie Reasoning Model + skill adapters","One open-weight model family for every answer, specialised per job by small adapters that are swapped in without a restart.",["open weights","skill adapters"]),
     ("/kiln","Kiln","Trains, tests, trials and promotes new skill adapters from production outcomes — nothing goes live without beating what's running.",["train","test","promote"]),
   ]))
   + sec("05","Runs on","AMD or NVIDIA hardware you own", runs([
     ("Reference design",True,"AMD Ryzen AI Max+ 395 rack","Twelve shelves of four servers in one 42U rack — the same server as the AgentMesh pod."),
     ("Available on",False,"NVIDIA DGX Spark","One to four units for a site or a pilot, and the place new skill adapters are trained."),
     ("Pairs with",False,"Every AgentMesh pod","On AMD or NVIDIA Jetson AGX Thor, at every plant in the fleet."),
   ]))
   + sec("06","By design","Sized for a fleet", metrics([("~860","agents awake at once · estimate"),("1000s","agents in total, mostly asleep"),("4 of 12","shelves can fail without losing saved agents")])
     + '<p class="lead rv" style="font-size:15px;margin-top:16px">Estimates from measurements on single servers; we replace them with measured numbers after our bench tests.</p>'
     + '<div class="disc" style="margin-top:22px"><a class="dcard rv" href="../resources/agentnexus-architecture.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><div class="ix">/architecture</div><h3>AgentNexus — Architecture Overview</h3><p>How the rack is organised, what happens step by step, how data is kept safe and what happens when something breaks — written for architects and business leaders.</p><div class="spec"><span class="chip">overview</span><span class="chip">diagrams</span></div></a></div>'),
 "edge-streaming-analytics": sec("03","Signals we read","The data that predicts failure", disc([
     ("/vibration","Vibration and ultrasonic","Accelerometers and acoustic sensors on bearings, gearboxes, pumps and compressors.",["25.6 kHz","bearings"]),
     ("/electrical","Electrical waveforms","Power quality and partial discharge in switchgear, transformers and inverters.",["power quality","partial discharge"]),
     ("/battery","Battery systems","Cell voltage and temperature, read-only from the battery management system, plus off-gas sensors.",["cells","off-gas"]),
     ("/process","Process signatures","Weld current, test-rig pressure and strain, and control-system tags from the historian.",["weld","test rig","historian"]),
   ])) + sec("04","By the numbers","Engineered for fast signals", metrics([("25.6<span class='o'>kHz</span>","per vibration channel"),("&lt;30<span class='o'>ms</span>","to a decision · target"),("read-only","by design")])),
 "edge-data-fabric": sec("03","How it's built","From documents to a living plant model", disc([
     ("/extract","Reads what you already have","Manuals, procedures, maintenance records and tables become structured records.",["manuals","records"]),
     ("/link","Links it together","Records become a typed graph: this pump, its motor, its manual, its last three failures.",["graph","links"]),
     ("/find","Finds by meaning","Vector Memory finds similar cases even when the words differ.",["meaning","similar cases"]),
     ("/history","Keeps the history","Every change is versioned with an audit trail, so you can see what was known when.",["versioned","audit"]),
   ])),
 "gpu-edgegateway": sec("03","How it decides","Typed questions, clear answers", disc([
     ("/choice","Which option?","Pick a model, an adapter or a route from a fixed list — with a probability for each.",["choice"]),
     ("/yesno","Yes or no?","Is this safe, is it in scope, does it need a person?",["yes / no"]),
     ("/score","How much?","Urgency, difficulty or risk on a fixed scale.",["score"]),
   ])) + '<section><div class="wrap">' + shead("04","Further reading","The economics behind it","Read in the browser or export to PDF.")
   + '<div class="disc"><a class="dcard rv" href="../gpu-edgegateway-whitepaper.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><div class="ix">/economics</div><h3>Edge-Native Economics</h3><p>Turning unpredictable, metered AI spend into fixed, predictable cost for the industrial edge.</p><div class="spec"><span class="chip">whitepaper</span></div></a></div></div></section>',
 "edge-security-intelligence": '<section><div class="wrap">' + shead("03","Further reading","For your security team","Read in the browser or export to PDF.")
   + '<div class="disc"><a class="dcard rv" href="../ai-soc-modernization-whitepaper.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><div class="ix">/ai-soc</div><h3>AI SOC Modernization</h3><p>An edge-native, identity-driven security architecture for distributed IT/OT.</p><div class="spec"><span class="chip">whitepaper</span></div></a></div></div></section>',
 "gpu-microcloud": sec("03","By design","The rack, in numbers", metrics([("12","shelves, each its own failure zone"),("4","servers per shelf, linked by fast cables"),("5","shelves share cluster control")])),
}
# ===================== /MOCK =====================

PLATP=[x for x in PLATP if x[0] in ("agentmesh","agentnexus")]
# ===================== MOCK: product page presentation =====================
PCSS = """
/* ---------- product pages ---------- */
.ph2{padding:140px 0 40px}
.ph2 .grid{display:grid;gap:40px;align-items:center}
@media(min-width:980px){.ph2 .grid{grid-template-columns:1.05fr .95fr}}
.ph2 h1{font-size:clamp(46px,7vw,92px);margin:16px 0 0}
.ph2 .lead{margin:22px 0 28px;max-width:52ch}
.ph2 .pill{display:inline-flex;gap:8px;flex-wrap:wrap;margin-top:22px}
.kstrip{display:grid;gap:0;margin-top:46px;border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--surface)}
@media(min-width:720px){.kstrip{grid-template-columns:repeat(4,1fr)}}
.kstrip>div{padding:22px 24px;border-right:1px solid var(--line)}
.kstrip>div:last-child{border-right:0}
.kstrip .v{font-family:var(--disp);font-weight:800;font-size:clamp(26px,3vw,38px);letter-spacing:-.03em;color:var(--fg)}
.kstrip .v .o{color:var(--accent)}
.kstrip .k{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-dim);margin-top:6px}
.livep{border:1px solid var(--line-2);border-radius:var(--r-lg);background:linear-gradient(160deg,var(--surface-2),var(--ink-2));box-shadow:0 40px 90px -40px rgba(0,0,0,.45);overflow:hidden}
.livep .hd{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;border-bottom:1px solid var(--line)}
.livep .hd .tag{font-size:10.5px}
.livep .wave{height:120px;border-bottom:1px solid var(--line);background:repeating-linear-gradient(90deg,transparent,transparent 31px,rgba(128,128,160,.07) 31px,rgba(128,128,160,.07) 32px)}
.livep .wave svg{width:100%;height:100%;display:block}
.livep .rows{padding:6px 18px 14px}
.livep .r{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px dashed var(--line);font-size:14px}
.livep .r:last-child{border-bottom:0}
.livep .r .k{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--fg-dim)}
.livep .r .v{color:var(--fg);font-weight:600;text-align:right}
.livep .r .v.a{color:var(--accent)} .livep .r .v.s{color:var(--steel)}
.livep .ft{padding:10px 18px;font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-dim);border-top:1px solid var(--line)}
.flow4{display:grid;gap:14px;margin-top:34px;counter-reset:f}
@media(min-width:860px){.flow4{grid-template-columns:repeat(4,1fr)}}
.flow4 .st{position:relative;border:1px solid var(--line);border-radius:var(--r-lg);padding:26px 22px 22px;background:var(--surface)}
.flow4 .st .n{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;font-family:var(--mono);font-size:13px;font-weight:700;color:var(--accent-ink);background:var(--accent);margin-bottom:16px}
.flow4 .st:nth-child(even) .n{background:var(--steel);color:#fff}
.flow4 .st h3{font-size:21px;margin:0 0 8px}
.flow4 .st p{font-size:15px;margin:0}
.flow4 .st .who{margin-top:14px;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--fg-dim)}
@media(min-width:860px){.flow4 .st:not(:last-child)::after{content:"→";position:absolute;right:-13px;top:44px;color:var(--fg-dim);font-size:18px;z-index:2;background:var(--ink);padding:0 2px}}
.lanes{display:grid;gap:18px;margin-top:34px}
@media(min-width:860px){.lanes{grid-template-columns:1fr 1fr}}
.lane{border-radius:var(--r-lg);padding:30px;border:1px solid var(--line-2);background:var(--surface)}
.lane.a{border-color:color-mix(in srgb,var(--accent) 55%,var(--line-2));background:linear-gradient(180deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface))}
.lane.b{border-color:color-mix(in srgb,var(--steel) 55%,var(--line-2));background:linear-gradient(180deg,color-mix(in srgb,var(--steel) 9%,var(--surface)),var(--surface))}
.lane .big{font-family:var(--disp);font-weight:800;font-size:clamp(30px,3.6vw,44px);letter-spacing:-.03em;margin:6px 0 4px}
.lane.a .big{color:var(--accent)} .lane.b .big{color:var(--steel)}
.lane ul{margin:16px 0 0;padding:0;list-style:none}
.lane li{padding:10px 0;border-top:1px solid var(--line);font-size:15.5px;color:var(--fg-mut);display:flex;gap:10px}
.lane li b{color:var(--fg);font-weight:600;min-width:118px}
.never{margin-top:18px;border:1px dashed var(--line-2);border-radius:var(--r);padding:16px 20px;font-size:15px;color:var(--fg-mut)}
.never b{color:var(--fg)}
.kits{display:grid;gap:12px;margin-top:34px}
@media(min-width:640px){.kits{grid-template-columns:1fr 1fr}}
@media(min-width:980px){.kits{grid-template-columns:repeat(3,1fr)}}
.kit{border:1px solid var(--line);border-radius:var(--r);padding:20px 22px;background:var(--surface);transition:border-color .25s,transform .25s var(--e)}
.kit:hover{border-color:var(--accent);transform:translateY(-2px)}
.kit .ico{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:color-mix(in srgb,var(--accent) 14%,transparent);color:var(--accent);margin-bottom:12px}
.kit .ico svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:1.8}
.kit h4{margin:0 0 6px;font-family:var(--disp);font-size:18px;color:var(--fg)}
.kit p{margin:0;font-size:14.5px}
.kit .sig{margin-top:12px;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--fg-dim)}
.hwrow{display:grid;gap:16px;margin-top:34px}
@media(min-width:860px){.hwrow{grid-template-columns:repeat(3,1fr)}}
.hw{border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--surface);display:flex;flex-direction:column;text-decoration:none;transition:border-color .25s,transform .25s var(--e)}
.hw:hover{border-color:var(--accent);transform:translateY(-3px)}
.hw .im{background:var(--surface-2);border-bottom:1px solid var(--line);padding:18px;display:grid;place-items:center}
.hw .im img{width:100%;max-width:300px;height:auto;display:block}
.hw .bd{padding:20px 22px 22px}
.hw .st{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;padding:3px 9px;border-radius:999px;border:1px solid var(--line-2);color:var(--fg-mut)}
.hw .st.now{border-color:var(--accent);color:var(--accent)}
.hw h4{margin:12px 0 6px;font-family:var(--disp);font-size:19px;color:var(--fg)}
.hw p{margin:0;font-size:15px}
.layers{display:grid;gap:10px;margin-top:34px}
.layer{display:grid;gap:14px;align-items:center;border:1px solid var(--line);border-radius:var(--r-lg);padding:22px 26px;background:var(--surface)}
@media(min-width:860px){.layer{grid-template-columns:220px 1fr 260px}}
.layer .nm{font-family:var(--disp);font-weight:800;font-size:22px;color:var(--fg)}
.layer .nm small{display:block;font-family:var(--mono);font-weight:500;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-dim);margin-bottom:4px}
.layer p{margin:0;font-size:15.5px}
.layer .chips{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-start}
.layer:nth-child(1){border-left:4px solid var(--steel)} .layer:nth-child(2){border-left:4px solid var(--accent)}
.layer:nth-child(3){border-left:4px solid var(--violet)} .layer:nth-child(4){border-left:4px solid var(--fg-dim)}
.loopwrap{display:grid;gap:30px;align-items:center;margin-top:30px}
@media(min-width:900px){.loopwrap{grid-template-columns:1fr 1fr}}
.loopviz{width:100%;max-width:460px;height:auto;display:block;margin:0 auto}
.loopviz .ring{fill:none;stroke:var(--line-2);stroke-width:2;stroke-dasharray:6 8;animation:kgflow 3s linear infinite}
.loopviz .nd{fill:var(--surface);stroke:var(--accent);stroke-width:2}
.loopviz .nd.s{stroke:var(--steel)}
.loopviz .t{fill:var(--fg);font-family:var(--disp);font-weight:700;font-size:16px;text-anchor:middle}
.loopviz .s{fill:var(--fg-mut);font-family:var(--body);font-size:12px;text-anchor:middle}
.loopviz .c{fill:var(--fg);font-family:var(--disp);font-weight:800;font-size:22px;text-anchor:middle}
.gate{display:grid;gap:10px}
.gate div{border:1px solid var(--line);border-radius:var(--r);padding:14px 18px;background:var(--surface);font-size:15px;color:var(--fg-mut)}
.gate b{color:var(--fg)}
.pairs{display:grid;gap:24px;align-items:center;border:1px solid var(--line-2);border-radius:var(--r-lg);padding:34px;background:linear-gradient(135deg,var(--surface-2),var(--surface))}
@media(min-width:860px){.pairs{grid-template-columns:1fr auto}}
.pairs h3{margin:0 0 8px;font-size:clamp(24px,2.6vw,32px)}
.pairs p{margin:0;max-width:62ch}
.glance{width:100%;border-collapse:separate;border-spacing:0;margin-top:22px;border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--surface)}
.glance th,.glance td{padding:15px 20px;text-align:left;border-bottom:1px solid var(--line);font-size:15px;vertical-align:top}
.glance tr:last-child td{border-bottom:0}
.glance th{font-family:var(--disp);font-size:18px;color:var(--fg)}
.glance th.m{color:var(--accent)} .glance th.n{color:var(--steel)}
.glance td:first-child{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--fg-dim);width:22%}
.glance td{color:var(--fg-mut)}
.illus{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-dim)}
"""

ICO={
 "rot":'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 4v3M12 17v3M4 12h3M17 12h3"/></svg>',
 "bat":'<svg viewBox="0 0 24 24"><rect x="3" y="7" width="16" height="10" rx="2"/><path d="M21 10v4M7 10v4M11 10v4"/></svg>',
 "ele":'<svg viewBox="0 0 24 24"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
 "leak":'<svg viewBox="0 0 24 24"><path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/></svg>',
 "test":'<svg viewBox="0 0 24 24"><path d="M3 17l5-6 4 4 4-7 5 9"/><path d="M3 21h18"/></svg>',
 "ot":'<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><path d="M7 7h.01M7 17h.01"/></svg>',
}
ICO.setdefault("eye",'<svg viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>')


def kpistrip(items):
    return '<div class="kstrip rv">'+"".join(f'<div><div class="v">{v}</div><div class="k">{k}</div></div>' for v,k in items)+'</div>'
def flow4(items):
    return '<div class="flow4">'+"".join(f'<div class="st rv"><div class="n">{i+1:02d}</div><h3>{t}</h3><p>{d}</p><div class="who">{w}</div></div>' for i,(t,d,w) in enumerate(items))+'</div>'
def kits(items):
    return '<div class="kits">'+"".join(f'<div class="kit rv"><div class="ico">{ICO[i]}</div><h4>{t}</h4><p>{d}</p><div class="sig">{s}</div></div>' for i,t,d,s in items)+'</div>'
def hwrow(items, base="../"):
    out=[]
    for img,anchor,st,now,t,d in items:
        out.append(f'<a class="hw rv" href="{base}device-platform.html#{anchor}" data-cursor><div class="im"><img src="{base}assets/images/{img}{'' if img.endswith(('.jpg','.png')) else ('.jpg' if img.startswith('sketch/') else '.png')}" alt="{t}" loading="lazy"></div><div class="bd"><span class="st{" now" if now else ""}">{st}</span><h4>{t}</h4><p>{d}</p></div></a>')
    return '<div class="hwrow">'+"".join(out)+'</div>'
def layers(items):
    return '<div class="layers">'+"".join(f'<div class="layer rv"><div class="nm"><small>{k}</small>{n}</div><p>{d}</p><div class="chips">{"".join(f"<span class=chip>{c}</span>" for c in ch)}</div></div>' for k,n,d,ch in items)+'</div>'
def wave_svg(burst=True):
    pts="M0,60 "+" ".join(f"L{x},{60+((-1)**(x//20))*(8 if not (burst and 380<x<470) else 34)}" for x in range(0,801,10))
    return f'<svg viewBox="0 0 800 120" preserveAspectRatio="none"><path d="{pts}" fill="none" stroke="var(--accent)" stroke-width="2"/><path d="{pts}" fill="none" stroke="var(--accent)" stroke-width="7" opacity=".12"/></svg>'
def livepanel(title, tag, rows, foot, wave=True):
    r="".join(f'<div class="r"><span class="k">{k}</span><span class="v {c}">{v}</span></div>' for k,v,c in rows)
    w=f'<div class="wave">{wave_svg()}</div>' if wave else ''
    return f'<div class="livep rv"><div class="hd"><span class="tag" style="color:var(--fg-mut)">{title}</span><span class="tag" style="color:var(--steel)">{tag}</span></div>{w}<div class="rows">{r}</div><div class="ft">{foot}</div></div>'
def loop_svg():
    import math
    nodes=[("Learn","outcomes become data",-90,""),("Train","new skill adapter",0,"s"),("Test","cases never seen",90,""),("Trial","slice of live traffic",180,"s")]
    p=['<svg class="loopviz" viewBox="0 0 460 460" role="img" aria-label="The Kiln learning loop: learn from outcomes, train a new skill adapter, test it on unseen cases, trial it on live traffic, and switch it on only if it is better.">',
       '<circle class="ring" cx="230" cy="230" r="150"/>','<text x="230" y="224" class="c">Kiln</text><text x="230" y="248" class="s">switch on only if better</text>']
    for t,s,a,c in nodes:
        x=230+150*math.cos(math.radians(a)); y=230+150*math.sin(math.radians(a))
        p.append(f'<circle class="nd {"ns" if c else ""}" cx="{x:.0f}" cy="{y:.0f}" r="58"/><text x="{x:.0f}" y="{y-2:.0f}" class="t">{t}</text><text x="{x:.0f}" y="{y+18:.0f}" class="s">{s}</text>')
    p.append('</svg>'); return "".join(p)


# ===================== diagrams v2 (AgentMesh signal-to-action, AgentNexus fleet, Kiln loop) =====================
import math as _m, random as _rnd

def _flow(d, cls="fl-a", dur=2.4, begin=0.0, rev=False, r=3.2):
    kp = ' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if rev else ''
    return f'<circle r="{r}" cx="-50" class="{cls}"><animateMotion dur="{dur}s" begin="-{begin:.2f}s" repeatCount="indefinite"{kp} path="{d}"/></circle>'

def _svg_mesh_v2():
    o = ['<svg class="axviz ax2" viewBox="0 0 1000 500" role="img" aria-label="AgentMesh signal to action: robot, vision, vibration, electrical, battery and test-rig signals stream into the Sovereign Pod, which perceives, decides and acts inside a 30 millisecond budget — Lane A acts directly on low-consequence outputs, Lane B raises an alarm and a request the safety PLC, cell controller and operator decide — then reasons after the event, drafting records, and adapts nightly through the Kiln. Every decision goes to the signed Evidence Log.">',
         '<defs><marker id="axh3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>',
         '<text x="20" y="24" class="l">SIGNALS</text><text x="300" y="24" class="l">SOVEREIGN POD · FACTORY NETWORK</text><text x="780" y="24" class="l">OUTCOMES</text>']
    sig = [("Robot joints", "current · torque"), ("Vision", "DeepVision at the cell"), ("Vibration", "ultrasonic · bearings"),
           ("Electrical", "power quality · drives"), ("Battery", "weld · formation · off-gas"), ("Test rigs", "pressure · strain")]
    _rnd.seed(7)
    for n, (a, b) in enumerate(sig):
        y = 40 + n * 66
        o.append(f'<rect x="20" y="{y}" width="230" height="56" rx="9" class="bx"/><text x="32" y="{y+22}" class="t2">{a}</text><text x="32" y="{y+40}" class="s2">{b}</text>')
        pts = " ".join(f"{150+i*6.6:.1f},{y+17+_rnd.uniform(-6,6) if i%3 else y+17:.1f}" for i in range(15))
        o.append(f'<polyline points="{pts}" class="spark" style="animation-delay:-{n*0.35:.2f}s"/>')
        d = f"M250,{y+28} C278,{y+28} 274,{150 if n<3 else 190} 300,{150 if n<3 else 190}"
        o.append(f'<path d="{d}" class="lk-c"/>')
        o.append(_flow(d, "fl-a", 1.6, n*0.27, r=2.6))
    # pod frame
    o.append('<rect x="300" y="40" width="390" height="390" rx="12" class="bx-a"/>')
    # latency budget bar
    o.append('<text x="316" y="64" class="l2">DECIDE BUDGET · TARGET &lt; 30 MS</text>')
    o.append('<rect x="316" y="72" width="358" height="12" rx="6" class="bx"/><rect x="316" y="72" width="358" height="12" rx="6" class="budget"/>')
    o.append('<line x1="644" y1="66" x2="644" y2="90" class="tick"/><text x="640" y="100" class="xs" text-anchor="end">30 MS</text>')
    stages = [("1 · Perceive", "Unovie Gateway reads · Signal Encoders fingerprint"),
              ("2 · Decide", "Vector Memory + Decision Engine pick a lane"),
              ("3 · Act or ask", "Lane A acts · Lane B alarms and requests"),
              ("4 · Reason", "Reasoning Model names the cause, drafts the record"),
              ("5 · Adapt", "Kiln: nightly, tested on unseen cases, signed")]
    for n, (a, b) in enumerate(stages):
        y = 112 + n * 62
        cls = "bx ly" if n < 3 else "bx ly slow"
        o.append(f'<rect x="316" y="{y}" width="300" height="50" rx="8" class="{cls}"/><text x="330" y="{y+21}" class="t2">{a}</text><text x="330" y="{y+38}" class="s2">{b}</text>')
        if n < 4:
            o.append(f'<path d="M466,{y+50} V{y+62}" class="lk-o" marker-end="url(#axh3)"/>')
    # loop brackets
    o.append('<path d="M626,112 h10 v174 h-10" class="brk"/><text x="652" y="204" class="l2 vert" transform="rotate(90 652 204)" text-anchor="middle">FAST LOOP</text>')
    o.append('<path d="M626,298 h10 v112 h-10" class="brk dim"/><text x="652" y="354" class="l2 vert" transform="rotate(90 652 354)" text-anchor="middle">AFTER THE EVENT</text>')
    # outcomes
    outs = [("Lane A · acts directly", "reject gate · divert to rework", 40, "oa"), ("Lane B · alarm + request", "safety PLC · cell controller · operator decide", 140, "ob"),
            ("Drafted records", "NCRs · work orders → MES · QMS", 240, ""), ("Evidence Log", "signed record of every decision", 340, "")]
    srcy = [237, 237, 323, 0]
    for k, (a, b, y, c) in enumerate(outs):
        o.append(f'<rect x="780" y="{y}" width="200" height="74" rx="10" class="bx {c}"/><text x="794" y="{y+28}" class="t2">{a}</text><text x="794" y="{y+47}" class="s2">{b.split(" · ")[0] if len(b)>34 else b}</text>')
        if len(b) > 34:
            o.append(f'<text x="794" y="{y+63}" class="s2">{" · ".join(b.split(" · ")[1:])}</text>')
    paths = [("M616,237 C700,237 700,77 778,77", "fl-g"), ("M616,237 C700,237 700,177 778,177", "fl-o"), ("M616,323 C700,323 700,277 778,277", "fl-a")]
    for d, c in paths:
        o.append(f'<path d="{d}" class="lk-o" marker-end="url(#axh3)"/>')
        o.append(_flow(d, c, 1.8, 0.4 if c == "fl-o" else 0))
    o.append('<path d="M690,410 C730,410 740,377 778,377" class="lk-c" marker-end="url(#axh3)"/>')
    o.append(_flow("M690,410 C730,410 740,377 778,377", "fl-s", 2.6))
    o.append('<rect x="20" y="452" width="960" height="30" rx="15" class="bx-d"/><text x="500" y="471" class="l" text-anchor="middle">THE LANGUAGE MODEL IS NEVER ON THE PATH THAT MOVES EQUIPMENT · EVERY DECISION IS SIGNED</text>')
    o.append('</svg>')
    return "".join(o)

def _svg_nexus_v2():
    o = ['<svg class="axviz ax2" viewBox="0 0 1000 470" role="img" aria-label="AgentNexus: AgentMesh pods at cell lines, fab bays, test stands, shipyards and storage fleets send findings over encrypted links to one 42U rack of twelve shelves with four servers each. Thousands of agents sleep in sealed sandboxes and wake on demand; the Model Router, Reasoning Model, Vector Memory and Kiln serve them, tested skill updates flow back to the pods, and results go to MES, QMS, work-order systems and people. AgentNexus never moves equipment.">',
         '<defs><marker id="axh4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>',
         '<text x="20" y="24" class="l">SITES · AGENTMESH PODS</text><text x="290" y="24" class="l">AGENTNEXUS · ONE RACK · YOUR ENCLAVE</text><text x="790" y="24" class="l">BUSINESS</text>']
    sites = [("Cell Line 2", "battery"), ("Fab Bay 3", "chip fab"), ("Test Stand 2", "space"), ("Yard 1", "shipyard"), ("Storage fleet", "14 sites")]
    for n, (a, b) in enumerate(sites):
        y = 40 + n * 74
        o.append(f'<rect x="20" y="{y}" width="200" height="58" rx="9" class="bx"/><text x="34" y="{y+24}" class="t2">{a}</text><text x="34" y="{y+42}" class="s2">{b} · fast local loop</text><circle cx="206" cy="{y+14}" r="2.6" class="led" style="animation-delay:{n*.3}s"/>')
        d = f"M220,{y+29} C255,{y+29} 260,{150+n*40} 290,{150+n*40}"
        o.append(f'<path d="{d}" class="lk-c"/>')
        o.append(_flow(d, "fl-a", 2.2, n*0.45))
        o.append(_flow(d, "fl-s", 3.0, 1.0+n*0.5, rev=True, r=2.8))
    o.append('<text x="20" y="430" class="s2">… and every other site, over encrypted links</text>')
    # rack
    o.append('<rect x="290" y="40" width="470" height="380" rx="12" class="bx-a"/>')
    o.append('<rect x="306" y="56" width="132" height="348" rx="6" class="rack"/>')
    for sh in range(12):
        y = 66 + sh * 27.5
        o.append(f'<rect x="314" y="{y:.1f}" width="116" height="21" rx="3" class="shelf"/>')
        for k in range(4):
            o.append(f'<rect x="{319+k*28}" y="{y+4:.1f}" width="22" height="13" rx="2" class="srv"/><circle cx="{337+k*28}" cy="{y+8:.1f}" r="1.6" class="led tw" style="animation-delay:{((sh*4+k)*0.137)%2:.2f}s"/>')
    o.append('<text x="372" y="414" class="xs" text-anchor="middle">12 SHELVES × 4 · 42U</text>')
    # agent field
    o.append('<text x="456" y="66" class="l2">AGENTS · SEALED SANDBOXES</text>')
    _rnd.seed(3)
    for r in range(6):
        for c in range(22):
            awake = _rnd.random() < 0.14
            o.append(f'<circle cx="{460+c*12.6:.1f}" cy="{80+r*12}" r="3.2" class="ag {"aw" if awake else ""}" style="animation-delay:-{_rnd.uniform(0,4):.2f}s"/>')
    o.append('<text x="456" y="160" class="s2">most asleep · any agent wakes in &lt; 0.5 s (target)</text>')
    layers = [("Model Router", "picks the model and skill adapter"), ("Reasoning Model", "compares sites, drafts records and plans"),
              ("Vector Memory", "cross-site patterns and history"), ("Kiln", "trains skill adapters · tested before release")]
    for n, (a, b) in enumerate(layers):
        y = 174 + n * 54
        o.append(f'<rect x="456" y="{y}" width="290" height="46" rx="8" class="bx ly"/><text x="470" y="{y+20}" class="t2">{a}</text><text x="470" y="{y+37}" class="s2">{b}</text>')
    o.append('<text x="460" y="404" class="l2">MESH ARBITER · DATA COPIED ACROSS SHELVES</text>')
    outs = [("MES · QMS", "quality records · NCRs", 40, ""), ("Work orders", "SAP · Maximo · planning", 130, ""), ("People", "engineers · operators", 220, ""), ("Never moves", "equipment — advisory only", 330, "dash")]
    for a, b, y, c in outs:
        cls = "bx-d" if c else "bx"
        o.append(f'<rect x="790" y="{y}" width="190" height="64" rx="10" class="{cls}"/><text x="804" y="{y+27}" class="t2">{a}</text><text x="804" y="{y+45}" class="s2">{b}</text>')
        if not c:
            d = f"M760,230 C778,230 772,{y+32} 788,{y+32}"
            o.append(f'<path d="{d}" class="lk-o" marker-end="url(#axh4)"/>')
            o.append(_flow(d, "fl-a", 2.0, (y/90)*0.5))
    o.append('<rect x="20" y="440" width="960" height="24" rx="12" class="bx-d"/><text x="500" y="456" class="l" text-anchor="middle">SECURE BY DESIGN · CNCF-CONFORMANT · MICROSERVICES NATIVE · RUNS AIR-GAPPED IN YOUR ENCLAVE</text>')
    o.append('</svg>')
    return "".join(o)

def loop_svg():
    st = [("Learn", "outcomes become data", -90), ("Train", "new skill adapter", -18), ("Test", "beat it on unseen cases", 54), ("Trial", "slice of live traffic", 126), ("Switch on", "fleet-wide, rollback ready", 198)]
    cx, cy, R = 240, 240, 160
    o = ['<svg class="loopviz ax2" viewBox="0 0 480 480" role="img" aria-label="The Kiln learning loop: learn from outcomes, train a new skill adapter, test it on cases it has never seen, trial it on a slice of live traffic, then switch it on fleet-wide with a one-step rollback. The base model stays the same.">',
         '<defs><marker id="axh5" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>',
         f'<circle cx="{cx}" cy="{cy}" r="{R}" class="ring2"/>']
    for k in range(5):
        a0 = _m.radians(-90 + k*72 + 20); a1 = _m.radians(-90 + k*72 + 52)
        x0, y0 = cx + R*_m.cos(a0), cy + R*_m.sin(a0); x1, y1 = cx + R*_m.cos(a1), cy + R*_m.sin(a1)
        o.append(f'<path d="M{x0:.1f},{y0:.1f} A{R},{R} 0 0 1 {x1:.1f},{y1:.1f}" class="arc" marker-end="url(#axh5)"/>')
    ring = f"M{cx},{cy-R} A{R},{R} 0 1 1 {cx-0.01},{cy-R}"
    o.append(_flow(ring, "fl-a", 7.5, 0, r=5))
    o.append(f'<circle cx="{cx}" cy="{cy}" r="74" class="core"/><text x="{cx}" y="{cy-8}" class="kc" text-anchor="middle">Kiln</text>'
             f'<text x="{cx}" y="{cy+14}" class="s2" text-anchor="middle">base model unchanged</text><text x="{cx}" y="{cy+30}" class="s2" text-anchor="middle">one-step rollback</text>')
    for n, (a, b, deg) in enumerate(st):
        x = cx + R*_m.cos(_m.radians(deg)); y = cy + R*_m.sin(_m.radians(deg))
        w = 150
        cls = "bx ly gate" if a == "Test" else ("bx ly on" if a == "Switch on" else "bx ly")
        o.append(f'<rect x="{x-w/2:.1f}" y="{y-24:.1f}" width="{w}" height="48" rx="24" class="{cls}"/><text x="{x:.1f}" y="{y-3:.1f}" class="t2" text-anchor="middle">{n+1} · {a}</text><text x="{x:.1f}" y="{y+14:.1f}" class="s2" text-anchor="middle">{b}</text>')
    o.append('</svg>')
    return "".join(o)

SVG_MESH = _svg_mesh_v2()
SVG_NEXUS = _svg_nexus_v2()
# =================== /diagrams v2 ===================

def product_page(slug, cat, title_html, lead, pills, kpis, panel, sections, cta_lead, desc):
    head=HEAD("../", f"{re.sub('<[^>]+>','',title_html)} — Unovie.AI", desc)
    chips="".join(f'<span class="chip">{c}</span>' for c in pills)
    body=f'''{NGBG}{NAV("../")}
<section class="ph2"><div class="wrap">
  <div class="crumb rv"><a href="../index.html">Home</a><span class="sep">/</span><a href="../index.html#platform">Platform</a><span class="sep">/</span><span style="color:var(--fg-mut)">{re.sub('<[^>]+>','',title_html)}</span></div>
  <div class="grid">
    <div><div class="tag rv">{cat}</div><h1 class="rv">{title_html}</h1><p class="lead rv">{lead}</p>
      <div class="cta rv"><a class="btn btn-acc" href="../index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a><a class="btn btn-gh" href="#how" data-cursor>See how it works</a></div>
      <div class="pill rv">{chips}</div></div>
    <div>{panel}</div>
  </div>
  {kpistrip(kpis)}
</div></section>
{sections}
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Let's build</div>
  <h2 style="margin-top:16px">{cta_lead}</h2>
  <p class="lead">Turnkey Edge-AI — fixed time, fixed cost, full responsibility.</p>
  <div class="cta"><a class="btn btn-acc" href="/contact.html" data-m="moc.eivonu|snoitulos" data-subject="Project enquiry" data-cursor>Talk to our engineers <span class="ar">→</span></a>
    <a class="btn btn-gh" href="../index.html#accelerators" data-cursor>See industrial solutions</a></div>
</div></div></section>
{FOOTER("../")}'''
    os.makedirs(f"{ROOT}/platform",exist_ok=True)
    open(f"{ROOT}/platform/{slug}.html","w",encoding="utf-8").write(head+body)

def S(num,label,title,body,lead="",id_=""):
    i=f' id="{id_}"' if id_ else ''
    return f'<section{i}><div class="wrap">{shead(num,label,title,lead)}{body}</div></section>'

A_="<span class='serif' style='color:var(--accent)'>"; T_="<span class='serif' style='color:var(--steel)'>"; E_="</span>"


def hmi_showcase(screens, lead):
    tabs="".join(f'<button class="tab{" active" if k==0 else ""}" data-tab="{sid}" role="tab" aria-selected="{"true" if k==0 else "false"}" data-cursor>{label}</button>' for k,(sid,label,img,cap) in enumerate(screens)) if len(screens)>1 else ""
    panels="".join(f'<div class="tpanel{" active" if k==0 else ""}" id="{sid}" role="tabpanel"><figure class="hmiframe"><div class="bezel"><a href="../assets/images/sketch/{img}.jpg" target="_blank" rel="noopener" title="Open full size"><img src="../assets/images/sketch/{img}.jpg" alt="Illustration: {cap}" loading="lazy" width="2400" height="1350"></a></div><div class="stand"></div><figcaption>{cap} · illustration · targets, not measured · click to enlarge</figcaption></figure></div>' for k,(sid,label,img,cap) in enumerate(screens))
    t=f'<div class="tabs hmitabs" role="tablist" aria-label="Operator HMI">{tabs}</div>' if tabs else ''
    return f'<p class="lead rv" style="margin-top:-6px">{lead}</p>{t}{panels}'
MESH_HMI = S("01","Operator HMI","What operators "+A_+"see."+E_, hmi_showcase([
   ("hmi-battery","Battery line · laser weld","portal-battery","Cell Line 2 · module laser weld 5 & formation rack F-12 · Lane A rework divert"),
   ("hmi-fab","Fab utilities · dry pump","portal-fab","Fab utilities · sub-fab bay 3 · dry pump VP-3-14 · Lane B request"),
   ("hmi-test","Test stand · hot-fire run","portal-test","Engine test stand 2 · hot-fire run 117 · advisory to the test conductor"),
   ("hmi-line","Robotic assembly · weld cell","portal-assembly","Precision assembly line B · weld cell 3 & spindle 04 · Lane A reject")],
   "Every AgentMesh pod comes with an operator screen: live asset signals, the decision and its lane, similar past events, the drafted work order and the nightly Kiln evidence pack — on one page."), id_="hmi")
NEXUS_HMI = S("01","Fleet HMI","The fleet, "+T_+"on one screen."+E_, hmi_showcase([
   ("hmi-fleet","Fleet operations","portal-fleet","AgentNexus fleet operations · findings, agents, routing, plans and adapter rollout")],
   "Findings from every AgentMesh pod, cross-site patterns, the agents at work, how requests are routed, the plans waiting for sign-off and the skill adapters being trialled."), id_="hmi")


MESH_NEXTGEN = S("02","Built in","Built into "+A_+"next-generation lines."+E_,
  disc([
   ("/robots","Robot cells and motion","AgentMesh reads robot controllers, servo drives and motion axes — joint current, torque, vibration and cycle data — and spots a drifting joint or gearbox before it scraps parts or stops the line.",["robot controllers","joint torque","cycle data"]),
   ("/vision","Vision and sensor fusion","DeepVision on NVIDIA Jetson AGX Thor at the cell, fused with electrical, acoustic, thermal and force signals. A defect is judged on everything the cell knows, not on one camera frame.",["DeepVision","sensor fusion","at the tool"]),
   ("/mes","Into MES, quality and test systems","Findings land where engineers already work: MES and quality systems, test-data systems, the cell controller and the work-order system. Records arrive drafted, with the evidence attached.",["MES · QMS","test data","work orders"]),
   ("/ramp","From first line to gigafactory","Baselines are learned during ramp-up, in weeks. The same pod, playbooks and skill adapters copy to every new line and site — and AgentMesh also works with the control systems you already have.",["ramp-up","copies to new lines","existing systems too"])])
  + flow4([("Connect","Robot controllers, vision, sensors, test rigs and the factory network, through the Unovie Gateway with allow-listed protocols.","Unovie Gateway"),
           ("Learn the ramp","Baselines from your own first production: what good and bad look like on each cell and asset.","Vector Memory"),
           ("Add intelligence","Agents watch, decide, explain and draft the work — inside the safety lanes.","Decision Engine · Reasoning Model"),
           ("Hand off","Diverts, alarms, requests and drafted records flow into MES, quality and work-order systems.","cell controller · MES · QMS")]),
  "Next-generation factories are built dense with sensors, cameras and robots, and produce far more data than people can watch. AgentMesh is built into them from day one, so every signal has something watching it.")

MESH_SECTIONS = (
  S("03","How it works","From signal to action, "+A_+"at the machine."+E_,
    f'<div class="axwrap rv">{SVG_MESH}</div>'
    + flow4([("Perceive","The Unovie Gateway reads sensors and network traffic read-only. Signal Encoders turn each window into a fingerprint.","Unovie Gateway · Signal Encoders"),
             ("Decide","Vector Memory checks what this looks like from history; the Unovie Decision Engine applies your rules and picks a lane.","Vector Memory · Decision Engine"),
             ("Reason","After the event, the Unovie Reasoning Model names the likely root cause and drafts the work order.","Unovie Reasoning Model"),
             ("Adapt","Each night the Kiln proposes small playbook changes and keeps them only if a held-out test improves.","Kiln · Evidence Log")]),
    "A Sovereign Pod on the factory network keeps the fast loop local. It reads, decides and records — and leaves control where it belongs.", "how")
  + S("04","The safety boundary","Two lanes. "+A_+"Your control system stays in charge."+E_,
    '<div class="lanes">'
    '<div class="lane a rv"><div class="tag" style="color:var(--accent)">Lane A</div><div class="big">Acts directly</div><p>Only for outputs where a wrong call costs little and is easy to undo.</p><ul><li><b>Reject gate</b>a part with a bad weld signature goes to the reject bin</li><li><b>Diverter</b>product is routed to rework instead of shipping</li><li><b>IT quarantine</b>a suspicious device is isolated on the IT side</li></ul></div>'
    '<div class="lane b rv"><div class="tag" style="color:var(--steel)">Lane B</div><div class="big">Alarm + request</div><p>Anything that touches process safety. AgentMesh asks; people and safety systems decide.</p><ul><li><b>Alarm</b>raised on your existing alarm system</li><li><b>Request</b>written to a register your PLC or safety system reads</li><li><b>Operator</b>sees the request and the evidence, and decides</li></ul></div>'
    '</div><div class="never rv"><b>Never:</b> AgentMesh does not write to valves or safety functions on its own, and the language model is never in the path that moves equipment. Every decision — in either lane — is written to the signed Evidence Log.</div>')
  + S("05","Deep-tech sites","Built for the factories "+A_+"being built now."+E_,
    disc([
     ("/battery","Battery &amp; energy storage","Cell, module and pack lines: weld, formation and aging signals watched in line, with suspect parts diverted to rework. On storage fleets, early signs of thermal runaway go to the fire panel as an alarm.",["Battery Line &amp; Storage Safety","in-line QA","alarm only on fleets"]),
     ("/fab","Chip fabs &amp; suppliers","Pumps, chillers, scrubbers, ultra-pure water and gas systems watched through ramp-up and steady state, at the fab and at its gas, chemical and parts suppliers. Process and design data never leave the fence.",["fab utilities","supplier plants","IP stays on site"]),
     ("/space","Space &amp; aerospace","Lander, satellite and vehicle lines with vision QA and drafted quality records; rocket and engine test stands watched run by run, beside the qualified test system — never inside it.",["Test Campaign Monitor","quality records","advisory"]),
     ("/robotics","Robotics &amp; autonomous systems","Robot-dense lines and the robots, drones and vessels they build: joint, motor and gearbox health at every cell, and fleet health for systems that run disconnected and sync when they return.",["Robot &amp; Motion Health","DeepVision","works offline"]),
     ("/defense","Defense &amp; dual-use manufacturing","New shipyards, autonomous-vessel yards and dual-use factories: line and yard QA, machinery health and factory network watch, inside the security boundary you already maintain.",["shipyards","autonomous vessels","your enclave"]),
     ("/energy","Advanced energy &amp; nuclear","Construction, balance-of-plant and site-security monitoring on new reactor and power sites, with condition reports drafted for review. Never on reactor protection or safety-related systems.",["balance of plant","condition reports","non-safety only"])]),
    "Battery lines, chip fabs, space factories, robot lines and new shipyards share three things: dense sensors and robots, data that can't leave the site, and audits that need evidence. That is the job AgentMesh was built for.", "sectors")
  + S("06","Secure by design","Born with "+A_+"compliance in mind."+E_,
    disc([
     ("/sp800-53","Designed against NIST SP 800-53","Built around SP 800-53 Rev. 5 control families as tailored for OT by the SP 800-82r3 overlay: boundary protection (air-gapped, one-way outputs), least privilege, audit, change control, integrity and supply chain.",["SC · AC · AU","CM · SI · SR","OT overlay"]),
     ("/ai-rmf","Governed by the NIST AI RMF","Govern, Map, Measure, Manage: every kit declares its context and lane, every change is tested on unseen cases, and the language model only drafts — guided by the Generative AI Profile (NIST AI 600-1).",["AI RMF","AI 600-1","human sign-off"]),
     ("/your-frameworks","Evidence for your industry's frameworks","The nightly evidence pack is material for SP 800-171 and CMMC programs, IEC 62443, fab equipment-security reviews, aerospace quality records and battery-site safety reviews. Compliance stays with your assessor; we give them the evidence.",["800-171 · CMMC","IEC 62443","SEMI E187"]),
     ("/data","Data that can't leave, doesn't","Export-controlled, defense and IP-sensitive data stays on hardware you own, inside the security boundary you already maintain. Models improve on site; nothing is shared back to us.",["air-gapped","your enclave","on-site learning"])]),
    "Deep-tech sites can't bolt security on later, so we didn't either. AgentMesh was designed from day one against the frameworks their security and compliance teams already use.", "security")
  + S("07","Cloud-native by design","CNCF-conformant. "+A_+"Microservices native."+E_,
    disc([
     ("/cncf","CNCF-conformant platform","Every Sovereign Pod runs a CNCF Certified Kubernetes distribution, with CNCF projects underneath. Your platform team runs it with the same tools, skills and practices as the rest of your estate — no proprietary appliance OS.",["Certified Kubernetes","CNCF projects","open standards"]),
     ("/microservices","Microservices native","The Unovie Gateway, Signal Encoders, Vector Memory, Decision Engine, Reasoning Model, Evidence Log and Kiln each run as their own containerised service, talking over typed contracts. Each one scales, updates and rolls back on its own.",["containerised services","typed gRPC contracts","independent rollout"]),
     ("/declarative","Declarative and repeatable","Pinned images and declarative manifests: the pod on a new line is the same as the pod on the last one. Playbooks and skill adapters ship as versioned artefacts, signed and reversible.",["pinned images","declarative","versioned"]),
     ("/secure-defaults","Secure defaults, built in","Default-deny network policy for every namespace, secrets encrypted at rest, sandboxed workloads — and failover handled by the Mesh Arbiter in milliseconds, not left to the scheduler.",["default-deny","encrypted secrets","Mesh Arbiter"])]),
    "AgentMesh is built the way modern platform teams already run software — cloud-native, on open standards — and still runs air-gapped at the machine.", "cloud-native")
  + S("08","Domain kits","Packaged for "+A_+"the assets you run."+E_,
    kits([("rot","Robot &amp; Motion Health","Joint, servo, gearbox and spindle health on robots, motion axes and conveyors — with a drafted work order.","joint current · torque · vibration"),
          ("bat","Battery Line &amp; Storage Safety","Weld, formation and aging signatures in line; thermal-runaway precursors on storage fleets, as an alarm.","weld · cycler · off-gas"),
          ("ele","Electrical Health","Drives, tool power, inverters and switchgear: early signs of arcing and insulation failure.","power quality · partial discharge"),
          ("eye","Vision Quality Inspection","DeepVision defect checks on cells, welds, wafers and composite parts, fused with process signals.","vision · thermal · process"),
          ("test","Test Campaign Monitor","Anomaly flags to the test conductor during a run, and a drafted post-test report.","pressure · strain · acoustics"),
          ("ot","Factory Network Watch","Unauthorized writes and unusual commands on the factory network, with evidence for audits.","control traffic · alarms")])
    + '<div class="sensors">'
    + "".join(f'<figure class="rv"><img src="../assets/images/sketch/{f}.jpg" alt="Illustration: {c}" loading="lazy"><figcaption>{c}</figcaption></figure>' for f,c in [("sensors","Vibration + ultrasonic sensors"),("daq","High-speed signal DAQ"),("weld-clamp","Weld-current clamp"),("agx-thor","DeepVision at the cell")])
    + '</div><p class="illus rv" style="margin-top:10px">Generic partner hardware · illustrations</p>',
    "Each kit packages the connections, fingerprints, rules, playbook and reports for one class of asset. A pod can run several.")
  + S("09","Runs on","AMD or NVIDIA. "+A_+"Hardware you own."+E_,
    hwrow([("sketch/sovereign-pod","ryzen-ai-max-395","Runs today",True,"AMD Ryzen AI Max+ 395","The reference Sovereign Pod: four servers in 3U with 2 × 10GbE networking and NVMe storage, quiet enough for a rack on the factory floor."),
           ("sketch/agx-thor","agx-thor","Available on",False,"NVIDIA Jetson AGX Thor","Robotics and DeepVision at the tool — inspection, robot cells and wafer handling in the fab."),
           ("sketch/dgx-spark","dgx-spark","Available on",False,"NVIDIA DGX Spark","The AI engineering lab — test stands, replay and a single-unit AgentMesh for a pilot.")]),
    "Same kits, same lanes, same Evidence Log on every platform.")
  + S("10","Why teams choose it","Built for the factory floor, "+A_+"not the slide."+E_,
    kpistrip([("Yours","hardware, models, playbooks and evidence"),("Air-gapped","by default · nothing leaves site"),("Per asset","priced on failures avoided, not seats"),("Weeks","to a working pod, not quarters")]))
  + '<section><div class="wrap"><div class="pairs rv"><div><div class="tag" style="color:var(--steel)">Pairs with AgentNexus</div><h3>One pod per line or site. '+T_+'One AgentNexus for the fleet.'+E_+'</h3><p>AgentMesh sends what it finds to AgentNexus, where agents compare sites, plan maintenance and learn from what happened — without ever reaching back into factory control.</p></div><a class="btn btn-gh" href="agentnexus.html" data-cursor>Explore AgentNexus <span class="ar">→</span></a></div></div></section>'
)

NEXUS_FLEETS = S("02","Deep-tech fleets","One rack for "+T_+"every site you run."+E_,
  disc([
   ("/battery","Gigafactories and storage fleets","Findings from every cell and module line, and thermal and off-gas findings from mostly unstaffed storage sites, in one view. Agents assemble the quality, inspection and incident records reviewers and insurers ask for.",["line + fleet","quality records","incident records"]),
   ("/build-test","Factories and test stands","A test-stand anomaly is traced back to the production lot that built the part. Agents draft non-conformance reports and quality records for your engineers to sign.",["test → production","NCR drafts","quality records"]),
   ("/fab","Fabs and supplier plants","Utilities findings from the fab and from its gas, chemical and parts-cleaning suppliers in one place, so a failing pump at a supplier is caught before it reaches the fab.",["supplier network","utilities","IP stays on site"]),
   ("/robotics","Robot and autonomous fleets","Robot cells across every line and site, and the robots, drones and vessels you ship: joint and motor health compared across the fleet, with fielded systems syncing findings when they reconnect.",["fleet health","sync on reconnect","DeepVision"]),
   ("/dual-use","Dual-use programs","The same platform for commercial and defense work, including new shipyards and autonomous-vessel yards. AgentNexus runs in your own enclave, on hardware you own, so program data stays inside the boundary you already accredit.",["shipyards","your enclave","dual-use"]),
   ("/energy","New energy sites","Construction progress, balance-of-plant condition reports and work orders across new power and advanced nuclear sites — always advisory, never on safety systems.",["condition reports","advisory","work orders"])]),
  "Deep-tech companies run more than one site: a factory and a test stand, a fab and its suppliers, gigafactory lines and a storage fleet, robot lines and the robots they ship. AgentNexus is where their agents work across all of them — drafting records and work orders in English or Spanish.", "fleets")

NEXUS_SECTIONS = (  S("03","How it works","One rack for "+T_+"a fleet of sites."+E_,
    f'<div class="axwrap rv">{SVG_NEXUS}</div>'
    + flow4([("Event","An AgentMesh pod sends what it found, over an encrypted link.","AgentMesh → AgentNexus"),
             ("Wake","The right agent wakes in its sealed sandbox on any free server.","Unovie Agent Runtime"),
             ("Reason","The Unovie Model Router picks the model and skill adapter; the agent compares sites and history.","Model Router · Reasoning Model"),
             ("Act","Work orders, quality records and reports go to MES, QMS, SAP or Maximo, and to your people.","Business systems")]),
    "AgentMesh keeps the fast loop at each line and site. AgentNexus works at business speed across all of them — and never moves equipment.", "how")
  + S("04","Inside the rack","Four layers, "+T_+"one system."+E_,
    '<figure class="rackfig rv"><img src="../assets/images/sketch/agentnexus-rack.jpg" alt="Illustration of the AgentNexus reference rack: a 42U cabinet with two 10GbE switches, twelve 3U trays of four AMD Ryzen AI Max+ 395 nodes, one tray pulled out, and dual PDUs" loading="lazy"><figcaption>Reference rack · 42U · 12 trays × 4 AMD Ryzen AI Max+ 395 · illustration</figcaption></figure>'
    + layers([("Layer 1","Agents","The Unovie Agent Runtime gives every agent a sealed sandbox. Idle agents sleep and wake on demand, network access is allow-listed, and passwords never reach the agent.",["sandboxed","sleep · wake","allow-listed"]),
            ("Layer 2","Models","The Unovie Model Router and Decision Models pick the model and skill adapter for every request. The Unovie Reasoning Model answers; Vector Memory powers search.",["Model Router","skill adapters","open weights"]),
            ("Layer 3","Learning","The Kiln turns production outcomes into new skill adapters — tested and trialled before they go live.",["Kiln","tested","reversible"]),
            ("Layer 4","Platform","Twelve shelves of four servers run as one system. Data is copied across shelves; the Mesh Arbiter moves work when something stops.",["12 shelves","copied data","Mesh Arbiter"])]))
  + S("05","Gets better from production","Nothing goes live "+T_+"unless it's better."+E_,
    '<div class="loopwrap"><div class="rv">'+loop_svg()+'</div><div class="gate">'
    '<div class="rv"><b>Learn.</b> Agents and operators report outcomes; the router records what was asked and what worked.</div>'
    '<div class="rv"><b>Train.</b> The Kiln trains a small skill adapter for one job on the rack — the base model stays the same.</div>'
    '<div class="rv"><b>Test.</b> The new adapter must beat the current one on cases it has never seen.</div>'
    '<div class="rv"><b>Trial, then switch on.</b> It quietly answers a slice of live traffic first; only then is it switched on everywhere, with a one-step rollback.</div>'
    '</div></div>')
  + S("06","Runs on","AMD or NVIDIA. "+T_+"Hardware you own."+E_,
    hwrow([("sketch/agentnexus-rack","ryzen-ai-max-395","Reference design",True,"AMD Ryzen AI Max+ 395 rack","Twelve shelves of four servers in one 42U rack — the same server as the AgentMesh pod."),
           ("dgx-spark","dgx-spark","Available on",False,"NVIDIA DGX Spark","The AI engineering lab: where new skill adapters are trained, and a small AgentNexus for one site."),
           ("agx-thor","agx-thor","Pairs with",False,"AgentMesh on Jetson AGX Thor","Robotics and DeepVision tools in the fab report to the same AgentNexus.")]))
  + S("07","By design","Sized for a fleet",
    kpistrip([("~860","agents awake at once · estimate"),("1000s","agents in total, mostly asleep"),("4 of 12","shelves can fail without losing saved agents"),("0.5<span class='o'>s</span>","response budget · target")])
    + '<p class="lead rv" style="font-size:15px;margin-top:14px">Estimates from measurements on single servers; we replace them with measured numbers after our bench tests.</p>'
    + '<div class="disc" style="margin-top:22px"><a class="dcard rv" href="../resources/agentnexus-architecture.html" target="_blank" rel="noopener" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><div class="ix">/architecture</div><h3>AgentNexus — Architecture Overview</h3><p>How the rack is organised, what happens step by step, how data is kept safe and what happens when something breaks — for architects and business leaders.</p><div class="spec"><span class="chip">overview</span><span class="chip">diagrams</span></div></a></div>')
  + S("08","Secure by design","Born with "+T_+"compliance in mind."+E_,
    disc([
     ("/sandbox","Least privilege for every agent","Each agent runs in a sealed sandbox with allow-listed network access, and credentials never reach the agent — access control and identification as SP 800-53 describes them.",["AC · IA","sealed sandboxes","allow-listed"]),
     ("/audit","Every action on the record","Agent actions, model routing decisions and drafted records are written to the signed Evidence Log, for audit and non-repudiation.",["AU","signed","exportable"]),
     ("/change","Change control for AI","New skill adapters are trained, tested on unseen cases, trialled and switched on only if better — with one-step rollback. That is AI RMF Measure and Manage, and SP 800-53 change control.",["CM · SI","AI RMF","rollback"]),
     ("/enclave","Inside your enclave","AgentNexus runs on hardware you own, inside the boundary you already accredit — the natural home for CUI and export-controlled programs under SP 800-171 and CMMC.",["your enclave","800-171 · CMMC","dual-use"])]),
    "Designed against NIST SP 800-53 controls and the NIST AI Risk Management Framework from the first line of code — evidence for your assessors, not a certificate from us.", "security")
  + S("09","Cloud-native by design","CNCF-conformant. "+T_+"Microservices native."+E_,
    disc([
     ("/cncf","CNCF-conformant cluster","The 48 servers run as one CNCF Certified Kubernetes cluster, with CNCF graduated and incubating projects for service networking, replicated storage and observability.",["Certified Kubernetes","CNCF projects","one cluster"]),
     ("/microservices","Microservices native","The Agent Runtime, Model Router, Decision Models, Reasoning Model, Vector Memory and Kiln are separate services with typed contracts — each scales, updates and rolls back on its own, across twelve failure zones.",["independent services","typed contracts","12 failure zones"]),
     ("/agents","Agents as sandboxed workloads","Every agent is a sealed, sandboxed workload that sleeps when idle and wakes on any free server — thousands of agents on one rack, scheduled like any other cloud-native workload.",["sandboxed","sleep · wake","scheduled"]),
     ("/ops","Runs like the rest of your estate","Declarative manifests, pinned images, rolling updates and standard observability — operated by your platform team, or by us as a service.",["declarative","rolling updates","observability"])]),
    "AgentNexus is a cloud-native platform on open standards, inside your own enclave.", "cloud-native")
  + '<section><div class="wrap"><div class="pairs rv"><div><div class="tag" style="color:var(--accent)">Starts with AgentMesh</div><h3>The fleet view is only as good as '+A_+'what each line sees.'+E_+'</h3><p>AgentMesh puts AI on the signals at every line, with safety decisions left to your control systems. AgentNexus brings the fleet together.</p></div><a class="btn btn-gh" href="agentmesh.html" data-cursor>Explore AgentMesh <span class="ar">→</span></a></div></div></section>'
)

MESH_PANEL = livepanel("Pump P-101 · bearing 3","AgentMesh",[("Signal","vibration 25.6 kHz",""),("Fingerprint","matches past outer-race wear","a"),("Lane","B · alarm + request sent","s"),("Work order","drafted for planner review",""),("Evidence","signed · logged","")],"Illustration")
NEXUS_PANEL = livepanel("Fleet · this morning","AgentNexus",[("Plant A","AgentMesh event · pump wear","a"),("Plant C","same pattern, two weeks ago","s"),("Agent","maintenance planner · awake",""),("Proposal","align repair with planned outage",""),("To","work order in the maintenance system","")],"Illustration",wave=False)


MESH_PANEL = ('<figure class="portalfig rv"><div class="pimg"><a href="../assets/images/sketch/portal-battery.jpg" target="_blank" rel="noopener" title="Open full size"><img src="../assets/images/sketch/portal-battery.jpg" alt="Illustration of the AgentMesh operator screen for a battery cell line: laser-weld and formation signals, the decision lane, similar past events, a drafted non-conformance report and the nightly Kiln evidence pack" width="2400" height="1350"></a></div>'
  '<figcaption><b>AgentMesh operator screen</b><span>Cell Line 2 · module laser weld · illustration · click to enlarge</span></figcaption></figure>')
NEXUS_PANEL = ('<figure class="portalfig rv"><div class="pimg"><a href="../assets/images/sketch/portal-fleet.jpg" target="_blank" rel="noopener" title="Open full size"><img src="../assets/images/sketch/portal-fleet.jpg" alt="Illustration of the AgentNexus fleet HMI: site findings, cross-site patterns, agents, model routing, a proposed maintenance plan and a skill adapter rollout" width="2400" height="1350"></a></div>'
  '<figcaption><b>AgentNexus fleet HMI</b><span>Fleet operations · illustration · click to enlarge</span></figcaption></figure>')

product_page("agentmesh","Platform · AgentMesh","Agent"+A_+"Mesh"+E_,
  "Agentic Physical AI for next-generation factories — battery lines, chip fabs, space hardware, robotics and autonomous systems. AgentMesh sits on the factory network beside robots, tools and test systems, puts AI on every signal they produce, and decides inside a 30-millisecond budget. Low-consequence actions happen directly; anything safety-related goes to your safety PLC, cell controller and operators.",
  ["sensor-dense","robot cells","DeepVision","CNCF-conformant","microservices","air-gapped"],
  [("&lt;30<span class='o'>ms</span>","decision budget · target"),("0<span class='o'>B</span>","leaves site by default"),("10","domain kits"),("2","safety lanes")],
  MESH_PANEL, MESH_HMI+MESH_NEXTGEN+MESH_SECTIONS, "Put AI on "+A_+"every signal your line makes."+E_,
  "AgentMesh puts Agentic Physical AI into next-generation factories — battery, chips, space, robotics and defense — with a 30 ms decision budget, a clear safety boundary and a signed Evidence Log.")
product_page("agentnexus","Platform · AgentNexus","Agent"+T_+"Nexus"+E_,
  "Agents that work across every site you run — gigafactories and storage fleets, factories and test stands, fabs and their suppliers, robot fleets and shipyards. They compare sites, plan maintenance and draft work orders and quality records within half a second, learn from production, and never move equipment.",
  ["sealed agents","multi-site","CNCF-conformant","microservices","dual-use","AMD · NVIDIA"],
  [("0.5<span class='o'>s</span>","response budget · target"),("48","servers in one 42U rack"),("12","shelves, each its own failure zone"),("0","equipment it controls")],
  NEXUS_PANEL, NEXUS_HMI+NEXUS_FLEETS+NEXUS_SECTIONS, "Run agents "+T_+"across every site."+E_,
  "AgentNexus runs AI agents across every site of a next-generation manufacturer: sealed sandboxes, a model router with skill adapters, and models that improve from production — on AMD or NVIDIA hardware you own.")
# ===================== /MOCK product pages =====================


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
  "A petaFLOP AI supercomputer that fits on a desk. NVIDIA DGX Spark pairs the GB10 Grace Blackwell Superchip with 128 GB of coherent unified memory and up to 1,000 TFLOPS of FP4 compute — enough to prototype, fine-tune and run models up to ~200B parameters locally, or ~405B across a linked pair. We run it as your private development and inference node: the full Unovie stack, your data, your room.",
  [("1,000<span class='o'>TFLOPS</span>","FP4 AI compute"),("128<span class='o'>GB</span>","coherent memory"),("200<span class='o'>B</span>","params, local")],
  ("A supercomputer you own",[("/gb10","Grace Blackwell GB10","A 20-core Arm Grace CPU and a Blackwell GPU joined by NVLink-C2C share one coherent memory space — no PCIe copies between CPU and GPU.",["GB10","NVLink-C2C","coherent"]),
   ("/memory","128 GB for big models","Unified LPDDR5X holds models up to ~200B parameters; two units linked over ConnectX scale to ~405B — inference and fine-tuning without the cloud.",["200B local","405B linked","ConnectX"]),
   ("/stack","The full NVIDIA AI stack","Runs NIM microservices, CUDA frameworks and the same containers as DGX in the datacenter — develop locally, deploy to the edge unchanged.",["NIM","CUDA","portable"])]),
  ("Desk to deployment",[("Build","Prototype &amp; fine-tune locally on Spark."),("Ground","Wire in your Nexus context and data."),("Validate","Run the same containers as production."),("Promote","Ship unchanged to edge or MicroCloud.")]),
  "Your own AI supercomputer, <span class='serif' style='color:var(--accent)'>on your desk.</span>"),
 ("qualcomm-qcs6490","Device · Power-efficient edge","Qualcomm <span class='serif' style='color:var(--accent)'>QCS6490</span>",
  "A power-efficient edge-AI processor for robots, cameras and handhelds. The Qualcomm QCS6490 pairs an octa-core Kryo CPU, an Adreno GPU and a Hexagon AI processor for up to 12 TFLOPS — multi-camera vision and on-device models on a fanless, battery-friendly power budget, with Wi-Fi 6E and long industrial lifecycle support. We bring the Unovie stack to it, so intelligence runs at the far edge, on hardware you own.",
  [("12<span class='o'>TFLOPS</span>","Hexagon AI"),("5","concurrent cameras"),("Wi-Fi <span class='o'>6E</span>","FastConnect")],
  ("AI on a power budget",[("/hexagon","Hexagon AI at low watts","Up to 12 TFLOPS from the Hexagon processor with a fused tensor accelerator — vision, speech and sensor models on a budget that fits a fanless box or a battery.",["12 TFLOPS","Hexagon","low-power"]),
   ("/vision","Triple ISP, many cameras","A Spectra triple ISP ingests up to five concurrent cameras with computer-vision hardware — multi-camera perception for robots, handhelds and smart cameras.",["Spectra ISP","5 cameras","CV"]),
   ("/connect","Wi-Fi 6E, built to last","FastConnect Wi-Fi 6E and Bluetooth 5.2 keep the edge connected wirelessly, with wide-temperature, long-lifecycle industrial availability.",["Wi-Fi 6E","BT 5.2","industrial"])]),
  ("Sense to inference",[("Capture","Up to 5 cameras and sensors stream in."),("Process","Kryo CPU + Adreno GPU + Hexagon NPU."),("Infer","Vision and language models on-device."),("Connect","Results over Wi-Fi 6E, no cloud.")]),
  "Intelligence at the <span class='serif' style='color:var(--accent)'>far edge.</span>"),
 ("amd-ryzen-ai-max-395","Device · Private AI server","AMD Ryzen AI <span class='serif' style='color:var(--accent)'>Max+ 395</span>",
  "A private AI server in a small metal box. The AMD Ryzen AI Max+ 395 fuses 16 Zen 5 CPU cores, a Radeon 8060S iGPU and a next-gen XDNA 2 NPU for 126 platform AI TFLOPS, paired with 128 GB of LPDDR5X-8000 — enough to run 70B-class models locally, behind dual 10GbE and USB4 so nodes cluster into a compute hub. We deploy the Unovie stack on it for secure, private inference on hardware you own.",
  [("126<span class='o'>TFLOPS</span>","platform AI"),("128<span class='o'>GB</span>","LPDDR5X-8000"),("70<span class='o'>B</span>","models, local")],
  ("A private model server",[("/apu","16 Zen 5 + Radeon + XDNA 2","Sixteen Zen 5 CPU cores, a Radeon 8060S iGPU and a next-gen XDNA 2 NPU combine for 126 AI TFLOPS — CPU, GPU and NPU inference in one package.",["Zen 5","Radeon 8060S","XDNA 2"]),
   ("/memory","128 GB for big models","128 GB of LPDDR5X-8000 keeps large models — 70B-class and up — resident and private, with no weights leaving the box.",["128 GB","LPDDR5X-8000","70B local"]),
   ("/cluster","Clusters into a hub","Dual 10GbE and dual USB4 at 40 Gbps link nodes into an AI compute hub for distributed, local inference.",["dual 10GbE","USB4 40G","clustering"])]),
  ("Box to private cloud",[("Load","70B-class models resident in 128 GB."),("Serve","CPU + Radeon iGPU + XDNA 2 NPU."),("Cluster","Link nodes over 10GbE / USB4."),("Operate","Private inference, fully on-prem.")]),
  "Private models, <span class='serif' style='color:var(--accent)'>your box.</span>"),
]
def devshot(vh, vlead, img, alt):
    return ('<section><div class="wrap"><div class="shead"><div class="l">'
            '<div class="num rv"><span class="ln"></span>The device</div>'
            f'<h2 class="rv">{vh}</h2></div><p class="lead rv">{vlead}</p></div>'
            f'<div class="devshot rv"><img class="devimg" src="assets/images/{img}.png" width="820" height="440" alt="{alt}" loading="lazy"></div></div></section>')
DEV_VIS={
 "nvidia-agx-thor": devshot("An edge box you can <span class='serif' style='color:var(--accent)'>hold.</span>",
   "Thor ships as a compact, fan-cooled edge node: a dense I/O wall of USB, networking, display and capture, with a Blackwell GPU and 128&#8201;GB of unified memory behind it. Mount it on the line, in the cab or at the cell — and run the models where the data is born.",
   "agx-thor","NVIDIA AGX Thor edge node — periwinkle line drawing of the chassis and front I/O"),
 "nvidia-dgx-spark": devshot("A supercomputer that fits on a <span class='serif' style='color:var(--accent)'>desk.</span>",
   "Spark is a desktop-sized chassis with a perforated cooling top and a full I/O wall — a GB10 Grace Blackwell Superchip and 128&#8201;GB of coherent memory inside. Develop, fine-tune and serve large models locally; promote them to the edge unchanged.",
   "dgx-spark","NVIDIA DGX Spark desktop AI supercomputer — periwinkle line drawing"),
 "qualcomm-qcs6490": devshot("Built for the far <span class='serif' style='color:var(--accent)'>edge.</span>",
   "QCS6490 reference hardware brings a full I/O wall — USB-C, USB 3.0, dual Ethernet, 10GbE and HDMI — to a compact, fanless box. Premium-tier on-device AI without the power bill, deployed where wires and watts are scarce.",
   "qcs6490","Qualcomm QCS6490 edge box — periwinkle line drawing of the chassis and front I/O"),
 "amd-ryzen-ai-max-395": devshot("A server that hides in <span class='serif' style='color:var(--accent)'>plain sight.</span>",
   "An all-metal chassis with a built-in 230&#8201;W supply exposes dual 10GbE, dual USB4 and fast PCIe 4.0 NVMe on its I/O wall — a quiet, durable node you can rack a few of, or set one on a desk.",
   "ryzen-ai-max-395","AMD Ryzen AI Max+ 395 mini AI server — periwinkle line drawing"),
}
DEV_ARCH={
 "nvidia-agx-thor": platx("Built for the machine",[
   ("/compute","Blackwell GPU + Tensor Cores","2,560 CUDA cores and next-gen Tensor Cores with FP4 and a transformer engine for on-device generative AI.",["CUDA","Tensor","FP4"]),
   ("/cpu","14-core Arm Neoverse","A 14-core Arm Neoverse-V3AE cluster feeds the GPU and runs the control plane, sensors and OS.",["Neoverse-V3AE","14-core"]),
   ("/io","Sensor-grade I/O","High-speed camera, networking and PCIe lanes ingest many sensors at once with deterministic latency.",["MIPI/CSI","PCIe","10/25G"])],
   "By the numbers",[("2,070<span class='o'>TFLOPS</span>","FP4 (sparse)"),("128<span class='o'>GB</span>","LPDDR5X"),("273<span class='o'>GB/s</span>","memory bandwidth"),("40&#8211;130<span class='o'>W</span>","configurable")]),
 "nvidia-dgx-spark": platx("One coherent memory space",[
   ("/superchip","GB10 Grace Blackwell","Grace CPU and Blackwell GPU on one package, joined by NVLink-C2C at chip-to-chip bandwidth.",["GB10","NVLink-C2C"]),
   ("/memory","128 GB unified LPDDR5X","CPU and GPU address one coherent pool — no host-device copies, and room for ~200B-parameter models.",["unified","coherent","200B"]),
   ("/fabric","ConnectX scale-out","ConnectX networking links two Sparks into a single ~405B-parameter inference target.",["ConnectX","RDMA","405B"])],
   "By the numbers",[("1,000<span class='o'>TFLOPS</span>","FP4 AI"),("128<span class='o'>GB</span>","unified memory"),("20","Arm Grace cores"),("4<span class='o'>TB</span>","NVMe storage")]),
 "qualcomm-qcs6490": platx("A heterogeneous compute engine",[
   ("/cpu","Octa-core Kryo CPU","A 6&#8201;nm octa-core Qualcomm Kryo CPU runs the OS, control and classical workloads beside the AI engines.",["Kryo","octa-core","6 nm"]),
   ("/npu","Hexagon + Adreno","The Hexagon processor with a fused tensor accelerator and the Adreno GPU share inference and graphics — up to 12 TFLOPS.",["Hexagon","Adreno","12 TFLOPS"]),
   ("/isp","Spectra triple ISP","A triple ISP captures up to five concurrent camera streams with 4K HDR video and on-sensor computer vision.",["Spectra","5 cameras","4K HDR"])],
   "By the numbers",[("12<span class='o'>TFLOPS</span>","Hexagon AI"),("5","concurrent cameras"),("Wi-Fi <span class='o'>6E</span>","FastConnect"),("6<span class='o'>nm</span>","process")]),
 "amd-ryzen-ai-max-395": platx("One package, three engines",[
   ("/cpu","16 Zen 5 cores","A 16-core Zen 5 CPU drives orchestration, data prep and classical workloads alongside inference.",["Zen 5","16-core"]),
   ("/gpu","Radeon 8060S + XDNA 2","The Radeon 8060S iGPU and XDNA 2 NPU share AI work for 126 TFLOPS across vision, language and agents.",["Radeon 8060S","XDNA 2","126 TFLOPS"]),
   ("/thermal","140W, vapor-chamber cooled","Dual turbine fans and a full-coverage vapor chamber sustain 140&#8201;W at about 32&#8201;dB — full performance, near silence.",["140W TDP","vapor chamber","~32 dB"])],
   "By the numbers",[("126<span class='o'>TFLOPS</span>","platform AI"),("128<span class='o'>GB</span>","LPDDR5X-8000"),("16<span class='o'>TB</span>","NVMe · PCIe 4.0"),("140<span class='o'>W</span>","TDP, ~32 dB")]),
}
# ===================== MOCK: Hardware families =====================
A="<span class='serif' style='color:var(--accent)'>"; E="</span>"
DEVP=[
 ("amd-ryzen-ai-max-395","Sovereign factory intelligence · AMD","AMD Ryzen AI "+A+"Max+ 395"+E,
  "Built for sovereign factory intelligence: AI on the signals your lines and equipment produce, kept inside your site. Four of these quiet, compact servers make an AgentMesh Sovereign Pod in 3U next to the control system; twelve pods make an AgentNexus rack that runs agents across the fleet. Each server has sixteen Zen 5 cores, a Radeon 8060S graphics processor and an XDNA 2 AI accelerator sharing one pool of memory.",
  [("Asset health","purpose"),("4 / 3U","servers per Sovereign Pod"),("48 / 42U","servers per AgentNexus rack")],
  ("What runs on it",[
   ("/agentmesh","AgentMesh Sovereign Pod","Four servers in 3U with 2 × 10GbE networking and NVMe storage, on the factory network: Signal Encoders, the Unovie Decision Engine, the Unovie Reasoning Model and the Kiln — air-gapped by default.",["4 servers · 3U","2 × 10GbE","NVMe"]),
   ("/agentnexus","AgentNexus rack","Twelve pods in one 42U rack: agents on the processors; models, skill adapters and training on the graphics processors; data copied across shelves.",["48 servers","42U","one system"]),
   ("/npu","An AI accelerator for small models","The XDNA 2 accelerator (51 TOPS, measured on our servers) is being tested for small helper models, to free graphics time for the main model.",["XDNA 2","51 TOPS","in test"])]),
  ("Server to fleet",[("Server","One box, three compute engines."),("Pod","Four servers in 3U, linked."),("Rack","Twelve pods, one system."),("Fleet","A pod per plant, one AgentNexus.")]),
  "Sovereign intelligence for "+A+"every factory."+E),
 ("nvidia-agx-thor","Robotics &amp; DeepVision · NVIDIA","NVIDIA Jetson AGX "+A+"Thor"+E,
  "Built for robotics and DeepVision in the fab. Jetson AGX Thor puts a Blackwell-class graphics processor and 128 GB of memory into a module that lives inside a robot cell, an inspection tool or a mobile robot — running high-resolution vision models next to the camera and the motion controller, with AgentMesh's safety lanes and Evidence Log around every decision.",
  [("Robotics + vision","purpose"),("2,070<span class='o'>TFLOPS</span>","FP4 AI · NVIDIA spec"),("128<span class='o'>GB</span>","unified memory")],
  ("Vision and motion, at the tool",[
   ("/deepvision","DeepVision inspection","High-resolution vision models find defects, particles and misalignment on wafers, dies, panels and assemblies at line speed — on the tool, without sending images off the floor.",["defects","particles","on-tool"]),
   ("/robotics","Robot cells and mobile robots","Perception and checks for robot cells, wafer-handling robots and autonomous mobile robots, combined with motor, drive and vibration signals.",["robot cells","AMRs","handling"]),
   ("/lanes","Same lanes, same evidence","A reject or a hold is Lane A; anything that touches people or process safety is Lane B — an alarm and a request to the cell controller and the operator. Every decision lands in the Evidence Log.",["Lane A","Lane B","Evidence Log"])]),
  ("Image to action",[("See","Cameras and sensors stream into Thor."),("Detect","Vision models score every part."),("Decide","Lanes apply the safety boundary."),("Learn","Findings flow to AgentNexus and the Kiln.")]),
  "DeepVision and robotics, "+A+"at the tool."+E),
 ("nvidia-dgx-spark","AI engineering lab · NVIDIA","NVIDIA DGX "+A+"Spark"+E,
  "Built for the AI engineering lab. DGX Spark pairs a Grace Blackwell superchip with 128 GB of shared memory on a desk: train and test new skill adapters, run test-stand analytics and digital-twin experiments on recorded data, and host a small AgentNexus for one site — then move the same models to the plant unchanged.",
  [("Lab + training","purpose"),("1,000<span class='o'>TFLOPS</span>","FP4 AI · NVIDIA spec"),("128<span class='o'>GB</span>","shared memory")],
  ("Three roles, one box",[
   ("/train","Skill adapter training","The Kiln trains new skill adapters here, which then go through the same tests before they reach production.",["Kiln","skill adapters"]),
   ("/lab","Test stands and digital twins","Analyse test-rig runs and replay recorded factory data against new models before anything touches the factory network.",["test stands","replay","digital twin"]),
   ("/nexus","Site AgentNexus","One to four units host agents, the Unovie Model Router and skill adapters for a single site or a pilot.",["site","pilot","1–4 units"])]),
  ("Lab to plant",[("Record","Bring in recorded plant data."),("Train","The Kiln trains a skill adapter."),("Test","Prove it on unseen cases."),("Ship","Same model to the plant.")]),
  "Build and prove it "+A+"in the lab."+E),
 ("qualcomm-qcs6490","Mobile &amp; remote assets · Qualcomm","Qualcomm "+A+"QCS6490"+E,
  "Built for mobile and remote assets. Where wires and watts are scarce — a mobile robot, an AGV, a drone dock, a battery container — a fanless QCS6490 box collects and pre-processes signals on site and forwards compact fingerprints to the nearest AgentMesh pod.",
  [("Remote assets","purpose"),("12<span class='o'>TFLOPS</span>","on-device AI"),("fanless","low power")],
  ("Reach the hard-to-wire assets",[
   ("/collect","Collect on site","Reads sensors where running cables would be costly or impossible.",["remote","low power"]),
   ("/prepare","Prepare locally","Turns raw signal into compact fingerprints before sending anything.",["fingerprints","bandwidth"]),
   ("/forward","Forward to AgentMesh","Sends findings to the nearest pod, where the safety lanes and Evidence Log apply.",["AgentMesh","lanes"])]),
  ("Sensor to pod",[("Sense","Sensors on remote assets."),("Prepare","Fingerprints on the device."),("Forward","Wireless to the nearest pod."),("Decide","AgentMesh applies the lanes.")]),
  "Reach the "+A+"far edge."+E),
]
DEV_ARCH["amd-ryzen-ai-max-395"]=platx("One package, three engines",[
   ("/cpu","16 Zen 5 cores","Run the agents, the plant connections and the system itself.",["Zen 5","16 cores"]),
   ("/gpu","Radeon 8060S graphics","Runs the Unovie Reasoning Model, skill adapters and training.",["Radeon 8060S"]),
   ("/npu","XDNA 2 AI accelerator","Being tested for small helper models.",["XDNA 2","51 TOPS"])],
   "By the numbers",[("16","Zen 5 cores"),("64–128<span class='o'>GB</span>","shared memory"),("2 × 10<span class='o'>GbE</span>","network"),("6 × 2<span class='o'>TB</span>","NVMe in our build")])
DEV_ARCH["nvidia-agx-thor"]=platx("Built for the machine",[
   ("/compute","Blackwell-class graphics","Runs models on the equipment itself.",["Blackwell"]),
   ("/cpu","14 Arm cores","Run the plant connections and the AgentMesh services.",["Arm","14 cores"]),
   ("/io","Fast sensor I/O","Many sensors and networks at once.",["sensors","networking"])],
   "By the numbers · NVIDIA spec",[("2,070<span class='o'>TFLOPS</span>","FP4 (sparse)"),("128<span class='o'>GB</span>","unified memory"),("273<span class='o'>GB/s</span>","memory bandwidth"),("40–130<span class='o'>W</span>","configurable")])
DEV_ARCH["nvidia-dgx-spark"]=platx("One shared memory space",[
   ("/superchip","Grace Blackwell","Arm processor and Blackwell graphics in one package.",["GB10"]),
   ("/memory","128 GB shared","Room for models, agents and training on one unit.",["128 GB"]),
   ("/link","Links to a second unit","Two units can work as one.",["scale-out"])],
   "By the numbers · NVIDIA spec",[("1,000<span class='o'>TFLOPS</span>","FP4 AI"),("128<span class='o'>GB</span>","shared memory"),("20","Arm cores"),("4<span class='o'>TB</span>","NVMe storage")])
DEV_ARCH["qualcomm-qcs6490"]=platx("Built for low power",[
   ("/cpu","Eight-core processor","Runs the device and its connections.",["8 cores"]),
   ("/ai","On-device AI engine","Pre-processes signals before sending.",["12 TFLOPS"]),
   ("/connect","Wireless built in","Wi-Fi 6E and Bluetooth.",["Wi-Fi 6E"])],
   "By the numbers · Qualcomm spec",[("12<span class='o'>TFLOPS</span>","on-device AI"),("6<span class='o'>nm</span>","process"),("Wi-Fi <span class='o'>6E</span>","wireless"),("fanless","design")])
# ===================== /MOCK =====================

def _devkey(slug): return slug.split("-",1)[1]
def devpanel(s, first):
    slug,cat,title,lead,kpis,feats,hows,cta=s; key=_devkey(slug)
    return (f'<div class="tpanel{" active" if first else ""}" id="{key}" role="tabpanel" aria-labelledby="tab-{key}">'
      f'<section class="psub"><div class="wrap"><div class="tag rv">{cat}</div>'
      f'<h2 class="rv" style="margin-top:10px">{title}</h2><p class="lead rv">{lead}</p>{metrics(kpis)}</div></section>'
      f'{DEV_VIS.get(slug,"")}'
      f'<section><div class="wrap">{shead("01","What it does",feats[0])}{disc(feats[1])}</div></section>'
      f'<section><div class="wrap">{shead("02","How it works",hows[0])}{steps(hows[1])}</div></section>'
      f'{DEV_ARCH.get(slug,"")}</div>')
# ===================== MOCK: Hardware page, Industry 4.0 content =====================
ICO.update({
 "truck":'<svg viewBox="0 0 24 24"><path d="M3 7h11v8H3zM14 10h4l3 3v2h-7z"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>',
 "cell":'<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>',
 "clip":'<svg viewBox="0 0 24 24"><rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9zM8 12h8M8 16h5"/></svg>',
 "pin":'<svg viewBox="0 0 24 24"><path d="M12 22s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
 "pipe":'<svg viewBox="0 0 24 24"><path d="M2 9h8v6H2zM14 9h8v6h-8zM10 11h4v2h-4z"/></svg>',
 "fleet":'<svg viewBox="0 0 24 24"><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M7 6h10M6 8l5 8M18 8l-5 8"/></svg>',
 "flask":'<svg viewBox="0 0 24 24"><path d="M9 3h6M10 3v6L4 20h16L14 9V3"/></svg>',
 "wafer":'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M7 9h10M6 12h12M7 15h10M9 6v12M12 3v18M15 6v12"/></svg>',
 "eye":'<svg viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
})

def factlist(items):
    return '<table class="glance rv facts">'+"".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in items)+'</table>'

STACK_ROWS=[
 ("Unovie Gateway","read-only plant connections"),
 ("Signal Encoders","signal fingerprints"),
 ("Vector Memory","\"seen this before?\""),
 ("Unovie Decision Engine","Lane A / Lane B"),
 ("Unovie Reasoning Model","root cause, work orders"),
 ("Kiln","tested improvements"),
 ("Evidence Log","signed record"),
 ("Unovie Agent Runtime","fleet agents in sandboxes"),
 ("Unovie Model Router","model + skill adapter per request"),
 ("Mesh Arbiter","failover"),
]
def stackmatrix(cols, marks, note):
    head='<tr><th>Unovie platform component</th>'+''.join(f'<th>{c}</th>' for c in cols)+'</tr>'
    sym={"y":'<span class="mk y" title="runs here">●</span>',"p":'<span class="mk p" title="light / partial">◐</span>',"n":'<span class="mk n">—</span>'}
    rows=''.join(f'<tr><td><b>{n}</b><small>{d}</small></td>'+''.join(f'<td>{sym[m]}</td>' for m in marks[i])+'</tr>' for i,(n,d) in enumerate(STACK_ROWS))
    return f'<div class="stackwrap rv"><table class="stackm">{head}{rows}</table></div><p class="illus rv" style="margin-top:10px">{note}</p>'

def sketchpair(items):
    return '<div class="field" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">'+''.join(
        f'<div class="fcard rv"><div class="sk" style="aspect-ratio:16/10"><img src="assets/images/sketch/{img}.jpg" alt="{alt}" loading="lazy" style="object-fit:contain;padding:10px"></div><div class="bd"><div class="tag">{tag}</div><h4>{t}</h4><p>{d}</p></div></div>'
        for img,alt,tag,t,d in items)+'</div>'

DEV_EXTRA={
 "amd-ryzen-ai-max-395":
   S("03","Industry 4.0 use cases","Agentic jobs it runs "+A_+"today."+E_,
     kits([("rot","Robot &amp; motion health","Robot &amp; Motion Health on robots, motion axes, spindles and conveyors: fault class, severity and a drafted work order.","AgentMesh · joint current · vibration"),
           ("bat","Battery line &amp; storage safety","Weld and formation signatures in line; on storage sites, runaway precursors raised as an alarm into the fire panel.","AgentMesh · weld · cycler · off-gas"),
           ("ele","Fab utilities &amp; electrical health","Pumps, chillers, scrubbers, drives and tool power at fabs and their suppliers: early warnings with a drafted work order.","AgentMesh · vibration · power quality"),
           ("ot","Factory network watch","Unauthorized writes and unusual commands on the factory network, with evidence mapped to NIST SP 800-53.","AgentMesh · control traffic"),
           ("clip","Quality records &amp; planning","Agents group findings across lines and sites, draft non-conformance reports and quality records, and plan repairs around production.","AgentNexus · agents"),
           ("fleet","Fleet learning","The same fault pattern seen on one line is recognised on the next; tested skill adapters roll out fleet-wide.","AgentNexus · Kiln")]),
     "The same server runs both systems: four in a Sovereign Pod at each line or site, forty-eight in one AgentNexus rack.")
   + S("04","Two deployment shapes","One server, "+A_+"pod or rack."+E_,
     sketchpair([("sovereign-pod","Illustration of the AgentMesh Sovereign Pod","AgentMesh","Sovereign Pod · 3U","Four servers on a sliding shelf in a compact cabinet, with 2 × 10GbE networking and NVMe storage, on the factory network."),
                 ("agentnexus-rack","Illustration of the AgentNexus reference rack","AgentNexus","Reference rack · 42U","Twelve trays of four servers, two switches and dual power feeds, in a central cabinet.")])
     + factlist([("Where it sits","Factory network (pod) · central cabinet (rack)"),("Form","4 servers in 3U · 48 servers in 42U"),("Per server","16 Zen 5 cores · Radeon 8060S graphics · XDNA 2 accelerator · 64 GB shared memory · NVMe storage"),
                 ("Network","2 × 10GbE per server to two switches · fast cables inside each shelf"),("Environment","Climate-controlled rack, 0–35 °C"),("Status","Pod runs today · rack is a reference design on the same server")]))
   + S("05","What runs on it","The full Unovie platform",
     stackmatrix(["Sovereign Pod","AgentNexus rack"],
       [list("yp"),list("yn"),list("yy"),list("yn"),list("yy"),list("yy"),list("yy"),list("py"),list("py"),list("yy")],
       "● runs here · ◐ light or partial role · — not used. The pod forwards events to AgentNexus; the rack never reaches back into factory control.")),
 "nvidia-agx-thor":
   S("03","Industry 4.0 use cases","Robotics and DeepVision "+A_+"for the fab."+E_,
     kits([("eye","Wafer &amp; die inspection","DeepVision models find defects, particles and scratches on wafers and dies at the tool, holding or rejecting a lot through Lane A.","semiconductor · electronics"),
           ("wafer","Panel &amp; assembly inspection","Solder, placement and surface defects on boards, panels and assemblies, checked at line speed.","PCB · display · assembly"),
           ("cell","Robot-cell quality","Vision plus process signatures — weld current, torque, vibration — confirm every robot cycle.","robot cells · welding · fastening"),
           ("truck","Wafer handling &amp; AMRs","Perception and health checks for wafer-handling robots and autonomous mobile robots moving lots between tools.","handling · AMRs · drives"),
           ("rot","Tool health","Vacuum pumps, chillers and motion stages watched through their own vibration and electrical signals.","vibration · electrical"),
           ("pin","Clean-room sovereignty","Images and models stay on the tool; only findings and evidence move to AgentNexus.","no images off the floor")]),
     "Thor is where Unovie uses vision first: the cameras and models sit on the tool, inside the same safety lanes as every AgentMesh decision.")
   + S("04","Deployment","Where it lives",
     factlist([("Where it sits","Inside an inspection tool, a robot cell, a wafer-handling robot or an AMR"),("Form","Compact module · 40–130 W configurable (NVIDIA spec)"),("Memory","128 GB unified (NVIDIA spec)"),
               ("Connectivity","Works disconnected · findings sync to AgentNexus"),("Status","Available on — the AgentMesh software is brought to Thor per project")]))
   + S("05","What runs on it","AgentMesh, at the tool",
     stackmatrix(["Jetson AGX Thor"],[list("y"),list("y"),list("y"),list("y"),list("y"),list("p"),list("y"),list("n"),list("n"),list("n")],
       "● runs here · ◐ light role (nightly playbook only; training happens on AgentNexus or DGX Spark) · — not used.")),
 "nvidia-dgx-spark":
   S("03","Industry 4.0 use cases","The lab where "+A_+"plant AI is built."+E_,
     kits([("flask","Skill adapter training","The Kiln trains new skill adapters on recorded plant outcomes, ready for testing.","Kiln · training"),
           ("test","Test-stand analytics","Pressure, strain and acoustic data from test rigs analysed run by run, with drafted test reports.","aerospace · energy · automotive"),
           ("fleet","Digital-twin experiments","Replay recorded plant data against new models and rules before anything reaches the plant.","replay · what-if"),
           ("clip","Site AgentNexus","A small AgentNexus for one site: planner, shift-handover and quality agents working across lines.","AgentNexus · 1–4 units")]),
     "When a pilot grows, the same agents, models and adapters move to the AMD rack unchanged.")
   + S("04","Deployment","Where it lives",
     factlist([("Where it sits","Engineering office, server room or a shelf near the line"),("Form","Desk-sized unit · two can be linked"),("Memory","128 GB shared (NVIDIA spec)"),
               ("Roles","Single-unit AgentMesh · site AgentNexus · training node"),("Status","Available on — brought to Spark per project")]))
   + S("05","What runs on it","Mesh, Nexus or training",
     stackmatrix(["As AgentMesh","As site AgentNexus"],
       [list("yp"),list("yn"),list("yy"),list("yn"),list("yy"),list("yy"),list("yy"),list("ny"),list("py"),list("pp")],
       "● runs here · ◐ light or partial role · — not used.")),
 "qualcomm-qcs6490":
   S("03","Industry 4.0 use cases","Remote and mobile assets, "+A_+"in the loop."+E_,
     kits([("pin","Mobile robots &amp; AGVs","Motor, wheel and battery health on robots that move, pre-processed on board.","motor current · vibration"),
           ("pipe","Drone docks &amp; outdoor assets","Motor, charge and environment signals at docks and outdoor equipment, with only compact findings sent back.","motor · battery · environment"),
           ("bat","Battery containers","Battery and off-gas data from remote containers, forwarded to the nearest pod for the safety lanes.","battery data · off-gas"),
           ("rot","Wireless sensing","Sensors on moving and hard-to-cable equipment, without running new cable.","wireless · battery-powered")]),
     "QCS6490 senses and prepares; the decisions, lanes and Evidence Log stay on the nearest AgentMesh pod.")
   + S("04","Deployment","Where it lives",
     factlist([("Where it sits","Next to remote assets, in a small fanless enclosure"),("Power","Low power, fanless (Qualcomm spec)"),("Connectivity","Wi-Fi 6E and Bluetooth · forwards to the nearest pod"),("Status","Far-edge sensing that feeds AgentMesh")]))
   + S("05","What runs on it","Sensing and fingerprints",
     stackmatrix(["QCS6490"],[list("p"),list("y"),list("n"),list("n"),list("n"),list("n"),list("n"),list("n"),list("n"),list("n")],
       "● runs here · ◐ light role (local sensor connections) · — runs on the nearest AgentMesh pod instead.")),
}


def signals(title, items, note):
    return S("06","Industry signals",title, disc(items) + f'<p class="illus rv" style="margin-top:14px">{note}</p>')
SIG_NOTE="Public announcements and vendor material, November 2026 · vendor-reported, not Unovie measurements"
DEV_SIGNALS={
 "amd-ryzen-ai-max-395": signals("What the industry is doing "+A_+"on this chip."+E_,[
   ("/on-prem-llm","On-premise industrial AI boxes","Industrial PC makers now ship compact systems built on the Ryzen AI Max+ 395 with dual 10GbE, aimed at running language models on-premise in plants.",["industrial PCs","on-premise","vendor-reported"]),
   ("/maintenance","Predictive maintenance with local models","Industrial AI software partners run local models on Ryzen AI processors to detect anomalies, predict failures and trigger guided actions from live plant data — without cloud inference bills.",["anomaly detection","predictive maintenance","vendor-reported"]),
   ("/embedded","An embedded family for robots and machine vision","AMD's embedded Ryzen AI line extends the same architecture to robotics, industrial PCs and machine vision, with industrial lifecycles.",["robotics","machine vision","embedded"]),
   ("/unovie","Where Unovie fits","AgentMesh and AgentNexus put these servers to work as a complete system: asset signals, safety lanes, evidence and fleet agents — not just a box that runs a model.",["AgentMesh","AgentNexus"])], SIG_NOTE),
 "nvidia-agx-thor": signals("What the industry is doing "+A_+"on Thor."+E_,[
   ("/inspection","Multi-camera quality inspection","Industrial Thor systems are being deployed for multi-camera quality inspection, automated optical inspection and defect detection on the line.",["AOI","defect detection","vendor-reported"]),
   ("/robots","Industrial robots and manufacturing cells","Industrial robot makers and heavy-equipment makers are adopting Thor for manufacturing cells and autonomous equipment that fuse many sensor streams on the device.",["robot cells","autonomous equipment","vendor-reported"]),
   ("/agentic","Agentic factory operations","A major industrial computer maker reports running an agentic “factory brain” on Thor in its own manufacturing plants.",["agentic AI","factory operations","vendor-reported"]),
   ("/sensors","High-speed sensor ingest","Thor with a sensor bridge ingests camera, LiDAR, IMU and encoder data for real-time pipelines in harsh, vibrating environments.",["camera","LiDAR · IMU","rugged"]),
   ("/fab","Where Unovie fits","Unovie focuses Thor on DeepVision in fabs — wafer, die and panel inspection and wafer handling — inside AgentMesh's safety lanes. Public fab deployments on Thor are still emerging.",["DeepVision","fabs","AgentMesh"])], SIG_NOTE),
 "nvidia-dgx-spark": signals("What the industry is doing "+A_+"on Spark."+E_,[
   ("/plantfloor","Language models on the plant floor","Industrial DataOps platforms now run on DGX Spark, bringing language-model capability to factory data with lower latency and data kept on site.",["industrial data","on site","vendor-reported"]),
   ("/twin","Live digital twins","Demonstrations stream real camera feeds into DGX Spark to keep a simulation-based digital twin of a cell continuously in step with the physical world.",["digital twin","simulation","demo"]),
   ("/support","Supported for edge and on-prem","A supported software stack with lifecycle management and security updates is offered for smart-manufacturing and inspection deployments.",["supported stack","on-prem"]),
   ("/lab","Where Unovie fits","Unovie uses Spark as the AI engineering lab: training and testing skill adapters, replaying recorded plant data, and hosting a small AgentNexus for a pilot.",["Kiln","test stands","site AgentNexus"])], SIG_NOTE),
 "qualcomm-qcs6490": signals("What the industry is doing "+A_+"on QCS6490."+E_,[
   ("/handhelds","Rugged handhelds, scanners and HMIs","Qualcomm targets rugged handhelds and tablets, industrial scanners, industrial PCs and operator panels with this processor.",["rugged","HMI","vendor-reported"]),
   ("/robots","Mobile robots and inspection drones","Autonomous mobile robots, companion robots and site-inspection drones are listed robotics targets.",["AMRs","site inspection"]),
   ("/maint","Anomaly detection at hazardous sites","Third-party inspection robots built on QCS6490 use multimodal sensing to flag anomalies and support predictive maintenance in factories and hazardous sites.",["multimodal sensing","predictive maintenance","vendor-reported"]),
   ("/lifecycle","Long industrial lifecycle","Part of a product-longevity programme with extended software support, and runs Linux, Ubuntu, Android and Windows IoT.",["longevity","multi-OS"])], SIG_NOTE),
}

def devpanel(s, first):
    slug,cat,title,lead,kpis,feats,hows,cta=s; key=_devkey(slug)
    return (f'<div class="tpanel{" active" if first else ""}" id="{key}" role="tabpanel" aria-labelledby="tab-{key}">'
      f'<section class="psub"><div class="wrap"><div class="tag rv">{cat}</div>'
      f'<h2 class="rv" style="margin-top:10px">{title}</h2><p class="lead rv">{lead}</p>{metrics(kpis)}</div></section>'
      f'{DEV_VIS.get(slug,"") if slug!="amd-ryzen-ai-max-395" else ""}'
      f'<section><div class="wrap">{shead("01","What it does",feats[0])}{disc(feats[1])}</div></section>'
      f'<section><div class="wrap">{shead("02","How it works",hows[0])}{steps(hows[1])}</div></section>'
      f'{DEV_EXTRA.get(slug,"")}'
      f'{DEV_SIGNALS.get(slug,"")}'
      f'</div>')

HW_MATRIX='''<section style="padding-top:20px"><div class="wrap">
  <div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>Choose by job</div><h2 class="rv">Which hardware <span class="serif" style="color:var(--accent)">for which job.</span></h2></div>
  <p class="lead rv">Every option runs the same Unovie platform. Pick by where the work happens and how much of it there is.</p></div>
  <div class="stackwrap rv"><table class="glance hwm">
    <tr><th></th><th>AMD Ryzen AI Max+ 395</th><th>NVIDIA Jetson AGX Thor</th><th>NVIDIA DGX Spark</th><th>Qualcomm QCS6490</th></tr>
    <tr><td>Industry 4.0 purpose</td><td><b>Sovereign factory intelligence</b></td><td><b>Robotics &amp; DeepVision for fabs</b></td><td><b>AI engineering lab</b></td><td><b>Mobile &amp; remote assets</b></td></tr>
    <tr><td>Role</td><td>AgentMesh Sovereign Pod · AgentNexus rack</td><td>AgentMesh at the tool or robot</td><td>Training · test stands · site AgentNexus</td><td>Far-edge sensing for AgentMesh</td></tr>
    <tr><td>Where it sits</td><td>Factory network · central cabinet</td><td>Inspection tool · robot cell · AMR</td><td>Engineering lab · server room</td><td>Robots, AGVs · remote assets</td></tr>
    <tr><td>Agentic jobs</td><td>Robot &amp; motion health · battery line safety · fab utilities · factory network watch · quality records</td><td>Wafer &amp; die inspection · robot-cell quality · wafer handling &amp; AMRs · tool health</td><td>Skill adapter training · test-stand analytics · digital-twin experiments · site agents</td><td>Mobile robots · AGVs · drone docks · battery containers</td></tr>
    <tr><td>Memory</td><td>64 GB per server (128 GB builds)</td><td>128 GB unified</td><td>128 GB shared</td><td>On-device</td></tr>
    <tr><td>Form</td><td>4 servers / 3U · 48 servers / 42U</td><td>Module · 40–130 W</td><td>Desk-sized unit</td><td>Fanless box</td></tr>
    <tr><td>Status</td><td><span class="st now">Runs today</span></td><td><span class="st">Available on</span></td><td><span class="st">Available on</span></td><td><span class="st">Far edge</span></td></tr>
  </table></div>
</div></section>
'''
HWCSS='''
/* ---------- hardware page (mock) ---------- */
.stackwrap{overflow-x:auto;margin-top:30px}
.stackm{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--surface)}
.stackm th,.stackm td{padding:12px 18px;border-bottom:1px solid var(--line);text-align:center;font-size:14.5px;color:var(--fg-mut)}
.stackm th{font-family:var(--disp);font-size:15px;color:var(--fg);background:var(--surface-2)}
.stackm th:first-child,.stackm td:first-child{text-align:left}
.stackm td:first-child b{display:block;color:var(--fg);font-weight:600}
.stackm td:first-child small{font-size:12.5px;color:var(--fg-dim)}
.stackm tr:last-child td{border-bottom:0}
.mk{font-size:17px}.mk.y{color:var(--accent)}.mk.p{color:var(--steel)}.mk.n{color:var(--fg-dim)}
.glance.facts{margin-top:22px}
.glance.facts td:first-child{width:24%}
.glance.hwm{min-width:860px}
.glance.hwm th{font-size:15px;color:var(--fg)}
.glance.hwm td:first-child{width:14%}
.glance .st{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;padding:3px 9px;border-radius:999px;border:1px solid var(--line-2);color:var(--fg-mut)}
.glance .st.now{border-color:var(--accent);color:var(--accent)}
'''
# ===================== /MOCK hardware =====================

_dtabs="".join(f'<button class="tab{" active" if i==0 else ""}" id="tab-{_devkey(s[0])}" data-tab="{_devkey(s[0])}" role="tab" aria-selected="{"true" if i==0 else "false"}" data-cursor>{re.sub("<[^>]+>","",s[2])}</button>' for i,s in enumerate(DEVP))
_dpanels="".join(devpanel(s,i==0) for i,s in enumerate(DEVP))
_devhead=HEAD("","Hardware — AgentMesh and AgentNexus on AMD and NVIDIA — Unovie.AI","AgentMesh and AgentNexus run the same agents, models and safety lanes on AMD Ryzen AI Max+ 395, NVIDIA Jetson AGX Thor and NVIDIA DGX Spark, with Qualcomm QCS6490 at the far edge.")
_devbody=f"""{NGBG}{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">Hardware</span></div>
  <div class="tag rv">Hardware</div>
  <h1 class="rv" style="margin-top:18px">Two hardware families. <span class="serif" style="color:var(--accent)">One platform.</span></h1>
  <p class="lead rv">AgentMesh and AgentNexus run the same agents, models, safety lanes and Evidence Log on AMD and NVIDIA hardware you own. AMD Ryzen AI Max+ 395 is the reference build for both. NVIDIA Jetson AGX Thor brings AgentMesh inside the machine; NVIDIA DGX Spark runs AgentMesh on a desk or a small AgentNexus for a site; Qualcomm QCS6490 extends sensing to the far edge.</p>
  <div class="runs rv" style="margin:26px 0 22px"><div class="run"><span class="st now">Runs today</span><h4>AMD Ryzen AI Max+ 395</h4><p>The AgentMesh Sovereign Pod (2 × 10GbE, NVMe) runs today; the AgentNexus rack is a reference design on the same server.</p></div><div class="run"><span class="st">Available on</span><h4>NVIDIA Jetson AGX Thor · DGX Spark</h4><p>Robotics &amp; DeepVision at the tool; the AI engineering lab — brought to NVIDIA per project.</p></div><div class="run"><span class="st">Far edge</span><h4>Qualcomm QCS6490</h4><p>Remote and mobile assets, feeding the nearest AgentMesh pod.</p></div></div>
  <div class="cta rv"><a class="btn btn-acc" href="index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
    <a class="btn btn-gh" href="resources/edge-ai-models.html" target="_blank" data-cursor>Read the field guide</a></div>
</div></section>
{HW_MATRIX}
<section class="tabwrap"><div class="wrap"><div class="tabs" role="tablist" aria-label="Hardware">{_dtabs}</div></div></section>
{_dpanels}
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Let's build</div>
  <h2 style="margin-top:16px">Pick the hardware. <span class="serif" style="color:var(--accent)">We'll run the platform on it.</span></h2>
  <p class="lead">Turnkey Edge-AI — fixed time, fixed cost, full responsibility.</p>
  <div class="cta"><a class="btn btn-acc" href="/contact.html" data-m="moc.eivonu|snoitulos" data-subject="Project enquiry" data-cursor>Talk to our engineers <span class="ar">→</span></a>
    <a class="btn btn-gh" href="index.html#accelerators" data-cursor>See all solutions</a></div>
</div></div></section>
{FOOTER("")}"""
open(f"{ROOT}/device-platform.html","w",encoding="utf-8").write(_devhead+_devbody)

# ----- ABOUT -----
about=f'''{HEAD("","About — Unovie.AI","An AI-engineering studio that designs, builds, and operates custom Edge-AI Agentic Systems.")}{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">About</span></div>
  <div class="tag rv">About <span class="o">·</span> Unovie.AI</div>
  <h1 class="rv" style="margin-top:18px">We engineer AI that <span class="serif" style="color:var(--accent)">ships.</span></h1>
  <p class="lead rv">Unovie is an AI-engineering studio for Industry 4.0, founder-led by a team whose vision matches the most ambitious in the field — and measured by what reaches production. We take full responsibility for AI transformation — from architecture through POC and MVP to production readiness — on a foundation of frozen-base, self-improving edge systems that you own and can audit. While the market splits between multi-year transformation programs and big-vision manifestos, we take the third path: production-grade, agentic systems you own, delivered in weeks at a fixed cost.</p>
  <div class="cta rv"><a class="btn btn-acc" href="index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
    <a class="btn btn-gh" href="resources/edge-ai-models.html" target="_blank" data-cursor>Read our field guide</a></div>
  {metrics([("4","engineering disciplines"),("5","-step methodology"),("fixed","time &amp; cost")])}
</div></section>
<section id="engineering"><div class="wrap">{shead("01","What we are good at","Four engineering disciplines.")}{disc([
  ("/model-engineering","Signal &amp; Model Engineering","We turn every signal a next-generation line produces — robot joints, vision, vibration, electrical, battery, test-rig and network data — into fingerprints and small, specialised models.",['signal encoders', 'skill adapters', 'held-out tests']),
  ("/robotics-ot","Robotics &amp; OT Integration","AI built into sensor-dense, robotic lines, designed against NIST SP 800-53 controls — your safety PLC, cell controller and operators stay in charge.",['robot cells', 'Lane A · Lane B', 'SP 800-53']),
  ("/edge-efficiency","Edge Efficiency","Fast answers on small, owned hardware.",['&lt; 30 ms target', 'AMD · NVIDIA', 'compact models']),
  ("/sovereign-reliable","Sovereign &amp; Reliable Operations","Systems you own and can run without us.",['air-gapped', 'Mesh Arbiter', 'fixed cost'])])}</div></section>
<section id="delivery"><div class="wrap">{shead("02","How we deliver","A proven, success-based methodology.")}{steps([
  ("Assess &amp; plan","Workshops, ROI, value outcomes."),("Solution design","Roadmap &amp; reference architecture."),
  ("Build &amp; test","Data, models, testing, monitoring."),("Optimize","KPI tracking &amp; feedback loops."),("Train &amp; support","Enablement &amp; adoption.")])}</div></section>
<section><div class="wrap">{shead("03","Why teams choose us","Vision that ships.")}{disc([
  ("/leadership","Founder-led vision","Led by founders whose ambition matches the field's most visionary — and who insist that vision reach production.",["founder-led","visionary"]),
  ("/velocity","Execution velocity","Production-grade agentic systems in weeks, not multi-year programs — fixed scope, fixed cost.",["weeks","fixed cost"]),
  ("/sovereignty","Owned &amp; sovereign","On-prem on hardware you own, auditable and reversible — your context never leaves your boundary.",["on-prem","auditable"])])}<div class="cta rv" style="margin-top:8px"><a class="btn btn-gh" href="why-unovie.html" data-cursor>Why Unovie <span class="ar">→</span></a></div></div></section>
<section><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Partners</div>
  <h2 style="margin-top:16px">Trusted with <span class="serif" style="color:var(--accent)">NVIDIA · AMD · Qualcomm · Siemens · GE.</span></h2>
  <p class="lead">Manufacturing · Logistics · Oil &amp; Gas · Food Processing. Bring us a problem; we will return a system.</p>
  <div class="cta"><a class="btn btn-acc" href="/contact.html" data-m="moc.eivonu|snoitulos" data-cursor>Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("")}'''
open(f"{ROOT}/about.html","w",encoding="utf-8").write(about)

# ----- WHY UNOVIE -----
why=f'''{HEAD("","Why Unovie — veteran founders, sovereign AI for next-generation manufacturing","Unovie is an Austin, Texas AI-engineering studio that takes industrial AI from pilot to production in a quarter: on-site OT engineers, a 6-week paid pilot on your data, and AgentMesh and AgentNexus running on hardware you own.")}{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">Why Unovie</span></div>
  <div class="tag rv">Why Unovie <span class="o">·</span> Engineering first <span class="o">·</span> AI native <span class="o">·</span> Austin, Texas</div>
  <h1 class="rv" style="margin-top:18px">Built in Austin. <span class="serif" style="color:var(--accent)">Ready for your factory.</span></h1>
  <p class="lead rv">Unovie is an engineering-first, AI-native company built for Physical AI, headquartered in Austin, Texas. We are a young company with veteran founders: each brings 20+ years in OT and Physical AI — control systems, robot cells, factory networks, safety boundaries and the low-latency problems deep-tech sites run into. For four years we have been building that experience into a sovereign AI platform for next-generation manufacturing. Most industrial AI is still stuck in pilots; we take it to production in a quarter, with your data on site and safety decisions left with your control systems and operators.</p>
  <div class="cta rv"><a class="btn btn-acc" href="index.html#contact" data-cursor>Meet us in Austin <span class="ar">→</span></a>
    <a class="btn btn-gh" href="platform/agentmesh.html" data-cursor>See the platform</a></div>
  {metrics([("20+ yrs","each founder, in OT &amp; Physical AI"),("4 yrs","building the Unovie platform"),("6 weeks","paid pilot on your line"),("1 quarter","from pilot to production")])}
</div></section>
<section><div class="wrap">{shead("01","Who we are","Engineering first. "+A_+"AI native."+E_,"A young company with veteran founders. Each spent 20+ years in OT and Physical AI before starting Unovie; the platform was built around agents and small specialised models from day one.")}{disc([
  ("/engineering-first","Engineering first","Each founder brings 20+ years designing, building and running OT and Physical AI systems: control systems, robot cells, factory networks, safety systems and the boundaries between them. We start from how your factory really works.",["20+ years each","OT &amp; Physical AI","factory-first"]),
  ("/low-latency","Low latency, at the control layer","A 30 ms decision budget at the machine; integration with robot controllers, safety PLCs, vision systems and test rigs over OPC UA, EtherCAT and Modbus — and the discipline to never write where we shouldn't.",["&lt; 30 ms target","robots · safety PLC","OPC UA · EtherCAT"]),
  ("/ai-native","AI native, cloud native","Agents, small specialised models, Vector Memory and a test-gated improvement loop are built in from the start — as microservices on a CNCF-conformant platform, not AI bolted onto legacy software.",["agents","microservices","CNCF-conformant"]),
  ("/compliance","Born with compliance in mind","Designed from day one against NIST SP 800-53 controls (with the SP 800-82r3 OT overlay) and the NIST AI Risk Management Framework. Every decision, request and change is written to a signed Evidence Log, so engineers, auditors and insurers can see exactly what the AI did and why.",["SP 800-53","AI RMF","Evidence Log"])])}</div></section>
<section><div class="wrap">{shead("02","Built for Physical AI","From bits "+A_+"to atoms."+E_,"Physical AI means AI that reads the real world through its signals and acts on real equipment — so it has to be fast, local and safe. That is what AgentMesh and AgentNexus are built for.")}{steps([
  ("Perceive","Vibration, electrical, battery, process and network signals, read where they start."),
  ("Reason","Context from the factory's own history, manuals and failures — explained, with evidence."),
  ("Act","Low-consequence actions directly; safety-related actions as requests your systems decide."),
  ("Adapt","Tested improvements every night, signed and reversible — the base model never drifts.")])}</div></section>
<section><div class="wrap">{shead("03","Based in Texas","Close to where "+A_+"deep tech is being built."+E_,"We serve customers nationally. Texas is our home base and proof of proximity: it is building fabs, gigafactories, space and robot factories, new shipyards and reactors — sites with sensitive data that can't go to the cloud, and too few people to watch it all. Here we're close enough to be on your floor this week.")}{disc([
  ("/i-35","Austin &amp; Central Texas","Chip fabs and their suppliers, robotics and space factories: fab utilities, robot cells and vision QA, with quality records drafted for sign-off.",["chip fabs","robotics","space"]),
  ("/battery","Battery manufacturing &amp; storage","Battery lines and storage fleets: in-line weld and formation signals, and early warning of thermal runaway on storage sites, as an alarm.",["battery lines","storage fleets","evidence"]),
  ("/gulf","Houston to the Gulf Coast","Space hardware and test stands, new shipyards and autonomous-vessel yards, and advanced energy sites.",["space","shipyards","advanced energy"]),
  ("/test","Test stands","Aerospace and energy test stands: anomaly flags to the test conductor during a run, and drafted post-test reports — never in the flight-critical path.",["test stands","AS9100 QA","reports"])])}</div></section>
<section><div class="wrap">{shead("04","Why now","Ready for "+A_+"2027."+E_,"Several dated changes are turning industrial AI from a pilot into a requirement.")}{disc([
  ("/pilots","Pilots need to become production","Most manufacturers are still in pilots or limited deployments. Buyers want a partner who reaches production in a quarter, on their own hardware.",["pilot to production","one quarter"]),
  ("/rules","New factories, new scrutiny","Factory ramps in 2027–28 arrive with battery-site safety rules, fab equipment-security standards and defense data-handling requirements. Buyers need monitoring and evidence, not just dashboards.",["factory ramps","equipment security","2027–28"]),
  ("/governance","Governance decides what survives","AI governance rules — including Texas's, which recognises the NIST AI RMF — reward systems that can show their work. Every Unovie site ships a signed evidence pack mapped to NIST SP 800-53, the NIST AI RMF and IEC 62443.",["SP 800-53","NIST AI RMF","IEC 62443"]),
  ("/hardware","Hardware you own, AMD or NVIDIA","Memory and accelerator prices are volatile. Our platform runs on AMD and NVIDIA, so you choose the hardware — or let us own and refresh it as a service.",["AMD","NVIDIA","as-a-service"])])}</div></section>
<section><div class="wrap">{shead("05","How we engage","From site audit to "+A_+"fleet."+E_)}{steps([
  ("Site audit","An engineer reviews your sensors, robots, network and control systems before anything is signed."),
  ("6-week pilot","One domain kit on your own line, a baseline ROI view and a measured latency report — credited toward production."),
  ("Production site","An AgentMesh Sovereign Pod integrated with your sensors, cell controllers, safety PLC, MES and work-order system."),
  ("Fleet rollout","New lines and sites reuse the playbook; AgentNexus brings the fleet together."),
  ("Operate","Kiln updates, evidence pack and support under one subscription — or hardware-as-a-service.")])}</div></section>
<section><div class="wrap">{shead("06","Where we are different","Built for outcomes, not programs.")}{disc([
  ("/floor","Founders who have worked on the floor","Every engagement is led by a pair with deep factory and OT experience: one person who speaks operations and OT security, and one engineer who audits and delivers — backed by founders with 20+ years each in OT and Physical AI.",["OT experience","site audit","delivery"]),
  ("/safety","Safety stays with you","AI never sits on the path that moves equipment. Low-consequence actions happen directly; anything safety-related is an alarm and a request your PLC, safety system and operator decide.",["Lane A","Lane B","no SIL claim"]),
  ("/sovereignty","Sovereign by default","Air-gapped by default, on hardware you own, with allow-listed connections. Nothing leaves the site unless you want it to.",["air-gapped","read-only","on-prem"]),
  ("/price","Priced per asset and kit","We price by monitored asset and domain kit — never per seat or per camera — and the pilot is credited toward production.",["per asset","per kit","creditable pilot"]),
  ("/platform","A platform, not a manifesto","AgentMesh runs today on owned AMD hardware next to the control system, AgentNexus extends it across sites, and both come to NVIDIA Jetson AGX Thor and DGX Spark.",["AgentMesh","AgentNexus","AMD · NVIDIA"]),
  ("/leadership","Founder-led vision that ships","Founders whose ambition matches the field's most visionary — measured by what reaches production, on your terms.",["founder-led","ships"])])}</div></section>
<section><div class="wrap">{shead("07","The market is bifurcated","We are the third path.")}{disc([
  ("/transformation","The transformation play","Global integrators rebuild the entire digital estate. Valuable — but multi-year, multi-million, and slow to first value.",["multi-year","whole-estate"]),
  ("/vision","The vision play","Vision-led firms sell the destination. Inspiring — but often a roadmap without a delivery engine.",["inspiring","no engine"]),
  ("/unovie","The Unovie play","Founder-level vision married to an Austin engineering studio that ships: a working, vertical, owned system in production in a quarter.",["vision + execution","owned","one quarter"])])}</div></section>
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Austin, Texas</div>
  <h2 style="margin-top:16px">Bring us an asset. <span class="serif" style="color:var(--accent)">We'll be on your floor.</span></h2>
  <p class="lead">On site across Texas — from the I-35 corridor to the Gulf Coast. Fixed scope, fixed cost, full responsibility, on hardware you own.</p>
  <div class="cta"><a class="btn btn-acc" href="index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
    <a class="btn btn-gh" href="about.html" data-cursor>About the studio</a></div>
</div></div></section>
{FOOTER("")}'''
open(f"{ROOT}/why-unovie.html","w",encoding="utf-8").write(why)

# ---- sitemap.xml + robots.txt (Google indexing) ----
SITE="https://unovie.ai"
LASTMOD="2026-11-14"   # bump when content materially changes (kept fixed for idempotent builds)
def _u(path):  # path relative to site root; "" = homepage
    return SITE + "/" + path
_pages=["", "about.html", "why-unovie.html", "contact.html", "resources/agentnexus-architecture.html",
        "resources/edge-ai-models.html", "resources/edge-ai-whitepaper.html", "gpu-edgegateway-whitepaper.html", "ai-soc-modernization-whitepaper.html"]
_pages += [f"solutions/{s[0]}.html" for s in SOL]
_pages += [f"platform/{s[0]}.html" for s in PLATP]
_pages += ["device-platform.html"]
_pages += ["resources/medsdlc-html/"+p for p in ("index.html","exec-brief.html","01-requirements.html","02-maturity-model.html","03-reference-architecture.html","04-model-strategy-and-finetuning.html","05-evaluation-and-validation.html","06-agentic-workflows.html","07-security-and-compliance.html","08-token-and-gpu-economics.html","09-adoption-roadmap.html","scorecard.html","diagrams.html")]
def _prio(p):
    if p=="": return "1.0"
    if p=="why-unovie.html": return "0.8"
    if p=="device-platform.html" or p.startswith(("solutions/","platform/")): return "0.9"
    if p.startswith("resources/") or p in ("gpu-edgegateway-whitepaper.html","ai-soc-modernization-whitepaper.html"): return "0.6"
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
    return ("home" if p=="" else "solution" if p.startswith("solutions/") else "platform" if p.startswith("platform/") else "device" if p=="device-platform.html"
            else "resource" if p.startswith("resources/") or p in ("gpu-edgegateway-whitepaper.html","ai-soc-modernization-whitepaper.html") else "company")
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
def _name(h): return re.sub(r'\s+',' ',_strip(re.sub(r'<span[^>]*>(.*?)</span>',r'\1',h))).strip()
_IND=["smart-factory-floor","batch-optimization","osha-compliance","smart-warehouse","maritime-digital-twin","remote-expertise"]
_solmap={s[0]:s for s in SOL}
_sol="\n".join(f"- [{_name(_solmap[k][2])}]({_u('solutions/'+k+'.html')}): {_firstsent(_solmap[k][3])}" for k in _IND if k in _solmap)
_oth="\n".join(f"- [{_name(s[2])}]({_u('solutions/'+s[0]+'.html')}): {_firstsent(s[3])}" for s in SOL if s[0] not in _IND)
open(f"{ROOT}/llms.txt","w",encoding="utf-8").write(f"""# Unovie.AI

> Sovereign AI engine for the physical frontier — the Agentic Physical AI platform for Industry 4.0. Unovie designs, builds and operates custom Edge-AI Agentic Systems for next-generation manufacturing — sensor-dense, AI-heavy, robot-heavy factories in battery, chips, space, robotics and autonomous systems, defense and advanced energy — fixed scope, fixed cost, on AMD or NVIDIA hardware the customer owns. The platform has two systems: AgentMesh puts AI on every signal a next-generation line produces — robots, vision, sensors and test rigs — at the machine; AgentNexus runs AI agents across every site. Air-gapped by default and designed against NIST SP 800-53 and the NIST AI RMF; safety decisions stay with the customer's safety PLC, cell controller and operators.

Unovie is a four-year-old, engineering-first, AI-native company built for Physical AI, headquartered in Austin, Texas and serving customers nationally. Each founder brings 20+ years in OT and Physical AI (control systems, robot cells, factory networks, safety systems and low-latency edge systems). Its offering is written as "custom Edge-AI Agentic Systems". Figures on this site marked "target" or "estimate" are design targets, not measurements.

## About Unovie
- Engineering first: founders with 20+ years each designing, building and running OT and Physical AI systems; integration with robot controllers, safety PLCs, vision systems, test rigs and industrial protocols such as OPC UA, EtherCAT and Modbus; a 30 ms decision budget at the machine (target).
- AI native: agents, small specialised models, Vector Memory and a test-gated improvement loop (the Kiln) are built into the platform from the start, not added to legacy software.
- Built for Physical AI ("from bits to atoms"): Perceive (signals read where they start) → Reason (plant history, manuals, failures, with evidence) → Act (low-consequence actions directly; safety-related actions as requests the customer's systems decide) → Adapt (tested, signed, reversible improvements; the base model never drifts).
- Location: headquartered in Austin, Texas; serves customers nationally, with on-site presence across Texas.
- Customers: next-generation, sensor-dense, AI-heavy and robot-heavy manufacturers — battery and energy storage (cell, module and pack lines; storage fleets); chip fabs and their gas, chemical and parts suppliers; space and aerospace (vehicle and satellite lines, test stands); robotics and autonomous systems (robot-dense lines; robots, drones and vessels in the field); defense and dual-use manufacturing (new shipyards and autonomous-vessel yards); advanced energy and nuclear (non-safety roles only: construction, balance of plant, security).
- Why these customers: data that cannot leave the site (export-controlled and defense data, chip and product IP), dense sensors and robots that produce more data than people can watch, and audits that need evidence. Unovie is air-gapped by default and every decision is written to a signed Evidence Log; output is advisory wherever certification or airworthiness rules apply.
- Safety boundary: a language model is never on the path that moves equipment; Unovie does not act as a safety instrumented function and makes no SIL claim.

## How Unovie engages
1. Site audit: an engineer reviews sensors, robots, network and control systems before a contract is signed.
2. Paid pilot (6 weeks): one domain kit on the customer's own data, a baseline ROI view and a measured latency report; credited toward a production site.
3. Production site (about one quarter from pilot): an AgentMesh Sovereign Pod integrated with sensors, cell controllers, the safety PLC, MES/QMS and the work-order system.
4. Fleet rollout: new lines and sites reuse the playbook; AgentNexus brings the fleet together.
5. Operate: Kiln updates, the governed-AI evidence pack (mapped to NIST SP 800-53, the NIST AI RMF and IEC 62443) and support under one subscription, or hardware-as-a-service.
Pricing is per monitored asset and domain kit, never per seat or per camera.

## Cloud-native architecture
- CNCF-conformant: AgentMesh pods and the AgentNexus rack run a CNCF Certified Kubernetes distribution, with CNCF projects for service networking, replicated storage and observability. (Conformance refers to the Kubernetes distribution; Unovie does not claim a CNCF certification for its own product.)
- Microservices native: each capability (Unovie Gateway, Signal Encoders, Vector Memory, Decision Engine, Decision Models, Reasoning Model, Model Router, Agent Runtime, Evidence Log, Kiln) is its own containerised service with typed gRPC contracts; services scale, update and roll back independently.
- Declarative and repeatable (pinned images, declarative manifests, versioned and signed playbooks and skill adapters); secure defaults (default-deny network policy per namespace, encrypted secrets, sandboxed agents). Failover is decided by the Mesh Arbiter, not the Kubernetes scheduler.

## Security and compliance
- Born with security compliance in mind: the platform is designed against NIST SP 800-53 Rev. 5 control families (as tailored for OT by the NIST SP 800-82 Rev. 3 OT overlay) and the NIST AI Risk Management Framework, with the Generative AI Profile (NIST AI 600-1) guiding the Unovie Reasoning Model.
- Mapping: air-gapped by default and one-way outputs (SC, AC); sealed agent sandboxes and least privilege (AC, IA); signed append-only Evidence Log (AU); test-gated, signed, reversible changes via the Kiln (CM, SI); owned hardware and open-weight models with known provenance (SR); failover (CP). AI RMF: Govern (Evidence Log, sign-off), Map (each domain kit declares context and lane), Measure (held-out tests, measured latency), Manage (lanes, trials, rollback).
- The evidence pack is material for customers' own programs — SP 800-171/CMMC, IEC 62443, SEMI E187, aerospace quality records, battery-site safety reviews. Unovie does not claim certification; compliance is determined by the customer's assessor.

## Platform
- [AgentMesh]({_u('platform/agentmesh.html')}): Agentic Physical AI at the machine for next-generation factories (battery lines, chip fabs and suppliers, space hardware, robotics and autonomous systems). A Sovereign Pod (four AMD Ryzen AI Max+ 395 servers in 3U, with 2 × 10GbE networking and NVMe storage) on the factory network connects to robot controllers, vision systems (DeepVision on NVIDIA Jetson AGX Thor), sensors, test rigs and the factory network; decides inside a 30 ms budget (target); acts directly only on low-consequence outputs (Lane A, e.g. diverting a part to rework) and sends anything safety-related as an alarm and a request to the safety PLC, cell controller and operators (Lane B). Results go to MES, QMS, test-data and work-order systems. Also works with existing control systems. Every decision is written to a signed Evidence Log; air-gapped by default; the language model is never on the path that moves equipment.
- [AgentNexus]({_u('platform/agentnexus.html')}): AI agents across every site a next-generation manufacturer runs — gigafactories and storage fleets, factories and test stands, fabs and supplier plants, robot fleets, shipyards and dual-use programs. One 42U rack (twelve shelves of four servers, 48 in total) runs thousands of agents in sealed sandboxes, connects to every AgentMesh pod, and turns findings into cross-site analysis, maintenance plans, non-conformance reports, quality records and work orders (drafted in English or Spanish) within a 0.5 s response budget (target). It learns from production through the Kiln (train, test on unseen cases, trial, switch on) and never moves equipment. Runs in the customer's own enclave.

## Core concepts
- Sovereign Pod: the AgentMesh appliance — four servers in 3U with 2 × 10GbE networking and NVMe storage, on the factory network, air-gapped by default.
- Lane A: low-consequence outputs AgentMesh may act on directly (reject gate, diverter, IT-side quarantine).
- Lane B: anything touching process safety — AgentMesh raises an alarm and writes a request; the PLC, safety system and operator decide.
- Evidence Log: append-only, signed record of every decision, action, request and change.
- Unovie Gateway: connection to robot controllers, vision systems, sensors, data-acquisition boxes, test rigs and the factory network, with allow-listed protocols and an audit trail.
- Signal Encoders: turn windows of raw signal into compact fingerprints.
- Vector Memory: finds similar past events ("have we seen this before, and was it bad?").
- Unovie Decision Engine: applies rules and small decision models and picks the lane.
- Unovie Decision Models: small models that answer typed questions (choice, yes/no, score) with a probability for each answer.
- Unovie Reasoning Model: the open-weight language model that explains events, finds root causes and drafts work orders; never in the path that moves equipment.
- Skill adapters: small add-ons that specialise the Unovie Reasoning Model for one job, swapped in without a restart.
- Kiln: the improvement loop — trains, tests on unseen cases, trials on live traffic and promotes changes only if they beat what is running.
- Unovie Agent Runtime: runs each AgentNexus agent in a sealed sandbox, sleeps idle agents and wakes them on demand.
- Unovie Model Router: picks the model and skill adapter for every request.
- Mesh Arbiter: failover service that moves work when a server or shelf stops.
- Domain kit: a packaged domain (connections, fingerprints, rules, playbook, reports) for one class of asset.
- Operator HMI: the screen each AgentMesh pod provides — live asset signals, the decision and its lane, similar past events, the drafted work order and the nightly Kiln evidence pack. AgentNexus has a fleet HMI showing findings across sites, agents at work, model routing, plans awaiting sign-off and skill adapters in trial.

## Agentic jobs
Packaged jobs for next-generation lines (each a domain kit with its connections, fingerprints, rules, playbook and reports), deployed in weeks:
- Robot & Motion Health: joint, servo and gearbox drift caught before it scraps parts or stops the line; Lane A divert in under 30 ms (target).
- Vision Quality Inspection: DeepVision at the cell, fused with process signals, on NVIDIA Jetson AGX Thor.
- Battery Line & Storage Safety: weld and formation signatures in line; thermal-runaway warning on storage fleets (alarm only).
- Fab Utilities Watch: pumps, chillers, scrubbers and gas systems at the fab and its suppliers; Lane B requests, facilities decide.
- Test Campaign Monitor: flags to the test conductor during a run, beside the qualified test system; post-test report drafted.
- Quality Records & NCRs: agents draft non-conformance reports and quality records for sign-off, in English or Spanish.
- How to start: "Pilot on your line" — a 6-week paid pilot on the customer's own line, credited toward production ({_u('index.html')}#contact).

## Domain kits
- Robot & Motion Health: joint, servo, gearbox and spindle health on robots, motion axes and conveyors (joint current, torque, vibration).
- Battery Line & Storage Safety: weld, formation and aging signatures in line; thermal-runaway precursors on storage fleets, alarmed into the fire panel.
- Electrical Health: drives, tool power, inverters and switchgear (power quality, partial discharge).
- Vision Quality Inspection: DeepVision defect checks on cells, welds, wafers and composite parts, fused with process signals.
- Test Campaign Monitor: anomaly flags to the test conductor during test-stand runs and drafted post-test reports (pressure, strain, acoustics).
- Factory Network Watch: unauthorized writes and unusual commands on the factory network, with audit evidence.

## Hardware
Each option runs the same Unovie platform and serves one Industry 4.0 purpose.
- [AMD Ryzen AI Max+ 395]({_u('device-platform.html')}#ryzen-ai-max-395): sovereign factory intelligence. The reference server for the AgentMesh Sovereign Pod (4 servers, 3U, 2 × 10GbE networking, NVMe storage) and the AgentNexus rack (48 servers, 42U); 64 GB per server in Unovie's build. Status: runs today.
- [NVIDIA Jetson AGX Thor]({_u('device-platform.html')}#agx-thor): robotics and DeepVision for fabs — wafer, die and panel inspection, robot-cell quality, wafer handling and mobile robots, at the tool. Status: available on, per project.
- [NVIDIA DGX Spark]({_u('device-platform.html')}#dgx-spark): the AI engineering lab — skill adapter training, test-stand analytics, digital-twin experiments and a site-level AgentNexus. Status: available on, per project.
- [Qualcomm QCS6490]({_u('device-platform.html')}#qcs6490): mobile and remote assets — mobile robots, AGVs, drone docks and battery containers, feeding the nearest AgentMesh pod.

## Resources
- [AgentNexus — Architecture Overview]({_u('resources/agentnexus-architecture.html')}): how AgentNexus is organised, what happens step by step, how data is kept safe and what happens when something breaks — for architects and business leaders.
- [Edge AI Models — Field Guide]({_u('resources/edge-ai-models.html')}): a 25-chapter architect's eBook on how edge-AI models actually learn.
- [Frozen-Base Doctrine — Whitepaper]({_u('resources/edge-ai-whitepaper.html')}): adapting custom models on the edge without retraining.
- [Edge-Native Inference Gateway — Whitepaper]({_u('gpu-edgegateway-whitepaper.html')}): turning unpredictable, metered AI opex into fixed, predictable cost for the industrial edge.
- [AI SOC Modernization — Whitepaper]({_u('ai-soc-modernization-whitepaper.html')}): an edge-native, identity-driven security architecture for distributed IT/OT.
- [Agentic SDLC for Regulated MedTech]({_u('resources/medsdlc-html/index.html')}): a self-hosted, validated, agent-native software development lifecycle for FDA / IEC 62304 medical-device engineering.

## Company
- [Why Unovie]({_u('why-unovie.html')}): a young company with veteran founders — each founder brings 20+ years in OT and Physical AI, and the company has spent four years building its sovereign AI platform for next-generation manufacturing. Headquartered in Austin, Texas, serving customers nationally. Site audit, a 6-week paid pilot on the customer's own line, and production in a quarter.
- [About]({_u('about.html')}): an AI-engineering studio for Industry 4.0, built in Austin, Texas.
- [Contact]({_u('contact.html')}): start a project.

## Machine-readable
- [Full content (llms-full.txt)]({SITE}/llms-full.txt): the entire site as one markdown document for direct LLM/agent consumption.
- [Vector index (JSON)]({SITE}/agents/index.json): embeddable, chunked content records for RAG.
- [Sitemap]({SITE}/sitemap.xml)
""")

print(f"built: index + {len(SOL)} solutions + {len(PLATP)} platform + device-platform({len(DEVP)} tabs) + about + assets + sitemap({len(_pages)}) + agents-index({len(records)} chunks) + llms.txt + llms-full.txt")

# ----- cache-busting: stamp assets/site.{css,js} with a content hash on every page -----
import hashlib as _hl, glob as _gl
def _asset_v(rel): return _hl.md5(open(f"{ROOT}/{rel}","rb").read()).hexdigest()[:10]
_AV={"assets/site.css":_asset_v("assets/site.css"),"assets/site.js":_asset_v("assets/site.js")}
for _f in _gl.glob(f"{ROOT}/**/*.html",recursive=True):
    if "/resources/medsdlc-html/" in _f: continue
    _s=open(_f,encoding="utf-8").read()
    _n=re.sub(r'(assets/site\.(?:css|js))(?:\?v=[0-9a-f]+)?"',lambda m:f'{m.group(1)}?v={_AV[m.group(1)]}"',_s)
    if _n!=_s: open(_f,"w",encoding="utf-8").write(_n)
print("cache-bust:",_AV)
