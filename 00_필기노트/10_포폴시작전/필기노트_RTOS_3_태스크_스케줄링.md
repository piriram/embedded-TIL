<span style="color:#1d4ed8">I. RTOS 3 — Task Scheduling</span><br>
<br>
<span style="color:#1d4ed8">1. Single-Core에서 여러 task를 실행하는 방법</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>task</strong>: scheduler가 독립적으로 실행·관리하는 작업 단위</span><br>
<span style="color:#111827">② <strong>scheduler</strong>: 다음에 CPU를 사용할 task를 선택하는 RTOS 구성 요소</span><br>
<span style="color:#111827">③ <strong>priority</strong>: task 실행 중요도를 나타내는 값</span><br>
<span style="color:#111827">④ <strong>preemption</strong>: 더 높은 priority task가 현재 task의 CPU 사용을 빼앗는 것</span><br>
<span style="color:#dc2626">★ <strong>Single-Core에서는 한 순간에 task 하나만 실행되고 scheduler가 CPU 시간을 나눔</strong></span><br>
<br>
<span style="color:#1d4ed8">2) 동시에 보이는 이유</span><br>
<span style="color:#111827">① 각 task 코드는 독립적인 while(forever)처럼 작성</span><br>
<span style="color:#111827">② CPU가 짧은 시간 조각마다 실행 task를 빠르게 교체</span><br>
<span style="color:#111827">③ timer·pin·message event는 hardware interrupt로 처리 가능</span><br>
<span style="color:#111827">④ 실제 parallel 실행이 아니라 time sharing으로 concurrent하게 보임</span><br>
<br>
<span style="color:#1d4ed8">그림: Single-Core CPU timeline</span><br>
<span style="color:#111827">시간 → [Task A] [Task B] [Task C] [Task B] [Task A]</span><br>
<span style="color:#dc2626">! task는 각각 계속 실행되는 것처럼 보여도 CPU core 하나를 번갈아 사용</span><br>
<br>
<span style="color:#1d4ed8">2. Tick과 Time Slicing</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>tick</strong>: hardware timer가 scheduler 실행 기회를 만드는 주기적 시간 단위</span><br>
<span style="color:#111827">② <strong>time slice</strong>: 한 task가 다음 scheduling 판단 전까지 CPU를 쓰는 시간 조각</span><br>
<span style="color:#111827">③ <strong>ready list</strong>: 지금 실행 가능한 task 목록</span><br>
<span style="color:#dc2626">! tick은 task 자체가 아니라 scheduler 판단의 시간 기준</span><br>
<br>
<span style="color:#1d4ed8">2) FreeRTOS scheduling 흐름</span><br>
<span style="color:#111827">hardware timer가 일정 간격으로 interrupt 발생</span><br>
<span style="color:#111827">→ tick 도착</span><br>
<span style="color:#111827">→ scheduler가 ready task와 priority 확인</span><br>
<span style="color:#111827">→ 다음 running task 선택</span><br>
<span style="color:#111827">→ 필요하면 context switch</span><br>
<span style="color:#111827">cf) 강의의 ESP32 예제는 1ms tick 사용</span><br>
<span style="color:#dc2626">★ <strong>ready 상태 중 가장 높은 priority task가 먼저 선택</strong></span><br>
<br>
<span style="color:#1d4ed8">3. Priority / Round-Robin / Preemptive Scheduling</span><br>
<span style="color:#1d4ed8">1) Priority 기반 선택</span><br>
<span style="color:#111827">① Task A priority 0, Task B·C priority 1이라면 B·C가 A보다 먼저 실행</span><br>
<span style="color:#111827">② 높은 priority task가 ready이면 낮은 priority task는 기다림</span><br>
<span style="color:#111827">③ priority 숫자와 최대 범위는 FreeRTOSConfig 설정에 따라 확인</span><br>
<span style="color:#dc2626">! 높은 priority task가 계속 ready이면 낮은 priority task 실행이 밀릴 수 있음</span><br>
<br>
<span style="color:#1d4ed8">2) Round-Robin</span><br>
<span style="color:#111827">① 같은 priority의 ready task가 여러 개면 번갈아 CPU 사용</span><br>
<span style="color:#111827">② 예시: priority 1인 B와 C가 차례로 time slice를 받음</span><br>
<span style="color:#111827">③ 같은 priority 안에서 실행 기회를 나누는 scheduling 방식</span><br>
<br>
<span style="color:#1d4ed8">3) Preemptive Scheduling</span><br>
<span style="color:#111827">① 낮은 priority task 실행 중 높은 priority task가 ready로 전환</span><br>
<span style="color:#111827">② scheduler가 높은 priority task를 선택</span><br>
<span style="color:#111827">③ 기존 task의 context를 저장하고 높은 priority task로 전환</span><br>
<span style="color:#111827">④ 강의의 단순 timeline에서는 tick 중간에 ready가 된 task가 다음 tick에 선택</span><br>
<span style="color:#dc2626">★ <strong>priority는 실행 순서를 보장하는 절대 시간표가 아니라 ready task 선택 기준</strong></span><br>
<br>
<span style="color:#1d4ed8">4. vTaskDelay와 Blocked State</span><br>
<span style="color:#1d4ed8">1) vTaskDelay 동작</span><br>
<span style="color:#111827">① 실행 중 task가 vTaskDelay(2)를 호출</span><br>
<span style="color:#111827">② 2 ticks 동안 blocked state로 이동</span><br>
<span style="color:#111827">③ blocked 동안 CPU를 사용하지 않고 scheduler 선택 대상에서 제외</span><br>
<span style="color:#111827">④ delay 만료 후 ready state로 복귀</span><br>
<span style="color:#dc2626">! vTaskDelay는 CPU 전체를 멈추는 것이 아니라 현재 task만 기다리게 함</span><br>
<br>
<span style="color:#1d4ed8">2) Event 대기</span><br>
<span style="color:#111827">① Queue wait: message가 들어올 때까지 blocked</span><br>
<span style="color:#111827">② Semaphore wait: semaphore가 release될 때까지 blocked</span><br>
<span style="color:#111827">③ 기다리는 task가 CPU를 점유하지 않아 다른 task가 실행 가능</span><br>
<span style="color:#dc2626">★ 기다릴 일이 있으면 busy loop보다 blocked state를 활용</span><br>
<br>
<span style="color:#1d4ed8">5. Task State</span><br>
<span style="color:#1d4ed8">1) Ready</span><br>
<span style="color:#111827">① task가 생성되면 ready state 진입</span><br>
<span style="color:#111827">② 실행할 준비가 됐지만 더 높은 priority task 때문에 기다릴 수 있음</span><br>
<span style="color:#111827">③ 같은 priority task가 있으면 round-robin 차례를 기다림</span><br>
<br>
<span style="color:#1d4ed8">2) Running</span><br>
<span style="color:#111827">① scheduler가 선택해 CPU를 실제 사용 중인 상태</span><br>
<span style="color:#111827">② Single-Core에서는 한 순간에 running task가 하나</span><br>
<span style="color:#111827">③ Multi-Core에서는 core 수만큼 동시에 running 가능</span><br>
<br>
<span style="color:#1d4ed8">3) Blocked</span><br>
<span style="color:#111827">① delay·queue·semaphore 같은 event를 기다리는 상태</span><br>
<span style="color:#111827">② CPU를 사용하지 않고 unblock event가 오면 ready 복귀</span><br>
<br>
<span style="color:#1d4ed8">4) Suspended</span><br>
<span style="color:#111827">① vTaskSuspend로 scheduler 선택 대상에서 제외</span><br>
<span style="color:#111827">② timer나 event로 자동 복귀하지 않음</span><br>
<span style="color:#111827">③ vTaskResume 명시적 호출이 있어야 ready로 복귀</span><br>
<span style="color:#dc2626">! Blocked는 event로 복귀 / Suspended는 명시적 resume으로 복귀</span><br>
<br>
<span style="color:#1d4ed8">그림: Task state transition</span><br>
<span style="color:#111827">생성 → Ready ⇄ Running</span><br>
<span style="color:#111827">Running → delay/queue/semaphore wait → Blocked → event → Ready</span><br>
<span style="color:#111827">Running → vTaskSuspend → Suspended → vTaskResume → Ready</span><br>
<span style="color:#dc2626">! Ready는 실행 가능, Running은 실제 실행, Blocked·Suspended는 선택 제외</span><br>
<br>
<span style="color:#1d4ed8">6. Hardware Interrupt와 Scheduler</span><br>
<span style="color:#111827">① hardware interrupt는 RTOS task priority와 별도 우선순위 체계</span><br>
<span style="color:#111827">② task 실행 중 interrupt가 발생하면 task를 멈추고 ISR 수행</span><br>
<span style="color:#111827">③ ISR 종료 뒤 중단 지점으로 돌아가고 scheduler가 다음 task를 결정</span><br>
<span style="color:#111827">④ interrupt끼리 preempt하는 nested interrupt는 hardware·설정에 따라 다름</span><br>
<span style="color:#dc2626">★ <strong>hardware interrupt priority와 task priority를 같은 층위로 보면 안 됨</strong></span><br>
<span style="color:#dc2626">! ISR이 길면 모든 task의 system latency가 늘어나므로 짧게 유지</span><br>
<br>
<span style="color:#1d4ed8">7. Context Switching</span><br>
<span style="color:#1d4ed8">1) Context에 포함되는 것</span><br>
<span style="color:#111827">① program counter: 다음 실행 instruction 위치</span><br>
<span style="color:#111827">② CPU register 값</span><br>
<span style="color:#111827">③ stack의 함수 호출 정보와 지역 변수</span><br>
<span style="color:#111827">④ task가 사용 중인 working memory 상태</span><br>
<span style="color:#111827">cf) context = task가 중단 지점부터 다시 실행되기 위해 보존해야 하는 실행 문맥</span><br>
<br>
<span style="color:#1d4ed8">2) Context Switch 흐름</span><br>
<span style="color:#111827">현재 Task A context 저장</span><br>
<span style="color:#111827">→ 다음 Task B context 복원</span><br>
<span style="color:#111827">→ Task B가 이전 중단 지점부터 실행</span><br>
<span style="color:#dc2626">! context switching도 CPU 시간과 task stack을 사용하므로 공짜가 아님</span><br>
<span style="color:#dc2626">! task stack이 너무 작으면 함수 실행과 context 저장 중 문제가 생길 수 있음</span><br>
<br>
<span style="color:#1d4ed8">8. Multi-Core Scheduler</span><br>
<span style="color:#111827">① Single-Core: 한 순간에 running task 하나</span><br>
<span style="color:#111827">② Multi-Core: scheduler가 서로 다른 core에 task를 배치해 실제 동시 실행 가능</span><br>
<span style="color:#111827">③ ESP32는 multi-core 환경을 제공</span><br>
<span style="color:#111827">④ core 배치와 shared resource 보호까지 고려해야 해 scheduling이 복잡해짐</span><br>
<span style="color:#dc2626">! scheduling 원리를 처음 볼 때는 한 core로 제한하면 timeline을 해석하기 쉬움</span><br>
<br>
<span style="color:#1d4ed8">9. ESP32 Preemption 실습</span><br>
<span style="color:#1d4ed8">1) 실습 구성</span><br>
<span style="color:#111827">① 문자열 출력 task: priority 1, 문자 단위 출력 후 1초 delay</span><br>
<span style="color:#111827">② asterisk(*) task: priority 2, 100ms마다 출력</span><br>
<span style="color:#111827">③ control task: asterisk task suspend/resume, 문자열 task delete</span><br>
<span style="color:#111827">④ Serial = 300 baud로 낮춰 preemption이 눈에 보이게 함</span><br>
<span style="color:#111827">⑤ setup·loop도 자체 task 안에서 실행</span><br>
<br>
<span style="color:#1d4ed8">2) 관찰 결과</span><br>
<span style="color:#111827">① priority 2 asterisk task가 문자열 task를 preempt해 문장 중간에 * 출력</span><br>
<span style="color:#111827">② suspend하면 *가 멈추고 resume하면 다시 출력</span><br>
<span style="color:#111827">③ 문자열 task 삭제 후 asterisk task만 계속 실행</span><br>
<span style="color:#dc2626">! Serial.print 전체 문자열은 buffer에 한 번에 복사될 수 있어 문자 단위 출력으로 관찰</span><br>
<span style="color:#dc2626">! vTaskDelete 전 handle이 NULL이 아닌지 확인하고 삭제 직후 NULL로 설정</span><br>
<br>
<span style="color:#1d4ed8">10. LED Blink Challenge</span><br>
<span style="color:#111827">① Task A: LED blink 수행</span><br>
<span style="color:#111827">② Task B: serial input에서 새 delay 값 수신</span><br>
<span style="color:#111827">③ input 대기 중에도 blink task는 독립적으로 실행</span><br>
<span style="color:#111827">④ 두 task가 공유하는 delay variable의 안전한 갱신을 고려</span><br>
<span style="color:#dc2626">! shared variable 문제는 이후 mutex·semaphore 학습으로 연결</span><br>
<br>
<span style="color:#1d4ed8">11. 핵심 3줄</span><br>
<span style="color:#111827">1) <strong>FreeRTOS scheduler는 ready task 중 가장 높은 priority task를 선택하고 같은 priority는 round-robin으로 실행할 수 있다.</strong></span><br>
<span style="color:#111827">2) <strong>task는 Ready·Running·Blocked·Suspended 상태를 오가며 기다리는 동안 blocked가 되면 CPU를 사용하지 않는다.</strong></span><br>
<span style="color:#111827">3) <strong>task 전환에는 register·program counter·stack을 저장·복원하는 context switching이 필요하고 hardware interrupt는 별도 우선순위로 task보다 먼저 실행된다.</strong></span><br>
<br>
<span style="color:#1d4ed8">Q. Ready와 Running의 차이는?</span><br>
<span style="color:#111827">A. Ready는 실행할 준비가 된 상태이고 Running은 scheduler가 선택해 CPU를 실제로 사용하는 상태다.</span><br>
<span style="color:#1d4ed8">Q. Blocked와 Suspended의 차이는?</span><br>
<span style="color:#111827">A. Blocked는 delay 만료나 event로 ready에 복귀하지만 Suspended는 vTaskResume 같은 명시적 호출이 필요하다.</span><br>
<span style="color:#1d4ed8">Q. 같은 priority task는 어떻게 실행되는가?</span><br>
<span style="color:#111827">A. 둘 다 ready라면 round-robin으로 time slice를 번갈아 받을 수 있다.</span><br>
<span style="color:#1d4ed8">Q. Context switching에서 무엇을 보존하는가?</span><br>
<span style="color:#111827">A. program counter, CPU register, stack과 task working state를 저장해 다음 실행 때 중단 지점부터 이어 간다.</span><br>
<span style="color:#1d4ed8">Q. Task priority와 interrupt priority는 같은가?</span><br>
<span style="color:#111827">A. 서로 다른 우선순위 체계이며 hardware interrupt는 일반 task 실행을 중단하고 ISR을 먼저 수행할 수 있다.</span><br>
<br>
<span style="color:#1d4ed8">12. 30초 면접 답변</span><br>
<span style="color:#111827">RTOS task scheduling은 ready 상태인 task 중 priority와 정책에 따라 다음에 CPU를 사용할 task를 고르는 과정입니다.</span><br>
<span style="color:#111827">FreeRTOS는 tick을 시간 기준으로 사용하며 높은 priority task를 먼저 실행하고, 같은 priority task는 round-robin으로 CPU 시간을 나눌 수 있습니다.</span><br>
<span style="color:#111827">vTaskDelay나 semaphore wait 중인 task는 blocked가 되어 CPU를 쓰지 않고 조건이 풀리면 ready로 돌아옵니다.</span><br>
<span style="color:#dc2626">Task를 바꿀 때는 program counter·register·stack을 저장·복원하는 context switch가 일어나며 hardware interrupt는 task scheduling보다 우선하므로 ISR을 짧게 유지합니다.</span><br>
<br>
<span style="color:#1d4ed8">13. 지금 깊이 조절</span><br>
<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- tick / time slice / scheduler</span><br>
<span style="color:#111827">- priority / round-robin / preemption</span><br>
<span style="color:#111827">- Ready / Running / Blocked / Suspended</span><br>
<span style="color:#111827">- context switching</span><br>
<span style="color:#111827">- task priority와 interrupt priority의 차이</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- vTaskSuspend / vTaskResume / vTaskDelete</span><br>
<span style="color:#111827">- multi-core scheduler와 task affinity</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- scheduler configuration과 tickless idle</span><br>
<span style="color:#111827">- priority inversion·starvation</span><br>
<span style="color:#111827">- ISR에서의 context switch와 FromISR API</span><br>
<span style="color:#dc2626">! 지금은 ready task 선택과 state transition을 timeline으로 설명한다</span><br>
<br>
<span style="color:#1d4ed8">14. 참고 자료</span><br>
<a style="color:#111827" href="../../10_주제별/cs/RTOS/3_태스크_스케줄링.md">Task Scheduling — 원본 학습노트</a><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=95yUbClyf3E">Introduction to RTOS Part 3</a><br>
<a style="color:#111827" href="https://www.freertos.org/Documentation/RTOS_book.html">FreeRTOS Documentation</a><br>
<a style="color:#111827" href="https://www.freertos.org/RTOS-task-states.html">FreeRTOS Task States</a><br>
