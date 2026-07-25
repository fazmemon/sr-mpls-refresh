#!/usr/bin/env python3
"""HRT estate topology + BGP overlay.
All node/link/session data taken verbatim from the live box 2026-07-25:
  netlab report addressing, show isis segment-routing prefix-segments,
  show ip bgp summary on every speaker.
"""
import os

VBW, VBH = 1780, 1275
OUT = os.path.expanduser(
    "/private/tmp/claude-501/-Users-fazmemon-Documents-dev/"
    "89d936fb-5ee0-472c-b9cb-04d4d589aaaa/scratchpad/srmpls/dclab-estate.html")

# name: (cx, cy, role, loopback, mgmt, sid, subtitle)
N = {
    "spine1": (300, 175, "spine", "10.0.0.1", "101", "", "OSPF · EVPN-RR"),
    "spine2": (520, 175, "spine", "10.0.0.2", "102", "", "OSPF · EVPN-RR"),
    "leaf1":  (190, 315, "leaf",  "10.0.0.3", "103", "", "VTEP"),
    "leaf2":  (350, 315, "leaf",  "10.0.0.4", "104", "", "VTEP"),
    "leaf3":  (510, 315, "leaf",  "10.0.0.5", "105", "", "VTEP"),
    "h1":     (190, 432, "host",  "172.16.0.16", "116", "", ""),
    "h2":     (350, 432, "host",  "172.16.0.17", "117", "", ""),
    "h3":     (510, 432, "host",  "172.16.0.18", "118", "", ""),
    "bl1":    (700, 175, "border","10.0.0.6", "106", "900006", "OSPF + IS-IS-SR"),
    "mdrx":   (700,  52, "feed",  "172.16.2.20", "120", "", "SSM receiver"),
    "core1":  (960, 508, "core",  "10.0.0.7", "107", "900007", "IS-IS-SR"),
    "core2":  (1220,508, "core",  "10.0.0.8", "108", "900008", "IS-IS-SR"),
    "core3":  (960, 722, "core",  "10.0.0.9", "109", "900009", "IS-IS-SR"),
    "core4":  (1220,722, "core",  "10.0.0.10","110", "900010", "IS-IS-SR"),
    "asbr1":  (1440,612, "asbr",  "10.0.0.11","111", "900011", "ASBR · BGP-LU"),
    "asbr2":  (1440,852, "asbr",  "10.0.0.12","112", "900012", "ASBR · BGP-LU"),
    "edge2":  (1440,992, "edge",  "10.0.0.13","113", "900013", "SR egress · EPE"),
    "peer1":  (1215,1148,"ext",   "10.0.0.14","114", "", "AS 65100 · exchange"),
    "transit1":(1600,1148,"ext",  "10.0.0.15","115", "", "AS 65200 · transit"),
    "mktdata":(1692,868, "feed",  "172.16.1.19","119","", "SSM source"),
}

# (a, b, label, kind)
LINKS = [
    ("leaf1","spine1","","dc"), ("leaf1","spine2","","dc"),
    ("leaf2","spine1","","dc"), ("leaf2","spine2","","dc"),
    ("leaf3","spine1","","dc"), ("leaf3","spine2","","dc"),
    ("bl1","spine1","","bd"),   ("bl1","spine2","","bd"),
    ("h1","leaf1","","host"), ("h2","leaf2","","host"), ("h3","leaf3","","host"),
    ("mdrx","bl1","172.16.2.0/24 · dedicated L3","md"),
    ("bl1","core1","10.1.0.32/30","xw"), ("bl1","core3","10.1.0.36/30","xw"),
    ("core1","core2","metric 10","wan"),
    ("core3","core1","metric 10","wan"),
    ("core2","core4","metric 10","wan"),
    ("core4","core3","metric 100","wanhi"),
    ("asbr1","core2","10.1.0.56/30","xw"), ("asbr1","core4","10.1.0.60/30","xw"),
    ("asbr1","asbr2","10.1.0.64/30 · inter-AS","ias"),
    ("asbr2","edge2","10.1.0.68/30","wan"),
    ("edge2","peer1","10.1.0.72/30","ext"),
    ("edge2","transit1","10.1.0.76/30","ext"),
    ("mktdata","edge2","172.16.1.0/24 · dedicated L3","md"),
]

