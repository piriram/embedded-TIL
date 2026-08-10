# 임베디드 포트폴리오 면접 대비 Q&A (Level 5, UART 추가 후)

> **대상:** 양산 관점의 신뢰성, 성능 경계, Test 자동화와 확장 판단
>
> **답변 기준:** 현재 구현과 양산 수준 개선안을 구분합니다. Watchdog, HardFault Dump, OTA, CI, DMA와 Binary Protocol은 구현 완료 기술로 주장하지 않습니다.

---

## 1. UART Interface의 신뢰성 경계

### Q1-1. 현재 UART 구조가 Traffic 증가에도 안전하다고 볼 수 있나요?

> **답변:**
>
> 현재 검증 범위에서는 115200 baud, 10Hz Text Telemetry와 짧은 Command를 처리했고 512byte Burst 중에도 System이 유지됐습니다. 하지만 RX는 Byte당 Interrupt가 발생하고 TX는 Blocking이므로 Traffic이 커지면 ISR 부하와 TX 대기 시간이 증가합니다. 양산 단계에서는 Worst-case 대역폭, CPU 사용률과 Latency를 측정한 뒤 DMA, IDLE Line 수신과 TX Queue 적용 여부를 결정해야 합니다.

### Q1-2. Text CSV Protocol의 장점과 한계는 무엇인가요?

> **답변:**
>
> 사람이 Terminal에서 바로 읽을 수 있고 Python으로 쉽게 Parsing할 수 있어 개발과 진단에 유리합니다. 반면 Binary보다 전송량이 크고, 현재 Protocol에는 Payload 길이와 CRC가 없어 Data 손상을 강하게 검출하기 어렵습니다. 제품 통신으로 확장한다면 Header, Version, Message Type, Length, Payload와 CRC를 갖춘 Frame을 설계하고, 진단용 Text Channel과 제품 Data Channel의 분리도 검토하겠습니다.

### Q1-3. UART Framing, Noise 또는 Overrun Error는 어떻게 복구하나요?

> **답변:**
>
> 현재 구현에는 UART Error Callback 기반의 명시적인 복구 정책이 없습니다. 이 부분은 한계입니다. 개선 시 `HAL_UART_ErrorCallback()`에서 Error Code를 기록하고 ORE, FE, NE 상태를 정리한 뒤 RX를 재무장전하겠습니다. 연속 오류 횟수와 마지막 오류 시각을 진단 정보로 남기고, 기준을 넘으면 UART Peripheral 재초기화 또는 System Recovery로 단계화하겠습니다.

---

## 2. Fail-safe와 장애 복구

### Q2-1. System이 Hang되면 자동으로 복구할 수 있나요?

> **답변:**
>
> 현재 Firmware에는 IWDG를 적용하지 않아 Hang 자동 복구를 구현했다고 말할 수 없습니다. 제품 수준으로 확장한다면 Main Loop가 단순히 순회했다는 이유만으로 Watchdog을 갱신하지 않고, Sensor Sampling, Command 처리와 주요 상태 머신의 정상 진행을 확인한 뒤 갱신하겠습니다. Reset 원인과 마지막 오류 상태도 Boot Log에 남겨 반복 장애를 분석할 수 있게 하겠습니다.

### Q2-2. HardFault가 발생했을 때 원인을 추적할 장치가 있나요?

> **답변:**
>
> 현재 HardFault Register Dump는 구현하지 않았습니다. 개선한다면 Fault 진입 시 Stack Frame의 PC, LR과 xPSR, SCB의 CFSR, HFSR, BFAR, MMFAR를 Reset 후에도 확인 가능한 영역에 저장하겠습니다. UART 자체 문제로 Fault가 발생했을 수 있으므로 Fault Handler에서 무조건 UART 출력에 의존하기보다 최소 정보 저장 후 Reset하고 다음 Boot에서 보고하는 방식을 우선 검토하겠습니다.

### Q2-3. Sensor 자동 복구가 무한히 반복되면 문제가 되지 않나요?

> **답변:**
>
> 현재는 Offline 동안 1Hz로 계속 I2C와 Sensor 재초기화를 시도합니다. 개발용 Prototype에서는 재연결 확인에 단순하지만, 제품에서는 전력과 Bus 안정성에 영향을 줄 수 있습니다. 연속 실패 횟수, Exponential Backoff, Recovery 단계와 영구 Fault 상태를 정의하고, 복구 횟수와 마지막 원인을 진단 정보로 보존하는 방식이 필요합니다.

---

## 3. 검증과 자동화

### Q3-1. Module 변경이 기존 동작을 깨뜨리지 않았다고 어떻게 확인했나요?

