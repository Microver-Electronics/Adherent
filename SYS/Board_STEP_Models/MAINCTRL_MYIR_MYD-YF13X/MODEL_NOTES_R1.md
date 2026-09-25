# MYIR MYD-YF13X provisional placement model R1

Blackocean Technologies / Adherent360 APDU

Reconstructed from the three user-supplied images: dimensioned base-board top view, populated top photograph and bottom photograph. The reference board is marked MYB-YF13X-V02. This is not manufacturer CAD and does not establish the exact populated ordering variant.

## Confirmed from the dimension drawing

- PCB outline: 137.29 x 105 mm.
- Units: millimetres.

## Assumptions

- PCB thickness 1.6 mm and corner radius 2 mm.
- Four mounting holes: diameter 3.2 mm, centres 4 mm from adjacent board edges. These are estimated from the images; do not use them to drill mounting hardware.
- Connector XY positions and footprints are scaled from the top-view drawing. All connector and component heights are estimates.
- RJ45 bodies are 16 mm above the PCB top, dual USB 15.5 mm, field terminal block 12 mm, DC jack/audio 11 mm, expansion header including exposed pins 11 mm, SoM shield 4.3 mm.
- Bottom-side FFC connectors extend 2.5 mm below the PCB; SIM and microSD socket envelopes extend 2.0 and 1.8 mm. Their locations are estimated from the mirrored bottom photograph.
- Connector cavities, screw terminals, mating hardware, solder tails, most small components and cable bend space are not modelled. Header pins are illustrative, not an electrical pin-count reference.
- The empty mini-PCIe area has no fitted modem model. SIM socket geometry represents the physical board connector, not a cellular requirement.
- SMA geometry is a simplified connector projection; no external antenna is included.

## Use and files

Use for preliminary placement only. Verify hole locations, component height, underside clearance and connector access against actual hardware or manufacturer drawings before releasing mounting parts.

Origin is the lower-left corner in the supplied top view, on the PCB bottom surface. X runs right, Y runs towards the expansion headers, Z is positive above the PCB. Bottom-side components have negative Z.

- `MAINCTRL_MYD-YF13X_Provisional_Placement_R1.step`: independent solid components; millimetres.
- `MAINCTRL_MYD-YF13X_Provisional_Placement_R1.png`: preview rendered from CAD geometry; colours are illustrative.
- `build_ocp_R1.py`: reproducible OpenCascade source (cadquery-ocp, NumPy, Pillow).
- `validation_R1.json`: STEP reimport validity and bounding-box measurements. Assembly dimensions include estimated connector projections and must not be mistaken for verified product dimensions.
