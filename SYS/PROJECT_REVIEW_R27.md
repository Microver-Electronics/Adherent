# Adherent R27 document review

Reviewed against the current system diagram, supplied mechanical BOM and conveyor sheet, recorded project decisions and supplier references in the workbooks. This is a document and architecture review; no physical machine, manufactured PCB or bracket-fit test was performed.

## Changes completed

- Aligned presentation, electrical workbook and draw.io to one 24 V system PSU and SYSCTRL-derived 12 V. RSP-500-24 rating: 24 V, 21 A, 504 W.
- Removed junction boxes. W15 is six direct SYSCTRL sensor runs; W23 is five direct IOCTRL sensor runs. W14/W22 are retired with zero quantity.
- Separated IOCTRL's 24 V module feed W34 from its 12 V latch-contact feed W35. Relay contacts do not generate 12 V.
- Added the requested component/part-number spreadsheet: 74 rows including diagram components, internal parts, interface positions and excluded/external items. Unknown MPNs are TBC.
- Included McMaster 1422N13 J2, one per machine, in both BOMs and the component register. Retained native COTS connectors separately from custom-board Micro-Fit candidates.
- Corrected stale supply, driver and connector assumptions, obsolete naming in embedded presentation diagrams, and lane indexing. Replaced false completed-status icons with explicit open/excluded states.
- Retained 70 conveyors, 70 buttons, 70 LEDs, 10 LANECTRL assemblies and one each of MAINCTRL, SYSCTRL and IOCTRL. Two custom designs, eleven custom assemblies.
- Added status-light, protective-earth and marker-supply cable requirements. Corrected unrelated FW/SW template descriptions and model-availability documentation.

## Engineering evidence still required

The electrical workbook records O01-O15 with responsible roles and required evidence. Release blockers include exact gantry drive/brake compatibility at 24 V, SYSCTRL converter selection, conveyor loaded/stall current and signal reference, enforced concurrency, motor transient protection, harness/protection sizing and physical validation.

The candidate SMBJ33CA clamp specification does not establish protection below the candidate DRV8876 absolute maximum. A 6.3 A nominal fuse holder cannot be assumed suitable for a larger buck-input branch. Motor phase-current ratings do not substitute for drive supply-input current. Candidate parts remain unreleased.

Marker and latch/sensor models, MYIR order code, servo variant, PCB layouts and direct-harness lengths remain unresolved. The supplied bracket DWG is preserved, but PCB/button/LED fit has not been checked. Reconstructed STEP models do not validate real hardware dimensions.

## Verification

- Visually checked all 14 slides. Presentation package and layout validators reported no findings; three intentional template background shapes extend beyond slide boundaries.
- Rendered and inspected diagram and workbook content. Mapped all 44 component blocks in the diagram to spreadsheet entries. Checked edge references, direct sensor endpoints, cable IDs and quantities across spreadsheets.
- Recalculated power: known peak subtotal 268.96 W, excluding three unknown load currents and unresolved marker supply. Increasing peak conveyor concurrency from one to two adds 48 W, producing 316.96 W; restored baseline afterward. These are planning assumptions, not measured approval.
- Seven simultaneous 2 A conveyors plus row losses require 14.05 A, exceeding the candidate 5 A row fuse. Workbook flags this case.
- 39 stable cable identifiers; 31 required types. Five required route lengths missing. The 111 m known routing subtotal is not a complete cut list.
- 18 branch-protection positions: 17 DIN and F14 on SYSCTRL. Cached spreadsheet formulas contain no error cells.

Documents are aligned for design discussion and selection work. Manufacturing/procurement release remains pending the evidence above.
