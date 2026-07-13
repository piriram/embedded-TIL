# Ch.05 Timer / PWM ver4 — 코넬 노트: 시간 이벤트와 PWM

> **사용법:** 왼쪽 `단서·질문`만 보고 오른쪽 설명을 말해 본 뒤, 각 노트의 `요약`으로 답을 확인한다. 손필기할 때는 왼쪽 열을 약 1/3, 오른쪽 열을 약 2/3으로 나눈다.

**학습 목표:** 레지스터 값을 암기하기보다, **Timer가 시간을 만들고 → event가 ISR에 전달되며 → 긴 작업은 main이 처리하고 → PWM은 하드웨어가 파형을 만든다**는 흐름을 설명한다.

> **범위**
> - 지금 이해: `PSC`, `CNT`, `ARR`, `CCR`, Update Event, ISR, `volatile`, 100 ms event, PWM
> - 나중에: exception frame 세부 레지스터, FPU context, ARPE, center-aligned, complementary PWM, dead time, FreeRTOS timer service task

---

## 1. 코넬 노트 1 — Timer가 필요한 이유

| 단서·질문 (왼쪽 열) | 노트 (오른쪽 열) |
| --- | --- |
| **busy-wait delay의 문제는?** | CPU가 반복문으로 시간이 지났는지 계속 확인한다. `while (시간이_안_지남) { }` 동안 다른 작업을 하지 못한다. |
| **Timer는 무엇을 하는가?** | Timer peripheral hardware가 clock을 세고, 설정한 시점에 event를 만든다. CPU는 그 사이 application 작업을 하거나 sleep할 수 있다. |
| **polling과 Timer interrupt의 차이?** | polling은 CPU가 timeout을 반복 확인한다. Timer interrupt는 hardware가 시간 만료를 감지해 CPU에 알린다. 예를 들어 100 ms 센서 샘플링이나 1초 LED toggle에 쓴다. |
| **ISR에 긴 delay를 넣으면?** | polling 문제가 ISR 안으로 옮겨갈 뿐이다. ISR이 길어지면 main과 다른 interrupt의 응답도 늦어진다. |
| **Timer와 Counter는 어떻게 다른가?** | Timer는 내부 clock으로 시간/주기를 만들고, Counter는 외부 pin 신호의 횟수를 센다. 같은 Timer peripheral도 clock source에 따라 두 역할을 할 수 있다. |

> **주의**
> Timer는 단순 delay 함수가 아니라 시스템의 시간 기준을 제공하는 hardware다.

### 요약

- Timer는 CPU를 기다리게 하지 않고 시간 event를 만든다.
- `Timer = 내부 clock`, `Counter = 외부 신호 횟수`로 먼저 구분한다.

---

## 2. 코넬 노트 2 — `PSC → CNT → ARR` 시간 생성

| 단서·질문 (왼쪽 열) | 노트 (오른쪽 열) |
| --- | --- |
| **Timer의 시간 흐름은?** | `Timer clock → PSC → CNT → ARR → Update Event` 순서다. 계산도 이 순서로 생각한다. |
| **`PSC`의 역할은?** | `PSC`(Prescaler)는 timer clock을 나눠 `CNT`가 세는 속도를 낮춘다. register 값이 `N`이면 실제 분주비는 `N+1`이다. |
| **`CNT`, `ARR`은?** | `CNT`(Counter)는 현재 count 값이고, `ARR`(Auto-Reload Register)은 count의 끝값이다. `CNT`가 `ARR`에 도달하면 reload하며 Update Event를 만들 수 있다. |
| **왜 `+1`이 붙는가?** | count가 0부터 시작하기 때문이다. `ARR = M`이면 한 주기의 count 수는 `M+1`이다. |
| **주기·주파수 공식은?** | `T = (PSC+1) × (ARR+1) / timer_clk`<br>`f = timer_clk / ((PSC+1) × (ARR+1))` |
| **계산에서 흔한 실수는?** | `PSC` 또는 `ARR` 하나만으로 주기가 정해진다고 생각하는 것, 실제 `timer_clk`를 clock tree에서 확인하지 않는 것이다. |

![Timer clock, prescaler, counter, ARR, update event 흐름](./assets/filginote_05/timer_count_flow.svg)

### 요약

- `PSC`는 count 속도, `ARR`은 한 주기의 count 범위를 정한다.
- register 값은 0부터 시작하므로 `PSC+1`, `ARR+1` 규칙을 반드시 적용한다.

---

