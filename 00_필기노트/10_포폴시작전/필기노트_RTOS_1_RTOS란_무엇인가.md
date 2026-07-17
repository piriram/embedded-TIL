<span style="color:#1d4ed8">I. RTOS 1 — RTOS란 무엇인가</span><br>
<br>
<span style="color:#1d4ed8">1. OS와 RTOS의 역할</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>OS(Operating System)</strong>: application 실행과 hardware resource를 관리하는 software</span><br>
<span style="color:#111827">② <strong>scheduler</strong>: 여러 task 중 다음에 CPU를 사용할 task를 선택하는 구성 요소</span><br>
<span style="color:#111827">③ <strong>RTOS</strong>: Real-Time Operating System, deadline을 예측 가능하게 만족하도록 설계된 OS</span><br>
<span style="color:#111827">④ <strong>deterministic</strong>: task 실행 시점과 시간의 상한을 예측할 수 있는 성질</span><br>
<span style="color:#dc2626">★ <strong>real-time은 무조건 빠름이 아니라 정해진 시간 안에 예측 가능하게 동작함</strong></span><br>
<br>
<span style="color:#1d4ed8">2) 일반 OS가 하는 일</span><br>
<span style="color:#111827">① background process와 user application에 CPU 시간 배분</span><br>
<span style="color:#111827">② file·library·folder 같은 virtual resource 관리</span><br>
<span style="color:#111827">③ disk·keyboard·mouse·monitor 같은 device driver 관리</span><br>
<span style="color:#111827">④ Windows·macOS·Linux·iOS·Android는 general purpose OS</span><br>
<br>
<span style="color:#1d4ed8">2. General Purpose OS와 RTOS</span><br>
<span style="color:#1d4ed8">1) General Purpose OS</span><br>
<span style="color:#111827">① 사용자가 느끼는 responsiveness와 여러 application의 원활한 실행을 우선</span><br>
<span style="color:#111827">② 사람이 알아차리지 못할 작은 deadline 지연은 허용할 수 있음</span><br>
<span style="color:#111827">③ task가 정확히 언제·얼마나 실행될지 미리 알기 어려운 non-deterministic scheduler</span><br>
<br>
<span style="color:#1d4ed8">2) RTOS</span><br>
<span style="color:#111827">① scheduler가 task의 timing deadline을 만족하도록 설계</span><br>
<span style="color:#111827">② medical device·engine controller처럼 지연이 치명적인 장치에 필요</span><br>
<span style="color:#111827">③ 여러 task에 CPU 시간을 나누고 중요한 task에 높은 priority 부여</span><br>
<span style="color:#111827">④ RTOS마다 scheduler만 제공하거나 driver·network stack까지 제공할 수 있음</span><br>
<span style="color:#dc2626">! RTOS의 핵심은 기능 개수가 아니라 <strong>deadline과 실행 timing의 예측 가능성</strong></span><br>
<br>
<span style="color:#1d4ed8">3. Super Loop</span><br>
<span style="color:#1d4ed8">1) 기본 구조</span><br>
<span style="color:#111827">setup 실행</span><br>
<span style="color:#111827">→ while(forever) 진입</span><br>
<span style="color:#111827">→ sensor 읽기 → 계산 → display 갱신</span><br>
<span style="color:#111827">→ 다시 loop 처음으로 반복</span><br>
<span style="color:#111827">cf) super loop = 무한 loop 안에서 여러 작업을 차례로 반복하는 firmware 구조</span><br>
<br>
<span style="color:#1d4ed8">2) 장점</span><br>
<span style="color:#111827">① 구현이 단순하고 debugging이 쉬움</span><br>
<span style="color:#111827">② CPU cycle과 memory overhead가 작음</span><br>
<span style="color:#111827">③ task 수가 적고 각 작업이 짧으면 RTOS보다 좋은 선택일 수 있음</span><br>
<span style="color:#dc2626">★ 단순한 MCU project에는 super loop가 충분할 수 있음</span><br>
<br>
<span style="color:#1d4ed8">3) 한계</span><br>
<span style="color:#111827">① task 2가 오래 걸리면 뒤의 task 3도 함께 지연</span><br>
<span style="color:#111827">② display update가 밀려 사용자가 lag를 느낄 수 있음</span><br>
<span style="color:#111827">③ serial input polling이나 sensor data를 놓칠 수 있음</span><br>
<span style="color:#dc2626">! super loop의 한 작업이 오래 걸리면 뒤의 모든 작업 latency가 늘어남</span><br>
<br>
<span style="color:#1d4ed8">그림: Super Loop와 RTOS 비교</span><br>
<span style="color:#111827">Super Loop: [Task A] → [긴 Task B────────] → [늦어진 Task C]</span><br>
<span style="color:#111827">RTOS: [A] → [B 일부] → [중요한 C] → [B 계속]</span><br>
<span style="color:#dc2626">! RTOS scheduler는 CPU 시간을 나누고 priority로 실행 순서를 조절</span><br>
<br>
<span style="color:#1d4ed8">4. Interrupt와 RTOS의 역할 경계</span><br>
<span style="color:#1d4ed8">1) Interrupt가 적합한 경우</span><br>
<span style="color:#111827">① button event나 timer interval처럼 즉시 반응해야 하는 사건 처리</span><br>
<span style="color:#111827">② strict deadline task가 한두 개면 ISR이 더 단순할 수 있음</span><br>
<span style="color:#111827">③ 강의 경험칙: 1ms보다 짧은 deadline은 interrupt 검토</span><br>
<span style="color:#111827">④ 수백 ns보다 짧으면 빠른 processor나 FPGA 같은 hardware 검토</span><br>
<span style="color:#dc2626">! 위 시간은 절대 기준이 아니라 강의의 경험적 판단이며 target에서 검증</span><br>
<br>
<span style="color:#1d4ed8">2) RTOS에서도 interrupt는 동작</span><br>
<span style="color:#111827">① hardware interrupt가 발생하면 실행 중 task를 멈추고 ISR 수행</span><br>
<span style="color:#111827">② ISR이 끝나면 멈춘 지점으로 돌아감</span><br>
<span style="color:#111827">③ nested interrupt는 복잡하므로 ISR을 짧게 유지</span><br>
<span style="color:#dc2626">★ <strong>RTOS는 interrupt를 대체하지 않으며 task와 ISR은 역할이 다름</strong></span><br>
<br>
<span style="color:#1d4ed8">5. Concurrent Task와 priority</span><br>
<span style="color:#1d4ed8">1) Single-Core에서의 concurrent 실행</span><br>
<span style="color:#111827">① core 하나에서는 여러 task가 물리적으로 동시에 실행되지 않음</span><br>
<span style="color:#111827">② scheduler가 CPU 시간을 잘게 나눠 동시에 실행되는 것처럼 보이게 함</span><br>
<span style="color:#111827">③ user input·storage·hardware control·계산을 독립 task로 분리 가능</span><br>
<span style="color:#111827">cf) concurrent = 여러 작업의 실행 구간이 시간상 겹쳐 진행되는 구조</span><br>
<span style="color:#dc2626">! 높은 priority task를 빠르게 처리하면 낮은 priority background task는 더 늦어질 수 있음</span><br>
<br>
<span style="color:#1d4ed8">2) Multi-Core</span><br>
<span style="color:#111827">① core가 여러 개면 서로 다른 task를 실제로 동시에 실행 가능</span><br>
<span style="color:#111827">② ESP32 같은 MCU는 concurrent task를 처리할 resource 여유가 큼</span><br>
<span style="color:#111827">③ shared resource 보호와 core별 실행까지 고려해야 함</span><br>
<br>
<span style="color:#1d4ed8">6. Task / Thread / Process</span><br>
<span style="color:#111827">① <strong>Task</strong>: 코드에서 완료해야 하는 작업 단위</span><br>
<span style="color:#111827">② <strong>Thread</strong>: own program counter와 memory set을 가진 CPU utilization 단위</span><br>
<span style="color:#111827">③ <strong>Process</strong>: 실행 중인 program instance, 하나 이상의 thread를 가질 수 있음</span><br>
<span style="color:#111827">④ 일반 OS의 한 process 안 thread는 heap 같은 resource를 공유</span><br>
<span style="color:#111827">⑤ 많은 RTOS는 하나의 process 구조에 가깝고 FreeRTOS task는 thread에 가까운 의미</span><br>
<span style="color:#dc2626">! FreeRTOS 문맥의 task를 일반적인 독립 process와 같다고 보면 안 됨</span><br>
<br>
<span style="color:#1d4ed8">7. RTOS 도입 비용</span><br>
<span style="color:#1d4ed8">1) Resource overhead</span><br>
<span style="color:#111827">① scheduler와 task switching에 CPU 시간 사용</span><br>
<span style="color:#111827">② 각 task stack과 관리 정보에 RAM 사용</span><br>
<span style="color:#111827">③ 2KB RAM 수준의 작은 8/16-bit MCU에서는 application resource가 부족할 수 있음</span><br>
<span style="color:#111827">④ ESP32처럼 강력한 MCU는 RTOS overhead를 감당하기 쉬움</span><br>
<br>
<span style="color:#1d4ed8">2) 설계·debugging 비용</span><br>
<span style="color:#111827">① task priority와 CPU 시간 배분 설계</span><br>
<span style="color:#111827">② task 간 shared resource와 synchronization 관리</span><br>
<span style="color:#111827">③ 실행 순서에 따라 달라지는 concurrency bug 추적</span><br>
<span style="color:#dc2626">! 기능 분리의 이점보다 scheduling·동기화 비용이 크면 RTOS가 과한 선택</span><br>
<br>
<span style="color:#1d4ed8">8. 언제 RTOS를 선택할까</span><br>
<span style="color:#1d4ed8">1) RTOS가 유리한 조건</span><br>
<span style="color:#111827">① 여러 task를 concurrent하게 처리해야 함</span><br>
<span style="color:#111827">② user input·storage·hardware·network 기능을 분리하고 싶음</span><br>
<span style="color:#111827">③ timing deadline을 예측 가능하게 만족해야 함</span><br>
<span style="color:#111827">④ Wi-Fi·Bluetooth stack처럼 빠른 event response와 많은 resource가 필요</span><br>
<span style="color:#111827">⑤ 팀이 기능을 task 단위로 나눠 개발해야 함</span><br>
<br>
<span style="color:#1d4ed8">2) Super Loop / ISR이 유리한 조건</span><br>
<span style="color:#111827">① task 수가 적고 각 작업이 짧음</span><br>
<span style="color:#111827">② CPU와 RAM이 매우 제한적임</span><br>
<span style="color:#111827">③ deadline 작업이 한두 개라 ISR로 해결 가능</span><br>
<span style="color:#111827">④ RTOS overhead와 debugging 부담이 더 큼</span><br>
<span style="color:#dc2626">★ <strong>RTOS는 모든 firmware의 정답이 아니라 복잡도와 resource를 교환하는 도구</strong></span><br>
<br>
<span style="color:#1d4ed8">9. FreeRTOS와 ESP32</span><br>
<span style="color:#111827">① FreeRTOS는 free/open source이며 IoT device에서 널리 사용</span><br>
<span style="color:#111827">② 2017년부터 Amazon이 project maintenance 담당</span><br>
<span style="color:#111827">③ Zephyr도 Linux Foundation 지원 RTOS project</span><br>
<span style="color:#111827">④ ESP32는 modified FreeRTOS를 기본 실행하며 Arduino에서도 task 생성 가능</span><br>
<span style="color:#111827">⑤ ESP32 RTOS는 vanilla FreeRTOS와 완전히 같지 않음</span><br>
<span style="color:#dc2626">! API와 동작 차이는 ESP-IDF·FreeRTOS 문서를 함께 확인</span><br>
<br>
<span style="color:#1d4ed8">10. 핵심 3줄</span><br>
<span style="color:#111827">1) <strong>RTOS는 여러 task에 CPU 시간을 배분하면서 timing deadline을 예측 가능하게 만족하도록 설계된 운영체제다.</strong></span><br>
<span style="color:#111827">2) <strong>Super loop는 단순하고 overhead가 작지만 긴 작업이 뒤 작업을 지연시키며, RTOS는 priority로 독립 task를 조정한다.</strong></span><br>
<span style="color:#111827">3) <strong>작은 MCU나 짧은 deadline 작업은 super loop·interrupt가 더 적합할 수 있으므로 resource와 복잡도를 보고 선택한다.</strong></span><br>
<br>
<span style="color:#1d4ed8">Q. RTOS에서 real-time은 무슨 뜻인가?</span><br>
<span style="color:#111827">A. 무조건 빠르다는 뜻이 아니라 정해진 deadline 안에 예측 가능하게 동작한다는 뜻이다.</span><br>
<span style="color:#1d4ed8">Q. Super Loop의 가장 큰 한계는?</span><br>
<span style="color:#111827">A. 한 작업이 오래 걸리면 뒤의 display·input·sensor 작업이 모두 밀릴 수 있다는 점이다.</span><br>
<span style="color:#1d4ed8">Q. RTOS와 interrupt 중 무엇을 선택해야 하는가?</span><br>
<span style="color:#111827">A. 여러 concurrent 기능과 deadline 관리에는 RTOS가 유리하고, 매우 짧고 정확한 event가 한두 개면 ISR이 더 적합할 수 있다.</span><br>
<span style="color:#1d4ed8">Q. RTOS가 작은 MCU에 부적합할 수 있는 이유는?</span><br>
<span style="color:#111827">A. scheduler와 task switching, task별 stack이 제한된 CPU와 RAM을 사용하기 때문이다.</span><br>
<br>
<span style="color:#1d4ed8">11. 30초 면접 답변</span><br>
<span style="color:#111827">RTOS는 여러 task를 동시에 실행하는 것처럼 관리하면서 각 task의 timing deadline을 예측 가능하게 만족하도록 설계된 운영체제입니다.</span><br>
<span style="color:#111827">Super loop는 단순하고 overhead가 작지만 한 작업이 오래 걸리면 display update나 sensor polling 같은 뒤 작업이 함께 밀릴 수 있습니다.</span><br>
<span style="color:#111827">RTOS scheduler는 CPU 시간을 task에 나누고 priority를 적용해 중요한 작업을 먼저 처리합니다.</span><br>
<span style="color:#dc2626">다만 작은 MCU나 매우 짧은 timing 작업은 super loop와 interrupt가 더 적합할 수 있어 task 수·deadline·RAM·debugging 비용을 보고 선택합니다.</span><br>
<br>
<span style="color:#1d4ed8">12. 지금 깊이 조절</span><br>
<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- real-time = deadline의 예측 가능성</span><br>
<span style="color:#111827">- General Purpose OS와 RTOS 차이</span><br>
<span style="color:#111827">- Super Loop의 장점과 한계</span><br>
<span style="color:#111827">- RTOS와 interrupt의 역할 경계</span><br>
<span style="color:#111827">- RTOS 도입 기준과 overhead</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- task / thread / process</span><br>
<span style="color:#111827">- FreeRTOS / Zephyr / ESP RTOS</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- scheduler policy와 worst-case response time</span><br>
<span style="color:#111827">- synchronization과 shared resource</span><br>
<span style="color:#111827">- multicore scheduling과 nested interrupt</span><br>
<span style="color:#dc2626">! 지금은 RTOS가 필요한 상황과 필요하지 않은 상황을 구분한다</span><br>
<br>
<span style="color:#1d4ed8">13. 참고 자료</span><br>
<a style="color:#111827" href="../../10_주제별/cs/RTOS/1_RTOS란_무엇인가.md">RTOS란 무엇인가 — 원본 학습노트</a><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=F321087yYy4">Introduction to RTOS Part 1</a><br>
<a style="color:#111827" href="https://www.freertos.org/">FreeRTOS</a><br>
<a style="color:#111827" href="https://www.zephyrproject.org/">Zephyr Project</a><br>
