# 임베디드 포트폴리오 면접 대비 Q&A (Level 1, UART 추가 후)

> **대상:** 프로젝트 개요, 전체 구조, 기술 선택과 Data Flow
>
> **답변 기준:** `STM32F103 + MPU6050 + UART 진단 인터페이스`의 실제 구현과 실물 검증만 사용합니다. SPI, RTOS, CAN, DMA는 구현한 기술로 답하지 않습니다.

---

## 1. 프로젝트 개요와 목표

### Q1-1. 이 프로젝트를 한 문장으로 설명해 주세요.

> **답변:**
>
> STM32F103에서 MPU6050의 6축 데이터를 I2C로 수집하고 Roll/Pitch를 계산한 뒤, PC로 10Hz Telemetry를 전송하고 UART Command로 상태를 조회하거나 Stream을 제어할 수 있게 만든 개인 Firmware 프로젝트입니다. 정상 동작뿐 아니라 Sensor 단절 감지, 자동 복구와 복구 후 Telemetry 재개까지 실물 Hardware에서 검증했습니다.

### Q1-2. 단순 Sensor 출력에서 UART 진단 인터페이스까지 확장한 이유는 무엇인가요?

> **답변:**
>
> Debugger의 변수 화면만으로는 장시간 동작, 전송 누락, 장애 발생 시점과 복구 과정을 남기기 어려웠습니다. 그래서 Sequence와 Timestamp를 포함한 UART Telemetry를 정의하고, PC에서 상태를 조회하고 Stream을 제어할 수 있는 양방향 진단 경로를 추가했습니다. 덕분에 감각적으로 동작을 보는 수준에서 원본 Log와 분석 결과로 동작을 다시 확인할 수 있는 구조로 확장했습니다.

### Q1-3. 본인이 담당한 범위는 어디까지인가요?

> **답변:**
>
> 개인 프로젝트로 요구사항 정리, STM32와 Sensor 배선, Firmware Module 설계와 구현, Build와 Flash, UART 시험 Script 작성, 실물 장애 시험과 결과 문서화까지 전 과정을 수행했습니다. 다만 CAN, RTOS, UART DMA, Binary Protocol은 이번 완료 범위에 포함하지 않았습니다.

---

## 2. Hardware 구성과 Interface 선택

### Q2-1. 전체 Hardware 구성과 Data 흐름을 설명해 주세요.

> **답변:**
>
> STM32F103C8T6이 I2C1 100kHz로 MPU6050 호환 Sensor의 14byte Data를 읽습니다. Firmware가 Raw 가속도와 Gyro 값을 변환하고 상보 필터로 Roll/Pitch를 계산합니다. 결과는 USART1 115200 baud, 8N1 설정으로 USB-to-TTL을 거쳐 PC에 전달됩니다. 반대 방향으로는 PC Command가 USART1 RX Interrupt를 통해 들어와 Stream과 상태 조회 기능을 제어합니다. ST-Link는 SWD 방식의 Build 결과 Flash와 Debug에 사용했습니다.

### Q2-2. I2C와 UART를 각각 선택한 이유는 무엇인가요?

> **답변:**
>
> MPU6050은 Register 기반 I2C Interface를 제공하고, 주소와 Register를 지정해 여러 축의 값을 한 번에 읽기 적합해 I2C를 사용했습니다. UART는 별도 Clock Line 없이 PC와 쉽게 연결할 수 있고, 사람이 읽을 수 있는 Log와 Command를 양방향으로 주고받기 쉬워 진단 Interface로 선택했습니다. 이번 프로젝트에는 SPI 장치를 사용하지 않았습니다.

### Q2-3. STM32F103C8T6을 선택한 이유는 무엇인가요?

> **답변:**
>
> 프로젝트에 필요한 I2C, UART, GPIO와 Interrupt Controller를 갖추고 있고, Cortex-M3 기반 STM32의 Peripheral 초기화와 HAL 동작을 학습하기에 적합했습니다. 실제 Build 결과도 RAM 2,352B, Flash 17,180B로 각각 20KB와 64KB 범위 안에 들어 요구 기능을 수행하기에 충분했습니다.

---

## 3. Software Architecture와 Data Flow

### Q3-1. Software를 어떤 Module로 나눴나요?

> **답변:**
>
> `mpu6050.c`는 Register 접근, 14byte Burst Read와 자세각 계산을 담당합니다. `telemetry.c`는 `IMU_Sample_t`를 CSV Record로 직렬화하고 Sequence를 관리합니다. `uart_console.c`는 RX Interrupt, 64byte Ring Buffer와 Command Parser를 담당합니다. `main.c`는 이 Module들을 조합해 20Hz Sampling, 10Hz Telemetry와 1Hz Recovery Probe를 Scheduling합니다.

