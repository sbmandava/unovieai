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
if idx!=open(f"{ROOT}/index.html",encoding="utf-8").read():
    open(f"{ROOT}/index.html","w",encoding="utf-8").write(idx)

# ---- 3) shared chrome (base = "" for root, "../" for subdirs) ----
# Inline theme bootstrap (runs in <head>, before first paint → no flash).
# Default: light on desktop, dark on mobile/touch. A saved toggle (uvTheme) always wins.
# The `data-theme-init` attribute keeps the homepage-slimming regex (bare <script>) from matching it.
THEMEINIT = "<script data-theme-init>(function(){var m=false;try{m=matchMedia('(max-width:768px), (hover:none) and (pointer:coarse)').matches;}catch(e){}var s=null;try{s=m?sessionStorage.getItem('uvTheme'):localStorage.getItem('uvTheme');}catch(e){}document.documentElement.setAttribute('data-theme',(s==='light'||s==='dark')?s:'dark');})();</script>"

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
<link rel="icon" href="{base}assets/favicon.ico?v=2" sizes="any"><link rel="icon" type="image/png" href="{base}assets/favicon.png?v=2"><link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png?v=2">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/site.css">{THEMEINIT}</head><body>
<div class="grain"></div><div class="cur"></div><div class="cur-r"></div>'''

def NAV(base):
    h=base+"index.html"
    return f'''<header class="nav"><div class="wrap"><div class="row">
  <a class="brand" href="{h}"><img class="logo" src="{base}assets/images/unovie-logo.png" alt="Unovie.AI"></a>
  <nav class="navlinks">
    <div class="drop"><button data-cursor>Sectors ▾</button><div class="menu">
      <a href="{base}sectors/battery.html"><span class="ic">01</span><span><span class="t">Battery &amp; energy storage</span><br><span class="s">Cell lines and storage sites</span></span></a>
      <a href="{base}sectors/fabs.html"><span class="ic">02</span><span><span class="t">Chip fabs &amp; suppliers</span><br><span class="s">Fab utilities and supplier plants</span></span></a>
      <a href="{base}sectors/space.html"><span class="ic">03</span><span><span class="t">Space &amp; aerospace</span><br><span class="s">Test stands and vehicle lines</span></span></a>
      <a href="{base}sectors/robotics.html"><span class="ic">04</span><span><span class="t">Robotics, drones &amp; autonomy</span><br><span class="s">Robot cells, drones and vessels</span></span></a>
      <a href="{base}sectors/defense.html"><span class="ic">05</span><span><span class="t">Defense &amp; dual-use</span><br><span class="s">Shipyards and dual-use factories</span></span></a>
      <a href="{base}sectors/energy.html"><span class="ic">06</span><span><span class="t">Advanced energy &amp; nuclear</span><br><span class="s">Balance of plant, non-safety only</span></span></a>
    </div></div>
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
      <a href="{base}resources/edge-ai-models.html" target="_blank" rel="noopener"><span class="ic">01</span><span><span class="t">Edge AI Models: Field Guide (summary)</span><br><span class="s">Summary; full guide on request</span></span></a>
      <a href="{base}resources/edge-ai-whitepaper.html" target="_blank" rel="noopener"><span class="ic">02</span><span><span class="t">Training Without Retraining (summary)</span><br><span class="s">Custom models on the edge</span></span></a>
      <a href="{base}gpu-edgegateway-whitepaper.html" target="_blank" rel="noopener"><span class="ic">03</span><span><span class="t">Edge-Native Economics: Whitepaper</span><br><span class="s">Predictable AI cost at the edge</span></span></a>
      <a href="{base}ai-soc-modernization-whitepaper.html" target="_blank" rel="noopener"><span class="ic">04</span><span><span class="t">AI SOC Modernization: Whitepaper</span><br><span class="s">Security for IT and OT networks</span></span></a>
    </div></div>
    <div class="drop"><button data-cursor>Why Unovie ▾</button><div class="menu">
      <a href="{base}why-unovie.html"><span class="ic">01</span><span><span class="t">Why Unovie</span><br><span class="s">Veteran founders, built in Austin</span></span></a>
      <div class="msub">Proof &amp; answers</div>
      <a href="{base}resources/case-study-device-certification.html"><span class="ic">02</span><span><span class="t">Case study: AI device certification</span><br><span class="s">12 months, 16 boxes per stream, air-gapped</span></span></a>
      <a href="{base}resources/case-study-vision-edge.html"><span class="ic">03</span><span><span class="t">Case study: camera AI in a chip fab</span><br><span class="s">1,000 camera feeds, decided on site</span></span></a>
      <a href="{base}faq.html"><span class="ic">04</span><span><span class="t">FAQ for buyers</span><br><span class="s">Data, safety, hardware, pilot cost</span></span></a>
    </div></div>
  </nav>
  <a class="navcta" href="{h}#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
  <button class="burger" id="burger" aria-label="Menu">☰</button>
</div></div></header>
<div class="mobile" id="mobile">
  <a href="{h}#deeptech"><span class="mono">01</span><br>Sectors</a>
  <a href="{base}platform/agentmesh.html"><span class="mono">02</span><br>AgentMesh</a>
  <a href="{base}platform/agentnexus.html"><span class="mono">03</span><br>AgentNexus</a>
  <a href="{base}device-platform.html"><span class="mono">04</span><br>Hardware</a>
  <a href="{base}why-unovie.html"><span class="mono">05</span><br>Why Unovie</a>
  <a href="{base}resources/case-study-device-certification.html"><span class="mono">06</span><br>Case study</a>
  <a href="{base}faq.html"><span class="mono">07</span><br>FAQ</a>
  <a href="{h}#contact" style="color:var(--accent)"><span class="mono">08</span><br>Pilot on your line →</a>
</div>'''

def FOOTER(base):
    h=base+"index.html"
    return f'''<footer><div class="wrap"><div class="fgrid">
  <div class="fcol fbrand"><a class="brand" href="{h}"><img class="logo" src="{base}assets/images/unovie-logo.png" alt="Unovie.AI"></a>
    <p>Physical AI for deep-tech factories. Built in Austin, Texas.</p></div>
  <div class="fcol"><h4>Platform</h4>
    <a href="{base}platform/agentmesh.html">AgentMesh</a><a href="{base}platform/agentnexus.html">AgentNexus</a><a href="{base}device-platform.html">Hardware</a></div>
  <div class="fcol"><h4>Sectors</h4>
    <a href="{base}sectors/battery.html">Battery</a><a href="{base}sectors/fabs.html">Chip fabs</a><a href="{base}sectors/space.html">Space</a><a href="{base}sectors/robotics.html">Robotics &amp; autonomy</a><a href="{base}sectors/defense.html">Defense</a><a href="{base}sectors/energy.html">Advanced energy</a></div>
  <div class="fcol"><h4>Company</h4>
    <a href="{base}about.html">About</a><a href="{base}why-unovie.html">Why Unovie</a><a href="{base}resources/case-study-device-certification.html">Case study</a><a href="{base}faq.html">FAQ</a><a href="{base}contact.html">Contact</a><a href="https://www.linkedin.com/company/unovie/" target="_blank" rel="noopener">LinkedIn</a></div>
  <div class="fcol"><h4>Research</h4>
    <a href="{base}resources/edge-ai-models.html" target="_blank">Edge AI field guide</a><a href="{base}resources/edge-ai-whitepaper.html" target="_blank">Training without retraining</a><a href="{base}gpu-edgegateway-whitepaper.html" target="_blank">Edge economics</a><a href="{base}ai-soc-modernization-whitepaper.html" target="_blank">AI SOC</a></div>
</div><div class="fbot"><span>© 2026 Unovie</span><span>Runs on AMD and NVIDIA · works with your PLCs, MES and safety systems</span></div></div></footer>
<script src="{base}assets/site.js"></script></body></html>'''

def metrics(items):  # list of (value_html, label)
    cells="".join(f'<div class="ktile rv"><div class="big">{v}</div><div class="lab">{l}</div></div>' for v,l in items)
    return f'<div class="kgrid">{cells}</div>'
def disc(items):     # list of (ix, title, desc, [chips])
    out=[]
    for i,(ix,t,d,ch) in enumerate(items):
        g='var(--steel)' if i%2 else 'var(--accent)'
        chips="".join(f'<span class="chip">{c}</span>' for c in ch)
        out.append(f'<div class="dcard rv"><div class="glow" style="background:{g}"></div>{'' if str(ix).startswith('/') else f'<div class="ix">{ix}</div>'}<h3>{t}</h3><p>{d}</p><div class="spec">{chips}</div></div>')
    return f'<div class="disc{" d3" if len(out)==3 else ""}">{"".join(out)}</div>'
def steps(items):    # list of (title, desc)
    out=[f'<div class="stage rv"><div class="ix">{i+1:02d}</div><h3>{t}</h3><p>{d}</p></div>' for i,(t,d) in enumerate(items)]
    return f'<div class="pipe" style="grid-template-columns:repeat(auto-fit,minmax(170px,1fr))">{"".join(out)}</div>'
def shead(num,label,title,lead=""):
    L=f'<p class="lead rv">{lead}</p>' if lead else ""
    return f'<div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>{num} · {label}</div><h2 class="rv">{title}</h2></div>{L}</div>'

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
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER(base)}'''
    open(f"{full}/{slug}.html","w",encoding="utf-8").write(head+body)

