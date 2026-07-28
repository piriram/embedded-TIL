<span style="color:#1d4ed8">I. Timer / PWM — 시간 이벤트와 하드웨어 출력</span><br>
<br>
<span style="color:#1d4ed8">1. Timer는 CPU를 기다리게 하지 않고 시간 기준을 만든다</span><br>
<span style="color:#1d4ed8">1) busy-wait delay의 한계</span><br>
<span style="color:#1d4ed8">① CPU가 시간을 직접 기다리는 방식</span><br>
<span style="color:#111827">a. while(시간이_안_지남) { }를 반복하는 동안 CPU는 다른 일을 처리하지 못함</span><br>
<span style="color:#111827">cf) busy-wait delay = CPU가 반복문을 실행하며 시간·조건을 직접 기다리는 방식</span><br>
<span style="color:#1d4ed8">2) Timer의 역할</span><br>
<span style="color:#1d4ed8">① peripheral hardware가 clock을 세고, 설정한 시점에 event를 만듦</span><br>
<span style="color:#111827">a. CPU는 그 사이 application 작업을 하거나 sleep할 수 있음</span><br>
<span style="color:#111827">b. ex) 100 ms마다 센서를 읽고, 1초마다 LED를 toggle</span><br>
<span style="color:#dc2626">★ <strong>Timer는 단순 delay 함수가 아니라 system의 시간 기준을 제공하는 hardware</strong></span><br>
<span style="color:#1d4ed8">3) Polling과 Timer interrupt</span><br>
<span style="color:#1d4ed8">① Polling</span><br>
<span style="color:#111827">a. CPU가 timeout이 지났는지 반복해서 확인</span><br>
<span style="color:#1d4ed8">② Timer interrupt</span><br>
<span style="color:#111827">a. hardware가 시간 만료를 감지해 CPU에 알림</span><br>
<span style="color:#dc2626">! 긴 delay를 ISR 안에 넣으면 polling 문제가 ISR 안으로 옮겨갈 뿐</span><br>
<span style="color:#1d4ed8">4) Timer와 Counter</span><br>
<span style="color:#1d4ed8">① Timer</span><br>
<span style="color:#111827">a. 내부 clock을 기준으로 시간과 주기를 만듦</span><br>
<span style="color:#1d4ed8">② Counter</span><br>
<span style="color:#111827">a. 외부 pin 신호가 들어온 횟수를 셈</span><br>
<span style="color:#111827">↔ 같은 Timer peripheral도 clock source에 따라 두 역할을 할 수 있음</span><br>
<br>
<span style="color:#1d4ed8">2. Timer는 속도를 낮춰 세고, 끝값에서 event를 만든다 (PSC → CNT → ARR)</span><br>
<span style="color:#1d4ed8">1) 먼저 세 이름</span><br>
<span style="color:#111827">① <strong>PSC</strong>(Prescaler)는 clock 속도를 낮추고, <strong>CNT</strong>(Counter)는 현재 숫자를 세며, <strong>ARR</strong>(Auto-Reload Register)은 셀 끝값을 정함</span><br>
<span style="color:#dc2626">! 먼저 “속도를 낮춘 뒤 → 숫자를 세고 → 끝값에서 event”라고 잡으면 됨</span><br>
<span style="color:#1d4ed8">2) 하드웨어 시간 흐름</span><br>
<span style="color:#1d4ed8">① Timer clock → PSC → CNT → ARR → Update Event</span><br>
<span style="color:#111827">a. PSC(Prescaler)는 clock을 나눠 CNT가 세는 속도를 낮춤</span><br>
<span style="color:#111827">cf) PSC register가 N이면 실제 분주비는 N+1</span><br>
<span style="color:#111827">b. CNT(Counter)는 현재 count 값</span><br>
<span style="color:#111827">c. ARR(Auto-Reload Register)은 CNT가 셀 끝값</span><br>
<span style="color:#111827">d. CNT가 ARR에 도달하면 reload하고 Update Event를 만들 수 있음</span><br>
<span style="color:#dc2626">! 계산은 항상 <strong>clock → PSC → CNT → ARR 순서</strong>로 생각</span><br>
<span style="color:#1d4ed8">3) 0부터 세므로 +1</span><br>
<span style="color:#1d4ed8">① PSC와 ARR의 실제 의미</span><br>
<span style="color:#111827">a. PSC register가 N이면 실제 분주비는 <strong>N+1</strong></span><br>
<span style="color:#111827">b. ARR register가 M이면 한 주기의 count 수는 <strong>M+1</strong></span><br>
<span style="color:#111827">c. 주기 <strong>T = (PSC+1) × (ARR+1) / timer_clk</strong></span><br>
<span style="color:#111827">d. 주파수 <strong>f = timer_clk / ((PSC+1) × (ARR+1))</strong></span><br>
<span style="color:#dc2626">! <strong>PSC 또는 ARR 하나만으로 주기가 정해지는 것은 아님</strong></span><br>
<span style="color:#1d4ed8">그림: Timer 시간 생성 흐름</span><br>
<span style="color:#111827">Timer clock → PSC → CNT → ARR → Update Event</span><br>
<span style="color:#dc2626">! 화살표 순서와 PSC·ARR의 역할을 함께 확인</span><br>
<img src="./assets/filginote_05/timer_count_flow.svg" width="720" alt="Timer clock, prescaler, counter, ARR, update event 흐름"><br>
<span style="color:#1d4ed8">외부 그림 후보: 더 보기 쉬운 흐름도를 골라 확인</span><br>
<span style="color:#111827">① <a href="https://micromouseonline.com/wp-content/uploads/2016/02/TIM3-diagram-Fig119-RM0090.png">후보 A — TIM3 단순화 block diagram (원본 이미지)</a>: clock → PSC → CNT → ARR 연결을 중심으로 보기</span><br>
<span style="color:#111827">② <a href="https://deepbluembedded.com/wp-content/uploads/2020/06/STM32-Basic-Timer-Module-Hardware-Timers-Explained-Tutorial.png">후보 B — STM32 Basic Timer block diagram (원본 이미지)</a>: PSC, CNT, ARR와 update/interrupt 연결을 조금 더 자세히 보기</span><br>
<span style="color:#111827">③ <a href="https://www.st.com/resource/en/product_training/STM32G4-WDG_TIMERS-General_Purpose_Timer_GPTIM.pdf">후보 C — ST 공식 GPTIM 교육자료 (PDF)</a>: 실제 Timer 내부 block과 Update Event를 공식 표기로 확인</span><br>
<span style="color:#dc2626">! A는 흐름 이해용, B는 register 연결 이해용, C는 실제 hardware 구조 확인용</span><br>
<br>
<span style="color:#1d4ed8">3. Update Event가 ISR에 도달하려면 허용 단계가 필요하다</span><br>
<span style="color:#1d4ed8">1) Event와 interrupt는 다름</span><br>
<span style="color:#1d4ed8">① ISR까지의 흐름</span><br>
<span style="color:#111827">a. CNT가 ARR에 도달 → <strong>Update Event</strong> 발생</span><br>
<span style="color:#111827">b. SR의 <strong>UIF</strong> flag가 event 발생 사실을 기록</span><br>
<span style="color:#111827">cf) UIF(Update Interrupt Flag) = Update Event가 발생했음을 나타내는 status flag</span><br>
<span style="color:#111827">c. DIER의 <strong>UIE</strong>를 켜면 event가 interrupt request가 될 수 있음</span><br>
<span style="color:#111827">cf) UIE(Update Interrupt Enable) = Update Event interrupt 허용 bit</span><br>
<span style="color:#111827">d. <strong>NVIC</strong>가 IRQ를 허용하면 CPU가 handler로 들어감</span><br>
<span style="color:#dc2626">★ <strong>Event 발생 → interrupt enable → ISR 실행은 서로 다른 단계</strong></span><br>
<span style="color:#1d4ed8">2) 설정의 큰 순서</span><br>
<span style="color:#1d4ed8">① Timer를 시작하기 전</span><br>
<span style="color:#111827">a. Timer peripheral clock enable</span><br>
<span style="color:#111827">b. PSC와 ARR 설정</span><br>
<span style="color:#111827">c. Update interrupt(UIE) enable</span><br>
<span style="color:#111827">d. NVIC에서 해당 IRQ enable</span><br>
<span style="color:#111827">e. Counter(CEN) 시작</span><br>
<span style="color:#dc2626">! <strong>clock, UIE, NVIC 중 하나라도 빠지면 handler는 실행되지 않음</strong></span><br>
<span style="color:#1d4ed8">3) ISR이 끝난 뒤</span><br>
<span style="color:#1d4ed8">① CPU의 복귀</span><br>
<span style="color:#111827">a. CPU는 main 흐름을 잠시 멈추고 vector table이 가리키는 ISR로 이동</span><br>
<span style="color:#111827">cf) vector table = 각 interrupt가 실행할 handler 주소를 모아 둔 표</span><br>
<span style="color:#111827">b. ISR이 끝나면 hardware가 저장·복원한 실행 상태를 바탕으로 중단 지점으로 복귀</span><br>
<span style="color:#dc2626">! 면접에서는 hardware가 context를 저장·복원한다고 설명하면 충분</span><br>
<br>
<span style="color:#1d4ed8">4. ISR은 알리고, main은 처리한다</span><br>
<span style="color:#1d4ed8">1) Foreground / Background 구조</span><br>
<span style="color:#1d4ed8">① 역할 분리</span><br>
<span style="color:#111827">a. background = main()의 while(1), 일반 application logic</span><br>
<span style="color:#111827">b. foreground = Timer·GPIO·UART 등의 <strong>ISR</strong>, background를 잠시 선점</span><br>
<span style="color:#111827">cf) 작은 MCU의 이 구조를 super loop 또는 main + ISRs라고 부름</span><br>
<span style="color:#1d4ed8">2) ISR의 원칙</span><br>
<span style="color:#1d4ed8">① 최소 처리</span><br>
<span style="color:#111827">a. UIF를 확인하고 clear</span><br>
<span style="color:#111827">b. flag 또는 event counter 기록처럼 짧은 일만 수행</span><br>
<span style="color:#111827">c. 긴 delay, printf, I2C polling, 복잡한 CAN 처리는 main으로 넘김</span><br>
<span style="color:#dc2626">★ ISR이 빠른 이유는 interrupt라서가 아니라 <strong>짧게 설계했기 때문</strong></span><br>
<span style="color:#1d4ed8">3) ISR과 main의 공유 데이터</span><br>
<span style="color:#1d4ed8">① volatile의 역할과 한계</span><br>
<span style="color:#111827">a. ISR이 바꾸고 main이 읽는 flag/counter에는 <strong>volatile</strong>이 필요할 수 있음</span><br>
<span style="color:#111827">b. volatile은 compiler가 read/write를 생략하지 않게 할 뿐</span><br>
<span style="color:#111827">c. <strong>volatile은 atomicity나 race condition 해결책이 아님</strong></span><br>
<span style="color:#dc2626">! <strong>read-modify-write 또는 multi-byte 데이터는 별도 보호 방법을 검토</strong></span><br>
<span style="color:#1d4ed8">4) Timer ISR의 최소 형태</span><br>
<span style="color:#1d4ed8">① event 전달</span><br>
<span style="color:#111827">a. Timer Update Event → UIF set → NVIC → TIMx_IRQHandler()</span><br>
<span style="color:#111827">b. ISR: UIF clear → sample_due flag 또는 event counter 기록 → return</span><br>
<span style="color:#111827">c. main: event를 가져옴 → 실제 sensor/CAN 작업 수행</span><br>
<span style="color:#dc2626">! flag 하나는 여러 event를 합칠 수 있음. 누락이 문제면 counter를 검토</span><br>
<br>
<span style="color:#1d4ed8">5. Timer를 100 ms IMU → CAN 흐름에 연결한다</span><br>
<span style="color:#1d4ed8">1) Timer의 목적</span><br>
<span style="color:#1d4ed8">① delay가 아니라 event</span><br>
<span style="color:#111827">a. Timer의 역할은 100 ms delay를 넣는 것이 아니라 100 ms time event를 만드는 것</span><br>
<span style="color:#111827">b. 센서 읽기와 CAN 송신은 Timer hardware가 아니라 application의 후속 처리</span><br>
<span style="color:#1d4ed8">2) 권장 흐름</span><br>
<span style="color:#1d4ed8">① 100 ms마다 실행할 일</span><br>
<span style="color:#111827">a. Timer가 100 ms마다 Update Event 발생</span><br>
<span style="color:#111827">b. ISR이 UIF를 clear하고 sample event 기록</span><br>
<span style="color:#111827">c. main loop가 event를 가져와 MPU6050 register를 읽음</span><br>
<span style="color:#111827">d. accel/gyro 값을 CAN payload로 만듦</span><br>
<span style="color:#111827">e. CAN 송신 요청 후 UART log로 결과 확인</span><br>
<span style="color:#dc2626">! <strong>I2C transaction 전체를 ISR에서 돌리면 ISR이 길어져 구조의 장점이 사라짐</strong></span><br>
<span style="color:#1d4ed8">3) Blocking과 non-blocking</span><br>
<span style="color:#1d4ed8">① Blocking</span><br>
<span style="color:#111827">a. sensor 읽기 → delay → CAN 송신 → delay</span><br>
<span style="color:#1d4ed8">② Non-blocking</span><br>
<span style="color:#111827">a. Timer가 시간이 지남을 event로 전달하고 main loop는 계속 돌아감</span><br>
<span style="color:#111827">b. UART 수신, 버튼, 오류 event 등 다른 일을 늦게 처리하지 않음</span><br>
<span style="color:#dc2626">★ <strong>non-blocking은 아무것도 안 하는 것이 아니라 기다림을 미래 event로 분리하는 것</strong></span><br>
<span style="color:#1d4ed8">4) 100 ms 계산 예시</span><br>
<span style="color:#1d4ed8">① counter tick을 10 kHz로 만들 때</span><br>
<span style="color:#111827">a. 목표: T = 0.1 s = (PSC+1) × (ARR+1) / timer_clk</span><br>
<span style="color:#111827">b. 100 ms는 1000 counts이므로 ARR + 1 = 1000</span><br>
<span style="color:#111827">c. 실제 timer_clk는 보드의 clock tree에서 먼저 확인</span><br>
<span style="color:#dc2626">! 다른 STM32의 clock 숫자를 현재 보드에 복사하면 안 됨</span><br>
<br>
<span style="color:#1d4ed8">6. PWM은 Timer hardware가 출력 파형을 만든다</span><br>
<span style="color:#1d4ed8">1) PWM의 출발점</span><br>
<span style="color:#1d4ed8">① HIGH와 LOW의 반복</span><br>
<span style="color:#111827">a. <strong>PWM</strong>(Pulse Width Modulation)은 digital HIGH/LOW를 빠르게 반복하는 방식</span><br>
<span style="color:#111827">b. 한 주기 중 HIGH 시간의 비율을 <strong>duty cycle</strong>이라 함</span><br>
<span style="color:#111827">c. LED 밝기, 모터 속도, 부저, 전력 제어에서 평균 에너지 전달을 조절</span><br>
<span style="color:#dc2626">! PWM은 연속 아날로그 전압을 직접 만드는 DAC와 다름</span><br>
<span style="color:#1d4ed8">2) ARR은 주기, CCR은 duty</span><br>
<span style="color:#1d4ed8">① 각 register의 역할</span><br>
<span style="color:#111827">a. ARR은 PWM 전체 주기와 주파수의 기준</span><br>
<span style="color:#111827">b. <strong>CCR</strong>(Capture/Compare Register)은 CNT와 비교할 값</span><br>
<span style="color:#111827">c. PWM에서 CCR은 HIGH 구간 길이, 즉 duty를 결정</span><br>
<span style="color:#111827">d. <strong>주파수는 timer clock·PSC·ARR, duty는 CCR</strong>로 분리해 설명</span><br>
<span style="color:#dc2626">! mode/polarity에 따라 HIGH/LOW 해석은 달라질 수 있음</span><br>
<span style="color:#1d4ed8">3) 예시: ARR = 9, CCR = 4</span><br>
<span style="color:#1d4ed8">① count와 출력</span><br>
<span style="color:#111827">a. CNT: 0 1 2 3 4 5 6 7 8 9 → reload</span><br>
<span style="color:#111827">b. PWM: HIGH HIGH HIGH HIGH | LOW LOW LOW LOW LOW LOW</span><br>
<span style="color:#111827">c. <strong>duty ≈ CCR / (ARR+1)</strong></span><br>
<span style="color:#1d4ed8">그림: PWM의 ARR과 CCR</span><br>
<span style="color:#111827">ARR은 한 주기의 길이, CCR은 HIGH 구간의 길이</span><br>
<span style="color:#dc2626">! 주파수와 duty가 각각 어느 register에 연결되는지 확인</span><br>
<img src="./assets/filginote_05/pwm_arr_ccr.svg" width="720" alt="PWM에서 ARR은 주기, CCR은 duty를 결정하는 구조"><br>
<span style="color:#1d4ed8">4) Timer interrupt와 PWM의 차이</span><br>
<span style="color:#1d4ed8">① Timer interrupt</span><br>
<span style="color:#111827">a. ARR 도달 사건을 CPU가 ISR에서 처리</span><br>
<span style="color:#1d4ed8">② PWM</span><br>
<span style="color:#111827">a. CNT와 CCR 비교 결과를 Timer hardware가 output pin에 직접 반영</span><br>
<span style="color:#111827">b. PWM의 HIGH/LOW 전환마다 CPU가 ISR을 실행할 필요 없음</span><br>
<span style="color:#dc2626">★ <strong>Timer를 쓴다가 항상 ISR을 쓴다는 뜻은 아님</strong></span><br>
<br>
<span style="color:#1d4ed8">7. Hardware Timer와 Software Timer는 목적이 다르다</span><br>
<span style="color:#1d4ed8">1) Hardware Timer</span><br>
<span style="color:#1d4ed8">① <strong>MCU Timer peripheral의 hardware clock</strong>이 시간 기준</span><br>
<span style="color:#111827">a. PWM, 정확한 peripheral timing, input capture에 적합</span><br>
<span style="color:#dc2626">! ISR은 짧게 유지</span><br>
<span style="color:#1d4ed8">2) RTOS Software Timer</span><br>
<span style="color:#1d4ed8">① <strong>RTOS tick</strong>이 시간 기준</span><br>
<span style="color:#111827">a. 단순 timeout과 주기 callback에 적합</span><br>
<span style="color:#111827">b. tick보다 정밀할 수 없음</span><br>
<span style="color:#dc2626">! callback도 길게 block하지 않기</span><br>
<span style="color:#111827">↔ <strong>PWM·정밀 timing은 Hardware Timer, RTOS 위의 단순 timeout은 Software Timer</strong></span><br>
<br>
<span style="color:#dc2626">8. 핵심 3줄</span><br>
<span style="color:#dc2626">1) <strong>Timer는 PSC → CNT → ARR로 시간을 세고 ARR 도달 시 Update Event를 만든다.</strong></span><br>
<span style="color:#dc2626">2) <strong>ISR은 UIF clear와 event 기록만 하고, IMU 읽기·CAN 송신 같은 긴 일은 main/task가 처리한다.</strong></span><br>
<span style="color:#dc2626">3) <strong>PWM은 CNT와 CCR의 비교 결과를 hardware가 pin에 직접 반영하며, 주파수는 PSC·ARR, duty는 CCR로 제어한다.</strong></span><br>
<br>
<span style="color:#dc2626">? Timer가 busy-wait delay보다 나은 이유는?</span><br>
<span style="color:#111827">A. hardware가 시간을 세는 동안 CPU가 다른 작업이나 sleep을 할 수 있고, 필요한 시점에만 event로 대응하기 때문이다.</span><br>
<span style="color:#dc2626">? Timer ISR에 I2C 센서 읽기를 바로 넣지 않는 이유는?</span><br>
<span style="color:#111827">A. transaction이 길어지면 ISR이 main과 다른 interrupt 응답을 늦춘다. ISR은 event만 전달하고 긴 처리는 main/task가 맡는 편이 안전하다.</span><br>
<span style="color:#dc2626">? volatile이면 ISR과 main의 공유 변수는 안전한가?</span><br>
<span style="color:#111827">A. 아니다. volatile은 최적화를 제한할 뿐이며, atomicity나 race condition은 별도로 설계해야 한다.</span><br>
<span style="color:#dc2626">? PWM은 왜 CPU가 매번 pin을 toggle하지 않아도 되는가?</span><br>
<span style="color:#111827">A. Timer hardware가 CNT와 CCR의 비교 결과를 output channel에 직접 반영하기 때문이다.</span><br>
<br>
<span style="color:#1d4ed8">9. 30초 면접 답변</span><br>
<span style="color:#1d4ed8">1) 한 줄 정의</span><br>
<span style="color:#111827">a. Timer는 peripheral clock을 세어 시간 event를 만들고, PWM은 Timer의 비교 기능으로 duty가 있는 출력 파형을 만드는 hardware 기능이다.</span><br>
<span style="color:#1d4ed8">2) 통합 답변</span><br>
<span style="color:#111827">a. Timer는 peripheral clock을 PSC로 분주해 CNT를 세고, ARR에 도달하면 Update Event를 만드는 하드웨어입니다. interrupt를 사용하면 ISR에서는 UIF clear와 event 기록만 짧게 수행하고, IMU 읽기나 CAN 송신은 main loop로 넘겨 다른 event를 막지 않게 합니다. PWM은 같은 Timer에서 CNT와 CCR을 비교해 hardware가 pin의 HIGH/LOW 시간을 직접 바꾸므로, 주파수는 PSC와 ARR, duty는 CCR로 조절할 수 있습니다.</span><br>
<br>
<span style="color:#1d4ed8">10. 지금 깊이 조절</span><br>
<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- PSC, CNT, ARR, CCR, Update Event, ISR, volatile, 100 ms event, PWM</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- exception frame 세부 register, FPU context, ARPE, center-aligned PWM</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- complementary PWM, dead time, FreeRTOS timer service task</span><br>
<span style="color:#dc2626">! 지금은 시간이 event가 되고, ISR과 main이 일을 나누며, PWM이 hardware로 출력을 만든다는 흐름을 먼저 잡는다</span><br>
<br>
<span style="color:#1d4ed8">11. 참고 자료</span><br>
<a style="color:#111827" href="./필기노트_05_Timer_PWM_ver2.md">Timer / PWM ver2 원본</a><br>
<a style="color:#111827" href="../../10_주제별/stm32/timer/1_타이머카운터와_PWM.md">STM32 Timer/Counter와 PWM</a><br>
<a style="color:#111827" href="./필기노트_05_Timer_PWM.md">기존 손필기 v1</a><br>
<a style="color:#111827" href="../../../10_Experience/10_Projects/IMU_CAN_드라이버_시스템.md">IMU-CAN 드라이버 시스템</a><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=XOsyrZGZtR8">STM32 입문 강의 몰아보기 | ARM, GPIO, ADC, UART</a><br>
