#!/usr/bin/env python3
"""Generate SYS/ADHERENT_Harness_Wiring_Diagram.drawio (pin-level harness diagram, 3 pages).

Page 1  Harness wiring  - devices with product photos, connector.pin boxes and conductor-level wires.
                          Every build step is its own draw.io layer, so the harness can be derived
                          one step at a time (View > Layers).
Page 2  Cable schedule  - every cable / conductor per step, with instances, lengths and status.
Page 3  Connectors      - connector reference (board header, mating part, pin map, source).

Sources (checked 2026-09-26): LANECTRL R1 SchDoc/PcbDoc, NFC R1 netlist, SYSCTRL R1 netlist
(2026-09-25 20:17, early draft), ADHERENT_Electrical_Tables.xlsx, Mean Well RSP-500 spec,
Anaheim 23MSD manual (McMaster 6627T113), McMaster 6627T357 page, Emtech listing, Omron
EE-SX47/67 datasheet, Waveshare wiki/product page, MYIR MYD-YF13X page, Molex 1462362151 drawing,
CB002 supplier sheet, R27 harness register (git history) for cable IDs and length estimates.
"""
import base64, html, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "SYS/ADHERENT_Harness_Wiring_Diagram.drawio"
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "harness_img")
F = "fontFamily=Helvetica;"

# ----------------------------------------------------------------------------- colours
C = dict(
    L="#6D4C41", N="#1E88E5", PE="#43A047", P24="#E53935", P12="#FB8C00", GND="#212121",
    CAN="#3949AB", RS="#00ACC1", ETH="#546E7A", CTL="#8E24AA", FB="#C79100", MA="#00897B",
    MB="#D81B60", RF="#7356A0", TBC="#9E9E9E", WARN="#D32F2F", INK="#212121", SUB="#5F6B76",
)


def esc(s):
    return html.escape(s, quote=True)


def img_uri(name):
    with open(os.path.join(IMG, name + ".jpg"), "rb") as fh:
        return "data:image/jpeg," + base64.b64encode(fh.read()).decode()


class Page:
    def __init__(self, pid, name, w, h):
        self.pid, self.name, self.w, self.h = pid, name, w, h
        self.cells, self.geo, self.n = [], {}, 0

    def uid(self, p="c"):
        self.n += 1
        return f"{self.pid}_{p}{self.n}"

    def layer(self, lid, name, visible=True):
        vis = "" if visible else ' visible="0"'
        self.cells.append(f'<mxCell id="{lid}" value="{esc(name)}" parent="0"{vis} />')
        self.geo[lid] = (0, 0, 0, 0)

    def v(self, id, x, y, w, h, value, style, parent):
        px, py = self.geo[parent][:2]
        self.geo[id] = (px + x, py + y, w, h)
        self.cells.append(f'<mxCell id="{id}" value="{esc(value)}" style="{style}" vertex="1" parent="{parent}">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>')
        return id

    def e(self, id, src, tgt, value, style, parent, pts=(), lx=0.0):
        pts_xml = "".join(f'<mxPoint x="{a}" y="{b}" />' for a, b in pts)
        arr = f'<Array as="points">{pts_xml}</Array>' if pts else ""
        self.cells.append(f'<mxCell id="{id}" value="{esc(value)}" style="{style}" edge="1" parent="{parent}" '
                          f'source="{src}" target="{tgt}"><mxGeometry x="{lx}" relative="1" as="geometry">{arr}'
                          f'</mxGeometry></mxCell>')

    def free_line(self, id, x1, y1, x2, y2, style, parent):
        self.cells.append(f'<mxCell id="{id}" value="" style="{style}" edge="1" parent="{parent}">'
                          f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x1}" y="{y1}" as="sourcePoint" />'
                          f'<mxPoint x="{x2}" y="{y2}" as="targetPoint" /></mxGeometry></mxCell>')

    def xml(self):
        return (f'<diagram id="{self.pid}" name="{esc(self.name)}"><mxGraphModel dx="1800" dy="1100" grid="1" '
                f'gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
                f'pageWidth="{self.w}" pageHeight="{self.h}" background="#FFFFFF" math="0" shadow="0"><root>'
                f'<mxCell id="0" />' + "".join(self.cells) + '</root></mxGraphModel></diagram>')


# ============================================================================= PAGE 1
P = Page("hw", "1 · Harness wiring", 4920, 2330)
LAYERS = [
    ("L0", "Devices · connectors · photos"),
    ("L1", "Step 1 · AC mains & protective earth"),
    ("L2", "Step 2 · 24 V main feed"),
    ("L3", "Step 3 · Cabinet DC branches"),
    ("L4", "Step 4 · CAN bus"),
    ("L5", "Step 5 · Ethernet & RS485"),
    ("L6", "Step 6 · Gantry X / Z drives"),
    ("L7", "Step 7 · Labeling motors & servo"),
    ("L8", "Step 8 · Sensors"),
    ("L9", "Step 9 · Doors & latches"),
    ("L10", "Step 10 · Lane rows"),
    ("L11", "Step 11 · Status light & marker (TBC)"),
    ("LN", "Notes · legend · open issues"),
]
for lid, name in LAYERS:
    P.layer(lid, name)
STEP_NO = {lid: i for i, (lid, _) in enumerate(LAYERS)}
CIRC = "⓪①②③④⑤⑥⑦⑧⑨⑩⑪"

CONT = ("rounded=1;arcSize=2;dashed=1;dashPattern=6 4;strokeColor=#9E9E9E;fillColor=#FFFFFF;container=1;"
        "collapsible=0;recursiveResize=0;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacingLeft=8;"
        f"spacingTop=4;fontSize=14;fontColor={C['INK']};{F}")
PIN = f"rounded=0;fillColor=#FFFFFF;strokeColor=#616161;fontSize=9;html=1;whiteSpace=wrap;spacing=1;{F}"
PH = 18  # pin height (side pins) / width (top/bottom pins)


TAGS = {"CONN", "PCB", "MTR"}  # project convention: red bold category tag at the upper left of the box


def device(id, x, y, w, h, title, sub="", tag=None, stroke="#9E9E9E", tx=8):
    pre = f'<font color="#FF0000">{tag}</font>&nbsp; ' if tag in TAGS else ""
    val = f"<b>{pre}{title}</b>" + (f'<br><font style="font-size:10px" color="{C["SUB"]}">{sub}</font>' if sub else "")
    st = CONT.replace("strokeColor=#9E9E9E", f"strokeColor={stroke}").replace("spacingLeft=8;", f"spacingLeft={tx};")
    P.v(id, x, y, w, h, val, st, "L0")
    return id


def pins(dev, side, items, pw=150, ph=64):
    """items: list of (abs_coord, label, pin_id). side L/R: abs y centre. T/B: abs x centre."""
    dx, dy, dw, dh = P.geo[dev]
    for coord, label, pid in items:
        if side == "L":
            P.v(pid, 6, coord - dy - PH / 2, pw, PH, label, PIN + "align=left;spacingLeft=4;", dev)
        elif side == "R":
            P.v(pid, dw - 6 - pw, coord - dy - PH / 2, pw, PH, label, PIN + "align=right;spacingRight=4;", dev)
        elif side == "T":
            P.v(pid, coord - dx - PH / 2, 6, PH, ph, label, PIN + "horizontal=0;", dev)
        elif side == "B":
            P.v(pid, coord - dx - PH / 2, dh - 6 - ph, PH, ph, label, PIN + "horizontal=0;", dev)


def photo(dev, name, rx, ry, rw, rh, caption=None):
    P.v(dev + "_ph", rx, ry, rw, rh, "", "rounded=0;fillColor=#F7F7F7;strokeColor=#E0E0E0;connectable=0;html=1;", dev)
    P.v(dev + "_img", rx + 4, ry + 4, rw - 8, rh - 8, "",
        f"shape=image;html=1;imageAspect=1;aspect=fixed;connectable=0;image={img_uri(name)};", dev)
    if caption:
        P.v(dev + "_cap", rx, ry + rh + 1, rw, 14, caption,
            f"text;html=1;align=center;verticalAlign=top;fontSize=8;fontColor=#8A949C;{F}"
            "strokeColor=none;fillColor=none;spacing=0;connectable=0;", dev)


def note(dev_or_layer, id, rx, ry, rw, rh, text, fs=9, color=C["SUB"], box=False, warn=False, align="left"):
    st = (f"text;html=1;align={align};verticalAlign=top;whiteSpace=wrap;fontSize={fs};fontColor={color};{F}"
          "spacing=3;connectable=0;")
    if box:
        st += "strokeColor=#CFD8DC;fillColor=#FAFBFC;rounded=0;"
    else:
        st += "strokeColor=none;fillColor=none;"
    if warn:
        st = (f"rounded=0;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontSize={fs};{F}spacing=5;"
              f"fillColor=#FFEBEE;strokeColor={C['WARN']};strokeWidth=1.5;fontColor=#B71C1C;connectable=0;")
    P.v(id, rx, ry, rw, rh, text, st, dev_or_layer)


def wire(layer, src, tgt, label, col, width=1.8, dash=None, pts=(), lx=0.0, sx=(1, 0.5), tx=(0, 0.5), fs=9):
    st = ("edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=none;"
          f"startArrow=none;jumpStyle=arc;jumpSize=6;fontSize={fs};labelBackgroundColor=#FFFFFF;{F}"
          f"strokeColor={col};strokeWidth={width};fontColor={col};"
          f"exitX={sx[0]};exitY={sx[1]};exitDx=0;exitDy=0;entryX={tx[0]};entryY={tx[1]};entryDx=0;entryDy=0;")
    if dash == "d":
        st += "dashed=1;dashPattern=6 3;"
    elif dash == "tbc":
        st += "dashed=1;dashPattern=2 3;"
    P.e(P.uid("w"), src, tgt, label, st, layer, pts, lx)


def pill(layer, x, y, text, col, w=None):
    w = w or (len(text) * 6.2 + 16)
    P.v(P.uid("p"), x, y, w, 18, text,
        f"rounded=1;arcSize=50;html=1;whiteSpace=wrap;fontSize=10;fontStyle=1;{F}fillColor=#FFFFFF;"
        f"strokeColor={col};fontColor={col};spacing=1;connectable=0;", layer)


# ----------------------------------------------------------------------------- title / how-to
note("LN", "title", 40, 16, 1220, 70,
     '<font style="font-size:24px"><b>ADHERENT · Harness Wiring Diagram</b></font><br>'
     'Pin-level companion to ADHERENT_System_Wiring_Diagram · Blackocean Technologies · 2026-09-26 · '
     '<b>working document for harness derivation — not a release drawing</b>', fs=12, color=C["INK"])
note("LN", "howto", 1300, 14, 2330, 78,
     "<b>How to use</b> · Layers = build steps ①…⑪ (draw.io: View ▸ Layers, Ctrl+Shift+L) — switch on one step at a time "
     "and cut / crimp that step only. · Pin box = <b>connector.pin · signal</b> (board side) or <b>lead colour · function</b> "
     "(device side). · Boxes marked ×n are typical: one drawing stands for n identical instances; page 2 lists every "
     "instance with cable ID and length. · Dotted wire = TBC (not yet defined in the design files). · "
     '<font color="#D32F2F"><b>⚠ red box = interface conflict found in the documents — resolve before crimping.</b></font> '
     "· Cable IDs (W01…W39) follow the project harness register.", fs=11, color=C["INK"], box=True)

# ----------------------------------------------------------------------------- LEFT COLUMN
device("SITE", 40, 250, 220, 150, "SITE LAN", "customer network<br>site-supplied")
pins("SITE", "R", [(320, "RJ45 · site patch", "site_rj")], pw=110)