B="../"
# ----- SOLUTIONS -----
SOL=[
 ("smart-factory-floor","Manufacturing","Smart Factory <span class='serif' style='color:var(--accent)'>Floor</span>",
  "Vision-driven inspection and quality control that runs on the line, in real time, on Unovie's custom-built hardware accelerators, engineered for agentic performance, low latency and high availability — no cloud round-trip, no data egress.",
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
# Public tier only (brand/public-disclosure.md, 16 Nov 2026): outcomes, promises and proof.
# How the system works is not published on this site.
PLATP=[("agentmesh",),("agentnexus",)]   # slugs, used by the sitemap
A="<span class='serif' style='color:var(--accent)'>"; T="<span class='serif' style='color:var(--steel)'>"; E="</span>"
NDA_LINE='<p class="lead rv" style="font-size:15px;margin-top:16px">Want to see how it works? Our engineers can walk you through it. <a href="/contact.html" style="color:var(--accent)">Talk to our engineers →</a></p>'

ICO={
 "rot":'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 4v3M12 17v3M4 12h3M17 12h3"/></svg>',
 "bat":'<svg viewBox="0 0 24 24"><rect x="3" y="7" width="16" height="10" rx="2"/><path d="M21 10v4M7 10v4M11 10v4"/></svg>',
 "ele":'<svg viewBox="0 0 24 24"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
 "leak":'<svg viewBox="0 0 24 24"><path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/></svg>',
 "test":'<svg viewBox="0 0 24 24"><path d="M3 17l5-6 4 4 4-7 5 9"/><path d="M3 21h18"/></svg>',
 "ot":'<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><path d="M7 7h.01M7 17h.01"/></svg>',
 "eye":'<svg viewBox="0 0 24 24"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
}

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
def briefcard(product, glow="var(--accent)"):
    return (f'<div class="disc" style="margin-top:22px"><a class="dcard rv" href="/contact.html" data-cursor style="text-decoration:none">'
            f'<div class="glow" style="background:{glow}"></div><h3>Want the {product} architecture?</h3>'
            '<p>Our engineers can walk you through it. Talk to our engineers.</p>'
            '<div class="spec"><span class="chip">talk to our engineers</span></div></a></div>')


# ===================== outcome diagrams (public tier) =====================
import random as _rnd

def _flow(d, cls="fl-a", dur=2.4, begin=0.0, rev=False, r=3.2):
    kp = ' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if rev else ''
    return f'<circle r="{r}" cx="-50" class="{cls}"><animateMotion dur="{dur}s" begin="-{begin:.2f}s" repeatCount="indefinite"{kp} path="{d}"/></circle>'

def _svg_mesh_v2():
    o = ['<svg class="axviz ax2" viewBox="0 0 1000 500" role="img" aria-label="AgentMesh at the machine: robot, vision, vibration, electrical, battery and test-rig signals go into AgentMesh on the factory network, which decides within 30 milliseconds (target). It acts directly on low-consequence outputs, sends anything safety-related to your PLC and operators as an alarm and a request, drafts the record and writes every decision to a signed Evidence Log.">',
         '<defs><marker id="axh3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>',
         '<text x="20" y="24" class="l">SIGNALS</text><text x="300" y="24" class="l">AGENTMESH · AT THE MACHINE</text><text x="780" y="24" class="l">WHAT HAPPENS NEXT</text>']
    sig = [("Robot joints", "current · torque"), ("Vision", "DeepVision at the cell"), ("Vibration", "ultrasonic · bearings"),
           ("Electrical", "power quality · drives"), ("Battery", "weld · formation · off-gas"), ("Test rigs", "pressure · strain")]
    _rnd.seed(7)
    for n, (a, b) in enumerate(sig):
        y = 40 + n * 66
        o.append(f'<rect x="20" y="{y}" width="230" height="56" rx="9" class="bx"/><text x="32" y="{y+22}" class="t2">{a}</text><text x="32" y="{y+40}" class="s2">{b}</text>')
        pts = " ".join(f"{150+i*6.6:.1f},{y+17+_rnd.uniform(-6,6) if i%3 else y+17:.1f}" for i in range(15))
        o.append(f'<polyline points="{pts}" class="spark" style="animation-delay:-{n*0.35:.2f}s"/>')
        d = f"M250,{y+28} C278,{y+28} 274,{200 if n<3 else 240} 300,{200 if n<3 else 240}"
        o.append(f'<path d="{d}" class="lk-c"/>')
        o.append(_flow(d, "fl-a", 1.6, n*0.27, r=2.6))
    o.append('<rect x="300" y="40" width="390" height="390" rx="12" class="bx-a"/>')
    o.append('<text x="316" y="64" class="l2">DECIDES WITHIN 30 MS · TARGET</text>')
    o.append('<rect x="316" y="72" width="358" height="12" rx="6" class="bx"/><rect x="316" y="72" width="358" height="12" rx="6" class="budget"/>')
    o.append('<line x1="644" y1="66" x2="644" y2="90" class="tick"/><text x="640" y="100" class="xs" text-anchor="end">30 MS</text>')
    stages = [("Reads every signal", "read-only, on your factory network"),
              ("Checks your plant's history", "has this happened before, and was it bad?"),
              ("Decides", "act, or ask your control system"),
              ("Explains", "names the likely cause, drafts the record"),
              ("Records", "every decision, signed")]
    for n, (a, b) in enumerate(stages):
        y = 112 + n * 62
        o.append(f'<rect x="316" y="{y}" width="358" height="50" rx="8" class="bx ly"/><text x="330" y="{y+21}" class="t2">{a}</text><text x="330" y="{y+38}" class="s2">{b}</text>')
        if n < 4:
            o.append(f'<path d="M495,{y+50} V{y+62}" class="lk-o" marker-end="url(#axh3)"/>')
    outs = [("Acts directly", "reject gate · rework divert", 40, "oa"), ("Asks your PLC", "alarm + request · people decide", 140, "ob"),
            ("Drafted records", "NCRs · work orders to MES, QMS", 240, ""), ("Evidence Log", "signed record of every decision", 340, "")]
    for a, b, y, c in outs:
        o.append(f'<rect x="780" y="{y}" width="200" height="74" rx="10" class="bx {c}"/><text x="794" y="{y+30}" class="t2">{a}</text><text x="794" y="{y+50}" class="s2">{b}</text>')
    paths = [("M674,299 C730,299 720,77 778,77", "fl-g"), ("M674,299 C730,299 720,177 778,177", "fl-o"), ("M674,361 C730,361 730,277 778,277", "fl-a")]
    for d, c in paths:
        o.append(f'<path d="{d}" class="lk-o" marker-end="url(#axh3)"/>')
        o.append(_flow(d, c, 1.8, 0.4 if c == "fl-o" else 0))
    o.append('<path d="M674,423 C730,423 740,377 778,377" class="lk-c" marker-end="url(#axh3)"/>')
    o.append(_flow("M674,423 C730,423 740,377 778,377", "fl-s", 2.6))
    o.append('<rect x="20" y="452" width="960" height="30" rx="15" class="bx-d"/><text x="500" y="471" class="l" text-anchor="middle">A LANGUAGE MODEL IS NEVER ON THE PATH THAT MOVES EQUIPMENT · EVERY DECISION IS SIGNED</text>')
    o.append('</svg>')
    return "".join(o)

def _svg_nexus_v2():
    o = ['<svg class="axviz ax2" viewBox="0 0 1000 470" role="img" aria-label="AgentNexus across sites: AgentMesh pods at cell lines, fab bays, test stands, shipyards and storage fleets send findings over encrypted links to one AgentNexus rack in your enclave. Agents compare sites, draft plans, NCRs and work orders, and a named person approves them before they reach MES, QMS, ERP and work-order systems. It connects out only through one gate you control. AgentNexus never moves equipment.">',
         '<defs><marker id="axh4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>',
         '<text x="20" y="24" class="l">SITES · AGENTMESH PODS</text><text x="290" y="24" class="l">AGENTNEXUS · ONE RACK · YOUR ENCLAVE</text><text x="790" y="24" class="l">BUSINESS</text>']
    sites = [("Cell Line 2", "battery"), ("Fab Bay 3", "chip fab"), ("Test Stand 2", "space"), ("Yard 1", "shipyard"), ("Storage fleet", "14 sites")]
    for n, (a, b) in enumerate(sites):
        y = 40 + n * 74
        o.append(f'<rect x="20" y="{y}" width="200" height="58" rx="9" class="bx"/><text x="34" y="{y+24}" class="t2">{a}</text><text x="34" y="{y+42}" class="s2">{b} · decides locally</text><circle cx="206" cy="{y+14}" r="2.6" class="led" style="animation-delay:{n*.3}s"/>')
        d = f"M220,{y+29} C255,{y+29} 260,{150+n*40} 290,{150+n*40}"
        o.append(f'<path d="{d}" class="lk-c"/>')
        o.append(_flow(d, "fl-a", 2.2, n*0.45))
    o.append('<text x="20" y="430" class="s2">… and every other site, over encrypted links</text>')
    o.append('<rect x="290" y="40" width="470" height="380" rx="12" class="bx-a"/>')
    o.append('<text x="306" y="66" class="l2">AGENTS AT WORK ACROSS YOUR SITES</text>')
    _rnd.seed(3)
    for r in range(4):
        for c in range(34):
            awake = _rnd.random() < 0.18
            o.append(f'<circle cx="{310+c*12.8:.1f}" cy="{82+r*12}" r="3.2" class="ag {"aw" if awake else ""}" style="animation-delay:-{_rnd.uniform(0,4):.2f}s"/>')
    o.append('<text x="306" y="146" class="s2">answers within 0.5 s (target)</text>')
    layers = [("Compares sites", "the same problem, seen somewhere else"), ("Drafts the paperwork", "maintenance plans, NCRs, quality records, work orders"),
              ("Waits for a person", "a named person approves every draft"), ("One gate out", "your ERP and approved AI models, logged")]
    for n, (a, b) in enumerate(layers):
        y = 162 + n * 62
        o.append(f'<rect x="306" y="{y}" width="438" height="50" rx="8" class="bx ly"/><text x="320" y="{y+21}" class="t2">{a}</text><text x="320" y="{y+38}" class="s2">{b}</text>')
    outs = [("MES · QMS", "quality records · NCRs", 40, ""), ("ERP · work orders", "SAP · NetSuite · Infor · Maximo", 130, ""), ("People", "engineers · planners · quality", 220, ""), ("Never moves", "equipment · advisory only", 330, "dash")]
    for a, b, y, c in outs:
        cls = "bx-d" if c else "bx"
        o.append(f'<rect x="790" y="{y}" width="190" height="64" rx="10" class="{cls}"/><text x="804" y="{y+27}" class="t2">{a}</text><text x="804" y="{y+45}" class="s2">{b}</text>')
        if not c:
            d = f"M760,230 C778,230 772,{y+32} 788,{y+32}"
            o.append(f'<path d="{d}" class="lk-o" marker-end="url(#axh4)"/>')
            o.append(_flow(d, "fl-a", 2.0, (y/90)*0.5))
    o.append('<rect x="20" y="440" width="960" height="24" rx="12" class="bx-d"/><text x="500" y="456" class="l" text-anchor="middle">RUNS IN YOUR ENCLAVE · A PERSON APPROVES EVERY DRAFT · NEVER MOVES EQUIPMENT</text>')
    o.append('</svg>')
    return "".join(o)

SVG_MESH = _svg_mesh_v2()
SVG_NEXUS = _svg_nexus_v2()
# =================== /diagrams ===================

def product_page(slug, cat, title_html, lead, pills, kpis, panel, sections, cta_lead, desc):
    head=HEAD("../", f"{re.sub('<[^>]+>','',title_html)} | Unovie.AI", desc)
    chips="".join(f'<span class="chip">{c}</span>' for c in pills)
    body=f'''{NGBG}{NAV("../")}
<section class="ph2"><div class="wrap">
  <div class="crumb rv"><a href="../index.html">Home</a><span class="sep">/</span><a href="../index.html#platform">Platform</a><span class="sep">/</span><span style="color:var(--fg-mut)">{re.sub('<[^>]+>','',title_html)}</span></div>
  <div class="grid">
    <div><h1 class="rv">{title_html}</h1><p class="lead rv">{lead}</p>
      <div class="cta rv"><a class="btn btn-acc" href="../index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a><a class="btn btn-gh" href="#how" data-cursor>See how it works</a></div></div>
    <div>{panel}</div>
  </div>
  {kpistrip(kpis)}
</div></section>
{sections}
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Let's build</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("../")}'''
    os.makedirs(f"{ROOT}/platform",exist_ok=True)
    open(f"{ROOT}/platform/{slug}.html","w",encoding="utf-8").write(head+body)

def _ctable(head, rows):
    h="".join(f"<th>{c}</th>" for c in head)
    r="".join("<tr>"+"".join(f"<td>{c}</td>" for c in row)+"</tr>" for row in rows)
    return f'<div class="ctwrap rv"><table class="ctable"><tr>{h}</tr>{r}</table></div>'
def S(num,label,title,body,lead="",id_=""):
    i=f' id="{id_}"' if id_ else ''
    return f'<section{i}><div class="wrap">{shead(num,label,title,lead)}{body}</div></section>'

A_="<span class='serif' style='color:var(--accent)'>"; T_="<span class='serif' style='color:var(--steel)'>"; E_="</span>"


def hmi_showcase(screens, lead):
    tabs="".join(f'<button class="tab{" active" if k==0 else ""}" data-tab="{sid}" role="tab" aria-selected="{"true" if k==0 else "false"}" data-cursor>{label}</button>' for k,(sid,label,img,cap) in enumerate(screens)) if len(screens)>1 else ""
    panels="".join(f'<div class="tpanel{" active" if k==0 else ""}" id="{sid}" role="tabpanel"><figure class="hmiframe"><div class="bezel"><a href="../assets/images/sketch/{img}.jpg" target="_blank" rel="noopener" title="Open full size"><img src="../assets/images/sketch/{img}.jpg" alt="Illustration: {cap}" loading="lazy" width="2400" height="1350"></a></div><div class="stand"></div><figcaption>{cap}</figcaption></figure></div>' for k,(sid,label,img,cap) in enumerate(screens))
    t=f'<div class="tabs hmitabs" role="tablist" aria-label="Operator HMI">{tabs}</div>' if tabs else ''
    return f'<p class="lead rv" style="margin-top:-6px">{lead}</p>{t}{panels}'
MESH_HMI = S("01","Operator screen","What your operators "+A_+"see."+E_, hmi_showcase([
   ("hmi-battery","Battery line · laser weld","portal-battery","Cell Line 2 · module laser weld 5 · part sent to rework"),
   ("hmi-fab","Fab utilities · dry pump","portal-fab","Fab utilities · sub-fab bay 3 · dry pump VP-3-14 · request to facilities"),
   ("hmi-test","Test stand · hot-fire run","portal-test","Engine test stand 2 · hot-fire run 117 · advisory to the test conductor"),
   ("hmi-line","Robotic assembly · weld cell","portal-assembly","Assembly line B · weld cell 3 · part rejected")],
   "Each AgentMesh pod comes with an operator screen. It shows the live signals, what AgentMesh decided, similar past events and the drafted work order, on one page."), id_="hmi")
NEXUS_HMI = S("01","Fleet screen","Your whole fleet "+T_+"on one screen."+E_, hmi_showcase([
   ("hmi-fleet","Fleet operations","portal-fleet","AgentNexus fleet screen · findings, agents at work and plans waiting for sign-off")],
   "Findings from every site, problems seen in more than one place, and the plans waiting for someone to sign."), id_="hmi")


MESH_NEXTGEN = S("02","Built in","Built into "+A_+"new production lines."+E_,
  disc([
   ("/robots","Robot cells","AgentMesh reads robot controllers and servo drives. It spots a drifting joint or gearbox before it scraps parts or stops the line.",["robot controllers","joint torque"]),
   ("/vision","Vision with context","DeepVision runs at the cell on NVIDIA Jetson AGX Thor. A defect is judged on the camera and the process signals for the same part.",["DeepVision","at the cell"]),
   ("/mes","Into the systems you use","Findings go to your MES, quality system and work-order system. Records arrive drafted, with the evidence attached.",["MES · QMS","work orders"]),
   ("/ramp","From the first line to the tenth","AgentMesh learns a line's normal behaviour during ramp-up. The same setup copies to every new line and site. It also works with the control systems you already have.",["ramp-up","new lines"])]),
"New factories are full of sensors, cameras and robots. They produce far more data than people can watch. AgentMesh is built in from day one, so every signal has something watching it.")

MESH_SECTIONS = (
  S("03","How it works","From signal to action, "+A_+"at the machine."+E_,
    f'<div class="axwrap rv">{SVG_MESH}</div>'
    + flow4([("Read","AgentMesh reads sensors, robots, cameras and network traffic. It only reads.","read-only"),
             ("Decide","It compares what it sees with your plant's history and your rules. It decides within 30 ms (target).","30 ms · target"),
             ("Act or ask","It acts on its own only where a wrong call is cheap and easy to undo. Anything else goes to your PLC and operators.","you stay in charge"),
             ("Record","Every decision goes into a signed Evidence Log, with the likely cause and a drafted work order.","Evidence Log")]),
    "AgentMesh sits in a compact pod on your factory network. The fast decisions stay at the machine.", "how")
  + S("04","The safety boundary","Two lanes. "+A_+"Your control system stays in charge."+E_,
    '<div class="lanes">'
    '<div class="lane a rv"><div class="tag" style="color:var(--accent)">Lane A</div><div class="big">Acts directly</div><p>Only where a wrong call costs little and is easy to undo.</p><ul><li><b>Reject gate</b>a part with a bad weld goes to the reject bin</li><li><b>Diverter</b>product goes to rework instead of shipping</li><li><b>IT quarantine</b>a suspicious device is cut off on the IT side</li></ul></div>'
    '<div class="lane b rv"><div class="tag" style="color:var(--steel)">Lane B</div><div class="big">Alarm and request</div><p>Anything that touches process safety. AgentMesh asks. People and safety systems decide.</p><ul><li><b>Alarm</b>raised on your existing alarm system</li><li><b>Request</b>sent to your PLC or safety system</li><li><b>Operator</b>sees the request and the evidence, and decides</li></ul></div>'
    '</div><div class="never rv"><b>Never:</b> AgentMesh does not write to valves or safety functions on its own. A language model is never on the path that moves equipment. We make no SIL claim. Every decision in either lane goes into the signed Evidence Log.</div>')
  + S("05","Limits","Every machine has limits. "+A_+"The pod enforces them."+E_,
    disc([
     ("/limits","Limits, enforced","Every device is described with its limits, and the pod enforces them. A language model cannot change them.",["enforced limits"]),
     ("/evidence","Evidence anyone can check","You can export the Evidence Log and check it on your own systems or your auditor's laptop. If one record is changed, the check fails.",["signed","tamper-evident"]),
     ("/drafts","Drafts only","The assistant that explains events and writes up records can read. It cannot move anything.",["read only","drafts"])]))
  + S("06","Sectors","Built for the factories "+A_+"being built now."+E_,
    '<div class="disc"><a class="dcard rv" href="../sectors/battery.html" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--accent)"></div><h3>Battery &amp; energy storage</h3><p>Weld and formation checks in line. Early warning of thermal runaway on storage sites, as an alarm.</p><span class="go">Sector page →</span></a><a class="dcard rv" href="../sectors/fabs.html" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><h3>Chip fabs &amp; suppliers</h3><p>Fab utilities and supplier plants, watched through ramp-up. IP stays on site.</p><span class="go">Sector page →</span></a><a class="dcard rv" href="../sectors/space.html" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--accent)"></div><h3>Space &amp; aerospace</h3><p>Test stands watched run by run. Quality records drafted.</p><span class="go">Sector page →</span></a><a class="dcard rv" href="../sectors/robotics.html" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><h3>Robotics, drones &amp; autonomy</h3><p>Joint and gearbox health at every cell. Fleet health for systems that run offline.</p><span class="go">Sector page →</span></a><a class="dcard rv" href="../sectors/defense.html" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--accent)"></div><h3>Defense &amp; dual-use</h3><p>Line and yard QA, machinery health and network watch, inside your enclave.</p><span class="go">Sector page →</span></a><a class="dcard rv" href="../sectors/energy.html" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><h3>Advanced energy &amp; nuclear</h3><p>Balance of plant and site networks. Never on safety systems.</p><span class="go">Sector page →</span></a></div>',
    "", "sectors")
  + S("07","Security","Built for "+A_+"strict security reviews."+E_,
    disc([
     ("/nist","Designed against NIST","AgentMesh is designed against NIST SP 800-53 and the NIST AI Risk Management Framework. Designed against, not certified. Your assessor decides compliance.",["NIST SP 800-53","NIST AI RMF"]),
     ("/evidence","Evidence for your assessor","Each site gets an evidence pack your team can use for SP 800-171 and CMMC, IEC 62443, fab equipment-security reviews and aerospace quality records.",["800-171 · CMMC","IEC 62443"]),
     ("/data","Data stays on site","AgentMesh is air-gapped. Export-controlled, defense and IP-sensitive data stays inside the boundary you already run. Nothing is shared back to us.",["air-gapped","your site"])])
    , "", "security")
  + S("08","Domain kits","Packaged for "+A_+"the equipment you run."+E_,
    kits([("rot","Robot &amp; Motion Health","Joint, servo, gearbox and spindle health on robots, axes and conveyors, with a drafted work order.","joint current · torque · vibration"),
          ("bat","Battery Line &amp; Storage Safety","Weld, formation and aging checks in line. Thermal-runaway warning on storage sites, as an alarm.","weld · cycler · off-gas"),
          ("ele","Electrical Health","Drives, tool power, inverters and switchgear. Early signs of arcing and insulation failure.","power quality · partial discharge"),
          ("eye","Vision Quality Inspection","DeepVision defect checks on cells, welds, wafers and composite parts.","vision · process signals"),
          ("test","Test Campaign Monitor","Flags to the test conductor during a run, and a drafted post-test report.","pressure · strain · acoustics"),
          ("ot","Factory Network Watch","Unauthorized writes and unusual commands on the factory network, with evidence for audits.","control traffic · alarms")])
    + '<div class="sensors">'
    + "".join(f'<figure class="rv"><img src="../assets/images/sketch/{f}.jpg" alt="Illustration: {c}" loading="lazy"><figcaption>{c}</figcaption></figure>' for f,c in [("sensors","Vibration and ultrasonic sensors"),("daq","High-speed signal capture"),("weld-clamp","Weld-current clamp"),("agx-thor","DeepVision at the cell")])
    + '</div><p class="illus rv" style="margin-top:10px">Generic hardware · illustrations</p>',
    "Each kit is one packaged job for one kind of equipment. A pod can run several.")
  + S("09","Runs on","Unovie's custom-built "+A_+"AMD or NVIDIA hardware."+E_,
    hwrow([("sketch/sovereign-pod","ryzen-ai-max-395","Runs today",True,"AMD Ryzen AI Max+ 395","The Sovereign Pod: a compact 3U pod at the line, quiet enough for the factory floor."),
           ("sketch/agx-thor","agx-thor","Available on",False,"NVIDIA Jetson AGX Thor","Robotics and DeepVision inside the tool or the robot cell."),
           ("sketch/dgx-spark","dgx-spark","Available on",False,"NVIDIA DGX Spark","The AI engineering lab, and a one-unit AgentMesh for a pilot.")])
    ,
    "Same kits, same lanes and the same Evidence Log on every option.")
  + '<section><div class="wrap"><div class="pairs rv"><div><div class="tag" style="color:var(--steel)">Pairs with AgentNexus</div><h3>One pod per line or site. '+T_+'One AgentNexus for the fleet.'+E_+'</h3><p>AgentMesh sends what it finds to AgentNexus. There, agents compare sites and plan maintenance. AgentNexus never reaches back into factory control.</p></div><a class="btn btn-gh" href="agentnexus.html" data-cursor>Explore AgentNexus <span class="ar">→</span></a></div></div></section>'
)

NEXUS_FLEETS = S("02","Your sites","One system for "+T_+"every site you run."+E_,
  disc([
   ("/battery","Gigafactories and storage fleets","Findings from every cell line and every storage site in one view. Agents put together the quality and incident records that reviewers and insurers ask for.",["line + fleet","incident records"]),
   ("/build-test","Factories and test stands","A test-stand problem is traced back to the production lot that built the part. Agents draft the NCR for your engineer to sign.",["test → lot","NCR drafts"]),
   ("/fab","Fabs and suppliers","A failing pump at a gas or chemical supplier is caught before it affects the fab.",["supplier network","IP stays on site"]),
   ("/robotics","Robot fleets","Joint and motor health compared across every line and site. Drones and vessels catch up when they reconnect.",["fleet health","sync on reconnect"]),
   ("/dual-use","Dual-use programs","Commercial and defense work on one platform, including new shipyards. It runs in your own enclave, so program data stays inside your boundary.",["shipyards","your enclave"]),
   ("/energy","New energy sites","Condition reports and work orders across new power and nuclear sites. Advisory only, never on safety systems.",["condition reports","advisory"])]),
  "Most deep-tech companies run more than one site. AgentNexus is where their agents work across all of them, in English or Spanish.", "fleets")

NEXUS_SECTIONS = (  S("03","How it works","From a finding at one site "+T_+"to a plan for all of them."+E_,
    f'<div class="axwrap rv">{SVG_NEXUS}</div>'
    + flow4([("Finding","An AgentMesh pod sends what it found, over an encrypted link.","AgentMesh → AgentNexus"),
             ("Compare","An agent checks the other sites and the history for the same problem.","cross-site"),
             ("Draft","It drafts the maintenance plan, NCR, quality record or work order. It answers within 0.5 s (target).","drafts only"),
             ("Approve","A named person approves it before it goes to MES, QMS, your ERP or Maximo.","a person signs")]),
    "AgentMesh makes the fast decisions at each line. AgentNexus works at business speed across all of them. It never moves equipment.", "how")
  + S("04","Business skills","Connected to "+T_+"your business systems."+E_,
    disc([
     ("/operations","Operations","The morning production report with OEE and downtime. Breakdown write-ups with the likely causes ranked, ready when the technician arrives.",["morning report","OEE"]),
     ("/quality","Quality","NCRs and 8D corrective-action reports, with the process data lined up against the defect.",["NCR","8D · CAPA"]),
     ("/supply","Supply chain","Supplier quote requests and side-by-side bid comparisons, using real part usage across your sites.",["supplier RFQs","bid comparison"]),
     ("/sales","Sales and design","Quotes from drawings, priced against real machine availability.",["quotes","shop load"])])
    + '<p class="lead rv" style="font-size:15px;margin-top:14px">Private work stays on your rack. Only work that needs an outside AI model goes out, through one gate that is logged and that you control. Skills read your ERP and documents (SAP, Oracle NetSuite, Infor M3, Microsoft 365). A named person approves every quote, report and supplier email before it is sent. On controlled programs the outbound skills stay off. AgentMesh stays air-gapped either way. In design.</p>',
    "Much of a plant's day is paperwork. AgentNexus drafts it from the live records of every site, for your people to approve.", "skills")
  + S("05","Safety and security","What AgentNexus "+T_+"will never do."+E_,
    '<div class="nxsplit"><figure class="nxfig rv"><img src="../assets/images/sketch/agentnexus-rack-clean.jpg" alt="Illustration of the AgentNexus rack with one tray pulled out" width="982" height="1507" loading="lazy"></figure>'+disc([
     ("/equipment","It never moves equipment","AgentNexus is advisory. Plant control stays with your PLCs, safety systems and operators.",["advisory only"]),
     ("/approval","A person signs every draft","Plans, reports, quotes and emails wait for a named person to approve them.",["human sign-off"]),
     ("/proven","Nothing new switches on untested","A change goes live only after it has proven itself on cases it has never seen. Every change is logged and can be rolled back.",["tested","reversible"]),
     ("/enclave","Inside your enclave","It runs on Unovie's custom-built hardware inside the boundary you already run. It is designed against NIST SP 800-53 and the NIST AI RMF. Designed against, not certified.",["your enclave","NIST SP 800-53"])])+'</div>'
    , "", "security")
  + S("06","Runs on","Unovie's custom-built "+T_+"AMD or NVIDIA hardware."+E_,
    hwrow([("ryzen-ai-max-395","ryzen-ai-max-395","Reference design",True,"AMD Ryzen AI Max+ 395","One rack for the whole fleet, on the same chip as the AgentMesh pod."),
           ("dgx-spark","dgx-spark","Available on",False,"NVIDIA DGX Spark","The AI engineering lab, and a small AgentNexus for one site."),
           ("agx-thor","agx-thor","Pairs with",False,"AgentMesh on Jetson AGX Thor","Robotics and DeepVision tools in the fab report to the same AgentNexus.")])
    )
  + '<section><div class="wrap"><div class="pairs rv"><div><div class="tag" style="color:var(--accent)">Starts with AgentMesh</div><h3>The fleet view is only as good as '+A_+'what each line sees.'+E_+'</h3><p>AgentMesh watches the signals at every line and leaves safety decisions to your control systems. AgentNexus brings the fleet together.</p></div><a class="btn btn-gh" href="agentmesh.html" data-cursor>Explore AgentMesh <span class="ar">→</span></a></div></div></section>'
)

MESH_PANEL = ('<figure class="portalfig rv"><div class="pimg"><a href="../assets/images/sketch/portal-battery.jpg" target="_blank" rel="noopener" title="Open full size"><img src="../assets/images/sketch/portal-battery.jpg" alt="Illustration of the AgentMesh operator screen for a battery cell line: weld and formation signals, the decision, similar past events and a drafted non-conformance report" width="2400" height="1350"></a></div>'
  '<figcaption><b>AgentMesh operator screen</b><span>Cell Line 2 · module laser weld</span></figcaption></figure>')
NEXUS_PANEL = ('<figure class="portalfig rv"><div class="pimg"><a href="../assets/images/sketch/portal-fleet.jpg" target="_blank" rel="noopener" title="Open full size"><img src="../assets/images/sketch/portal-fleet.jpg" alt="Illustration of the AgentNexus fleet screen: findings from each site, problems seen at more than one site and a maintenance plan waiting for sign-off" width="2400" height="1350"></a></div>'
  '<figcaption><b>AgentNexus fleet screen</b><span>Fleet operations</span></figcaption></figure>')


# Keep only the sections a buyer needs on each product page, in this order, renumbered (16 Nov 2026).
def _pick(html, labels):
    secs=re.findall(r'<section.*?</section>', html, re.S)
    out=[]
    for lab in labels:
        for sec in secs:
            m=re.search(r'<span class="ln"></span>\d\d · ([^<]+)</div>', sec)
            if m and m.group(1)==lab:
                if lab=="How it works": sec=sec.replace('<section>','<section id="how">',1)
                out.append(sec); break
        else: raise SystemExit(f"_pick: no section labelled {lab!r}")
    return "".join(re.sub(r'(<span class="ln"></span>)\d\d( · )', lambda m,k=k: f'{m.group(1)}{k:02d}{m.group(2)}', sec, count=1) for k,sec in enumerate(out,1))
MESH_KEEP=["How it works","Operator screen","The safety boundary","Domain kits","Security"]
NEXUS_KEEP=["How it works","Fleet screen","Business skills","Safety and security"]

product_page("agentmesh","Platform · AgentMesh","Agent"+A_+"Mesh"+E_,
  "AI at the machine, for battery lines, chip fabs, space hardware and robot cells. AgentMesh watches every signal your line produces and decides within 30 ms (target).",
  ["robot cells","DeepVision","air-gapped","signed Evidence Log"],
  [("&lt;30<span class='o'>ms</span>","decision · target"),("0<span class='o'>B</span>","leaves the site"),("6","domain kits"),("2","safety lanes")],
  MESH_PANEL, _pick(MESH_HMI+MESH_NEXTGEN+MESH_SECTIONS, MESH_KEEP), "Put AI on "+A_+"every signal your line makes."+E_,
  "AgentMesh puts AI at the machine in battery, chip, space, robotics and defense factories. It decides within 30 ms (target), leaves safety to your control system and signs every decision.")
product_page("agentnexus","Platform · AgentNexus","Agent"+T_+"Nexus"+E_,
  "AI agents that work across every site you run: gigafactories and storage fleets, fabs and their suppliers, factories and test stands. They compare sites and draft maintenance plans, NCRs, quality records and work orders. A named person approves each one. AgentNexus answers within 0.5 s (target) and never moves equipment.",
  ["multi-site","person approves","your enclave","AMD · NVIDIA"],
  [("0.5<span class='o'>s</span>","answer · target"),("1","rack for the whole fleet"),("1","gate out, logged"),("0","equipment it controls")],
  NEXUS_PANEL, _pick(NEXUS_HMI+NEXUS_FLEETS+NEXUS_SECTIONS, NEXUS_KEEP), "Run agents "+T_+"across every site."+E_,
  "AgentNexus runs AI agents across every site of a deep-tech manufacturer. They draft plans, NCRs and work orders for a named person to approve, inside your own enclave.")



# ----- DEVICE PLATFORM -----
# Public tier: vendor silicon and what each is used for. No Unovie build specs.
def devshot(vh, vlead, img, alt):
    return ('<section><div class="wrap"><div class="shead"><div class="l">'
            '<div class="num rv"><span class="ln"></span>The device</div>'
            f'<h2 class="rv">{vh}</h2></div><p class="lead rv">{vlead}</p></div>'
            f'<div class="devshot rv"><img class="devimg" src="assets/images/{img}.png" width="820" height="440" alt="{alt}" loading="lazy"></div></div></section>')
DEV_VIS={
 "nvidia-agx-thor": devshot("An edge computer you can <span class='serif' style='color:var(--accent)'>hold.</span>",
   "Thor is a compact edge computer. You mount it on the line, in a vehicle or at the robot cell, and the models run where the data starts.",
   "agx-thor","NVIDIA AGX Thor edge computer, periwinkle line drawing"),
 "nvidia-dgx-spark": devshot("A supercomputer that fits on a <span class='serif' style='color:var(--accent)'>desk.</span>",
   "Spark is about the size of a desktop PC. Engineers build and test models on it, then move them to the plant unchanged.",
   "dgx-spark","NVIDIA DGX Spark desktop AI computer, periwinkle line drawing"),
 "qualcomm-qcs6490": devshot("Built for the far <span class='serif' style='color:var(--accent)'>edge.</span>",
   "A small, fanless box for places where cables and power are scarce.",
   "qcs6490","Qualcomm QCS6490 edge box, periwinkle line drawing"),
}
DEVP=[
 ("amd-ryzen-ai-max-395","Factory AI on your site · AMD","AMD Ryzen AI "+A+"Max+ 395"+E,
  "This chip runs AI on the signals your lines produce, and keeps it inside your site. It powers the AgentMesh pod at the line and the AgentNexus rack for the fleet. Each chip combines CPU cores, graphics and an AI engine that share one pool of memory (AMD spec).",
  [("Asset health","purpose"),("3U","pod at the line"),("1 rack","for the whole fleet")],
  ("What runs on it",[
   ("/agentmesh","AgentMesh Sovereign Pod","A compact 3U pod at the line, on your factory network. Air-gapped.",["3U pod","air-gapped"]),
   ("/agentnexus","AgentNexus rack","One rack in a central room runs agents for every site.",["one rack","every site"])]),
  ("Line to fleet",[("Pod","A compact pod at each line or site."),("Rack","One rack for the whole fleet."),("Fleet","Every new site gets the same setup.")]),
  "Factory AI that "+A+"stays on your site."+E),
 ("nvidia-agx-thor","Robotics &amp; DeepVision · NVIDIA","NVIDIA Jetson AGX "+A+"Thor"+E,
  "For robotics and DeepVision inside the fab. Jetson AGX Thor fits inside a robot cell, an inspection tool or a mobile robot. It runs high-resolution vision next to the camera, with AgentMesh's safety lanes and Evidence Log around every decision.",
  [("Robotics + vision","purpose"),("2,070<span class='o'>TFLOPS</span>","FP4 AI · NVIDIA spec"),("128<span class='o'>GB</span>","memory · NVIDIA spec")],
  ("Vision and motion, at the tool",[
   ("/deepvision","DeepVision inspection","Finds defects, particles and misalignment on wafers, dies, panels and assemblies at line speed. Images stay on the floor.",["defects","on the tool"]),
   ("/robotics","Robot cells and mobile robots","Checks for robot cells, wafer-handling robots and mobile robots, combined with motor and vibration signals.",["robot cells","AMRs"]),
   ("/lanes","Same safety lanes","A reject or a hold is acted on directly. Anything that touches people or process safety goes to the cell controller and the operator.",["Lane A","Lane B"])]),
  ("Image to action",[("See","Cameras and sensors feed Thor."),("Check","Vision models check every part."),("Decide","Safety lanes apply."),("Record","Every decision is logged.")]),
  "DeepVision and robotics, "+A+"at the tool."+E),
 ("nvidia-dgx-spark","AI engineering lab · NVIDIA","NVIDIA DGX "+A+"Spark"+E,
  "For the AI engineering lab. DGX Spark sits on a desk. Your team can test new models on recorded plant data, analyse test-stand runs, and host a small AgentNexus for one site. Models then move to the plant unchanged.",
  [("Lab + pilots","purpose"),("1,000<span class='o'>TFLOPS</span>","FP4 AI · NVIDIA spec"),("128<span class='o'>GB</span>","memory · NVIDIA spec")],
  ("Three uses, one box",[
   ("/lab","Test before the plant","Replay recorded plant data against new models before anything touches the factory network.",["replay","testing"]),
   ("/test","Test-stand analytics","Analyse test-rig runs and draft test reports.",["test stands","reports"]),
   ("/nexus","A small AgentNexus","One to four units run AgentNexus for a single site or a pilot.",["site","pilot"])]),
  ("Lab to plant",[("Record","Bring in recorded plant data."),("Test","Prove the change on cases it has never seen."),("Ship","Move the same model to the plant.")]),
  "Build and prove it "+A+"in the lab."+E),
 ("qualcomm-qcs6490","Mobile &amp; remote assets · Qualcomm","Qualcomm "+A+"QCS6490"+E,
  "For mobile and remote equipment: a mobile robot, an AGV, a drone dock or a battery container. A fanless QCS6490 box reads sensors on site and sends short summaries to the nearest AgentMesh pod.",
  [("Remote assets","purpose"),("12<span class='o'>TFLOPS</span>","on-device AI · Qualcomm spec"),("fanless","low power")],
  ("Reach the hard-to-wire equipment",[
   ("/collect","Reads sensors on site","Where running cable would be costly or impossible.",["remote","low power"]),
   ("/forward","Sends findings to AgentMesh","The nearest pod applies the safety lanes and the Evidence Log.",["AgentMesh","lanes"])]),
  ("Sensor to pod",[("Sense","Sensors on remote equipment."),("Summarise","On the device."),("Send","Wireless, to the nearest pod.")]),
  "Reach the "+A+"far edge."+E),
]

def _devkey(slug): return slug.split("-",1)[1]
ICO.update({
 "truck":'<svg viewBox="0 0 24 24"><path d="M3 7h11v8H3zM14 10h4l3 3v2h-7z"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>',
 "cell":'<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>',
 "clip":'<svg viewBox="0 0 24 24"><rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9zM8 12h8M8 16h5"/></svg>',
 "pin":'<svg viewBox="0 0 24 24"><path d="M12 22s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
 "pipe":'<svg viewBox="0 0 24 24"><path d="M2 9h8v6H2zM14 9h8v6h-8zM10 11h4v2h-4z"/></svg>',
 "fleet":'<svg viewBox="0 0 24 24"><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M7 6h10M6 8l5 8M18 8l-5 8"/></svg>',
 "flask":'<svg viewBox="0 0 24 24"><path d="M9 3h6M10 3v6L4 20h16L14 9V3"/></svg>',
 "wafer":'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M7 9h10M6 12h12M7 15h10M9 6v12M12 3v18M15 6v12"/></svg>',
})

def factlist(items):
    return '<table class="glance rv facts">'+"".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in items)+'</table>'

DEV_EXTRA={
 "amd-ryzen-ai-max-395":
   S("03","Agentic jobs","Jobs it runs "+A_+"today."+E_,
     kits([("rot","Robot &amp; motion health","Robots, axes, spindles and conveyors: what is wrong, how bad, and a drafted work order.","AgentMesh"),
           ("bat","Battery line &amp; storage safety","Weld and formation checks in line. Thermal-runaway warning on storage sites, as an alarm.","AgentMesh"),
           ("ele","Fab utilities &amp; electrical health","Pumps, chillers, scrubbers and drives at fabs and their suppliers, with early warnings.","AgentMesh"),
           ("ot","Factory network watch","Unauthorized writes and unusual commands on the factory network, with audit evidence.","AgentMesh"),
           ("clip","Quality records &amp; planning","Agents group findings across sites, draft NCRs and plan repairs around production.","AgentNexus")]))
   + S("04","Deployment","Where it lives",
     factlist([("Where it sits","Factory network (pod) · central room (rack)"),("Form","A compact 3U pod at the line · one rack for the whole fleet"),("Status","The pod runs today · the rack is a reference design on the same chip")])),
 "nvidia-agx-thor":
   S("03","Agentic jobs","Robotics and DeepVision "+A_+"for the fab."+E_,
     kits([("eye","Wafer &amp; die inspection","Finds defects, particles and scratches at the tool, and holds or rejects a lot.","semiconductor · electronics"),
           ("wafer","Panel &amp; assembly inspection","Solder, placement and surface defects, checked at line speed.","PCB · display · assembly"),
           ("cell","Robot-cell quality","Vision plus weld current, torque and vibration confirm every robot cycle.","robot cells · welding"),
           ("truck","Wafer handling &amp; AMRs","Health checks for wafer-handling robots and mobile robots moving lots between tools.","handling · AMRs")]),
     "Images and models stay on the tool. Only findings move on.")
   + S("04","Deployment","Where it lives",
     factlist([("Where it sits","Inside an inspection tool, a robot cell or a mobile robot"),("Power","40–130 W, configurable (NVIDIA spec)"),("Connectivity","Works disconnected · findings sync to AgentNexus"),("Status","Available per project")])),
 "nvidia-dgx-spark":
   S("03","Agentic jobs","The lab where "+A_+"plant AI is proven."+E_,
     kits([("flask","Testing improvements","New models are tested on recorded plant outcomes before they reach production.","testing"),
           ("test","Test-stand analytics","Pressure, strain and acoustic data from test rigs, run by run, with drafted reports.","aerospace · energy"),
           ("clip","Site AgentNexus","A small AgentNexus for one site: planning, shift handover and quality agents.","1–4 units")]),
     "When a pilot grows, the same agents and models move to the AMD rack unchanged.")
   + S("04","Deployment","Where it lives",
     factlist([("Where it sits","Engineering office, server room or a shelf near the line"),("Form","Desk-sized unit · two can be linked (NVIDIA spec)"),("Status","Available per project")])),
 "qualcomm-qcs6490":
   S("03","Agentic jobs","Remote and mobile equipment, "+A_+"in the loop."+E_,
     kits([("pin","Mobile robots &amp; AGVs","Motor, wheel and battery health on robots that move.","motor current · vibration"),
           ("pipe","Drone docks &amp; outdoor equipment","Motor, charge and environment signals, with only short findings sent back.","motor · battery"),
           ("bat","Battery containers","Battery and off-gas data from remote containers, sent to the nearest pod.","battery · off-gas")]),
     "QCS6490 reads and summarises. Decisions and the Evidence Log stay on the nearest AgentMesh pod.")
   + S("04","Deployment","Where it lives",
     factlist([("Where it sits","Next to remote equipment, in a small fanless box"),("Connectivity","Wi-Fi 6E and Bluetooth (Qualcomm spec)"),("Status","Far-edge sensing that feeds AgentMesh")])),
}

def devpanel(s, first):
    slug,cat,title,lead,kpis,feats,hows,cta=s; key=_devkey(slug)
    return (f'<div class="tpanel{" active" if first else ""}" id="{key}" role="tabpanel" aria-labelledby="tab-{key}">'
      f'<section class="psub"><div class="wrap"><div class="tag rv">{cat}</div>'
      f'<h2 class="rv" style="margin-top:10px">{title}</h2><p class="lead rv">{lead}</p>{metrics(kpis)}</div></section>'
      f'{DEV_VIS.get(slug,"")}'
      f'<section><div class="wrap">{shead("01","What it does",feats[0])}{disc(feats[1])}</div></section>'
      f'<section><div class="wrap">{shead("02","How it fits",hows[0])}{steps(hows[1])}</div></section>'
      f'{DEV_EXTRA.get(slug,"")}'
      f'</div>')

HW_MATRIX='''<section style="padding-top:20px"><div class="wrap">
  <div class="shead"><div class="l"><div class="num rv"><span class="ln"></span>Choose by job</div><h2 class="rv">Which hardware <span class="serif" style="color:var(--accent)">for which job.</span></h2></div>
  <p class="lead rv">Every option runs the same Unovie platform. Pick by where the work happens.</p></div>
  <div class="stackwrap rv"><table class="glance hwm">
    <tr><th></th><th>AMD Ryzen AI Max+ 395</th><th>NVIDIA Jetson AGX Thor</th><th>NVIDIA DGX Spark</th><th>Qualcomm QCS6490</th></tr>
    <tr><td>Used for</td><td><b>Factory AI on your site</b></td><td><b>Robotics &amp; DeepVision for fabs</b></td><td><b>AI engineering lab</b></td><td><b>Mobile &amp; remote equipment</b></td></tr>
    <tr><td>Role</td><td>AgentMesh pod · AgentNexus rack</td><td>AgentMesh at the tool or robot</td><td>Testing · test stands · site AgentNexus</td><td>Far-edge sensing for AgentMesh</td></tr>
    <tr><td>Where it sits</td><td>Factory network · central room</td><td>Inspection tool · robot cell · AMR</td><td>Engineering lab · server room</td><td>Robots, AGVs · remote equipment</td></tr>
    <tr><td>Form</td><td>3U pod at the line · one rack for the fleet</td><td>Module, 40–130 W</td><td>Desk-sized unit</td><td>Fanless box</td></tr>
    <tr><td>Status</td><td><span class="st now">Runs today</span></td><td><span class="st">Available on</span></td><td><span class="st">Available on</span></td><td><span class="st">Far edge</span></td></tr>
  </table></div>
</div></section>
'''

_dtabs="".join(f'<button class="tab{" active" if i==0 else ""}" id="tab-{_devkey(s[0])}" data-tab="{_devkey(s[0])}" role="tab" aria-selected="{"true" if i==0 else "false"}" data-cursor>{re.sub("<[^>]+>","",s[2])}</button>' for i,s in enumerate(DEVP))
_dpanels="".join(devpanel(s,i==0) for i,s in enumerate(DEVP))
_devhead=HEAD("","Hardware: AgentMesh and AgentNexus on AMD and NVIDIA | Unovie.AI","AgentMesh and AgentNexus run on Unovie's custom-built AMD or NVIDIA hardware accelerators: AMD Ryzen AI Max+ 395, NVIDIA Jetson AGX Thor and DGX Spark, with Qualcomm QCS6490 at the far edge.")
_devbody=f"""{NGBG}{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">Hardware</span></div>
  <div class="tag rv">Hardware</div>
  <h1 class="rv" style="margin-top:18px">Two hardware families. <span class="serif" style="color:var(--accent)">One platform.</span></h1>
  <p class="lead rv">AgentMesh and AgentNexus run on Unovie's custom-built AMD or NVIDIA hardware accelerators. AMD Ryzen AI Max+ 395 is the reference for both. NVIDIA Jetson AGX Thor puts AgentMesh inside the machine. NVIDIA DGX Spark is the engineering lab. Qualcomm QCS6490 reaches remote equipment.</p>
  <div class="runs rv" style="margin:26px 0 22px"><div class="run"><span class="st now">Runs today</span><h4>AMD Ryzen AI Max+ 395</h4><p>The AgentMesh pod runs today. The AgentNexus rack is a reference design on the same chip.</p></div><div class="run"><span class="st">Available on</span><h4>NVIDIA Jetson AGX Thor · DGX Spark</h4><p>Robotics and DeepVision at the tool, and the AI engineering lab. Set up per project.</p></div><div class="run"><span class="st">Far edge</span><h4>Qualcomm QCS6490</h4><p>Remote and mobile equipment, feeding the nearest AgentMesh pod.</p></div></div>
  <div class="cta rv"><a class="btn btn-acc" href="index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
</div>
</div></section>
{HW_MATRIX}
<section class="tabwrap"><div class="wrap"><div class="tabs" role="tablist" aria-label="Hardware">{_dtabs}</div></div></section>
{_dpanels}
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Let's build</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("")}"""
open(f"{ROOT}/device-platform.html","w",encoding="utf-8").write(_devhead+_devbody)

# ----- ABOUT -----
about=f'''{HEAD("","About | Unovie.AI","Unovie designs, builds and operates custom Edge-AI Agentic Systems for deep-tech manufacturing. Austin, Texas.")}{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">About</span></div>
  <div class="tag rv">About <span class="o">·</span> Physical AI for deep-tech industries</div>
  <h1 class="rv" style="margin-top:18px">We build AI that <span class="serif" style="color:var(--accent)">reaches production.</span></h1>
  <p class="lead rv">Unovie builds AI for factories in deep-tech industries. We are a founder-led engineering company. We take responsibility from the first site visit through the pilot to production. Big transformation programs take years. Strategy decks don't ship. We put a working system on your line in weeks, at a fixed cost.</p>
  <div class="cta rv"><a class="btn btn-acc" href="index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
</div>
  {metrics([("20+ yrs","each founder, in OT &amp; Physical AI"),("6 weeks","paid pilot on your line"),("fixed","scope &amp; cost")])}
</div></section>
<section><div class="wrap">{shead("01","At a glance","Unovie "+A_+"on one page."+E_,"The details live on their own pages. This is the short version.")}{_ctable(["",""],[
  ("<b>Who</b>","An engineering-first, AI-native company in Austin, Texas. Each founder has 20+ years in OT and Physical AI. <a href='why-unovie.html'>Why Unovie →</a>"),
  ("<b>What</b>","Custom Edge-AI Agentic Systems: <a href='platform/agentmesh.html'>AgentMesh</a> at the machine and <a href='platform/agentnexus.html'>AgentNexus</a> across every site, on Unovie's custom-built <a href='device-platform.html'>AMD or NVIDIA hardware accelerators</a>."),
  ("<b>For whom</b>","Deep-tech manufacturing: <a href='sectors/battery.html'>battery</a>, <a href='sectors/fabs.html'>chip fabs</a>, <a href='sectors/space.html'>space</a>, <a href='sectors/robotics.html'>robotics</a>, <a href='sectors/defense.html'>defense</a> and <a href='sectors/energy.html'>advanced energy</a>."),
  ("<b>How we work</b>","A site audit at no charge, a 6-week pilot, then production in about a quarter. <a href='index.html#delivery'>See the path</a>."),
  ("<b>Proof</b>","<a href='resources/case-study-device-certification.html'>Case study</a> · <a href='faq.html'>FAQ</a> · <a href='/contact.html'>talk to our engineers</a>")])}</div></section>
<section><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Who we build for</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("")}'''
open(f"{ROOT}/about.html","w",encoding="utf-8").write(about)

# ----- WHY UNOVIE -----
why=f'''{HEAD("","Why Unovie | Physical AI for next-generation manufacturing, Austin, Texas","Unovie is an Austin, Texas engineering company. It takes factory AI from pilot to production in about a quarter, with data kept on site and safety decisions left to your control systems.")}{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">Why Unovie</span></div>
  <div class="tag rv">Why Unovie <span class="o">·</span> Austin, Texas</div>
  <h1 class="rv" style="margin-top:18px">Built in Austin. <span class="serif" style="color:var(--accent)">Ready for your factory.</span></h1>
  <p class="lead rv">Unovie is a young company with veteran founders. Each has spent 20+ years on control systems, robot cells, factory networks and safety systems. We have spent four years building that experience into one platform. Most factory AI is still stuck in pilots. We take it to production in about a quarter. Your data stays on site, and your control systems and operators keep the safety decisions.</p>
  <div class="cta rv"><a class="btn btn-acc" href="index.html#contact" data-cursor>Pilot on your line <span class="ar">→</span></a>
    <a class="btn btn-gh" href="platform/agentmesh.html" data-cursor>See the platform</a></div>
  {metrics([("20+ yrs","each founder, in OT &amp; Physical AI"),("4 yrs","building the Unovie platform"),("6 weeks","paid pilot on your line"),("1 quarter","from pilot to production")])}
</div></section>
<section><div class="wrap">{shead("01","Who we are","Engineers who "+A_+"know the plant floor."+E_)}{disc([
  ("/engineering-first","We start from your factory","Our founders have designed, built and run control systems, robot cells and factory networks. We start from how your plant actually runs.",["20+ years each","OT"]),
  ("/control-layer","We work at the control layer","AgentMesh decides within 30 ms (target). It connects to robot controllers, safety PLCs, vision systems and test rigs over OPC UA, EtherCAT and Modbus. It never writes where it shouldn't.",["30 ms · target","OPC UA · EtherCAT"]),
  ("/evidence","We show our work","Every decision goes into a signed Evidence Log. Engineers, auditors and insurers can see what the AI did and why. The platform is designed against NIST SP 800-53 and the NIST AI RMF.",["Evidence Log","NIST SP 800-53"])])}</div></section>
<section><div class="wrap">{shead("02","Based in Texas","Close to where "+A_+"deep tech is being built."+E_,"We serve customers across the US. Texas is our home base. It is building fabs, gigafactories, space and robot factories, shipyards and reactors. We can be on your floor this week.")}{disc([
  ("/i-35","Austin and Central Texas","Chip fabs and their suppliers, robotics and space factories.",["chip fabs","robotics","space"]),
  ("/battery","Battery lines and storage","Weld and formation checks in line, and thermal-runaway warning on storage sites.",["battery lines","storage"]),
  ("/gulf","Houston and the Gulf Coast","Space hardware and test stands, shipyards and advanced energy sites.",["space","shipyards","energy"])])}</div></section>
<section><div class="wrap">{shead("03","Why now","Why this matters "+A_+"in 2027."+E_)}{disc([
  ("/pilots","Pilots need to become production","Most manufacturers are still running AI pilots. They want a partner who reaches production in a quarter.",["pilot to production"]),
  ("/rules","New factories face new rules","Factories opening in 2027 and 2028 face battery-site safety rules, fab equipment-security standards and defense data rules. Buyers need evidence, not dashboards.",["evidence","2027–28"]),
  ("/hardware","Hardware prices move","Memory and chip prices swing. We build the hardware, test it with the platform and can refresh it as a service, so the price risk is ours.",["AMD","NVIDIA"])])}</div></section>
<section><div class="wrap">{shead("04","How we engage","From site audit "+A_+"to fleet."+E_)}{steps([
  ("Site audit · no charge","An engineer spends 1–2 days on site reviewing your sensors, robots, network and control systems."),
  ("6-week pilot · $40–60K","One domain kit on your own line. You get a baseline ROI view and a measured latency report. The fee is credited in full against a production site signed within 90 days."),
  ("Production site","An AgentMesh pod connected to your sensors, cell controllers, safety PLC, MES and work-order system."),
  ("Fleet","New lines and sites reuse the same setup. AgentNexus connects them.")])}</div></section>
<section><div class="wrap">{shead("05","Where we are different","What you get "+A_+"working with us."+E_)}{disc([
  ("/floor","People who have worked on the floor","Every engagement is led by two people: one who knows operations and OT security, and one engineer who audits and delivers.",["OT experience","site audit"]),
  ("/safety","Safety and data stay with you","A language model is never on the path that moves equipment. We make no SIL claim. AgentMesh is air-gapped, so nothing leaves the site unless you want it to.",["no SIL claim","air-gapped"]),
  ("/price","Priced per asset and kit","We price per monitored asset and domain kit, never per seat or per camera.",["per asset","per kit"])])}</div></section>
<section><div class="wrap">{shead("06","Our place in the market","A third option.")}{disc([
  ("/transformation","Large integrators","They rebuild your whole digital estate. It is valuable, but it takes years and millions before first value.",["multi-year"]),
  ("/vision","Strategy firms","They describe where you should go. You still need someone to build it.",["roadmaps"]),
  ("/unovie","Unovie","We bring the plan and the engineering team. You get a working system you own, in production in about a quarter.",["owned","one quarter"])])}</div></section>
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Austin, Texas</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("")}'''
open(f"{ROOT}/why-unovie.html","w",encoding="utf-8").write(why)


# =====================================================================
# SECTOR PAGES · FAQ · CASE STUDY  (GTM critique P2, 15 Nov 2026)
# =====================================================================
PRICE_LINE='<p class="pricenote rv"><b>Site audit:</b> no charge, 1–2 days on site <span class="o">·</span> <b>6-week paid pilot:</b> $40–60K, credited in full against a production site signed within 90 days</p>'

def _hero_img(img, alt, base="../"):
    return (f'<figure class="portalfig rv"><div class="pimg"><a href="{base}assets/images/sketch/{img}.jpg" target="_blank" rel="noopener" title="Open full size">'
            f'<img src="{base}assets/images/sketch/{img}.jpg" alt="Illustration: {alt}" width="2400" height="1350"></a></div>'
            '</figure>')

def _ctable(head, rows):
    h="".join(f"<th>{c}</th>" for c in head)
    r="".join("<tr>"+"".join(f"<td>{c}</td>" for c in row)+"</tr>" for row in rows)
    return f'<div class="ctwrap rv"><table class="ctable"><tr>{h}</tr>{r}</table></div>'

def _never(txt):
    return f'<div class="never rv"><b>Never:</b> {txt}</div>'

def _tech_links(base="../"):
    return ('<div class="disc" style="margin-top:8px">'
      f'<a class="dcard rv" href="{base}platform/agentmesh.html#security" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--steel)"></div><h3>Secure by design</h3><p>Designed against NIST SP 800-53 and the NIST AI RMF. Evidence for your assessor.</p></a>'
      f'<a class="dcard rv" href="{base}faq.html" data-cursor style="text-decoration:none"><div class="glow" style="background:var(--accent)"></div><h3>Buyer questions, answered</h3><p>Data, safety, hardware, price and what happens when the link drops.</p></a>'
      '</div>')

# (slug, short name, tag, h1, lead, hero_img, hero_alt, chips, kpis, pains, jobs, connects, never, pilot)
SECTORS=[
 ("battery","Battery &amp; energy storage","Battery lines · storage sites",
  "Every weld, every cell, "+A_+"watched in line."+E_,
  "Cell, module and pack lines produce more weld, formation and aging data than any team can read. AgentMesh watches it in line and diverts suspect parts to rework. On storage sites it gives early warning of thermal runaway, as an alarm on the systems you already have.",
  "portal-battery","AgentMesh operator screen for a battery cell line: laser-weld and formation signals, the decision lane and a drafted non-conformance report",
  ["cell · module · pack","formation &amp; aging","storage sites"],
  [("&lt; 30 ms","divert decision · target"),("In line","every weld judged, not sampled"),("Alarm only","on storage sites"),("0","raw signals sent off site")],
  [("/ramp","Ramp-up scrap","A new line learns as it runs. A bad weld found at end-of-line test has already cost a finished module."),
   ("/safety","Storage-site safety reviews","Fire codes, insurers and safety reviews ask for evidence that warning signs were watched, every hour, on every rack."),
   ("/ip","Process data is the IP","Cell chemistry, weld schedules and formation recipes can't go to someone else's cloud.")],
  [("/line","Battery Line &amp; Storage Safety","Weld, formation and aging signatures judged in line. On the line, Lane A diverts a suspect part to rework. On storage sites, early signs of thermal runaway go out as an alarm.",["Lane A divert","alarm on fleets"]),
   ("/vision","Vision Quality Inspection","Weld seams, tab alignment and electrode defects checked by DeepVision and fused with the process signals for the same part.",["DeepVision","fused signals"]),
   ("/records","Quality records, drafted","Non-conformance reports and traceability records drafted with the evidence attached, ready for your quality engineer to sign.",["NCR drafts","sign-off"])],
  [("Laser-weld controllers and weld-current clamps","read-only"),("Formation and cycler data","read-only"),("Battery and energy management systems","read-only"),("MES and quality system","records out"),("Fire alarm panel","alarm input only"),("Work-order system (e.g. SAP, Maximo)","work orders out")],
  "AgentMesh never writes to a battery or energy management system and never triggers fire suppression. On storage sites it raises alarms; people and your safety systems act.",
  "Pilot on one cell line or one storage site: replay of past weld and formation data in weeks 1–2, live in-line flags in weeks 3–6."),
 ("fabs","Chip fabs &amp; suppliers","Fab utilities · supplier plants",
  "Fab utilities that "+A_+"never surprise you."+E_,
  "Pumps, chillers, scrubbers, ultra-pure water and gas systems keep the fab alive. AgentMesh watches them from their own signals through ramp-up and steady state, at the fab and at its gas, chemical and parts suppliers. Process and design data never leave the fence.",
  "portal-fab","AgentMesh operator screen for fab utilities: a sub-fab dry pump, its vibration signal and a request to facilities",
  ["sub-fab utilities","supplier plants","IP stays on site"],
  [("Lane B","facilities decide"),("Weeks","to learn a baseline during ramp"),("SEMI E187","evidence for equipment security"),("0","process data sent off site")],
  [("/downtime","Utility trips scrap wafers","A failed dry pump or scrubber can take a tool down mid-process. The warning signs are in the vibration and power data, days ahead."),
   ("/staff","Ramp with thin crews","New fabs and supplier plants open with fewer experienced facilities engineers than they need."),
   ("/ip","Design and process IP","Fab data is among the most guarded in industry. Cloud analytics is usually a non-starter.")],
  [("/utilities","Fab Utilities Watch","Pumps, chillers, scrubbers, UPW and gas systems watched continuously. Findings go to facilities as a Lane B request with the evidence attached.",["Lane B","work order drafted"]),
   ("/electrical","Electrical Health","Drives, tool power, UPS and switchgear: early signs of arcing and insulation failure, from power-quality and partial-discharge signals.",["power quality","partial discharge"]),
   ("/network","Factory Network Watch","Unusual commands and unauthorized writes on the tool and facilities network, with evidence for equipment-security reviews.",["SEMI E187","audit evidence"])],
  [("Vibration and ultrasonic sensors on rotating equipment","read-only"),("Facilities monitoring and SCADA","read-only"),("Power-quality meters and switchgear","read-only"),("Tool and facilities network traffic","passive copy"),("Work-order system (e.g. SAP, Maximo)","work orders out"),("Facilities alarm system","alarm input only")],
  "AgentMesh never changes a tool recipe or a facilities setpoint. It raises requests; your facilities team and control systems decide.",
  "Pilot on one sub-fab bay or one supplier plant: replay of past utilities data in weeks 1–2, live Lane B requests in weeks 3–6."),
 ("space","Space &amp; aerospace","Test stands · vehicle lines",
  "Every test run watched. "+A_+"Every flight part traced."+E_,
  "Launch-vehicle, engine and spacecraft programs run more tests than people can watch channel by channel. AgentMesh flags anomalies to the test conductor during a run, beside your qualified test system, and drafts the post-test report and quality records. Export-controlled data stays on site.",
  "portal-test","AgentMesh operator screen at an engine test stand: hot-fire run channels, an advisory flag to the test conductor and a drafted post-test report",
  ["test stands","cleanrooms","quality records"],
  [("&lt; 30 ms","advisory flags · target"),("Advisory","never in the test or flight path"),("On site","export-controlled data stays"),("Drafted","post-test reports and NCRs")],
  [("/cadence","More launches, more tests","Test cadence is rising faster than the number of engineers who can read every channel of every run."),
   ("/data","Data that can't leave","Test data and drawings for export-controlled programs can't go to a public cloud."),
   ("/records","Records for every part","Every flight part needs a record that ties test results back to the lot, the cleanroom step and the people who built it.")],
  [("/tcm","Test Campaign Monitor","Pressure, strain, temperature and acoustic channels compared run by run. Anomalies go to the test conductor as advisory flags, beside the qualified test system and never inside it.",["advisory","post-test report"]),
   ("/vision","Vision QA on the line","DeepVision checks on composite layups, welds and harnesses, fused with process signals from the same step.",["DeepVision","cleanroom"]),
   ("/records","Quality records, drafted","First-article and non-conformance drafts with the evidence attached, and a trace from a test anomaly back to the production lot, for AS9100 quality systems.",["NCR drafts","test → lot trace"])],
  [("Test-rig data acquisition","read-only copy"),("Test conductor console","advisory flags only"),("Cleanroom and line sensors, cameras","read-only"),("MES and quality system","records out"),("Product lifecycle and drawing systems","read-only lookups"),("Work-order system","work orders out")],
  "AgentMesh never commands a test stand, a range or a flight system. It advises; the test conductor and your qualified systems decide.",
  "Pilot on one test stand: read-only connection and replay of past campaigns in weeks 1–2, live advisory flags and drafted reports in weeks 3–6, a signed evidence pack in week 6."),
 ("robotics","Robotics, drones &amp; autonomous systems","Robot lines · drones · vessels",
  "Robot-dense lines, "+A_+"and the robots they build."+E_,
  "Robot cells, motion axes and vision stations produce a constant stream of joint, torque and image data. AgentMesh catches a drifting joint or gearbox before it scraps parts or stops the line, and keeps fleet health for drones and vessels that run disconnected and sync when they return.",
  "portal-assembly","AgentMesh operator screen for a robotic assembly line: weld cell and spindle signals and a Lane A reject",
  ["robot cells","DeepVision","works offline"],
  [("&lt; 30 ms","reject decision · target"),("Lane A","reject gate, rework divert"),("Offline","fleets sync when they return"),("0","raw signals sent off site")],
  [("/drift","Drift scraps parts first","A worn gearbox or a drifting servo shows up as bad parts long before the robot faults."),
   ("/volume","Too much data to watch","Every cell streams joint current, torque, cycle and vision data. Nobody can watch all of it."),
   ("/field","Fleets that go dark","Drones and autonomous vessels spend hours or days without a link. Health checks have to run on board and catch up later.")],
  [("/motion","Robot &amp; Motion Health","Joint, servo, gearbox and spindle health on robots, motion axes and conveyors, with a drafted work order.",["Lane A reject","work order"]),
   ("/vision","Vision Quality Inspection","DeepVision at the cell on NVIDIA Jetson AGX Thor, fused with force, electrical and acoustic signals from the same cycle.",["Jetson AGX Thor","sensor fusion"]),
   ("/fleet","Fleet health for drones and vessels","Motor, battery and structure checks on board or at the dock, synced to the nearest AgentMesh pod when the link returns.",["works offline","dock sync"])],
  [("Robot controllers and servo drives","read-only"),("Vision stations and cameras","read-only"),("Cell controller and PLC","reject / divert outputs only"),("MES and quality system","records out"),("Drone docks and vessel data links","sync on return"),("Work-order system","work orders out")],
  "AgentMesh never moves a robot axis and never overrides a safety PLC. Lane A acts only on reject gates and diverters; everything else is a request.",
  "Pilot on one robot cell or one dock: replay of past joint and vision data in weeks 1–2, live reject decisions or flags in weeks 3–6."),
 ("defense","Defense &amp; dual-use manufacturing","Shipyards · dual-use factories",
  "Inside your enclave. "+A_+"Nothing leaves it."+E_,
  "New shipyards, autonomous-vessel yards and dual-use factories are ramping with thin crews and strict data rules. AgentMesh runs line and yard quality checks, machinery health and factory network watch inside the security boundary you already maintain, and writes the evidence your assessors ask for.",
  "engine-room","machinery vibration and ultrasonic thickness monitoring on a main engine and generator, analysed locally",
  ["your enclave","shipyards","evidence for CMMC"],
  [("Air-gapped","by default"),("SP 800-171","evidence for CMMC programs"),("Lane B","people decide"),("0","bytes leave the enclave")],
  [("/crews","Ramp with thin crews","New yards and lines open faster than experienced inspectors and maintainers can be hired."),
   ("/cui","Controlled data","Controlled unclassified and export-controlled data must stay inside an approved boundary."),
   ("/evidence","Evidence for assessors","CMMC and SP 800-171 programs need records of what systems did and who approved it.")],
  [("/qa","Line and yard QA","DeepVision weld and structure checks fused with process signals, with drafted non-conformance reports.",["DeepVision","NCR drafts"]),
   ("/machinery","Machinery health","Vibration, electrical and ultrasonic signals on pumps, motors, generators and shop equipment, with work orders drafted.",["rotating equipment","electrical"]),
   ("/network","Factory Network Watch","Unusual commands and unauthorized writes on the factory network, logged for audits.",["OT network","audit evidence"])],
  [("Machinery sensors and condition monitoring","read-only"),("Weld and process equipment","read-only"),("Vision stations","read-only"),("Factory network traffic","passive copy"),("MES and quality system","records out"),("Maintenance system","work orders out")],
  "AgentMesh works on the factory, the yard and its machinery. It is never part of a weapon, fire-control or combat system, and the language model never sits on a path that moves equipment.",
  "Pilot on one line, dock or machinery space inside your enclave: replay in weeks 1–2, live flags and drafted records in weeks 3–6."),
 ("energy","Advanced energy &amp; nuclear","New reactor and power sites",
  "Balance of plant, watched. "+A_+"Safety systems, never touched."+E_,
  "New reactor, geothermal and power sites bring first-of-a-kind equipment and long commissioning schedules. AgentMesh watches construction, balance-of-plant equipment and site security from their own signals and drafts condition reports for review. It is never on reactor protection or any safety-related system.",
  "sensors","vibration and ultrasonic sensors on rotating equipment",
  ["balance of plant","condition reports","non-safety only"],
  [("Non-safety","systems only"),("Advisory","condition reports for review"),("Air-gapped","by default"),("0","raw signals sent off site")],
  [("/foak","First-of-a-kind equipment","New designs have no long failure history. Baselines have to be learned during commissioning."),
   ("/schedule","Commissioning schedules","Every week of delay is expensive, and equipment problems found late cost the most."),
   ("/evidence","Scrutiny and records","Owners, regulators and insurers expect clear records of condition and of who decided what.")],
  [("/bop","Balance-of-plant health","Pumps, fans, turbines, transformers and switchgear watched from vibration, electrical and thermal signals.",["rotating equipment","electrical"]),
   ("/reports","Condition reports, drafted","Findings written up with the evidence attached, for your engineers to review and sign.",["drafted","sign-off"]),
   ("/network","Site network watch","Unusual traffic and commands on non-safety plant and construction networks, with audit evidence.",["OT network","audit evidence"])],
  [("Balance-of-plant sensors","read-only"),("Non-safety plant historian","read-only"),("Electrical protection and power-quality data","read-only"),("Site network traffic (non-safety zones)","passive copy"),("Maintenance system","work orders out"),("Engineering review queue","reports out")],
  "AgentMesh is never connected to reactor protection, safety-related or safety-significant systems, and never writes to plant control. It only reads non-safety signals and drafts reports.",
  "Pilot on one balance-of-plant area during commissioning or operation: replay in weeks 1–2, live flags and drafted condition reports in weeks 3–6."),
]

def sector_page(t):
    slug,name,tag,h1,lead,img,alt,chips,kpis,pains,jobs,conn,never,pilot=t
    plain=re.sub('<[^>]+>','',name).replace("&amp;","&")
    head=HEAD("../", f"{plain} | Unovie.AI", re.sub('<[^>]+>','',lead)[:155])
    ch="".join(f'<span class="chip">{c}</span>' for c in chips)
    body=f'''{NGBG}{NAV("../")}
<section class="ph2 sector"><div class="wrap">
  <div class="crumb rv"><a href="../index.html">Home</a><span class="sep">/</span><a href="../index.html#deeptech">Sectors</a><span class="sep">/</span><span style="color:var(--fg-mut)">{name}</span></div>
  <div class="grid">
    <div><h1 class="rv">{h1}</h1><p class="lead rv">{lead}</p>
      <div class="cta rv"><a class="btn btn-acc" href="#pilot" data-cursor>Pilot on your line <span class="ar">→</span></a></div></div>
    <div>{_hero_img(img,alt)}</div>
  </div>
  {kpistrip(kpis)}
</div></section>
{S("01","The problem","What gets "+A_+"in the way."+E_, disc([(a,b,c,[]) for a,b,c in pains]))}
{S("02","The agentic jobs","What AgentMesh "+A_+"does here."+E_, disc(jobs), "Each job is a packaged domain kit. A pod can run several.")}
{S("03","What it connects to","Into the systems "+A_+"you already run."+E_, _ctable(["System","How AgentMesh uses it"], conn)+_never(never), "Everything is read-only unless the table says otherwise.")}
{S("04","The pilot","Six weeks, "+A_+"on your own data."+E_, steps([("Site audit · no charge","An engineer spends 1–2 days on site reviewing your sensors, network and control systems. Nothing is signed yet."),("Weeks 1–2","Read-only connection, baselines from your history, replay of past events."),("Weeks 3–6","Live findings, drafted records and a measured latency report."),("Week 6","Results review and a signed evidence pack.")]), pilot, "pilot")}
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">{name}</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("../")}'''
    os.makedirs(f"{ROOT}/sectors",exist_ok=True)
    open(f"{ROOT}/sectors/{slug}.html","w",encoding="utf-8").write(head+body)
for _t in SECTORS: sector_page(_t)

# ----- FAQ -----
FAQ=[
 ("Does any of our data leave the site?","Not by default. AgentMesh is air-gapped on your factory network. Raw signals, images and models stay on site. Only what you choose goes out, such as work orders to your maintenance system. AgentNexus can connect to your ERP and to approved AI models for business skills such as quotes and quality reports, through one gate you control. That traffic goes through one logged gate you control, a named person approves every draft, and on controlled programs it stays off."),
 ("What happens when the internet or site link drops?","Nothing changes at the machine. Each AgentMesh pod decides locally and keeps running. Findings for AgentNexus wait and sync when the link returns."),
 ("Is Unovie a safety system?","No. AgentMesh is never on the path that moves equipment, and we make no SIL claim. It acts on its own only on low-risk outputs, such as a reject gate or a rework diverter. Anything safety-related becomes an alarm and a request. Your PLC, safety system and operators decide."),
 ("What hardware does it run on?","Unovie's custom-built AMD or NVIDIA hardware accelerators. The AgentMesh pod is a compact 3U unit on AMD Ryzen AI Max+ 395. NVIDIA Jetson AGX Thor handles robotics and vision at the tool. NVIDIA DGX Spark is the engineering lab."),
 ("Do we have to buy the hardware?","No. We supply it set up and tested. You can buy it, or take it as a service with no upfront hardware cost."),
 ("What does a pilot cost?","The site audit is free: 1–2 days on site, then written findings and a pilot plan. The 6-week paid pilot is $40–60K. It is credited in full against a production site signed within 90 days."),
 ("What do we get at the end of the pilot?","One domain kit running on your own data, a baseline ROI view, a measured latency report and a signed evidence pack of what the system did and why."),
 ("How is production priced?","Per monitored asset and domain kit. Never per seat or per camera. We quote production after the pilot, when we both know the asset count and the value."),
 ("How fast can we reach production?","Our target is about one quarter from the end of the pilot. The pilot's setup carries straight over."),
 ("Which systems does it connect to?","Sensors, robot controllers, vision stations, test rigs, PLCs, MES and quality systems, historians, and work-order systems such as SAP and Maximo. Protocols include OPC UA, EtherCAT and Modbus. PLC connections are read-only except for the outputs you agree to."),
 ("Do you follow an industry standard for describing machines?","AgentMesh describes every device with its limits, and the pod enforces them. A language model never operates your equipment. We keep our device descriptions standard-neutral, so we can adopt a published industry standard when one is ready."),
 ("Is it certified or compliant with NIST, CMMC or IEC 62443?","Unovie is designed against NIST SP 800-53 and the NIST AI RMF. It produces evidence your team can use for SP 800-171 and CMMC or IEC 62443. Your assessor decides compliance, not a product."),
 ("Does the AI change itself over time?","Only after testing. Nothing new switches on until it has proven itself on cases it has never seen. Every change is signed, logged and can be rolled back."),
 ("Do you train on our data for other customers?","No. Models improve on your site, from your data. Nothing is shared back to Unovie or to other customers."),
 ("How does it work inside?","Our engineers can walk you through how it works. Talk to our engineers through the contact page and we will set up a call."),
 ("Where are your engineers?","Unovie is based in Austin, Texas. Our engineers work on site across Texas and serve customers nationally."),
]
import json as _jfaq
_ld=_jfaq.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]},ensure_ascii=False)
_items="".join(f'<details class="faq rv"{" open" if i<3 else ""}><summary><span class="n">{i+1:02d}</span>{q}</summary><p>{a}</p></details>' for i,(q,a) in enumerate(FAQ))
faq=f'''{HEAD("","FAQ | Unovie.AI: data, safety, hardware and pilot cost","Straight answers for buyers: does data leave the site, what happens when the link drops, is it a safety system, what hardware, and what a pilot costs.")}<script type="application/ld+json">{_ld}</script>{NAV("")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">FAQ</span></div>
  <div class="tag rv">FAQ <span class="o">·</span> For buyers</div>
  <h1 class="rv" style="margin-top:18px">Straight answers, <span class="serif" style="color:var(--accent)">first.</span></h1>
  <p class="lead rv">What plant, quality, security and finance teams ask us before a pilot. The answer comes first.</p>
</div></section>
<section><div class="wrap"><div class="faqlist">{_items}</div>{PRICE_LINE}</div></section>
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Still have a question?</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("")}'''
open(f"{ROOT}/faq.html","w",encoding="utf-8").write(faq)

