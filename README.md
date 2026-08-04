# STM32 LoRa APRS Repeater (Bluepill + 2x RFM96W)

## 📡 Project Overview

A simple, energy-efficient **LoRa APRS Repeater** based on the STM32F103C8T6 microcontroller (Bluepill) and two RFM96W radio modules (SX1278). The device operates in "Cross-Band" mode (receives on one frequency, transmits on another) and features telemetry and watchdog functions.

## 🚀 Features and Capabilities

* **Dual Radio:** Independent modules for RX (receiving from tracker) and TX (transmitting to iGate).
* **Continuous Listening (RX Continuous):** Ensures no frames are missed.
* **Buffering (Queue):** FIFO queue for 5 packets – prevents data loss when multiple frames arrive simultaneously.
* **Transparency:** Forwards raw LoRa frames (including 3C FF 01 headers), ensuring compatibility with most trackers and iGates.
* **Intelligent Watchdog (IWDG):** Automatic reset system in case of CPU hang-up.
* **Radio Sanity Check:** Custom mechanism for monitoring the status of radio modules. If a transmitter hang-up is detected (e.g., due to SPI errors or Brown-out), the system automatically performs a hard reset of the RF module.
* **Reset Counter (R_CNT):** Statistics for resets (Watchdog/Radio) stored in Backup registers (BKP); these persist through device resets and only clear upon a total power loss.
* **Energy Efficiency:** The processor enters SLEEP mode (WFI) when idle.
* **Telemetry:** Automatic station status transmission every 1 hour (supply voltage, coordinates, and reset counter).
* **Debug Mode:** Real-time monitoring of received and transmitted frames via UART when the service jumper is shorted.

## ⚙️ Radio Parameters (LoRa)

Settings for RX:

| Parameter | Value |
| :--- | :--- |
| **RX Frequency** | `434.855 MHz` |
| **Spreading Factor (SF)** | `9` |
| **Bandwidth (BW)** | `125 kHz` |
| **Coding Rate (CR)** | `4/7` |
| **Tx Power** | `Max (0xFF)` |

Settings are identical for TX:

| Parameter | Value |
| :--- | :--- |
| **TX Frequency** | `434.955 MHz` |
| **Spreading Factor (SF)** | `9` |
| **Bandwidth (BW)** | `125 kHz` |
| **Coding Rate (CR)** | `4/7` |
| **Tx Power** | `Max (0xFF)` |

### Output Power Configuration for PA_BOOST Pin (SX1278 / RFM96)

The table below details the register mappings for target RF output power on the **PA_BOOST** pin (range: +2 dBm to +20 dBm).

