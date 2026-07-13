# Ch.05 Timer / PWM ver3 — 시간 이벤트와 PWM의 기본 흐름

용도: A4 세로 반 접기 2열 손필기 / 신입 임베디드 면접 대비

이 노트의 목표는 레지스터 세부값을 외우는 것이 아니라, **Timer가 시간을 만들고 → event가 ISR에 전달되고 → 긴 작업은 main이 처리하며 → PWM은 하드웨어가 출력 파형을 만든다**는 흐름을 설명하는 데 있다.

> **범위**
> - 지금 이해: `PSC`, `CNT`, `ARR`, `CCR`, Update Event, ISR, `volatile`, 100 ms event, PWM
> - 나중에: exception frame 세부 레지스터, FPU context, ARPE, center-aligned, complementary PWM, dead time, FreeRTOS timer service task

---

## 1. Timer는 CPU가 기다리지 않게 시간을 만든다

<span style="color:#1d4ed8">Timer / PWM의 전체 지도</span><br>
<span style="color:#111827">busy-wait delay에서는 CPU가 시간이 지났는지 계속 확인함</span><br>
<span style="color:#111827">Timer는 peripheral hardware가 clock을 세고, 시간이 되면 event를 만듦</span><br>
<span style="color:#111827">CPU는 그 사이 다른 일을 하거나 sleep할 수 있음</span><br>
<span style="color:#dc2626">※ Timer는 단순 delay 함수가 아니라 system의 시간 기준을 제공하는 hardware</span><br>
<br>
<span style="color:#1d4ed8">Polling과 Timer interrupt</span><br>
<span style="color:#111827">- polling: CPU가 timeout을 반복 확인</span><br>
<span style="color:#111827">- timer interrupt: hardware가 시간 만료를 감지해 CPU에 알림</span><br>
<span style="color:#111827">- 예: 100 ms마다 센서 읽기, 1초마다 LED toggle</span><br>
<span style="color:#dc2626">※ 긴 delay를 ISR 안에 넣으면 polling 문제가 ISR 안에서 다시 생김</span><br>
<br>
<span style="color:#1d4ed8">Timer와 Counter</span><br>
<span style="color:#111827">- Timer: 내부 clock을 기준으로 시간/주기를 만듦</span><br>
<span style="color:#111827">- Counter: 외부 pin 신호가 들어온 횟수를 셈</span><br>
<span style="color:#111827">- 같은 Timer peripheral도 clock source에 따라 두 역할을 할 수 있음</span><br>

---

## 2. Timer는 PSC → CNT → ARR 순서로 시간을 만든다

<span style="color:#1d4ed8">하드웨어 시간 흐름</span><br>
<span style="color:#111827">Timer clock → PSC → CNT → ARR → Update Event</span><br>
<span style="color:#111827">- PSC(Prescaler): clock을 나눠 CNT가 세는 속도를 낮춤</span><br>
<span style="color:#111827">- CNT(Counter): 현재 count 값</span><br>
<span style="color:#111827">- ARR(Auto-Reload Register): CNT가 셀 끝값</span><br>
<span style="color:#111827">- CNT가 ARR에 도달하면 reload하고 Update Event를 만들 수 있음</span><br>
<span style="color:#dc2626">※ 계산은 항상 clock → PSC → CNT → ARR 순서로 생각</span><br>
<br>
<span style="color:#1d4ed8">0부터 세므로 +1</span><br>
<span style="color:#111827">- PSC register가 N이면 실제 분주비는 N+1</span><br>
<span style="color:#111827">- ARR register가 M이면 한 주기의 count 수는 M+1</span><br>
<span style="color:#111827">- 주기: `T = (PSC+1) × (ARR+1) / timer_clk`</span><br>
<span style="color:#111827">- 주파수: `f = timer_clk / ((PSC+1) × (ARR+1))`</span><br>
<span style="color:#dc2626">※ PSC 또는 ARR 하나만으로 주기가 정해지는 것은 아님</span><br>
<br>
<img src="./assets/filginote_05/timer_count_flow.svg" width="720" alt="Timer clock, prescaler, counter, ARR, update event 흐름"><br>

---

## 3. Update Event가 ISR로 들어오는 흐름

