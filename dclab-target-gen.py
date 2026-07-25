#!/usr/bin/env python3
"""TARGET architecture diagram (for approval) — 2-AS SR-MPLS + EVPN DC +
inter-AS BGP-LU + EPE + PIM-SSM market data + Traffic Dictator controller."""

VBW, VBH = 1360, 1500

# name: (cx, cy, role, [line1,line2,line3])
NODES = {
    "spine1": (350,250,"dc",   ["spine1","OSPF-SR · EVPN-RR","lo 10.0.0.1"]),
    "spine2": (700,250,"dc",   ["spine2","OSPF-SR · EVPN-RR","lo 10.0.0.2"]),
    "leaf1":  (300,410,"dc",   ["leaf1","VTEP · OSPF-SR","lo 10.0.0.3"]),
    "leaf2":  (660,410,"dc",   ["leaf2","VTEP · OSPF-SR","lo 10.0.0.4"]),
    "h1":     (300,555,"host", ["h1","tenant · md-rx","172.16.0.10"]),
    "h2":     (660,555,"host", ["h2","tenant · md-rx","172.16.0.11"]),
    "bl1":    (500,725,"sr1",  ["bl1","border-leaf · OSPF-SR","lo 10.0.0.6"]),
    "core1":  (360,895,"sr1",  ["core1","OSPF-SR core · ASBR1","lo 10.0.0.7"]),
    "core2":  (700,895,"sr1",  ["core2","OSPF-SR · TI-LFA/FlexAlgo","lo 10.0.0.8"]),
    "asbr2":  (360,1130,"sr2", ["asbr2","ASBR · OSPF-SR","lo 10.2.0.1"]),
    "edge2":  (610,1225,"sr2", ["edge2","SR egress · EPE SIDs","lo 10.2.0.2"]),
    "peer1":  (470,1415,"peer",["peer1  (P)","peer · AS 65100","FRR"]),
    "transit1":(760,1415,"tran",["transit1  (T)","transit · AS 65200","FRR"]),
    "mdsrc":  (960,1225,"mcast",["mktdata","PIM-SSM source","exchange feed"]),
    "td":     (1185,830,"ctrl", ["Traffic Dictator","SR-TE controller","BGP-LS + SR-Policy"]),
}

# (a, b, kind, label)
LINKS = [
    ("leaf1","spine1","dc",""),("leaf1","spine2","dc",""),
    ("leaf2","spine1","dc",""),("leaf2","spine2","dc",""),
    ("bl1","spine1","dc",""),("bl1","spine2","dc",""),
    ("h1","leaf1","host",""),("h2","leaf2","host",""),
    ("bl1","core1","sr1",""),("bl1","core2","sr1",""),
    ("core1","core2","sr1",""),
    ("core1","asbr2","interas","BGP-LU · inter-AS SR"),
    ("asbr2","edge2","sr2",""),
    ("edge2","peer1","epe","eBGP · EPE"),
    ("edge2","transit1","epet","eBGP · EPE"),
    ("edge2","mdsrc","mcast","PIM-SSM feed"),
    ("td","core1","ctrl","BGP-LS / SR-Policy"),
]

ROLE = {
    "dc":   dict(w=176,h=66,fill="var(--dc-fill)",  stroke="var(--dc)"),
    "sr1":  dict(w=190,h=66,fill="var(--sr1-fill)", stroke="var(--sr1)"),
    "sr2":  dict(w=176,h=66,fill="var(--sr2-fill)", stroke="var(--sr2)"),
    "host": dict(w=140,h=58,fill="var(--host-fill)",stroke="var(--host)"),
    "peer": dict(w=150,h=62,fill="var(--peer-fill)",stroke="var(--peer)"),
    "tran": dict(w=160,h=62,fill="var(--tran-fill)",stroke="var(--tran)"),
    "mcast":dict(w=150,h=62,fill="var(--mcast-fill)",stroke="var(--mcast)"),
    "ctrl": dict(w=182,h=66,fill="var(--ctrl-fill)",stroke="var(--ctrl)"),
}
LINKCOL = {"dc":"var(--dc)","host":"var(--host)","sr1":"var(--sr1)","sr2":"var(--sr2)",
           "interas":"var(--bd)","epe":"var(--peer)","epet":"var(--tran)",
           "mcast":"var(--mcast)","ctrl":"var(--ctrl)"}