## 3. 코넬 노트 3 — Event가 ISR에 도달하는 조건

| 단서·질문 (왼쪽 열) | 노트 (오른쪽 열) |
| --- | --- |
| **Update Event가 생기면 곧바로 ISR인가?** | 아니다. Event 발생, interrupt enable, ISR 실행은 서로 다른 단계다. |
| **Update Event부터 handler까지의 흐름은?** | `CNT`가 `ARR`에 도달 → Update Event 발생 → `SR.UIF` flag set → `DIER.UIE` enable → NVIC가 IRQ 허용 → CPU가 handler 실행. |
| **Timer 설정의 큰 순서는?** | 1. Timer peripheral clock enable<br>2. `PSC`, `ARR` 설정<br>3. Update interrupt(`UIE`) enable<br>4. NVIC에서 해당 IRQ enable<br>5. Counter(`CEN`) 시작 |
| **handler가 실행되지 않는 대표 원인은?** | peripheral clock, `UIE`, NVIC 중 하나라도 빠진 경우다. |
| **ISR이 끝나면 CPU는?** | CPU는 main 흐름을 잠시 멈추고 vector table이 가리키는 ISR로 이동한다. ISR이 끝나면 hardware가 저장·복원한 실행 상태를 바탕으로 중단 지점으로 복귀한다. |

> **주의**
> 면접에서는 “hardware가 context를 저장·복원한다”까지 설명하면 충분하다.

### 요약

- `UIF`는 event의 기록, `UIE`는 interrupt 요청 허용, NVIC는 CPU IRQ 허용이다.
- 세 단계 중 하나라도 빠지면 ISR은 실행되지 않는다.

---

## 4. 코넬 노트 4 — ISR은 알리고, main은 처리한다

| 단서·질문 (왼쪽 열) | 노트 (오른쪽 열) |
| --- | --- |
| **Foreground / Background 구조란?** | `main()`의 `while(1)`은 background(application logic), Timer·GPIO·UART ISR은 background를 잠시 선점하는 foreground다. 작은 MCU에서는 super loop 또는 main + ISRs 구조라고 부른다. |
| **Timer ISR의 최소 동작은?** | `UIF` 확인·clear → `sample_due` flag 또는 event counter 기록 → return. 실제 sensor/CAN 작업은 main이 수행한다. |
| **ISR에서 피할 일은?** | 긴 delay, `printf`, I2C polling, 복잡한 CAN 처리다. ISR이 빠른 이유는 interrupt라서가 아니라 짧게 설계했기 때문이다. |
| **`volatile`은 왜 필요한가?** | ISR이 쓰고 main이 읽는 flag/counter에서 compiler가 read/write를 생략하지 않게 할 수 있다. |
| **`volatile`만으로 안전한가?** | 아니다. atomicity와 race condition을 해결하지 않는다. read-modify-write 또는 multi-byte 공유 데이터는 별도 보호 방법을 검토한다. |
| **flag와 counter는 언제 구분하는가?** | flag 하나는 여러 event를 하나로 합칠 수 있다. event 누락이 문제면 counter를 검토한다. |

### 요약

- ISR은 event를 기록하는 짧은 통로, main/task는 오래 걸리는 실제 처리 담당이다.
- `volatile`은 최적화 제어일 뿐 동시성 해결책이 아니다.

---

## 5. 코넬 노트 5 — 100 ms IMU → CAN 적용

| 단서·질문 (왼쪽 열) | 노트 (오른쪽 열) |
| --- | --- |
| **Timer의 목적을 어떻게 표현해야 하나?** | “100 ms delay를 넣는다”가 아니라 “100 ms time event를 만든다”이다. Timer는 시간 기준을 만들고, 센서 읽기·CAN 송신은 application의 후속 처리다. |
| **권장 흐름은?** | 1. Timer가 100 ms마다 Update Event 발생<br>2. ISR이 `UIF`를 clear하고 sample event 기록<br>3. main loop가 event를 가져와 MPU6050 register 읽기<br>4. accel/gyro 값을 CAN payload로 구성<br>5. CAN 송신 요청 후 UART log로 결과 확인 |
| **blocking과 non-blocking 차이는?** | blocking은 `sensor 읽기 → delay → CAN 송신 → delay` 흐름이다. non-blocking은 Timer가 “시간이 지남”을 event로 전달하고 main loop가 계속 돌게 한다. |
| **non-blocking의 장점은?** | UART 수신, 버튼, 오류 event 등 다른 일을 늦게 처리하지 않는다. 기다림을 미래 event로 분리하는 방식이다. |
| **100 ms 계산 예시는?** | `T = 0.1 s = (PSC+1) × (ARR+1) / timer_clk`이다. counter tick을 10 kHz로 만들면 100 ms는 1000 counts이므로 `ARR + 1 = 1000`이다. |

