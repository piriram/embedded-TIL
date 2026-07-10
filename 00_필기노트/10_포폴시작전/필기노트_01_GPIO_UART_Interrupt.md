# Ch.01 GPIO / UART / Interrupt

용도: A4 세로 반 접기 2열 손필기

규칙:

- 1열 32줄 기준
- 내용이 길면 다음 페이지로 넘김
- 들여쓰기 없음
- 파랑: 제목, 번호, 핵심 키워드
- 검정: 설명, 예시, cf
- 빨강: 면접 주의, 헷갈리는 점
- 손그림과 이미지 링크는 관련 개념 바로 아래에 배치

## 1페이지: GPIO

<span style="color:#1d4ed8">주제: GPIO / UART / Interrupt</span><br>
<span style="color:#1d4ed8">1. GPIO(General Purpose Input/Output)</span><br>
<span style="color:#111827">a. MCU 핀을 입력 또는 출력으로 쓰는 기능</span><br>
<span style="color:#111827">b. 외부 회로와 디지털 신호를 주고받음</span><br>
<span style="color:#111827">- Output 예: LED 켜기/끄기</span><br>
<span style="color:#111827">- Input 예: 버튼 상태 읽기</span><br>
<span style="color:#dc2626">※ GPIO는 임베디드의 가장 기본 입출구</span><br>
<br>
<span style="color:#1d4ed8">2. GPIO Output</span><br>
<span style="color:#111827">a. MCU가 핀에 HIGH 또는 LOW 출력</span><br>
<span style="color:#111827">b. HIGH는 보통 3.3V, LOW는 0V</span><br>
<span style="color:#111827">c. LED, 릴레이, 부저 제어에 사용</span><br>
<span style="color:#111827">cf) 릴레이 = 작은 전기 신호로 큰 전원을 켜고 끄는 전기식 스위치</span><br>
<span style="color:#111827">- HAL 예: HAL_GPIO_WritePin()</span><br>
<span style="color:#111827">cf) HAL = 하드웨어 제어를 쉽게 해주는 제조사 제공 함수 묶음</span><br>
<span style="color:#111827">- 레지스터 예: ODR, BSRR</span><br>
<span style="color:#111827">cf) ODR/BSRR = GPIO 출력을 직접 제어하는 레지스터 이름</span><br>
<span style="color:#111827">cf) 부저 = 전기 신호를 소리로 바꾸는 출력 부품</span><br>
<span style="color:#dc2626">※ ODR/BSRR은 지금은 이름만 알기</span><br>


<span style="color:#1d4ed8">3. Active Low</span><br>
<span style="color:#111827">a. LOW일 때 동작하는 회로</span><br>
<span style="color:#111827">b. GPIO LOW → ON, GPIO HIGH → OFF</span><br>
<span style="color:#111827">- BluePill PC13 LED가 대표 예시</span><br>
<span style="color:#dc2626">※ HIGH=켜짐이라고 단정하면 안 됨</span><br>
<br>
<span style="color:#1d4ed8">그림: Active Low LED</span><br>
<span style="color:#111827">3.3V</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">[LED]</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">[R]</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">GPIO</span><br>
<span style="color:#dc2626">※ GPIO LOW = 전류 흐름 = LED ON</span><br>
<br>
<span style="color:#1d4ed8">이미지: Active Low</span><br>
<span style="color:#111827">SparkFun Active Low and Active High</span><br>
<a style="color:#111827" href="https://learn.sparkfun.com/tutorials/logic-levels/active-low-and-active-high">https://learn.sparkfun.com/tutorials/logic-levels/active-low-and-active-high</a><br>
<span style="color:#dc2626">※ LOW일 때 동작한다는 개념 확인</span><br>