device("J2", 300, 230, 280, 190, "J2 · RJ45 PANEL ADAPTER", "McMaster-Carr 1422N13 · rear panel", tag="CONN")
pins("J2", "L", [(320, "EXT · RJ45", "j2_ext")], pw=64)
pins("J2", "R", [(320, "INT · RJ45", "j2_int")], pw=64)
photo("J2", "J2", 80, 44, 120, 124, "image: supplied example diagram")

device("MRK", 40, 470, 590, 150, "MARKER · label marker", "on the labeling mechanism · model TBC", tag="TBC")
pins("MRK", "R", [(540, "DATA · W19 (interface TBC)", "mrk_d"), (590, "PWR · W39 (TBC)", "mrk_p")], pw=160)
note("MRK", "mrk_n", 10, 44, 400, 90, "Marker / printer not selected — data link and supply are open items "
     "(W19, W39). No harness can be built for this step yet.", fs=10)

device("MAIN", 720, 210, 560, 430, "MAINCTRL · MYIR MYD-YF13X", "STM32MP135 · Linux · purchased ×1", tag="PCB")
pins("MAIN", "L", [(320, "ETH0 · RJ45", "m_eth"), (540, "MARKER DATA (TBC)", "m_mrk")], pw=110)
pins("MAIN", "R", [(510, "DC jack + · 12 V", "m_12p"), (532, "DC jack − · 0 V", "m_12n")], pw=110)
pins("MAIN", "T", [(1020, "CAN_H", "m_ch"), (1042, "CAN_L", "m_cl")], ph=60)
pins("MAIN", "B", [(1100, "RS485 A", "m_ra"), (1122, "RS485 B", "m_rb"), (1144, "RS485 GND", "m_rg")], ph=66)
photo("MAIN", "MAINCTRL", 130, 76, 300, 250)
note("MAIN", "main_n", 120, 334, 240, 92,
     "12 V / 2 A power jack · 1× CAN · 1× RS485 · 1× RS232 · 2× GbE RJ45 · 2× USB host · USB-C OTG (MYIR). "
     "CAN / RS485 connector pinout and plug size: TBC from the MYIR hardware manual.", fs=8)

device("IO1", 720, 740, 560, 520, "IOCTRL-01", "Waveshare ESP32-S3-ETH-8DI-8RO · I/O split with IOCTRL-02 TBC",
       tag="PCB")
pins("IO1", "T", [(1100, "A", "i1_ta"), (1122, "B", "i1_tb"), (1144, "GND", "i1_tg")], ph=40)
pins("IO1", "B", [(1100, "A", "i1_ba"), (1122, "B", "i1_bb"), (1144, "GND", "i1_bg")], ph=40)
pins("IO1", "R", [(800, "PWR + · 7–36 V", "i1_pp"), (822, "PWR − · GND", "i1_pn"),
                  (864, "RO1–RO4 COM (link)", "i1_com")], pw=120)
pins("IO1", "L", [(800, "RO1 · NO", "i1_r1"), (822, "RO2 · NO", "i1_r2"), (844, "RO3 · NO", "i1_r3"),
                  (866, "RO4 · NO", "i1_r4"), (990, "DI1", "i1_d1"), (1012, "DI2", "i1_d2"), (1034, "DI3", "i1_d3"),
                  (1056, "DI4", "i1_d4"), (1078, "DI5", "i1_d5"), (1110, "DI common (silkscreen TBC)", "i1_dc")],
     pw=120)
photo("IO1", "IOCTRL", 150, 140, 260, 140)
note("IO1", "io1_n", 136, 296, 300, 172,
     "7–36 V screw terminal · isolated RS485 screw terminal, 120 Ω jumper (NC by default) · 8 relays "
     "1NO/1NC, ≤10 A 250 VAC / 30 VDC · 8 DI 5–36 V, passive or active (NPN/PNP), bidirectional opto-isolation "
     "(Waveshare wiki / product page).<br>RO5–RO8 and DI6–DI8 spare (door actuators excluded, W28 qty 0).<br>"
     "The RS485 terminal takes the incoming and the outgoing pair (daisy-chain to IOCTRL-02).", fs=9)

device("LAT", 40, 760, 590, 150, "K1–K4 · 12 V LATCH ×4", "main · retrieval · return · table · MPN TBC", tag="TBC")
pins("LAT", "R", [(800, "K1 + (main)", "k1"), (822, "K2 + (retrieval)", "k2"), (844, "K3 + (return)", "k3"),
                  (866, "K4 + (table)", "k4"), (888, "K1–K4 − · 0 V return", "kn")], pw=150)
note("LAT", "lat_n", 10, 44, 410, 100, "Latch part not selected: coil current, duty, suppression (flyback) and "
     "fail-safe behaviour TBC. R27 register: W20 = K1 (R/B), K2 (Y/G); W21 = K3, K4 (same colours), 4-core 22 AWG, "
     "0.8 m (R / Y = + by convention); latch-side plug candidate Micro-Fit 2-pin 43025-0200.", fs=9)

device("DOOR", 40, 950, 590, 190, "DI1–DI5 · DOOR POSITION SENSOR ×5",
       "reed / microswitch TBC · 4 latch doors + front access", tag="TBC")
pins("DOOR", "R", [(990, "S1 · main", "s1"), (1012, "S2 · retrieval", "s2"), (1034, "S3 · return", "s3"),
                   (1056, "S4 · table", "s4"), (1078, "S5 · front access", "s5"), (1110, "common (all 5)", "sc")],
     pw=150)
note("DOOR", "door_n", 10, 44, 410, 120, "Sensor type not selected. Wiring mode (dry contact to DI common, "
     "or powered NPN/PNP sensor) sets which DI common / reference is used — confirm on the Waveshare "
     "silkscreen before building W23 (5 direct runs, no junction box).", fs=9)

device("IO2", 720, 1340, 560, 160, "IOCTRL-02", "Waveshare ESP32-S3-ETH-8DI-8RO · functions TBC", tag="PCB")
pins("IO2", "T", [(1100, "A", "i2_ta"), (1122, "B", "i2_tb"), (1144, "GND", "i2_tg")], ph=40)
pins("IO2", "R", [(1390, "PWR + · 7–36 V", "i2_pp"), (1412, "PWR − · GND", "i2_pn")], pw=120)
note("IO2", "io2_n", 10, 56, 340, 90, "Last RS485 node → fit its 120 Ω jumper. I/O split with IOCTRL-01 and "
     "Modbus address TBC.", fs=9)

device("MAINS", 40, 1580, 220, 180, "MAINS", "IEC C13 cord set · site outlet<br>120 / 230 VAC")
pins("MAINS", "R", [(1640, "L", "ac_l"), (1662, "N", "ac_n"), (1684, "PE", "ac_pe")], pw=60)

device("J1", 300, 1560, 330, 260, "J1 · AC INLET · FILTER · SWITCH", "Schaffner/TE FN9264-6-06 (candidate)", tag="CONN")
pins("J1", "L", [(1640, "L · C14", "j1_li"), (1662, "N · C14", "j1_ni"), (1684, "PE · C14", "j1_pei")], pw=60)
pins("J1", "R", [(1640, "L · fast-on", "j1_lo"), (1662, "N · fast-on", "j1_no"), (1760, "PE", "j1_peo")], pw=68)
photo("J1", "J1", 74, 50, 172, 150)
note("J1", "j1_n", 8, 206, 314, 52, "IEC C14 inlet + EMI filter + 2-pole switch, 6 A 250 VAC, fast-on terminals. No fuse "
     "holder: protection TBC. PSU input up to 5.3 A at 115 VAC → check margin (-10 variant).", fs=8)

device("PSU", 720, 1560, 560, 330, "PSU1 · Mean Well RSP-500-24", "24 V · 21 A · 504 W · single system supply", tag="PSU")
pins("PSU", "L", [(1640, "TB1-1 · AC/L", "ps_l"), (1662, "TB1-2 · AC/N", "ps_n")], pw=80)
pins("PSU", "R", [(1700, "TB2-4/5/6 · +V", "ps_p"), (1722, "TB2-1/2/3 · −V", "ps_m")], pw=100)
pins("PSU", "B", [(1060, "TB1-3 · FG", "ps_fg"), (1180, "CN100 · unused", "ps_cn")], ph=76)
photo("PSU", "PSU1", 110, 44, 290, 176)
note("PSU", "psu_n", 94, 224, 180, 100, "CN100 (DF11-04DP): 1 −S · 2 +S · 3 RC− · 4 RC+. Left open: RC open = "
     "output ON; remote sense optional (Mean Well RSP-500 spec).", fs=9)

device("PE", 720, 1930, 560, 120, "CHASSIS PE STUD", "protective-earth bonding point")
pins("PE", "T", [(1060, "PE stud", "pe_t")], ph=40)
pins("PE", "L", [(1990, "PE in ← J1", "pe_in")], pw=80)
pins("PE", "R", [(1990, "→ panels / doors / DIN rail", "pe_out")], pw=150)
note("PE", "pe_n", 110, 64, 210, 44, "W37 bonding plan pending (all exposed metal).", fs=9)

# ----------------------------------------------------------------------------- SYSCTRL
device("SYS", 1500, 300, 900, 1600, "SYSCTRL · HW_ADHERENT_SYSCTRL_R1",
       "custom STM32 machine controller ×1<br>R1 schematic started 2026-09-25 · connector nets incomplete", tag="PCB")
