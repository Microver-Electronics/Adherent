# DOORIO provisional placement model R1

Blackocean Technologies / Adherent360 APDU

This is a simplified, locally reconstructed CAD model, not a Waveshare-supplied model. Use it for preliminary cabinet placement only. Do not manufacture or drill mounting parts from it.

## Reference and dimensions

Reference: the user-supplied dimension image, labelled ESP32-S3-POE-ETH-8DI-8RO. The project selects ESP32-S3-ETH-8DI-8RO (non-PoE, RS485). Mechanical equivalence is unverified.

- Overall nominal envelope: 175 x 90 x 40 mm.
- Base thickness: 10 mm.
- Upper enclosure width: 155 mm, interpreted from the image dimension. Confirm its exact datum with the manufacturer.
- Vertical mounting feature centre spacing: 70 mm, with 10 mm end offsets.
- Side mounting feature centre offset: 5 mm, interpreted symmetrically from the image. Horizontal spacing therefore assumed 165 mm; this is not independently confirmed.

## Estimated and omitted geometry

- Four 6 x 4.5 mm mounting slots are estimated visual features. Slot diameter/length were not supplied.
- Enclosure wall structure, cover, terminal recesses, connector sizes and connector positions are approximate.
- Internal PCB, components, fasteners, DIN-rail clip, SMA connector and antenna are omitted because dimensioned geometry was not supplied.
- The nominal envelope does not represent cable bend space or connector/antenna protrusions. Reserve these separately after checking the actual hardware.

## Files and validation

- DOORIO_Provisional_Placement_R1.step: separate solid parts, millimetres.
- DOORIO_Provisional_Placement_R1.svg: isometric preview; colours are illustrative.
- build_ocp_R1.py: reproducible OpenCascade source using cadquery-ocp.
- validation_R1.json: STEP reimport validity and bounding-box check.

Origin: lower corner of the nominal base. X = 175 mm length, Y = 90 mm width, Z = 40 mm height. Replace with the manufacturer model once available.
