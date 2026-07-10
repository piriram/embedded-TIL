# Ch.04 RTOS 기초

용도: A4 세로 반 접기 2열 손필기

규칙:

- 1열 32줄 기준
- 내용이 길면 다음 페이지로 넘김
- 들여쓰기 없음
- 파랑: 제목, 번호, 핵심 키워드
- 검정: 설명, 예시, cf
- 빨강: 면접 주의, 헷갈리는 점
- 손그림과 이미지 링크는 관련 개념 바로 아래에 배치

## 1페이지: RTOS가 왜 필요한가

<span style="color:#1d4ed8">주제: RTOS 기초</span><br>
<span style="color:#1d4ed8">1. RTOS(Real-Time Operating System)</span><br>
<span style="color:#111827">a. 여러 작업을 task로 나눠 실행하게 도와주는 운영체제</span><br>
<span style="color:#111827">b. scheduler가 어떤 task를 실행할지 결정함</span><br>
<span style="color:#111827">c. queue, semaphore, mutex 같은 통신/동기화 도구를 제공함</span><br>
<span style="color:#111827">- 예: 센서 읽기, 통신 송신, 로그 출력을 task로 분리</span><br>
<span style="color:#dc2626">※ RTOS를 쓴다고 자동으로 실시간성이 보장되는 것은 아님</span><br>
<span style="color:#111827">RTOS는 task를 나누고 scheduler가 실행 순서를 정하게 해줌</span><br>
<span style="color:#111827">하지만 deadline 안에 반드시 끝나는지는 별도로 설계해야 함</span><br>
<span style="color:#111827">- 중요한 task의 priority가 낮으면 늦게 실행될 수 있음</span><br>
<span style="color:#111827">- ISR이나 높은 priority task가 오래 CPU를 잡으면 밀릴 수 있음</span><br>
<span style="color:#111827">- mutex, queue, semaphore 대기 때문에 막힐 수 있음</span><br>
<span style="color:#111827">- task 실행 시간이 deadline보다 길면 RTOS여도 실패함</span><br>
<span style="color:#dc2626">※ 실시간성 = RTOS 사용 여부가 아니라 시간 제약을 만족하도록 설계/검증한 결과</span><br>
<br>
<span style="color:#1d4ed8">2. Bare-metal과 RTOS 차이</span><br>
<span style="color:#111827">a. Bare-metal: main loop와 interrupt 중심으로 직접 흐름 관리</span><br>
<span style="color:#111827">b. RTOS: task 단위로 작업을 나누고 scheduler가 실행 순서 관리</span><br>
<span style="color:#111827">c. 기능이 많아질수록 RTOS가 구조를 나누기 쉬움</span><br>
<span style="color:#111827">cf) 단순 LED, 버튼 제어는 bare-metal이 더 단순할 수 있음</span><br>
<span style="color:#dc2626">※ RTOS는 편한 라이브러리가 아니라 실행 구조를 바꾸는 선택</span><br>
<br>
<span style="color:#1d4ed8">그림: Bare-metal vs RTOS</span><br>
<span style="color:#111827">Bare-metal: while(1) 안에서 센서/통신/로그 순서대로 처리</span><br>
<span style="color:#111827">RTOS: SensorTask / CommTask / LogTask로 분리</span><br>
<span style="color:#111827">Scheduler가 우선순위와 상태를 보고 실행</span><br>
<span style="color:#dc2626">※ task 분리는 좋지만 stack/context switch 비용이 생김</span><br>
<br>
<span style="color:#1d4ed8">3. Task</span><br>
<span style="color:#111827">a. RTOS에서 독립적으로 실행되는 작업 단위</span><br>
<span style="color:#111827">b. 각 task는 자기 stack과 우선순위를 가짐</span><br>
<span style="color:#111827">c. delay, queue, semaphore 대기 때문에 실행이 멈출 수 있음</span><br>
<span style="color:#111827">- 예: SensorTask는 10ms마다 센서 값을 읽음</span><br>
<span style="color:#dc2626">※ task를 많이 만들면 stack 메모리 사용도 늘어남</span><br>

## 2페이지: Scheduler와 task 상태

