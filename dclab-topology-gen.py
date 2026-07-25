#!/usr/bin/env python3
"""Generate a Visio-style HTML/SVG topology for the dclab HRT lab.
Data taken verbatim from `netlab report addressing` on the live box."""

VBW, VBH = 1260, 1090

# name: (cx, cy, role, loopback, mgmt, subtitle)
NODES = {
    "spine1": (400, 120, "spine", "10.0.0.1", ".101", "OSPF · EVPN-RR"),
    "spine2": (860, 120, "spine", "10.0.0.2", ".102", "OSPF · EVPN-RR"),
    "leaf1":  (185, 340, "leaf",  "10.0.0.3", ".103", "VTEP"),
    "leaf2":  (455, 340, "leaf",  "10.0.0.4", ".104", "VTEP"),
    "leaf3":  (725, 340, "leaf",  "10.0.0.5", ".105", "VTEP"),
    "bl1":    (1055,340, "border","10.0.0.6", ".106", "OSPF + IS-IS-SR"),
    "h1":     (185, 505, "host",  "172.16.0.10", ".110", ""),
    "h2":     (455, 505, "host",  "172.16.0.11", ".111", ""),
    "h3":     (725, 505, "host",  "172.16.0.12", ".112", ""),
    "core1":  (475, 770, "core",  "10.0.0.7", ".107", "IS-IS-SR"),
    "core2":  (855, 770, "core",  "10.0.0.8", ".108", "IS-IS-SR"),
    "isp":    (665, 975, "isp",   "10.0.0.9", ".109", "AS 65100 · FRR"),
}

BOUNDARY_Y = 635

# (a, a_if, a_ip, b, b_if, b_ip, subnet, kind)
LINKS = [
    ("leaf1","Et1",".1", "spine1","Et1",".2",  "10.1.0.0/30","dc"),
    ("leaf1","Et2",".5", "spine2","Et1",".6",  "10.1.0.4/30","dc"),
    ("leaf2","Et1",".9", "spine1","Et2",".10", "10.1.0.8/30","dc"),
    ("leaf2","Et2",".13","spine2","Et2",".14", "10.1.0.12/30","dc"),
    ("leaf3","Et1",".17","spine1","Et3",".18", "10.1.0.16/30","dc"),
    ("leaf3","Et2",".21","spine2","Et3",".22", "10.1.0.20/30","dc"),
    ("bl1","Et1",".25","spine1","Et4",".26",   "10.1.0.24/30","border"),
    ("bl1","Et2",".29","spine2","Et4",".30",   "10.1.0.28/30","border"),
    ("bl1","Et3",".33","core1","Et1",".34",    "10.1.0.32/30","xwan"),
    ("bl1","Et4",".37","core2","Et1",".38",    "10.1.0.36/30","xwan"),
    ("core1","Et2",".41","core2","Et2",".42",  "10.1.0.40/30","wan"),
    ("core1","Et3",".45","isp","eth1",".46",   "10.1.0.44/30","peer"),
    ("core2","Et3",".49","isp","eth2",".50",   "10.1.0.48/30","peer"),
    ("h1","eth1","", "leaf1","Et3","",  "vlan1000 / vni101010","host"),
    ("h2","eth1","", "leaf2","Et3","",  "vlan1000 / vni101010","host"),
    ("h3","eth1","", "leaf3","Et3","",  "vlan1000 / vni101010","host"),
]

ROLE = {
    "spine":  dict(w=150,h=62,fill="var(--dc-fill)",  stroke="var(--dc)"),
    "leaf":   dict(w=150,h=62,fill="var(--dc-fill)",  stroke="var(--dc)"),
    "border": dict(w=176,h=66,fill="var(--bd-fill)",  stroke="var(--bd)"),
    "core":   dict(w=150,h=62,fill="var(--wan-fill)", stroke="var(--wan)"),
    "isp":    dict(w=176,h=62,fill="var(--peer-fill)",stroke="var(--peer)"),
    "host":   dict(w=118,h=46,fill="var(--host-fill)",stroke="var(--host)"),
}
LINKCOL = {"dc":"var(--dc)","border":"var(--bd)","xwan":"var(--bd)",
           "wan":"var(--wan)","peer":"var(--peer)","host":"var(--host)"}

def edge(cx, cy, w, h, tx, ty):
    """Point where line from (cx,cy)->(tx,ty) leaves the box."""
    dx, dy = tx-cx, ty-cy
    if dx == 0 and dy == 0: return cx, cy
    hw, hh = w/2, h/2
    sx = hw/abs(dx) if dx else 1e9
    sy = hh/abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx+dx*s, cy+dy*s

def lerp(ax,ay,bx,by,t): return ax+(bx-ax)*t, ay+(by-ay)*t

out = []
def A(s): out.append(s)

