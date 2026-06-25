#!/usr/bin/env python3
"""Dependency-free static-site builder for the Agentic-Native SDLC doc set.
Converts /opt/books/docs/*.md -> /opt/books/html/*.html with light/dark themes,
Mermaid-rendered SVG, and hand-authored inline SVG architecture/workflow diagrams.
"""
import os, re, html as _html

SRC = "/opt/books/docs"
OUT = "/opt/books/html"
ASSETS = os.path.join(OUT, "assets")
os.makedirs(ASSETS, exist_ok=True)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ----------------------------------------------------------------------------
# Inline markdown -> HTML
# ----------------------------------------------------------------------------
def fix_link(url):
    url = url.strip()
    if url.startswith("http") or url.startswith("#") or url.startswith("mailto:"):
        return url
    # internal .md (optionally with #anchor)
    m = re.match(r"^([^#]+\.md)(#.*)?$", url)
    if m:
        f, anc = m.group(1), m.group(2) or ""
        base = os.path.basename(f)
        if base.lower() == "readme.md":
            base = "index.html"
        else:
            base = re.sub(r"\.md$", ".html", base)
        return base + anc
    return url

def inline(t):
    codes = []
    def grab(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)
    t = re.sub(r"`([^`]+)`", grab, t)
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
              lambda m: '<a href="%s">%s</a>' % (esc(fix_link(m.group(2))), m.group(1)), t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % esc(codes[int(m.group(1))]), t)
    return t

def slugify(s):
    s = re.sub(r"`", "", s)
    s = re.sub(r"\*\*?", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s.strip("-") or "sec"

# ----- list parsing (nested) -----
def parse_list_block(lines):
    nodes = []
    for line in lines:
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if m:
            nodes.append({"indent": len(m.group(1)),
                          "ltype": "ol" if m.group(2)[0].isdigit() else "ul",
                          "content": m.group(3), "cont": []})
        elif nodes and line.strip():
            nodes[-1]["cont"].append(line.strip())
    if not nodes:
        return ""
    pos = [0]
    def build(indent):
        ltype = nodes[pos[0]]["ltype"]
        buf = ["<%s>" % ltype]
        while pos[0] < len(nodes) and nodes[pos[0]]["indent"] >= indent:
            node = nodes[pos[0]]
            if node["indent"] > indent:           # safeguard: deeper start
                buf.append("<li>%s</li>" % build(node["indent"]))
                continue
            content = inline(node["content"])
            if node["cont"]:
                content += "<br>" + inline(" ".join(node["cont"]))
            pos[0] += 1
            child = ""
            if pos[0] < len(nodes) and nodes[pos[0]]["indent"] > indent:
                child = build(nodes[pos[0]]["indent"])
            buf.append("<li>%s%s</li>" % (content, child))
        buf.append("</%s>" % ltype)
        return "".join(buf)
    return build(nodes[0]["indent"])

# ----- table parsing -----
def is_table_sep(l):
    l = l.strip()
    if "-" not in l:
        return False
    return re.match(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$", l) is not None

def split_cells(l):
    l = l.strip()
    if l.startswith("|"):
        l = l[1:]
    if l.endswith("|"):
        l = l[:-1]
    return [c.strip() for c in l.split("|")]

def parse_table(header, sep, body):
    heads = split_cells(header)
    aligns = []
    for a in split_cells(sep):
        a = a.strip()
        if a.startswith(":") and a.endswith(":"):
            aligns.append("center")
        elif a.endswith(":"):
            aligns.append("right")
        else:
            aligns.append("left")
    while len(aligns) < len(heads):
        aligns.append("left")
    out = ['<div class="tablewrap"><table>', "<thead><tr>"]
    for i, h in enumerate(heads):
        out.append('<th style="text-align:%s">%s</th>' % (aligns[i], inline(h)))
    out.append("</tr></thead><tbody>")
    for row in body:
        cells = split_cells(row)
        out.append("<tr>")
        for i in range(len(heads)):
            c = cells[i] if i < len(cells) else ""
            al = aligns[i] if i < len(aligns) else "left"
            out.append('<td style="text-align:%s">%s</td>' % (al, inline(c)))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)

# ----- block converter -----
def md_to_html(md):
    lines = md.split("\n")
    i, n, out = 0, len(md.split("\n")), []
    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            lang = s[3:].strip().lower()
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            body = "\n".join(code)
            if lang == "mermaid":
                out.append('<pre class="mermaid">%s</pre>' % esc(body))
            else:
                rep = ascii_replace(body)
                if rep is not None:
                    out.append(rep)
                else:
                    lab = ('<span class="codelang">%s</span>' % esc(lang)) if lang else ""
                    out.append('<div class="codeblock">%s<pre><code>%s</code></pre></div>' % (lab, esc(body)))
            continue
        if s == "":
            i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1)); txt = m.group(2).strip()
            sl = slugify(txt)
            out.append('<h%d id="%s">%s<a class="anchor" href="#%s">#</a></h%d>'
                        % (lvl, sl, inline(txt), sl, lvl))
            i += 1; continue
        if re.match(r"^---+\s*$", line):
            out.append("<hr>"); i += 1; continue
        if "|" in line and i + 1 < n and is_table_sep(lines[i + 1]):
            header = line; sep = lines[i + 1]; i += 2; body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(lines[i]); i += 1
            out.append(parse_table(header, sep, body)); continue
        if s.startswith(">"):
            q = []
            while i < n and lines[i].strip().startswith(">"):
                q.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append("<blockquote>%s</blockquote>" % md_to_html("\n".join(q)))
            continue
        if re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            lst = []
            while i < n and (re.match(r"^\s*([-*+]|\d+\.)\s+", lines[i]) or
                             (lines[i][:1] == " " and lines[i].strip() != "")):
                lst.append(lines[i]); i += 1
            out.append(parse_list_block(lst)); continue
        # paragraph
        para = []
        while i < n and lines[i].strip() != "":
            l = lines[i]
            if (l.strip().startswith("```") or re.match(r"^#{1,6}\s", l)
                    or re.match(r"^\s*([-*+]|\d+\.)\s+", l) or l.strip().startswith(">")
                    or re.match(r"^---+\s*$", l)):
                break
            if "|" in l and i + 1 < n and is_table_sep(lines[i + 1]):
                break
            para.append(l.strip()); i += 1
        txt = inline(" ".join(para))
        if txt.strip():
            out.append("<p>%s</p>" % txt)
    return "\n".join(out)

