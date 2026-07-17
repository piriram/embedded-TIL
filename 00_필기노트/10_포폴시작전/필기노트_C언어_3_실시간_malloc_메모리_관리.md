<span style="color:#1d4ed8">I. C언어 심화 3 — 실시간 시스템의 malloc과 메모리 관리</span><br>
<br>
<span style="color:#1d4ed8">1. malloc을 실시간 코드에서 조심하는 이유</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>heap</strong>: 실행 중 필요한 크기의 메모리를 빌려 쓰는 영역</span><br>
<span style="color:#111827">② <strong>malloc(size)</strong>: heap에서 연속된 size byte block을 찾아 시작 주소를 반환하는 함수</span><br>
<span style="color:#111827">③ <strong>real-time</strong>: 단순히 빠른 것이 아니라 정해진 시간 안에 끝남을 보장해야 하는 시스템 성질</span><br>
<span style="color:#111827">④ <strong>determinism</strong>: 같은 조건에서 실행 시간과 결과의 상한을 예측할 수 있는 성질</span><br>
<span style="color:#dc2626">! <strong>실시간 시스템의 핵심은 평균 속도가 아니라 최악 실행 시간의 예측 가능성</strong></span><br>
<br>
<span style="color:#1d4ed8">2) malloc의 기본 동작</span><br>
<span style="color:#111827">① 요청한 크기를 담을 수 있는 연속 block을 heap에서 탐색</span><br>
<span style="color:#111827">② 성공 → block 시작 주소 반환</span><br>
<span style="color:#111827">③ 실패 → NULL 반환</span><br>
<span style="color:#111827">④ allocator는 free block 탐색·metadata 갱신·동기화를 수행할 수 있음</span><br>
<span style="color:#111827">cf) allocator = heap의 빈 공간을 찾아 나눠 주고 회수하는 메모리 관리자</span><br>
<span style="color:#dc2626">! malloc은 <strong>실행 시간·반환 주소·장시간 뒤의 성공 여부</strong>를 deadline에 맞춰 보장하지 않음</span><br>
<br>
<span style="color:#1d4ed8">3) 정확한 사용 원칙</span><br>
<span style="color:#111827">① “절대 사용 금지”가 아니라 <strong>실시간 경로에서 무심코 사용하지 않기</strong></span><br>
<span style="color:#111827">② 필요하면 할당 시점·최대 사용량·실패 처리·실행 시간을 통제</span><br>
<span style="color:#111827">③ 초기화 때 필요한 메모리를 확보하고 운용 중 추가 할당을 피하는 방식이 안전</span><br>
<span style="color:#dc2626">★ <strong>malloc 자체보다 메모리 수명과 실패 정책이 설계되지 않은 것이 더 큰 문제</strong></span><br>
<br>
<span style="color:#1d4ed8">2. 장시간 실행에서 생기는 위험</span><br>
<span style="color:#1d4ed8">1) memory leak</span><br>
<span style="color:#111827">① 할당한 block의 마지막 소유자가 free하지 않아 다시 쓸 수 없는 상태</span><br>
<span style="color:#111827">② 짧은 테스트에서는 안 보이다가 장시간 뒤 heap 소진으로 나타남</span><br>
<span style="color:#111827">③ task·함수·queue 사이에서 소유권이 이동하면 해제 주체를 API 계약에 기록</span><br>
<span style="color:#dc2626">! 정상·오류·취소 경로 모두에서 <strong>누가 정확히 한 번 free하는지</strong> 정해야 함</span><br>
<br>
<span style="color:#1d4ed8">2) fragmentation</span><br>
<span style="color:#111827">① 서로 다른 크기의 block을 반복해서 할당·해제하면 빈 공간이 작은 조각으로 흩어짐</span><br>
<span style="color:#111827">② 전체 free RAM 합이 충분해도 큰 연속 block이 없으면 malloc은 NULL 반환</span><br>
<span style="color:#111827">③ 모든 block을 free해도 배치에 따라 fragmentation은 생길 수 있음</span><br>
<span style="color:#111827">cf) leak = 메모리를 돌려주지 않음 / fragmentation = 돌려준 공간이 잘게 흩어짐</span><br>
<span style="color:#dc2626">! <strong>leak을 고쳤다고 fragmentation 위험까지 사라지는 것은 아님</strong></span><br>
<br>
<span style="color:#1d4ed8">그림: fragmentation으로 연속 공간이 부족해지는 모습</span><br>
<span style="color:#111827">처음  [사용 32][사용 64][사용 32]</span><br>
<span style="color:#111827">해제  [사용 32][빈칸 64][사용 32]</span><br>
<span style="color:#111827">요청  80 byte → 전체 여유가 있어도 연속 80 byte가 없어 실패</span><br>
<span style="color:#dc2626">! 빈칸의 총합보다 <strong>요청 크기의 연속 block 존재 여부</strong>를 봐야 함</span><br>
<br>
<span style="color:#1d4ed8">3) 비결정적 실행 시간</span><br>
<span style="color:#111827">① heap 상태에 따라 적합한 free block을 찾는 시간이 달라짐</span><br>
<span style="color:#111827">② multi-thread 환경의 내부 lock과 cache miss도 지연을 늘릴 수 있음</span><br>
<span style="color:#111827">③ 할당 시간이 deadline 예산에 들어오는지 상한을 증명하기 어려움</span><br>
<span style="color:#dc2626">! ISR과 주기 제어 loop에서는 짧은 평균 시간이 아니라 <strong>최악 지연</strong>이 문제</span><br>
<br>
<span style="color:#1d4ed8">3. 어디에서 피하고 어디에서 허용할까</span><br>
<span style="color:#1d4ed8">1) 피해야 할 경로</span><br>
<span style="color:#111827">① ISR: 지연 상한과 allocator의 interrupt safety를 보장하기 어려움</span><br>
<span style="color:#111827">② 주기 제어 loop: 할당 지연이 deadline을 깨뜨릴 수 있음</span><br>
<span style="color:#111827">③ hard deadline 경로: NULL 반환이 핵심 기능 중단으로 이어질 수 있음</span><br>
<span style="color:#dc2626">★ <strong>ISR·control loop·hard deadline 경로에서는 일반 malloc을 사용하지 않는 것이 기본</strong></span><br>
<br>
<span style="color:#1d4ed8">2) 조건부 허용 경로</span><br>
<span style="color:#111827">① 시스템 초기화: 운용 전 한 번만 할당하고 최대량·실패를 검증</span><br>
<span style="color:#111827">② non-real-time task: heap budget·최대 block·동시성·실패 정책을 명시</span><br>
<span style="color:#111827">③ 초기화 완료 뒤 추가 malloc/free를 막으면 runtime fragmentation 위험 감소</span><br>
<span style="color:#dc2626">! 초기화 단계라도 RAM 예산과 초기화 실패 시 safe state는 필요</span><br>
<br>
<span style="color:#1d4ed8">4. 통제 가능한 대안</span><br>
<span style="color:#1d4ed8">1) static allocation</span><br>
<span style="color:#111827">① 크기와 개수가 고정이면 배열을 미리 확보</span><br>
<span style="color:#111827">② 메모리 사용량과 주소를 build 시점에 예측 가능</span><br>
<span style="color:#111827">③ 실제 사용량보다 크게 예약하면 RAM 낭비, 큰 요청에는 유연하지 않음</span><br>
<span style="color:#111827">ex) static uint8_t rx_buffers[4][128];</span><br>
<br>
<span style="color:#1d4ed8">2) fixed-size memory pool</span><br>
<span style="color:#111827">① 같은 크기의 message·packet·event용 block을 정해진 개수만 준비</span><br>
<span style="color:#111827">② 할당은 빈 block 하나 꺼내기, 해제는 다시 반납하기</span><br>
<span style="color:#111827">③ 일반 heap보다 실행 시간 상한과 fragmentation을 관리하기 쉬움</span><br>
<span style="color:#111827">④ pool 고갈 시 drop·back-pressure·재시도·safe state 중 정책 선택</span><br>
<span style="color:#111827">cf) back-pressure = 처리할 여유가 생길 때까지 생산·수신 속도를 늦추는 정책</span><br>
<span style="color:#dc2626">! block 크기·총 개수·최악 동시 사용량·동시 접근 보호를 함께 설계</span><br>
<br>
<span style="color:#1d4ed8">3) arena / startup-only allocation</span><br>
<span style="color:#111827">① 큰 고정 buffer 앞쪽부터 필요한 만큼 순서대로 사용</span><br>
<span style="color:#111827">② 개별 free 없이 reset·subsystem 재초기화 때 전체를 한 번에 반환</span><br>
<span style="color:#111827">③ 개별 객체 수명이 제각각이면 arena가 맞지 않음</span><br>
<span style="color:#dc2626">! <strong>수명이 비슷한 객체 묶음</strong>에 적합하고 runtime fragmentation을 만들지 않음</span><br>
<br>
<span style="color:#1d4ed8">5. FreeRTOS와 코드 리뷰</span><br>
<span style="color:#1d4ed8">1) FreeRTOS에서 확인할 것</span><br>
<span style="color:#111827">① task·queue·semaphore 같은 kernel object도 heap을 사용할 수 있음</span><br>
<span style="color:#111827">② heap_1~heap_5는 free 가능 여부와 fragmentation 처리 방식이 다름</span><br>
<span style="color:#111827">③ 일반 malloc/free와 RTOS allocation API 중 사용할 체계를 정함</span><br>
<span style="color:#111827">④ 반환값·task stack 여유·전체 free heap·high-water mark를 측정</span><br>
<span style="color:#111827">cf) high-water mark = 실행 중 가장 많이 사용했을 때 남은 최소 여유량</span><br>
<span style="color:#dc2626">! critical application은 dynamic allocation을 금지하거나 초기화·고정 pool로 제한</span><br>
<br>
<span style="color:#1d4ed8">2) 코드 리뷰 순서</span><br>
<span style="color:#111827">① malloc/calloc/realloc/free가 ISR·callback·deadline 경로에 있는가?</span><br>
<span style="color:#111827">② 모든 allocation failure에 NULL 검사와 안전 대응이 있는가?</span><br>
<span style="color:#111827">③ 정상·오류·취소 경로의 소유권과 정확히 한 번의 free가 명확한가?</span><br>
<span style="color:#111827">④ block 크기 × 최악 동시 개수로 heap budget을 계산했는가?</span><br>
<span style="color:#111827">⑤ soak test로 leak·fragmentation·high-water mark를 관찰했는가?</span><br>
<span style="color:#111827">⑥ static allocation·memory pool로 바꿀 수 있는가?</span><br>
<span style="color:#111827">cf) soak test = 장시간 연속 실행으로 누수·자원 고갈·누적 오류를 찾는 시험</span><br>
<span style="color:#dc2626">! malloc 호출 유무만 보지 말고 <strong>최악 사용량·수명·실패 뒤 동작</strong>을 검토</span><br>
<br>
<span style="color:#1d4ed8">6. 핵심 3줄</span><br>
<span style="color:#111827">1) <strong>실시간 시스템은 평균 속도보다 최악 실행 시간의 예측 가능성이 중요하므로 ISR과 deadline 경로에서 일반 malloc을 피한다.</strong></span><br>
<span style="color:#111827">2) <strong>동적 할당은 leak·fragmentation·NULL 반환을 고려해 최대량, 소유권, 정확히 한 번의 free, 실패 정책을 설계한다.</strong></span><br>
<span style="color:#111827">3) <strong>운용 중에는 static allocation·fixed-size pool·arena를 사용해 시간과 메모리 사용량을 통제한다.</strong></span><br>
<br>
<span style="color:#1d4ed8">Q. 실시간 시스템에서 malloc을 피하는 핵심 이유는?</span><br>
<span style="color:#111827">A. heap 상태에 따라 할당 시간과 성공 여부가 달라져 deadline과 장시간 안정성을 예측하기 어렵기 때문이다.</span><br>
<span style="color:#1d4ed8">Q. free RAM 합이 충분한데 malloc이 실패할 수 있는 이유는?</span><br>
<span style="color:#111827">A. fragmentation으로 빈 공간이 흩어져 요청 크기의 연속 block이 없을 수 있기 때문이다.</span><br>
<span style="color:#1d4ed8">Q. memory pool이 일반 heap보다 실시간 시스템에 유리한 이유는?</span><br>
<span style="color:#111827">A. block 크기와 개수가 고정되어 fragmentation을 줄이고 할당·반납 시간의 상한과 최대 메모리 사용량을 관리하기 쉽기 때문이다.</span><br>
<span style="color:#1d4ed8">Q. 초기화 단계에서는 malloc을 사용할 수 있는가?</span><br>
<span style="color:#111827">A. 최대 사용량과 실패 처리를 검증하고 운용 중 추가 할당·해제를 하지 않는 조건이라면 제한적으로 사용할 수 있다.</span><br>
<br>
<span style="color:#1d4ed8">7. 30초 면접 답변</span><br>
<span style="color:#111827">실시간 시스템에서 malloc을 무조건 금지한다기보다 운용 중 동적 할당을 통제해야 합니다.</span><br>
<span style="color:#111827">일반 heap은 누수와 fragmentation으로 장시간 뒤 NULL을 반환할 수 있고, 적합한 block을 찾는 시간도 일정하지 않아 ISR이나 주기 제어 loop에 부적절합니다.</span><br>
<span style="color:#111827">그래서 필요한 buffer는 초기화 때 미리 확보하거나 static array와 fixed-size memory pool을 사용합니다.</span><br>
<span style="color:#dc2626">꼭 동적 할당한다면 최대 사용량, NULL 처리, 소유권과 정확히 한 번의 free, 장시간 soak test까지 설계합니다.</span><br>
<br>
<span style="color:#1d4ed8">8. 지금 깊이 조절</span><br>
<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- real-time = 빠름이 아니라 deadline 안에 끝남</span><br>
<span style="color:#111827">- leak과 fragmentation의 차이</span><br>
<span style="color:#111827">- ISR·control loop에서 malloc을 피하는 이유</span><br>
<span style="color:#111827">- static allocation과 fixed-size memory pool</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- arena, startup-only allocation</span><br>
<span style="color:#111827">- FreeRTOS heap_1~heap_5, high-water mark</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- allocator의 worst-case execution time 측정</span><br>
<span style="color:#111827">- cache-aware custom allocator와 동시성 검증</span><br>
<span style="color:#111827">- target별 FreeRTOS heap scheme 선택과 정적 생성 API</span><br>
<span style="color:#dc2626">! 지금은 deadline 경로 회피·소유권·최대량·실패 정책을 먼저 잡는다</span><br>
<br>
<span style="color:#1d4ed8">9. 참고 자료</span><br>
<a style="color:#111827" href="../../10_주제별/c언어/100_실시간_시스템에서_malloc_사용_원칙.md">실시간 시스템에서 malloc 사용 원칙 — 원본 학습노트</a><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=0DXU6pYKkEk">Why you Should NEVER Use Malloc in Real-Time Systems</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/020_C_프로그램_메모리_레이아웃.md">C 프로그램의 메모리 레이아웃</a><br>
<a style="color:#111827" href="../../10_주제별/cs/RTOS/4_메모리_관리.md">RTOS 메모리 관리</a><br>