> **주의**
> 다른 STM32 예제의 clock 숫자를 현재 보드에 그대로 복사하지 말고, board의 clock tree에서 실제 `timer_clk`를 먼저 확인한다.

### 요약

- Timer는 일을 실행하는 장치가 아니라, 실행할 때를 알려 주는 장치다.
- I2C transaction 전체를 ISR에서 돌리면 구조의 장점이 사라진다.

---

## 6. 코넬 노트 6 — PWM은 하드웨어가 파형을 만든다

| 단서·질문 (왼쪽 열) | 노트 (오른쪽 열) |
| --- | --- |
| **PWM이란?** | PWM(Pulse Width Modulation)은 digital `HIGH/LOW`를 빠르게 반복하고, 한 주기 중 HIGH 비율(duty cycle)로 평균 에너지 전달을 조절하는 방식이다. LED 밝기, 모터 속도, 부저, 전력 제어에 쓴다. |
| **PWM과 DAC는?** | PWM은 연속 아날로그 전압을 직접 만드는 DAC와 다르다. |
| **`ARR`과 `CCR`의 역할은?** | `ARR`은 PWM 전체 주기·주파수의 기준, `CCR`(Capture/Compare Register)은 `CNT`와 비교할 값이다. PWM에서 `CCR`은 HIGH 구간 길이, 즉 duty를 결정한다. |
| **주파수와 duty는 어떻게 분리하는가?** | 주파수는 `timer clock / PSC / ARR`, duty는 `CCR`로 설명한다. mode/polarity에 따라 HIGH/LOW 해석은 달라질 수 있다. |
| **`ARR = 9`, `CCR = 4`면?** | `CNT`는 `0 1 2 3 4 5 6 7 8 9 → reload`로 센다. 예시 PWM은 `HIGH HIGH HIGH HIGH │ LOW LOW LOW LOW LOW LOW`이며 duty는 대략 `CCR / (ARR+1)`로 본다. |
| **Timer interrupt와 PWM의 본질적 차이는?** | Timer interrupt는 `ARR` 도달 사건을 CPU가 ISR에서 처리한다. PWM은 `CNT`와 `CCR`의 비교 결과를 Timer hardware가 output pin에 직접 반영하므로 전환마다 CPU ISR이 필요 없다. |

![PWM에서 ARR은 주기, CCR은 duty를 결정하는 구조](./assets/filginote_05/pwm_arr_ccr.svg)

> **주의**
> “Timer를 쓴다”가 항상 “ISR을 쓴다”는 뜻은 아니다.

### 요약

- PWM 주파수는 `PSC`·`ARR`, duty는 `CCR`로 분리한다.
- PWM은 CPU가 pin을 반복 toggle하지 않아도 Timer hardware가 출력을 만든다.

---

## 7. 코넬 노트 7 — Hardware Timer와 Software Timer 선택

| 단서·질문 (왼쪽 열) | 노트 (오른쪽 열) |
| --- | --- |
| **Hardware Timer의 시간 기준은?** | MCU Timer peripheral의 hardware clock이다. PWM, 정확한 peripheral timing, input capture에 맞는다. |
| **RTOS Software Timer의 시간 기준은?** | RTOS tick이다. 단순 timeout이나 주기 callback에 맞으며 tick보다 정밀할 수 없다. |
| **각각의 주의점은?** | Hardware Timer ISR은 짧게, RTOS Software Timer callback도 길게 block하지 않게 설계한다. |
| **어떻게 선택하는가?** | PWM·정밀 timing에는 Hardware Timer, RTOS 위의 단순 timeout에는 Software Timer를 선택한다. |

### 요약

- 같은 ‘timer’라도 시간 기준과 맞는 업무가 다르다.
- 정밀한 hardware timing과 RTOS의 편리한 timeout을 혼동하지 않는다.

---

## 8. 전체 요약 — 3문장 복습

1. Timer는 `PSC → CNT → ARR`로 시간을 세고 `ARR` 도달 시 Update Event를 만든다.
2. interrupt를 쓰면 ISR은 `UIF` clear와 event 기록만 하며, IMU 읽기·CAN 송신 같은 긴 일은 main/task가 처리한다.
3. PWM은 `CNT`와 `CCR` 비교 결과를 hardware가 pin에 직접 반영하므로, 주파수는 `PSC`·`ARR`, duty는 `CCR`로 제어한다.