# ----- CASE STUDY (anonymized; source: businessplan/case-study.md) -----
cs=f'''{HEAD("../","Case study: AI-driven certification for satellite set-top boxes | Unovie.AI","How Unovie built an air-gapped, GPU-accelerated verification platform for a national satellite pay-TV provider in twelve months: 16 boxes per stream, detection mAP 0.836 to 0.961, audio certified on 16 of 16 boxes.")}{NAV("../")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="../index.html">Home</a><span class="sep">/</span><a href="../index.html#resources">Research</a><span class="sep">/</span><span style="color:var(--fg-mut)">Case study</span></div>
  <div class="tag rv">Case study <span class="o">·</span> Device test automation <span class="o">·</span> 12 months</div>
  <h1 class="rv" style="margin-top:18px">One year, one platform: <span class="serif" style="color:var(--accent)">AI-driven certification for satellite set-top boxes.</span></h1>
  <p class="lead rv">A national satellite pay-TV provider asked us to replace manual set-top box testing with automation they could trust. In twelve months we designed, built and deployed an air-gapped, GPU-accelerated verification platform in their device lab. It presses real remote buttons, watches the real video output, judges what it sees and hands engineers an evidenced verdict. By the end of the year the whole QA team could test at once, the client was building its own vision models in-house, and every result could be read in plain English.</p>
  {metrics([("19 / 19","verification features delivered and verified"),("16","boxes verified in parallel from one 4K stream"),("0.836 → 0.961","detection mAP after one in-house retrain"),("16 / 16","boxes per stream with audio certified, up from 0"),("8","equipment rooms on one rack blueprint"),("0","bytes of test data leaving the lab")])}
</div></section>
{S("01","At a glance","The engagement.", _ctable(["",""],[("<b>Client</b>","National satellite pay-TV provider (name withheld)"),("<b>Problem</b>","Manual, unrepeatable certification of set-top box firmware across six product lines"),("<b>Deployment</b>","Air-gapped, on-premise NVIDIA GPU fabric inside the client's device lab"),("<b>Duration</b>","12 months, from first design to lab-wide operation"),("<b>Design scale</b>","128 boxes per rack · 50 racks · 6,400 devices · 300 ms from frame to verdict (design targets)")]))}
{S("02","The problem","A tester, "+A_+"a remote and a screen."+E_, disc([
  ("/manual","Manual and unrepeatable","Coverage was whatever one person could get through in a day, and no two runs were quite the same.",[]),
  ("/brittle","Brittle when automated","Earlier tools compared screenshots pixel by pixel. A font tweak or a new promo tile broke the test, so most failures were the tool's fault.",[]),
  ("/evidence","Verdicts without evidence","A note in a spreadsheet is a recollection. An annotated proof frame and a log start a different conversation with a developer.",[]),
  ("/audio","No audio at scale","One capture stream showed sixteen boxes, but the audio path reached one box at a time, so audio wasn't verified at scale at all.",[])]),
  "The lab certifies every firmware build for six product lines, each with several versions in test at once. The goal was never to review faster. It was to make exhaustive certification cheaper than sampling.")}
{S("03","Why it's hard","Thousands of screens, "+A_+"judged in 300 ms."+E_, _ctable(["Design target","Per stream","Per rack (128 boxes)","Full build-out (50 racks)"],[
  ("Devices under test","16","128","6,400"),("4K capture streams","1","8","400"),("Device-lane frames per second","960","7,680","384,000"),("Uncompressed video","~6 Gbps","~48 Gbps","~2.4 Tbps"),("Capture → verdict","300 ms","300 ms","300 ms")])
  + '<p class="illus rv" style="margin-top:10px">Engineering estimates at 60 fps, 8-bit 4:2:0 video · design targets, not measured</p>'
  + disc([("/copy","Moving data is the bottleneck","At terabits per second of decoded video, frames can't be copied through the CPU. Every step has to run in GPU memory.",[]),
          ("/time","Failures happen over time","Freeze, macroblocking, stuck splash screens and audio dropouts only show across a sequence of frames.",[]),
          ("/matrix","A matrix, not a checklist","Six product lines × several firmware versions: the same check has a different correct answer on each.",[]),
          ("/physical","Physical control at scale","Every verdict starts with a real IR keypress. Thousands of remotes need scheduling, with hardware locked so jobs never collide.",[])]))}
{S("04","What we delivered","An engine, "+A_+"then a platform."+E_, disc([
  ("/engine","The verification engine","Drives the remote, reads the screen with detection and OCR, judges A/V health on the GPU and attaches proof frames and a written report to every verdict. Sixteen boxes per 4K stream, sliced on the GPU. Tests are configuration, not code.",["19 of 19 features","on schedule"]),
  ("/factory","The model factory","An on-premise path from raw footage to labelled dataset to trained, versioned model. The client now retrains its own detectors: mAP rose from 0.836 to 0.961 in one cycle.",["in-house models","versioned"]),
  ("/channels","Adding a channel is a data task","Channels are matched against a managed library of reference images, so a new or rebranded channel needs a picture, not a retrain. The library rebuilds in under two seconds. Below a confidence margin the answer is “unknown” and a person looks.",["no retraining","honest unknown"]),
  ("/scheduling","Lab-wide scheduling","The whole QA team tests at once across 8 equipment rooms, with hardware locked per job, per-user attribution, a full audit trail and inventory synced from the client's own configuration database.",["no collisions","audit trail"]),
  ("/language","A private language layer","Plain-English reports and plain-English test authoring, on separate inference hardware inside the lab. Facts such as channel numbers come from configuration, never from the model.",["no cloud","no made-up facts"]),
  ("/audio","Audio, from zero to sixteen","Networked control of the audio routing lets one scenario step cycle through every box and check measured signal level, so audio is certified on all sixteen paths.",["16 / 16","measured signal"])]))}
{S("05","Results","After "+A_+"twelve months."+E_, _ctable(["Outcome","What changed"],[
  ("Automation the team trusts","Interpretation replaced screenshot comparison, so harmless UI changes no longer cause false failures."),
  ("Evidence on every verdict","Pass, fail or partial, each with an annotated proof frame and a per-lane log, one click away."),
  ("In-house model ownership","The client builds, versions and retrains its own models."),
  ("Flat cost as the line-up grows","New and rebranded channels take minutes, not a retraining project."),
  ("Fails safely","Low-confidence frames return “unknown” and go to a person. The system never guesses."),
  ("Data sovereignty","Fully air-gapped. No footage, labels, models or results leave the lab.")]))}
{S("06","What carries over","The same discipline, "+A_+"on the factory floor."+E_, disc([
  ("/vision","Vision QA at the line","GPU video pipelines that judge what they see, not pixel diffs, are the core of our Vision Quality Inspection kit and DeepVision at the cell.",["Vision QA","DeepVision"]),
  ("/evidence","Evidence first","Every verdict carries its proof. In AgentMesh that is the signed Evidence Log.",["Evidence Log"]),
  ("/data","Change without retraining","Where the business changes often, the change goes into reference data a person can manage, not into the model. A new channel needed a picture, not a project.",["reference data"]),
  ("/sovereign","Air-gapped by default","Nothing left the lab. Nothing leaves your site either.",["air-gapped"])]),
  "This project was in media device testing, not manufacturing. What carries over is how it was engineered.")}
<section><div class="wrap"><p class="illus rv">Client details are withheld under confidentiality. Year-one results were measured in the client's lab; scale figures are engineering design targets.</p></div></section>
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Still checking by hand?</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Tell us about one line or one problem. An engineer will show you what Unovie would watch, what it would catch and what it would hand your team.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Talk to our engineers <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("../")}'''
open(f"{ROOT}/resources/case-study-device-certification.html","w",encoding="utf-8").write(cs)

