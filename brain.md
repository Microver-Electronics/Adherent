# Adherent APDU project brain

Last updated: 2026-09-24

Project: Adherent360 APDU / AVM pharmaceutical vending machine.
Working repository: https://github.com/Microver-Electronics/Adherent
Electrical design company: Blackocean Technologies.

This file records project decisions and working assumptions. A diagram label or a candidate part is not proof of datasheet compatibility. Distinguish confirmed requirements from proposed implementation details when continuing the design.

## Current deliverables

- Current system diagram: [Electrical System Level Wiring Diagram R26](SYS/Electrical_System_Level_Wiring_Diagram_R26.drawio).
- Diagram preview: [R26 PNG](SYS/Electrical_System_Level_Wiring_Diagram_R26.png).
- Latest electrical workbook: [APDU Electrical Tables R23](SYS/APDU_Electrical_Tables_R23.xlsx). **Historical: not aligned with the R25/R26 power changes.**
- Latest versioned presentation: [Design Review Questions R24](SYS/APDU_Design_Review_Questions_R24.pptx). Records cellular and UPS rejection in red; **not aligned with R25/R26 power changes**.
- The unversioned `SYS/APDU_Design_Review_Questions.pptx` is an older deck; do not assume it is current.
- Mechanical model handoff folder: [Board STEP Models](SYS/Board_STEP_Models/README.md).

## Confirmed decisions

- Ten rows, seven lanes per row: 70 conveyor channels.
- One conveyor motor per lane. One momentary button and one LED per lane.
- Only one AC/DC PSU remains: **PSU1, Mean Well RSP-500-24**, nominal 24 V / 500 W. Recalculate the combined power budget before treating its capacity as sufficient.
- The separate 12 V and 48 V PSUs were removed.
- **24 V to 12 V conversion is on the custom SYSCTRL PCB.** There is no separate cabinet DC/DC module.
- The customer requires CAN for the custom-board network.
- DOORIO is an explicit exception: **RS485 to MAINCTRL**. Its Ethernet and wireless functions are unused.
- No Ethernet switch in the system. Provide a hardwired Ethernet connection to the site network.
- The iPad is external and uses the customer's app or a browser; it is not integrated into the cabinet.
- LANEPANEL was merged into LANECTRL. There is no separate LANEPANEL PCB.
- Cellular connectivity and UPS/battery backup were rejected during the meeting as unnecessary.
- Camera/OCR is outside the current baseline and remains a customer question.
- The customer requested no emergency stop. This is a recorded scope decision, not a completed machine safety assessment.

## Boards

### MAINCTRL — off the shelf, quantity 1

- **MYIR MYD-YF13X**, STM32MP135-based Linux development board.
- Replaces the previously considered MYD-LT527-SX; do not reintroduce that product or its price/specifications.
- Supervisory application, site/server communication, CAN master and RS485 master.
- Base-board supply requirement recorded from MYIR documentation: 12 V / 2 A. Feed from the SYSCTRL-derived 12 V rail, not directly from 24 V.
- Exact populated order code, Ethernet capabilities, BSP and radio accessories require verification against the purchased variant. Some older deliverables contain unverified Gigabit claims.
- Official product page: https://www.myirtech.com/list.asp?id=727
- Product document: https://www.myirtech.com/download/STM32/MYD-YF13X.pdf

### DOORIO — off the shelf, quantity 1

- **Waveshare ESP32-S3-ETH-8DI-8RO**, RS485 version with standard Ethernet port. Do not substitute the CAN `-C` or PoE version without a decision.
- Eight relay outputs and eight isolated digital inputs.
- Module input range 7–36 V; current design powers the module from 24 V.
- RS485 connection to MYD-YF13X. Modbus RTU firmware is planned; do not assume the factory firmware meets the required protocol and behavior without testing.
- RO1–RO4 switch four 12 V electromechanical latches: main, retrieval, return and table doors.
- Relay COM receives **separate 12 V derived on SYSCTRL**. The module's 24 V input does not supply or convert the relay-contact voltage.
- DI1–DI5 are allocated to door sensors in the diagram. RO5–RO8 remain reserved for undefined actuator requirements.
- Ethernet, Wi-Fi and BLE unused.
- Official documentation: https://www.waveshare.com/wiki/ESP32-S3-ETH-8DI-8RO

### SYSCTRL — custom PCB, quantity 1

