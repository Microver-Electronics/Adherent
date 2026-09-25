# Adherent system documents

- [Electrical parts sheet](ADHERENT_Electrical_Tables.xlsx): one worksheet, 32 grouped entries. Diagram reference, component, part number, quantity, location, product/source link, STEP/drawing link and rough dimensions in mm.
- [System wiring diagram](ADHERENT_System_Wiring_Diagram.drawio) and [PNG preview](ADHERENT_System_Wiring_Diagram.png): matching part references, no displayed revision tags.
- [Design review](ADHERENT_Design_Review.pptx): 10 slides covering used system interfaces, current SYSCTRL power architecture and selected NFC antenna.
- [Earlier engineering review](ADHERENT_Project_Review.md): historical validation and open engineering issues.
- [Mechanical BOM](../MEC/ADHERENT_Mechanical_BOM.xlsx) and [board STEP models](../MEC/Board_STEP_Models/README.md).

Use MAINCTRL, SYSCTRL, LANECTRL and IOCTRL everywhere. LANECTRL-01 through LANECTRL-10 are ten instances of HW_ADHERENT_LANECTRL_R1. IOCTRL-01 and IOCTRL-02 are two identical Waveshare ESP32-S3-ETH-8DI-8RO modules. CONVEYOR-01 through CONVEYOR-10 identify row groups, each containing seven CB002-24V-573mm conveyors. References are identical in the diagram and parts sheet.

TBC means not confirmed. Missing part selections, source links and dimensions remain explicitly marked. MAINCTRL and IOCTRL STEP models are provisional; the IOCTRL reconstruction uses a PoE reference whose fit to the selected non-PoE variant is unverified. Internal SYSCTRL functions are not additional purchased assemblies. Zero-quantity rows identify excluded or external blocks.

Detailed multi-tab engineering schedules and the previous component register are retained in Git history at commit aef502b. They are superseded as customer deliverables by the single parts sheet. No junction boxes are used.