# ----------------------------------------------------------------------------
# Hand-authored SVG diagrams
# ----------------------------------------------------------------------------
SVG_CLASS_CSS = """.d-card{fill:var(--card);stroke:var(--border);stroke-width:1.3}
.d-card2{fill:var(--card-2);stroke:var(--border);stroke-width:1.3}
.d-band{fill:var(--band);stroke:var(--border);stroke-width:1.3}
.d-accentbox{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.4}
.d-greenbox{fill:var(--green-soft);stroke:var(--green);stroke-width:1.4}
.d-warnbox{fill:var(--warn-soft);stroke:var(--warn);stroke-width:1.4}
.d-text{fill:var(--text)}
.d-muted{fill:var(--muted)}
.d-line{stroke:var(--line);stroke-width:1.7;fill:none}
.d-dash{stroke:var(--line);stroke-width:1.5;stroke-dasharray:6 4;fill:none}
.d-arrow{fill:var(--line)}
svg text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
"""
SVG_VARS_LIGHT = (":root,svg{--card:#ffffff;--card-2:#eef2f7;--band:#e9eef5;--text:#1b2733;"
                  "--muted:#5b6b7b;--border:#cdd6e0;--accent:#2f6fed;--accent-soft:#e7f0ff;"
                  "--green:#1f9d57;--green-soft:#e3f7ec;--warn:#c2410c;--warn-soft:#fbe9df;--line:#8aa0b6}")
SVG_VARS_DARK = ("@media (prefers-color-scheme:dark){:root,svg{--card:#1a222c;--card-2:#222d3a;"
                 "--band:#172029;--text:#e6edf3;--muted:#9bb0c3;--border:#33414f;--accent:#5a8bff;"
                 "--accent-soft:#16263f;--green:#3ad07f;--green-soft:#11301f;--warn:#f2913d;"
                 "--warn-soft:#2e2113;--line:#6b86a3}}")
DEFS = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="d-arrow"/></marker></defs>')

def box(x, y, w, h, lines, cls="d-card", fs=11.5, rx=7, weight="400", tcls="d-text"):
    if isinstance(lines, str):
        lines = [lines]
    out = ['<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d"/>' % (cls, x, y, w, h, rx)]
    nls = len(lines)
    cy = y + h / 2 - (nls - 1) * (fs + 3) / 2 + fs * 0.35
    for k, ln in enumerate(lines):
        out.append('<text class="%s" x="%.1f" y="%.1f" font-size="%.1f" font-weight="%s" text-anchor="middle">%s</text>'
                   % (tcls, x + w / 2, cy + k * (fs + 3), fs, weight, esc(ln)))
    return "".join(out)

def tlines(x, y, lines, cls="d-text", fs=12, weight="400", lh=15, anchor="start"):
    if isinstance(lines, str):
        lines = [lines]
    return "".join('<text class="%s" x="%.1f" y="%.1f" font-size="%.1f" font-weight="%s" text-anchor="%s">%s</text>'
                   % (cls, x, y + k * lh, fs, weight, anchor, esc(ln)) for k, ln in enumerate(lines))

def arrow(x1, y1, x2, y2, cls="d-line"):
    return '<path class="%s" d="M%.1f,%.1f L%.1f,%.1f" marker-end="url(#arr)"/>' % (cls, x1, y1, x2, y2)

def wrap_inline(vb_w, vb_h, body):
    return ('<svg viewBox="0 0 %d %d" width="100%%" preserveAspectRatio="xMidYMid meet" '
            'role="img" xmlns="http://www.w3.org/2000/svg">%s%s</svg>' % (vb_w, vb_h, DEFS, body))

def wrap_standalone(vb_w, vb_h, body):
    style = "<style>%s %s %s</style>" % (SVG_VARS_LIGHT, SVG_VARS_DARK, SVG_CLASS_CSS)
    return ('<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" font-family="sans-serif">'
            '%s%s%s</svg>' % (vb_w, vb_h, style, DEFS, body))

