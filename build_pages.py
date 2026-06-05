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
     "--w:74%":"food-safety","--w:70%":"batch-optimization","--w:66%":"remote-expertise"}
for w,slug in ACC.items():
    idx=idx.replace(f'<div class="acard rv" style="{w}">',
                    f'<div class="acard rv" data-href="solutions/{slug}.html" data-cursor style="{w}">',1)
PLAT={"Edge Data Fabric":"edge-data-fabric","Edge Streaming Analytics":"edge-streaming-analytics",
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
    <a href="{base}platform/edge-data-fabric.html">Edge Data Fabric</a><a href="{base}platform/edge-streaming-analytics.html">Streaming Analytics</a>
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

def page(base, folder, slug, cat, crumb_cat, title_html, lead, kpis, feats, hows, cta_lead):
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
 ("food-safety","Food processing","Food Safety <span class='serif' style='color:var(--accent)'>Monitoring</span>",
  "Monitor food-safety parameters in real time at the edge — temperature, contamination signals, process drift — and act before incidents happen.",
  [("−30<span class='o'>%</span>","contamination"),("+20<span class='o'>%</span>","customer CSAT"),("continuous","monitoring")],
  ("Catch it before it ships",[("/sense","Parameter monitoring","Real-time temperature, humidity, and process signals.",["temp","process"]),
   ("/anomaly","Anomaly detection","Spots contamination signatures early.",["anomaly","early"]),
   ("/log","Compliance logging","Continuous, audit-ready records.",["HACCP","audit"])]),
  ("Sense to record",[("Sense","Capture line parameters."),("Detect","Flag anomalies."),("Alert","Stop &amp; notify."),("Record","Compliance trail.")]),
  "Ship safe. <span class='serif' style='color:var(--accent)'>Every batch.</span>"),
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
  "A typed knowledge graph + vector memory of your domain that grows with every document and grounds every answer in source records — on-prem.",
  [("graph<span class='s'>+vector</span>","unified memory"),("on-prem","data never leaves"),("real-time","ingest")],
  ("Context that compounds",[("/ingest","Continuous ingest","Documents and streams become typed, queryable structure.",["typed","incremental"]),
   ("/search","Hybrid search","BM25 + dense vectors for grounded retrieval.",["BM25","vector"]),
   ("/isolation","Tier isolation","Per-collection, per-tier boundaries kept end to end.",["multi-tenant","governed"])]),
  ("Ingest to serve",[("Ingest","Walk &amp; dedupe sources."),("Structure","Extract typed entities."),("Index","Graph + vector."),("Serve","Grounded answers.")]),
  "Know what you know — and <span class='serif' style='color:var(--steel)'>why.</span>"),
 ("edge-streaming-analytics","Platform","Edge Streaming <span class='serif' style='color:var(--steel)'>Analytics</span>",
  "Run inference on live streams at the edge — sensors, cameras, telemetry — with millisecond decisions and zero cloud round-trip.",
  [("ms","decision latency"),("on-edge","inference"),("24/7","offline-capable")],
  ("Decisions on the wire",[("/ingest","Stream ingest","High-throughput connectors for live sources.",["kafka","mqtt"]),
   ("/infer","On-edge inference","NVFP4-accelerated models score events in flight.",["NVFP4","low-latency"]),
   ("/alert","Real-time alerting","Thresholds, anomalies, and routed actions.",["alerting","actions"])]),
  ("Stream to action",[("Ingest","Connect live streams."),("Infer","Score in flight."),("Detect","Anomaly &amp; threshold."),("Act","Alert or actuate.")]),
  "Real-time, <span class='serif' style='color:var(--steel)'>actually.</span>"),
 ("gpu-microcloud","Platform","GPU <span class='serif' style='color:var(--steel)'>MicroCloud</span>",
  "On-prem GPU as a managed, scheduled, metered resource — multi-tenant isolation with chargeback, so your hardware runs like a private cloud.",
  [("MIG","hard isolation"),("scheduled","fair-share"),("metered","chargeback")],
  ("Your GPUs, run like cloud",[("/schedule","Workload scheduling","Fair-share scheduling across teams and jobs.",["queue","priority"]),
   ("/isolate","Multi-tenant isolation","MIG partitioning keeps tenants apart.",["MIG","secure"]),
   ("/meter","Metering &amp; chargeback","Per-tenant accounting for real cost visibility.",["metering","reports"])]),
  ("Pool to bill",[("Pool","Aggregate edge GPUs."),("Schedule","Place workloads."),("Isolate","Partition tenants."),("Meter","Account &amp; bill.")]),
  "Datacenter discipline, <span class='serif' style='color:var(--steel)'>on-prem.</span>"),
 ("gpu-edgegateway","Platform","GPU <span class='serif' style='color:var(--steel)'>EdgeGateway</span>",
  "Secure, OpenAI-compatible model serving at the perimeter — auth, routing, and token-aware load balancing across your edge backends.",
  [("OpenAI","compatible API"),("token-aware","routing"),("authd","per-route")],
  ("One endpoint, many models",[("/api","OpenAI-compatible","Drop-in endpoint for any compatible client.",["/v1","drop-in"]),
   ("/auth","Auth &amp; routing","OIDC/JWT with per-route role rules.",["OIDC","RBAC"]),
   ("/lb","Token-aware LB","Routes by load across vLLM / Ollama backends.",["vLLM","balance"])]),
  ("Request to response",[("Authenticate","Validate identity &amp; role."),("Route","Pick the backend."),("Serve","NVFP4 fast path."),("Observe","Meter &amp; log.")]),
  "Serve models <span class='serif' style='color:var(--steel)'>safely.</span>"),
]
for s in PLATP: page(B,"platform",s[0],s[1],"Platform",s[2],s[3],s[4],s[5],s[6],s[7])

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
