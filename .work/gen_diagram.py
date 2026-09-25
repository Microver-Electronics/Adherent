#!/usr/bin/env python3
"""Generate SYS/ADHERENT_System_Wiring_Diagram.drawio with a fixed, corridor-based layout.

Content is carried over from the R27 diagram (2026-09-25 state). Only layout, wording
density and the NFC reader block (now the HW_ADHERENT_NFC_R1 custom PCB) change.
"""
import html, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "SYS/ADHERENT_System_Wiring_Diagram.drawio"

RED, BLUE, INK, GREY, AMBER, PURPLE = "#BE3A2B", "#1D5FA8", "#171A1F", "#6B737C", "#9A6510", "#7356A0"
FONT = "fontFamily=Helvetica;"
cells = []


def esc(s):
    return html.escape(s, quote=True)


def g(t):  # grey secondary line
    return f'<font color="{GREY}">{t}</font>'


GEO = {}


def vertex(id, x, y, w, h, value, style, parent="1"):
    px, py = (GEO[parent][0], GEO[parent][1]) if parent in GEO else (0, 0)
    GEO[id] = (px + x, py + y, w, h)
    cells.append(f'<mxCell id="{id}" value="{esc(value)}" style="{style}" vertex="1" parent="{parent}">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" /></mxCell>')


def zone(id, x, y, w, h, title, stroke=INK, fill="#F0F2F5", dashed=True):
    vertex(id, x, y, w, h, title,
           f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;"
           f"dashed={1 if dashed else 0};{FONT}fontSize=14;fontStyle=1;fontColor={stroke};verticalAlign=top;"
           f"align=left;spacingLeft=12;spacingTop=6;")


def box(id, x, y, w, h, value, stroke=INK, fill="#FFFFFF", dashed=False, tag=None, fs=12, sw=1.5,
        parent="1", valign="middle"):
    top = 18 if tag else 0
    vertex(id, x, y, w, h, value,
           f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
           f"dashed={1 if dashed else 0};{FONT}fontSize={fs};spacing=6;spacingTop={top};verticalAlign={valign};",
           parent)
    if tag:
        vertex(f"tag_{id}", 6, 3, 52, 17, tag,
               f"text;html=1;align=left;verticalAlign=top;{FONT}fontSize=13;fontStyle=1;fontColor=#FF0000;"
               "strokeColor=none;fillColor=none;spacing=0;connectable=0;", parent=id)


def text(id, x, y, w, h, value, fs=11, color="#4A5158", align="left", extra=""):
    vertex(id, x, y, w, h, value,
           f"text;html=1;align={align};verticalAlign=top;fontSize={fs};fontColor={color};{FONT}"
           f"strokeColor=none;fillColor=none;whiteSpace=wrap;{extra}")


KIND = {
    # colour, width, dashed
    "p24": (RED, 3.5, 0), "p12": (RED, 2.5, 0), "pTBC": (RED, 2.5, 1),
    "data": (BLUE, 1.8, 0), "dataTBC": (BLUE, 1.8, 1),
    "mot": (INK, 2, 0), "ac": (INK, 2, 0), "excl": (AMBER, 1.6, 1), "rf": (PURPLE, 1.6, 1),
}


def edge(id, src, tgt, label, kind, exit, entry, pts=(), lx=0.0, ly=0.0, start=None, end="block", fs=11, at=None, vlabel=False):
    col, w, d = KIND[kind]
    if at is not None:
        lx = label_pos(src, tgt, exit, entry, pts, at)
    st = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jumpStyle=arc;jumpSize=8;strokeColor={col};"
          f"strokeWidth={w};dashed={d};{FONT}fontSize={fs};fontColor={col};labelBackgroundColor=#FFFFFF;"
          f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;")
    if vlabel:
        st += "horizontal=0;"
    st += f"endArrow={end};endFill=1;endSize=7;" if end != "none" else "endArrow=none;"
    st += f"startArrow={start};startFill=1;startSize=7;" if start else "startArrow=none;"
    pts_xml = "".join(f'<mxPoint x="{px}" y="{py}" />' for px, py in pts)
    arr = f'<Array as="points">{pts_xml}</Array>' if pts else ""
    cells.append(f'<mxCell id="{id}" value="{esc(label)}" style="{st}" edge="1" parent="1" source="{src}" target="{tgt}">'
                 f'<mxGeometry x="{lx}" y="{ly}" relative="1" as="geometry">{arr}<mxPoint as="offset" /></mxGeometry></mxCell>')