DASH = {"interas":"9 5","epe":"7 5","epet":"7 5","mcast":"6 5","ctrl":"5 5"}

def edge(cx,cy,w,h,tx,ty):
    dx,dy=tx-cx,ty-cy
    if dx==0 and dy==0: return cx,cy
    s=min((w/2)/abs(dx) if dx else 1e9,(h/2)/abs(dy) if dy else 1e9)
    return cx+dx*s,cy+dy*s
def lerp(ax,ay,bx,by,t): return ax+(bx-ax)*t,ay+(by-ay)*t

out=[]; A=out.append
link_svg=[]; label_svg=[]
for a,b,kind,lab in LINKS:
    ax,ay=NODES[a][0],NODES[a][1]; bx,by=NODES[b][0],NODES[b][1]
    aw,ah=ROLE[NODES[a][2]]["w"],ROLE[NODES[a][2]]["h"]
    bw,bh=ROLE[NODES[b][2]]["w"],ROLE[NODES[b][2]]["h"]
    x1,y1=edge(ax,ay,aw,ah,bx,by); x2,y2=edge(bx,by,bw,bh,ax,ay)
    col=LINKCOL[kind]; d=DASH.get(kind,"")
    da=f' stroke-dasharray="{d}"' if d else ""
    sw="2.6" if kind in ("interas",) else "2.2"
    link_svg.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="{sw}"{da}/>')
    if lab:
        tl={"interas":0.30,"ctrl":0.40}.get(kind,0.5)
        mx,my=lerp(x1,y1,x2,y2,tl); pw=len(lab)*6.7+14
        label_svg.append(f'<g><rect x="{mx-pw/2:.0f}" y="{my-11:.0f}" width="{pw:.0f}" height="21" rx="10" fill="var(--card)" stroke="{col}" stroke-width="1.2"/><text x="{mx:.0f}" y="{my+3:.0f}" class="llab" fill="{col}" text-anchor="middle">{lab}</text></g>')

# zones
A(f'<rect x="46" y="120" width="866" height="858" rx="16" class="z-as1"/>')
A(f'<text x="66" y="150" class="zbig" fill="var(--sr1)">AS 65001 — your estate · OSPF-SR + EVPN/VXLAN</text>')
A(f'<rect x="78" y="172" width="800" height="426" rx="12" class="z-dc"/>')
A(f'<text x="96" y="194" class="zsm" fill="var(--dc)">DC — EVPN/VXLAN · OSPF-SR underlay · tenants + md receivers</text>')
A(f'<rect x="78" y="630" width="800" height="320" rx="12" class="z-core"/>')
A(f'<text x="96" y="652" class="zsm" fill="var(--sr1)">Core — OSPF-SR · TI-LFA · Flex-Algo · ASBR1=core1</text>')
# inter-AS boundary
A(f'<line x1="46" y1="1002" x2="912" y2="1002" stroke="var(--bd)" stroke-width="2.4" stroke-dasharray="11 7"/>')
A(f'<rect x="520" y="987" width="440" height="30" rx="15" fill="var(--card)" stroke="var(--bd)" stroke-width="1.3"/>')
A(f'<text x="740" y="1007" text-anchor="middle" class="bdlab">AS 65001 ⟷ AS 65002 · inter-AS SR-MPLS (BGP-LU)</text>')
# AS2 zone
A(f'<rect x="46" y="1032" width="866" height="258" rx="16" class="z-as2"/>')
A(f'<text x="66" y="1062" class="zbig" fill="var(--sr2)">AS 65002 — SR exit AS · OSPF-SR</text>')
# external band label
A(f'<text x="66" y="1345" class="zsm" fill="var(--host)">EXTERNAL EXITS — EPE chooses peer vs transit</text>')

