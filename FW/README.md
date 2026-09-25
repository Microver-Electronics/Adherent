# Z-Band Smart Amp - Firmware

Firmware for the **Z-Band Smart CATV RF Amplifier** main board.

- **MCU:** STM32L431RBT6 (Cortex-M4F, 128 KB flash, 64 KB SRAM, LQFP64)
- **Clocks:** 24 MHz HSE crystal -> 80 MHz SYSCLK (PLL /M=3 xN=20 /R=2),
  32.768 kHz LSE, HSI16 as the I2C1 kernel clock
- **IDE / toolchain:** STM32CubeIDE (managed build, GNU Tools for STM32)
- **Architecture:** bare-metal cooperative scheduler (no RTOS), layered drivers
  on top of the ST HAL

The amplifier provides +30 dB gain over a single coax in/out, with a
microcontroller-managed RF path (digital step attenuator, switched
cable-sim / equalization conditioning, return-path passthrough), an
on-board RF power-measurement subsystem (ADF4351 + MAX9933 detector
daughterboard), a 240x320 ST7789 LCD with a 5-button menu, and
non-volatile storage of operating state.

See [`docs/FIRMWARE_DESIGN.md`](docs/FIRMWARE_DESIGN.md) for the full
architecture, [`docs/OPERATION_MANUAL.md`](docs/OPERATION_MANUAL.md) for the
Z-BAND operator guide, and [`docs/PINMAP.md`](docs/PINMAP.md) for the authoritative
pin assignments (extracted from `HW_Z-BAND_SMART_AMP_R1`).

## Layout

```
FW/
+-- ZBand_SmartAmp/               # STM32CubeIDE project (import as existing project)
|   +-- ZBand_SmartAmp.ioc        # CubeMX configuration (pinout, clocks, peripherals)
|   +-- STM32L431RBTX_FLASH.ld    # linker script (stack raised to 0x1000)
|   +-- Core/
|   |   +-- Inc/                  # main.h (pin defines), peripheral init headers
|   |   +-- Src/                  # main.c, gpio/adc/i2c/spi init, IT handlers
|   |   +-- Startup/              # startup_stm32l431rbtx.s
|   +-- Drivers/                  # STM32L4xx HAL + CMSIS (ST-provided)
|   +-- App/                      # application firmware (all custom code)
|       +-- include/              # fw_config.h, fw_types.h
|       +-- util/                 # scheduler (HAL_GetTick), debug (ITM), crc32
|       +-- devices/              # st7789(+gfx), pe4312, pe42462,
|       |                         #   at24cs02, buttons, adf4351, rf_detector,
|       |                         #   adc_inputs, power_rails
|       +-- app/                  # settings, rf_path, measurement, agc,
|                                 #   channel_plan, ui, app
+-- docs/
+-- OLD_FIRMWARE_ON_OLD_HARDWARE/ # reference: proven rev 6.x tuner firmware
```

The old custom CMake / bare-metal register tree (`src/`, `cmake/`,
`linker/`, `include/`) has been removed; the CubeIDE project above is the
only firmware source.

## Building

Open STM32CubeIDE, then **File > Import > Existing Projects into
Workspace** and select `FW/ZBand_SmartAmp`. Build with the Debug or
Release configuration.

Command-line sanity build (uses the GNU tools bundled with CubeIDE):

```powershell
# from FW/ZBand_SmartAmp, with arm-none-eabi-gcc on PATH
powershell -ExecutionPolicy Bypass -File build_check.ps1
```

Regenerating from CubeMX (`ZBand_SmartAmp.ioc`) is safe: all custom code
lives in `App/` and in `USER CODE` sections of `Core/`.

## Flashing / debug

- Flash from CubeIDE (ST-LINK, SWD), or:

```bash
st-flash --connect-under-reset write ZBand_SmartAmp/Debug/ZBand_SmartAmp.bin 0x08000000
```

- **Customer UART (J4):** USART1 on PA9 TX / PA10 RX, **115200 8N1**. Connect a
  USB-UART adapter to J4 (cross TX/RX). At boot you get an interactive CLI
  (`help`, `status`, `rails`, `ch`, `gain`, `mode`, `ver`). Firmware log lines
  are prefixed with `E`/`W`/`I`/`D`.
- **Developer SWO (optional):** when `FW_DEBUG_ITM=1`, logs are also mirrored to
  ITM stimulus port 0. Enable SWV in the CubeIDE debug configuration.

## Hardware errata / bring-up notes

- **PA8 detector readback erratum:** the detector output `PD_OUTADJ`
  (J3.4) is routed to **PA8**, which has **no ADC channel**. The firmware
  reads the detector on **PA4 (ADC1_IN9)** and assumes a rework wire
  J3.4 -> PA4. If the board is respun instead, only the channel selection
  in `App/devices/adc_inputs.c` changes. PA8 is left analog/hi-Z.
- The PE42462 conditioning truth table in `App/app/rf_path.c`
  (`s_cond_map`) and the AS179 tap-select polarity in
  `App/app/measurement.c` (`tap_select`) are marked for confirmation at
  RF bring-up.
- `USB_P/USB_N` (PA11/PA12) are routed on the board, but **STM32L431 has
  no USB peripheral** - USB is not used by this firmware.
