flowchart TD
    Start([START]) --> InitHAL[Inicjalizacja HAL, zegarów i peryferii<br/>GPIO, SPI1, USART1, ADC1, IWDG, RTC]
    InitHAL --> ReadBKP[Odczyt reset_counter z RTC BKP<br/>Inkrementacja jeśli reset od IWDG]
    ReadBKP --> InitLoRa[Inicjalizacja modułów LoRa:<br/>- RX: 434.855 MHz, Continuous RX<br/>- TX: 434.955 MHz, Sleep]
    InitLoRa --> BlinkLED[Mignięcie LED PC13]
    BlinkLED --> TelemetryInit[Wygenerowanie i dodanie<br/>pierwszej telemetrii do kolejki]
    TelemetryInit --> MainLoop

    %% PĘTLA GŁÓWNA
    subgraph MainLoop [Pętla Główna - while 1]
        
        %% SECTION 1: SYSTEM & HEALTH
        Sec1_ResetCheck{Zrestartować MCU?<br/>HAL_GetTick - lastReboot > reset_time}
        Sec1_ResetCheck -- Tak --> SysReset[NVIC_SystemReset]
        Sec1_ResetCheck -- Nie --> CheckRadios[Sprawdzenie reformatu 0x42<br/>dla loraRX i loraTX]
        
        CheckRadios --> HealthCheck{Oba moduły<br/>odpowiadają?}
        HealthCheck -- Tak --> FeedWDT1[HAL_IWDG_Refresh]
        HealthCheck -- Nie --> ResetFailedRadio[Reset sprzętowy RST i ponowna<br/>inicjalizacja zawieszonego modułu]
        ResetFailedRadio --> CheckRecovered{Czy oba działają?}
        CheckRecovered -- Tak --> FeedWDT2[HAL_IWDG_Refresh]
        CheckRecovered -- Nie --> Sec2_RX

        FeedWDT1 --> Sec2_RX
        FeedWDT2 --> Sec2_RX

        %% SECTION 2: RECEIVING
        Sec2_RX{packetReceivedFlag == 1?}
        Sec2_RX -- Tak --> ClearRXFlag[packetReceivedFlag = 0]
        ClearRXFlag --> ReadRX[Pobranie pakietu z loraRX<br/>LoRa_Receive]
        ReadRX --> RXLenCheck{Długość > 0?}
        RXLenCheck -- Tak --> DebugRX[Print RX text/hex]
        DebugRX --> PushQueue[Queue_Push: Dodaj pakiet do kolejki]
        PushQueue --> SetRXCont[Ustaw loraRX w MODE_RX_CONTINUOUS]
        RXLenCheck -- Nie --> SetRXCont
        SetRXCont --> Sec3_TX
        Sec2_RX -- Nie --> Sec3_TX

        %% SECTION 3: TRANSMITTING
        Sec3_TX{QueueHead != QueueTail?<br/>Kolejka nie pusta}
        Sec3_TX -- Tak --> PopQueue[Queue_Pop: Pobierz pakiet do txBuffer]
        PopQueue --> LED_ON[LED ON - PC13 Low]
        LED_ON --> SendTX[LoRa_Send: Nadaj przez loraTX]
        SendTX --> TX_Success{Nadanio pomyślnie?}

        TX_Success -- Tak --> InitTX_RX[Przełącz loraTX w tryb RX<br/>na 10 sekund]
        InitTX_RX --> StartWindowTimer[waitStart = HAL_GetTick]

        %% SUB-LOOP 10S WINDOW
        subgraph Window10s [Okno Odpowiedzi - 10s Loop]
            W_FeedWDT[HAL_IWDG_Refresh] --> W_CheckRX{Odbiór na loraRX?}
            W_CheckRX -- Tak --> W_PushRX[Pobierz i dodaj do kolejki]
            W_PushRX --> W_CheckTX
            W_CheckRX -- Nie --> W_CheckTX{Odbiór odpowiedzi na loraTX?}
            
            W_CheckTX -- Tak --> W_ReadTX[Pobierz odpowiedź z loraTX]
            W_ReadTX --> W_Retransmit[LoRa_Send: Przekaż odpowiedź przez loraRX]
            W_Retransmit --> W_SetRXCont[loraRX back to RX_CONTINUOUS]
            W_SetRXCont --> BreakWindow[txReplyReceived = 1<br/>Przerwij pętlę 10s]

            W_CheckTX -- Nie --> W_TimeCheck{Upłynęło 10 sekund?}
            W_TimeCheck -- Nie --> Delay5ms[HAL_Delay 5ms]
            Delay5ms --> W_FeedWDT
        end

        BreakWindow --> SleepTX[Uśpij loraTX: MODE_SLEEP]
        W_TimeCheck -- Tak --> SleepTX
        SleepTX --> LED_OFF[LED OFF - PC13 High]
        LED_OFF --> Sec4_Telemetry

        TX_Success -- Nie --> RetryCheck{msg_tx_counter < 3?}
        RetryCheck -- Tak --> RePush[Queue_Push: Ponów ze zwiększonym licznikiem]
        RetryCheck -- Nie --> DropPacket[Odrzuć pakiet]
        RePush --> LED_OFF
        DropPacket --> LED_OFF

        Sec3_TX -- Nie --> Sec4_Telemetry

        %% SECTION 4: TELEMETRY
        Sec4_Telemetry{HAL_GetTick - lastTelemetryTime<br/>> TELEMETRY_INTERVAL?}
        Sec4_Telemetry -- Tak --> SendTelem[SendTelemetry: Odczytaj VREFINT,<br/>zbuduj ramkę APRS i dodaj do kolejki]
        SendTelem --> UpdateTelemTime[lastTelemetryTime = HAL_GetTick]
        UpdateTelemTime --> Sec5_Sleep
        Sec4_Telemetry -- Nie --> Sec5_Sleep

        %% SECTION 5: SLEEP
        Sec5_Sleep{Kolejka pusta AND<br/>packetReceivedFlag == 0?}
        Sec5_Sleep -- Tak --> PWR_Sleep[HAL_PWR_EnterSLEEPMode<br/>Sleep Mode WFI]
        PWR_Sleep --> MainLoop
        Sec5_Sleep -- Nie --> MainLoop

    end