for s in link_svg: A(s)

for name,(cx,cy,role,lines) in NODES.items():
    r=ROLE[role]; w,h=r["w"],r["h"]
    A(f'<g><rect x="{cx-w/2:.0f}" y="{cy-h/2:.0f}" width="{w}" height="{h}" rx="10" fill="{r["fill"]}" stroke="{r["stroke"]}" stroke-width="2.2"/>')
    if len(lines)==3 and h>=62:
        A(f'<text x="{cx:.0f}" y="{cy-12:.0f}" text-anchor="middle" class="nname">{lines[0]}</text>')
        A(f'<text x="{cx:.0f}" y="{cy+5:.0f}" text-anchor="middle" class="nrole">{lines[1]}</text>')
        A(f'<text x="{cx:.0f}" y="{cy+21:.0f}" text-anchor="middle" class="nlo">{lines[2]}</text></g>')
    else:
        A(f'<text x="{cx:.0f}" y="{cy-8:.0f}" text-anchor="middle" class="nname">{lines[0]}</text>')
        A(f'<text x="{cx:.0f}" y="{cy+8:.0f}" text-anchor="middle" class="nrole">{lines[1]}</text>')
        A(f'<text x="{cx:.0f}" y="{cy+22:.0f}" text-anchor="middle" class="nlo">{lines[2] if len(lines)>2 else ""}</text></g>')

for s in label_svg: A(s)
body="\n".join(out)

HTML=f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=yes">
<title>TARGET architecture — HRT lab (for approval)</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#0f172a;--muted:#64748b;
 --dc:#2563eb;--dc-fill:#eff6ff;--sr1:#7c3aed;--sr1-fill:#f5f3ff;
 --sr2:#0891b2;--sr2-fill:#ecfeff;--bd:#dc2626;--host:#475569;--host-fill:#f1f5f9;
 --peer:#059669;--peer-fill:#ecfdf5;--tran:#d97706;--tran-fill:#fffbeb;
 --mcast:#ea580c;--mcast-fill:#fff7ed;--ctrl:#db2777;--ctrl-fill:#fdf2f8;
 --z-as1:#7c3aed11;--z-as2:#0891b211;--z-dc:#2563eb0d;--z-core:#7c3aed0d;}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0b1120;--card:#111827;--ink:#e5e7eb;--muted:#94a3b8;
 --dc:#60a5fa;--dc-fill:#0b1e3b;--sr1:#a78bfa;--sr1-fill:#1e1633;--sr2:#22d3ee;--sr2-fill:#083344;
 --bd:#f87171;--host:#94a3b8;--host-fill:#1e293b;--peer:#34d399;--peer-fill:#062b20;
 --tran:#fbbf24;--tran-fill:#3a2a08;--mcast:#fb923c;--mcast-fill:#3a1e0a;--ctrl:#f472b6;--ctrl-fill:#3a0f26;
 --z-as1:#7c3aed22;--z-as2:#0891b222;--z-dc:#2563eb18;--z-core:#7c3aed18;}}}}