# (a, b, kind, label)  kind: ibgp | ibgp_rr | ebgp | lu | gap | kill
BGP = [
    ("leaf1","spine1","ibgp_rr",""), ("leaf1","spine2","ibgp_rr",""),
    ("leaf2","spine1","ibgp_rr",""), ("leaf2","spine2","ibgp_rr",""),
    ("leaf3","spine1","ibgp_rr",""), ("leaf3","spine2","ibgp_rr",""),
    ("spine1","spine2","ibgp",""),
    ("bl1","spine1","ibgp_rr",""), ("bl1","spine2","ibgp_rr",""),
    ("bl1","asbr1","wan","iBGP · RR + next-hop-self"),
    ("asbr1","asbr2","lu","eBGP + BGP-LU"),
    ("asbr2","edge2","ibgp",""),
    ("edge2","peer1","ebgp","EPE"), ("edge2","transit1","ebgp","EPE"),
]

ROLE = {
    "spine": dict(w=142,h=60,f="var(--dc-fill)",  s="var(--dc)"),
    "leaf":  dict(w=142,h=60,f="var(--dc-fill)",  s="var(--dc)"),
    "border":dict(w=168,h=64,f="var(--bd-fill)",  s="var(--bd)"),
    "core":  dict(w=142,h=60,f="var(--wan-fill)", s="var(--wan)"),
    "asbr":  dict(w=160,h=62,f="var(--as-fill)",  s="var(--as)"),
    "edge":  dict(w=160,h=62,f="var(--as-fill)",  s="var(--as)"),
    "ext":   dict(w=168,h=58,f="var(--peer-fill)",s="var(--peer)"),
    "host":  dict(w=112,h=44,f="var(--host-fill)",s="var(--host)"),
    "feed":  dict(w=136,h=48,f="var(--md-fill)",  s="var(--md)"),
}
LC = {"dc":"var(--dc)","bd":"var(--bd)","xw":"var(--bd)","wan":"var(--wan)",
      "wanhi":"var(--wanhi)","ias":"var(--as)","ext":"var(--peer)",
      "host":"var(--host)","md":"var(--md)"}
BC = {"ibgp":"var(--bgp)","ibgp_rr":"var(--bgp)","ebgp":"var(--bgpe)",
      "lu":"var(--bgplu)","gap":"var(--gap)","kill":"var(--kill)","wan":"var(--gap)"}


def edge(cx, cy, w, h, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2) / abs(dx) if dx else 1e9
    sy = (h / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def ends(a, b):
    ax, ay = N[a][0], N[a][1]
    bx, by = N[b][0], N[b][1]
    ra, rb = ROLE[N[a][2]], ROLE[N[b][2]]
    x1, y1 = edge(ax, ay, ra["w"], ra["h"], bx, by)
    x2, y2 = edge(bx, by, rb["w"], rb["h"], ax, ay)
    return x1, y1, x2, y2


phys, plab = [], []
for a, b, lab, kind in LINKS:
    x1, y1, x2, y2 = ends(a, b)
    col = LC[kind]
    dash = ' stroke-dasharray="8 5"' if kind in ("ext", "md") else ""
    wdt = 3.0 if kind in ("ias", "wanhi") else 2.2
    phys.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                f'stroke="{col}" stroke-width="{wdt}"{dash}/>')
    if lab:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        pw = len(lab) * 6.2 + 12
        plab.append(
            f'<g><rect x="{mx-pw/2:.0f}" y="{my-9:.0f}" width="{pw:.0f}" height="18" '
            f'rx="9" fill="var(--pill)" stroke="{col}" stroke-width="0.9"/>'
            f'<text x="{mx:.0f}" y="{my+4:.0f}" class="pl" text-anchor="middle">{lab}</text></g>')