# --- Diagram A: Reference architecture (7 planes) ---
def d_arch():
    W, H = 960, 624
    b = [tlines(30, 32, "Reference Architecture — seven planes (Kubernetes-native, self-hosted)", "d-muted", 14, "600")]
    bands = [
        ("Developer Interface", ["IDE plugin", "CLI / terminal agent", "MCP client", "Review UI"]),
        ("Agent & Orchestration", ["Planner", "Coder", "Test", "Review", "Integrator · A2A", "Argo Workflows"]),
        ("Harness & Control", ["Routing Gateway", "Policy Server", "Sandbox Mgr", "Hooks", "Sessions / Memory"]),
        ("Model Serving · self-hosted", ["Tier-S", "Tier-M", "Tier-L", "Tier-V", "Tier-E", "vLLM·Triton·KServe"]),
        ("Data & Knowledge", ["Code Graph", "Vector Store", "Reg. Corpus", "MLflow Registry", "Context Store"]),
        ("Platform & Infrastructure", ["Kubernetes", "GPU Operator", "Istio + SPIRE", "Vault", "KEDA · Kueue"]),
    ]
    x0, w0, top, bh, gap = 30, 700, 50, 80, 10
    for i, (title, chips) in enumerate(bands):
        by = top + i * (bh + gap)
        b.append('<rect class="d-band" x="%d" y="%d" width="%d" height="%d" rx="10"/>' % (x0, by, w0, bh))
        b.append(tlines(x0 + 14, by + 21, title, "d-text", 12.5, "700"))
        cx0, cxe = x0 + 14, x0 + w0 - 14
        nch = len(chips); gc = 10
        cw = (cxe - cx0 - (nch - 1) * gc) / nch
        cyt, ch = by + 33, 34
        for j, cp in enumerate(chips):
            cxx = cx0 + j * (cw + gc)
            ccls = "d-accentbox" if (title.startswith("Model Serving") and cp.startswith("Tier")) else "d-card"
            b.append('<rect class="%s" x="%.1f" y="%d" width="%.1f" height="%d" rx="7"/>' % (ccls, cxx, cyt, cw, ch))
            b.append('<text class="d-text" x="%.1f" y="%d" font-size="10.5" text-anchor="middle">%s</text>'
                     % (cxx + cw / 2, cyt + ch / 2 + 4, esc(cp)))
    rx, rw, ry = 742, 196, top
    rh = 6 * bh + 5 * gap
    b.append('<rect class="d-accentbox" x="%d" y="%d" width="%d" height="%d" rx="10"/>' % (rx, ry, rw, rh))
    cxr, cyr = rx + rw / 2, ry + rh / 2
    b.append('<text class="d-text" x="%.1f" y="%.1f" font-size="13" font-weight="700" text-anchor="middle" '
             'transform="rotate(-90 %.1f %.1f)">Governance &amp; Audit · 21 CFR Part 11 · WORM evidence</text>'
             % (cxr, cyr, cxr, cyr))
    return W, H, "".join(b)

# --- Diagram B: 99.9% assurance pipeline ---
def d_pipe():
    W, H = 1000, 360
    b = [tlines(24, 28, "The 99.9% release gate — Generate → Verify → Repair → Gate → Sign", "d-muted", 14, "600")]
    y, h = 110, 74
    N = [(24, 120, "d-card", ["Task + Spec", "BDD / Gherkin"]),
         (170, 130, "d-accentbox", ["Model Fleet", "S / M / L / V"]),
         (326, 174, "d-greenbox", ["Deterministic", "Verifiers"]),
         (528, 150, "d-card", ["Eval Gate", "≥ 99.9%"]),
         (706, 140, "d-card", ["HITL", "by safety class"]),
         (874, 102, "d-card", ["PR +", "Audit record"])]
    cy = y + h / 2
    for (x, w, cls, lines) in N:
        b.append(box(x, y, w, h, lines, cls, 12.5))
    for i in range(len(N) - 1):
        x1 = N[i][0] + N[i][1]; x2 = N[i + 1][0]
        b.append(arrow(x1 + 3, cy, x2 - 3, cy))
    # repair loop
    n3cx = 326 + 87; n2cx = 170 + 65; by = y + h
    b.append('<path class="d-dash" d="M%.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" marker-end="url(#arr)"/>'
             % (n3cx, by, n3cx, by + 56, n2cx, by + 56, n2cx, by + 3))
    b.append(tlines((n3cx + n2cx) / 2, by + 74, "fail → repair loop (bounded budget)", "d-muted", 11, "600", anchor="middle"))
    # abstain note
    b.append(tlines(170 + 65, y - 8, "abstain → escalate", "d-muted", 10, "600", anchor="middle"))
    # verifier list
    b.append(tlines(326, 286, ["build · type-check · unit · property",
                               "mutation · differential · fuzz",
                               "SAST/DAST · schema · formal · policy"], "d-muted", 10.5, "400", 14))
    # class C note
    b.append(arrow(706 + 70, by, 706 + 70, by + 28))
    b.append(tlines(706 + 70, by + 42, "Class C → dual control", "d-muted", 10.5, "600", anchor="middle"))
    return W, H, "".join(b)

