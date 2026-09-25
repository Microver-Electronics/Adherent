# Adherent APDU project brain

Last updated: 2026-09-25

Project: Adherent360 APDU / AVM pharmaceutical vending machine.
Working repository: https://github.com/Microver-Electronics/Adherent
Electrical design company: Blackocean Technologies.

This file records project decisions and working assumptions. A diagram label or a candidate part is not proof of datasheet compatibility. Distinguish confirmed requirements from proposed implementation details when continuing the design.

## Current deliverables

- Project landing page: [README](README.md), with current document links, diagram preview, controller roles and implementation status. Banner source: `docs/assets/adherent-banner.svg`.
- Current system diagram: [Electrical System Level Wiring Diagram R27](SYS/ADHERENT_System_Wiring_Diagram.drawio).
- Diagram preview: [R27 PNG](SYS/ADHERENT_System_Wiring_Diagram.png).
- Electrical workbook: [APDU Electrical Tables R27](SYS/ADHERENT_Electrical_Tables.xlsx). BOM, interfaces, cables, protection, power model and open engineering items.
- Presentation: [Design Review Questions R27](SYS/ADHERENT_Design_Review.pptx). Aligned with the current diagram and workbook.
- Component/part-number register: [System Diagram Components R27](SYS/ADHERENT_Electrical_Tables.xlsx), 82 rows including interfaces and explicit external/options.
- [Review findings](SYS/ADHERENT_Project_Review.md).
- Superseded SYS revisions and the older unversioned presentation were removed from the working folder; recover them from Git history when needed.
- Mechanical model handoff folder: [Board STEP Models](MEC/Board_STEP_Models/README.md).
- LANECTRL front metal bracket reference: [LANE DRAWING SPACE FOR UMIT.DWG](MEC/01_CAD_MODELS/Draw%C4%B1ng/LANE%20DRAWING%20SPACE%20FOR%20UMIT.DWG). User confirms the bracket is being made to this drawing; PCB fit and clearances have not yet been checked.
- Hardware folders: `HW/HW_ADHERENT_SYSCTRL_R1`, `HW/HW_ADHERENT_MAINCTRL_R1`, `HW/HW_ADHERENT_LANECTRL_R1`, `HW/HW_ADHERENT_IOCTRL_R1`.
- Rear-panel Ethernet connector J2: **McMaster-Carr 1422N13**, quantity 1 per system, replaces the previous Neutrik candidate. Shielded Cat5e RJ45 female/female, screw-on mounting, black plastic housing; 0.95 in (24.13 mm) panel cutout and 0.14 in mounting holes, mounting fasteners included. [Product](https://www.mcmaster.com/product/1422N13), [supplier specifications](https://www.mcmaster.com/products/data-transmission-couplers/).

## Confirmed decisions

- Ten rows, seven lanes per row: 70 conveyor channels.
- One conveyor motor per lane. One momentary button and one LED per lane.
- Only one AC/DC PSU remains: **PSU1, Mean Well RSP-500-24**, rated 24 V / 21 A / 504 W. Recalculate the combined power budget before treating its capacity as sufficient.
- The separate 12 V and 48 V PSUs were removed.
- **24 V to 12 V conversion is on the custom SYSCTRL PCB.** There is no separate cabinet DC/DC module.
- The customer requires CAN for the custom-board network.
- IOCTRL is an explicit exception: **both IOCTRL modules (IOCTRL-01, IOCTRL-02) connect to MAINCTRL over RS485**. Their Ethernet and wireless functions are unused.
- **IOCTRL quantity is 2 per system** (customer/user decision, 2026-09-25). Supersedes the earlier quantity of 1.
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

### IOCTRL — off the shelf, quantity 2

- **Two identical modules per system: IOCTRL-01 and IOCTRL-02** (decision 2026-09-25; previously 1). Same product and variant for both.
- Combined capacity: 16 relay outputs and 16 isolated digital inputs.

- **Waveshare ESP32-S3-ETH-8DI-8RO**, RS485 version with standard Ethernet port. Do not substitute the CAN `-C` or PoE version without a decision.
- Eight relay outputs and eight isolated digital inputs.
- Module input range 7–36 V; current design powers the module from 24 V.
- RS485 connection to MYD-YF13X. Modbus RTU firmware is planned; do not assume the factory firmware meets the required protocol and behavior without testing.
- Proposed: both modules on one multi-drop RS485 bus from MAINCTRL, with distinct Modbus slave addresses and termination at the two bus ends only. Topology (shared bus vs two MAINCTRL ports), addressing and termination are **TBC**.
- RO1–RO4 switch four 12 V electromechanical latches: main, retrieval, return and table doors.
- Relay COM receives **separate 12 V derived on SYSCTRL**. The module's 24 V input does not supply or convert the relay-contact voltage.
- DI1–DI5 are allocated to door sensors in the diagram. RO5–RO8 remain reserved for undefined actuator requirements.
- The latch/door-sensor allocation above describes the original single module. **How the four latches, five door sensors and any new functions are split between IOCTRL-01 and IOCTRL-02 is TBC.** The functions assigned to the second module have not been defined; do not invent them.
- Power: two module 24 V feeds and 12 V relay-contact feeds must be accounted for (per-module or shared branches TBC; see W34/W35).
- Ethernet, Wi-Fi and BLE unused.
- Official documentation: https://www.waveshare.com/wiki/ESP32-S3-ETH-8DI-8RO

### SYSCTRL — custom PCB, quantity 1

- `HW_ADHERENT_SYSCTRL_R1` / `FW_ADHERENT_SYSCTRL_R1`.
- STM32 machine controller; combines the former motion-control and auxiliary-I/O functions. The current IOCTRL name refers to the separate Waveshare relay/input module.
- Gantry drive control interfaces, brake control, basket servo control, optical sensors, labeling stepper drivers and auxiliary outputs.
- **Onboard 24→12 V buck supplies the existing 12 V loads**, including local circuitry, MAINCTRL and latch contacts. LANECTRL R1 does not use 12 V: it takes only 24 V and generates its own 5 V / 3.3 V.
- Buck topology, MPN, current capacity, protection, thermal design and sequencing are not selected/validated.
- Local servo voltage conversion remains necessary; DS3218 is not a direct 12 V or 24 V load.
- TMC5160 and TMC2209 are proposed labeling stepper drivers, not finalized selections.

### LANECTRL — custom PCB, quantity 10

- `HW_ADHERENT_LANECTRL_R1` / `FW_ADHERENT_LANECTRL_R1`. Altium project in `HW/HW_ADHERENT_LANECTRL_R1`, designer Umit KAYACIK (Microver title block). Schematic R1 "Initial Release" 2026-09-23; PCB placed and routed; STEP re-exported 2026-09-25.
- One board per row: seven conveyor channels, seven feedback inputs, seven rocker switches and seven lane-LED outputs. Includes the former LANEPANEL functions.
- Facts below come from the current SchDoc/PcbDoc files (checked 2026-09-25). The Protel netlist, BOMs and schematic PDF in the folder are older than the latest schematic/PCB edits; regenerate them before any release.

**Architecture (as designed, supersedes the R27 "H-bridge / 12 V lane logic" description)**

- Motor drive: **2 × TI TPS4H160BQPWPRQ1** 4-channel high-side smart switches (U7: lanes 1–4, U9: lanes 5–7, U9 channel 4 unused). On/off only: no H-bridge, no PWM speed control, no reversal. Current limit R_CL = 1.2 kΩ (R62/R71), current-sense R_CS = 604 Ω (R65/R75) to MCU ADC; FAULT, SEH/SEL and DIAG_EN to MCU. R62/R65/R71/R75 values are marked "?" in the schematic and still need confirmation.
- Hardware interlock: each lane input = rocker switch **AND** MCU enable (2 × SN74HCS08, EN_LANEx with 10 k pull-downs). A lane cannot run with its switch off, and cannot run without MCU enable.
- MCU: **STM32G0B1RET6** (LQFP64), 8 MHz crystal ECS-80-8-30Q-VS with 8.2 pF load caps. SWD on Samtec FTSH-103 (J9). USB-C (J10, USB 2.0 device, 5.1 k CC pull-downs, CMC + ESD) for service/programming.
- CAN: **SN65HVD231** (3.3 V) + ACT45B common-mode choke. CAN_RS driven by MCU (R44 pull-up keeps the node in standby at reset). **120 Ω termination selected with 2-pin jumper P1** (Molex 22-03-2021 + R43). Node ID from **4-position DIP switch S1** (Würth 418121270804, NODE_ID0–3).
- Power: single **24 V input**. Chain: F1 0452005 (5 A) → SMDJ24CA TVS → LM74700-Q1 + BSC028N06NS ideal-diode reverse protection → bulk 2 × 220 µF → motor rail; LMR50410 buck 24 V → 5 V (88.7 k / 22.1 k, VREF 1.0 V → 5.0 V) → AMS1117-3.3, with USB VBUS OR-ed in through MBR0520 diodes. VM_SENSE divider 100 k / 10 k to ADC. **The board has no 12 V input; lane logic is powered from its own 24 V input.**
- Lane connector: **7 × Molex Micro-Fit 3.0 43650-0300** (3-pin, right angle), pin 1 = switched 24 V (LANE_OUTx), pin 2 = GND, pin 3 = SIGNAL. SMF33A TVS on outputs and signal lines (the default BOM variant leaves D10 not fitted).
- SIGNAL input: 24 V dry contact → 10 k pull-down at connector, 100 k / 15 k divider (24 V → 3.13 V), BAT54WS clamp to 3.3 V, RC filter, to MCU GPIO.
- Bus connector: **one Molex Micro-Fit 3.0 43045-0400 (2 × 2, 4-pin): 1 = +24 V, 2 = GND, 3 = CANH, 4 = CANL.** There is no second (bus-out) connector on the board; daisy-chaining the CAN bus between rows therefore needs a harness-level solution (T-splice / Y-cable) or a board change. **Open decision.**
- User interface: 7 × C&K **300SP1J1BLKM2RE** PCB-mount rocker switches (SPDT ON–ON, 3.3 V logic level). Lane LEDs are **off-board**: 7 × 2-pin 2.54 mm headers LEDS1–LEDS7 on the switch side, driven from MCU GPIO through 100 Ω (R50–R56). The LED part and its mounting in the bracket are TBC. The earlier on-board LED footprints D29–D35 (Würth 150080VS75000) were removed from the PCB but still appear in the exported BOM/netlist. Board status LEDs D25 (power), D27 and D28 (LED_STAT, LED_CAN) are SMD parts on the bottom side.
- PCB: **504.0 × 60.0 mm**, 4 layers (Top / Int1 GND / Int2 PWR / Bottom), about 1.6 mm total thickness. Top side carries only the THT rocker switches, LED headers and mounting holes; **all SMD parts are on the bottom side**. Lanes run in order along the board: J7…J1 from left to right at **72.0 mm pitch**, J8 at the right end next to lane 1, USB-C at the bottom edge centre (x ≈ 272 mm). **8 × M3 mounting holes** at x = 6 / 167 / 343 / 498 mm and y = 6 / 54 mm from the lower-left corner (MTG2 at y = 55 mm, 1 mm off the others; confirm this is intentional).
- Previously listed candidates **Omron B3F-4055, Kingbright WP7113ID and DRV8876 are superseded** by the design above.

**Critical schematic error (found 2026-09-25, must fix before fabrication)**

- In `04_POWER.SchDoc` the protected rail after M1 carries power port **+24V_PR**, while the TPS4H160 VS pins (`08_DRIVER`) and the LMR50410 VIN/EN use power port **VM**. Nothing joins +24V_PR and VM, and the PcbDoc also holds them as two separate nets. As drawn, neither the motor switches nor the 5 V/3.3 V logic would receive power. Rename one port (or add the connection), recompile, update the PCB from the schematic and re-run DRC.

**Other open LANECTRL items**

- Recompile and regenerate the netlist, BOMs (both variants) and schematic PDF. The current PDF shows an empty block-diagram page, but `02_BLOCK_DIAGRAM.SchDoc` now embeds the A3 block-diagram image. The PcbDoc still uses NetS1_x names where the schematic now has NODE_ID0–3 (ECO pending).
- Only B1 (ferrite bead) lacks an MPN in the BOM. The variant name is still the default "Variant of HW_ADHERENT_LANECTRL_R1".
- LM74700 symbol pin naming, BAT54WS footprint polarity and TPS4H160 R_CL/R_CS values need final review.
- Bracket fit: check the 504 × 60 mm outline, hole pattern, switch positions and LED header positions against `LANE DRAWING SPACE FOR UMIT.DWG`.
- The current board model is `MEC/HW_ADHERENT_LANECTRL_R1/HW_ADHERENT_LANECTRL_R1(Variant of HW_ADHERENT_LANECTRL_R1).step` (identical export in the Altium Project Outputs). Older copies are in `MEC/01_CAD_MODELS/` and `MEC/Board_STEP_Models/LANECTRL_Custom/`.
- `HW/HW_ADHERENT_LANECTRL_R1/HW_ADHERENT_LABELCTRL_R1/` is a separate KiCad project nested inside the LANECTRL folder. It is not part of LANECTRL; move it to its own HW folder once its scope is defined.

**Conveyor interface facts used by LANECTRL**

- Customer bench measurement at 24 V (`Docs/New_Docs/information.txt`): 190 mA running, 280–310 mA with manual braking, about 0.5 A when stalled by hand. The SIGNAL line switches between 0 V and 24 V when the feedback plate moves (24 V dry contact); the board must read it and stop the motor.
- Supplier internal schematic (`Docs/Müşteriden gelen dosyalar/`): the motor is fed through series diode D3 and has freewheel diode D1 and capacitor C1. The plate switch S1 connects the supply to the signal pin through D2. The SIGNAL level is therefore only valid while that lane is energised. The drawing's pin numbering is the reverse of the datasheet (pin 1 = +24 V, pin 3 = SIGNAL). LANECTRL follows the datasheet; confirm on a real conveyor with a meter. Reversed polarity is blocked by D3 rather than shorted.
- Firmware still needs a stall/timeout strategy using current sense, because the conveyor has no limit switch.

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
- F14: lane-logic protection on SYSCTRL; 12 V passes into the CAN/lane harness. **Superseded by LANECTRL R1:** the board has no 12 V input, so the 12 V conductor in W25 and branch F14 are no longer needed for the lane rows. Remove them at the next diagram/workbook revision, or record a new use.
- W24 / F1–F10: 24 V row feeders. With LANECTRL R1 each row's 24 V (motors and logic) and CAN share one 4-pin Micro-Fit (43045-0400: +24 V / GND / CANH / CANL). How W24 and the W25 CAN backbone merge into a harness is **TBC**, because the board has only one bus connector.
- W29 / F15 and W30 / F16: proposed 24 V gantry drive feeds, pending supplier confirmation.
- W34 / F17: 24 V IOCTRL module power. With two IOCTRL modules, per-module feeds or a shared branch are TBC; cable quantity and fuse rating need updating.
- W35 / F18: derived 12 V feed to IOCTRL relay contacts. Second-module relay-contact feed TBC; 12 V converter load depends on the latches actually switched.
- W33: MAINCTRL–IOCTRL RS485. Now serves two modules; add the IOCTRL-01 to IOCTRL-02 segment (or a second run) once topology is fixed.
- W02, W31 and W32 retired with the removed PSUs. W14 and W22 retired with the cancelled intermediate sensor trunks.
- W15: six direct gantry sensor runs to SYSCTRL. W23: five direct door sensor runs to IOCTRL (module split TBC). No junction boxes.
- W36 status light, W37 PE bonding, W38 site-supplied Ethernet and W39 unresolved marker supply are explicitly scheduled.
- Fuse ratings, wire sizes, connector loading, DC/DC losses and simultaneous motor loads need recalculation. Older spreadsheet currents are estimates, not verified sizing.

## Communication

- Proposed CAN backbone: MAINCTRL → SYSCTRL → LANECTRL-10 through LANECTRL-01.
- Diagram baseline: CAN 2.0B, 500 kbit/s, termination at MAINCTRL and LANECTRL-01. Validate implementation and cable routing.
- LANECTRL R1 implementation: termination is fitted with jumper P1 (only on the end-of-bus board). The CAN node ID is set with the 4-bit DIP switch S1 (16 addresses, 10 used). The single 4-pin bus connector means the backbone needs T-splices or Y-cables at each row unless a second connector is added.
- Separate RS485 link: MAINCTRL ↔ IOCTRL-01 and IOCTRL-02 (proposed shared multi-drop bus; TBC).
- Site Ethernet connection serves the external iPad/app and server communication. Optional Wi-Fi/BLE arrangements remain distinct from rejected cellular connectivity.

## Motors and mechanisms

Current inventory is **75 motors across five model/part-reference groups**, excluding undefined door actuators:

- Conveyor motors: 70 brushed DC geared motors, one per lane. **CB002-24V-573mm is the conveyor assembly model**, not a confirmed standalone motor MPN. Driven on/off by TPS4H160 high-side switches on LANECTRL (no reversal, no PWM). Measured: 190 mA running, about 0.5 A when stalled by hand.
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
  - One model covers both IOCTRL placements; cabinet space, DIN mounting and cable clearance must be reserved for **two** modules.
  - Nominal 175 × 90 × 40 mm envelope from the user image.
  - Reference image is the **PoE variant**; compatibility with the selected non-PoE product is unverified.
  - Slots and connector geometry are estimated; DIN clip and antenna are omitted.
- MAINCTRL: `MEC/Board_STEP_Models/MAINCTRL_MYIR_MYD-YF13X/MAINCTRL_MYD-YF13X_Provisional_Placement_R1.step`.
  - Documented PCB outline 137.29 × 105 mm.
  - PCB thickness, hole positions/diameters, connector heights and component envelopes are estimates.
  - Simplified top- and bottom-side components are included.
- Both models passed solid validity and STEP reimport checks. **Geometry validity does not validate dimensional accuracy.** Read each folder's `MODEL_NOTES_R1.md`; use for preliminary placement only, not fabrication.
- No manufacturer IOCTRL STEP download was found in the checked official resources. Manufacturer request draft is saved locally and has not been sent.
- LANECTRL: the STEP model is exported from the routed R1 PCB (`MEC/HW_ADHERENT_LANECTRL_R1/`, 2026-09-25). SYSCTRL still needs a STEP from its PCB layout.

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
- English presentation, concise text and useful visuals. Remove unused interface options from the current presentation; retain historical decisions in project records.
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
- Seven-conveyor row case: 14.05 A versus candidate 5 A protection; concurrency must be constrained and tested. **Update:** that figure assumed 2 A per conveyor. The measured stall is about 0.5 A, so a row with all seven lanes stalled draws about 3.5 A plus logic, below the 5 A fuse (F1 0452005) on LANECTRL. The TPS4H160 current limit (R_CL 1.2 kΩ) caps each channel. Recalculate the PSU budget with measured values.
- 39 cable IDs, 28 required external types, five missing route lengths; 109.5 m is only the known routing subtotal.
- 18 branch-protection references; physical placement and holder quantities need reconciliation with the merged SYSCTRL connector architecture.
- FW/SW folders contain scope descriptions only, no implemented firmware/application builds.
- HW contains four reserved board folders; no production PCB designs have been added. README must distinguish planned functions from implemented or validated capabilities. **Update 2026-09-25:** LANECTRL R1 is placed and routed (not released; see the critical +24V_PR/VM error above). SYSCTRL R1 and NFC R1 Altium projects have also been started; they are not described here yet.

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
- Current document names use `ADHERENT_<Purpose>` without R27 suffixes. The editable system diagram and PNG share `ADHERENT_System_Wiring_Diagram`. The earlier presentation is explicitly `ADHERENT_Design_Review.pptx`.
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

## Current presentation — 2026-09-25

- `SYS/ADHERENT_Design_Review.pptx` supersedes the earlier snapshot. Ten slides retain the established design and cover used system interfaces.
- Removed camera/OCR, UPS, cellular and unapproved interior-lighting topic slides. Removed machine Wi-Fi/BLE/AP-mode options and payment-terminal interface alternatives from retained slide text, diagrams and notes.
- Site-network iPad access remains. CAN row control, RS485 IOCTRL, gantry controls, direct sensors, wired Ethernet and required status indication remain in scope. The status-light model remains TBC.
- NFC antenna is Molex 1462362151. Reader/front-end selection, host interface, RF matching and supply remain TBC; no specific host port is assigned.
- Presentation architecture reflects one SYSCTRL onboard 24 V-to-12 V SMPS and integrated power connectors. W04/W06/W07 are internal SYSCTRL links. Removed stale external cable totals and old document filenames.
- The overview image is a presentation-specific view of the current draw.io diagram with excluded blocks omitted. The source system diagram is unchanged.
- Final PPTX passed package/layout validation, a normal Microsoft PowerPoint opening, and visual review of all slides. README links now point to the current presentation.

## IOCTRL quantity change — 2026-09-25

- The Waveshare **ESP32-S3-ETH-8DI-8RO** IOCTRL module is used **twice per system**: IOCTRL-01 and IOCTRL-02. This supersedes every earlier "IOCTRL quantity 1" statement.
- System controller count: MAINCTRL ×1 and IOCTRL ×2 purchased (**3 purchased controller assemblies**), plus the custom boards.
- Open for the second module: assigned functions and I/O allocation, RS485 topology/addressing/termination, 24 V and 12 V feed branches (W34/W35, F17/F18), cabinet placement, and the updated power budget.
- Aligned to IOCTRL ×2 on 2026-09-25: `README.md`, `SYS/README.md`, `SYS/ADHERENT_Electrical_Tables.xlsx` (row IOCTRL-01, -02, qty 2), `SYS/ADHERENT_System_Wiring_Diagram.drawio` + PNG, `SYS/ADHERENT_Design_Review.pptx` (slides 3, 7, 10 and notes), `MEC/Board_STEP_Models/README.md` and `FW/README.md`.
- Diagram shows IOCTRL-01/-02 as one stacked block ("COTS ×2") because the I/O split is undefined; draw two separate blocks once the allocation is decided. The PNG was rendered with the draw.io viewer, not the desktop CLI; re-export from draw.io desktop if exact font rendering matters.
- The small overview image on presentation slide 3 is an earlier presentation-specific render and still shows one IOCTRL; its text is not legible at slide size. Regenerate it with the next diagram change.

## LANECTRL R1 documentation alignment — 2026-09-25

- The LANECTRL section above was rewritten from the current `HW_ADHERENT_LANECTRL_R1` SchDoc/PcbDoc files: TPS4H160 high-side drive, 24 V-only supply, single 4-pin Micro-Fit bus connector, 7 × 3-pin Micro-Fit lane connectors, C&K rocker switches, off-board lane LEDs, and a 504 × 60 mm 4-layer PCB. Superseded: H-bridge, 12 V lane logic, B3F-4055, WP7113ID and DRV8876.
- Recorded the critical +24V_PR / VM disconnection in `04_POWER` (fix before fabrication), the stale netlist/BOM/PDF outputs and the single-bus-connector harness decision.
- Aligned `README.md`, `FW/README.md`, `MEC/Board_STEP_Models/README.md`, the LANECTRL/CONVEYOR rows of `SYS/ADHERENT_Electrical_Tables.xlsx`, row 18 of `MEC/ADHERENT_Mechanical_BOM.xlsx`, the LANECTRL blocks in `SYS/ADHERENT_System_Wiring_Diagram.drawio` and the connector HOLD line of `SYS/ADHERENT_Design_Review.pptx`.
- Fixed the bracket DWG links; the file is in `MEC/01_CAD_MODELS/Drawıng/`.

## System diagram layout rebuild — 2026-09-25

- `SYS/ADHERENT_System_Wiring_Diagram.drawio` is now generated by `.work/gen_diagram.py` (fixed coordinates, orthogonal corridors). Edit the script and re-render, or edit the `.drawio` directly and keep the PNG in step.
- Layout: column 1 = network / AC + PSU1 / NFC; column 2 = control cabinet (MAINCTRL, SYSCTRL with BUCK12 and SYSCTRL-PWR, IOCTRL ×2, status light); column 3 = gantry / labeling / doors; column 4 = ten lane rows. IOCTRL is drawn inside the control cabinet, matching the parts sheet location.
- Content is unchanged: all W / F / J / K / RO / DI references, part numbers and TBC flags were carried over and checked by script. Wording was shortened; details that the connecting line already shows (for example W13, W15, W20 / W21, W23) moved from box text to the line labels.
- Added the missing custom PCB **NFC · HW_ADHERENT_NFC_R1** (STM32F103C8 + ST25R200 reader, CAN node, 24 V + CAN on a 4-pin Micro-Fit) in place of the "NFC reader / front end TBC" block. Its system wiring (CAN position / node ID, 24 V branch and fuse, mounting) has no W / F reference yet, so no harness is drawn. The parts sheet NFC row was updated to match.
- `HW_ADHERENT_LABELCTRL_R1` is an empty KiCad skeleton with no defined function, so it is not shown.
- PNG rendered with draw.io desktop 24.7.17 (CLI, scale 1.75).
