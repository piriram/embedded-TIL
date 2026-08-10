# 임베디드 포트폴리오 면접 대비 Q&A (Level 2, UART 추가 후)

> **대상:** UART Interrupt, Ring Buffer, Parser, Scheduling과 C 구현 세부
>
> **답변 기준:** Source Code에서 확인되는 구현만 설명합니다. UART RX는 Interrupt 기반이고 TX는 Blocking 방식입니다.

---

## 1. Polling과 Interrupt

### Q1-1. 어떤 작업에 Polling을 사용했고 어떤 작업에 Interrupt를 사용했나요?

> **답변:**
>
> UART RX는 Byte가 언제 도착할지 모르므로 `HAL_UART_Receive_IT()`를 사용한 Event-driven Interrupt 방식으로 처리했습니다. 반면 Sensor Sampling, Telemetry 발행과 Recovery Probe는 Main Loop에서 `HAL_GetTick()` 차이를 확인하는 주기 Polling 방식으로 Scheduling했습니다. 입력 Event는 놓치지 않으면서 주기 작업은 단순하게 관리하려는 구분입니다.

### Q1-2. UART RX ISR에서는 정확히 무엇을 하나요?

> **답변:**
>
> 수신된 1byte를 Ring Buffer에 Enqueue하고, Buffer가 가득 찼으면 Overflow Counter를 증가시킨 뒤 `HAL_UART_Receive_IT()`로 다음 1byte 수신을 재무장전합니다. 문자열 비교, 응답 전송, Sensor 접근과 상태 변경은 수행하지 않습니다. ISR 실행 시간을 짧게 유지하고 실제 처리는 Main Context로 넘기기 위한 구조입니다.

### Q1-3. 왜 한 번에 1byte씩 Interrupt 수신하도록 구현했나요?

> **답변:**
>
> Command 길이가 가변이고 Line 종료 문자인 CR 또는 LF를 기준으로 처리하기 때문에 1byte 수신 방식이 구현과 검증에 단순했습니다. 다만 Byte마다 Interrupt가 발생하므로 고속 또는 대용량 입력에는 비효율적입니다. 현재 115200 baud의 짧은 Command Interface에서는 시험을 통과했지만, 부하가 커지면 DMA Circular Buffer와 IDLE Line 검출을 검토할 수 있습니다.

---

## 2. Ring Buffer와 공유 Data

### Q2-1. Ring Buffer를 사용한 이유와 동작 원리를 설명해 주세요.

> **답변:**
>
> UART Byte가 들어오는 시점과 Main Loop가 Command를 처리하는 시점을 분리하기 위해 사용했습니다. ISR은 `head` 위치에 Byte를 저장하고 다음 위치로 이동하며, Main은 `tail` 위치의 Byte를 읽고 이동합니다. 다음 `head`가 `tail`과 같으면 Full로 판단해 새 Byte를 버리고 Overflow Counter를 증가시킵니다. 배열 크기는 64byte이고 Full과 Empty를 구분하기 위해 한 칸을 비우므로 실제 저장 가능량은 63byte입니다.

### Q2-2. `head`, `tail`, `overflow_count`에 `volatile`을 붙인 이유는 무엇인가요?

> **답변:**
>
> ISR과 Main Context에서 값이 비동기적으로 바뀌므로 Compiler가 값을 Register에 고정해 두지 않고 매번 Memory에서 읽고 쓰게 하려는 목적입니다. 다만 `volatile`은 상호 배제나 모든 연산의 원자성을 보장하는 Keyword가 아닙니다. 이 구현은 ISR이 `head`를, Main이 `tail`을 갱신하는 Single Producer/Single Consumer 구조로 공유 쓰기를 줄였습니다.

### Q2-3. Buffer가 가득 차면 어떻게 되나요?

> **답변:**
>
> 기존 Data를 덮어쓰지 않고 새 Byte를 버리며 `overflow_count`를 증가시킵니다. `status` Command로 Counter를 확인할 수 있습니다. 다만 실제 512byte Burst 시험에서는 Counter가 0이어서 Overflow 분기 자체가 실행됐다고 주장할 수는 없습니다. 확인된 사실은 Burst 중 System과 10Hz Telemetry가 유지됐다는 범위입니다.

---

## 3. Command Parser

### Q3-1. Command 한 줄은 어떻게 완성하고 판별하나요?