| Target Power (dBm) | Output Power (mW) | Power Level (% mW)* | OutputPower Bits (3–0) | REG_PA_CONFIG (`0x09`) | REG_PA_DAC (`0x4D`) | REG_OCP (`0x0B`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **20 dBm** | **~100 mW** | **200% (High Power)** | `15` (`0x0F`) | `0x8F` | **`0x87`** | **`0x3B`** (150mA) |
| **17 dBm** | ~50 mW | 100% (Std Max) | `15` (`0x0F`) | `0x8F` | `0x84` | `0x2B` (100mA) |
| **16 dBm** | ~40 mW | ~80% | `14` (`0x0E`) | `0x8E` | `0x84` | `0x2B` (100mA) |
| **15 dBm** | ~32 mW | ~63% | `13` (`0x0D`) | `0x8D` | `0x84` | `0x2B` (100mA) |
| **14 dBm** | ~25 mW | **50%** | `12` (`0x0C`) | `0x8C` | `0x84` | `0x2B` (100mA) |
| **13 dBm** | ~20 mW | ~40% | `11` (`0x0B`) | `0x8B` | `0x84` | `0x2B` (100mA) |
| **10 dBm** | ~10 mW | 20% | `8` (`0x08`) | `0x88` | `0x84` | `0x2B` (100mA) |
| **5 dBm** | ~3.2 mW | ~6.3% | `3` (`0x03`) | `0x83` | `0x84` | `0x2B` (100mA) |
| **2 dBm** | ~1.6 mW | ~3.1% (Min) | `0` (`0x00`) | `0x80` | `0x84` | `0x2B` (100mA) |

*\*Note: +20 dBm mode requires a max 1% duty cycle operation to prevent thermal overload on the SX1278 IC.*

*\*Note: Percentage power level relates to true radiated RF power in milliwatts ($P_{\text{mW}} = 10^{\frac{P_{\text{dBm}}}{10}}$), referenced to 17 dBm (~50 mW) as 100%.*

## 🔌 Wiring Diagram (Pinout)

The device uses the **SPI1** bus shared by both radio modules.

### Module 1: Receiver (RX - 434.855 MHz)
| RFM96W Pin | STM32 Pin (Bluepill) | Notes |
| :--- | :--- | :--- |
| MISO | **PA6** | Shared SPI |
| MOSI | **PA7** | Shared SPI |
| SCK | **PA5** | Shared SPI |
| NSS (CS) | **PA4** | Chip Select |
| RST | **PB0** | Reset |
| DIO0 | **PB1** | Interrupt (EXTI1) |
| 3.3V | 3.3V | |
| GND | GND | |

### Module 2: Transmitter (TX - 434.955 MHz)
| RFM96W Pin | STM32 Pin (Bluepill) | Notes |
| :--- | :--- | :--- |
| MISO | **PA6** | Shared SPI |
| MOSI | **PA7** | Shared SPI |
| SCK | **PA5** | Shared SPI |
| NSS (CS) | **PA3** | Chip Select |
| RST | **PB10** | Reset |
| DIO0 | **PB11** | Interrupt (EXTI15) |
| 3.3V | 3.3V | |
| GND | GND | |

### Other
| Function | STM32 Pin | Description |
| :--- | :--- | :--- |
| **DEBUG UART TX** | **PA9** | Logs (Baud: 115200) |
| **DEBUG SWITCH** | **PB12** | Short to GND enables logs |
| **LED STATUS** | **PC13** | Blinks on transmission (Built-in) |

## 📡 Telemetry

The repeater identifies itself with the callsign: `NOCALL-1` (default).
Default coordinates (Null Island/Test): `!0100.00N/00100.00E`.
Telemetry frame format (sent every 1 hour):
```text
!0100.00N/00100.00E#NOCALL-1 BAT:3.42V R_CNT:0
```
* **Coordinates:** 51.737N, 19.574E (encoded in NMEA format).
* **Voltage:** Internal reference voltage (VREFINT) reading converted to supply voltage (VDDA).
* **R_CNT:** Reset counter from Backup Domain (BKP_DR1).

## 🛠️ Debugging

To view device operation:
* Connect a USB-UART converter to pins PA9 (RX converter) and GND.
* Short pin PB12 to ground (GND).
* Open a terminal (e.g., PuTTY, RealTerm) with a baud rate of 115200 bps.

Example logs:
```text
RX: Recv 77 bytes
RX CONTENT (TXT): <▒SP7FM-2>APLRG1,WIDE1-1:=L4@&ySI4l_ !GTracker via lora_aprs_reapeater|$E!=|
RX HEX: 3C FF 01 53 50 37 46 4D 2D 32 3E 41 50 4C 52 47 31 2C 57 49 44 45 31 2D 31 3A 3D 4C 34 40 26 79 53 49 34 6C 5F 20 21 47 54 72 61 63 6B 65 72 20 76 69 61 20 6C 6F 72 61 5F 61 70 72 73 5F 72 65 61 70 65 61 74 65 72 7C 24 45 21 3D 7C
QUEUE: Package added (77 B)
TX: Preparing to send...
TX msg. counter: 1
APRS CONTENT: <▒SP7FM-2>APLRG1,WIDE1-1:=L4@&ySI4l_ !GTracker via lora_aprs_reapeater|$E!=|
TX: Success
TX_RX: Switching TX module to RX mode for 10s response window...
TX_RX: Reply received on TX module (79 B)
TX_RX REPLY CONTENT: <▒SP7FM-2>APLRG1,SP7FM-10*:=L4@&ySI4l_ !GTracker via lora_aprs_reapeater|$E!=|
TX_RX: Retransmitting reply via RX module...
TX: Done.
```
If pin PB12 is open (High state - PullUp), the repeater operates "silently" on UART, saving processor time.

## ⚠️ Important Notes

* **Antennas:** Never power up the TX module without an antenna connected! This risks damaging the RFM96 chip.
* **Power Supply:** Ensure the 3.3V source has sufficient current capability (LoRa transmission can draw >100mA).
* **Separation:** Due to the close frequencies (100kHz spacing), physical separation of RX and TX antennas is recommended to prevent the transmitter from desensitizing the receiver, or use bandpass filters/duplexer.

## 📝 Compilation
Project prepared for STM32CubeIDE / STM32CubeMX / STM32CubeProgrammer.

* **MCU:** STM32F103C8Tx
* **Libraries:** HAL Driver
* **Language:** C (C99/GNU11)

## How to Build Custom Firmware

You don't need to install STM32CubeIDE or any toolchain locally!

1. **Fork** this repository to your GitHub account.
2. Go to the **Actions** tab in your forked repository and enable workflows if prompted.
3. Select **Build Custom APRS Firmware** from the workflow list and click **Run workflow**.
4. Fill in the form with your custom parameters (callsign, frequencies, power levels, etc.) and submit.
5. Once the build completes, download your ready-to-flash binary files (`.bin` / `.hex`) from the **Artifacts** section.

## 🔗 Sources

* https://stm32-base.org/boards/STM32F103C8T6-Blue-Pill

## 📷 Foto

![board_v1](./img/board_1.png)


---
Project created for the LoRa APRS network by SP7FM and SP7DW.