- `HW_ADHERENT_SYSCTRL_R1` / `FW_ADHERENT_SYSCTRL_R1`.
- STM32 machine controller; combines the former MOTIONCTRL and IOCTRL functions.
- Gantry drive control interfaces, brake control, basket servo control, optical sensors, labeling stepper drivers and auxiliary outputs.
- **Onboard 24→12 V buck supplies the existing 12 V loads**, including local circuitry, MAINCTRL, LANECTRL logic and latch contacts.
- Buck topology, MPN, current capacity, protection, thermal design and sequencing are not selected/validated.
- Local servo voltage conversion remains necessary; DS3218 is not a direct 12 V or 24 V load.
- TMC5160 and TMC2209 are proposed labeling stepper drivers, not finalized selections.

### LANECTRL — custom PCB, quantity 10

- `HW_ADHERENT_LANECTRL_R1` / `FW_ADHERENT_LANECTRL_R1`.
- One board per row: seven motor H-bridges, seven feedback inputs, seven buttons and seven LEDs.
- Includes the former LANEPANEL functions. Two custom PCB designs total: SYSCTRL and LANECTRL; 11 custom assemblies total.
- R26 retains 24 V for conveyor motors and SYSCTRL-derived 12 V for lane logic through the CAN harness.
- Current button candidate: Omron B3F-4055, momentary. Current LED candidate: Kingbright WP7113ID.
- Driver/TVS choices, connector current capacity, button placement and bezel alignment still need detailed design verification.
- Diagram assumes front-of-row mounting; confirm mechanically.

## R26 power routing and identifiers

- W03: PSU1 24 V output to fused distribution.
- W06 / F11: 24 V motor supply to SYSCTRL.
- W07 / F12: 24 V input to the SYSCTRL buck section.
- W04: SYSCTRL 12 V output back to a **separate** 12 V distribution rail.
- W05 / F13: derived 12 V to MAINCTRL.
- F14: lane-logic protection on SYSCTRL; 12 V passes into the CAN/lane harness.
- W24 / F1–F10: 24 V row-motor feeders.
- W29 / F15 and W30 / F16: proposed 24 V gantry drive feeds, pending supplier confirmation.
- W34 / F17: 24 V DOORIO module power.
- W35 / F18: derived 12 V feed to DOORIO relay contacts; provisional new references.
- W33: MAINCTRL–DOORIO RS485.
- W02, W31 and W32 retired with the removed PSUs.
- Fuse ratings, wire sizes, connector loading, DC/DC losses and simultaneous motor loads need recalculation. Older spreadsheet currents are estimates, not verified sizing.

## Communication

- Proposed CAN backbone: MAINCTRL → SYSCTRL → LANECTRL-10 through LANECTRL-01.
- Diagram baseline: CAN 2.0B, 500 kbit/s, termination at MAINCTRL and LANECTRL-01. Validate implementation and cable routing.
- Separate RS485 link: MAINCTRL ↔ DOORIO.
- Site Ethernet connection serves the external iPad/app and server communication. Optional Wi-Fi/BLE arrangements remain distinct from rejected cellular connectivity.

## Motors and mechanisms

Current inventory is **75 motors across five model/part-reference groups**, excluding undefined door actuators:

- Conveyor motors: 70 brushed DC geared motors, one per lane. **CB002-24V-573mm is the conveyor assembly model**, not a confirmed standalone motor MPN. External H-bridges on LANECTRL.
- Gantry X/Z: 2 × **Emtech 57BYG250-76**, NEMA23 closed-loop steppers. Mechanical BOM states brake and driver included. **Whether drivers are integrated into the motors or separate modules is unconfirmed.** X includes a 3:1 gearbox.
- Basket tilt: 1 × **Miuzei DS3218** servo; drive electronics are internal. Exact variant and supply range need confirmation before final regulator selection.
- Chuck rotation: 1 × NEMA23 stepper; **6627T113** is the recorded CAD/catalog reference. Manufacturer MPN needs confirmation. External SYSCTRL driver proposed.
- Chuck jaws: 1 × NEMA11 stepper; **6627T357** is the recorded CAD/catalog reference. Manufacturer MPN needs confirmation. External SYSCTRL driver proposed.

Do not assume the Emtech drive supports 24 V or any specific STEP/DIR voltage until its exact driver datasheet is available. Earlier drawings overstated integrated-driver status and signal compatibility.

The four electromagnetic latches are not counted as motors. Door actuator models and quantities are undefined; the table-door actuator was excluded from the earlier scope.

## Mechanical inputs and STEP models