:root[data-theme=dark]{{--bg:#0b1120;--card:#111827;--ink:#e5e7eb;--muted:#94a3b8;
 --dc:#60a5fa;--dc-fill:#0b1e3b;--sr1:#a78bfa;--sr1-fill:#1e1633;--sr2:#22d3ee;--sr2-fill:#083344;
 --bd:#f87171;--host:#94a3b8;--host-fill:#1e293b;--peer:#34d399;--peer-fill:#062b20;
 --tran:#fbbf24;--tran-fill:#3a2a08;--mcast:#fb923c;--mcast-fill:#3a1e0a;--ctrl:#f472b6;--ctrl-fill:#3a0f26;
 --z-as1:#7c3aed22;--z-as2:#0891b222;--z-dc:#2563eb18;--z-core:#7c3aed18;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1400px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:6px 0 2px}}.sub{{color:var(--muted);font-size:13px;margin:0 0 12px;line-height:1.5}}
.card{{background:var(--card);border:1px solid #94a3b833;border-radius:16px;padding:10px;overflow:auto}}
svg{{width:100%;height:auto;min-width:900px;display:block}}
.z-as1{{fill:var(--z-as1);stroke:var(--sr1);stroke-width:1.4;stroke-dasharray:4 4}}
.z-as2{{fill:var(--z-as2);stroke:var(--sr2);stroke-width:1.4;stroke-dasharray:4 4}}
.z-dc{{fill:var(--z-dc);stroke:var(--dc);stroke-width:1;stroke-dasharray:3 4}}
.z-core{{fill:var(--z-core);stroke:var(--sr1);stroke-width:1;stroke-dasharray:3 4}}
.zbig{{font:700 15px sans-serif}}.zsm{{font:600 12.5px sans-serif}}
.bdlab{{font:700 13px sans-serif;fill:var(--bd)}}
.nname{{font:700 15px sans-serif;fill:var(--ink)}}.nrole{{font:10.5px sans-serif;fill:var(--muted)}}
.nlo{{font:600 11px ui-monospace,monospace;fill:var(--ink)}}
.llab{{font:700 11px sans-serif}}
.legend{{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;font-size:12.5px}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}.sw{{width:22px;height:4px;border-radius:2px}}
.note{{color:var(--muted);font-size:12.5px;margin-top:10px;line-height:1.55}}
code{{background:#94a3b822;padding:1px 5px;border-radius:4px;font-size:12px}}
</style>
<div class="wrap">
<h1>TARGET architecture — for approval</h1>
<p class="sub">2-AS SR-MPLS network: EVPN/VXLAN DC → OSPF-SR core → <b>inter-AS SR via BGP-LU</b> → AS2 exit → <b>EPE</b> (peer vs transit) · <b>PIM-SSM</b> market data · <b>Traffic Dictator</b> SR-TE controller · EVPN tenants. Not built yet — approve and I build it.</p>
<div class="card">
<svg viewBox="0 0 {VBW} {VBH}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
{body}
</svg>
</div>
<div class="legend">
 <span><i class="sw" style="background:var(--dc)"></i>DC fabric (EVPN/OSPF-SR)</span>
 <span><i class="sw" style="background:var(--sr1)"></i>AS1 SR core</span>
 <span><i class="sw" style="background:var(--sr2)"></i>AS2 SR</span>
 <span><i class="sw" style="background:var(--bd)"></i>inter-AS BGP-LU</span>
 <span><i class="sw" style="background:var(--peer)"></i>EPE peer</span>
 <span><i class="sw" style="background:var(--tran)"></i>EPE transit</span>
 <span><i class="sw" style="background:var(--mcast)"></i>PIM-SSM</span>
 <span><i class="sw" style="background:var(--ctrl)"></i>controller</span>
</div>
<p class="note">
<b>What it drills:</b> OSPF-SR fabric-wide (SRGB, prefix-SIDs) · TI-LFA + Flex-Algo on the core · SR-TE by hand and via Traffic Dictator · <b>inter-AS SR-MPLS</b> stitched ASBR-to-ASBR with BGP-LU (SAFI 4) · <b>EPE</b> Peer-Node-SIDs at edge2 to pick peer(65100) vs transit(65200) · <b>PIM-SSM</b> (S,G) market-data tree from <code>mktdata</code> to the DC trading hosts (IGMPv3 joins) · EVPN multi-tenancy (VRF/VNI) + the SDN-connector / k8s-CNI discussion.
<br><b>15 nodes:</b> 10× cEOS for the SR/EVPN nodes, 5× FRR/Linux for the edges + hosts + feed (fits 32 GB; upsize the box if we push further). Loopbacks/AS numbers shown are the planned scheme.
</p>
</div>
"""
open("/private/tmp/claude-501/-Users-fazmemon-Documents-dev/0c9e181c-930f-4f27-af06-9d7639575bc4/scratchpad/dclab-target.html","w").write(HTML)
print("wrote dclab-target.html", len(HTML))
