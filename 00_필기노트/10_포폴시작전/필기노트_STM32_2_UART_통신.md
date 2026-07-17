<span style="color:#1d4ed8">I. STM32 실전 2 — UART 통신</span><br>
<br>
<span style="color:#1d4ed8">1. UART의 통신 분류</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>Serial</strong>: 데이터를 한 bit씩 순서대로 보내는 통신</span><br>
<span style="color:#111827">② <strong>Full Duplex</strong>: 양방향으로 동시에 송수신할 수 있는 방식</span><br>
<span style="color:#111827">③ <strong>Asynchronous</strong>: 별도 clock 선 없이 양쪽이 통신 속도를 약속하는 방식</span><br>
<span style="color:#111827">④ <strong>UART</strong>: Universal Asynchronous Receiver Transmitter</span><br>
<span style="color:#dc2626">★ <strong>UART = 비동기·직렬·전이중 통신</strong></span><br>
<br>
<span style="color:#1d4ed8">2) Serial vs Parallel</span><br>
<span style="color:#111827">① Serial: 한 bit씩 전송, 배선이 적고 간섭이 적어 임베디드에서 널리 사용</span><br>
<span style="color:#111827">② Parallel: 여러 bit를 동시에 전송, 빠르지만 배선이 복잡하고 거리가 길면 noise 증가</span><br>
<span style="color:#111827">③ UART·SPI·I2C·USB·Ethernet·CAN은 serial 통신</span><br>
<span style="color:#111827">↔ 구분 기준: 한 번에 한 bit를 보내는가, 여러 bit를 동시에 보내는가</span><br>
<br>
<span style="color:#1d4ed8">3) Full Duplex vs Half Duplex</span><br>
<span style="color:#111827">① Full Duplex: 전화처럼 양쪽이 동시에 송수신 가능</span><br>
<span style="color:#111827">② Half Duplex: 무전기처럼 양방향이지만 동시에 송수신할 수 없음</span><br>
<span style="color:#111827">③ UART는 TX와 RX 선이 분리되어 full duplex 가능</span><br>
<span style="color:#111827">↔ 구분 기준: 양방향 통신을 동시에 할 수 있는가</span><br>
<br>
<span style="color:#1d4ed8">4) Synchronous vs Asynchronous</span><br>
<span style="color:#111827">① Synchronous: SPI·I2C처럼 clock 신호에 맞춰 송수신</span><br>
<span style="color:#111827">② Asynchronous: UART처럼 clock 선 없이 baud rate를 맞춰 송수신</span><br>
<span style="color:#111827">③ STM32F767의 USART는 synchronous와 asynchronous를 지원하지만 여기서는 UART 방식 사용</span><br>
<span style="color:#111827">cf) USART = Universal Synchronous/Asynchronous Receiver Transmitter</span><br>
<span style="color:#dc2626">! clock 선이 없으므로 <strong>양쪽의 통신 설정이 반드시 같아야 함</strong></span><br>
<br>
<span style="color:#1d4ed8">2. UART frame과 결선</span><br>
<span style="color:#1d4ed8">1) UART frame의 약속</span><br>
<span style="color:#111827">① Idle: 전송하지 않을 때 data line은 High</span><br>
<span style="color:#111827">② Start bit: line이 Low로 내려가며 frame 시작</span><br>
<span style="color:#111827">③ Data bits: 실제 data 5~8bit</span><br>
<span style="color:#111827">④ Parity bit: 선택적인 오류 검출 bit, 이 실습에서는 사용하지 않음</span><br>
<span style="color:#111827">⑤ Stop bit: line을 High로 올려 frame 종료, 1~2bit 선택</span><br>
<span style="color:#dc2626">★ <strong>Idle High → Start Low → Data → 선택적 Parity → Stop High</strong></span><br>
<br>
<span style="color:#1d4ed8">그림: UART frame</span><br>
<span style="color:#111827">[Idle High] → [Start Low] → [Data 5~8bit] → [Parity] → [Stop High]</span><br>
<span style="color:#dc2626">! TX와 RX는 baud rate·data bit·parity·stop bit 설정을 맞춤</span><br>
<br>
<span style="color:#1d4ed8">2) 문자 A 전송 예시</span><br>
<span style="color:#111827">① 문자 'A'의 ASCII 값 = 0100 0001</span><br>
<span style="color:#111827">② 8 data bit 설정에서 Start Low → 0100 0001 → Stop High 순서로 전송</span><br>
<span style="color:#111827">cf) ASCII = 문자와 숫자 code를 대응시킨 표준 문자 encoding</span><br>
<br>
<span style="color:#1d4ed8">3) TX와 RX 교차 결선</span><br>
<span style="color:#111827">MCU TX ─────────→ 상대 RX</span><br>
<span style="color:#111827">MCU RX ←───────── 상대 TX</span><br>
<span style="color:#dc2626">! <strong>TX↔RX를 교차</strong>하며 TX끼리·RX끼리 연결하면 통신되지 않음</span><br>
<br>
<span style="color:#1d4ed8">3. baud rate와 BRR 설정</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>baud rate</strong>: 송수신 timing을 맞추기 위한 통신 속도 설정</span><br>
<span style="color:#111827">② <strong>BPS(Bits Per Second)</strong>: 1초에 전송하는 bit 수</span><br>
<span style="color:#111827">③ <strong>USART_BRR</strong>: USART의 baud rate를 정하는 register</span><br>
<span style="color:#dc2626">! 비동기 통신은 양쪽 clock이 따로이므로 baud rate 오차가 누적될 수 있음</span><br>
<br>
<span style="color:#1d4ed8">2) STM32F767 USART2 계산</span><br>
<span style="color:#111827">① USART2 clock = APB1 54MHz</span><br>
<span style="color:#111827">② 9600bps: 54,000,000 / 9,600 = 5,625 → BRR = 5625</span><br>
<span style="color:#111827">③ 115200bps: 54,000,000 / 115,200 = 468.75 → 반올림 469</span><br>
<span style="color:#111827">④ 자주 쓰는 속도: 9600 / 115200</span><br>
<span style="color:#dc2626">! OVER8 설정에 따라 계산식이 달라지므로 clock·oversampling 조건을 함께 확인</span><br>
<span style="color:#dc2626">★ <strong>USART clock과 원하는 BPS를 확인한 뒤 BRR 값을 계산</strong></span><br>
<br>
<span style="color:#1d4ed8">4. USART2 초기화</span><br>
<span style="color:#1d4ed8">1) 필요한 register와 bit</span><br>
<span style="color:#111827">① RCC_APB1ENR: USART2 peripheral clock enable</span><br>
<span style="color:#111827">② RCC_AHB1ENR: GPIOD clock enable</span><br>
<span style="color:#111827">③ GPIOD_MODER: PD5·PD6을 Alternate Function mode(10)로 설정</span><br>
<span style="color:#111827">④ USART_CR1/CR2/CR3: USART 동작 조건 설정</span><br>
<span style="color:#111827">⑤ USART_BRR: baud rate 설정</span><br>
<span style="color:#111827">⑥ UE(bit0): USART Enable</span><br>
<span style="color:#111827">⑦ RE(bit2): Receiver Enable</span><br>
<span style="color:#111827">⑧ TE(bit3): Transmitter Enable</span><br>
<span style="color:#111827">cf) Alternate Function = GPIO pin을 일반 입출력 대신 UART 등 주변장치 신호에 연결하는 mode</span><br>
<span style="color:#dc2626">! PD5=TX, PD6=RX이며 GPIO mode만 바꾸는 것이 아니라 peripheral clock도 켜야 함</span><br>
<br>
<span style="color:#1d4ed8">2) 설정 순서</span><br>
<span style="color:#111827">① init_MCU()로 기본 clock 초기화</span><br>
<span style="color:#111827">② APB1에서 USART2 clock enable</span><br>
<span style="color:#111827">③ AHB에서 GPIOD clock enable</span><br>
<span style="color:#111827">④ PD5·PD6을 Alternate Function mode로 설정</span><br>
<span style="color:#111827">⑤ USART_CR1/CR2/CR3을 0으로 초기화해 비활성 상태에서 설정</span><br>
<span style="color:#111827">⑥ USART_BRR에 baud rate 계산값 기록</span><br>
<span style="color:#111827">⑦ CR1의 UE·RE·TE enable</span><br>
<span style="color:#dc2626">★ <strong>clock → GPIO AF → USART 비활성 설정 → BRR → UE/RE/TE enable</strong></span><br>
<br>
<span style="color:#1d4ed8">3) 핵심 설정 표현</span><br>
<span style="color:#111827">RCC-&gt;APB1ENR |= (1U &lt;&lt; 17); → USART2 clock</span><br>
<span style="color:#111827">RCC-&gt;AHB1ENR |= (1U &lt;&lt; 3); → GPIOD clock</span><br>
<span style="color:#111827">GPIOD-&gt;MODER |= (2U &lt;&lt; (5U * 2U)); → PD5 AF mode</span><br>
<span style="color:#111827">GPIOD-&gt;MODER |= (2U &lt;&lt; (6U * 2U)); → PD6 AF mode</span><br>
<span style="color:#111827">USART2-&gt;BRR = 5625; → 9600bps</span><br>
<span style="color:#111827">USART2-&gt;CR1 |= (1U&lt;&lt;0) | (1U&lt;&lt;2) | (1U&lt;&lt;3); → UE·RE·TE</span><br>
<span style="color:#dc2626">! register bit 번호와 pin의 실제 Alternate Function 연결은 reference manual·datasheet로 확인</span><br>
<br>
<span style="color:#1d4ed8">5. polling으로 문자 송수신</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>polling</strong>: 원하는 상태가 될 때까지 flag를 반복해서 확인하는 방식</span><br>
<span style="color:#111827">② <strong>USART_ISR</strong>: 송수신 상태 flag를 담는 register</span><br>
<span style="color:#111827">③ <strong>TXE</strong>: Transmit Data Register Empty, 송신 register가 비었음을 알림</span><br>
<span style="color:#111827">④ <strong>RXNE</strong>: Receive Data Register Not Empty, 받은 data가 있음을 알림</span><br>
<span style="color:#111827">⑤ <strong>TDR/RDR</strong>: 송신 data 쓰기 / 수신 data 읽기 register</span><br>
<span style="color:#dc2626">! flag 확인 없이 TDR/RDR에 접근하지 말고 data 준비 상태를 먼저 확인</span><br>
<br>
<span style="color:#1d4ed8">2) TX 흐름</span><br>
<span style="color:#111827">USART_ISR의 TXE(bit7) 확인</span><br>
<span style="color:#111827">→ TXE=0이면 TDR가 빌 때까지 대기</span><br>
<span style="color:#111827">→ TXE=1이면 USART_TDR에 문자 쓰기</span><br>
<span style="color:#111827">→ USART가 자동으로 serial frame 송신</span><br>
<span style="color:#dc2626">★ <strong>TXE 대기 → TDR write → hardware 송신</strong></span><br>
<br>
<span style="color:#1d4ed8">3) RX 흐름</span><br>
<span style="color:#111827">USART_ISR의 RXNE(bit5) 확인</span><br>
<span style="color:#111827">→ RXNE=0이면 data가 들어올 때까지 대기</span><br>
<span style="color:#111827">→ RXNE=1이면 USART_RDR에서 문자 읽기</span><br>
<span style="color:#111827">→ 받은 값을 함수 반환값으로 전달</span><br>
<span style="color:#dc2626">★ <strong>RXNE 대기 → RDR read → 수신 data 사용</strong></span><br>
<br>
<span style="color:#1d4ed8">4) polling의 특징</span><br>
<span style="color:#111827">① 코드가 단순해 첫 송수신 실습과 동작 확인에 적합</span><br>
<span style="color:#111827">② data가 올 때까지 while문에서 CPU가 계속 기다림</span><br>
<span style="color:#111827">③ 이 노트는 polling 방식이며 interrupt·DMA는 이후 별도 학습</span><br>
<span style="color:#dc2626">! blocking receive는 data가 오지 않으면 다음 일을 수행하지 못함</span><br>
<br>
<span style="color:#1d4ed8">6. PC 연결과 loopback 성격의 실습</span><br>
<span style="color:#1d4ed8">1) 하드웨어와 프로그램</span><br>
<span style="color:#111827">① MCU UART를 PC USB에 바로 연결하지 않고 USB-UART 변환 module 사용</span><br>
<span style="color:#111827">② PC에서는 Tera Term으로 COM port와 serial 속도 설정</span><br>
<span style="color:#111827">③ Tera Term Speed = MCU와 같은 9600</span><br>
<span style="color:#111827">④ Bluetooth module도 MCU와는 UART로 통신할 수 있음</span><br>
<span style="color:#dc2626">! PC·MCU·변환 module 사이 TX/RX 교차와 같은 baud rate 확인</span><br>
<br>
<span style="color:#1d4ed8">2) 받은 문자 +1 되돌리기</span><br>
<span style="color:#111827">PC에서 'a' 송신</span><br>
<span style="color:#111827">→ MCU가 uart_recv_char()로 수신</span><br>
<span style="color:#111827">→ received += 1</span><br>
<span style="color:#111827">→ uart_send_char()로 'b' 송신</span><br>
<span style="color:#111827">→ Tera Term에서 'b' 확인</span><br>
<span style="color:#dc2626">★ 송신과 수신 경로를 한 번에 검증하는 가장 단순한 기능 시험</span><br>
<br>
<span style="color:#1d4ed8">3) 통신 불량 점검 순서</span><br>
<span style="color:#111827">① Tera Term이 올바른 COM port를 열었는가?</span><br>
<span style="color:#111827">② PC와 MCU의 baud·data bit·parity·stop bit가 같은가?</span><br>
<span style="color:#111827">③ TX↔RX가 교차 연결됐는가?</span><br>
<span style="color:#111827">④ USART2와 GPIOD clock이 enable됐는가?</span><br>
<span style="color:#111827">⑤ PD5·PD6이 올바른 Alternate Function mode인가?</span><br>
<span style="color:#111827">⑥ CR1의 UE·RE·TE가 enable됐는가?</span><br>
<span style="color:#111827">⑦ debugger에서 TXE·RXNE와 TDR·RDR 값을 확인했는가?</span><br>
<span style="color:#dc2626">! <strong>PC 설정 → 배선 → clock/pin → USART register → status flag</strong> 순서로 좁힘</span><br>
<br>
<span style="color:#1d4ed8">7. 핵심 3줄</span><br>
<span style="color:#111827">1) <strong>UART는 clock 선 없이 양쪽이 baud rate와 frame 형식을 맞춰 한 bit씩 송수신하는 비동기 직렬·전이중 통신이다.</strong></span><br>
<span style="color:#111827">2) <strong>STM32F767 USART2는 clock과 GPIO AF를 설정하고 BRR을 기록한 뒤 CR1의 UE·RE·TE를 enable한다.</strong></span><br>
<span style="color:#111827">3) <strong>송신은 TXE 확인 후 TDR에 쓰고, 수신은 RXNE 확인 후 RDR에서 읽으며 TX와 RX는 교차 결선한다.</strong></span><br>
<br>
<span style="color:#1d4ed8">Q. UART가 비동기 통신인 이유는?</span><br>
<span style="color:#111827">A. 별도 clock 선 없이 송수신 양쪽이 같은 baud rate와 frame 형식을 약속해 timing을 맞추기 때문이다.</span><br>
<span style="color:#1d4ed8">Q. TX와 RX를 왜 교차 연결하는가?</span><br>
<span style="color:#111827">A. 한 장치가 보내는 TX 신호를 상대 장치의 수신 입력 RX가 받아야 하기 때문이다.</span><br>
<span style="color:#1d4ed8">Q. BRR 값은 어떻게 구하는가?</span><br>
<span style="color:#111827">A. 이 실습 조건에서는 USART2의 APB1 54MHz clock을 원하는 BPS로 나눈 값을 사용하며 OVER8 조건도 확인한다.</span><br>
<span style="color:#1d4ed8">Q. TXE와 RXNE의 역할은?</span><br>
<span style="color:#111827">A. TXE는 TDR에 새 data를 쓸 수 있음을, RXNE는 RDR에 읽을 data가 들어왔음을 알리는 상태 flag다.</span><br>
<span style="color:#1d4ed8">Q. polling UART의 단점은?</span><br>
<span style="color:#111827">A. flag가 바뀔 때까지 CPU가 while문에서 기다려 다른 작업을 수행하지 못할 수 있다는 점이다.</span><br>
<br>
<span style="color:#1d4ed8">8. 30초 면접 답변</span><br>
<span style="color:#111827">UART는 별도 clock 선 없이 송수신 양쪽이 같은 baud rate를 약속해 data를 한 bit씩 주고받는 비동기 직렬 통신입니다.</span><br>
<span style="color:#111827">Frame은 Idle High 상태에서 Start Low, data bit, 선택적인 parity, Stop High 순서로 구성되고 TX와 RX는 교차 연결합니다.</span><br>
<span style="color:#111827">STM32에서는 USART clock과 GPIO Alternate Function을 설정하고, BRR로 baud rate를 정한 뒤 CR1의 UE·RE·TE를 enable합니다.</span><br>
<span style="color:#dc2626">송신은 TXE를 확인해 TDR에 쓰고 수신은 RXNE를 확인해 RDR에서 읽으며, 통신 불량은 설정·배선·clock·pin·status flag 순으로 점검합니다.</span><br>
<br>
<span style="color:#1d4ed8">9. 지금 깊이 조절</span><br>
<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- 비동기·직렬·전이중의 의미</span><br>
<span style="color:#111827">- Idle → Start → Data → Stop frame</span><br>
<span style="color:#111827">- TX↔RX 교차와 양쪽 설정 일치</span><br>
<span style="color:#111827">- clock → GPIO AF → BRR → UE/RE/TE</span><br>
<span style="color:#111827">- TXE/TDR 송신과 RXNE/RDR 수신</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- USART, parity, OVER8</span><br>
<span style="color:#111827">- USB-UART 변환 module, Tera Term</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- UART interrupt와 ring buffer</span><br>
<span style="color:#111827">- DMA 기반 송수신</span><br>
<span style="color:#111827">- baud rate 오차율과 oversampling 계산</span><br>
<span style="color:#111827">- framing·parity·overrun error 처리</span><br>
<span style="color:#dc2626">! 지금은 frame·결선·초기화·polling 송수신 흐름을 직접 설명한다</span><br>
<br>
<span style="color:#1d4ed8">10. 참고 자료</span><br>
<a style="color:#111827" href="../../10_주제별/stm32/uart/1_UART통신.md">STM32 UART 통신 — 원본 학습노트</a><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=XOsyrZGZtR8">STM32 입문 강의 몰아보기</a><br>
<a style="color:#111827" href="../../10_주제별/stm32/gpio/1_GPIO출력과_LED제어.md">GPIO 출력과 LED 제어</a><br>
<a style="color:#111827" href="../../10_주제별/stm32/기초/3_클럭과_PLL설정.md">클럭과 PLL 설정</a><br>