# ----- CASE STUDY 2 (anonymized): video decisions at the edge (18 Nov 2026; source: vision edge-AI proposal, public tier only) -----
uc=f'''{HEAD("../","Case study: camera AI that decides on site for a semiconductor manufacturer | Unovie.AI","How Unovie proved vision AI for a semiconductor manufacturer: 300+ frames per second analysed on site in the MVP, sized for 25 cameras per chamber and 40 chambers per site, with nothing sent off site to decide.")}{NAV("../")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="../index.html">Home</a><span class="sep">/</span><a href="../index.html#resources">Research</a><span class="sep">/</span><span style="color:var(--fg-mut)">Case study</span></div>
  <div class="tag rv">Case study <span class="o">·</span> Vision at the edge <span class="o">·</span> Semiconductor</div>
  <h1 class="rv" style="margin-top:18px">A thousand cameras, <span class="serif" style="color:var(--accent)">and every decision made on site.</span></h1>
  <p class="lead rv">A semiconductor manufacturer wanted cameras watching every chamber on its lines: 25 cameras per chamber, 40 chambers per site. Nobody can watch a thousand feeds, and sending them all to the cloud would have been slow, expensive and a risk for sensitive footage. They had only a couple of dozen labelled images to start from. We proved the approach in an MVP on their own footage, analysing more than 300 frames per second on site, then designed the site so the vision AI runs next to the cameras, every feed is checked as it arrives, and the video stays in the building.</p>
  {metrics([("25","cameras per chamber"),("40","chambers per site"),("1,000","camera feeds watched"),("300+","frames per second analysed on site in the MVP")])}
</div></section>
{S("01","At a glance","The engagement.", _ctable(["",""],[("<b>Client</b>","Semiconductor manufacturer (name withheld)"),("<b>Problem</b>","Cameras on every chamber, but no way to watch or act on a thousand feeds in time"),("<b>Starting point</b>","About 25 labelled images and a few videos"),("<b>Scope</b>","25 cameras per chamber · 40 chambers per site · about 21 TB of video a month"),("<b>Deployment</b>","On site, next to the cameras, on NVIDIA Jetson hardware accelerators. No cloud in the decision path"),("<b>Engagement</b>","MVP on the customer's own footage, then a site design sized from the MVP results"),("<b>MVP result</b>","300+ frames per second analysed on site, on the customer's own footage")]))}
{S("02","The problem","Too many cameras, "+A_+"not enough eyes."+E_, disc([
  ("/eyes","Nobody watches the feeds","Cameras get installed for safety and quality, then mostly record. Problems are found later, on a replay, after the parts are scrapped.",[]),
  ("/cloud","The cloud adds delay","A round trip to the cloud adds delay and depends on the network link. A decision that matters on the line can't wait for either.",[]),
  ("/cost","Costs grow with every camera","Per-camera cloud pricing looks small at ten cameras. At a thousand, it becomes one of the biggest lines in the budget.",[]),
  ("/models","Models go stale","Lighting, fixtures and products change. A model set up once and left alone gets worse every month.",[])]))}
{S("03","What we built","Watch every feed, "+A_+"flag what matters."+E_, disc([
  ("/edge","Decides next to the camera","Each feed is checked as it arrives, on hardware in the customer's building. No cloud round trip, and it keeps working if the internet link drops.",["on site","no round trip"]),
  ("/proof","Shows its proof","Every flag comes with the frame and a short note on what was seen, sent to the operator or engineer who owns that chamber.",["proof frame","right person"]),
  ("/hands","People decide","The system flags and asks. It never moves equipment. The customer's control systems and people decide what happens next.",["alarm and request","no equipment control"]),
  ("/fresh","Stays accurate","Starting from about 25 labelled images, we built the first models and look after them from there. Improvements are tested on the customer's own footage before they go live, and can be rolled back.",["tested on your data","reversible"])]))}
{S("04","What the site gets","Built for "+A_+"the factory floor."+E_, _ctable(["",""],[
  ("<b>Cameras</b>","Rugged industrial cameras, made in the USA and NDAA compliant, with depth sensing and night vision. Existing cameras can be used too."),
  ("<b>On-site AI hardware</b>","Unovie's custom-built NVIDIA Jetson hardware accelerators, sized to the site's camera count. Keeps running if one unit fails."),
  ("<b>Video stays on site</b>","Footage is analysed and kept on site. Archiving it anywhere else is the customer's choice, not a requirement."),
  ("<b>Connected to existing systems</b>","Flags go to the existing alarms, MES, quality and work-order systems."),
  ("<b>Looked after</b>","Model updates, hardware support and monitoring included. Buy the hardware or take it as a service.")]))}
{S("05","What carries over","The same engine, "+A_+"on other lines."+E_, disc([
  ("/test","Test stands","Watches a test run alongside the sensors and flags anything unusual to the test conductor as it happens.",["space &amp; aerospace"]),
  ("/weld","Battery welds and tabs","Checks welds and tab alignment in line, together with the process signals for the same cell.",["battery"]),
  ("/robot","Robot cells","Spots misplaced parts and drifting motions before they turn into scrap or a stopped cell.",["robotics"]),
  ("/dock","Conveyors and docks","Watches jams, spills and blocked lanes on conveyors and loading docks and alerts the shift lead.",["material handling"])]),
  "This project was in a chip fab. The same engine is set up for other lines during a pilot, on their own footage.")}
{S("06","How we start","Small, "+A_+"then site-wide."+E_, _ctable(["Step","What happens"],[
  ("<b>Site audit</b>","No charge, 1–2 days. An engineer walks your floor, looks at your cameras and network, and picks the first tools to watch."),
  ("<b>6-week pilot</b>","A handful of cameras on one tool, on your own footage, with a results report you can check."),
  ("<b>Production</b>","Roll out chamber by chamber, then site by site, in about a quarter.")]))}
<section><div class="wrap"><p class="illus rv">Customer details are withheld under confidentiality. The 300+ frames per second was measured in the MVP on the customer's own footage. Camera, chamber and video figures are the customer's site requirements.</p></div></section>
<section id="contact"><div class="wrap"><div class="cta-final rv">
  <div class="tag" style="color:var(--accent);justify-content:center;display:flex">Cameras already on the line?</div>
  <h2 style="margin-top:16px">See how our systems can help <span class="serif" style="color:var(--accent)">your line</span>.</h2>
  <p class="lead">Book a short live demo. We'll show the vision engine checking a camera feed on site, and talk through what it would watch on your floor.</p>
  <div class="cta" style="justify-content:center"><a class="btn btn-big" href="/contact.html">Book a demo <span class="ar">→</span></a></div>
</div></div></section>
{FOOTER("../")}'''
open(f"{ROOT}/resources/case-study-vision-edge.html","w",encoding="utf-8").write(uc)