def label_pos(src, tgt, exit, entry, pts, at):
    """Relative label position (-1..1) of the path point nearest to absolute point `at`."""
    sx, sy, sw_, sh = GEO[src]
    tx, ty, tw, th = GEO[tgt]
    path = [(sx + exit[0] * sw_, sy + exit[1] * sh)] + list(pts) + [(tx + entry[0] * tw, ty + entry[1] * th)]
    segs = list(zip(path[:-1], path[1:]))
    lens = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in segs]
    total = sum(lens) or 1
    best, acc, bestpos = None, 0.0, 0.0
    for (a, b), L in zip(segs, lens):
        for k in range(0, 101):
            t = k / 100
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            d = (x - at[0]) ** 2 + (y - at[1]) ** 2
            if best is None or d < best:
                best, bestpos = d, acc + L * t
        acc += L
    return round(bestpos / total * 2 - 1, 4)


def legend_line(id, x1, y, x2, kind, label):
    col, w, d = KIND[kind]
    cells.append(f'<mxCell id="{id}" value="" style="endArrow=none;html=1;strokeColor={col};strokeWidth={w};dashed={d};" '
                 f'edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x1}" y="{y}" as="sourcePoint" />'
                 f'<mxPoint x="{x2}" y="{y}" as="targetPoint" /></mxGeometry></mxCell>')
    text(id + "_t", x2 + 8, y - 9, 260, 20, label, fs=12, color=INK)


# ------------------------------------------------------------------ title
text("title", 40, 18, 1150, 60,
     "<b>Electrical System Level Wiring Diagram</b><br>"
     "Adherent360 APDU / AVM · Blackocean Technologies · 10 rows × 7 lanes = 70 conveyors · "
     "2026-09-25 · design review baseline", fs=20, color=INK)

# ------------------------------------------------------------------ column A: network / power / NFC
zone("g_net", 40, 100, 540, 390, "NETWORK / USER ACCESS", stroke=BLUE, fill="#EEF3F9")
box("wifi", 60, 145, 240, 80, "<b>WIFI · Wi-Fi / BT antenna</b> · optional<br>Bulkhead RP-SMA<br>" +
    g("USB Wi-Fi / BT module on MAINCTRL"), stroke=BLUE, dashed=True, tag="CONN", sw=2)
box("rj45", 320, 145, 240, 80, "<b>J2 · RJ45 panel adapter</b><br>McMaster-Carr 1422N13<br>Shielded Cat5e F/F · rear panel",
    stroke=BLUE, tag="CONN", sw=2)
box("lan", 60, 265, 500, 50, "<b>LAN · pharmacy LAN / router</b> · site equipment", stroke=BLUE, fill="#EEF3F9", sw=2)
box("ipad", 60, 360, 240, 90, "<b>IPAD · iPad</b> (not integrated)<br>Adherent app / web browser", stroke=BLUE, sw=2)
vertex("cloud", 320, 345, 240, 120, "<b>CLOUD · Adherent servers</b><br>internet · vend API",
       f"ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={BLUE};strokeWidth=2;{FONT}fontSize=12;")

zone("g_power", 40, 530, 540, 330, "AC INPUT & SINGLE 24 V POWER SUPPLY", stroke=RED, fill="#F7F0EE")
box("acin", 60, 580, 500, 60, "<b>J1 · AC inlet · EMI filter · main breaker</b><br>120 / 230 VAC · IEC C14 + PE", tag="CONN")
box("psu24", 60, 690, 500, 100, "<b>PSU1 · Mean Well RSP-500-24</b><br>24 V · 21 A · 504 W rated · single system AC/DC PSU<br>" +
    g("Full load / thermal budget remains HOLD"), stroke=RED, sw=2)