<span style="color:#1d4ed8">4. Scheduler</span><br>
<span style="color:#111827">a. 실행 가능한 task 중 어떤 task를 CPU에 올릴지 정함</span><br>
<span style="color:#111827">b. 보통 priority가 높은 ready task가 먼저 실행됨</span><br>
<span style="color:#111827">c. tick interrupt나 이벤트 발생 때 task 전환이 일어날 수 있음</span><br>
<span style="color:#111827">Tick interrupt = RTOS가 일정 주기로 받는 시간 알림</span><br>
<span style="color:#111827">delay 시간 감소, timeout 확인, task 전환 판단에 사용</span><br>
<span style="color:#111827">- 예: vTaskDelay(10)은 tick 10번 뒤 Ready</span><br>
<span style="color:#dc2626">※ tick은 RTOS의 주기적 시간 기준</span><br>
<span style="color:#111827">cf) priority = 작업의 중요도/우선순위</span><br>
<span style="color:#dc2626">※ 우선순위를 잘못 잡으면 중요한 작업이 늦어질 수 있음</span><br>
<br>
<span style="color:#1d4ed8">5. Task 상태</span><br>
<span style="color:#111827">a. Running: 지금 CPU에서 실행 중</span><br>
<span style="color:#111827">b. Ready: 실행 가능하지만 순서를 기다림</span><br>
<span style="color:#111827">c. Blocked: delay, queue, semaphore 같은 이벤트를 기다림</span><br>
<span style="color:#111827">d. Suspended: 스케줄 대상에서 제외됨</span><br>
<span style="color:#111827">Ready task = 바로 실행 가능하지만 아직 CPU를 못 받은 task</span><br>
<span style="color:#111827">priority가 높아도 Blocked 상태면 실행 대상이 아님</span><br>
<span style="color:#dc2626">※ blocked는 멈춘 것이 아니라 조건을 기다리는 상태</span><br>
<br>
<span style="color:#1d4ed8">그림: Task 상태 전이도</span><br>
<span style="color:#111827">Ready → Running: scheduler가 CPU에 올림</span><br>
<span style="color:#111827">Running → Ready: 더 높은 priority task 등장 또는 time slice 종료</span><br>
<span style="color:#111827">Running → Blocked: delay, queue, semaphore 대기 시작</span><br>
<span style="color:#111827">Blocked → Ready: 시간 만료 또는 이벤트 발생</span><br>
<span style="color:#111827">Ready/Blocked → Suspended: task를 명시적으로 중지</span><br>
<span style="color:#111827">Suspended → Ready: task를 다시 resume</span><br>
<span style="color:#dc2626">※ 상태 전이도는 task가 왜 실행/대기/재실행되는지 설명하는 그림</span><br>
<img src="./assets/filginote_04/task_state_wikimedia.png" width="520" alt="FreeRTOS Task 상태 전이도"><br>
<span style="color:#111827">출처: Wikimedia Commons, File: Task state.png</span><br>
<span style="color:#111827">라이선스: GNU GPL v2 or later</span><br>
<br>
<span style="color:#1d4ed8">6. Queue</span><br>
<span style="color:#111827">a. task 사이에 데이터를 전달하는 통로</span><br>
<span style="color:#111827">b. 보내는 쪽은 데이터를 넣고, 받는 쪽은 데이터를 꺼냄</span><br>
<span style="color:#111827">c. ISR에서 task로 이벤트나 데이터를 넘길 때도 자주 사용</span><br>
<span style="color:#111827">- 예: UART 수신 ISR → Queue → ParserTask</span><br>
<span style="color:#dc2626">※ 데이터 자체를 보내면 queue, 단순 깨우기면 semaphore/notification 고려</span><br>

## 3페이지: Semaphore와 Mutex

<span style="color:#1d4ed8">7. Semaphore</span><br>
<span style="color:#111827">a. 이벤트 발생이나 자원 개수를 알려주는 동기화 도구</span><br>
<span style="color:#111827">b. task가 semaphore를 기다리다가 신호가 오면 깨어날 수 있음</span><br>
<span style="color:#111827">c. binary semaphore는 0 또는 1 상태로 이벤트 신호에 많이 씀</span><br>
<span style="color:#111827">- 예: 버튼 interrupt 발생 → semaphore give → ButtonTask wake</span><br>
<span style="color:#dc2626">※ binary semaphore는 mutex와 모양이 비슷해도 목적이 다름</span><br>
<br>
<span style="color:#1d4ed8">8. Counting Semaphore</span><br>
<span style="color:#111827">a. 여러 개의 같은 자원 개수를 count로 관리함</span><br>
<span style="color:#111827">b. count가 남아 있으면 task가 자원을 사용할 수 있음</span><br>
<span style="color:#111827">c. buffer slot, resource pool 같은 곳에 사용 가능</span><br>
<span style="color:#111827">cf) count = 사용 가능한 개수</span><br>
<span style="color:#dc2626">※ 공유 변수 보호용이면 counting semaphore보다 mutex를 먼저 생각</span><br>
<br>
<span style="color:#1d4ed8">9. Mutex(Mutual Exclusion)</span><br>
<span style="color:#111827">a. 공유 자원을 한 번에 하나의 task만 쓰게 보호하는 lock</span><br>
<span style="color:#111827">b. lock을 잡은 task가 작업 후 unlock해야 다른 task가 사용 가능</span><br>
<span style="color:#111827">c. UART 출력, I2C 버스, 공유 변수 보호에 사용</span><br>
<span style="color:#111827">cf) mutual exclusion = 상호 배제, 동시에 못 들어가게 막는 것</span><br>
<span style="color:#dc2626">※ mutex는 owner 개념이 있어서 잡은 task가 풀어야 함</span><br>
<br>
<span style="color:#1d4ed8">그림: Mutex로 공유 자원 보호</span><br>
<span style="color:#111827">Task A lock → UART 사용 → unlock</span><br>
<span style="color:#111827">Task B는 unlock 전까지 대기</span><br>
<span style="color:#dc2626">※ lock 구간은 짧게 유지해야 지연이 줄어듦</span><br>