### Q3-2. `main.c`에서 Module을 분리한 이유와 효과는 무엇인가요?

> **답변:**
>
> Sensor Register 처리, 통신 문자열 처리와 System 상태 전이를 한 파일에 두면 변경 영향 범위를 찾기 어려워집니다. 책임별로 분리해 Sensor Driver, Transport, Command 처리와 Scheduling의 경계를 명확히 했습니다. 특히 Sensor 결과를 `IMU_Sample_t`로 표현해 UART 문자열 형식과 Sensor 처리 로직이 직접 결합하지 않도록 했고, 향후 다른 Transport로 확장할 수 있는 경계를 만들었습니다.

### Q3-3. Sensor Data가 PC에 도달하는 과정을 순서대로 설명해 주세요.

> **답변:**
>
> Main Loop가 `HAL_GetTick()` 차이를 확인해 50ms마다 MPU6050의 14byte Register를 읽습니다. Driver가 Raw 6축 값을 복원하고 상보 필터로 Roll/Pitch를 갱신합니다. 100ms 주기가 되면 Main이 이를 `IMU_Sample_t`에 담고, Telemetry Module이 Sequence, Timestamp, Raw 값, 자세각과 상태를 CSV 한 줄로 만들어 UART TX로 전송합니다.

### Q3-4. PC에서 보낸 Command는 어떤 경로로 처리되나요?

> **답변:**
>
> USART1이 1byte를 수신하면 RX Callback이 그 Byte를 64byte Ring Buffer에 저장하고 다음 수신 Interrupt를 재무장전합니다. Main Loop의 `UART_Console_Process()`가 Buffer를 비우면서 한 줄을 조립하고, `status`, `stream on`, `stream off`를 판별해 System State를 변경하거나 응답을 전송합니다. 문자열 비교와 상태 변경은 ISR이 아니라 Main Context에서 수행합니다.

---

## 4. Scheduling과 설계 판단

### Q4-1. Sensor Sampling은 20Hz인데 Telemetry는 왜 10Hz인가요?

> **답변:**
>
> Sensor 수집과 외부 관측의 책임을 분리하기 위해 각각 50ms와 100ms 주기로 구성했습니다. 자세각 계산은 더 자주 갱신하면서도, 사람이 확인하는 Text Telemetry의 전송량은 낮출 수 있습니다. 현재 주기는 제품 요구사항에서 도출한 절대값이라기보다 이번 Prototype의 설계값이며, 60초 시험으로 실제 10Hz 유지 여부를 검증했습니다.

### Q4-2. RTOS를 사용했나요? 여러 주기는 어떻게 처리했나요?

> **답변:**
>
> RTOS는 사용하지 않았습니다. Bare-metal Super-loop에서 `HAL_GetTick()`의 현재 값과 작업별 마지막 실행 시점의 차이를 비교하는 Cooperative Scheduling을 사용했습니다. 현재 작업 수와 부하에서는 이 구조로 목표 주기를 만족했고, 60초 동안 100ms 간격의 Telemetry 600건을 확인했습니다. 작업이 많아지고 우선순위와 Deadline 관리가 복잡해지면 RTOS 도입을 다시 검토할 수 있습니다.

---

## 5. 결과와 한계

### Q5-1. 프로젝트가 정상 동작한다고 무엇으로 증명했나요?

> **답변:**
>
> 60초 동안 10Hz Telemetry 600건을 수집해 Sequence 누락 0건, Parsing 실패 0건과 100ms 간격을 확인했습니다. Command, 31자 초과 입력, 512byte Burst, 실행 중 SDA 단절과 재연결도 별도 시나리오로 시험했습니다. 원본 Log, 분석 Script와 Test Matrix를 함께 남겨 결과를 다시 확인할 수 있게 했습니다.

### Q5-2. 현재 구현의 가장 중요한 한계는 무엇인가요?

> **답변:**
>
> UART RX는 Interrupt와 Ring Buffer로 분리했지만 TX는 20ms Timeout의 `HAL_UART_Transmit()`을 사용하는 Blocking 방식입니다. 또한 60초와 512byte Burst 시험은 Prototype 검증으로는 의미가 있지만 장시간 Soak Test나 전기적 Noise 내성을 증명하지는 않습니다. 따라서 현재 결과를 양산 수준 신뢰성으로 과장하지 않고, 다음 단계에서는 TX 부하 측정, UART Error 처리와 장시간 반복 시험을 추가해야 합니다.