text("pwr_note", 60, 800, 500, 55,
     "W37: protective-earth bonding to PSU FG and exposed metal · plan pending.<br>"
     "24 V → 12 V is generated only on SYSCTRL; no separate distribution assembly or external 24 → 12 V module.")

zone("g_nfc", 40, 900, 540, 385, "NFC · ANTENNA SELECTED · READER BOARD R1 IN DESIGN", stroke=PURPLE, fill="#F3EEF9")
box("nfc_antenna", 60, 950, 210, 125, "<b>ANT-NFC · Molex 1462362151</b><br>13.56 MHz · 15 × 15 mm<br>102 mm cable · adhesive<br>" +
    g("Selected · 1 per machine planned"), stroke=PURPLE)
box("nfc_pcb", 310, 950, 250, 170, "<b>NFC · HW_ADHERENT_NFC_R1</b><br>Custom PCB · reader board<br>STM32F103C8 + ST25R200<br>"
    "CAN node · 24 V + CAN in<br>4-pin Micro-Fit (J1)<br>" + g("R1 schematic / layout in progress<br>Not a payment terminal"),
    stroke=PURPLE, tag="PCB", sw=2)
text("nfc_note", 60, 1135, 500, 140,
     "System wiring of the NFC board is <b>TBC</b>: CAN bus position and node ID, 24 V feed branch and fuse, "
     "mounting / reading position. No W / F reference is assigned yet, so no harness is drawn.<br>"
     "Matching / RF termination to the antenna is on the NFC board.", fs=11)

# ------------------------------------------------------------------ column B: control cabinet
zone("g_cab", 640, 100, 600, 1185, "CONTROL CABINET · base compartment (behind AVM-BASE-COVER)")
box("sbc", 690, 145, 520, 150,
    "<b>MAINCTRL · MYIR MYD-YF13X · COTS ×1</b><br>HW_ADHERENT_MAINCTRL_R1 · FW_ADHERENT_MAINCTRL_R1<br>"
    "STM32MP135 / Linux · supervisory application<br>CAN master to SYSCTRL / lanes · RS485 master to IOCTRL-01 / -02<br>"
    "12 V from SYSCTRL via F13 / W05 · native MYIR connectors<br>" + g("Exact SKU, populated interfaces and BSP TBC"),
    tag="PCB")
vertex("motion", 690, 345, 520, 570,
       "<b>SYSCTRL · custom STM32 machine controller ×1</b><br>HW_ADHERENT_SYSCTRL_R1 · FW_ADHERENT_SYSCTRL_R1<br>"
       "Gantry: STEP / DIR / ENA, ALARM, brakes (interfaces TBC)<br>Servo: PWM + local regulator (voltage / current TBC)<br>"
       "Labeling: chuck / jaw motor drivers + jaw home sensor<br>6 gantry sensors direct · CAN node · status light W36",
       f"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={INK};strokeWidth=2;{FONT}fontSize=12;"
       "spacing=6;verticalAlign=top;spacingTop=22;")
vertex("tag_motion", 6, 3, 52, 17, "PCB",
       f"text;html=1;align=left;verticalAlign=top;{FONT}fontSize=13;fontStyle=1;fontColor=#FF0000;strokeColor=none;"
       "fillColor=none;spacing=0;connectable=0;", parent="motion")
box("sysctrl_buck", 20, 160, 480, 60,
    "<b>BUCK12 · onboard SMPS 24 V → 12 V</b> · rating / implementation TBC<br>"
    "Feeds MAINCTRL, local logic / servo / sensors and latch contacts", stroke=RED, fill="#FFF4EE", fs=11, sw=2,
    parent="motion")