# --- Diagram C: multi-agent workflow ---
def d_multi():
    W, H = 1000, 462
    b = [tlines(24, 26, "Multi-agent workflow — gated, evidenced, human-signed", "d-muted", 14, "600")]
    agents = [("Planner", "d-accentbox"), ("Spec / Story", "d-card"), ("Coder", "d-card"),
              ("Test", "d-card"), ("Review", "d-card"), ("Integrator", "d-card")]
    x0, w, step, y, h = 24, 140, 160, 70, 60
    cxs = []
    for i, (name, cls) in enumerate(agents):
        x = x0 + i * step
        cxs.append(x + w / 2)
        b.append(box(x, y, w, h, name, cls, 12.5, weight="600"))
    cy = y + h / 2
    for i in range(len(agents) - 1):
        b.append(arrow(x0 + i * step + w + 2, cy, x0 + (i + 1) * step - 2, cy))
    # eval badges between coder->test, test->review, review->integrator
    for i in (2, 3, 4):
        mx = (x0 + i * step + w + x0 + (i + 1) * step) / 2
        b.append('<rect class="d-greenbox" x="%.1f" y="%.1f" width="40" height="20" rx="10"/>' % (mx - 20, cy - 30))
        b.append('<text class="d-text" x="%.1f" y="%.1f" font-size="10" text-anchor="middle">eval</text>' % (mx, cy - 16))
    # human checkpoints above review & integrator
    for i, lab in ((4, ["Human review"]), (5, ["Human sign", "dual · Class C"])):
        hx = cxs[i]
        b.append(box(hx - 70, 8, 140, 34, lab, "d-warnbox", 10.5, rx=7))
        b.append(arrow(hx, 42, hx, y - 2))
    # policy band
    b.append('<rect class="d-accentbox" x="24" y="200" width="940" height="44" rx="9"/>')
    b.append(tlines(494, 226, "Policy Server — structural + semantic gating on every tool call", "d-text", 12.5, "700", anchor="middle"))
    for cx in cxs:
        b.append('<path class="d-dash" d="M%.1f,%d L%.1f,%d" marker-end="url(#arr)"/>' % (cx, y + h, cx, 200))
    # tools band
    b.append('<rect class="d-band" x="24" y="290" width="940" height="44" rx="9"/>')
    b.append(tlines(494, 316, "MCP Tool Plane — sandboxed (gVisor / Kata), egress-deny", "d-text", 12.5, "700", anchor="middle"))
    b.append(arrow(494, 244, 494, 288))
    # evidence band
    b.append('<rect class="d-greenbox" x="24" y="380" width="940" height="42" rx="9"/>')
    b.append(tlines(494, 405, "Immutable evidence captured at every step → 21 CFR Part 11 record", "d-text", 12.5, "700", anchor="middle"))
    b.append(arrow(494, 334, 494, 378))
    return W, H, "".join(b)

# --- Diagram D: maturity staircase ---
def d_stair():
    W, H = 980, 470
    b = [tlines(24, 28, "ASMM-Med maturity — capability rises with assurance", "d-muted", 14, "600")]
    items = [("L0", "Ad-hoc", ["Suggestions only"], "d-warnbox"),
             ("L1", "Governed", ["Inline completion"], "d-card"),
             ("L2", "Spec-Driven", ["Single-step", "full review"], "d-card2"),
             ("L3", "Orchestrated", ["Multi-step", "HITL gates"], "d-accentbox"),
             ("L4", "Validated Autonomous", ["Autonomous within", "validated bounds"], "d-greenbox"),
             ("L5", "Self-Optimizing", ["Closed-loop", "PCCP-governed"], "d-accentbox")]
    base, sw, sgap = 444, 150, 4
    tops = []
    for i, (tag, name, auto, cls) in enumerate(items):
        x = 24 + i * (sw + sgap)
        top = base - (i + 1) * 58
        tops.append((x, top))
        b.append('<rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="8"/>' % (cls, x, top, sw, base - top))
        b.append(tlines(x + 12, top + 24, tag, "d-text", 16, "800"))
        b.append(tlines(x + 12, top + 41, name, "d-text", 11.5, "600"))
        b.append(tlines(x + 12, top + 58, auto, "d-muted", 10, "400", 13))
    for i in range(len(items) - 1):
        x1 = tops[i][0] + sw; y1 = tops[i][1]
        x2 = tops[i + 1][0]; y2 = tops[i + 1][1]
        b.append(arrow(x1, y1, x2, y2))
    # governing rule note
    b.append('<rect class="d-card" x="556" y="40" width="404" height="84" rx="10"/>')
    b.append(tlines(572, 66, ["Governing level = min(D1 Governance, D4 Evaluation,",
                              "D6 Security). Autonomy never outruns assurance.",
                              "Class C is always dual human control."], "d-text", 12, "500", 18))
    return W, H, "".join(b)

# --- Diagram E: model fleet routing ---
def d_fleet():
    W, H = 940, 372
    b = [tlines(24, 28, "Tiered model routing — smallest-capable-model first", "d-muted", 14, "600")]
    b.append(box(24, 150, 150, 64, ["Dev request", "+ context"], "d-card", 12))
    b.append(box(212, 144, 168, 76, ["Routing Gateway", "Tier-S classifier"], "d-accentbox", 12.5, weight="600"))
    b.append(arrow(174, 182, 210, 182))
    tiers = [("Tier-S", "autocomplete · classify", "≈ lowest $"),
             ("Tier-M", "test · review · docs", "low $"),
             ("Tier-L", "architecture · planning", "high $ · sparse"),
             ("Tier-V", "diagrams · imaging · PDF", "multimodal"),
             ("Tier-E", "retrieval · rerank", "tiny $")]
    tx, tw, th = 482, 230, 52
    for j, (nm, sub, cost) in enumerate(tiers):
        ty = 24 + j * 66
        cls = "d-accentbox" if nm in ("Tier-S",) else "d-card"
        b.append('<rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="8"/>' % (cls, tx, ty, tw, th))
        b.append(tlines(tx + 14, ty + 22, nm, "d-text", 12.5, "700"))
        b.append(tlines(tx + 14, ty + 39, sub, "d-muted", 10.5))
        b.append(tlines(tx + tw - 12, ty + 31, cost, "d-muted", 10.5, "600", anchor="end"))
        b.append(arrow(380, 182, tx - 2, ty + th / 2))
    return W, H, "".join(b)

# --- Diagram F: how released correctness is earned (replaces an ASCII flow) ---
def d_flow():
    W, H = 920, 196
    b = [tlines(24, 30, "How released correctness is earned", "d-muted", 14, "600")]
    N = [(24, 150, "d-accentbox", ["Generate", "model fleet"]),
         (210, 214, "d-greenbox", ["Verify · deterministic", "compiler·tests·SAST·schema·formal"]),
         (460, 116, "d-card", ["Repair", "loop"]),
         (612, 256, "d-card", ["Gate", "eval + HITL · release"])]
    y, h = 66, 66
    cy = y + h / 2
    for (x, w, cls, lines) in N:
        b.append(box(x, y, w, h, lines, cls, 11.5))
    for i in range(len(N) - 1):
        b.append(arrow(N[i][0] + N[i][1] + 3, cy, N[i + 1][0] - 3, cy))
    n3cx, n1cx, by = 460 + 58, 24 + 75, y + h
    b.append('<path class="d-dash" d="M%.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" marker-end="url(#arr)"/>'
             % (n3cx, by, n3cx, by + 38, n1cx, by + 38, n1cx, by + 3))
    b.append(tlines((n3cx + n1cx) / 2, by + 54, "fail → repair", "d-muted", 11, "600", anchor="middle"))
    return W, H, "".join(b)

