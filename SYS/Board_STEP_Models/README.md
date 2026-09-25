# Board STEP models

Blackocean Technologies / Adherent360 APDU

Mechanical integration handoff folder. STEP models have not been collected yet.

- `MAINCTRL_MYIR_MYD-YF13X/`: off-the-shelf MYIR central controller, 1 unit.
- `IOCTRL_Waveshare_ESP32-S3-ETH-8DI-8RO/`: off-the-shelf relay and digital input module, 1 unit.
- `SYSCTRL_Custom/`: custom machine controller, 1 PCB assembly. Export the STEP assembly from the PCB design when available.
- `LANECTRL_Custom/`: custom row controller, 10 identical PCB assemblies. One board model is sufficient for the ten placements. Buttons and LEDs are part of this board; no separate LANEPANEL.

Store `.step` or `.stp` models in the corresponding folder. For purchased products, record the source URL, exact product variant, and model revision alongside the file. Indicate whether connectors and the enclosure are included, so the mechanical team can check mounting and cable clearance.
