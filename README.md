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

Settings are identical for RX and TX (except for frequency):

| Parameter | Value |
| :--- | :--- |
| **RX Frequency** | `434.855 MHz` |
| **TX Frequency** | `434.955 MHz` |
| **Spreading Factor (SF)** | `9` |
| **Bandwidth (BW)** | `125 kHz` |
| **Coding Rate (CR)** | `4/7` |
| **Tx Power** | `Max (0xFF)` |

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

## 🔗 Sources

* https://stm32-base.org/boards/STM32F103C8T6-Blue-Pill

## 📷 Foto

![board_v1](./img/board_1.png)


---
Project created for the LoRa APRS network by SP7FM and SP7DW.