<span style="color:#1d4ed8">Event와 interrupt는 같은 말이 아니다</span><br>
<span style="color:#111827">1. CNT가 ARR에 도달하면 Update Event 발생</span><br>
<span style="color:#111827">2. SR의 UIF flag가 event 발생 사실을 기록</span><br>
<span style="color:#111827">3. DIER의 UIE를 켜면 event가 interrupt request가 될 수 있음</span><br>
<span style="color:#111827">4. NVIC가 IRQ를 허용하면 CPU가 handler로 들어감</span><br>
<span style="color:#dc2626">※ event 발생 → interrupt enable → ISR 실행은 서로 다른 단계</span><br>
<br>
<span style="color:#1d4ed8">설정의 큰 순서</span><br>
<span style="color:#111827">1. Timer peripheral clock enable</span><br>
<span style="color:#111827">2. PSC와 ARR 설정</span><br>
<span style="color:#111827">3. Update interrupt(UIE) enable</span><br>
<span style="color:#111827">4. NVIC에서 해당 IRQ enable</span><br>
<span style="color:#111827">5. Counter(CEN) 시작</span><br>
<span style="color:#dc2626">※ clock, UIE, NVIC 중 하나라도 빠지면 handler는 실행되지 않음</span><br>
<br>
<span style="color:#1d4ed8">CPU는 어떻게 돌아오는가</span><br>
<span style="color:#111827">- interrupt는 main 흐름과 무관하게 발생하는 hardware event</span><br>
<span style="color:#111827">- CPU는 실행 흐름을 잠시 멈추고 vector table이 가리키는 ISR로 이동</span><br>
<span style="color:#111827">- ISR이 끝나면 hardware가 저장한 실행 상태를 바탕으로 중단 지점으로 복귀</span><br>
<span style="color:#dc2626">※ 면접에서는 “hardware가 context를 저장·복원한다”까지 설명하면 충분</span><br>

---

## 4. ISR은 알리고, main은 처리한다

<span style="color:#1d4ed8">Foreground / Background 구조</span><br>
<span style="color:#111827">- background: `main()`의 `while(1)`, 일반 application logic</span><br>
<span style="color:#111827">- foreground: Timer, GPIO, UART 등의 ISR, background를 잠시 선점</span><br>
<span style="color:#111827">- 작은 MCU에서는 이 구조를 super loop 또는 main + ISRs라고 부름</span><br>
<br>
<span style="color:#1d4ed8">ISR의 원칙</span><br>
<span style="color:#111827">- UIF를 확인하고 clear</span><br>
<span style="color:#111827">- flag/event counter 기록처럼 짧은 일만 수행</span><br>
<span style="color:#111827">- 긴 delay, `printf`, I2C polling, 복잡한 CAN 처리는 main으로 넘김</span><br>
<span style="color:#dc2626">※ ISR이 빠른 이유는 interrupt라서가 아니라, 짧게 설계했기 때문</span><br>
<br>
<span style="color:#1d4ed8">ISR과 main의 공유 데이터</span><br>
<span style="color:#111827">- ISR이 바꾸고 main이 읽는 flag/counter에는 `volatile`이 필요할 수 있음</span><br>
<span style="color:#111827">- `volatile`은 compiler가 read/write를 생략하지 않게 할 뿐</span><br>
<span style="color:#111827">- `volatile`은 atomicity나 race condition 해결책이 아님</span><br>
<span style="color:#dc2626">※ read-modify-write 또는 multi-byte 데이터는 별도 보호 방법을 검토</span><br>
<br>
<span style="color:#1d4ed8">Timer ISR의 최소 형태</span><br>
<span style="color:#111827">Timer Update Event → UIF set → NVIC → `TIMx_IRQHandler()`</span><br>
<span style="color:#111827">ISR: UIF clear → `sample_due` flag 또는 event counter 기록 → return</span><br>
<span style="color:#111827">main: event를 가져옴 → 실제 sensor/CAN 작업 수행</span><br>
<span style="color:#dc2626">※ flag 하나는 여러 event를 합칠 수 있음. 누락이 문제면 counter를 검토</span><br>

---

## 5. 포트폴리오 연결: 100 ms IMU → CAN 흐름