## 4페이지: 면접 핵심 비교

<span style="color:#1d4ed8">10. Mutex vs Binary Semaphore</span><br>
<span style="color:#111827">a. Binary semaphore: 이벤트 신호에 적합</span><br>
<span style="color:#111827">b. Mutex: 공유 자원 보호에 적합</span><br>
<span style="color:#111827">c. Mutex는 owner 개념과 priority inheritance가 있음</span><br>
<span style="color:#111827">d. Binary semaphore는 보통 priority inheritance가 없음</span><br>
<span style="color:#dc2626">※ 0/1이라 같다고 말하면 면접에서 위험함</span><br>
<br>
<span style="color:#1d4ed8">11. Priority Inversion</span><br>
<span style="color:#111827">a. 낮은 priority task가 mutex를 잡고 있음</span><br>
<span style="color:#111827">b. 높은 priority task가 같은 mutex를 기다림</span><br>
<span style="color:#111827">c. 중간 priority task가 CPU를 써서 낮은 task가 mutex를 못 놓음</span><br>
<span style="color:#111827">d. 결과적으로 높은 priority task가 오래 밀림</span><br>
<span style="color:#dc2626">※ priority inheritance는 이 문제를 줄이기 위한 장치</span><br>
<br>
<span style="color:#1d4ed8">12. ISR에서 주의</span><br>
<span style="color:#111827">a. ISR에서는 오래 걸리는 작업과 blocking을 피함</span><br>
<span style="color:#111827">b. ISR에서 mutex를 잡고 기다리는 구조는 부적절함</span><br>
<span style="color:#111827">c. ISR은 queue/semaphore/notification으로 task를 깨우고 빠져나옴</span><br>
<span style="color:#111827">cf) FromISR 계열 API는 interrupt context용 API</span><br>
<span style="color:#dc2626">※ ISR은 직접 처리보다 task에 넘기는 구조를 우선 생각</span><br>

## 면접 30초 답변

<span style="color:#1d4ed8">RTOS 기초 설명</span><br>
<span style="color:#111827">RTOS는 여러 기능을 task로 나누고 scheduler가 priority와 상태를 보고 실행 순서를 관리하게 해주는 운영체제입니다.</span><br>
<span style="color:#111827">다만 실시간성은 RTOS 사용만으로 보장되지 않고, priority, task 실행 시간, interrupt 지연, 공유 자원 대기 시간을 설계하고 검증해야 합니다.</span><br>
<span style="color:#111827">Task는 running, ready, blocked 같은 상태를 오가며, queue는 task 사이에 데이터를 전달할 때 사용합니다.</span><br>
<span style="color:#111827">Semaphore는 이벤트 신호나 자원 개수를 표현하는 데 쓰고, mutex는 UART나 I2C 같은 공유 자원을 한 번에 하나의 task만 쓰게 보호할 때 사용합니다.</span><br>
<span style="color:#dc2626">특히 mutex는 owner와 priority inheritance가 있고, binary semaphore는 주로 signaling 용도라 둘을 같은 것으로 보면 안 됩니다.</span><br>

## 지금 깊이 조절

<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- RTOS는 task와 scheduler 구조</span><br>
<span style="color:#111827">- ready / running / blocked 차이</span><br>
<span style="color:#111827">- queue는 데이터 전달</span><br>
<span style="color:#111827">- semaphore는 이벤트 신호 또는 자원 개수</span><br>
<span style="color:#111827">- mutex는 공유 자원 보호</span><br>
<span style="color:#111827">- tick interrupt는 RTOS의 주기적 시간 기준</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- direct task notification</span><br>
<span style="color:#111827">- context switch</span><br>
<span style="color:#111827">- stack overflow hook</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- FreeRTOS API 코드</span><br>
<span style="color:#111827">- ISR-safe API</span><br>
<span style="color:#111827">- priority inversion 실험</span><br>
<span style="color:#111827">- stack size 계산과 디버깅</span><br>
<span style="color:#dc2626">※ 지금은 용도 구분과 면접용 한 줄 설명을 먼저 잡는다</span><br>

## Q. 꼬리질문

<span style="color:#1d4ed8">Q. 면접에서 이어질 수 있는 질문</span><br>
<span style="color:#111827">- RTOS를 쓰면 bare-metal보다 항상 좋은가?</span><br>
<span style="color:#111827">- task 상태에는 무엇이 있는가?</span><br>
<span style="color:#111827">- queue와 semaphore는 언제 다르게 쓰는가?</span><br>
<span style="color:#111827">- mutex와 binary semaphore는 어떻게 다른가?</span><br>
<span style="color:#111827">- priority inversion은 무엇이고 어떻게 줄이는가?</span><br>
<span style="color:#111827">- ISR에서 mutex를 쓰면 왜 위험한가?</span><br>