box("dist", 0, 250, 520, 320,
    "<b>SYSCTRL-PWR · SYSCTRL power connectors</b><br>24 V input from PSU1 (W03)<br>"
    "24 V out: lane rows F1–F10 · X / Z drives F15 / F16 (TBC) · IOCTRL F17<br>"
    "12 V out: MAINCTRL F13 · IOCTRL relay COM F18<br>"
    "F1–F18 are branch references; protection implementation TBC<br>" +
    g("Connectors on the SYSCTRL PCB, not a separate distribution assembly"),
    stroke=RED, fill="#FFFAF8", tag="CONN", sw=1.5, parent="motion")
box("ioctrl_02_stack", 698, 983, 520, 150, "", stroke=BLUE, fill="#EEF3F9", sw=2)
box("ioctrl", 690, 975, 520, 150,
    "<b>IOCTRL-01 / IOCTRL-02 · Waveshare ESP32-S3-ETH-8DI-8RO · COTS ×2</b><br>"
    "24 V module supply via F17 / W34, each module · rated input 7–36 V<br>"
    "Relay COM: SYSCTRL-derived 12 V via F18 / W35<br>"
    "Isolated RS485 to MAINCTRL · two addresses, shared bus TBC · Modbus RTU to verify<br>"
    "RO1–4: latches · DI1–5: door sensors · split across modules TBC<br>" + g("Wi-Fi / BLE / Ethernet unused"),
    stroke=BLUE, fill="#EEF3F9", tag="PCB", sw=2)
box("stacklight", 690, 1165, 250, 60, "<b>STACK · 12 V status light</b><br>MPN TBC · W36 direct from SYSCTRL · route TBC",
    stroke="#394047", fs=11)
text("cab_note", 955, 1160, 270, 115,
     "Sensors are wired directly to controller boards; no junction boxes.<br>"
     "CAN backbone: MAINCTRL → SYSCTRL → LANECTRL-10 → … → LANECTRL-01 · two end terminations · 500 kbit/s planning bitrate.")

# ------------------------------------------------------------------ column C: gantry / labeling / doors
CX, CW = 1425, 610
zone("g_gantry", 1400, 100, 660, 445, "GANTRY · 6 direct sensor runs to SYSCTRL · igus chains X 762 mm / Z 1616 mm")
box("xstep", CX, 145, CW, 80, "<b>X · closed-loop stepper + supplied driver</b> · Emtech 57BYG250-76 · 2 N·m · 4 A · brake · X-GB 3:1 gearbox<br>" +
    g("24 V input proposed, supplier confirmation required · STEP / DIR / ENA in · ALARM out · brake 24 V (TBC)"),
    tag="MTR", valign="middle")
box("zstep", CX, 245, CW, 80, "<b>Z · closed-loop stepper + supplied driver</b> · Emtech 57BYG250-76 · 2 N·m · 4 A · brake holds carriage<br>" +
    g("24 V input proposed, supplier confirmation required · STEP / DIR / ENA in · ALARM out · brake 24 V (TBC)"),
    tag="MTR")
box("servo", CX, 345, CW, 80, "<b>SERVO · basket tilt servo · Miuzei DS3218 ×1</b><br>Local regulator on SYSCTRL · exact variant, travel and supply range TBC<br>" +
    g("Stall / current limit and signal timing require verification"), tag="MTR")
box("optos", CX, 445, CW, 80, "<b>X-SENS / Z-SENS · 6 × Omron prewired sensors</b><br>EE-SX672-WR ×3 (X) · EE-SX674-WR ×3 (Z) · direct to SYSCTRL J21–J26<br>" +
    g("1 m supplied leads · actual routes / lead arrangement TBC"))

zone("g_station", 1400, 565, 660, 315, "LABELING MECHANISM · laser platform assembly")
box("chuck", CX, 610, CW, 70, "<b>CHUCK · chuck rotate stepper</b><br>NEMA23 + gearbox · catalog reference 6627T113 · 4-wire",
    tag="MTR")
box("jaws", CX, 700, CW, 70, "<b>JAWS · chuck jaw stepper + JAW-SENS home sensor</b><br>NEMA11 · catalog reference 6627T357 · T5 belt · 4-wire",
    tag="MTR")