<span style="color:#1d4ed8">Timer의 목적</span><br>
<span style="color:#111827">Timer의 역할은 “100 ms delay를 넣는 것”이 아니라 “100 ms time event를 만드는 것”</span><br>
<span style="color:#111827">센서 읽기와 CAN 송신은 timer hardware가 아니라 application의 후속 처리</span><br>
<br>
<span style="color:#1d4ed8">권장 흐름</span><br>
<span style="color:#111827">1. Timer가 100 ms마다 Update Event 발생</span><br>
<span style="color:#111827">2. ISR이 UIF를 clear하고 sample event 기록</span><br>
<span style="color:#111827">3. main loop가 event를 가져와 MPU6050 register를 읽음</span><br>
<span style="color:#111827">4. accel/gyro 값을 CAN payload로 만듦</span><br>
<span style="color:#111827">5. CAN 송신 요청 후 UART log로 결과 확인</span><br>
<span style="color:#dc2626">※ I2C transaction 전체를 ISR에서 돌리면 ISR이 길어져 구조의 장점이 사라짐</span><br>
<br>
<span style="color:#1d4ed8">Blocking과 non-blocking</span><br>
<span style="color:#111827">- blocking: sensor 읽기 → delay → CAN 송신 → delay</span><br>
<span style="color:#111827">- non-blocking: Timer가 “시간이 지남”을 event로 전달하고, main loop는 계속 돌아감</span><br>
<span style="color:#111827">- 장점: UART 수신, 버튼, 오류 event 등 다른 일을 늦게 처리하지 않음</span><br>
<span style="color:#dc2626">※ non-blocking은 아무것도 안 하는 것이 아니라 기다림을 미래 event로 분리하는 것</span><br>
<br>
<span style="color:#1d4ed8">100 ms 계산 예시</span><br>
<span style="color:#111827">목표: `T = 0.1 s = (PSC+1) × (ARR+1) / timer_clk`</span><br>
<span style="color:#111827">- 실제 `timer_clk`는 보드의 clock tree에서 먼저 확인</span><br>
<span style="color:#111827">- 예: counter tick을 10 kHz로 만들면 100 ms는 1000 counts</span><br>
<span style="color:#111827">- 따라서 `ARR + 1 = 1000`, register에는 0부터 세는 +1 규칙 반영</span><br>
<span style="color:#dc2626">※ 다른 STM32의 clock 숫자를 현재 보드에 복사하면 안 됨</span><br>

---

## 6. PWM은 Timer hardware가 출력 파형을 만든다

<span style="color:#1d4ed8">PWM의 출발점</span><br>
<span style="color:#111827">PWM(Pulse Width Modulation)은 digital HIGH/LOW를 빠르게 반복하는 방식</span><br>
<span style="color:#111827">한 주기 중 HIGH 시간의 비율을 duty cycle이라 함</span><br>
<span style="color:#111827">LED 밝기, 모터 속도, 부저, 전력 제어에서 평균 에너지 전달을 조절</span><br>
<span style="color:#dc2626">※ PWM은 연속 아날로그 전압을 직접 만드는 DAC와 다름</span><br>
<br>
<span style="color:#1d4ed8">ARR은 주기, CCR은 duty</span><br>
<span style="color:#111827">- ARR: PWM 전체 주기와 주파수의 기준</span><br>
<span style="color:#111827">- CCR(Capture/Compare Register): CNT와 비교할 값</span><br>
<span style="color:#111827">- PWM에서 CCR은 HIGH 구간 길이, 즉 duty를 결정</span><br>
<span style="color:#111827">- 주파수는 `timer clock/PSC/ARR`, duty는 `CCR`로 분리해 설명</span><br>
<span style="color:#dc2626">※ mode/polarity에 따라 HIGH/LOW 해석은 달라질 수 있음</span><br>
<br>
<span style="color:#1d4ed8">예시: ARR = 9, CCR = 4</span><br>
<span style="color:#111827">CNT: 0 1 2 3 4 5 6 7 8 9 → reload</span><br>
<span style="color:#111827">PWM: HIGH HIGH HIGH HIGH | LOW LOW LOW LOW LOW LOW</span><br>
<span style="color:#111827">duty ≈ `CCR / (ARR+1)`</span><br>
<br>
<img src="./assets/filginote_05/pwm_arr_ccr.svg" width="720" alt="PWM에서 ARR은 주기, CCR은 duty를 결정하는 구조"><br>
<br>
<span style="color:#1d4ed8">Timer interrupt와 PWM의 차이</span><br>
<span style="color:#111827">- Timer interrupt: ARR 도달 사건을 CPU가 ISR에서 처리</span><br>
<span style="color:#111827">- PWM: CNT와 CCR 비교 결과를 Timer hardware가 output pin에 직접 반영</span><br>
<span style="color:#111827">- PWM의 HIGH/LOW 전환마다 CPU가 ISR을 실행할 필요는 없음</span><br>
<span style="color:#dc2626">※ “Timer를 쓴다”가 항상 “ISR을 쓴다”는 뜻은 아님</span><br>