<span style="color:#1d4ed8">4. GPIO Input</span><br>
<span style="color:#111827">a. MCU가 핀의 전압 상태를 읽음</span><br>
<span style="color:#111827">b. 버튼, 센서 디지털 출력 확인</span><br>
<span style="color:#111827">c. 입력 핀이 떠 있으면 값이 흔들림</span><br>
<span style="color:#111827">cf) floating = HIGH/LOW가 정해지지 않은 불안정 상태</span><br>
<span style="color:#dc2626">※ 그래서 pull-up / pull-down이 필요</span><br>
<br>
<span style="color:#1d4ed8">5. Pull-up / Pull-down</span><br>
<span style="color:#111827">a. Pull-up: 기본값을 HIGH로 고정</span><br>
<span style="color:#111827">b. Pull-down: 기본값을 LOW로 고정</span><br>
<span style="color:#111827">c. 버튼 회로에서 자주 사용</span><br>
<span style="color:#111827">- Pull-up 버튼: 안 누름 HIGH, 누름 LOW</span><br>
<span style="color:#111827">- Pull-down 버튼: 안 누름 LOW, 누름 HIGH</span><br>
<span style="color:#dc2626">※ 버튼 입력이 반대로 보이는 이유</span><br>
<br>
<span style="color:#1d4ed8">이미지: Pull-up / Pull-down</span><br>
<span style="color:#111827">SparkFun Pull-up Resistors</span><br>
<a style="color:#111827" href="https://learn.sparkfun.com/tutorials/pull-up-resistors/all">https://learn.sparkfun.com/tutorials/pull-up-resistors/all</a><br>
<span style="color:#dc2626">※ 버튼 회로와 floating 입력 이해</span><br>


<span style="color:#1d4ed8">그림: Pull-up 버튼</span><br>
<span style="color:#111827">3.3V</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">[R]</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">+---- GPIO</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">[버튼]</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">GND</span><br>
<span style="color:#dc2626">※ 안 누름 HIGH, 누르면 LOW</span><br>
<br>
<span style="color:#1d4ed8">그림: Pull-down 버튼</span><br>
<span style="color:#111827">3.3V</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">[버튼]</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">+---- GPIO</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">[R]</span><br>
<span style="color:#111827">|</span><br>
<span style="color:#111827">GND</span><br>
<span style="color:#dc2626">※ 안 누름 LOW, 누르면 HIGH</span><br>


## 2페이지: UART / Interrupt

<span style="color:#1d4ed8">6. UART란</span><br>
<span style="color:#111827">a. 비동기 직렬 통신</span><br>
<span style="color:#111827">b. TX는 송신, RX는 수신</span><br>
<span style="color:#111827">c. PC 로그 출력과 디버깅에 자주 사용</span><br>
<span style="color:#111827">- MCU TX → PC RX</span><br>
<span style="color:#111827">- MCU RX ← PC TX</span><br>
<span style="color:#dc2626">※ GND를 공유해야 기준 전압이 맞음</span><br>
<br>
<span style="color:#1d4ed8">그림: UART 연결</span><br>
<span style="color:#111827">MCU TX ---- PC RX</span><br>
<span style="color:#111827">MCU RX ---- PC TX</span><br>
<span style="color:#111827">MCU GND --- PC GND</span><br>
<span style="color:#dc2626">※ 보내는 선은 받는 선에 연결</span><br>
<span style="color:#dc2626">※ GND는 반드시 공통</span><br>
<br>
<span style="color:#1d4ed8">이미지: UART TX/RX/GND</span><br>
<span style="color:#111827">Nordic UART Protocol</span><br>
<a style="color:#111827" href="https://academy.nordicsemi.com/courses/nrf-connect-sdk-fundamentals/lessons/lesson-4-serial-communication-uart/topic/uart-protocol/">https://academy.nordicsemi.com/courses/nrf-connect-sdk-fundamentals/lessons/lesson-4-serial-communication-uart/topic/uart-protocol/</a><br>
<span style="color:#111827">ST Getting started with UART</span><br>
<a style="color:#111827" href="https://wiki.st.com/stm32mcu/wiki/Getting_started_with_UART">https://wiki.st.com/stm32mcu/wiki/Getting_started_with_UART</a><br>


<span style="color:#1d4ed8">7. UART 설정: 115200 8N1</span><br>
<span style="color:#111827">a. UART 통신을 위한 약속값</span><br>
<span style="color:#111827">b. 115200 = 1초에 보내는 비트 수</span><br>
<span style="color:#111827">c. 8 = 데이터 8비트</span><br>
<span style="color:#111827">d. N = parity 없음</span><br>
<span style="color:#111827">e. 1 = stop bit 1개</span><br>
<span style="color:#111827">cf) parity/stop bit는 지금은 이름만 알기</span><br>
<span style="color:#dc2626">※ MCU와 PC 설정이 같아야 글자가 안 깨짐</span><br>
<br>
<span style="color:#1d4ed8">8. Polling vs Interrupt</span><br>
<span style="color:#1d4ed8">1) Polling</span><br>
<span style="color:#111827">a. CPU가 계속 상태를 확인</span><br>
<span style="color:#111827">b. 단순하지만 CPU 시간을 씀</span><br>
<span style="color:#1d4ed8">2) Interrupt</span><br>
<span style="color:#111827">a. 이벤트 발생 시 CPU가 반응</span><br>
<span style="color:#111827">b. 효율적이지만 설계 주의 필요</span><br>
<span style="color:#111827">- 버튼 눌림, UART 수신, 타이머에 사용</span><br>
<span style="color:#dc2626">※ 인터럽트가 항상 정답은 아님</span><br>