SYS_L = [
    (510, "12 V OUT + → MAINCTRL · F13", "sy_12m_p"), (532, "0 V → MAINCTRL", "sy_12m_n"),
    (680, "MARKER PWR · W39 (TBC)", "sy_mrk"),
    (800, "24 V OUT + → IOCTRL-01 · F17", "sy_io1_p"), (822, "0 V → IOCTRL-01", "sy_io1_n"),
    (864, "12 V OUT + → relay COM · F18", "sy_com"),
    (1290, "0 V ← latch returns (W35 0 V)", "sy_latn"),
    (1390, "24 V OUT + → IOCTRL-02 · W34", "sy_io2_p"), (1412, "0 V → IOCTRL-02", "sy_io2_n"),
    (1700, "J1 · +24 V IN (pin TBC)", "sy_j1p"), (1722, "J1 · 0 V IN (pin TBC)", "sy_j1n"),
]
pins("SYS", "L", SYS_L, pw=190)
pins("SYS", "T", [(2000, "CAN_H (conn. TBC)", "sy_ch"), (2022, "CAN_L (conn. TBC)", "sy_cl")], ph=96)
SYS_R = [
    (340, "+24 V → NFC (branch TBC)", "sy_nfc_p"), (362, "0 V → NFC", "sy_nfc_n"),
    (470, "J11/J13.1 · PUL+", "sy_d1"), (492, "J11/J13.2 · PUL−", "sy_d2"), (514, "J11/J13.3 · DIR+", "sy_d3"),
    (536, "J11/J13.4 · DIR−", "sy_d4"), (558, "J11/J13.5 · ENA+", "sy_d5"), (580, "J11/J13.6 · ENA−", "sy_d6"),
    (602, "J11/J13.7 · ALM_IN (4k7 pull-up)", "sy_d7"), (624, "J11/J13.8 · GND", "sy_d8"),
    (646, "DRIVE +24 V · F15 (X) / F16 (Z)", "sy_dp"), (668, "DRIVE 0 V", "sy_dn"),
    (702, "J11/J13.9 · +24V_MOT (brake +)", "sy_d9"), (724, "J11/J13.10 · BRK− (low side)", "sy_d10"),
    (845, "J15 · +V servo (pin TBC)", "sy_sv_p"), (867, "J15 · GND (pin TBC)", "sy_sv_n"),
    (889, "J15 · PWM (pin TBC)", "sy_sv_s"),
    (990, "J12.1 · BMA1", "sy_c1"), (1012, "J12.2 · BMA2", "sy_c2"), (1034, "J12.3 · BMB1", "sy_c3"),
    (1056, "J12.4 · BMB2", "sy_c4"),
    (1220, "J14.1 · OUT1A", "sy_j1"), (1242, "J14.2 · OUT2A", "sy_j2"), (1264, "J14.3 · OUT1B", "sy_j3"),
    (1286, "J14.4 · OUT2B", "sy_j4"),
    (1384, "SENS +V ×6 (conn. TBC)", "sy_g_p"), (1406, "SENS 0 V ×6", "sy_g_n"),
    (1428, "SENS IN · X1–X3 / Z1–Z3", "sy_g_s"),
    (1548, "JAW-SENS +V (TBC)", "sy_js_p"), (1570, "JAW-SENS 0 V (TBC)", "sy_js_n"), (1592, "JAW-SENS IN (TBC)", "sy_js_s"),
    (1690, "STACK +12 V (TBC)", "sy_st_p"), (1712, "STACK OUT 1 (TBC)", "sy_st_1"),
    (1734, "STACK OUT 2 (TBC)", "sy_st_2"), (1756, "STACK OUT 3 (TBC)", "sy_st_3"),
    (1830, "ROW FEED +24 V ×10 · branch F1…F10", "sy_row_p"), (1852, "ROW FEED 0 V (×10)", "sy_row_n"),
]
pins("SYS", "R", SYS_R, pw=200)
photo("SYS", "SYSCTRL", 250, 150, 400, 380, "board render: supplied example diagram (R1 layout in progress)")
note("SYS", "sys_n", 222, 556, 456, 330,
     "<b>What the R1 schematic already defines</b> (netlist export 2026-09-25 20:17):<br>"
     "• <b>Input</b> J1 Phoenix 1757242 (2-pos 5.08 mm); same sheet: LM74700 ideal-diode controller + 2 × CSD18540 + "
     "SMDJ33A TVS. Not yet on nets.<br>"
     "• <b>12 V</b> LM5146 buck, 24 V in → 12 V / 12 A (sheet title). Logic rails LMR33630 + TLV75733.<br>"
     "• <b>Fused outputs</b> F1–F7 4 A/72 V; by placement F1→J4, F2→J5, F3→J6, F5→J8 (5-pin), F6→J9 (5-pin), "
     "F7→J10, F4 without connector; J7 via TPS16637 eFuse. Nets not yet connected → the functional outputs on "
     "this box (F13, F15–F18, F1…F10, NFC, stack, marker) still have to be assigned to real connectors.<br>"
     "• <b>X / Z drive</b> J11 / J13 Micro-Fit 43045-1000 (10-pin): AM26C31 differential PUL / DIR / ENA, ALM input "
     "(4k7 pull-up), pin 9 = +24V_MOT, pin 10 = BRK− (DMN6140 low side). In the netlist only J11.7, J11.9, J13.9 "
     "and J13.10 reach circuitry (J11.8 is linked only to J13.8); the rest is open. J13 nets are named _Y although "
     "J13 drives Z → rename.<br>"
     "• <b>Chuck</b> J12 43045-0400 ← TMC5160 + BSC072N08 bridge (coil outputs).<br>"
     "• <b>Jaws</b> J14 43045-0400 ← TMC2240 (coil outputs).<br>"
     "• <b>Servo</b> J15 Molex 43650-0300 on sheet DRIVER4 with TPS54560 buck, INA181 current sense and "
     "74AHCT1G125 buffer (servo stage; pin map TBC).<br>"
     "• <b>CAN</b> SN65HVD232 + switchable 112 Ω termination (2 × 56 Ω in series through the CPC1014 contact, "
     "CAN_TERM) — no bus connector placed yet; keep it OFF (SYSCTRL is not a bus end).<br>"
     "• <b>Not yet in R1</b>: sensor inputs (R27: J21–J27 Micro-Fit 3-pin), stack-light outputs, ten row feeds.<br>"
     "• Service: J2 UART (SWR201), J3 SWD (FTSH-105).<br>"
     "F13 / F15–F18 / F1…F10 on the functional pins are R27 branch IDs, not R1 board fuses.", fs=10, color=C["INK"],
     box=True)

OUTS = [
    ("Row feeds LANECTRL-01…10", "24 V", "10", "W24", "6 fused headers + J7 eFuse exist; nets open"),
    ("X / Z driver supply", "24 V", "2", "W29 / W30", "not assigned"),
    ("IOCTRL-01 / -02 supply", "24 V", "1–2", "W34", "not assigned (R27: 1 feed)"),
    ("NFC reader supply", "24 V", "1", "TBC", "not assigned"),
    ("Marker supply", "TBC", "1", "W39", "marker not selected"),
    ("MAINCTRL", "12 V", "1", "W05", "not assigned"),
    ("Relay COM → latches", "12 V", "1", "W35", "not assigned"),
    ("Stack light", "12 V", "1", "W36", "no output circuit in R1"),
    ("Servo (own buck)", "4.8–6.8 V", "1", "W13", "J15 + TPS54560 exist"),
    ("X / Z brakes", "24 V", "2", "in W11 / W12", "J11 / J13 pin 9 +24V_MOT"),
]
tr = "".join(f"<tr><td style='border:1px solid #CFD8DC;padding:1px 4px'>{a}</td><td style='border:1px solid #CFD8DC;padding:1px 4px'>{b}</td>"
             f"<td style='border:1px solid #CFD8DC;padding:1px 4px;text-align:center'>{c}</td><td style='border:1px solid #CFD8DC;padding:1px 4px'>{d}</td>"
             f"<td style='border:1px solid #CFD8DC;padding:1px 4px'>{e}</td></tr>" for a, b, c, d, e in OUTS)
note("SYS", "sys_outs", 222, 900, 456, 300,
     "<b>Branch outputs the harness needs from SYSCTRL</b> (functional, from the cable list)"
     "<table style='border-collapse:collapse;width:100%;margin-top:4px;font-size:9px'>"
     "<tr style='background:#ECEFF1'><th style='border:1px solid #CFD8DC;text-align:left;padding:1px 4px'>Output</th>"
     "<th style='border:1px solid #CFD8DC;text-align:left;padding:1px 4px'>Rail</th><th style='border:1px solid #CFD8DC'>Qty</th>"
     "<th style='border:1px solid #CFD8DC;text-align:left;padding:1px 4px'>Cable</th>"
     "<th style='border:1px solid #CFD8DC;text-align:left;padding:1px 4px'>R1 status</th></tr>" + tr + "</table>"
     '<br><font color="#B71C1C"><b>⚠ About 18–19 protected branch outputs are needed; R1 has 7 output headers '
     "(J4–J10: six behind board fuses F1–F3 / F5–F7, one behind the J7 eFuse; F4 has no header) and their rails "
     "are not yet defined.</b></font> Options: more fused outputs on SYSCTRL, or a separate fused distribution for "
     "the ten row feeds. F-numbers in this table and on the pins are R27 branch IDs, not R1 board fuses.",
     fs=10, color=C["INK"], box=True)

# ----------------------------------------------------------------------------- FIELD COLUMN (right of SYSCTRL)
device("NFC", 2700, 190, 430, 210, "NFC · HW_ADHERENT_NFC_R1", "custom reader PCB<br>STM32F103C8 + ST25R200", tag="PCB")
pins("NFC", "T", [(3000, "J1.3 CAN1_P", "n_ch"), (3022, "J1.4 CAN1_N", "n_cl")], ph=70)
pins("NFC", "L", [(340, "J1.1 · +24V_VIN", "n_p"), (362, "J1.2 · GND", "n_n")], pw=100)
pins("NFC", "R", [(300, "J4.1 · ANT", "n_a1"), (322, "J4.2 · ANT", "n_a2")], pw=80)
photo("NFC", "NFC", 116, 84, 170, 118)
note("NFC", "nfc_n", 292, 150, 134, 58, "Switchable 112 Ω (CPC1014): OFF unless NFC is a bus end.", fs=8)

device("ANT", 3240, 190, 360, 210, "ANT-NFC · Molex 1462362151", "13.56 MHz · 15 × 15 mm · adhesive", tag="CONN")
pins("ANT", "L", [(300, "RED lead", "a_1"), (322, "BLACK lead", "a_2")], pw=74)
photo("ANT", "ANT", 96, 42, 60, 160)
note("ANT", "ant_n", 160, 44, 196, 160,
     "Lead 102 mm, twisted pair RED / BLACK 28 AWG. Plug Molex 505565-0201 (Micro-Lock Plus 1.25 mm) + 505431-1000 "
     "terminals (Molex drawing).", fs=9)

device("DRV", 2650, 410, 420, 340, "X / Z DRIVER ×2 (typical)", "Emtech closed-loop driver · supplied with the motor kit",
       tag="MTR")
pins("DRV", "L", [(470, "PUL+", "dv_1"), (492, "PUL−", "dv_2"), (514, "DIR+", "dv_3"), (536, "DIR−", "dv_4"),
                  (558, "ENA+", "dv_5"), (580, "ENA−", "dv_6"), (602, "ALM+ (TBC)", "dv_7"), (624, "ALM− (TBC)", "dv_8"),
                  (646, "+V DC (24 V proposed)", "dv_p"), (668, "GND", "dv_n")], pw=110)
pins("DRV", "R", [(470, "A+", "dv_ap"), (492, "A−", "dv_am"), (514, "B+", "dv_bp"), (536, "B−", "dv_bm"),
                  (580, "ENCODER · DB15", "dv_enc")], pw=100)
photo("DRV", "EMTECH_KIT", 124, 58, 170, 136)
note("DRV", "drv_n", 118, 206, 196, 128, "X = SYSCTRL J11, Z = J13. Terminal names per driver label (the listing "
     "gives none) — check before crimping. Listing: 48 V DC kit; BOM: 24 V proposed → confirm.", fs=9)

device("MOT", 3200, 410, 400, 340, "X / Z MOTOR ×2 (typical)", "Emtech 57BYG250-76 · closed loop · brake · encoder",
       tag="MTR")
pins("MOT", "L", [(470, "A+ · WHT", "mt_ap"), (492, "A− · GRN", "mt_am"), (514, "B+ · BLU", "mt_bp"),
                  (536, "B− · BLK", "mt_bm"), (580, "ENC · DB15 plug", "mt_enc"),
                  (690, "BRAKE + (colour TBC)", "mt_bk_p"), (712, "BRAKE − (colour TBC)", "mt_bk_n")], pw=120)
photo("MOT", "EMTECH_MOTOR", 150, 56, 240, 100)
note("MOT", "mot_n", 150, 160, 244, 176,
     "Emtech listing: motor lead A+ WHT · A− GRN · B+ BLU · B− BLK (2.0 m). Encoder: 0.3 m lead on the motor + "
     "1.7 m extension, DB15: WHT 0 V · RED +5 V · YEL EB+ · GRN EB− · BLU EA− · BLK EA+. Brake: 2 leads, voltage "
     "and colours TBC (fed from SYSCTRL J11/J13 pins 9–10, not from the driver).", fs=9)

device("SRV", 2650, 785, 420, 134, "SERVO · Miuzei DS3218", "basket tilt · 20 kg · DC 4.8–6.8 V", tag="MTR")
pins("SRV", "L", [(845, "RED · +V 4.8–6.8 V", "sv_p"), (867, "BLACK · GND", "sv_n"), (889, "WHITE · PWM", "sv_s")],
     pw=120)
photo("SRV", "SERVO", 134, 44, 110, 84)
note("SRV", "srv_n", 250, 44, 166, 84, "Lead colours as pictured on the supplier listing. Set the SYSCTRL servo buck "
     "(TPS54560) inside 4.8–6.8 V.", fs=8)

device("CHK", 2650, 930, 950, 222, "CHUCK · McMaster 6627T113", "= Anaheim 23MSD006S-00-00-00 · NEMA 23 "
       "integrated step driver · sinking inputs", tag="MTR")