box("camq", CX, 790, 290, 75, "<b>CAM · camera / OCR · excluded</b><br>Pending decision · no power or cable allocated",
    stroke=AMBER, dashed=True, fs=11)
box("printer", 1745, 790, 290, 75, "<b>MARKER · label marker · model TBC</b><br>W19 data interface pending<br>"
    "W39 supply / protection pending · no extra PSU", stroke=AMBER, dashed=True, fs=11)

zone("g_doors", 1400, 960, 660, 325, "DOORS & LATCHES · direct wiring to IOCTRL ×2")
box("latches", CX, 1005, CW, 70, "<b>K1–K4 · 4 × 12 V latch</b> · main · retrieval · return · table<br>" +
    g("Switched 12 V from IOCTRL RO1–RO4 · MPN, duty, suppression and fail behavior TBC"))
box("doorsens", CX, 1095, CW, 70, "<b>DI1–DI5 · 5 × door sensor</b> (reed / microswitch TBC) · main · retrieval · return · table · front access<br>" +
    g("Direct to IOCTRL DI1–DI5 · lead lengths and DI reference / polarity TBC"))
box("dooract", CX, 1185, CW, 55, "<b>DOORACT · door actuators · excluded until defined</b><br>W28 quantity 0 · RO5–RO8 reserved · no reversing circuit approved",
    stroke=AMBER, dashed=True, fs=11)

# ------------------------------------------------------------------ column D: lane rows
zone("g_lanes", 2140, 100, 790, 1185,
     "LANE ROWS · 10 rows × 7 lanes · HW_ADHERENT_LANECTRL_R1 ×10 · FW_ADHERENT_LANECTRL_R1")
vertex("busbar", 2160, 150, 6, 1010, "", f"rounded=0;html=1;fillColor={RED};strokeColor={RED};")
for i in range(1, 11):
    y = 150 + (i - 1) * 103
    node = {1: "CAN node 1 · 120 Ω termination (jumper)", 10: "CAN node 10 · bus entry"}.get(i, f"CAN node {i}")
    box(f"lc{i}", 2205, y, 320, 83,
        f"<b>LANECTRL-{i:02d}</b> · {node}<br>7 × high-side switch · 7 × feedback · 7 × rocker + LED<br>" +
        g(f"24 V + CAN in (F{i}) · 4-pin Micro-Fit"), stroke=RED, tag="PCB", fs=11, sw=2)
    box(f"lanes{i}", 2610, y, 300, 83,
        f"<b>CONVEYOR-{i:02d}</b> · 7 × CB002-24V-573mm<br>24 V · ≤0.2 A no-load · 5.8 cm/s · ≤6 kg<br>" +
        g("0.19 A run · ≈0.5 A stall (bench test)"), tag="MTR", fs=11)
    edge(f"e_f{i}", "busbar", f"lc{i}", f"F{i}", "p12", (1, (y + 41.5 - 150) / 1010), (0, 0.5), fs=10, lx=-0.2)
    edge(f"e_l{i}", f"lc{i}", f"lanes{i}", "W27 · 7 × 3-pos", "mot", (1, 0.5), (0, 0.5), start="block", fs=10)
    if i < 10:
        edge(f"e_rs{i + 1}", f"lc{i}", f"lc{i + 1}", "W26", "data", (0.5, 1), (0.5, 0), end="none", fs=10)
text("lane_note", 2160, 1195, 760, 90,
     "Rocker switches on board, lane LEDs via headers · busbar = 10 separately fused row feeds F1–F10 (W24) · W26 = CAN daisy-chain between rows; harness form TBC "
     "(one 4-pin bus connector per board).<br>LANECTRL boards sit at the front of each row behind the metal bracket "
     "(DWG in MEC/01_CAD_MODELS/Drawıng) · PCB 504 × 60 mm · 72 mm lane pitch · fit to verify.<br>"
     "W27: 70 motor / signal leads stay in rows · on/off high-side drive, no reversal · signal pin reference to confirm.<br>"
     "Lane n = 1…70: row = floor((n−1)/7)+1 · channel = ((n−1) mod 7)+1.")