# =====================================================================
# BLOG  (17 Nov 2026) — blog/index.html + blog/<slug>.html. Public tier only: outcomes and
# promises, never how the system works (brand/public-disclosure.md). Newest first.
# =====================================================================
BLOG=[
 dict(slug="every-flight-is-a-test-run",
      date="17 November 2026", iso="2026-11-17", sector="Space &amp; aerospace",
      title="Every flight is a test run now.",
      dek="On 14 November a Starship upper stage came back from orbit and landed for the first time. Reuse moves the bottleneck to the ground: reading the data from the last flight before the next one.",
      img="space-reuse-mp", video=True,
      body="""
<p>On Saturday, 14 November 2026, SpaceX landed a Starship upper stage that had been to orbit, a first for the program (<a href="https://www.space.com/news/live/spacex-starship-flight-15-live-updates-nov-14-2026-starship-first-double-landing-attempt" target="_blank" rel="noopener">Space.com</a>). It's a milestone worth thinking about for anyone who builds and tests flight hardware, because of what reuse does to the work on the ground.</p>

<h2>Reuse turns every flight into a test run</h2>
<p>When a vehicle is thrown away after one flight, its data is read once, for lessons. When the same vehicle flies again, the data from each flight decides whether that particular unit is ready for the next one. The same holds on the ground. Engines go back on the stand more often, and each static fire, acceptance run and qualification test adds to the record of one specific piece of hardware.</p>
<p>So the time between flights starts to depend on something that isn't hardware at all: how quickly engineers can read what the last run recorded, and how confident they are in what they found.</p>

<h2>The bottleneck is reading, not recording</h2>
<p>Test programs already record far more than people can watch. A single run produces pressure, strain, temperature and high-rate acoustic and vibration channels, more than anyone can watch at once. The high-rate ones add up fast. One tri-axial vibration sensor sampled at 25.6 kHz with 24-bit samples produces about 20 GB a day:</p>
<p class="math">25,600 samples/s × 3 axes × 3 bytes × 86,400 s ≈ 19.9 GB per day</p>
<p>In most programs, people still read these channels after the run, a few at a time, against their memory of earlier runs. Test cadence is rising faster than the number of engineers who can do that.</p>

<h2>Reading the run while it happens</h2>
<p>The reading can start sooner. Every channel can be compared with similar past runs while the run is still going, so the test conductor sees an anomaly as it happens instead of in next week's review. By the time the stand goes quiet, the post-test report can already be drafted, with the flagged moments and the most similar past runs attached, ready for an engineer to check and sign. And the record of each part, from lot and build step to every test it has seen, can stay complete as the same hardware flies again.</p>
<p>None of this needs to sit inside the qualified test system. It can run beside it, read-only, with the test conductor still making every call and nothing commanding the stand or the vehicle. Test data and drawings for export-controlled programs can stay on site, inside the security boundary they already live in.</p>
<p>This is the work our Test Campaign Monitor does on <a href="../platform/agentmesh.html">AgentMesh</a>, with advisory flags within a 30 ms target and a language model never on the path that moves equipment.</p>

<h2>If you run a test program</h2>
<p>We're always glad to compare notes with test teams. Want to see how it works? Our engineers can walk you through it.</p>
<p><a href="../sectors/space.html">More on space &amp; aerospace →</a> &nbsp;·&nbsp; <a href="/contact.html">Talk to our engineers →</a></p>
<p class="disclose">Unovie has no relationship with SpaceX. Figures marked "target" are design targets, not measurements. Event details from public reporting at the time of writing.</p>
"""),
]

