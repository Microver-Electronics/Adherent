# Adherent APDU project brain

Last updated: 2026-09-24

Project: Adherent360 APDU / AVM pharmaceutical vending machine.
Working repository: https://github.com/Microver-Electronics/Adherent
Electrical design company: Blackocean Technologies.

This file records project decisions and working assumptions. A diagram label or a candidate part is not proof of datasheet compatibility. Distinguish confirmed requirements from proposed implementation details when continuing the design.

## Current deliverables

- Project landing page: [README](README.md), with current document links, diagram preview, controller roles and implementation status. Banner source: `docs/assets/adherent-banner.svg`.
- Current system diagram: [Electrical System Level Wiring Diagram R27](SYS/ADHERENT_System_Wiring_Diagram.drawio).
- Diagram preview: [R27 PNG](SYS/ADHERENT_System_Wiring_Diagram.png).
- Electrical workbook: [APDU Electrical Tables R27](SYS/ADHERENT_Electrical_Tables.xlsx). BOM, interfaces, cables, protection, power model and open engineering items.
- Presentation: [Design Review Questions R27](SYS/ADHERENT_Design_Review_Snapshot.pptx). Aligned with the current diagram and workbook.
- Component/part-number register: [System Diagram Components R27](SYS/ADHERENT_Electrical_Tables.xlsx), 82 rows including interfaces and explicit external/options.
- [Review findings](SYS/ADHERENT_Project_Review.md).
- Superseded SYS revisions and the older unversioned presentation were removed from the working folder; recover them from Git history when needed.
- Mechanical model handoff folder: [Board STEP Models](MEC/Board_STEP_Models/README.md).
- LANECTRL front metal bracket reference: [LANE DRAWING SPACE FOR UMIT.DWG](MEC/01_CAD_MODELS/LANE%20DRAWING%20SPACE%20FOR%20UMIT.DWG). User confirms the bracket is being made to this drawing; PCB fit and clearances have not yet been checked.
- Hardware folders: `HW/HW_ADHERENT_SYSCTRL_R1`, `HW/HW_ADHERENT_MAINCTRL_R1`, `HW/HW_ADHERENT_LANECTRL_R1`, `HW/HW_ADHERENT_IOCTRL_R1`.
- Rear-panel Ethernet connector J2: **McMaster-Carr 1422N13**, quantity 1 per system, replaces the previous Neutrik candidate. Shielded Cat5e RJ45 female/female, screw-on mounting, black plastic housing; 0.95 in (24.13 mm) panel cutout and 0.14 in mounting holes, mounting fasteners included. [Product](https://www.mcmaster.com/product/1422N13), [supplier specifications](https://www.mcmaster.com/products/data-transmission-couplers/).

## Confirmed decisions

- Ten rows, seven lanes per row: 70 conveyor channels.
- One conveyor motor per lane. One momentary button and one LED per lane.
- Only one AC/DC PSU remains: **PSU1, Mean Well RSP-500-24**, rated 24 V / 21 A / 504 W. Recalculate the combined power budget before treating its capacity as sufficient.
- The separate 12 V and 48 V PSUs were removed.
- **24 V to 12 V conversion is on the custom SYSCTRL PCB.** There is no separate cabinet DC/DC module.
- The customer requires CAN for the custom-board network.
- IOCTRL is an explicit exception: **RS485 to MAINCTRL**. Its Ethernet and wireless functions are unused.
- No Ethernet switch in the system. Provide a hardwired Ethernet connection to the site network.
- The iPad is external and uses the customer's app or a browser; it is not integrated into the cabinet.
- LANEPANEL was merged into LANECTRL. There is no separate LANEPANEL PCB.
- Cellular connectivity and UPS/battery backup were rejected during the meeting as unnecessary.
- Camera/OCR is outside the current baseline and remains a customer question.
- The customer requested no emergency stop. This is a recorded scope decision, not a completed machine safety assessment.

## NFC antenna selection

- User-selected antenna: **Molex 1462362151**, planning quantity 1 per machine.
- Manufacturer: 13.56 MHz, 2.40 uH, 15 x 15 x 0.27 mm, adhesive mount, 102 mm cable.
- [Molex](https://www.molex.com/en-us/products/part-detail/1462362151), [selected DigiKey listing](https://www.digikey.com/en/products/detail/molex/1462362151/15204370).
- This is an antenna, not a complete reader. Reader/front-end, matching, termination, host interface, board allocation, mounting and supply remain TBC under O16. Payment-terminal functionality is not selected.
- Antenna cable is included in the component; do not order it again as a generic patch cable. Any reader power/host harness is still undefined.

## Boards

### MAINCTRL — off the shelf, quantity 1

- **MYIR MYD-YF13X**, STM32MP135-based Linux development board.
- Replaces the previously considered MYD-LT527-SX; do not reintroduce that product or its price/specifications.
- Supervisory application, site/server communication, CAN master and RS485 master.
- Base-board supply requirement recorded from MYIR documentation: 12 V / 2 A. Feed from the SYSCTRL-derived 12 V rail, not directly from 24 V.
- Exact populated order code, Ethernet capabilities, BSP and radio accessories require verification against the purchased variant. Some older deliverables contain unverified Gigabit claims.
- Official product page: https://www.myirtech.com/list.asp?id=727
- Product document: https://www.myirtech.com/download/STM32/MYD-YF13X.pdf

### IOCTRL — off the shelf, quantity 1

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
- STM32 machine controller; combines the former motion-control and auxiliary-I/O functions. The current IOCTRL name refers to the separate Waveshare relay/input module.
- Gantry drive control interfaces, brake control, basket servo control, optical sensors, labeling stepper drivers and auxiliary outputs.
- **Onboard 24→12 V buck supplies the existing 12 V loads**, including local circuitry, MAINCTRL, LANECTRL logic and latch contacts.
- Buck topology, MPN, current capacity, protection, thermal design and sequencing are not selected/validated.
- Local servo voltage conversion remains necessary; DS3218 is not a direct 12 V or 24 V load.
- TMC5160 and TMC2209 are proposed labeling stepper drivers, not finalized selections.

### LANECTRL — custom PCB, quantity 10

- `HW_ADHERENT_LANECTRL_R1` / `FW_ADHERENT_LANECTRL_R1`.
- One board per row: seven motor H-bridges, seven feedback inputs, seven buttons and seven LEDs.
- Includes the former LANEPANEL functions. Two custom PCB designs total: SYSCTRL and LANECTRL; 11 custom assemblies total.
- R27 retains 24 V for conveyor motors and SYSCTRL-derived 12 V for lane logic through the CAN harness.
- Current button candidate: Omron B3F-4055, momentary. Current LED candidate: Kingbright WP7113ID.
- Driver/TVS choices, connector current capacity, button placement and bezel alignment still need detailed design verification.
- Diagram assumes front-of-row mounting; confirm mechanically.

## Latest SYSCTRL representation correction

- SYSCTRL and the former lower distribution box are one PCB assembly. The lower area represents SYSCTRL power connectors, not a separate distribution assembly.
- Show one onboard 24 V-to-12 V SMPS block. PSU1 supplies 24 V to SYSCTRL; external loads connect through SYSCTRL.
- Removed the misleading external W04/W06/W07 loop arrows between those two boxes. Their previous external-harness descriptions must not be used as released wiring.
- F1–F18 remain branch references; the previous 17-DIN-holder placement is not confirmed by this correction. Final protection implementation and connector pinouts remain TBC.
- Electrical tables and component register now reflect this correction. W04/W06/W07 have zero external-harness quantity; DIN-holder procurement is withdrawn. Presentation remains an earlier review snapshot and must be refreshed before presenting the current topology/NFC scope.

## R27 power routing and identifiers

- W03: PSU1 24 V output directly to SYSCTRL system input; connector MPN/pins TBC.
- W06 internalized: F11 is an internal SYSCTRL motor-rail protection reference, not an external jumper.
- W07 internalized: F12 is the onboard SMPS input branch; no separate external input cable.
- W04 internalized: onboard SMPS output feeds internal SYSCTRL 12 V routing; no separate distribution rail assembly.
- W05 / F13: derived 12 V to MAINCTRL.
- F14: lane-logic protection on SYSCTRL; 12 V passes into the CAN/lane harness.
- W24 / F1–F10: 24 V row-motor feeders.
- W29 / F15 and W30 / F16: proposed 24 V gantry drive feeds, pending supplier confirmation.
- W34 / F17: 24 V IOCTRL module power.
- W35 / F18: derived 12 V feed to IOCTRL relay contacts.
- W33: MAINCTRL–IOCTRL RS485.
- W02, W31 and W32 retired with the removed PSUs. W14 and W22 retired with the cancelled intermediate sensor trunks.
- W15: six direct gantry sensor runs to SYSCTRL. W23: five direct door sensor runs to IOCTRL. No junction boxes.
- W36 status light, W37 PE bonding, W38 site-supplied Ethernet and W39 unresolved marker supply are explicitly scheduled.
- Fuse ratings, wire sizes, connector loading, DC/DC losses and simultaneous motor loads need recalculation. Older spreadsheet currents are estimates, not verified sizing.

## Communication

- Proposed CAN backbone: MAINCTRL → SYSCTRL → LANECTRL-10 through LANECTRL-01.
- Diagram baseline: CAN 2.0B, 500 kbit/s, termination at MAINCTRL and LANECTRL-01. Validate implementation and cable routing.
- Separate RS485 link: MAINCTRL ↔ IOCTRL.
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
- Mechanical BOM: `MEC/ADHERENT_Mechanical_BOM.xlsx`.
- Conveyor reference: `SYS/Conveyor belt(CB002-24V-573mm).pdf`.
- Test-rig reference: `SYS/APDU-Test-Rig-Drawing-Set-BOT-TR-001-RevD.pdf`; this is not the production electrical design.
- Approximate CAD envelope used previously for cable estimates: 855 × 890 × 1905 mm. Treat derived routing lengths as estimates.

### Provisional reconstructed board models

- IOCTRL: `MEC/Board_STEP_Models/IOCTRL_Waveshare_ESP32-S3-ETH-8DI-8RO/IOCTRL_Provisional_Placement_R1.step`.
  - Nominal 175 × 90 × 40 mm envelope from the user image.
  - Reference image is the **PoE variant**; compatibility with the selected non-PoE product is unverified.
  - Slots and connector geometry are estimated; DIN clip and antenna are omitted.
- MAINCTRL: `MEC/Board_STEP_Models/MAINCTRL_MYIR_MYD-YF13X/MAINCTRL_MYD-YF13X_Provisional_Placement_R1.step`.
  - Documented PCB outline 137.29 × 105 mm.
  - PCB thickness, hole positions/diameters, connector heights and component envelopes are estimates.
  - Simplified top- and bottom-side components are included.
- Both models passed solid validity and STEP reimport checks. **Geometry validity does not validate dimensional accuracy.** Read each folder's `MODEL_NOTES_R1.md`; use for preliminary placement only, not fabrication.
- No manufacturer IOCTRL STEP download was found in the checked official resources. Manufacturer request draft is saved locally and has not been sent.
- Custom board STEP models await actual PCB layouts.

## Documentation and harness conventions

- Use Blackocean Technologies branding; no Melis Electronics branding in new deliverables.
- Avoid personal names in customer-facing deliverables. Use “the team”, “the mechanical team” or “the customer”.
- Document title: **Electrical System Level Wiring Diagram**.
- Keep only current deliverable revisions under `SYS`. Recover older revisions from Git history. No RAR bundles.
- Keep diagram blocks and orthogonal routes spacious, labels legible and arrows clear.
- Put a **red, bold category tag in the upper-left corner inside each applicable component box**: `CONN` for connectors, `PCB` for controller boards, `MTR` for motors. Keep tags attached to their boxes and reserve enough space so they do not overlap content.
- R27 category tags cover 4 connector/interface boxes (RJ45 panel adapter, optional antenna bulkhead AC inlet and SYSCTRL power connectors), 13 controller-board boxes, and 15 motor/assembly boxes (five individual motor groups and ten seven-conveyor row groups). Counts refer to diagram boxes, not physical component quantities.
- Category tags do not replace existing J/W/F identifiers or controller names. Onboard converter sections are not separate PCBs; excluded door actuators remain undefined and are not tagged as selected motors.
- Edit the `.drawio` source and regenerate its PNG together. README embeds the current PNG from `SYS`.
- Bold red arrows carry power only. Data/control paths are blue. Clearly distinguish proposed connections.
- Keep tables in Excel rather than in the diagram. No revision-history or option-item blocks in the diagram.
- English presentation, concise text and useful visuals. Retain cellular/UPS topics as closed meeting decisions in red.
- Custom PCB I/O connector preference: Molex Micro-Fit 3.0. Purchased boards retain their native connectors; do not assign Micro-Fit MPNs to incompatible COTS sockets.
- Preferred harness cable: four-conductor 22 AWG, red/black/yellow/green, where electrically suitable. Use appropriately rated exceptions for mains and higher-current circuits.
- No junction boxes. Sensors run directly to controller boards. Use crimped mating connectors on custom boards and the native terminals/connectors on COTS hardware.
- Naming: `HW_ADHERENT_XXX_RY`, `FW_ADHERENT_XXX_RY`, `WR_ADHERENT_AAA_TO_BBB_RY`.
- Preserve custom PCB quantities unless the user explicitly changes the architecture.
- Do not send messages or files to third parties without explicit authorization.

## Outstanding engineering work

1. R27 aligns workbook, component register, presentation and diagram. Resolve OpenItems O01-O16 before engineering release; document consistency does not close physical validation.
2. Size the SYSCTRL 24→12 V converter and review total PSU1 capacity, protection, cable/connector current ratings and power sequencing.
3. Obtain exact Emtech driver/brake documentation; confirm 24 V performance, wiring and driver packaging.
4. Confirm latch current, duty cycle, fail behavior and suppression; define any door actuators separately.
5. Confirm conveyor stall/load current and feedback signal type. Do not equate that signal with verified product dispensing without evidence.
6. Confirm MAINCTRL populated variant, connector dimensions and network specifications.
7. Obtain manufacturer mechanical CAD or verify reconstructed models against hardware.
8. Finalize PCB mounting, harness routing, lengths and service clearances with the mechanical team.
9. Resolve remaining customer questions: camera/OCR, illumination, iPad pairing, NFC/card reader and label marker.

## R27 planning checks

- Known PSU peak subtotal: 268.96 W, excluding four unresolved load-current entries (including NFC reader) and marker power. Not a complete capacity approval.
- Seven-conveyor row case: 14.05 A versus candidate 5 A protection; concurrency must be constrained and tested.
- 39 cable IDs, 28 required external types, five missing route lengths; 109.5 m is only the known routing subtotal.
- 18 branch-protection references; physical placement and holder quantities need reconciliation with the merged SYSCTRL connector architecture.
- FW/SW folders contain scope descriptions only, no implemented firmware/application builds.
- HW contains four reserved board folders; no production PCB designs have been added. README must distinguish planned functions from implemented or validated capabilities.

## Local build references

- `.work/r26_diagram.py`: creates R26 from R25; restore the R25 input from Git history before rerunning.
- `.work/r25_diagram.py`: creates R25 from R24; restore the R24 input from Git history before rerunning.
- `.work/r24/`: presentation edit and validation scripts/artifacts from the R24 update.
- Each provisional board-model folder contains `build_ocp_R1.py` and validation output.
- CAD dependencies were installed in `.work/cad-deps`. Direct OpenCascade imports worked; full CadQuery import stalled in VTK. Some dependency access required elevated execution in this environment.
- Render diagrams using the installed draw.io CLI and inspect the PNG before delivery. Check both content and geometry; a successful export alone does not prove correctness.

## Mechanical model location

- Board STEP models are maintained in `MEC/Board_STEP_Models`, alongside machine CAD. Use MAINCTRL, SYSCTRL, LANECTRL and IOCTRL consistently across model folders and system documents.

## Customer handoff and naming — 2026-09-25 (supersedes earlier workbook instructions)

- The customer needs one short worksheet, not detailed electrical schedules. `SYS/ADHERENT_Electrical_Tables.xlsx` is the only current electrical parts workbook: 32 grouped entries with diagram reference, component, part number, quantity, location, clickable source and STEP/drawing links, and rough dimensions in mm.
- Removed the duplicate component workbook. Previous engineering schedules remain in Git history at `aef502b`; preserve engineering decisions recorded above until resolved.
- Current document names use `ADHERENT_<Purpose>` without R27 suffixes. The editable system diagram and PNG share `ADHERENT_System_Wiring_Diagram`. The earlier presentation is explicitly `ADHERENT_Design_Review_Snapshot.pptx`.
- Mechanical BOM is `MEC/ADHERENT_Mechanical_BOM.xlsx`. Board models are under `MEC/Board_STEP_Models`; supplier part numbers and original supplied CAD/drawing names remain traceable.
- Canonical board roles: MAINCTRL, SYSCTRL, LANECTRL, IOCTRL. HW/FW board revision identifiers keep R1 because it identifies the board design rather than the documentation revision.
- Match the visible diagram references to the customer sheet. CONVEYOR-01…10 are row groups of seven; LANECTRL-01…10 are individual row-controller instances. X-GB and JAW-SENS remain subcomponents of their labeled motor blocks.
- No independent distribution box. BUCK12 and SYSCTRL-PWR are internal SYSCTRL functions. No junction boxes.
- Manufacturer/source dimensions and provisional model envelopes must remain distinguished. Missing selections, drawings or dimensions stay TBC. Do not invent mounting dimensions.
- Commit and push completed changes incrementally, as requested by the user.

## Excel compatibility fix — 2026-09-25

- Fixed duplicate `pageMargins` in `ADHERENT_Electrical_Tables.xlsx`, introduced by the print-settings patch. Cell contents, styles, 27 hyperlinks and one-sheet layout are unchanged.
- Both released workbooks passed read-only, normal Microsoft Excel opening. Electrical sheet exported from Excel to exactly one A3 landscape PDF page and was visually checked.
- Published 14-slide presentation and both tracked historical PPTX files opened in Microsoft PowerPoint.
- 72 tracked files passed applicable ZIP CRC, XML/package relationship, PDF parsing, image decoding, JSON or file-signature checks. STEP geometry and DWG mechanical fit are separate from these file-format checks.
- Future workbook checks must reject duplicate singleton worksheet records and include normal Microsoft Excel opening; a Python reader alone does not prove Excel compatibility.

### Expanded repository check after incoming LANECTRL commits

- Integrated upstream `7fbfe32` and `587bbe7` before pushing the Excel fix; no incoming hardware files were discarded.
- Repeated applicable structural checks across all 225 tracked files. Both additional LANECTRL BOM workbooks passed normal read-only Microsoft Excel opening, bringing the native-tested workbook count to four.
- LANECTRL Altium schematics, PCB layout, libraries, BOMs and exported models are now present. Earlier statements that all HW folders were empty no longer describe LANECTRL. Presence and file integrity do not establish production release or resolve electrical design holds.
- Altium binary container signatures and tracked ZIP checks passed. Native Altium editing/compilation and DWG geometric validation were not performed.
- All nine tracked STEP/STP files imported successfully into OpenCascade and produced non-null shapes. Full topology, mounting dimensions and physical fit are not certified by this import check.
