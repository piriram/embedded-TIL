# 임베디드 포트폴리오 면접 대비 Q&A (Level 3, UART 추가 후)

> **대상:** 실제 UART/I2C Troubleshooting, 원인 분리와 검증 방법
>
> **답변 원칙:** 관찰한 현상, 추정한 원인, 적용한 해결과 검증 결과를 구분합니다.

---

## 1. UART RX Interrupt Troubleshooting

### Q1-1. UART 출력은 되는데 Command 입력에 반응하지 않았던 문제를 어떻게 해결했나요?

> **답변:**
>
> 먼저 TX가 정상이라는 사실로 Baud Rate와 PC 연결 전체가 완전히 끊긴 문제는 아니라고 범위를 줄였습니다. `HAL_UART_Receive_IT()` 호출 후에도 RX Callback에 진입하지 않는 것을 확인했고, USART1 NVIC Enable과 IRQ Handler 연결이 빠진 것을 찾았습니다. `HAL_UART_MspInit()`에서 IRQ Priority와 Enable을 설정하고 `USART1_IRQHandler()`가 `HAL_UART_IRQHandler()`를 호출하도록 연결한 뒤 ACK 응답으로 양방향 통신을 검증했습니다.

### Q1-2. Mac Terminal에서 Enter를 눌러도 Command가 처리되지 않았던 이유는 무엇인가요?

> **답변:**
>
> 초기 Parser가 LF만 Line 종료로 기대했지만 사용한 Terminal 환경에서는 CR이 들어왔습니다. 수신 Byte를 확인해 종료 문자 가정이 틀렸음을 찾았고, CR과 LF를 모두 종료 문자로 처리하도록 수정했습니다. CRLF가 들어오는 경우에도 빈 두 번째 Line은 무시하도록 했습니다.

### Q1-3. 긴 Command 뒤에 Error가 여러 번 발생한 원인은 무엇이었나요?

> **답변:**
>
> Command Buffer가 찼을 때 Index만 0으로 되돌리면 같은 Line의 남은 Byte가 새 Command로 해석됐습니다. 그래서 Too-long Error 뒤에 Invalid Command가 추가로 발생했습니다. 초과 시 `discard_until_eol`을 설정해 다음 개행까지 폐기하고, 한 Line당 `ERR,COMMAND_TOO_LONG`을 한 번만 반환하도록 고쳤습니다.

---

## 2. Firmware와 실물 상태 불일치

### Q2-1. Source를 수정했는데 보드 동작이 그대로였던 문제는 어떻게 판별했나요?

> **답변:**
>
> 처음에는 Parser 수정이 잘못됐다고 의심했지만, Session 시작 Timestamp가 약 427만 ms여서 보드가 최근 Reset되지 않았다는 사실을 확인했습니다. 이를 근거로 최신 Firmware가 Flash되지 않았다고 판단했습니다. STM32CubeProgrammer CLI로 Download, Verify와 Software Reset을 수행하고, Reset 뒤 낮아진 첫 `t_ms`와 변경된 응답으로 새 Firmware 실행을 확인했습니다.

### Q2-2. 이 경험에서 얻은 Debugging 원칙은 무엇인가요?

> **답변:**
>
> Source Code와 Target에서 실행 중인 Binary가 같다는 전제를 먼저 검증해야 한다는 점입니다. 이후에는 Build 성공만 보지 않고 Flash Verify, Reset 여부와 Boot/Timestamp처럼 실행 Image를 구분할 수 있는 증거를 확인합니다. 더 확장한다면 Firmware Version이나 Git Commit ID를 Boot Record에 넣는 방법도 고려할 수 있습니다.

---

## 3. Sensor 장애 감지와 자동 복구

### Q3-1. Sensor가 동작 중 분리되면 Firmware는 어떻게 반응하나요?

> **답변:**
>
> I2C Read 실패 시 Sensor 상태를 Offline으로 바꾸고 `ERR,SENSOR_OFFLINE`을 상태 전이 시점에 한 번 전송합니다. 복구 전에는 이전 자세값을 새 정상 Data처럼 발행하지 않고 IMU Telemetry를 중지합니다. Offline 상태에서는 1초마다 복구를 시도합니다.