def _blogfig(b, base):
    src=f"{base}assets/images/blog/{b['img']}"
    if b.get("video"):
        m=f'<video autoplay loop muted playsinline poster="{src}.jpg" aria-label="Illustration: {b["title"]}"><source src="{src}.mp4" type="video/mp4"></video>'
    else:
        m=f'<img src="{src}.jpg" alt="Illustration: {b["title"]}">'
    return f'<figure class="postfig rv">{m}<figcaption>Illustration · targets, not measurements</figcaption></figure>'

os.makedirs(f"{ROOT}/blog",exist_ok=True)
for b in BLOG:
    plain=re.sub('<[^>]+>','',b["title"])
    html=f'''{HEAD("../", f"{plain} | Unovie.AI blog", re.sub('<[^>]+>','',b["dek"])[:155])}
{NGBG}{NAV("../")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="../index.html">Home</a><span class="sep">/</span><a href="index.html">Blog</a><span class="sep">/</span><span style="color:var(--fg-mut)">{b["sector"]}</span></div>
  <div class="meta rv" style="font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--fg-dim)">{b["date"]} · {b["sector"]}</div>
  <h1 class="rv" style="margin-top:14px">{b["title"]}</h1>
  <p class="lead rv">{b["dek"]}</p>
</div></section>
<section style="padding-top:0"><div class="wrap"><article class="post">
{_blogfig(b,"../")}
{b["body"]}
</article></div></section>
{FOOTER("../")}'''
    open(f"{ROOT}/blog/{b['slug']}.html","w",encoding="utf-8").write(html)

