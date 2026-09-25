# Adherent firmware

No firmware implementation or build has been added yet. Planned project identifiers:

- FW_ADHERENT_MAINCTRL_R1: MYIR Linux supervisor, site networking, CAN and RS485 master.
- FW_ADHERENT_SYSCTRL_R1: gantry/labeling motion, sensors, outputs and fault handling.
- FW_ADHERENT_LANECTRL_R1: STM32G0B1RET6, ten CAN nodes (SN65HVD231; node ID from the 4-bit DIP switch S1, CAN_RS controlled by the MCU). Drives seven conveyor channels on/off through 2 × TPS4H160 (EN_LANEx ANDed with the rocker switch in hardware). Reads current sense (DRV_CS1/2 with SEH/SEL multiplexing), FAULT, 24 V rail (VM_SENSE), seven 24 V feedback inputs (LANEx_SIG) and seven switch states, and drives seven lane LEDs plus status/CAN LEDs. USB-C device port for service. Needed: stall/timeout stop (no limit switch; about 0.5 A stall measured) and the rule that feedback is valid only while the lane is energised.
- FW_ADHERENT_IOCTRL_R1: Waveshare RS485 integration on two modules (IOCTRL-01, IOCTRL-02) with distinct RS485 addresses; selected firmware behavior requires validation.

Six gantry sensors connect directly to SYSCTRL and five door sensors directly to IOCTRL (split between the two modules TBC). No junction boxes. Each IOCTRL module is powered from 24 V; relay contacts switch separate SYSCTRL-derived 12 V.

Define and test protocol/register maps, watchdogs, motor concurrency, startup and power-loss states, and motion/access interlocks before release. See R27 electrical workbook OpenItems. Hardware pin assignments and current limits are not released.