### Q3-2. SDA를 다시 연결했는데도 Sensor가 복구되지 않은 원인을 어떻게 다뤘나요?

> **답변:**
>
> 단순 `WHO_AM_I` 재시도만으로는 복구되지 않았습니다. Signal이 돌아와도 STM32F1 I2C Peripheral에 BUSY/START 상태가 남아 있을 가능성을 원인 후보로 세웠습니다. 이 원인을 Register로 직접 확정한 것은 아니므로 가능성으로 표현합니다. Recovery Probe 전에 `HAL_I2C_DeInit()`과 `MX_I2C1_Init()`을 수행한 뒤 Sensor를 다시 초기화하도록 변경했습니다.

### Q3-3. 자동 복구가 실제로 됐다는 것을 어떻게 검증했나요?

> **답변:**
>
> Streaming 중 SDA Signal을 분리했을 때 Seq 18 뒤 `ERR,SENSOR_OFFLINE`이 한 번 발생하고 IMU가 멈추는 것을 확인했습니다. SDA 재연결 후에는 `OK,SENSOR_RECOVERED`가 한 번 발생했고 Seq 19~37의 IMU 19건이 연속으로 재개됐습니다. 따라서 장애 감지, 복구 Event와 Data 재개를 하나의 Log에서 확인했습니다.

---

## 4. 호환 Sensor와 Data 검증

### Q4-1. I2C 주소에는 응답하는데 Sensor 초기화가 실패했던 이유는 무엇인가요?

> **답변:**
>
> I2C Scan에서는 0x68 주소가 응답했지만 `WHO_AM_I`가 정품 MPU6050의 일반적인 값과 다른 0x72였습니다. 배선 불량으로 단정하지 않고 Scan 결과와 ID Register를 분리해 확인했고, 사용 중인 호환 Sensor의 실측 ID를 허용 목록에 추가했습니다. 무조건 모든 ID를 허용하지 않고 확인한 값만 명시적으로 추가했습니다.

### Q4-2. 60초 Telemetry의 무결성은 어떻게 분석했나요?

> **답변:**
>
> Python 분석 Script로 IMU Record와 Control Record를 구분하고, Field Parsing, Sequence 연속성, Timestamp 간격과 Status 분포를 계산했습니다. 결과는 유효 Record 600건, Seq 8~607, 누락 0건, Parsing 실패 0건, Min/Avg/Max 100ms와 Status OK 600건이었습니다. 원본 Log와 요약 결과를 함께 보존했습니다.

### Q4-3. 512byte Burst 시험으로 무엇을 증명했고 무엇은 증명하지 못했나요?

> **답변:**
>
> 연속 입력 중에도 System이 중단되지 않고 10Hz Telemetry가 유지되며, Too-long Error가 한 번만 발생하고 추가 Invalid Error가 생기지 않는 것을 확인했습니다. 하지만 Overflow Counter는 0이었으므로 실제 Ring Buffer Overflow 처리 분기가 동작했다고 증명한 시험은 아닙니다. 이 한계를 결과에 함께 기록했습니다.

---

## 5. Memory와 성능 판단

### Q5-1. 제한된 Memory를 어떻게 관리했나요?

> **답변:**
>
> 동적 할당은 사용하지 않고 64byte RX Ring Buffer, 32byte Command Buffer와 160byte TX Buffer를 고정 크기로 두었습니다. Build 결과 RAM은 2,352B/20KB, Flash는 17,180B/64KB였습니다. 다만 Build 사용량만으로 Stack 최악 사용량까지 증명되는 것은 아니므로, 양산 수준에서는 Stack Watermark나 정적 분석을 추가해야 합니다.

### Q5-2. 성능 최적화를 위해 실제로 적용한 것은 무엇인가요?

> **답변:**
>
> ISR에서는 Byte 저장과 RX 재무장전만 하고 문자열 Parsing을 Main으로 미뤘습니다. Sensor Sampling과 Telemetry 주기를 분리했으며, Roll/Pitch는 Text 전송 시 0.01도 단위 정수로 바꿔 Float Formatting 의존성과 전송량을 줄였습니다. 반면 CPU 사용률을 직접 측정하지 않았으므로 성능이 몇 퍼센트 개선됐다는 식의 수치는 주장하지 않습니다.