_cards="".join(f'''<a class="bcard rv" href="{b['slug']}.html" data-cursor><img src="../assets/images/blog/{b['img']}.jpg" alt=""><div><div class="meta">{b["date"]} · {b["sector"]}</div><h3>{b["title"]}</h3><p>{b["dek"]}</p><span class="go" style="color:var(--accent)">Read →</span></div></a>''' for b in BLOG)
open(f"{ROOT}/blog/index.html","w",encoding="utf-8").write(f'''{HEAD("../","Blog | Unovie.AI","Field notes from Unovie's engineers on Physical AI for battery, chip, space, robotics, defense and advanced energy manufacturing.")}
{NGBG}{NAV("../")}
<section class="phero"><div class="wrap">
  <div class="crumb rv"><a href="../index.html">Home</a><span class="sep">/</span><span style="color:var(--fg-mut)">Blog</span></div>
  <h1 class="rv">Field notes <span class="serif" style="color:var(--accent)">from the floor.</span></h1>
  <p class="lead rv">What our engineers see on test stands, lines and fleets, and what it means for Physical AI in next-generation manufacturing.</p>
</div></section>
<section style="padding-top:0"><div class="wrap"><div class="bloglist">{_cards}</div></div></section>
{FOOTER("../")}''')

# ---- sitemap.xml + robots.txt (Google indexing) ----
SITE="https://unovie.ai"
LASTMOD="2026-11-14"   # bump when content materially changes (kept fixed for idempotent builds)
def _u(path):  # path relative to site root; "" = homepage
    return SITE + "/" + path