> **답변:**
>
> Main Loop가 Ring Buffer에서 Byte를 꺼내 `cmd_line`에 누적합니다. CR 또는 LF가 들어오면 문자열 끝에 Null 문자를 추가하고 `status`, `stream on`, `stream off`와 비교합니다. 정의되지 않은 문자열에는 `ERR,INVALID_COMMAND`를 반환합니다. CRLF가 연속으로 들어와도 첫 종료 문자에서 처리한 뒤 두 번째 빈 Line은 무시합니다.

### Q3-2. 31자를 초과한 Command는 왜 나머지 Line까지 버리나요?

> **답변:**
>
> 초과 시점에 Buffer만 초기화하면 남은 Byte가 새로운 Command처럼 해석돼 Error가 반복될 수 있습니다. 그래서 `ERR,COMMAND_TOO_LONG`을 한 번 전송한 뒤 `discard_until_eol` 상태로 전환하고, 다음 CR 또는 LF까지 버립니다. 한 입력 Line에 Error 응답이 한 번만 대응하도록 경계를 명확히 한 것입니다.

### Q3-3. `status` Command로 무엇을 확인할 수 있나요?

> **답변:**
>
> Sensor 상태, Stream ON/OFF, Telemetry Rate와 RX Overflow Counter를 확인할 수 있습니다. 예를 들면 `STATUS,sensor=OK,stream=ON,rate=10,overflow=0` 형태입니다. 현장에서 Debugger를 연결하지 않고도 주요 Runtime 상태를 확인하기 위한 최소 진단 정보입니다.

---

## 4. UART TX와 Protocol

### Q4-1. Telemetry Record에 Sequence와 Timestamp를 넣은 이유는 무엇인가요?

> **답변:**
>
> 값만 전송하면 일부 Line이 누락되거나 주기가 흔들려도 찾기 어렵습니다. Sequence로 누락, 중복과 역순을 검사하고, `t_ms` 차이로 실제 전송 간격과 Rate를 계산하도록 했습니다. 이 Field를 이용해 60초 Log에서 Seq 8~607, 누락 0건과 100ms 간격을 확인했습니다.

### Q4-2. Roll/Pitch를 왜 `float` 문자열 대신 0.01도 단위 정수로 보냈나요?

> **답변:**
>
> 내부 계산 결과에 100을 곱해 `int16_t`인 `roll_cdeg`, `pitch_cdeg`로 직렬화했습니다. 소수 둘째 자리까지의 표현을 유지하면서 Target의 `printf` Float Formatting 의존성과 문자열 길이를 줄이기 위한 선택입니다. 수신 측은 값을 100으로 나누면 각도로 복원할 수 있습니다.

### Q4-3. UART TX도 비동기 방식인가요?

> **답변:**
>
> 아닙니다. RX는 Interrupt 기반이지만 TX는 `HAL_UART_Transmit()`과 20ms Timeout을 사용하는 Blocking 방식입니다. 현재 10Hz Text Telemetry에서는 실측 주기를 만족했지만, 전송량이나 Deadline이 늘어날 때는 TX Interrupt 또는 DMA 방식으로 바꾸고 전송 Queue를 두는 것이 적절합니다.

---

## 5. DMA와 RTOS 적용 판단

### Q5-1. 왜 UART DMA를 적용하지 않았나요?

> **답변:**
>
> DMA가 항상 더 좋은 것이 아니라 전송량, CPU 점유와 Timing 요구로 필요성을 판단해야 한다고 봤습니다. 현재는 10Hz Text Telemetry와 짧은 Command를 처리하며 60초 연속 전송과 Burst 시험에서 목표 동작을 만족했습니다. 측정된 병목 없이 DMA를 추가하면 Buffer 소유권과 Callback 상태 관리만 복잡해질 수 있어 이번 범위에서는 제외했습니다.

### Q5-2. RTOS 없이 공유 자원 충돌을 어떻게 관리했나요?

> **답변:**
>
> 현재는 단일 Main Context에서 Command Parsing, Sensor 접근과 TX를 순차 실행하고, ISR은 RX Buffer 생산만 담당합니다. 여러 Task가 같은 I2C나 UART를 동시에 사용하는 구조가 아니므로 Mutex를 사용하지 않았습니다. 향후 RTOS와 여러 Producer를 도입하면 Peripheral 소유권, Queue와 Mutex 정책을 별도로 설계해야 합니다.