pins("CHK", "L", [(990, "1 · DIR · BRN", "ck1"), (1012, "2 · CLK · RED", "ck2"), (1034, "3 · ON/OFF · ORN", "ck3"),
                  (1056, "4 · MS2 · YEL", "ck4"), (1078, "5 · MS1 · GRN", "ck5"),
                  (1100, "6 · +12–24 VDC · BLU", "ck6"), (1122, "7 · 0 VDC · VIO", "ck7")], pw=130)
photo("CHK", "CHUCK", 144, 52, 150, 150)
note("CHK", "chk_n", 300, 48, 250, 164, "7-pin input: AMP 640440-7 (CBL-AA4031, 12 in leads). Open input = "
     "inactive (pulled up to +5 V inside); active = pulled to 0 V. MS1/MS2 select 2 / 8 / 64 / 256 microsteps. "
     "Source: Anaheim 23MSD manual (McMaster 6627T113).", fs=9)
note("CHK", "chk_w", 560, 48, 384, 118,
     "⚠ <b>W16 blocked.</b> SYSCTRL J12 carries TMC5160 coil outputs (BMA1/BMA2/BMB1/BMB2). 6627T113 has its own "
     "driver and needs CLK/DIR/ON-OFF/MS1/MS2 logic + 12–24 V supply — a 4-wire phase cable cannot work.<br>"
     "Decide one: (a) change CHUCK to a plain bipolar NEMA 23 motor on J12, or (b) keep 6627T113 and give SYSCTRL "
     "open-drain CLK/DIR/ON-OFF outputs + a fused 24 V pair on a 7-way connector.", fs=9, warn=True)

device("JAW", 2650, 1160, 420, 156, "JAWS · McMaster 6627T357", "NEMA 11 bipolar · 0.67 A/phase · 5.6 Ω · 3.08 mH",
       tag="MTR")
pins("JAW", "L", [(1220, "RED · A+", "jw1"), (1242, "BLUE · A−", "jw2"), (1264, "GREEN · B+", "jw3"),
                  (1286, "BLACK · B−", "jw4")], pw=100)
photo("JAW", "JAWS", 114, 48, 110, 84)
note("JAW", "jaw_n", 228, 44, 188, 104, "4 leads 26 AWG, 24 in. Colour code per the McMaster 4-lead diagram "
     "(A = red, Ā = blue, B = green, B̄ = black). Set TMC2240 run current ≤ 0.67 A.", fs=8)

device("GS", 2650, 1324, 420, 156, "X-SENS ×3 / Z-SENS ×3 (typical ×6)", "Omron EE-SX672-WR (X) · EE-SX674-WR (Z)",
       tag="SENS")
pins("GS", "L", [(1384, "BRN · +V 5–24 V", "gs_p"), (1406, "BLU · 0 V", "gs_n"), (1428, "BLK · OUT (NPN OC)", "gs_s"),
                 (1450, "PNK · L (mode)", "gs_l")], pw=110)
photo("GS", "OMRON", 122, 48, 90, 76)
note("GS", "gs_n2", 216, 44, 200, 108, "1 m pre-wired leads. OUT 100 mA max. PNK (L) open = dark-ON; PNK to BRN = "
     "light-ON (Omron datasheet). The SYSCTRL input is 3-wire → terminate PNK in the harness for the chosen mode.",
     fs=8)

device("JS", 2650, 1488, 420, 134, "JAW-SENS · jaw home sensor", "part TBC · W18", tag="TBC")
pins("JS", "L", [(1548, "+V (TBC)", "js_p"), (1570, "0 V (TBC)", "js_n"), (1592, "OUT (TBC)", "js_s")], pw=90)
note("JS", "js_n2", 104, 48, 310, 70, "Sensor not selected — lead colours and supply follow the chosen part.", fs=9)

device("ST", 2650, 1630, 420, 156, "STACK · 12 V status light", "part, lamp count and common TBC · W36", tag="TBC")
pins("ST", "L", [(1690, "+12 V (TBC)", "st_p"), (1712, "LAMP 1 (TBC)", "st_1"), (1734, "LAMP 2 (TBC)", "st_2"),
                 (1756, "LAMP 3 (TBC)", "st_3")], pw=100)
note("ST", "st_n2", 114, 48, 300, 90, "No stack-light output exists on SYSCTRL R1 yet (R27: J44, HOLD O15).", fs=9)

# ----------------------------------------------------------------------------- LANE AREA
device("LC", 3700, 640, 600, 620, "LANECTRL ×10 (typical)",
       "HW_ADHERENT_LANECTRL_R1 · STM32G0B1<br>2 × TPS4H160 high-side (on/off) · 7 lanes per board", tag="PCB")
pins("LC", "T", [(4170, "J8.3", "lc_ch"), (4192, "J8.4", "lc_cl")], ph=40)
pins("LC", "L", [(720, "J8.1 · +24V_VIN", "lc_p"), (742, "J8.2 · GND", "lc_n")], pw=104)
pins("LC", "R", [(700, "J1.1 · LANE_OUT1", "lc_o1"), (722, "J1.2 · GND", "lc_g1"), (744, "J1.3 · SIG1", "lc_s1"),
                 (800, "J2…J7 .1 · LANE_OUTn", "lc_on"), (822, "J2…J7 .2 · GND", "lc_gn"),
                 (844, "J2…J7 .3 · SIGn", "lc_sn"),
                 (910, "LEDSn.1 · + (via 100 Ω)", "lc_lp"), (932, "LEDSn.2 · − (GND)", "lc_ln")], pw=150)
photo("LC", "LANECTRL", 120, 110, 300, 52, "board render: supplied example diagram")
note("LC", "lc_note", 116, 190, 322, 420,
     "J8 Micro-Fit 43045-0400 (dual row): 1 +24V_VIN · 2 GND · 3 CAN_H · 4 CAN_L — the only power + bus "
     "connector.<br>J1–J7 Micro-Fit 43650-0300: 1 LANE_OUTn (switched +24 V) · 2 GND · 3 SIGn (feedback: +24 V "
     "through the conveyor plate switch, valid only while the lane is on).<br>LEDS1–7: 2-pin 2.54 mm headers for the "
     "off-board lane LEDs (pin 1 via 100 Ω, pin 2 GND).<br>S1 DIP = CAN node ID · P1 jumper = "
     "120 Ω (fit on LANECTRL-01 only) · J9 SWD · J10 USB-C.<br><br>"
     '<font color="#B71C1C">⚠ Board R1: +24V_PR (after M1) is not joined to VM (driver / buck rail) in schematic '
     "and PCB — nothing downstream is powered until fixed. Harness tests will fail on R1 as drawn.</font><br><br>"
     '<font color="#B71C1C">⚠ Single J8: the CAN pair must enter and leave through pins 3 / 4. Micro-Fit takes '
     "one wire per crimp → splice the in / out pairs to one short tail per pin (keep the stub short), or add a "
     "second bus connector in R2.</font>", fs=10, color=C["INK"])

device("CV1", 4420, 620, 460, 160, "CONVEYOR (lane 1 of 7)", "CB002-24V-573mm · ×70 total", tag="MTR")
pins("CV1", "L", [(700, "1 · +24 V", "cv_1"), (722, "2 · GND", "cv_2"), (744, "3 · SIGNAL", "cv_3")], pw=84)
photo("CV1", "CONVEYOR", 96, 44, 184, 92)
note("CV1", "cv_n", 284, 36, 172, 122, "JST VH3.96 3-pin (VHR-3N + SVH-21T-P1.1). 0.19 A run / ≈0.5 A stall (bench). "
     "⚠ The supplier schematic numbers the pins in reverse (3 = +) → meter-check one conveyor first.", fs=8)
device("CVN", 4420, 790, 460, 76, "CONVEYOR lanes 2…7", "same pin-to-pin as lane 1 (J2…J7)", tag="MTR", tx=100)
pins("CVN", "L", [(800, "1 · +24 V", "cvn_1"), (822, "2 · GND", "cvn_2"), (844, "3 · SIGNAL", "cvn_3")], pw=84)
device("LED", 4420, 880, 460, 76, "LANE LED ×7 per row", "off-board · part TBC · behind the bracket", tag="TBC", tx=100)
pins("LED", "L", [(910, "+ anode", "led_p"), (932, "− cathode", "led_n")], pw=84)

# ----------------------------------------------------------------------------- CAN BUS (step 4)
BUS_X0, BUS_X1 = 990, 4230
P.v("canH", BUS_X0, 145, BUS_X1 - BUS_X0, 10, "",
    f"shape=line;html=1;strokeWidth=3;strokeColor={C['CAN']};connectable=1;", "L4")
P.v("canL", BUS_X0, 167, BUS_X1 - BUS_X0, 10, "",
    f"shape=line;html=1;strokeWidth=3;strokeColor={C['CAN']};dashed=1;dashPattern=6 3;connectable=1;", "L4")
P.v(P.uid("t"), 930, 138, 56, 46, "120 Ω<br><font style=\"font-size:8px\">MAINCTRL end</font>",
    f"rounded=0;html=1;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor={C['CAN']};strokeWidth=1.5;fontSize=10;"
    f"fontStyle=1;fontColor={C['CAN']};connectable=0;{F}", "L4")
note("L4", "can_lbl", 1060, 116, 620, 26,
     f'<font color="{C["CAN"]}"><b>CAN_H ━━ / CAN_L ╍╍ · 500 kbit/s · twisted pair + 0 V reference</b></font>', fs=10)
note("L4", "can_end", 4240, 128, 640, 56,
     f'<font color="{C["CAN"]}"><b>→ row chain LANECTRL-10 … -01 (W25 / W26, see inset)</b><br>'
     "120 Ω at LANECTRL-01 (P1). NFC position on the bus TBC.</font>", fs=10)


def drop(layer, pid, bus, x, tbc=False):
    bx = P.geo[bus][0]
    rel = round((x - bx) / (BUS_X1 - BUS_X0), 5)
    dash = "dashed=1;dashPattern=2 3;" if tbc else ("dashed=1;dashPattern=6 3;" if bus == "canL" else "")
    st = (f"edgeStyle=none;rounded=0;html=1;endArrow=oval;endFill=1;endSize=5;startArrow=none;jumpStyle=arc;"
          f"jumpSize=6;strokeColor={C['CAN']};strokeWidth=1.8;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX={rel};"
          f"entryY=0.5;entryDx=0;entryDy=0;entryPerimeter=0;{dash}")
    P.e(P.uid("d"), pid, bus, "", st, layer)


for pid, bus, x in [("m_ch", "canH", 1020), ("m_cl", "canL", 1042), ("sy_ch", "canH", 2000), ("sy_cl", "canL", 2022),
                    ("lc_ch", "canH", 4170), ("lc_cl", "canL", 4192)]:
    drop("L4", pid, bus, x)
drop("L4", "n_ch", "canH", 3000, tbc=True)
drop("L4", "n_cl", "canL", 3022, tbc=True)
pill("L4", 2040, 244, "④ W08 · MAINCTRL ↔ SYSCTRL · 0.4 m", C["CAN"])
pill("L4", 4204, 480, "④ W25 / W26 → J8.3 / J8.4", C["CAN"], w=184)
pill("L4", 3040, 94, "④ NFC tap · W-ID TBC", C["TBC"], w=150)