_pages=["", "about.html", "why-unovie.html", "contact.html",
        "resources/edge-ai-models.html", "resources/edge-ai-whitepaper.html", "gpu-edgegateway-whitepaper.html", "ai-soc-modernization-whitepaper.html"]
_pages += [f"solutions/{s[0]}.html" for s in SOL]
_pages += [f"platform/{s[0]}.html" for s in PLATP]
_pages += ["device-platform.html", "faq.html", "resources/case-study-device-certification.html", "resources/case-study-vision-edge.html"]
_pages += [f"sectors/{t[0]}.html" for t in SECTORS]
_pages += ["blog/index.html"] + [f"blog/{b['slug']}.html" for b in BLOG]
_pages += ["resources/medsdlc-html/"+p for p in ("index.html","exec-brief.html","01-requirements.html","02-maturity-model.html","03-reference-architecture.html","04-model-strategy-and-finetuning.html","05-evaluation-and-validation.html","06-agentic-workflows.html","07-security-and-compliance.html","08-token-and-gpu-economics.html","09-adoption-roadmap.html","scorecard.html","diagrams.html")]
def _prio(p):
    if p=="": return "1.0"
    if p=="why-unovie.html": return "0.8"
    if p=="device-platform.html" or p.startswith(("solutions/","platform/","sectors/")): return "0.9"
    if p=="faq.html": return "0.8"
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
    return ("home" if p=="" else "sector" if p.startswith("sectors/") else "faq" if p=="faq.html" else "solution" if p.startswith("solutions/") else "platform" if p.startswith("platform/") else "device" if p=="device-platform.html"
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

> Physical AI for your factory floor. Unovie designs, builds and operates custom Edge-AI Agentic Systems for battery, chip, space, robotics, defense and advanced energy manufacturers, at a fixed scope and cost, on Unovie's custom-built AMD or NVIDIA hardware accelerators. AgentMesh puts AI at the machine, on every signal a next-generation line produces. AgentNexus runs AI agents across every site. A language model is never on the path that moves equipment, and every decision is recorded in a signed Evidence Log.

Figures on this site marked "target" are design targets, not measurements.

## About Unovie
- An engineering-first, AI-native company in Austin, Texas, serving customers nationally.
- Founders with 20+ years each in OT and Physical AI. Four years building the platform.
- Customers: next-generation manufacturers in battery and energy storage, chip fabs and their suppliers, space and aerospace, robotics and autonomous systems, defense and dual-use manufacturing, and advanced energy and nuclear (non-safety roles only).
- Safety boundary: Unovie is not a safety system and makes no SIL claim. Safety decisions stay with the customer's PLC, safety system and operators.
- Security: designed against NIST SP 800-53 and the NIST AI RMF (designed against, not certified). Compliance is decided by the customer's assessor.

## How Unovie engages
1. Site audit: no charge, 1–2 days on site.
2. Paid pilot: 6 weeks, $40–60K, one domain kit on the customer's own data. Credited in full against a production site signed within 90 days.
3. Production: about one quarter after the pilot.
4. Fleet: new lines and sites reuse the same setup; AgentNexus connects them.
Pricing is per monitored asset and domain kit, never per seat or per camera. Hardware can be bought or taken as a service.

## Platform
- [AgentMesh]({_u('platform/agentmesh.html')}): AI at the machine, on every signal a next-generation line produces: robots, vision, sensors and test rigs. A compact 3U pod at the line, air-gapped. Decides within 30 ms (target). Acts only on low-consequence outputs, such as a reject gate or a rework diverter. Anything touching safety becomes an alarm and a request that the PLC, cell controller and operators decide. Every device is described with its limits, and the pod enforces them.
- [AgentNexus]({_u('platform/agentnexus.html')}): AI agents working across every site. Drafts maintenance plans, NCRs, quality records and work orders for a named person to approve. Answers within 0.5 s (target). Never moves equipment. Runs in the customer's own enclave, as one rack for the whole fleet. Connects out only through one gate the customer controls and can audit (the customer's ERP and approved AI models, in design). Private work stays local.
- Evidence Log: a signed record of every decision that the customer can audit.
- Safe updates: improvements are tested, signed and reversible. Nothing new switches on until it has proven itself on cases it has never seen.
- Operator HMI: each AgentMesh pod has an operator screen; AgentNexus has a fleet screen.
- Engineering teams can book an architecture walkthrough with our engineers: {_u('contact.html')}

## Agentic jobs
Packaged domain kits, deployed in weeks:
- Robot & Motion Health: joint, servo and gearbox drift caught before it scraps parts or stops the line.
- Vision Quality Inspection: DeepVision at the cell, on NVIDIA Jetson AGX Thor.
- Battery Line & Storage Safety: weld and formation checks in line; thermal-runaway warning on storage sites (alarm only).
- Fab Utilities Watch: pumps, chillers, scrubbers and gas systems at the fab and its suppliers.
- Electrical Health: drives, inverters and switchgear.
- Test Campaign Monitor: flags to the test conductor during a run; post-test report drafted.
- Factory Network Watch: unauthorized writes and unusual commands on the factory network.
- Quality Records & NCRs: drafted for sign-off, in English or Spanish.

## Sectors
- [Battery & energy storage]({_u('sectors/battery.html')}): cell lines and storage sites.
- [Chip fabs & suppliers]({_u('sectors/fabs.html')}): fab utilities and supplier plants.
- [Space & aerospace]({_u('sectors/space.html')}): test stands and vehicle lines.
- [Robotics, drones & autonomy]({_u('sectors/robotics.html')}): robot cells, drones and vessels.
- [Defense & dual-use]({_u('sectors/defense.html')}): shipyards and dual-use factories.
- [Advanced energy & nuclear]({_u('sectors/energy.html')}): balance of plant, non-safety only.
- [FAQ]({_u('faq.html')}): data, safety, hardware and pilot cost.

## Hardware
All options run the same platform on Unovie's custom-built AMD or NVIDIA hardware accelerators.
- [AMD Ryzen AI Max+ 395]({_u('device-platform.html')}#ryzen-ai-max-395): the AgentMesh pod at the line and the AgentNexus rack for the fleet. Runs today.
- [NVIDIA Jetson AGX Thor]({_u('device-platform.html')}#agx-thor): robotics and DeepVision at the tool. Available per project.
- [NVIDIA DGX Spark]({_u('device-platform.html')}#dgx-spark): the AI engineering lab and a small AgentNexus for one site. Available per project.
- [Qualcomm QCS6490]({_u('device-platform.html')}#qcs6490): mobile and remote equipment, feeding the nearest AgentMesh pod.

## Resources
- [Case study: AI-driven certification for satellite set-top boxes]({_u('resources/case-study-device-certification.html')}): an anonymized 12-month project in a device test lab (not a factory). 16 boxes verified per 4K stream, detection mAP 0.836 to 0.961 after one in-house retrain, audio certified on 16 of 16 boxes, 0 bytes of test data leaving the lab.
- [Case study: camera AI that decides on site in a chip fab]({_u('resources/case-study-vision-edge.html')}): an anonymized semiconductor manufacturer. 25 cameras per chamber, 40 chambers per site, about 21 TB of video a month kept on site; proved in an MVP on the customer's own footage (300+ frames per second analysed on site), starting from about 25 labelled images.
- [Edge AI Models: Field Guide (summary)]({_u('resources/edge-ai-models.html')}): a summary. Request the full guide: {_u('request.html')}?doc=edge-ai-models
- [Training Without Retraining (summary)]({_u('resources/edge-ai-whitepaper.html')}): custom models on the edge. Request the full guide: {_u('request.html')}?doc=training-without-retraining
- [Edge-Native Economics: Whitepaper]({_u('gpu-edgegateway-whitepaper.html')}): predictable AI cost at the industrial edge.
- [AI SOC Modernization: Whitepaper]({_u('ai-soc-modernization-whitepaper.html')}): security for IT and OT networks.
- [Agentic SDLC for Regulated MedTech]({_u('resources/medsdlc-html/index.html')}): software development for FDA / IEC 62304 medical-device engineering.

## Blog
- [Blog]({_u('blog/index.html')}): field notes from Unovie's engineers.
- [Every flight is a test run now]({_u('blog/every-flight-is-a-test-run.html')}): reuse in space programs moves the bottleneck to reading test data; how Test Campaign Monitor helps, beside the qualified test system.

## Company
- [Why Unovie]({_u('why-unovie.html')}): veteran founders, Austin, Texas, pilot to production in about a quarter.
- [About]({_u('about.html')}): Physical AI for deep-tech industries.
- [Contact]({_u('contact.html')}): the contact form. Site audit at no charge, then a 6-week paid pilot.
- [LinkedIn](https://www.linkedin.com/company/unovie/): company page.

## Machine-readable
- [Full content (llms-full.txt)]({SITE}/llms-full.txt): the public site as one markdown document.
- [Vector index (JSON)]({SITE}/agents/index.json): chunked content records for RAG.
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