# BGP sessions drawn as arcs so they read as an overlay, not cabling
bgp, blab = [], []
for a, b, kind, lab in BGP:
    x1, y1, x2, y2 = ends(a, b)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = max((dx * dx + dy * dy) ** 0.5, 1)
    bow = min(L * 0.17, 95)
    cx, cy = mx - dy / L * bow, my + dx / L * bow
    col = BC[kind]
    dash = ' stroke-dasharray="9 6"' if kind in ("gap", "kill") else ""
    wdt = {"lu": 3.4, "gap": 3.0, "kill": 2.2, "ebgp": 2.6, "wan": 3.0}.get(kind, 1.7)
    op = 0.55 if kind == "kill" else 1
    bgp.append(f'<path d="M{x1:.0f},{y1:.0f} Q{cx:.0f},{cy:.0f} {x2:.0f},{y2:.0f}" '
               f'fill="none" stroke="{col}" stroke-width="{wdt}"{dash} opacity="{op}"/>')
    if lab:
        lx, ly = (mx + cx) / 2, (my + cy) / 2
        pw = len(lab) * 6.4 + 14
        blab.append(
            f'<g><rect x="{lx-pw/2:.0f}" y="{ly-10:.0f}" width="{pw:.0f}" height="20" '
            f'rx="10" fill="var(--pill)" stroke="{col}" stroke-width="1.1"/>'
            f'<text x="{lx:.0f}" y="{ly+4:.0f}" class="bl" text-anchor="middle" '
            f'fill="{col}">{lab}</text></g>')

nodes = []
for name, (cx, cy, role, lo, mg, sid, sub) in N.items():
    r = ROLE[role]
    w, h = r["w"], r["h"]
    nodes.append(f'<g><rect x="{cx-w/2:.0f}" y="{cy-h/2:.0f}" width="{w}" height="{h}" '
                 f'rx="9" fill="{r["f"]}" stroke="{r["s"]}" stroke-width="2"/>')
    if role in ("host", "feed"):
        nodes.append(f'<text x="{cx}" y="{cy-4}" text-anchor="middle" class="nn">{name}</text>')
        nodes.append(f'<text x="{cx}" y="{cy+11}" text-anchor="middle" class="ns">{lo}</text>')
        if sub:
            nodes.append(f'<text x="{cx}" y="{cy+h/2+14:.0f}" text-anchor="middle" class="ns">{sub}</text>')
    else:
        nodes.append(f'<text x="{cx}" y="{cy-10}" text-anchor="middle" class="nn">{name}</text>')
        nodes.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" class="nl">lo {lo}</text>')
        tail = f'{sub} · SID {sid}' if sid else sub
        nodes.append(f'<text x="{cx}" y="{cy+20}" text-anchor="middle" class="ns">{tail}</text>')
    nodes.append('</g>')

zones = [
    f'<rect x="90" y="112" width="700" height="390" rx="14" class="z-dc"/>',
    f'<text x="112" y="140" class="zl" fill="var(--dc)">RESEARCH DC — AS 65000 · OSPF underlay · EVPN/VXLAN · spines = RRs</text>',
    f'<rect x="875" y="408" width="430" height="378" rx="14" class="z-wan"/>',
    f'<text x="895" y="762" class="zl" fill="var(--wan)">BGP-FREE SR CORE — IS-IS-SR only</text>',
    f'<text x="895" y="779" class="zl2" fill="var(--wan)">no BGP process on any core node</text>',
    f'<rect x="1330" y="762" width="230" height="300" rx="14" class="z-as"/>',
    f'<text x="1350" y="790" class="zl" fill="var(--as)">AS 65001</text>',
    f'<text x="1350" y="810" class="zl2" fill="var(--as)">colo / exchange edge</text>',
]

SVG = "\n".join(zones + phys + plab + nodes)
SVGB = "\n".join(bgp + blab)

