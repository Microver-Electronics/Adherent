# Board STEP models

Blackocean Technologies / Adherent360 APDU

Mechanical integration handoff folder. Models are available, but they are not all verified manufacturer models or production PCB exports.

- `MAINCTRL_MYIR_MYD-YF13X/`: off-the-shelf MYIR central controller, 1 unit.
- `IOCTRL_Waveshare_ESP32-S3-ETH-8DI-8RO/`: off-the-shelf relay and digital input module, 2 identical units (IOCTRL-01, IOCTRL-02). One model is sufficient for both placements; reserve cabinet space and cable clearance for two.
- `SYSCTRL_Custom/`: custom machine controller, 1 PCB assembly. Export the STEP assembly from the PCB design when available.
- `LANECTRL_Custom/`: custom row controller, 10 identical PCB assemblies. One board model is sufficient for the ten placements. Rocker switches are on this board; lane LEDs connect through 2-pin headers on the board. No separate LANEPANEL.

Store `.step` or `.stp` models in the corresponding folder. For purchased products, record the source URL, exact product variant, and model revision alongside the file. Indicate whether connectors and the enclosure are included, so the mechanical team can check mounting and cable clearance.

## Current model status

- MAINCTRL and IOCTRL have reconstructed `Provisional_Placement_R1.step` models with notes and geometry-validation results. Estimated holes and connector heights are not fabrication dimensions.
- MYIR `myc-yf135-v02_asm.stp` is a module model, not the complete MYD-YF13X carrier assembly.
- LANECTRL: the current model is `../HW_ADHERENT_LANECTRL_R1/HW_ADHERENT_LANECTRL_R1(Variant of HW_ADHERENT_LANECTRL_R1).step`, exported from the routed R1 PCB on 2026-09-25 (504 × 60 mm, 4-layer, rocker switches and LED headers on one side, all SMD on the other, 8 × M3 holes). `LANECTRL_Custom/HW_ADHERENT_LANECTRL_R1.step` is an earlier export; replace it or ignore it. Fit to the front-bracket DWG remains to be verified.
- SYSCTRL requires a STEP assembly from the actual PCB design.
- IOCTRL's reconstruction used a PoE-variant image; fit to the selected non-PoE variant remains open.

No RAR bundle is maintained. Use the individual model files and notes.