# ---- links (drawn first, under nodes) ----
link_svg, label_svg = [], []
for a,aif,aip,b,bif,bip,sub,kind in LINKS:
    ax,ay = NODES[a][0],NODES[a][1]; bx,by = NODES[b][0],NODES[b][1]
    aw,ah = ROLE[NODES[a][2]]["w"],ROLE[NODES[a][2]]["h"]
    bw,bh = ROLE[NODES[b][2]]["w"],ROLE[NODES[b][2]]["h"]
    x1,y1 = edge(ax,ay,aw,ah,bx,by)
    x2,y2 = edge(bx,by,bw,bh,ax,ay)
    col = LINKCOL[kind]
    dash = ' stroke-dasharray="7 5"' if kind=="peer" else ""
    link_svg.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="2.2"{dash}/>')
    # interface labels near each end
    ix,iy = lerp(x1,y1,x2,y2,0.11)
    jx,jy = lerp(x1,y1,x2,y2,0.89)
    if aif:
        label_svg.append(f'<text x="{ix:.0f}" y="{iy:.0f}" class="ifl">{aif}{(" ."+aip[1:]) if aip else ""}</text>')
    if bif:
        label_svg.append(f'<text x="{jx:.0f}" y="{jy:.0f}" class="ifl">{bif}{(" ."+bip[1:]) if bip else ""}</text>')
    # subnet pill only on links with room (WAN/peer/xwan/host); DC Clos octets suffice
    if kind not in ("dc","border"):
        mx,my = lerp(x1,y1,x2,y2,0.5)
        pw = len(sub)*6.4+10
        pc = "var(--pill-peer)" if kind=="peer" else ("var(--pill-host)" if kind=="host" else "var(--pill)")
        label_svg.append(f'<g><rect x="{mx-pw/2:.0f}" y="{my-9:.0f}" width="{pw:.0f}" height="17" rx="8" fill="{pc}" stroke="{col}" stroke-width="0.8"/><text x="{mx:.0f}" y="{my+3:.0f}" class="subn" text-anchor="middle">{sub}</text></g>')

# ---- zones ----
A(f'<rect x="24" y="46" width="{VBW-48}" height="550" rx="14" class="zone-dc"/>')
A(f'<text x="44" y="76" class="zlab" fill="var(--dc)">RESEARCH DC — EVPN/VXLAN overlay · OSPF underlay · AS 65000</text>')
A(f'<rect x="24" y="662" width="{VBW-48}" height="366" rx="14" class="zone-wan"/>')
A(f'<text x="44" y="692" class="zlab" fill="var(--wan)">WAN — IS-IS L2 + SR-MPLS · AS 65000</text>')
# boundary
A(f'<line x1="24" y1="{BOUNDARY_Y}" x2="{VBW-24}" y2="{BOUNDARY_Y}" stroke="var(--bd)" stroke-width="2.4" stroke-dasharray="10 7"/>')
A(f'<rect x="{VBW/2-215:.0f}" y="{BOUNDARY_Y-15}" width="430" height="30" rx="15" fill="var(--bd-fill)" stroke="var(--bd)" stroke-width="1.2"/>')
A(f'<text x="{VBW/2:.0f}" y="{BOUNDARY_Y+5}" text-anchor="middle" class="bdlab">★ ISLAND BOUNDARY — no OSPF↔IS-IS redistribution</text>')

for s in link_svg: A(s)

# ---- nodes ----
for name,(cx,cy,role,lo,mgmt,sub) in NODES.items():
    r = ROLE[role]; w,h = r["w"],r["h"]
    A(f'<g><rect x="{cx-w/2:.0f}" y="{cy-h/2:.0f}" width="{w}" height="{h}" rx="9" fill="{r["fill"]}" stroke="{r["stroke"]}" stroke-width="2"/>')
    if role=="host":
        A(f'<text x="{cx:.0f}" y="{cy-3:.0f}" text-anchor="middle" class="nname">{name}</text>')
        A(f'<text x="{cx:.0f}" y="{cy+13:.0f}" text-anchor="middle" class="nsub">{lo}</text></g>')
    else:
        A(f'<text x="{cx:.0f}" y="{cy-9:.0f}" text-anchor="middle" class="nname">{name}</text>')
        A(f'<text x="{cx:.0f}" y="{cy+7:.0f}" text-anchor="middle" class="nlo">lo {lo}</text>')
        A(f'<text x="{cx:.0f}" y="{cy+22:.0f}" text-anchor="middle" class="nsub">{sub} · m{mgmt}</text></g>')

for s in label_svg: A(s)

svg_body = "\n".join(out)