HTML = f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=yes">
<title>HRT estate — topology + BGP</title>
<style>
:root{{
  --bg:#f6f7f9; --card:#fff; --ink:#0f172a; --muted:#64748b;
  --dc:#2563eb; --dc-fill:#eff6ff; --wan:#7c3aed; --wan-fill:#f5f3ff;
  --wanhi:#c026d3; --peer:#059669; --peer-fill:#ecfdf5;
  --bd:#dc2626; --bd-fill:#fef2f2; --as:#ea580c; --as-fill:#fff7ed;
  --host:#475569; --host-fill:#f1f5f9; --md:#0891b2; --md-fill:#ecfeff;
  --bgp:#0284c7; --bgpe:#059669; --bgplu:#7c3aed; --gap:#d97706; --kill:#dc2626;
  --pill:#ffffff; --z-dc:#dbeafe44; --z-wan:#ede9fe44; --z-as:#ffedd544;
}}
@media (prefers-color-scheme: dark){{
  :root{{ --bg:#0b1120; --card:#111827; --ink:#e5e7eb; --muted:#94a3b8;
    --dc:#60a5fa; --dc-fill:#0b1e3b; --wan:#a78bfa; --wan-fill:#1e1633;
    --wanhi:#e879f9; --peer:#34d399; --peer-fill:#062b20;
    --bd:#f87171; --bd-fill:#3b0d0d; --as:#fb923c; --as-fill:#3b1d06;
    --host:#94a3b8; --host-fill:#1e293b; --md:#22d3ee; --md-fill:#083344;
    --bgp:#38bdf8; --bgpe:#34d399; --bgplu:#a78bfa; --gap:#fbbf24; --kill:#f87171;
    --pill:#0f172a; --z-dc:#1e3a8a2e; --z-wan:#4c1d952e; --z-as:#7c2d122e; }}
}}
:root[data-theme=dark]{{ --bg:#0b1120; --card:#111827; --ink:#e5e7eb; --muted:#94a3b8;
  --dc:#60a5fa; --dc-fill:#0b1e3b; --wan:#a78bfa; --wan-fill:#1e1633; --wanhi:#e879f9;
  --peer:#34d399; --peer-fill:#062b20; --bd:#f87171; --bd-fill:#3b0d0d;
  --as:#fb923c; --as-fill:#3b1d06; --host:#94a3b8; --host-fill:#1e293b;
  --md:#22d3ee; --md-fill:#083344; --bgp:#38bdf8; --bgpe:#34d399; --bgplu:#a78bfa;
  --gap:#fbbf24; --kill:#f87171; --pill:#0f172a;
  --z-dc:#1e3a8a2e; --z-wan:#4c1d952e; --z-as:#7c2d122e; }}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1500px;margin:0 auto;padding:14px}}
h1{{font-size:19px;margin:4px 0 2px}}
.sub{{color:var(--muted);font-size:13px;margin:0 0 10px}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 10px}}
button{{font:600 13px/1 inherit;padding:9px 14px;border-radius:999px;cursor:pointer;
  border:1.5px solid #94a3b855;background:var(--card);color:var(--ink)}}
button[aria-pressed=true]{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
.card{{background:var(--card);border:1px solid #94a3b833;border-radius:16px;
  padding:10px;overflow:auto}}
svg{{width:100%;height:auto;min-width:900px;display:block}}
.z-dc{{fill:var(--z-dc);stroke:var(--dc);stroke-width:1;stroke-dasharray:3 4}}
.z-wan{{fill:var(--z-wan);stroke:var(--wan);stroke-width:1;stroke-dasharray:3 4}}
.z-as{{fill:var(--z-as);stroke:var(--as);stroke-width:1;stroke-dasharray:3 4}}
.zl{{font:700 14px sans-serif}} .zl2{{font:600 11.5px sans-serif;opacity:.85}}
.nn{{font:700 15px sans-serif;fill:var(--ink)}}
.nl{{font:600 11.5px ui-monospace,monospace;fill:var(--ink)}}
.ns{{font:10.5px sans-serif;fill:var(--muted)}}
.pl{{font:10px ui-monospace,monospace;fill:var(--ink)}}
.bl{{font:700 11px sans-serif}}
#bgpl{{display:none}} body.showbgp #bgpl{{display:block}}
body.bgponly #physl{{opacity:.16}}
.legend{{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;font-size:12.5px}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}
.sw{{width:20px;height:4px;border-radius:2px;display:inline-block}}
.note{{color:var(--muted);font-size:12.5px;margin-top:10px;line-height:1.55}}
code{{background:#94a3b822;padding:1px 5px;border-radius:4px;font-size:11.5px}}
b.ink{{color:var(--ink)}}
</style>
<div class="wrap">
<h1>HRT estate — topology and BGP</h1>
<p class="sub">Built from the live box, 25 Jul 2026 · S0 complete: WAN iBGP up, label forwarding verified · 20 nodes · EC2 netlab/containerlab · <code>netlab connect &lt;node&gt;</code> · admin/admin</p>
<div class="bar">
  <button id="b1" aria-pressed="true">Physical + IGP</button>
  <button id="b2" aria-pressed="false">BGP sessions</button>
  <button id="b3" aria-pressed="false">Both</button>
</div>
<div class="card">
<svg viewBox="0 0 {VBW} {VBH}" xmlns="http://www.w3.org/2000/svg">
<g id="physl">
{SVG}
</g>
<g id="bgpl">
{SVGB}
</g>
</svg>
</div>
<div class="legend">
  <span><i class="sw" style="background:var(--dc)"></i>DC fabric</span>
  <span><i class="sw" style="background:var(--bd)"></i>border / DC↔WAN</span>
  <span><i class="sw" style="background:var(--wan)"></i>SR core (IS-IS-SR)</span>
  <span><i class="sw" style="background:var(--wanhi)"></i>metric 100 link</span>
  <span><i class="sw" style="background:var(--as)"></i>AS 65001 / inter-AS</span>
  <span><i class="sw" style="background:var(--peer)"></i>external eBGP</span>
  <span><i class="sw" style="background:var(--md)"></i>market data, dedicated L3</span>
  <span><i class="sw" style="background:var(--gap)"></i>WAN-domain iBGP (over the BGP-free core)</span>
</div>
<p class="note">
<b class="ink">Read the core as an absence.</b> <code>show running-config section bgp</code> returns nothing on
core1–core4. In the BGP view they are the only nodes with no arc touching them — every session terminates
on an edge, and the core exists purely to switch labels between BGP next-hops it resolves through IS-IS-SR.
<br><br>
<b class="ink">Two IGP domains, no redistribution.</b> The DC is OSPF; the WAN/DCI core and AS 65001 each run
their own IS-IS-SR. <code>bl1</code> is the only node in two of them and it runs them side by side. Nothing
leaks between them — reachability crosses on BGP with next-hop rewrite, and SR provides transport to
whatever next-hop lands.
<br><br>
<b class="ink">Service prefixes are kept out of the core IGP on purpose — this is the load-bearing bit.</b>
While <code>172.16.2.0/24</code> was in IS-IS, the core had a native route to it and forwarded plain IP
hop by hop; the SR label plane was fully programmed and completely unused. Removing that one interface
from IS-IS was the entire fix — EOS immediately resolved the BGP route over the SR tunnel with no extra
configuration:
<br><br>
<code>B I 172.16.2.0/24 [200/0] via 10.0.0.6/32, IS-IS SR tunnel index 2 → label 900006</code>
<br><br>
and the traceroute turned into <code>core1 &lt;MPLS:L=900006&gt; → bl1 → mdrx</code>. A BGP-free core is not
a core that happens to run no BGP — it is a core with <i>no route to the service at all</i>, which is what
leaves label switching as the only way through. Watch for the trap that produced this: netlab had put
<code>bl1</code>'s receiver-facing interface into <b>both</b> OSPF and IS-IS, so the prefix was being
injected into both domains without a <code>redistribute</code> statement anywhere.
<br><br>
<b class="ink">Ring metrics are deliberate, and now applied.</b> core4↔core3 is 100 and the rest are 10, so for
<code>bl1 → asbr1</code> the path is core1→core2 and the alternate neighbour core3 has no loop-free path —
its own route back to core2 runs through core1. No LFA exists, so TI-LFA has to build a repair to the
post-convergence path and push a two-label stack rather than a single swap. Verified: with all four links
at the default 10 the traceroute ECMP'd round both sides of the ring; at 100 it collapses to the single
path <code>asbr1 → core2 → core1 → bl1</code>. Equal metrics would prove nothing.
<br><br>
<b class="ink">Market data never touches the overlay.</b> <code>mktdata</code> at the colo edge and
<code>mdrx</code> in the DC both sit on dedicated routed segments — PIM-SSM inter-AS across the SR core, no
VXLAN, no head-end replication, and the A/B disjointness stays available. Not yet configured: PIM is at
zero lines on all eight EOS nodes.
</p>
</div>
<script>
var b=document.body,B=[b1,b2,b3];
function set(i){{
  b.classList.toggle('showbgp', i>0);
  b.classList.toggle('bgponly', i===1);
  B.forEach(function(x,j){{x.setAttribute('aria-pressed', j===i);}});
}}
B.forEach(function(x,i){{x.onclick=function(){{set(i);}};}});
</script>
"""

open(OUT, "w").write(HTML)
print("wrote", OUT, len(HTML), "bytes")