DIAGRAMS = {
    "arch": (d_arch, "Figure A — Reference Architecture (seven planes)"),
    "pipe": (d_pipe, "Figure B — The 99.9% Release-Gate Assurance Pipeline"),
    "flow": (d_flow, "Figure F — How Released Correctness Is Earned"),
    "multi": (d_multi, "Figure C — Multi-Agent Workflow (gated &amp; evidenced)"),
    "stair": (d_stair, "Figure D — ASMM-Med Maturity Staircase"),
    "fleet": (d_fleet, "Figure E — Tiered Model-Fleet Routing"),
}

# render standalone .svg files + cache inline versions
SVG_INLINE = {}
for key, (fn, cap) in DIAGRAMS.items():
    w, h, body = fn()
    SVG_INLINE[key] = (wrap_inline(w, h, body), cap)
    with open(os.path.join(ASSETS, "diagram-%s.svg" % key), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + wrap_standalone(w, h, body))

def figure(key):
    svg, cap = SVG_INLINE[key]
    return ('<figure class="diagram"><div class="diagram-scroll">%s</div>'
            '<figcaption>%s &nbsp;·&nbsp; <a href="assets/diagram-%s.svg">open SVG</a></figcaption></figure>'
            % (svg, cap, key))

def try_fraction(body):
    """Render an ASCII dash-fraction (numerator / ---- / denominator) as typeset HTML."""
    lines = [l.rstrip() for l in body.split("\n")]
    di = next((i for i, l in enumerate(lines) if re.search(r"-{6,}", l)), None)
    if di is None:
        return None
    dash = lines[di]
    run = re.search(r"-{6,}", dash)
    prefix = dash[:run.start()].strip()
    suffix = dash[run.end():].strip()
    num = next((lines[j].strip() for j in range(di - 1, -1, -1) if lines[j].strip()), "")
    den = next((lines[j].strip() for j in range(di + 1, len(lines)) if lines[j].strip()), "")
    if not num or not den:
        return None
    html = '<div class="formula">'
    if prefix:
        html += '<span class="flabel">%s</span>' % esc(prefix)
    html += ('<span class="frac"><span class="num">%s</span><span class="den">%s</span></span>'
             % (esc(num), esc(den)))
    if suffix:
        html += '<span class="fsuffix">%s</span>' % esc(suffix)
    return html + "</div>"

def ascii_replace(body):
    """Swap genuine ASCII-art code blocks for real SVG figures / typeset formulas.
    Leaves legitimate monospace (pseudocode, masking examples, ∏/≤ formulas, worked
    numeric examples) untouched."""
    if re.search(r"[─-╿▶◀▲▼]", body):   # box-drawing / triangles
        return figure("pipe")                                        # README assurance flow
    if "Released correctness" in body and "Generate" in body:
        return figure("flow")
    return try_fraction(body)

# ----------------------------------------------------------------------------
# Page assembly
# ----------------------------------------------------------------------------
PAGES = [
    ("README.md", "index.html", "Overview"),
    (None, "exec-brief.html", "Executive Brief"),
    ("01-requirements.md", "01-requirements.html", "01 · Requirements"),
    ("02-maturity-model.md", "02-maturity-model.html", "02 · Maturity Model"),
    ("03-reference-architecture.md", "03-reference-architecture.html", "03 · Reference Architecture"),
    ("04-model-strategy-and-finetuning.md", "04-model-strategy-and-finetuning.html", "04 · Model Strategy & Fine-Tuning"),
    ("05-evaluation-and-validation.md", "05-evaluation-and-validation.html", "05 · Evaluation & Validation"),
    ("06-agentic-workflows.md", "06-agentic-workflows.html", "06 · Agentic Workflows"),
    ("07-security-and-compliance.md", "07-security-and-compliance.html", "07 · Security & Compliance"),
    ("08-token-and-gpu-economics.md", "08-token-and-gpu-economics.html", "08 · Token & GPU Economics"),
    ("09-adoption-roadmap.md", "09-adoption-roadmap.html", "09 · Adoption Roadmap"),
    (None, "scorecard.html", "Assessment Scorecard"),
    (None, "diagrams.html", "Diagrams (SVG)"),
]
INJECT = {
    "index.html": ["arch"],
    "02-maturity-model.html": ["stair"],
    "03-reference-architecture.html": ["arch"],
    "04-model-strategy-and-finetuning.html": ["fleet"],
    "05-evaluation-and-validation.html": ["pipe"],
    "06-agentic-workflows.html": ["multi"],
}

def nav_html(active):
    items = []
    for src, out_, label in PAGES:
        cls = ' class="active"' if out_ == active else ""
        items.append('<li%s><a href="%s">%s</a></li>' % (cls, out_, label))
    return "<ul>%s</ul>" % "".join(items)