# ----------------------------------------------------------------------------- STEP 1 · AC / PE
wire("L1", "ac_l", "j1_li", "L", C["L"], 2.5)
wire("L1", "ac_n", "j1_ni", "N", C["N"], 2.5)
wire("L1", "ac_pe", "j1_pei", "PE", C["PE"], 2.5)
wire("L1", "j1_lo", "ps_l", "L", C["L"], 2.5)
wire("L1", "j1_no", "ps_n", "N", C["N"], 2.5)
wire("L1", "j1_peo", "pe_in", "PE", C["PE"], 2.5, pts=[(676, 1760), (676, 1990)])
wire("L1", "pe_t", "ps_fg", "PE → FG", C["PE"], 2.5, sx=(0.5, 0), tx=(0.5, 1))
P.v("pe_tail", 1284, 1981, 60, 18, "W37", f"text;html=1;fontSize=10;fontStyle=1;fontColor={C['PE']};{F}"
    "strokeColor=none;fillColor=none;align=left;verticalAlign=middle;connectable=0;", "L1")
pill("L1", 634, 1604, "① W01", C["L"], w=62)
pill("L1", 60, 1770, "① site cord · IEC C13", C["L"], w=140)
pill("L1", 684, 1900, "① W37", C["PE"], w=62)

# ----------------------------------------------------------------------------- STEP 2 · 24 V feed
wire("L2", "ps_p", "sy_j1p", "+24 V", C["P24"], 3)
wire("L2", "ps_m", "sy_j1n", "0 V", C["GND"], 3)
pill("L2", 1300, 1666, "② W03 · 24 V main · 0.5 m", C["P24"], w=176)

# ----------------------------------------------------------------------------- STEP 3 · DC branches
wire("L3", "sy_12m_p", "m_12p", "+12 V", C["P12"], 2.5, sx=(0, 0.5), tx=(1, 0.5))
wire("L3", "sy_12m_n", "m_12n", "0 V", C["GND"], 2, sx=(0, 0.5), tx=(1, 0.5))
pill("L3", 1296, 478, "③ W05 · 12 V · 0.5 m", C["P12"], w=150)
wire("L3", "sy_io1_p", "i1_pp", "+24 V", C["P24"], 2.5, sx=(0, 0.5), tx=(1, 0.5))
wire("L3", "sy_io1_n", "i1_pn", "0 V", C["GND"], 2, sx=(0, 0.5), tx=(1, 0.5))
wire("L3", "sy_com", "i1_com", "+12 V COM", C["P12"], 2.5, sx=(0, 0.5), tx=(1, 0.5))
pill("L3", 1296, 766, "③ W34 · 24 V", C["P24"], w=100)
pill("L3", 1296, 876, "③ W35 · 12 V pair", C["P12"], w=124)
note("L3", "w35_t", 1292, 898, 200, 44, "+12 V → RO1–RO4 COM · 0 V → latch returns K1–K4 (R27 register)", fs=9,
     color=C["P12"])
wire("L3", "sy_io2_p", "i2_pp", "+24 V", C["P24"], 2.5, sx=(0, 0.5), tx=(1, 0.5))
wire("L3", "sy_io2_n", "i2_pn", "0 V", C["GND"], 2, sx=(0, 0.5), tx=(1, 0.5))
pill("L3", 1296, 1356, "③ W34 (module 2)", C["P24"], w=128)
wire("L3", "sy_dp", "dv_p", "+24 V · ③ W29 X / W30 Z", C["P24"], 2.5)
wire("L3", "sy_dn", "dv_n", "0 V", C["GND"], 2)
wire("L3", "sy_nfc_p", "n_p", "+24 V (TBC)", C["P24"], 2, dash="tbc")
wire("L3", "sy_nfc_n", "n_n", "0 V (TBC)", C["GND"], 1.6, dash="tbc")
pill("L3", 2420, 306, "③ NFC feed · W-ID / fuse TBC", C["TBC"], w=190)

# ----------------------------------------------------------------------------- STEP 5 · Ethernet / RS485
wire("L5", "site_rj", "j2_ext", "", C["ETH"], 3)
wire("L5", "j2_int", "m_eth", "", C["ETH"], 3)
pill("L5", 60, 406, "⑤ W38 · site patch (site-supplied)", C["ETH"], w=210)
pill("L5", 588, 294, "⑤ W09", C["ETH"], w=58)
note("L5", "w09_t", 586, 330, 130, 40, "Cat5e/6 shielded patch · 0.5 m", fs=9, color=C["ETH"])
for a, b, lab, dsh in [("m_ra", "i1_ta", "A", None), ("m_rb", "i1_tb", "B", "d"), ("m_rg", "i1_tg", "", None)]:
    wire("L5", a, b, lab, C["RS"] if lab else C["GND"], 1.8, dash=dsh, sx=(0.5, 1), tx=(0.5, 0))
for a, b, lab, dsh in [("i1_ba", "i2_ta", "A", None), ("i1_bb", "i2_tb", "B", "d"), ("i1_bg", "i2_tg", "", None)]:
    wire("L5", a, b, lab, C["RS"] if lab else C["GND"], 1.8, dash=dsh, sx=(0.5, 1), tx=(0.5, 0))
pill("L5", 1152, 700, "⑤ W33 · RS485 · 1.5 m", C["RS"], w=150)
pill("L5", 1152, 1300, "⑤ W33 ext. · daisy-chain", C["RS"], w=160)

# ----------------------------------------------------------------------------- STEP 6 · X / Z drives
ctl = [("sy_d1", "dv_1", "PUL+", None), ("sy_d2", "dv_2", "PUL−", "d"), ("sy_d3", "dv_3", "DIR+", None),
       ("sy_d4", "dv_4", "DIR−", "d"), ("sy_d5", "dv_5", "ENA+", None), ("sy_d6", "dv_6", "ENA−", "d")]
for a, b, lab, dsh in ctl:
    wire("L6", a, b, lab, C["CTL"], 1.6, dash=dsh)
wire("L6", "sy_d7", "dv_7", "ALM", C["FB"], 1.6)
wire("L6", "sy_d8", "dv_8", "GND", C["GND"], 1.4)
wire("L6", "sy_d9", "mt_bk_p", "+24V_MOT · brake (in W11 / W12)", C["P24"], 1.8,
     pts=[(2615, 702), (2615, 758), (3150, 758), (3150, 690)], lx=0.05)
wire("L6", "sy_d10", "mt_bk_n", "", C["GND"], 1.6, pts=[(2600, 724), (2600, 771), (3165, 771), (3165, 712)])
pill("L6", 2410, 436, "⑥ W11 X 1.2 m / W12 Z 2.2 m · 10 cond.", C["CTL"], w=236)
for a, b, lab, col, dsh in [("dv_ap", "mt_ap", "A+", C["MA"], None), ("dv_am", "mt_am", "A−", C["MA"], "d"),
                            ("dv_bp", "mt_bp", "B+", C["MB"], None), ("dv_bm", "mt_bm", "B−", C["MB"], "d")]:
    wire("L6", a, b, lab, col, 2, dash=dsh)
wire("L6", "dv_enc", "mt_enc", "", C["ETH"], 3)
pill("L6", 3082, 598, "⑥ kit cables", C["ETH"], w=92)

# ----------------------------------------------------------------------------- STEP 7 · labeling motors & servo
wire("L7", "sy_sv_p", "sv_p", "+V servo", C["P12"], 2)
wire("L7", "sy_sv_n", "sv_n", "GND", C["GND"], 1.6)
wire("L7", "sy_sv_s", "sv_s", "PWM", C["CTL"], 1.6)
pill("L7", 2410, 814, "⑦ W13 · servo · 3.8 m", C["CTL"], w=130)
for a, b, lab, col, dsh in [("sy_j1", "jw1", "A+", C["MA"], None), ("sy_j2", "jw2", "A−", C["MA"], "d"),
                            ("sy_j3", "jw3", "B+", C["MB"], None), ("sy_j4", "jw4", "B−", C["MB"], "d")]:
    wire("L7", a, b, lab, col, 2, dash=dsh)
pill("L7", 2410, 1188, "⑦ W17 · jaws · 1.5 m", C["MA"], w=130)
note("L7", "w16_block", 2410, 984, 230, 80,
     "⚠ <b>W16 not drawn</b> — J12 (coil outputs) ≠ 6627T113 input (logic + 12–24 V). See CHUCK.", fs=9, warn=True)

# ----------------------------------------------------------------------------- STEP 8 · sensors
wire("L8", "sy_g_p", "gs_p", "+V", C["P24"], 1.8)
wire("L8", "sy_g_n", "gs_n", "0 V", C["GND"], 1.6)
wire("L8", "sy_g_s", "gs_s", "OUT → IN", C["FB"], 1.6)
pill("L8", 2410, 1352, "⑧ W15 ×6 · length TBC (1 m leads)", C["FB"], w=210)
wire("L8", "sy_js_p", "js_p", "+V", C["P24"], 1.6, dash="tbc")
wire("L8", "sy_js_n", "js_n", "0 V", C["GND"], 1.4, dash="tbc")
wire("L8", "sy_js_s", "js_s", "IN", C["FB"], 1.4, dash="tbc")
pill("L8", 2410, 1516, "⑧ W18 · 1.5 m (TBC)", C["TBC"], w=128)

# ----------------------------------------------------------------------------- STEP 9 · doors & latches
for a, b, lab in [("i1_r1", "k1", "K1 +"), ("i1_r2", "k2", "K2 +"), ("i1_r3", "k3", "K3 +"), ("i1_r4", "k4", "K4 +")]:
    wire("L9", a, b, lab, C["P12"], 2, sx=(0, 0.5), tx=(1, 0.5))
wire("L9", "kn", "sy_latn", "0 V return (K1–K4)", C["GND"], 2, pts=[(690, 888), (690, 1290)], lx=0.0)
pill("L9", 440, 736, "⑨ W20 K1/K2 · W21 K3/K4", C["P12"], w=170)
for a, b, lab in [("i1_d1", "s1", "DI1"), ("i1_d2", "s2", "DI2"), ("i1_d3", "s3", "DI3"), ("i1_d4", "s4", "DI4"),
                  ("i1_d5", "s5", "DI5"), ("i1_dc", "sc", "COM")]:
    wire("L9", a, b, lab, C["FB"], 1.6, sx=(0, 0.5), tx=(1, 0.5))
pill("L9", 440, 1146, "⑨ W23 ×5 · direct", C["FB"], w=120)

# ----------------------------------------------------------------------------- STEP 10 · lane rows
wire("L10", "sy_row_p", "lc_p", "+24 V", C["P24"], 2.5, pts=[(3650, 1830), (3650, 720)], lx=-0.6)
wire("L10", "sy_row_n", "lc_n", "0 V", C["GND"], 2, pts=[(3635, 1852), (3635, 742)], lx=-0.6)
pill("L10", 2420, 1796, "⑩ W24 ×10 · one fused pair per row · 2.4 m", C["P24"], w=250)
for a, b, lab, col in [("lc_o1", "cv_1", "+24 V", C["P24"]), ("lc_g1", "cv_2", "GND", C["GND"]),
                       ("lc_s1", "cv_3", "SIG", C["FB"])]:
    wire("L10", a, b, lab, col, 1.8)
for a, b, lab, col in [("lc_on", "cvn_1", "+24 V", C["P24"]), ("lc_gn", "cvn_2", "GND", C["GND"]),
                       ("lc_sn", "cvn_3", "SIG", C["FB"])]:
    wire("L10", a, b, lab, col, 1.8)
wire("L10", "lc_lp", "led_p", "+", C["P24"], 1.4)
wire("L10", "lc_ln", "led_n", "−", C["GND"], 1.4)
pill("L10", 4306, 668, "⑩ W27 ×70", C["FB"], w=80)
note("L10", "w27_t", 4302, 760, 118, 30, "0.8 m each", fs=9, color=C["FB"])
pill("L10", 4306, 878, "⑩ LED ×70", C["P24"], w=74)

