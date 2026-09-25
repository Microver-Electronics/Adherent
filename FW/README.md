# Adherent firmware

No firmware implementation or build has been added yet. Planned project identifiers:

- FW_ADHERENT_MAINCTRL_R1: MYIR Linux supervisor, site networking, CAN and RS485 master.
- FW_ADHERENT_SYSCTRL_R1: gantry/labeling motion, sensors, outputs and fault handling.
- FW_ADHERENT_LANECTRL_R1: seven conveyor channels, buttons and LEDs; ten CAN nodes.
- FW_ADHERENT_IOCTRL_R1: Waveshare RS485 integration; selected firmware behavior requires validation.

Six gantry sensors connect directly to SYSCTRL and five door sensors directly to IOCTRL. No junction boxes. IOCTRL module power is 24 V; relay contacts switch separate SYSCTRL-derived 12 V.

Define and test protocol/register maps, watchdogs, motor concurrency, startup and power-loss states, and motion/access interlocks before release. See R27 electrical workbook OpenItems. Hardware pin assignments and current limits are not released.
