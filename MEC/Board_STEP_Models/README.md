# Board STEP models

Blackocean Technologies / Adherent360 APDU

Mechanical integration handoff folder. Models are available, but they are not all verified manufacturer models or production PCB exports.

- `MAINCTRL_MYIR_MYD-YF13X/`: off-the-shelf MYIR central controller, 1 unit.
- `IOCTRL_Waveshare_ESP32-S3-ETH-8DI-8RO/`: off-the-shelf relay and digital input module, 1 unit.
- `SYSCTRL_Custom/`: custom machine controller, 1 PCB assembly. Export the STEP assembly from the PCB design when available.
- `LANECTRL_Custom/`: custom row controller, 10 identical PCB assemblies. One board model is sufficient for the ten placements. Buttons and LEDs are part of this board; no separate LANEPANEL.

Store `.step` or `.stp` models in the corresponding folder. For purchased products, record the source URL, exact product variant, and model revision alongside the file. Indicate whether connectors and the enclosure are included, so the mechanical team can check mounting and cable clearance.

## Current model status

- MAINCTRL and IOCTRL have reconstructed `Provisional_Placement_R1.step` models with notes and geometry-validation results. Estimated holes and connector heights are not fabrication dimensions.
- MYIR `myc-yf135-v02_asm.stp` is a module model, not the complete MYD-YF13X carrier assembly.
- `LANECTRL_Custom/HW_ADHERENT_LANECTRL_R1.step` is present. Provenance, revision and fit to the front-bracket DWG remain to be verified.
- SYSCTRL requires a STEP assembly from the actual PCB design.
- IOCTRL's reconstruction used a PoE-variant image; fit to the selected non-PoE variant remains open.

No RAR bundle is maintained. Use the individual model files and notes.