- Machine CAD: `MEC/AVM-FRAME-MAINASSEMBLY_V4.STEP`.
- Mechanical BOM: `SYS/VENDING MACHINE GANTRY BILL OF MATERIALS - OFF THE SHELF COMPONENTS.xlsx`.
- Conveyor reference: `SYS/Conveyor belt(CB002-24V-573mm).pdf`.
- Test-rig reference: `SYS/APDU-Test-Rig-Drawing-Set-BOT-TR-001-RevD.pdf`; this is not the production electrical design.
- Approximate CAD envelope used previously for cable estimates: 855 × 890 × 1905 mm. Treat derived routing lengths as estimates.

### Provisional reconstructed board models

- DOORIO: `SYS/Board_STEP_Models/DOORIO_Waveshare_ESP32-S3-ETH-8DI-8RO/DOORIO_Provisional_Placement_R1.step`.
  - Nominal 175 × 90 × 40 mm envelope from the user image.
  - Reference image is the **PoE variant**; compatibility with the selected non-PoE product is unverified.
  - Slots and connector geometry are estimated; DIN clip and antenna are omitted.
- MAINCTRL: `SYS/Board_STEP_Models/MAINCTRL_MYIR_MYD-YF13X/MAINCTRL_MYD-YF13X_Provisional_Placement_R1.step`.
  - Documented PCB outline 137.29 × 105 mm.
  - PCB thickness, hole positions/diameters, connector heights and component envelopes are estimates.
  - Simplified top- and bottom-side components are included.
- Both models passed solid validity and STEP reimport checks. **Geometry validity does not validate dimensional accuracy.** Read each folder's `MODEL_NOTES_R1.md`; use for preliminary placement only, not fabrication.
- No manufacturer DOORIO STEP download was found in the checked official resources. Manufacturer request draft is saved locally and has not been sent.
- Custom board STEP models await actual PCB layouts.

## Documentation and harness conventions

- Use Blackocean Technologies branding; no Melis Electronics branding in new deliverables.
- Avoid personal names in customer-facing deliverables. Use “the team”, “the mechanical team” or “the customer”.
- Document title: **Electrical System Level Wiring Diagram**.
- Keep deliverables under `SYS`. Preserve prior revisions as separate R1, R2, … files.
- Keep diagram blocks and orthogonal routes spacious, labels legible and arrows clear.
- Bold red arrows carry power only. Data/control paths are blue. Clearly distinguish proposed connections.
- Keep tables in Excel rather than in the diagram. No revision-history or option-item blocks in the diagram.
- English presentation, concise text and useful visuals. Retain cellular/UPS topics as closed meeting decisions in red.
- Custom PCB I/O connector preference: Molex Micro-Fit 3.0. Purchased boards retain their native connectors; do not assign Micro-Fit MPNs to incompatible COTS sockets.
- Preferred harness cable: four-conductor 22 AWG, red/black/yellow/green, where electrically suitable. Use appropriately rated exceptions for mains and higher-current circuits.
- Board ends use crimps/connectors; junction-box ends may use ferrules and WAGO terminals.
- Naming: `HW_ADHERENT_XXX_RY`, `FW_ADHERENT_XXX_RY`, `WR_ADHERENT_AAA_TO_BBB_RY`.
- Preserve custom PCB quantities unless the user explicitly changes the architecture.
- Do not send messages or files to third parties without explicit authorization.

## Outstanding engineering work

1. Align the Excel workbook and presentation with R26; they still contain superseded supply assumptions.
2. Size the SYSCTRL 24→12 V converter and review total PSU1 capacity, protection, cable/connector current ratings and power sequencing.
3. Obtain exact Emtech driver/brake documentation; confirm 24 V performance, wiring and driver packaging.
4. Confirm latch current, duty cycle, fail behavior and suppression; define any door actuators separately.
5. Confirm conveyor stall/load current and feedback signal type. Do not equate that signal with verified product dispensing without evidence.
6. Confirm MAINCTRL populated variant, connector dimensions and network specifications.
7. Obtain manufacturer mechanical CAD or verify reconstructed models against hardware.
8. Finalize PCB mounting, harness routing, lengths and service clearances with the mechanical team.
9. Resolve remaining customer questions: camera/OCR, illumination, iPad pairing, NFC/card reader and label marker.

## Local build references

- `.work/r26_diagram.py`: creates R26 from R25.
- `.work/r25_diagram.py`: creates R25 from R24.
- `.work/r24/`: presentation edit and validation scripts/artifacts from the R24 update.
- Each provisional board-model folder contains `build_ocp_R1.py` and validation output.
- CAD dependencies were installed in `.work/cad-deps`. Direct OpenCascade imports worked; full CadQuery import stalled in VTK. Some dependency access required elevated execution in this environment.
- Render diagrams using the installed draw.io CLI and inspect the PNG before delivery. Check both content and geometry; a successful export alone does not prove correctness.