---

## 9. 자기점검·면접 꼬리질문

- Timer가 busy-wait delay보다 나은 이유를 CPU 사용 관점에서 설명할 수 있는가?
- `PSC = N`, `ARR = M`일 때 실제 분주비·count 수·주기 공식을 말할 수 있는가?
- Update Event부터 `TIMx_IRQHandler()`까지 필요한 `UIF`, `UIE`, NVIC의 역할을 구분할 수 있는가?
- `volatile`이 해결하는 문제와 해결하지 못하는 문제를 구분할 수 있는가?
- Timer ISR에 I2C 센서 읽기를 바로 넣지 않는 이유를 설명할 수 있는가?
- PWM에서 `ARR`과 `CCR`이 각각 바꾸는 값을 말할 수 있는가?
- Hardware Timer와 RTOS Software Timer의 선택 기준을 말할 수 있는가?

### 답 확인

**Q. Timer가 delay loop보다 나은 이유는?**<br>
A. hardware가 시간을 세는 동안 CPU가 다른 작업이나 sleep을 할 수 있고, 필요한 시점에만 event로 대응하기 때문이다.

**Q. Timer ISR에 I2C 센서 읽기를 바로 넣지 않는 이유는?**<br>
A. transaction이 길어지면 ISR이 main과 다른 interrupt 응답을 늦춘다. ISR은 event만 전달하고 긴 처리는 main/task가 맡는 편이 안전하다.

**Q. `volatile`이면 ISR과 main의 공유 변수는 안전한가?**<br>
A. 아니다. `volatile`은 최적화를 제한할 뿐이며, atomicity나 race condition은 별도로 설계해야 한다.

**Q. PWM은 왜 CPU가 매번 pin을 toggle하지 않아도 되는가?**<br>
A. Timer hardware가 `CNT`와 `CCR`의 비교 결과를 output channel에 직접 반영하기 때문이다.

---

## 참고 자료

- [Timer / PWM ver3 원본](./필기노트_05_Timer_PWM_ver3.md) — 코넬 노트 적용 전 상세 필기
- [Timer / PWM ver2 원본](./필기노트_05_Timer_PWM_ver2.md) — 원본 보존
- [STM32 Timer/Counter와 PWM](../../10_주제별/stm32/timer/1_타이머카운터와_PWM.md)
- [기존 손필기 v1](./필기노트_05_Timer_PWM.md)
- [IMU-CAN 드라이버 시스템](../../../10_Experience/10_Projects/IMU_CAN_드라이버_시스템.md)
- [STM32 입문 강의 몰아보기 | ARM, GPIO, ADC, UART (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Timer는 peripheral clock을 세어 시간 event를 만들고, PWM은 Timer의 비교 기능으로 duty가 있는 출력 파형을 만드는 hardware 기능이다.
- **왜 필요:** delay loop로 CPU를 묶지 않고 일정한 시점에 일을 시작하며, PWM에서는 CPU가 pin을 반복 toggle하지 않아도 된다.
- **동작:** Timer는 `PSC → CNT → ARR`로 count하고 `ARR` 도달 시 Update Event를 만든다. interrupt를 사용하면 ISR은 flag를 clear하고 event만 남기며, PWM은 `CNT`와 `CCR`의 비교 결과를 output pin에 직접 반영한다.
- **비교:** Timer interrupt는 CPU가 event를 처리하는 방식이고, PWM은 hardware가 pin 출력을 직접 만드는 방식이다. RTOS Software Timer는 tick 기반 timeout 기능이라 Hardware Timer와 목적이 다르다.
- **30초 통합 답변:**
  > Timer는 peripheral clock을 `PSC`로 분주해 `CNT`를 세고, `ARR`에 도달하면 Update Event를 만드는 하드웨어입니다. interrupt를 사용하면 ISR에서는 `UIF` clear와 event 기록만 짧게 수행하고, IMU 읽기나 CAN 송신은 main loop로 넘겨 다른 event를 막지 않게 합니다. PWM은 같은 Timer에서 `CNT`와 `CCR`을 비교해 hardware가 pin의 HIGH/LOW 시간을 직접 바꾸므로, 주파수는 `PSC`와 `ARR`, duty는 `CCR`로 조절할 수 있습니다.