> **답변:**
>
> ARM GCC Release Build와 실물 Flash Verify 후, Python Script로 60초 Telemetry, Command, Burst와 대화형 Recovery Test를 수행했습니다. 분석 Script가 Sequence, Timing, Parsing과 Status를 계산하고, Test Matrix에 기대 결과와 실제 결과를 나란히 기록했습니다. 자세 변화도 평면, 오른쪽 90도, 앞쪽 90도 절차로 다시 확인했습니다.

### Q3-2. 이것을 Unit Test나 CI라고 부를 수 있나요?

> **답변:**
>
> 현재는 Local Build와 Hardware 통합 시험 자동화이며 완전한 Unit Test나 CI Pipeline은 아닙니다. CI로 확장한다면 Push마다 Cross Build를 수행하고, Hardware와 분리 가능한 Parser와 Serializer는 Host 환경 Unit Test로 검증하겠습니다. 실제 UART와 Sensor Fault Injection은 장비가 필요한 HIL Test로 분리해 별도 Runner에서 수행하는 것이 적절합니다.

### Q3-3. 60초 600건 시험의 한계는 무엇인가요?

> **답변:**
>
> 목표 10Hz와 짧은 기간의 연속성은 확인했지만 Memory 누수, Counter Wrap-around, 열화와 간헐 오류까지 판단하기에는 짧습니다. 양산 수준에서는 수 시간 또는 수일 Soak Test, 반복 전원 인가, 다양한 Baud 오차와 Noise 조건, 수천 회 Sensor 단절 및 복구 시험을 추가하고 실패율과 복구 시간을 통계로 남겨야 합니다.

---

## 4. Resource와 성능 고도화

### Q4-1. DMA를 도입한다면 RX와 TX 중 어디부터 적용하겠습니까?

> **답변:**
>
> 먼저 측정으로 병목을 확인하겠지만, 대량의 가변 길이 RX가 요구된다면 DMA Circular Buffer와 UART IDLE Line 검출 조합을 우선 검토하겠습니다. TX가 커지거나 주기가 빨라진다면 Message Queue와 DMA TX로 Main Context의 Blocking 시간을 제거하겠습니다. DMA 완료 전 Buffer를 재사용하지 않도록 소유권과 Queue 상태를 함께 설계해야 합니다.

### Q4-2. 현재 Memory 사용량만 보고 여유가 충분하다고 판단할 수 있나요?

> **답변:**
>
> Build 결과 RAM 11.48%, Flash 26.21%는 정적 사용량 관점의 여유만 보여줍니다. ISR 중첩과 함수 호출에 따른 Worst-case Stack, Library 내부 Stack 사용량과 향후 기능 증가까지 보장하지 않습니다. Linker Map, Stack Usage 분석과 Runtime Watermark를 함께 확인해야 안전 여유를 판단할 수 있습니다.

---

## 5. 유지보수와 확장

### Q5-1. 출하 후 Firmware Update는 어떻게 할 계획인가요?

> **답변:**
>
> 현재 Bootloader나 OTA는 구현하지 않았습니다. 제품 요구가 생기면 Bootloader와 Application 영역을 분리하고 Image Size, Version, CRC 또는 Signature를 검증한 뒤 정상 Image로만 Jump하도록 설계해야 합니다. Update 중 전원 차단에 대비해 기존 Image 보존이나 A/B Slot, Rollback 정책도 함께 정의해야 합니다.

### Q5-2. CAN을 추가할 때 현재 구조에서 재사용할 수 있는 부분은 무엇인가요?

> **답변:**
>
> Sensor Driver가 만든 Data를 `IMU_Sample_t`로 Transport와 분리했기 때문에 Sampling과 자세각 계산은 재사용할 수 있습니다. UART의 CSV Serializer를 그대로 CAN에 넣는 것이 아니라 필요한 Field와 해상도를 정해 CAN Frame으로 Packing하는 별도 Transport Module을 추가해야 합니다. CAN은 아직 구현하지 않았으므로 확장 가능한 경계를 설명할 뿐 완료 기술로 주장하지 않습니다.

### Q5-3. 이 프로젝트를 양산 수준으로 올릴 때 우선순위를 정한다면요?

> **답변:**
>
> 첫째, UART Error 처리와 Watchdog, Reset 원인 기록으로 장애 관측성을 보강하겠습니다. 둘째, 장시간 시험과 반복 Fault Injection으로 실패율과 복구 시간을 측정하겠습니다. 셋째, 측정된 부하에 따라 DMA와 Binary Protocol을 결정하겠습니다. 마지막으로 안전한 Firmware Update와 HIL 자동화를 추가하겠습니다. 기능 수를 늘리기보다 실패를 발견하고 복구하며 증거를 남기는 순서로 고도화하겠습니다.