# ------------------------------------------------------------------ edges: network / power / cabinet
edge("e_sbc_rj45", "sbc", "rj45", "W09 · Ethernet", "data", (0, 40 / 150), (1, 0.5), at=(625, 185))
edge("e_sbc_wifi", "sbc", "wifi", "W10 · optional USB radio / antenna · qty 0", "dataTBC", (0.06, 0), (0.5, 0),
     pts=[(721, 128), (180, 128)], at=(450, 128))
edge("e_rj45_lan", "rj45", "lan", "W38 · site-supplied Ethernet", "data", (0.5, 1), (0.8, 0), end="none")
edge("e_wifi_lan", "wifi", "lan", "", "dataTBC", (0.5, 1), (0.24, 0), end="none")
edge("e_lan_ipad", "lan", "ipad", "web UI / app", "data", (0.24, 1), (0.5, 0))
edge("e_lan_cloud", "lan", "cloud", "internet", "data", (0.8, 1), (0.5, 0.07))
edge("e_ac24", "acin", "psu24", "W01 · AC", "ac", (0.5, 1), (0.5, 0))
edge("e_24dist", "psu24", "dist", "W03 · 24 V", "p24", (1, 0.5), (0, (740 - 595) / 320), at=(620, 740))
edge("e_12sbc", "dist", "sbc", "W05 · F13 · 12 V", "p12", (0, (700 - 595) / 320), (0, 125 / 150),
     pts=[(672, 700), (672, 270)], at=(672, 470), vlabel=True)
edge("e_rs485", "sbc", "ioctrl", "W33 · RS485 · IOCTRL-01 / -02", "data", (0, 85 / 150), (0, 55 / 150),
     pts=[(655, 230), (655, 1030)], at=(655, 880), vlabel=True)
edge("e_sbc_motion", "sbc", "motion", "W08 · CAN backbone · 500 kbit/s", "data", (0.25, 1), (0.25, 0), start="block")
edge("e_stack", "dist", "stacklight", "W36", "p12", (0, (890 - 595) / 320), (0, 0.5), pts=[(672, 890), (672, 1195)], at=(672, 1100), vlabel=True)
edge("e_12ioctrl", "dist", "ioctrl", "W34 · F17 · 24 V", "p24", (0.35, 1), (0.35, 0), at=(872, 945))
edge("e_contact12", "dist", "ioctrl", "W35 · F18 · 12 V relay COM", "p12", (0.72, 1), (0.72, 0), at=(1064, 945))

# SYSCTRL control outputs (right side of the logic area, abs y 400…525)
Y0 = 345
edge("e_gx", "motion", "xstep", "W11 · X drive ctrl", "data", (1, (400 - Y0) / 570), (0, 25 / 80), pts=[(1290, 400), (1290, 170)], lx=0.55)
edge("e_gz", "motion", "zstep", "W12 · Z drive ctrl", "data", (1, (425 - Y0) / 570), (0, 25 / 80), pts=[(1315, 425), (1315, 270)], lx=0.55)
edge("e_gservo", "motion", "servo", "W13 · servo", "data", (1, (450 - Y0) / 570), (0, 40 / 80), pts=[(1340, 450), (1340, 385)], lx=0.55)
edge("e_gopto", "optos", "motion", "W15 · 6 sensor runs", "data", (0, 40 / 80), (1, (475 - Y0) / 570), pts=[(1365, 485), (1365, 475)], lx=-0.55)
edge("e_chuck", "motion", "chuck", "W16 · chuck rotate", "mot", (1, (500 - Y0) / 570), (0, 35 / 70), pts=[(1340, 500), (1340, 645)], lx=0.55)
edge("e_jaws", "motion", "jaws", "W17 + W18 · jaws + home sensor", "mot", (1, (525 - Y0) / 570), (0, 35 / 70), pts=[(1310, 525), (1310, 735)], lx=0.5)