# chain inset (step 10)
P.v("chain", 3700, 1300, 1180, 370,
    "<b>ROW CHAIN · J8 on each LANECTRL (1 +24 V · 2 GND · 3 CAN_H · 4 CAN_L)</b>",
    "rounded=0;html=1;whiteSpace=wrap;fillColor=#FAFAFA;strokeColor=#B0BEC5;verticalAlign=top;align=left;"
    f"spacingLeft=8;spacingTop=4;fontSize=12;fontColor={C['INK']};{F}container=1;collapsible=0;", "L10")
bx0 = 60
for k in range(10):
    n = 10 - k
    x = bx0 + k * 108
    P.v(f"ch_lc{n}", x, 120, 92, 96,
        f"<b>LC-{n:02d}</b><br>J8<br>node ID {n}<br>{'P1 ON' if n == 1 else 'P1 off'}",
        f"rounded=0;html=1;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor={C['INK']};fontSize=10;{F}"
        + ("strokeWidth=2.5;" if n == 1 else ""), "chain")
    P.v(f"ch_f{n}", x + 6, 250, 80, 22, f"W24-{n:02d} · br. F{n}",
        f"rounded=1;arcSize=40;html=1;fillColor=#FFFFFF;strokeColor={C['P24']};fontColor={C['P24']};fontSize=9;"
        f"fontStyle=1;{F}", "chain")
    P.e(P.uid("cf"), f"ch_f{n}", f"ch_lc{n}", "",
        f"edgeStyle=none;html=1;endArrow=none;strokeColor={C['P24']};strokeWidth=2;exitX=0.5;exitY=0;entryX=0.5;"
        "entryY=1;", "L10")
    if k < 9:
        P.e(P.uid("cc"), f"ch_lc{n}", f"ch_lc{n - 1}", "W26",
            f"edgeStyle=none;html=1;endArrow=none;strokeColor={C['CAN']};strokeWidth=2.5;fontSize=9;fontColor={C['CAN']};"
            f"labelBackgroundColor=#FAFAFA;exitX=1;exitY=0.35;entryX=0;entryY=0.35;{F}", "L10")
P.v("ch_sys", 60, 50, 330, 22, "from SYSCTRL CAN · W25 · 1.8 m → LC-10",
    f"text;html=1;fontSize=10;fontColor={C['CAN']};fontStyle=1;{F}strokeColor=none;fillColor=none;align=left;",
    "chain")
P.e(P.uid("cs"), "ch_sys", "ch_lc10", "",
    f"edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;endFill=1;strokeColor={C['CAN']};strokeWidth=2.5;"
    "exitX=0.1;exitY=1;entryX=0.3;entryY=0;", "L10")
P.v("ch_end", 1146, 150, 28, 30, "120 Ω",
    f"text;html=1;fontSize=9;fontColor={C['CAN']};fontStyle=1;{F}strokeColor=none;fillColor=none;align=left;"
    "horizontal=0;", "chain")
note("chain", "ch_txt", 10, 282, 1160, 84,
     "• Physical CAN order MAINCTRL → SYSCTRL → LC-10 → … → LC-01 (end, P1 = 120 Ω). All other LANECTRL: P1 off. "
     "W26 ×9 short links (0.3 m each, R27 estimate).<br>"
     "• Each LC-nn also gets its own fused 24 V pair W24-nn from SYSCTRL (R27 branch IDs F1…F10) — ten separate "
     "pairs, not a shared bus. <font color=\"#B71C1C\">⚠ SYSCTRL R1 has six fused headers (board fuses F1–F3, F5–F7, "
     "4 A) + one eFuse header (J7): ten row feeds are not yet provided.</font><br>"
     "• At every J8 plug the incoming and outgoing CAN pairs share pins 3 / 4 (see ⚠ on the LANECTRL box). "
     "Label each plug with its row number; set S1 node ID = row number.", fs=10, color=C["INK"])

# ----------------------------------------------------------------------------- STEP 11 · TBC items
wire("L11", "mrk_d", "m_mrk", "", C["ETH"], 1.8, dash="tbc")
wire("L11", "mrk_p", "sy_mrk", "PWR (TBC)", C["P24"], 1.8, dash="tbc", pts=[(668, 590), (668, 680)], lx=0.1)
pill("L11", 646, 516, "⑪ W19", C["TBC"], w=56)
pill("L11", 1320, 648, "⑪ W39 (TBC)", C["TBC"], w=96)
for a, b, lab, col in [("sy_st_p", "st_p", "+12 V", C["P12"]), ("sy_st_1", "st_1", "L1", C["CTL"]),
                       ("sy_st_2", "st_2", "L2", C["CTL"]), ("sy_st_3", "st_3", "L3", C["CTL"])]:
    wire("L11", a, b, lab, col, 1.6, dash="tbc")
pill("L11", 2410, 1656, "⑪ W36 · stack light (TBC)", C["TBC"], w=166)

# NFC ↔ antenna (placed with step 4, reader node)
wire("L4", "n_a1", "a_1", "", C["RF"], 1.8, dash="d")
wire("L4", "n_a2", "a_2", "", C["RF"], 1.8, dash="d")
note("L4", "ant_w", 3136, 226, 100, 62, "⚠ antenna plug does not fit J4", fs=9, warn=True)

# ----------------------------------------------------------------------------- LEGEND + ISSUES
P.v("leg", 3700, 1700, 1180, 300, "<b>LEGEND</b>",
    f"rounded=0;html=1;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor=#BDBDBD;verticalAlign=top;align=left;"
    f"spacingLeft=8;spacingTop=4;fontSize=12;fontColor={C['INK']};{F}container=1;collapsible=0;", "LN")