def prevnext(active):
    idx = [p[1] for p in PAGES].index(active)
    parts = []
    if idx > 0:
        parts.append('<a class="pn prev" href="%s"><span>← Previous</span><b>%s</b></a>'
                     % (PAGES[idx - 1][1], PAGES[idx - 1][2]))
    else:
        parts.append("<span></span>")
    if idx < len(PAGES) - 1:
        parts.append('<a class="pn next" href="%s"><span>Next →</span><b>%s</b></a>'
                     % (PAGES[idx + 1][1], PAGES[idx + 1][2]))
    return '<nav class="prevnext">%s</nav>' % "".join(parts)

def toc_html(content):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)<a class="anchor"', content)
    if not heads:
        return ""
    lis = "".join('<li><a href="#%s">%s</a></li>' % (i, re.sub("<[^>]+>", "", t)) for i, t in heads)
    return '<aside class="toc"><div class="toc-t">On this page</div><ul>%s</ul></aside>' % lis

TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%% · Agentic-Native SDLC for Regulated MedTech</title>
<script>(function(){try{var t=localStorage.getItem('theme');if(!t){t=(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="topbar">
  <button class="menu-btn" aria-label="Menu" onclick="document.body.classList.toggle('nav-open')">☰</button>
  <a class="brand" href="index.html"><span class="brand-mark">◆</span> Agentic-Native SDLC <em>· Regulated MedTech</em></a>
  <button class="theme-btn" id="themeBtn" aria-label="Toggle theme" onclick="toggleTheme()"></button>
</header>
<div class="layout">
  <nav class="sidebar">
    <div class="side-t">Documents</div>
    %%NAV%%
    <div class="side-foot">Self-hosted · FDA / IEC&nbsp;62304 · ≥99.9% gate</div>
  </nav>
  <main class="content">
    <article class="prose">
      %%CONTENT%%
    </article>
    %%PREVNEXT%%
  </main>
  %%TOC%%
</div>
<div class="nav-scrim" onclick="document.body.classList.remove('nav-open')"></div>
<script src="assets/app.js"></script>
</body>
</html>
"""

def render_page(active, title, content_html, toc=""):
    page = TEMPLATE
    page = page.replace("%%TITLE%%", _html.escape(title))
    page = page.replace("%%NAV%%", nav_html(active))
    page = page.replace("%%CONTENT%%", content_html)
    page = page.replace("%%PREVNEXT%%", prevnext(active))
    page = page.replace("%%TOC%%", toc)
    return page

# ----------------------------------------------------------------------------
# Special page: Executive Brief (board-level, no diagrams)
# ----------------------------------------------------------------------------
def build_exec():
    return """
<h1>Executive Brief<a class="anchor" href="#top">#</a></h1>
<p class="eyebrow">Board-level summary · one page</p>
<p class="lead">We will adopt an <strong>agent-native software development lifecycle</strong> for our regulated
medical-device software &mdash; capturing the productivity of AI while meeting our FDA / IEC&nbsp;62304 obligations,
keeping all models and data inside our own infrastructure, and controlling cost. This is an engineering and
quality discipline, <strong>not &ldquo;vibe coding.&rdquo;</strong></p>

<div class="callout"><span class="k">The bet</span><span>Generation is becoming free; <strong>correctness, validation, traceability, and cost control are the
engineering</strong>. Our advantage comes from the system around the model, not the model alone.</span></div>

<h2>Why now</h2>
<p>AI now writes a large share of new code industry-wide, compressing implementation from weeks to hours. Our
competitors are moving. The risk is not adopting too slowly &mdash; it is adopting <em>without assurance</em>,
which in a regulated context means recalls, findings, and IP leakage. A disciplined framework lets us move fast
<em>and</em> stay defensible.</p>

<h2>What we are building</h2>
<div class="grid2">
  <div class="gcard"><h4>A self-hosted model fleet</h4><p>Open-weight, fine-tuned models served on our existing
  Kubernetes/GPU platform. <strong>No Claude / OpenAI / Gemini APIs</strong> &mdash; for cost at scale, data
  sovereignty, and regulatory control.</p></div>
  <div class="gcard"><h4>A six-level maturity model</h4><p>ASMM-Med moves us from ungoverned &ldquo;shadow AI&rdquo;
  to <strong>validated autonomous agents</strong>, in assurance-gated steps each signed off by Engineering,
  Quality/Regulatory, and Security.</p></div>
  <div class="gcard"><h4>Deterministic assurance</h4><p>Every AI output passes <strong>deterministic
  verifiers</strong> (compilers, tests, static analysis, formal checks) plus human review before it can ship.
  The model proposes; the system disposes.</p></div>
  <div class="gcard"><h4>Cost as a first-class metric</h4><p>We optimize <strong>cost-per-verified-change</strong>,
  not cost-per-token &mdash; via tiered model routing, caching, quantization, and in-loop budget limits.</p></div>
</div>

<h2>The three questions the board will ask</h2>
<div class="tablewrap"><table>
<thead><tr><th>Question</th><th>Our answer</th></tr></thead>
<tbody>
<tr><td><strong>How do we hit 99.9% accuracy if the AI is probabilistic?</strong></td>
<td>99.9% is a property of the <em>system</em>, not the model. We wrap every generation in deterministic checks
and human checkpoints (<em>Generate &rarr; Verify &rarr; Repair &rarr; Gate &rarr; Sign</em>). The model is the
least-trusted component; trust is manufactured around it. The highest-risk software (IEC&nbsp;62304 Class C)
always requires dual human sign-off.</td></tr>
<tr><td><strong>Can we afford the GPU cost?</strong></td>
<td>Self-hosting converts per-token vendor billing into an owned, amortizable GPU fleet. A small &ldquo;reflex&rdquo;
model handles the majority of calls cheaply; large reasoning models are used sparingly. At our scale this is
materially cheaper than API pricing &mdash; and sovereignty/IP control make it non-optional regardless.</td></tr>
<tr><td><strong>Will regulators accept it?</strong></td>
<td>Yes, when the agent is treated as <em>validated production software</em> under FDA Computer Software Assurance,
with documented intended use, risk-based evidence, full traceability, and immutable 21&nbsp;CFR Part&nbsp;11 records.
The framework is built to produce that evidence automatically.</td></tr>
</tbody></table></div>

<h2>What it unlocks</h2>
<ul>
<li><strong>Throughput</strong> &mdash; faster implementation, test generation, documentation, and safe modernization
of legacy code that was previously &ldquo;too risky to touch.&rdquo;</li>
<li><strong>Quality</strong> &mdash; more comprehensive automated test and evaluation coverage than humans can produce
in the same time, lowering escape-rate into regulated products.</li>
<li><strong>Leverage</strong> &mdash; smaller teams tackle larger problems; engineers shift from writing code to
designing, validating, and directing the systems that produce it.</li>
</ul>

<h2>Investment &amp; timeline (illustrative)</h2>
<div class="tablewrap"><table>
<thead><tr><th>Horizon</th><th>Maturity target</th><th>Focus</th></tr></thead>
<tbody>
<tr><td>Quarters&nbsp;1&ndash;2</td><td><span class="pill">L1</span> Governed Assistance</td><td>Kill shadow AI; stand up self-hosted serving + full logging</td></tr>
<tr><td>Quarters&nbsp;3&ndash;4</td><td><span class="pill">L2</span> Spec-Driven</td><td>Specs in-repo; deterministic evaluation harness in CI</td></tr>
<tr><td>Quarters&nbsp;5&ndash;7</td><td><span class="pill">L3</span> Orchestrated</td><td>Sandboxed agents, model fleet + routing, policy server</td></tr>
<tr><td>Quarters&nbsp;8&ndash;11</td><td><span class="pill">L4</span> Validated Autonomous</td><td>CSA-validate agents; 99.9% gates; full traceability</td></tr>
<tr><td>Quarter&nbsp;12+</td><td><span class="pill">L5</span> Self-Optimizing</td><td>Closed-loop fine-tuning; cost-optimized at scale</td></tr>
</tbody></table></div>
<p>Primary investment: GPU capacity, a platform/MLOps team, evaluation engineering, and quality/regulatory
integration. Resourcing and figures are placeholders for the funded business case.</p>

<h2>What we ask of the board</h2>
<ol>
<li>Endorse the <strong>self-hosted, assurance-gated strategy</strong> (no external LLM APIs).</li>
<li>Fund <strong>Phase&nbsp;1 (L1)</strong> &mdash; serving platform, logging, and the end of shadow AI.</li>
<li>Affirm the governance principle that <strong>autonomy never outruns assurance</strong>: no maturity level is
granted without joint Engineering + Quality/Regulatory + Security sign-off.</li>
</ol>

<div class="callout"><span class="k">Bottom line</span><span><strong>Structure scales; vibes don&rsquo;t.</strong> AI
amplifies our engineering and quality culture &mdash; both its strengths and its weaknesses. This framework
ensures it amplifies the right ones. <em>Full detail:</em> see the <a href="02-maturity-model.html">Maturity Model</a>
and the <a href="index.html">document set</a>.</span></div>
"""

# ----------------------------------------------------------------------------
# Special page: Assessment Scorecard (fillable template)
# ----------------------------------------------------------------------------
SC_DIMS = [
    ("D1", "Governance, Quality &amp; Regulatory", True,
     "QMS integration, IEC 62304 / ISO 13485 / QMSR alignment, CSA validation, traceability, change control",
     ["None / shadow AI", "AUP + logging", "QMS + SDD controlled", "GAMP risk-class + 42001",
      "CSA-validated + traceable", "PCCP + auto-evidence"]),
    ("D2", "Model Infrastructure &amp; MLOps", False,
     "Self-hosted serving, fine-tuning pipeline, registry, reproducibility, multi-LoRA, GPU platform",
     ["None / SaaS", "Single self-hosted", "Registry + first fine-tunes", "Tiered fleet + multi-LoRA",
      "Reproducible validated pipelines", "Continuous FT + auto-promote"]),
    ("D3", "Context &amp; Knowledge Engineering", False,
     "Specs, rule files, RAG over code/docs/regulatory corpus, memory, context hygiene",
     ["Editor buffer only", "System prompts", "specs + AGENTS.md + RAG", "Governed RAG + skills + hygiene",
      "Validated sources + provenance", "Self-curating + measured"]),
    ("D4", "Evaluation, Validation &amp; Assurance", True,
     "Deterministic verifiers, eval suites, trajectory eval, the 99.9% gate, abstention",
     ["None / “looks right”", "Lint + CI", "Deterministic harness in CI", "Output + trajectory evals",
      "≥ 99.9% gate + statistical", "Continuous + closed-loop"]),
    ("D5", "Agentic Orchestration &amp; Tooling", False,
     "Single &rarr; multi-agent, MCP/A2A, sandboxing, HITL design, workflow engine",
     ["None", "Inline only", "Single-step bounded", "Multi-step sandboxed + MCP",
      "Multi-agent A2A + hooks", "Self-orchestrating"]),
    ("D6", "Security &amp; Zero-Trust", True,
     "Identity, egress control, prompt-injection defense, supply chain, secrets, audit immutability",
     ["Uncontrolled", "SSO + RBAC + DLP", "Repo-scoped + Vault", "Zero-trust + OPA + sandbox",
      "Supply-chain + WORM + 62443", "Continuous red-team"]),
    ("D7", "Observability &amp; FinOps", False,
     "Tracing, eval dashboards, token/GPU metering, routing economics, budget guardrails",
     ["None", "Basic logs + GPU util", "Usage + cost dashboards", "Tracing + cost/task",
      "Cost-per-green-PR SLO", "Closed-loop cost opt"]),
    ("D8", "People, Skills &amp; Operating Model", False,
     "Roles (conductor/orchestrator), review culture, training, approval-fatigue controls",
     ["Individual experiments", "Training + champions", "Spec/review skills", "Orchestrator role emerges",
      "Formal roles + failure-mode review", "Judgment-first hiring"]),
]

def build_scorecard():
    h = ['<h1>ASMM-Med Assessment Scorecard<a class="anchor" href="#top">#</a></h1>',
         '<p>A fillable, self-contained template for a quarterly maturity assessment. Select the satisfied level '
         '(0&ndash;5) for each of the eight dimensions and record the supporting evidence. Your '
         '<strong>governing level = min(D1, D4, D6)</strong> is computed live &mdash; capability can never outrun '
         'governance, evaluation, and security. Entries save to this browser; use <em>Print</em> to produce a PDF '
         'for the quality record. See <a href="02-maturity-model.html">the maturity model</a> for full cell descriptors.</p>']
    # toolbar
    h.append('<div class="sc-toolbar">'
             '<button id="scSave">Save</button>'
             '<button class="ghost" id="scPrint">Print / PDF</button>'
             '<button class="ghost" id="scReset">Reset</button>'
             '<span class="saved-tag" id="savedTag"></span>'
             '<div class="sc-readout">'
             '<div class="ro gov">Governing level<b id="ro-gov">&mdash;</b></div>'
             '<div class="ro">Capability avg<b id="ro-cap">&mdash;</b></div>'
             '</div></div>')
    h.append('<form id="scorecard">')
    # meta
    h.append('<div class="sc-meta">'
             '<label>Organization / Business unit<input name="org" type="text" placeholder="e.g. Imaging Software, Site X"></label>'
             '<label>Assessor(s)<input name="assessor" type="text" placeholder="name, role"></label>'
             '<label>Assessment date<input name="date" type="date"></label>'
             '</div>')
    # dimensions
    for tag, name, gov, desc, levels in SC_DIMS:
        h.append('<div class="dim">')
        h.append('<div class="dim-h"><span class="tag">%s</span><span class="nm">%s</span>%s</div>'
                 % (tag, name, '<span class="gv">governing</span>' if gov else ''))
        h.append('<div class="dim-desc">%s</div>' % desc)
        h.append('<div class="levels">')
        nm = "d%s" % tag[1:]
        for lv, cap in enumerate(levels):
            h.append('<label><input type="radio" name="%s" value="%d">L%d<small>%s</small></label>'
                     % (nm, lv, lv, cap))
        h.append('</div>')
        h.append('<textarea name="ev%s" placeholder="Evidence / artifacts / gaps for %s (logs, validation records, eval reports, policy configs)…"></textarea>'
                 % (tag[1:], tag))
        h.append('</div>')
    # governing rule note + sign-off
    h.append('<blockquote><strong>Promotion rule.</strong> The overall operating level is the minimum across '
             'D1, D4, and D6. Advancing requires this scorecard plus documented evidence, signed by Engineering, '
             'Quality/Regulatory, and Security. Even at L4/L5, IEC&nbsp;62304 Class&nbsp;C changes always require '
             'dual human control.</blockquote>')
    h.append('<h2>Sign-off</h2>')
    h.append('<div class="sign">'
             '<label>Engineering<input name="sign_eng" type="text" placeholder="name / date"></label>'
             '<label>Quality &amp; Regulatory<input name="sign_qa" type="text" placeholder="name / date"></label>'
             '<label>Security<input name="sign_sec" type="text" placeholder="name / date"></label>'
             '</div>')
    h.append('</form>')
    return "\n".join(h)

SPECIAL = {"exec-brief.html": ("Executive Brief", build_exec),
           "scorecard.html": ("Assessment Scorecard", build_scorecard)}

# build all pages
for src, out_, label in PAGES:
    if out_ == "diagrams.html":
        gal = ['<h1>Architecture &amp; Workflow Diagrams<a class="anchor" href="#top">#</a></h1>',
               '<p>Hand-authored, self-contained SVG views of the platform. They are theme-aware and render '
               'without any external dependency, and each links to a standalone <code>.svg</code> file. The 27 '
               'in-line <em>Mermaid</em> diagrams inside the documents are additionally rendered to SVG in the browser.</p>']
        for key in ["arch", "pipe", "flow", "multi", "stair", "fleet"]:
            gal.append(figure(key))
        content = "\n".join(gal)
        with open(os.path.join(OUT, out_), "w", encoding="utf-8") as f:
            f.write(render_page(out_, label, content))
        continue
    if src is None:
        title, fn = SPECIAL[out_]
        content = fn()
        with open(os.path.join(OUT, out_), "w", encoding="utf-8") as f:
            f.write(render_page(out_, title, content, toc_html(content)))
        continue
    with open(os.path.join(SRC, src), encoding="utf-8") as f:
        md = f.read()
    content = md_to_html(md)
    for key in INJECT.get(out_, []):
        fig = figure(key)
        m = re.search(r"</h1>", content)
        content = (content[:m.end()] + "\n" + fig + "\n" + content[m.end():]) if m else (fig + content)
    with open(os.path.join(OUT, out_), "w", encoding="utf-8") as f:
        f.write(render_page(out_, label, content, toc_html(content)))

print("Built %d pages + %d standalone SVGs into %s" % (len(PAGES), len(DIAGRAMS), OUT))
print("Pages:", ", ".join(p[1] for p in PAGES))