# SYSCTRL-PWR outputs to the far side (corridor y 895…945 between labeling and doors)
edge("e_48z", "dist", "zstep", "W30 · F16 · 24 V (TBC) · Z drive", "pTBC", (1, (760 - 595) / 320), (1, 55 / 80),
     pts=[(1275, 760), (1275, 895), (2080, 895), (2080, 300)], at=(2080, 470), vlabel=True)
edge("e_48x", "dist", "xstep", "W29 · F15 · 24 V (TBC) · X drive", "pTBC", (1, (790 - 595) / 320), (1, 55 / 80),
     pts=[(1260, 790), (1260, 910), (2095, 910), (2095, 200)], at=(2095, 700), vlabel=True)
edge("e_feed", "dist", "busbar", "W24 · 10 separately fused row feeds · candidate 5 A/row, not released", "p24",
     (1, (820 - 595) / 320), (0, (930 - 150) / 1010), pts=[(1245, 820), (1245, 930)], at=(1700, 930))
edge("e_rs1", "dist", "lc10", "W25 · CAN_H / CAN_L / GND · LANECTRL R1 has no 12 V input (F14 unused)", "data",
     (1, (850 - 595) / 320), (0.5, 1), pts=[(1230, 850), (1230, 945), (2130, 945), (2130, 1180), (2365, 1180)], at=(1700, 945))
edge("e_printer", "sbc", "printer", "W19 · marker data, TBC", "dataTBC", (0.94, 0), (1, 0.5),
     pts=[(1179, 80), (2110, 80), (2110, 827)], at=(1650, 80))

# IOCTRL to doors (right side, abs y 1010…1090)
edge("e_latch", "ioctrl", "latches", "W20 / W21 · switched 12 V · RO1–4", "p12", (1, 35 / 150), (0, 0.5), pts=[(1360, 1010), (1360, 1040)], lx=0.3)
edge("e_doorsens", "doorsens", "ioctrl", "W23 · 5 direct sensor runs", "data", (0, 0.5), (1, 75 / 150), pts=[(1330, 1130), (1330, 1050)], lx=-0.3)
edge("e_dooract", "ioctrl", "dooract", "W28 · excluded", "excl", (1, 115 / 150), (0, 0.5), pts=[(1300, 1090), (1300, 1212)], lx=0.3)

# NFC RF link
edge("e_nfc_rf", "nfc_antenna", "nfc_pcb", "RF", "rf", (1, 0.5), (0, 62 / 170), end="none")

# ------------------------------------------------------------------ legend / references
text("legend_hdr", 40, 1311, 120, 20, "<b>Legend</b>", fs=12, color=INK)
legend_line("lg_p", 120, 1320, 170, "p24", "DC power · 24 V / derived 12 V")
legend_line("lg_m", 450, 1320, 500, "mot", "AC / motor phases")
legend_line("lg_d", 700, 1320, 750, "data", "data / control")
legend_line("lg_t", 900, 1320, 950, "dataTBC", "proposed / unconfirmed / optional")
text("lg_box", 1230, 1311, 700, 20, f'<font color="{AMBER}">▭ dashed amber box</font> = excluded / not selected · '
     '<font color="#FF0000"><b>CONN · PCB · MTR</b></font> = category tags', fs=12, color=INK)
text("tables_ref", 1950, 1302, 980, 45,
     "Parts and mounting references: ADHERENT_Electrical_Tables.xlsx (same references as this diagram). "
     "TBC = selection or dimensions pending. Provisional STEP models are placement references only.", fs=11,
     extra="strokeColor=#D4D9E0;fillColor=#F7EEDC;spacingLeft=8;spacingTop=4;")

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<mxfile host="Electron" agent="Blackocean Technologies">'
       '<diagram id="esl-wiring" name="Electrical System Level Wiring Diagram">'
       '<mxGraphModel dx="2000" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
       'fold="1" page="1" pageScale="1" pageWidth="2980" pageHeight="1370" math="0" shadow="0"><root>'
       '<mxCell id="0" /><mxCell id="1" parent="0" />' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
open(OUT, "w", encoding="utf-8").write(xml)
print("cells", len(cells), "->", OUT)
