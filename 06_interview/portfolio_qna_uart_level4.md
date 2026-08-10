# 임베디드 포트폴리오 면접 대비 Q&A (Level 4: 종합 모의 면접, UART 추가 후)

> **대상:** 실제 면접에서 Architecture 설명이 구현, 장애 대응과 한계 질문으로 깊어지는 흐름
>
> **활용법:** 먼저 각 질문에 소리 내어 답한 뒤 예시 답변과 비교합니다. 모르는 내용을 구현했다고 꾸미지 않고 확인한 범위와 한계를 함께 말합니다.

---

## 시나리오 1. Architecture에서 UART 구현까지

**면접관:** “프로젝트의 전체 Data Flow를 30초 안에 설명해 주세요.”

> **답변:** STM32F103이 MPU6050 Data를 I2C 100kHz로 20Hz Sampling하고, 상보 필터로 Roll/Pitch를 계산합니다. 결과는 `IMU_Sample_t`를 거쳐 10Hz CSV Telemetry로 PC에 전송합니다. PC Command는 UART RX Interrupt, 64byte Ring Buffer와 Main Context Parser를 거쳐 Stream과 상태 조회를 제어합니다.

**면접관:** “왜 Sensor는 20Hz인데 UART는 10Hz인가요?”

> **답변:** Sensor 갱신과 외부 관측 주기를 분리했습니다. 내부 자세값은 50ms마다 갱신하면서 사람이 보는 Text Log는 100ms마다 전송해 통신량을 낮췄습니다. 이 값은 Prototype 설계값이며, 60초 시험에서 실제 10Hz가 유지되는지 검증했습니다.

**면접관:** “UART를 비동기로 구현했다고 했는데 TX도 비동기입니까?”

> **답변:** 정확히는 RX가 Interrupt 기반 비동기 구조입니다. TX는 `HAL_UART_Transmit()`과 20ms Timeout을 사용하는 Blocking 방식입니다. 현재 10Hz에서는 목표 주기를 만족했지만, 부하가 증가하면 TX DMA 또는 Interrupt와 전송 Queue가 필요합니다.

**면접관:** “왜 처음부터 DMA를 쓰지 않았나요?”

> **답변:** 현재 전송량에서 병목이 측정되지 않았고 60초 연속 시험도 통과했기 때문입니다. 필요성이 확인되지 않은 DMA를 먼저 넣기보다 단순한 구조로 검증한 뒤 CPU 점유나 전송 지연이 문제가 될 때 적용하려고 했습니다.

---

## 시나리오 2. ISR, Ring Buffer와 동시성 압박

**면접관:** “RX Callback 안에서 Command Parsing까지 하면 안 되나요?”

> **답변:** 문자열 비교와 응답 TX가 길어지면 ISR 점유 시간이 늘고 다른 Interrupt 처리를 지연시킬 수 있습니다. 그래서 ISR은 Byte Enqueue와 다음 수신 재무장전만 하고, Parsing과 상태 변경은 Main Context에서 수행합니다.

**면접관:** “Ring Buffer의 Full과 Empty를 어떻게 구분하나요?”

> **답변:** `head == tail`이면 Empty이고, 다음 `head`가 `tail`과 같으면 Full로 판단합니다. 그래서 64byte 배열 중 실제 저장 가능량은 63byte입니다. Full이면 기존 Data를 덮어쓰지 않고 새 Byte를 버리며 Counter를 증가시킵니다.

**면접관:** “`volatile`을 붙이면 Race Condition이 모두 해결되나요?”

> **답변:** 아닙니다. `volatile`은 Compiler가 Memory 접근을 생략하거나 캐싱하지 않게 할 뿐 상호 배제와 복합 연산의 원자성을 보장하지 않습니다. 현재는 ISR만 `head`를, Main만 `tail`을 갱신하는 Single Producer/Single Consumer 구조로 공유 쓰기를 줄였습니다. 구조가 복잡해지면 Critical Section이나 Queue 정책을 추가로 검토해야 합니다.

**면접관:** “512byte를 보냈는데 64byte Buffer가 왜 Overflow되지 않았나요?”

> **답변:** Serial 입력과 동시에 Main Loop가 Buffer를 계속 소비했기 때문에 이번 시험에서는 Counter가 증가하지 않았습니다. 따라서 512byte 시험은 연속 입력 중 System 유지와 Parser 복구를 확인한 것이지, Overflow 분기 실행을 증명한 시험은 아닙니다.

---

## 시나리오 3. 장애 감지와 복구

**면접관:** “Sensor Cable이 빠지면 어떤 일이 생기나요?”

> **답변:** I2C Read 실패 시 Offline으로 상태 전이하고 `ERR,SENSOR_OFFLINE`을 한 번 발행합니다. 복구되기 전에는 오래된 자세값을 정상 Telemetry로 보내지 않고, 1Hz로 재연결을 시도합니다.

**면접관:** “Cable만 다시 꽂으면 바로 복구됐나요?”

> **답변:** 처음에는 복구되지 않았습니다. STM32F1 I2C Peripheral에 BUSY/START 상태가 남았을 가능성을 세우고, Probe 전에 I2C를 DeInit/Init한 뒤 Sensor를 다시 초기화하도록 수정했습니다. 이 원인은 Register로 확정한 것이 아니므로 가능성이라고 설명합니다.

**면접관:** “복구됐다는 근거는 무엇인가요?”

> **답변:** 실물 시험 Log에서 Seq 18 뒤 Offline과 IMU 중지를 확인했고, SDA 재연결 뒤 Recovered Event와 Seq 19~37의 연속된 IMU 19건을 확인했습니다. 장애 전후 Sequence가 이어지는 것까지 검증했습니다.

**면접관:** “그 시험만으로 현장 신뢰성을 보장할 수 있습니까?”

> **답변:** 아닙니다. 현재는 한 Hardware 구성에서 의도적으로 SDA를 분리하고 재연결한 기능 시험입니다. 장시간 반복, 전원 변동, Noise, 다양한 Cable 조건과 복구 실패 횟수 제한은 추가 검증이 필요합니다.

---

## 시나리오 4. 검증과 자기평가

**면접관:** “정상 동작을 눈으로 본 것과 검증한 것은 어떻게 다릅니까?”

> **답변:** 눈으로 몇 줄을 확인하는 대신 Sequence와 Timestamp가 있는 원본 Log를 수집하고 Script로 누락, Parsing과 주기를 계산했습니다. 60초 600건, Gap 0, Parsing 실패 0과 100ms 간격을 수치로 남겼고 Command와 장애 시험은 Test Matrix로 분리했습니다.

**면접관:** “현재 Architecture에 몇 점을 주겠습니까?”

> **답변:** Prototype 기준으로는 7점 정도입니다. Module 책임 분리, RX Interrupt, 장애 상태 전이와 재현 가능한 검증은 갖췄지만 TX가 Blocking이고 UART Error 처리, Watchdog, 장시간 시험과 실제 Overflow 재현이 빠져 있기 때문입니다.

**면접관:** “다시 설계한다면 무엇부터 바꾸겠습니까?”

> **답변:** 먼저 요구 전송량과 Worst-case 실행 시간을 측정하겠습니다. 그 결과에 따라 TX Queue와 DMA 적용 여부를 결정하고, UART Error Callback과 재초기화 정책, Firmware Version Record, 반복 가능한 Fault Injection Test를 추가하겠습니다. Binary Protocol이나 RTOS는 요구가 생긴 뒤 선택하겠습니다.