<span style="color:#1d4ed8">9. ISR(Interrupt Service Routine) 주의사항</span><br>
<span style="color:#111827">a. 인터럽트 발생 시 실행되는 함수</span><br>
<span style="color:#111827">b. 가능한 짧게 처리해야 함</span><br>
<span style="color:#111827">- 플래그만 세우고 main loop에서 처리</span><br>
<span style="color:#dc2626">※ ISR 안에서 delay, 긴 루프, printf 피하기</span><br>
<br>
<span style="color:#1d4ed8">10. PWM(Pulse Width Modulation)</span><br>
<span style="color:#111827">a. HIGH/LOW를 빠르게 반복해 평균 출력을 조절</span><br>
<span style="color:#111827">b. LED 밝기, 모터 속도, 수동 부저 소리에 사용</span><br>
<span style="color:#111827">cf) duty cycle = 한 주기 중 HIGH 비율</span><br>
<span style="color:#dc2626">※ PWM은 빠른 디지털 ON/OFF</span><br>
<br>
<span style="color:#1d4ed8">이미지: PWM duty cycle</span><br>
<span style="color:#111827">SparkFun PWM Duty Cycle</span><br>
<a style="color:#111827" href="https://learn.sparkfun.com/tutorials/pulse-width-modulation/duty-cycle">https://learn.sparkfun.com/tutorials/pulse-width-modulation/duty-cycle</a><br>
<span style="color:#dc2626">※ 25%, 50%, 75% duty 그림 확인</span><br>


<span style="color:#1d4ed8">그림: PWM 느낌</span><br>
<span style="color:#111827">25% duty: HIGH 짧음, LOW 김</span><br>
<span style="color:#111827">50% duty: HIGH/LOW 반반</span><br>
<span style="color:#111827">75% duty: HIGH 김, LOW 짧음</span><br>
<span style="color:#dc2626">※ HIGH 시간이 길수록 LED가 밝게 보임</span><br>
<br>
<span style="color:#1d4ed8">Q. 꼬리질문</span><br>
<span style="color:#111827">- Pull-up 버튼은 누르면 왜 LOW인가?</span><br>
<span style="color:#111827">- Active Low LED는 왜 LOW일 때 켜지나?</span><br>
<span style="color:#111827">- UART에서 baud rate가 다르면?</span><br>
<span style="color:#111827">- ISR은 왜 짧아야 하나?</span><br>
<span style="color:#111827">- PWM은 왜 밝기 조절처럼 보이나?</span><br>


## 면접 30초 답변

<span style="color:#1d4ed8">GPIO / UART / Interrupt 설명</span><br>
<span style="color:#111827">GPIO는 MCU 핀을 입력 또는 출력으로 설정해 외부 회로와 디지털 신호를 주고받는 기본 인터페이스입니다.</span><br>
<span style="color:#111827">UART는 TX/RX 두 선으로 데이터를 주고받는 비동기 직렬 통신이고, 주로 PC 로그 출력이나 디버깅에 사용합니다.</span><br>
<span style="color:#111827">인터럽트는 버튼 입력이나 UART 수신처럼 이벤트가 발생했을 때 CPU가 ISR을 실행하는 방식입니다.</span><br>
<span style="color:#dc2626">ISR은 짧게 처리하고, 긴 작업은 메인 루프나 태스크로 넘기는 것이 좋습니다.</span><br>


## 지금 깊이 조절

<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- GPIO, HIGH/LOW</span><br>
<span style="color:#111827">- Pull-up / Pull-down</span><br>
<span style="color:#111827">- Floating</span><br>
<span style="color:#111827">- Active Low</span><br>
<span style="color:#111827">- UART 설정은 양쪽이 같아야 함</span><br>
<span style="color:#111827">- Polling / Interrupt / ISR</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- ODR / BSRR</span><br>
<span style="color:#111827">- parity</span><br>
<span style="color:#111827">- stop bit</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- 레지스터 비트 구조</span><br>
<span style="color:#111827">- BSRR 하위/상위 16비트</span><br>
<span style="color:#111827">- PWM 주파수 계산</span><br>
<span style="color:#111827">- UART 프레임 상세</span><br>
<span style="color:#dc2626">※ 지금은 입구 개념을 먼저 잡는다</span><br>

