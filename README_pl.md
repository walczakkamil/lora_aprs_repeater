# STM32 LoRa APRS Repeater (Bluepill + 2x RFM96W)

## 📡 O projekcie

Prosty, energooszczędny **Repeter LoRa APRS** oparty na mikrokontrolerze STM32F103C8T6 (Bluepill) oraz dwóch modułach radiowych RFM96W (SX1278). Urządzenie działa w trybie "Cross-Band" (odbiera na jednej częstotliwości, nadaje na innej) i posiada funkcje telemetrii oraz watchdoga.

## 🚀 Możliwości i Funkcje

* **Podwójne radio:** Niezależne moduły dla RX (odbioru z trackera) i TX (nadawania do iGate`a).
* **Ciągły nasłuch (RX Continuous):** Nie przegapisz żadnej ramki.
* **Buforowanie (Kolejka):** Kolejka FIFO na 5 pakietów – zapobiega utracie danych, gdy przychodzi wiele ramek naraz.
* **Transparentność:** Przekazuje surowe ramki LoRa (włącznie z nagłówkami `3C FF 01`), dzięki czemu jest kompatybilny z większością trackerów i bramek iGate.
* **Inteligentny Watchdog (IWDG):** System automatycznego resetu w przypadku zawieszenia procesora.
* **Sanity Check Radia:** Autorski mechanizm monitorowania stanu modułów radiowych. W przypadku wykrycia zawieszenia nadajnika (np. przez błędy SPI lub Brown-out), system automatycznie wykonuje twardy reset modułu RF.
* **Licznik Resetów (R_CNT):** Statystyka resetów (Watchdog/Radio) przechowywana w rejestrach Backup (BKP), która przetrwa reset urządzenia, a zeruje się tylko przy całkowitym zaniku zasilania.
* **Energooszczędność:** Procesor przechodzi w tryb `SLEEP` (WFI), gdy nie przetwarza danych.
* **Telemetria:** Automatyczne wysyłanie statusu stacji co 1h (napięcie zasilania, koordynaty, licznik resetów).
* **Tryb Debug:** Podgląd na żywo odbieranych i wysyłanych ramek przez UART po zwarciu zworki serwisowej.

## ⚙️ Parametry Radiowe (LoRa)

Ustawienia są identyczne dla RX i TX (z wyjątkiem częstotliwości):

| Parametr | Wartość |
| :--- | :--- |
| **Częstotliwość RX** | `434.855 MHz` |
| **Częstotliwość TX** | `434.955 MHz` |
| **Spreading Factor (SF)** | `9` |
| **Bandwidth (BW)** | `125 kHz` |
| **Coding Rate (CR)** | `4/7` |
| **Moc nadawania** | `Max (0xFF)` |

## 🔌 Schemat Połączeń (Pinout)

Urządzenie wykorzystuje magistralę **SPI1** współdzieloną przez oba moduły radiowe.

### Moduł 1: Odbiornik (RX - 434.855 MHz)
| Pin RFM96W | Pin STM32 (Bluepill) | Uwagi |
| :--- | :--- | :--- |
| MISO | **PA6** | Wspólne SPI |
| MOSI | **PA7** | Wspólne SPI |
| SCK | **PA5** | Wspólne SPI |
| NSS (CS) | **PA4** | Chip Select |
| RST | **PB0** | Reset |
| DIO0 | **PB1** | Przerwanie (EXTI1) |
| 3.3V | 3.3V | |
| GND | GND | |

### Moduł 2: Nadajnik (TX - 434.955 MHz)
| Pin RFM96W | Pin STM32 (Bluepill) | Uwagi |
| :--- | :--- | :--- |
| MISO | **PA6** | Wspólne SPI |
| MOSI | **PA7** | Wspólne SPI |
| SCK | **PA5** | Wspólne SPI |
| NSS (CS) | **PA3** | Chip Select |
| RST | **PB10** | Reset |
| DIO0 | **PB11** | Przerwanie (EXTI15) |
| 3.3V | 3.3V | |
| GND | GND | |

### Pozostałe
| Funkcja | Pin STM32 | Opis |
| :--- | :--- | :--- |
| **DEBUG UART TX** | **PA9** | Logi (Baud: 115200) |
| **DEBUG SWITCH** | **PB12** | Zwarcie do GND włącza logi |
| **LED STATUS** | **PC13** | Miga przy nadawaniu (Wbudowana) |

## 📡 Telemetria

Repeter przedstawia się znakiem: `NOCALL-1` (domyślnie).
Domyślne koordynaty (Null Island/Test): `!0100.00N/00100.00E`.
Format ramki telemetrycznej (wysyłanej co 1 godzinę):
```text
!0100.00N/00100.00E#NOCALL-1 BAT:3.42V R_CNT:0
```
* **Współrzędne:** 51.737N, 19.574E (zakodowane w formacie NMEA).
* **Napięcie:** Odczyt wewnętrznego napięcia odniesienia (VREFINT) przeliczony na napięcie zasilania (VDDA).
* **R_CNT:** Licznik resetów odczytany z domeny Backup (BKP_DR1).

## 🛠️ Debugowanie

Aby podejrzeć pracę urządzenia:
* Podłącz konwerter USB-UART do pinów PA9 (RX konwertera) i GND.
* Zewrzyj pin PB12 do masy (GND).
* Otwórz terminal (np. PuTTY, RealTerm) z prędkością 115200 bps.
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

Jeżeli pin PB12 jest rozwarty (stan wysoki - PullUp), repeter działa "po cichu" na UART, oszczędzając czas procesora.

## ⚠️ Ważne uwagi

* **Anteny:** Nigdy nie uruchamiaj modułu TX bez podłączonej anteny! Grozi to uszkodzeniem układu RFM96.
* **Zasilanie:** Upewnij się, że źródło 3.3V ma wystarczającą wydajność prądową (nadawanie LoRa potrafi pobrać >100mA).
* **Separacja:** Ze względu na bliskość częstotliwości (100kHz odstępu), zaleca się fizyczną separację anten RX i TX, aby nadajnik nie "ogłuszał" odbiornika, lub zastosowanie filtrów pasmowych/dupleksera.

## 📝 Kompilacja

Projekt przygotowany dla STM32CubeIDE / STM32CubeMX / STM32CubeProgrammer.

* **MCU:** STM32F103C8Tx
* **Biblioteki:** HAL Driver
* **Język:* C (C99/GNU11)

## 🔗 Źródła

* https://stm32-base.org/boards/STM32F103C8T6-Blue-Pill

## 📷 Foto

![board_v1](./img/board_1.png)

---
Projekt stworzony na potrzeby sieci LoRa APRS przez SP7FM oraz SP7DW.