---

## 7. Hardware Timer와 Software Timer는 목적이 다르다

| 구분 | Hardware Timer | RTOS Software Timer |
|---|---|---|
| 시간 기준 | MCU Timer peripheral | RTOS tick |
| 잘 맞는 일 | PWM, 정확한 peripheral timing, input capture | 단순 timeout, 주기 callback |
| 정밀도 | hardware clock 기준 | tick보다 정밀할 수 없음 |
| 핵심 주의 | ISR은 짧게 | callback도 길게 block하지 않기 |

<span style="color:#dc2626">※ PWM과 정밀 timing은 Hardware Timer, RTOS 위의 단순 timeout은 Software Timer로 구분</span><br>

---

## 면접 답변 (30초 분량)

> /easy-quiz 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Timer는 peripheral clock을 세어 시간 event를 만들고, PWM은 그 Timer의 비교 기능으로 duty가 있는 출력 파형을 만드는 hardware 기능이다.
- **왜 필요:** delay loop로 CPU를 묶지 않고 일정한 시점에 일을 시작하며, PWM은 CPU가 pin을 반복 toggle하지 않아도 되게 한다.
- **동작:** Timer는 `PSC → CNT → ARR` 흐름으로 count하고 ARR 도달 시 Update Event를 만든다. interrupt를 켜면 ISR은 flag를 clear하고 event만 남기며, sensor 읽기·CAN 송신 같은 긴 일은 main이 처리한다. PWM은 CNT와 CCR을 비교해 output pin을 hardware가 직접 바꾼다.
- **비교:** Timer interrupt는 CPU가 event를 처리하는 방식이고, PWM은 hardware가 pin 출력을 직접 만드는 방식이다. Software Timer는 RTOS tick 기반 timeout 기능이라 Hardware Timer와 목적이 다르다.
- **30초 통합 답변:** Timer는 peripheral clock을 PSC로 분주해 CNT를 세고, ARR에 도달하면 Update Event를 만드는 하드웨어입니다. interrupt를 사용하면 ISR에서는 UIF clear와 event 기록만 짧게 수행하고, IMU 읽기나 CAN 송신은 main loop로 넘겨 다른 event를 막지 않게 합니다. PWM은 같은 Timer에서 CNT와 CCR을 비교해 하드웨어가 pin의 HIGH/LOW 시간을 직접 바꾸므로, 주파수는 PSC와 ARR, duty는 CCR로 조절할 수 있습니다.

---

## 면접 꼬리질문

**Q. Timer가 delay loop보다 나은 이유는?**  
A. hardware가 시간을 세는 동안 CPU가 다른 작업이나 sleep을 할 수 있고, 필요한 시점에만 event로 대응하기 때문이다.

**Q. Timer ISR에 I2C 센서 읽기를 바로 넣지 않는 이유는?**  
A. transaction이 길어지면 ISR이 main과 다른 interrupt 응답을 늦춘다. ISR은 event만 전달하고 긴 처리는 main/task가 맡는 편이 안전하다.

**Q. `volatile`이면 ISR과 main의 공유 변수는 안전한가?**  
A. 아니다. `volatile`은 최적화를 제한할 뿐이며, atomicity나 race condition은 별도로 설계해야 한다.

**Q. PWM은 왜 CPU가 매번 pin을 toggle하지 않아도 되는가?**  
A. Timer hardware가 CNT와 CCR의 비교 결과를 output channel에 직접 반영하기 때문이다.

**Q. MCU와 MPU 차이는 무엇인가?**  
A. MCU는 제어용 주변장치와 메모리가 집적된 경우가 많아 bare-metal/RTOS 환경에 자주 쓰이고, MPU는 외부 메모리와 복잡한 OS를 포함한 시스템에 더 적합하다.

---

## 참고 자료

- [Timer / PWM ver2 원본](./필기노트_05_Timer_PWM_ver2.md) — 원본 보존
- [STM32 Timer/Counter와 PWM](../../10_주제별/stm32/timer/1_타이머카운터와_PWM.md)
- [기존 손필기 v1](./필기노트_05_Timer_PWM.md)
- [IMU-CAN 드라이버 시스템](../../../10_Experience/10_Projects/IMU_CAN_드라이버_시스템.md)
- [STM32 입문 강의 몰아보기 | ARM, GPIO, ADC, UART (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)