LEG = [
    (C["L"], 2.5, None, "AC L"), (C["N"], 2.5, None, "AC N"), (C["PE"], 2.5, None, "PE (green / yellow)"),
    (C["P24"], 2.5, None, "+24 V"), (C["P12"], 2.5, None, "+12 V (derived on SYSCTRL)"), (C["GND"], 2, None, "0 V / GND"),
    (C["CAN"], 3, None, "CAN_H"), (C["CAN"], 3, "d", "CAN_L"), (C["RS"], 2, None, "RS485 A"),
    (C["RS"], 2, "d", "RS485 B"), (C["ETH"], 3, None, "Ethernet / supplied cable"),
    (C["CTL"], 1.8, None, "control out: + / PWM"), (C["CTL"], 1.8, "d", "control out: − (diff. pair)"),
    (C["FB"], 1.8, None, "feedback / sensor / lane signal"), (C["MA"], 2, None, "motor phase A+ (A− dashed)"),
    (C["MB"], 2, None, "motor phase B+ (B− dashed)"), (C["RF"], 1.8, "d", "NFC antenna lead"),
    (C["TBC"], 1.8, "tbc", "dotted = TBC (not in design files yet)"),
]
for i, (col, wdt, dsh, lab) in enumerate(LEG):
    cx = 20 + (i % 3) * 390
    cy = 40 + (i // 3) * 30
    d = "dashed=1;dashPattern=6 3;" if dsh == "d" else ("dashed=1;dashPattern=2 3;" if dsh == "tbc" else "")
    P.free_line(P.uid("lg"), 3700 + cx, 1700 + cy + 9, 3700 + cx + 60, 1700 + cy + 9,
                f"endArrow=none;html=1;strokeColor={col};strokeWidth={wdt};{d}", "LN")
    note("leg", P.uid("lt"), cx + 68, cy, 310, 20, lab, fs=10, color=C["INK"])
note("leg", "leg_t", 16, 222, 1150, 72,
     "Pin box: <b>J11/J13.3 · DIR+</b> = connector J11 (X) or J13 (Z), pin 3, signal DIR+ · device side: <b>lead colour · "
     "function</b>. Pill: <b>④ W08</b> = build step ④, cable W08. Red tag before a title = category (CONN · PCB · MTR). "
     "Lengths are R27 register estimates, not measured routes. Cable convention: 4-core 22 AWG red / black / yellow / "
     "green where electrically suitable; mains and power pairs sized per fuse / load (not yet specified).", fs=10, color=C["INK"])

ISS = [
    "<b>SYSCTRL R1 is an early draft</b>: J1, J4–J10, J15 have no nets; J11 / J13 mostly open (only J11.7, J11.9, "
    "J13.9, J13.10 connected); no CAN, sensor, stack-light or row-feed connectors yet. Pin labels on the SYSCTRL box "
    "are functional placeholders.",
    "<b>Row feeds</b>: 10 × fused 24 V (R27 branches F1…F10, W24) needed; R1 has six fused headers (board fuses F1–F3, "
    "F5–F7, 4 A) + one eFuse header. Row fuse vs. 7 lanes × stall current is still open (R27 O03 / O04).",
    "<b>CHUCK</b> 6627T113 is an integrated driver (logic + 12–24 V); SYSCTRL J12 gives coil outputs → W16 blocked.",
    "<b>NFC J4</b> Würth 61300211821 (2.54 mm pins) does not mate with the antenna plug Molex 505565-0201 "
    "(Micro-Lock Plus 1.25 mm).",
    "<b>LANECTRL J8</b> single 4-pin plug: CAN in + out share pins 3 / 4 → splice rule or second connector. "
    "Board R1: +24V_PR / VM not joined.",
    "<b>Gantry sensors</b> have 4 leads (PNK = L mode) → terminate PNK in the harness if the input stays 3-wire.",
    "<b>X / Z kit</b>: the listing is 48 V DC; the BOM proposes 24 V → confirm with Emtech. Brake voltage / lead colours TBC.",
    "<b>Servo</b> DS3218 needs 4.8–6.8 V → set the SYSCTRL servo buck accordingly; J15 pin map TBC.",
    "<b>Conveyor</b> VH3.96: datasheet 1 = +24 V / 3 = SIGNAL, supplier schematic reversed → meter-check before series "
    "crimping.",
    "<b>J13</b> nets are named _Y but drive Z → rename. <b>Terminations</b>: CAN 120 Ω only at the MAINCTRL end (check "
    "the MYIR board) and LANECTRL-01; SYSCTRL / NFC CPC1014 off; RS485 120 Ω jumper at the last IOCTRL (NC by default).",
    "<b>Not selected yet</b>: latches K1–K4, door sensors, jaw sensor, stack light, marker, J1 breaker / fuse, wire "
    "gauges, MAINCTRL plug / CAN / RS485 pinout (MYIR manual).",
    "<b>SYSCTRL branch outputs</b>: about 18–19 protected outputs are needed (table on the SYSCTRL box); R1 has 7 "
    "output headers (6 fused + 1 eFuse) with undefined rails. F-numbers on the SYSCTRL box are R27 branch IDs, not R1 "
    "board fuse designators.",
    "<b>J1 rating</b>: FN9264-6 is a 6 A part; RSP-500 AC input is up to 5.3 A (typ.) at 115 VAC → little margin at "
    "120 V sites (the -10 variant gives headroom). Check SYSCTRL J1 (Phoenix 1757242) current rating against the 24 V load.",
]
half = (len(ISS) + 1) // 2
col1 = "".join(f"<li>{t}</li>" for t in ISS[:half])
col2 = "".join(f"<li value='{half + 1 + i}'>{t}</li>" for i, t in enumerate(ISS[half:]))
iss_html = ("<b>⚠ OPEN ISSUES FOUND WHILE DERIVING THE HARNESS</b> (resolve before building the affected step)"
            "<table style='width:100%;border-collapse:collapse'><tr>"
            f"<td style='vertical-align:top;width:50%'><ol style='margin:4px 0 0 0;padding-left:22px'>{col1}</ol></td>"
            f"<td style='vertical-align:top;width:50%'><ol style='margin:4px 0 0 0;padding-left:26px'>{col2}</ol></td>"
            "</tr></table>")
note("LN", "issues", 40, 2090, 3600, 220, iss_html, fs=13, color=C["INK"], box=True)
note("LN", "srcs", 3700, 2090, 1180, 220,
     "<b>Sources used for pins and colours</b><br>"
     "LANECTRL R1 SchDoc / PcbDoc (2026-09-25) · NFC R1 netlist · SYSCTRL R1 netlist (2026-09-25 20:17) · "
     "ADHERENT_Electrical_Tables.xlsx · R27 harness register (git history: W-IDs, length estimates) · "
     "Mean Well RSP-500 spec · Schaffner/TE FN9264 listing · Anaheim 23MSD manual (McMaster 6627T113) · "
     "McMaster 6627T357 page + 4-lead diagram · Emtech NEMA 23 closed-loop listing (motor / encoder colours) · "
     "Miuzei DS3218 listing · Omron EE-SX47/67 datasheet · Waveshare ESP32-S3-ETH-8DI-8RO wiki + product page · "
     "MYIR MYD-YF13X product page · Molex 1462362151 sales drawing · CB002 supplier sheet + supplier schematic.<br>"
     "Photos: manufacturer / supplier pages; SYSCTRL and LANECTRL renders and the J2 photo come from the supplied "
     "example diagram.", fs=10, color=C["INK"], box=True)


# ============================================================================= PAGE 2 · CABLE SCHEDULE
def table(rows, widths, head, fs=11):
    th = "".join(f'<th style="border:1px solid #9E9E9E;background:#ECEFF1;padding:3px 5px;text-align:left;width:{w}px">{h}</th>'
                 for h, w in zip(head, widths))
    trs = ""
    for r in rows:
        bg = "#FFEBEE" if r[-1].startswith("⚠") else ("#F5F5F5" if "TBC" in r[-1] else "#FFFFFF")
        trs += "<tr>" + "".join(f'<td style="border:1px solid #BDBDBD;padding:2px 5px;vertical-align:top;background:{bg}">{c}</td>'
                                for c in r) + "</tr>"
    return (f'<table style="border-collapse:collapse;font-size:{fs}px;font-family:Helvetica;width:100%">'
            f"<tr>{th}</tr>{trs}</table>")


HEAD = ["Cable", "Qty", "Conductor / signal", "From (device · connector.pin)", "To (device · connector.pin)",
        "Length (R27 est.)", "Status / note"]
WID = [70, 36, 150, 300, 300, 80, 340]
SCHED = [
    ("① AC mains & protective earth", [
        ("site cord", "1", "L / N / PE", "site outlet", "J1 · IEC C14 inlet", "site", "Site-supplied IEC C13 cord set"),
        ("W01", "1", "L", "J1 · load side L (fast-on)", "PSU1 · TB1-1 AC/L", "0.4 m", "J1 = FN9264-6-06 candidate; breaker / fuse TBC; R27 lists W01 as L/N/PE — PE drawn via W37 here, fix in bonding plan"),
        ("W01", "", "N", "J1 · load side N (fast-on)", "PSU1 · TB1-2 AC/N", "", ""),
        ("W37", "1", "PE", "J1 · PE", "chassis PE stud", "TBC", "Bonding plan pending"),
        ("W37", "", "PE", "chassis PE stud", "PSU1 · TB1-3 FG", "", ""),
        ("W37", "n", "PE", "chassis PE stud", "panels · doors · DIN rail", "", "Bonding plan pending — TBC"),
    ]),
    ("② 24 V main feed", [
        ("W03", "1", "+24 V", "PSU1 · TB2-4/5/6 +V", "SYSCTRL · J1 (+) Phoenix 1757242", "0.5 m", "J1 pin polarity not yet on a net in R1 — TBC"),
        ("W03", "", "0 V", "PSU1 · TB2-1/2/3 −V", "SYSCTRL · J1 (−)", "", "Size for 21 A PSU / SYSCTRL input rating"),
    ]),
    ("③ Cabinet DC branches (from SYSCTRL)", [
        ("W05", "1", "+12 V / 0 V", "SYSCTRL · 12 V out, F13 (connector TBC)", "MAINCTRL · DC jack (12 V / 2 A, plug TBC)", "0.5 m", "SYSCTRL connector and MYIR plug TBC"),
        ("W34", "1–2", "+24 V / 0 V", "SYSCTRL · 24 V out, F17 (connector TBC)", "IOCTRL-01 and IOCTRL-02 · power terminal (7–36 V)", "1.5 m", "Per-module pair or shared branch TBC (R27: 1)"),
        ("W35", "1", "+12 V / 0 V", "SYSCTRL · 12 V out, F18 (connector TBC)", "IOCTRL-01 · RO1–RO4 COM (+12 V) · latch return point (0 V)", "1.5 m", "Relay COM supply and latch returns (R27)"),
        ("W29", "1", "+24 V / 0 V", "SYSCTRL · F15 (connector TBC)", "X driver · +V / GND", "1.2 m", "⚠ listing 48 V DC vs 24 V proposed — confirm"),
        ("W30", "1", "+24 V / 0 V", "SYSCTRL · F16 (connector TBC)", "Z driver · +V / GND", "2.2 m", "⚠ listing 48 V DC vs 24 V proposed — confirm"),
        ("—", "1", "+24 V / 0 V", "SYSCTRL · NFC branch (TBC)", "NFC · J1.1 +24V_VIN / J1.2 GND", "TBC", "No W-ID / fuse yet — TBC"),
    ]),
    ("④ CAN bus · 500 kbit/s · 120 Ω at both ends", [
        ("W08", "1", "CAN_H / CAN_L (+ 0 V, shield)", "MAINCTRL · native CAN connector (pinout TBC)", "SYSCTRL · CAN (no connector in R1)", "0.4 m", "Twisted pair; 120 Ω at MAINCTRL end (check MYIR board first) — TBC"),
        ("W25", "1", "CAN_H / CAN_L", "SYSCTRL · CAN", "LANECTRL-10 · J8.3 / J8.4", "1.8 m", "Enters row chain at LC-10"),
        ("W26", "9", "CAN_H / CAN_L", "LANECTRL-nn · J8.3 / J8.4", "LANECTRL-(nn−1) · J8.3 / J8.4", "9 × 0.3 m", "⚠ two pairs per J8 plug → splice rule / 2nd connector"),
        ("—", "1", "CAN_H / CAN_L", "bus tap (position TBC)", "NFC · J1.3 CAN1_P / J1.4 CAN1_N", "TBC", "NFC bus position and W-ID TBC"),
        ("—", "1", "antenna lead", "NFC · J4.1 / J4.2", "ANT-NFC · RED / BLACK lead (505565-0201)", "0.102 m (Molex lead)", "⚠ J4 2.54 mm header does not mate with Micro-Lock Plus plug"),
    ]),
    ("⑤ Ethernet & RS485", [
        ("W38", "1", "Ethernet", "site LAN", "J2 · EXT RJ45", "site", "Site-supplied patch cord"),
        ("W09", "1", "Ethernet Cat5e/6", "J2 · INT RJ45", "MAINCTRL · ETH0 RJ45", "0.5 m", "Shielded patch cord"),
        ("W33", "1", "RS485 A / B / GND", "MAINCTRL · RS485 (pinout TBC)", "IOCTRL-01 · RS485 A / B / GND", "1.5 m", "Twisted pair; check MYIR termination / bias"),
        ("W33 ext.", "1", "RS485 A / B / GND", "IOCTRL-01 · RS485 (same terminal)", "IOCTRL-02 · RS485 A / B / GND", "TBC", "Fit 120 Ω jumper at IOCTRL-02 (bus end) — ID TBC"),
    ]),
    ("⑥ Gantry X / Z drives (×2: X = J11, Z = J13)", [
        ("W11 / W12", "2", "PUL+ / PUL−", "SYSCTRL · J11.1 / J11.2 (J13 for Z)", "driver · PUL+ / PUL−", "1.2 m X / 2.2 m Z", "AM26C31 differential output"),
        ("W11 / W12", "", "DIR+ / DIR−", "SYSCTRL · J11.3 / J11.4", "driver · DIR+ / DIR−", "", ""),
        ("W11 / W12", "", "ENA+ / ENA−", "SYSCTRL · J11.5 / J11.6", "driver · ENA+ / ENA−", "", ""),
        ("W11 / W12", "", "ALM / GND", "SYSCTRL · J11.7 ALM_IN / J11.8 GND", "driver · ALM+ / ALM− (names TBC)", "", "Driver terminal names TBC"),
        ("W11 / W12", "", "+24V_MOT / BRK−", "SYSCTRL · J11.9 / J11.10", "motor · brake + / brake −", "", "Brake voltage / colours TBC"),
        ("supplied", "2", "A+ A− B+ B−", "driver · motor terminals", "motor lead WHT / GRN / BLU / BLK", "2.0 m", "Emtech kit cable"),
        ("supplied", "2", "encoder (6 wires)", "driver · encoder DB15", "motor encoder DB15 (WHT 0 V, RED +5 V, YEL EB+, GRN EB−, BLU EA−, BLK EA+)", "0.3 + 1.7 m", "Emtech kit: motor lead + extension"),
    ]),
    ("⑦ Labeling motors & servo", [
        ("W13", "1", "+V / GND / PWM", "SYSCTRL · J15 (43650-0300, pin map TBC)", "DS3218 · RED / BLACK / WHITE (300 mm lead re-terminated, R27)", "3.8 m", "Servo supply 4.8–6.8 V — TBC pin map"),
        ("W16", "1", "—", "SYSCTRL · J12 (TMC5160 coil outputs)", "CHUCK 6627T113 · 7-pin input", "1.5 m", "⚠ blocked: interface mismatch (see page 1)"),
        ("W17", "1", "A+ / A− / B+ / B−", "SYSCTRL · J14.1 OUT1A / .2 OUT2A / .3 OUT1B / .4 OUT2B", "JAWS 6627T357 · RED / BLUE / GREEN / BLACK", "1.5 m", "Leads 24 in; extend or plug — TBC"),
    ]),
    ("⑧ Sensors", [
        ("W15", "6", "+V / 0 V / OUT (+ L)", "SYSCTRL · sensor inputs X1–X3, Z1–Z3 (not in R1; R27 J21–J26)", "Omron EE-SX672-WR / EE-SX674-WR · BRN / BLU / BLK (PNK = L)", "TBC (sensor lead 1 m)", "Terminate PNK for dark-/light-ON — TBC connector"),
        ("W18", "1", "+V / 0 V / OUT", "SYSCTRL · jaw sensor input (TBC)", "JAW-SENS (part TBC)", "1.5 m", "R27: 4c 22 AWG R +V · B GND · Y OUT · G spare — TBC"),
    ]),
    ("⑨ Doors & latches", [
        ("W20", "1", "K1 R / B · K2 Y / G (R, Y = + by convention)", "IOCTRL-01 · RO1 NO, RO2 NO · 0 V of W35", "latch K1, K2 (Micro-Fit 2-pin candidate)", "0.8 m", "R27: 4c 22 AWG · latch part TBC"),
        ("W21", "1", "K3 R / B · K4 Y / G (R, Y = + by convention)", "IOCTRL-01 · RO3 NO, RO4 NO · 0 V of W35", "latch K3, K4", "0.8 m", "R27: 4c 22 AWG · latch part TBC"),
        ("W23", "5", "DIn / DI common", "IOCTRL-01 · DI1…DI5 / DI common", "door sensor S1…S5", "TBC", "Sensor type and DI mode TBC"),
    ]),
    ("⑩ Lane rows (×10 rows · 7 lanes each)", [
        ("W24-nn", "10", "+24 V / 0 V", "SYSCTRL · row feed, R27 branch Fnn (connector TBC)", "LANECTRL-nn · J8.1 +24V_VIN / J8.2 GND", "10 × 2.4 m", "⚠ R1: 6 fused headers + 1 eFuse only"),
        ("W27", "70", "LANE_OUT / GND / SIG", "LANECTRL-nn · Jk.1 / Jk.2 / Jk.3 (k = 1…7, 43650-0300)", "CONVEYOR · VH3.96 pin 1 / 2 / 3", "70 × 0.8 m", "Meter-check pin 1 / 3 on one conveyor first"),
        ("LED", "70", "+ / −", "LANECTRL-nn · LEDSk.1 (via 100 Ω) / LEDSk.2 GND (2.54 mm)", "lane LED k (off-board)", "TBC", "LED part TBC"),
    ]),
    ("⑪ Status light & marker", [
        ("W36", "1", "+12 V / lamp outputs", "SYSCTRL · stack-light outputs (not in R1; R27 J44)", "stack light (part TBC)", "TBC", "HOLD O15 — TBC"),
        ("W19", "1", "data (USB or Cat6, R27)", "MAINCTRL · port TBC", "MARKER · data (TBC)", "1.5 m", "Marker not selected — TBC"),
        ("W39", "1", "supply", "SYSCTRL · branch TBC", "MARKER · supply (TBC)", "TBC", "Marker not selected — TBC"),
    ]),
]
P2 = Page("cs", "2 · Cable schedule", 3000, 2600)
P2.layer("L0b", "Cable schedule")
P2.v("t2", 40, 20, 2900, 60, '<font style="font-size:24px"><b>ADHERENT · Cable schedule by build step</b></font><br>'
     "Companion to page 1. Qty = instances in the machine. Lengths = R27 register estimates (not measured). "
     "Grey rows = TBC, red rows = conflict to resolve first.",
     f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;fontColor={C['INK']};{F}strokeColor=none;fillColor=none;",
     "L0b")
col_x = [40, 1530]
col_y = [100, 100]
for i, (title, rows) in enumerate(SCHED):
    c = 0 if i < 6 else 1
    scale = 1430 / sum(WID)
    def lines(cell, w):
        per = max(8, int(w * scale / 6.0))
        return max(1, -(-len(cell) // per))
    h = 40 + 30 + sum(6 + 14 * max(lines(cell, w) for cell, w in zip(r, WID)) for r in rows)
    P2.v(f"tab{i}", col_x[c], col_y[c], 1430, h,
         f'<div style="font-size:14px;font-weight:bold;margin-bottom:4px">{title}</div>' + table(rows, WID, HEAD),
         f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=11;fontColor={C['INK']};{F}"
         "strokeColor=none;fillColor=none;overflow=width;", "L0b")
    col_y[c] += h + 26

# ============================================================================= PAGE 3 · CONNECTORS
CONN = [
    ("LANECTRL", "J8", "Molex 43045-0400 Micro-Fit 3.0, 2×2", "43025-0400 + 43030-0007 crimp (R27 candidate)", "1 +24V_VIN · 2 GND · 3 CAN_H · 4 CAN_L", "SchDoc / PcbDoc"),
    ("LANECTRL", "J1–J7", "Molex 43650-0300 Micro-Fit 3.0, 1×3", "43645-0300 + 43030-0007 (R27 candidate)", "1 LANE_OUTn · 2 GND · 3 SIGn", "SchDoc / PcbDoc"),
    ("LANECTRL", "LEDS1–7", "2-pin 2.54 mm header (Molex 22-03-2021)", "2.54 mm 2-way housing (TBC)", "1 via R50–R56 100 Ω · 2 GND", "SchDoc / netlist"),
    ("LANECTRL", "P1 / S1 / J9 / J10", "jumper / DIP / FTSH SWD / USB-C", "—", "P1 120 Ω CAN term. · S1 node ID · service ports", "SchDoc"),
    ("NFC", "J1", "Molex 43045-0400 Micro-Fit 3.0, 2×2", "43025-0400 + 43030-0007", "1 +24V_VIN · 2 GND · 3 CAN1_P · 4 CAN1_N", "NFC netlist"),
    ("NFC", "J4", "Würth 61300211821, 2-pin 2.54 mm", "⚠ antenna plug is Molex 505565-0201 (1.25 mm)", "1 / 2 antenna coil", "NFC netlist · Molex drawing"),
    ("SYSCTRL", "J1", "Phoenix 1757242 (2-pos, 5.08 mm)", "Phoenix MSTB 2,5/2-ST-5,08 plug — verify", "+24 V / 0 V (pins not yet on a net)", "SYSCTRL netlist"),
    ("SYSCTRL", "J11 (X) / J13 (Z)", "Molex 43045-1000 Micro-Fit 3.0, 2×5", "43025-1000 + 43030-0007", "1 PUL+ · 2 PUL− · 3 DIR+ · 4 DIR− · 5 ENA+ · 6 ENA− · 7 ALM_IN · 8 GND · 9 +24V_MOT · 10 BRK−", "SYSCTRL schematic"),
    ("SYSCTRL", "J12", "Molex 43045-0400 Micro-Fit 3.0, 2×2", "43025-0400 + 43030-0007", "1 BMA1 · 2 BMA2 · 3 BMB1 · 4 BMB2 (TMC5160)", "SYSCTRL netlist"),
    ("SYSCTRL", "J14", "Molex 43045-0400 Micro-Fit 3.0, 2×2", "43025-0400 + 43030-0007", "1 OUT1A · 2 OUT2A · 3 OUT1B · 4 OUT2B (TMC2240)", "SYSCTRL netlist"),
    ("SYSCTRL", "J15", "Molex 43650-0300 Micro-Fit 3.0, 1×3", "43645-0300 + 43030-0007", "servo +V / GND / PWM — pin map TBC", "SYSCTRL schematic"),
    ("SYSCTRL", "J4–J7, J10 / J8–J9", "Molex 43650-0200 (2-pin) / 43650-0500 (5-pin)", "43645-0200 / 43645-0500", "board fuses F1–F3 → J4–J6, F5–F7 → J8–J10, eFuse → J7 — allocation TBC", "SYSCTRL schematic"),
    ("SYSCTRL", "J2 / J3", "SWR201-NRTN-S03 UART / Samtec FTSH-105 SWD", "service cables", "UART 1 GND · 2 TX · 3 RX / ARM 10-pin SWD", "SYSCTRL netlist"),
    ("CONVEYOR", "—", "JST VH3.96 3-pin (on conveyor)", "JST VHR-3N + SVH-21T-P1.1", "1 +24 V · 2 GND · 3 SIGNAL = +24 V via plate switch S1 / D2 while powered (datasheet; supplier schematic numbers pins in reverse)", "CB002 supplier sheet + schematic"),
    ("CHUCK 6627T113", "input", "AMP 640440-7 (MTA-100, 7-pos)", "Anaheim CBL-AA4031 (12 in leads)", "1 DIR BRN · 2 CLK RED · 3 ON/OFF ORN · 4 MS2 YEL · 5 MS1 GRN · 6 +12–24 VDC BLU · 7 0 VDC VIO", "Anaheim 23MSD manual"),
    ("JAWS 6627T357", "leads", "4 flying leads, 26 AWG, 24 in", "to be terminated", "A+ RED · A− BLUE · B+ GREEN · B− BLACK", "McMaster page"),
    ("X / Z MOTOR", "leads", "motor lead 2.0 m · encoder 0.3 m + 1.7 m ext., DB15", "plugs into supplied driver", "A+ WHT · A− GRN · B+ BLU · B− BLK · enc WHT 0 V · RED 5 V · YEL EB+ · GRN EB− · BLU EA− · BLK EA+", "Emtech listing"),
    ("SERVO DS3218", "lead", "3-way servo plug", "to J15 (adapter / re-terminate TBC)", "BLACK GND · RED +V · WHITE PWM", "supplier listing photo"),
    ("Omron EE-SX67x-WR", "leads", "1 m flying leads", "to SYSCTRL sensor connector (TBC)", "BRN +V · BLU 0 V · BLK OUT · PNK L", "Omron datasheet"),
    ("ANT-NFC", "lead", "Molex 505565-0201 + 505431-1000", "needs Micro-Lock Plus 2-ckt header on NFC", "RED / BLACK twisted pair, 28 AWG, 102 mm", "Molex drawing"),
    ("PSU1 RSP-500-24", "TB1 / TB2 / CN100", "screw terminals / HRS DF11-04DP-2DS", "ring or fork lugs / CN100 unused", "TB1 1 AC/L · 2 AC/N · 3 FG · TB2 1–3 −V · 4–6 +V · CN100 1 −S · 2 +S · 3 RC− · 4 RC+", "Mean Well spec"),
    ("J1 FN9264-6-06", "—", "IEC C14 inlet, fast-on terminals", "insulated fast-on receptacles (size per datasheet)", "L · N · PE (load side)", "Schaffner/TE listing"),
    ("MAINCTRL MYD-YF13X", "DC / CAN / RS485 / ETH", "native MYIR connectors", "TBC from MYIR hardware manual", "12 V / 2 A jack · CAN · RS485 · 2 × GbE RJ45", "MYIR product page"),
    ("IOCTRL ESP32-S3-ETH-8DI-8RO", "terminals", "screw terminals", "bootlace ferrules", "7–36 V · RS485 A / B / GND · RO1–8 NO / COM / NC · DI1–8 + common", "Waveshare wiki / product page"),
    ("J2 1422N13", "—", "RJ45 F/F shielded coupler", "Cat5e / Cat6 patch cords", "1:1 pass-through", "R27 register (S05)"),
]
P3 = Page("cn", "3 · Connector reference", 3000, 1000)
P3.layer("L0c", "Connector reference")
P3.v("t3", 40, 20, 2900, 60, '<font style="font-size:24px"><b>ADHERENT · Connector reference</b></font><br>'
     "Board header, mating part and pin map for every harness end. Mating parts marked R27 are register candidates — "
     "confirm wire gauge, current and keying before ordering.",
     f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;fontColor={C['INK']};{F}strokeColor=none;fillColor=none;",
     "L0c")
P3.v("t3tab", 40, 100, 2900, 600, table(CONN, [220, 170, 360, 360, 900, 220],
                                         ["Device", "Ref.", "Board / device side", "Mating part", "Pin map", "Source"], fs=13),
     f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=11;fontColor={C['INK']};{F}strokeColor=none;fillColor=none;",
     "L0c")
P3.v("t3rules", 40, 760, 2900, 190,
     "<b>Harness build rules used in this drawing</b><ul style=\"margin:4px 0 0 0;padding-left:18px\">"
     "<li>One cable ID per physical cable (W01…W39); label both ends with W-ID and destination (e.g. W24-07 → LANECTRL-07 J8).</li>"
     "<li>Project cable convention: 4-core 22 AWG red / black / yellow / green where electrically suitable; mains and "
     "higher-current pairs use rated exceptions sized per fuse / load (gauges not yet specified in the design files).</li>"
     "<li>CAN and RS485: twisted pair, 120 Ω only at the two physical bus ends; shield / drain is not protective earth — "
     "terminate it at one end only (decision pending).</li>"
     "<li>Differential step signals (PUL±, DIR±, ENA±) as twisted pairs; motor phases as pairs A+/A− and B+/B−.</li>"
     "<li>IOCTRL screw terminals: bootlace ferrules. PSU1 barrier terminals: ring / fork lugs. Micro-Fit and VH crimps "
     "with the manufacturer tool.</li>"
     "<li>Protective earth green / yellow; all exposed metal bonded to the chassis PE stud (W37).</li>"
     "<li>Build and test one step (layer) at a time: continuity, polarity and termination resistance before power-up.</li></ul>",
     f"text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;fontColor={C['INK']};{F}"
     "strokeColor=#CFD8DC;fillColor=#FAFBFC;spacing=8;", "L0c")

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<mxfile host="Electron" agent="Blackocean Technologies" pages="3">'
       + P.xml() + P2.xml() + P3.xml() + "</mxfile>\n")
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(xml)
print("page1 cells", len(P.cells), "page2", len(P2.cells), "page3", len(P3.cells), "->", OUT, os.path.getsize(OUT))