HTML = f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=yes">
<title>dclab topology — HRT lab</title>
<style>
:root{{
  --bg:#f6f7f9; --card:#fff; --ink:#0f172a; --muted:#64748b;
  --dc:#2563eb; --dc-fill:#eff6ff; --wan:#7c3aed; --wan-fill:#f5f3ff;
  --peer:#059669; --peer-fill:#ecfdf5; --bd:#dc2626; --bd-fill:#fef2f2;
  --host:#475569; --host-fill:#f1f5f9;
  --pill:#ffffff; --pill-host:#f1f5f9; --pill-peer:#ecfdf5;
  --zone-dc:#dbeafe55; --zone-wan:#ede9fe55;
}}
@media (prefers-color-scheme: dark){{
  :root{{ --bg:#0b1120; --card:#111827; --ink:#e5e7eb; --muted:#94a3b8;
    --dc:#60a5fa; --dc-fill:#0b1e3b; --wan:#a78bfa; --wan-fill:#1e1633;
    --peer:#34d399; --peer-fill:#062b20; --bd:#f87171; --bd-fill:#3b0d0d;
    --host:#94a3b8; --host-fill:#1e293b;
    --pill:#0f172a; --pill-host:#1e293b; --pill-peer:#062b20;
    --zone-dc:#1e3a8a33; --zone-wan:#4c1d9533; }}
}}
:root[data-theme=dark]{{ --bg:#0b1120; --card:#111827; --ink:#e5e7eb; --muted:#94a3b8;
  --dc:#60a5fa; --dc-fill:#0b1e3b; --wan:#a78bfa; --wan-fill:#1e1633;
  --peer:#34d399; --peer-fill:#062b20; --bd:#f87171; --bd-fill:#3b0d0d;
  --host:#94a3b8; --host-fill:#1e293b; --pill:#0f172a; --pill-host:#1e293b;
  --pill-peer:#062b20; --zone-dc:#1e3a8a33; --zone-wan:#4c1d9533; }}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1300px;margin:0 auto;padding:16px}}
h1{{font-size:19px;margin:6px 0 2px}} .sub{{color:var(--muted);font-size:13px;margin:0 0 12px}}
.card{{background:var(--card);border:1px solid #94a3b833;border-radius:16px;padding:10px;overflow:auto}}
svg{{width:100%;height:auto;min-width:820px;display:block}}
.zone-dc{{fill:var(--zone-dc);stroke:var(--dc);stroke-width:1;stroke-dasharray:3 4}}
.zone-wan{{fill:var(--zone-wan);stroke:var(--wan);stroke-width:1;stroke-dasharray:3 4}}
.zlab{{font:600 15px sans-serif}}
.bdlab{{font:700 13px sans-serif;fill:var(--bd)}}
.nname{{font:700 16px sans-serif;fill:var(--ink)}}
.nlo{{font:600 12px ui-monospace,monospace;fill:var(--ink)}}
.nsub{{font:11px sans-serif;fill:var(--muted)}}
.ifl{{font:600 11px ui-monospace,monospace;fill:var(--ink)}}
.subn{{font:10px ui-monospace,monospace;fill:var(--ink)}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;margin-top:12px;font-size:13px}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}
.sw{{width:22px;height:4px;border-radius:2px;display:inline-block}}
.note{{color:var(--muted);font-size:12.5px;margin-top:10px;line-height:1.5}}
code{{background:#94a3b822;padding:1px 5px;border-radius:4px;font-size:12px}}
</style>
<div class="wrap">
<h1>dclab — HRT prep topology</h1>
<p class="sub">EC2 · netlab/containerlab · pinch to zoom · login <code>admin/admin</code> · <code>netlab connect &lt;node&gt;</code></p>
<div class="card">
<svg viewBox="0 0 {VBW} {VBH}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
{svg_body}
</svg>
</div>
<div class="legend">
  <span><i class="sw" style="background:var(--dc)"></i>DC fabric (OSPF/EVPN)</span>
  <span><i class="sw" style="background:var(--bd)"></i>border / DC↔WAN</span>
  <span><i class="sw" style="background:var(--wan)"></i>WAN (IS-IS-SR)</span>
  <span><i class="sw" style="background:var(--peer)"></i>eBGP peering (EPE)</span>
  <span><i class="sw" style="background:var(--host)"></i>host access</span>
</div>
<p class="note">
All P2P links are <code>/30</code> in <code>10.1.0.0/24</code>; only the host octet is shown at each interface (e.g. <code>Et1 .34</code> = <code>10.1.0.34</code>). Loopbacks <code>10.0.0.X/32</code>, mgmt <code>192.168.121.10X</code> (shown as <code>m.10X</code>). Hosts share one stretched L2 (VLAN 1000 / VNI 101010) across the three leaves.
<br><b>The red boundary:</b> bl1 runs OSPF and IS-IS-SR side by side with no redistribution, so the DC and WAN can't reach each other's loopbacks yet — that's the stitch to build.
</p>
</div>
"""
open("/private/tmp/claude-501/-Users-fazmemon-Documents-dev/0c9e181c-930f-4f27-af06-9d7639575bc4/scratchpad/sr-mpls-refresh/dclab-topology.html","w").write(HTML)
print("wrote dclab-topology.html", len(HTML), "bytes")
