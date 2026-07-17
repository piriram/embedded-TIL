<span style="color:#1d4ed8">I. C언어 심화 4 — C 프로그램의 메모리 레이아웃</span><br>
<br>
<span style="color:#1d4ed8">1. 소스 코드가 메모리에 놓이기까지</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>section</strong>: 코드와 데이터를 용도별로 묶어 실행 이미지에 배치한 단위</span><br>
<span style="color:#111827">② <strong>storage duration</strong>: 객체가 메모리에 존재하는 기간</span><br>
<span style="color:#111827">③ <strong>linker</strong>: 여러 object file과 library를 결합해 section의 최종 위치를 정하는 도구</span><br>
<span style="color:#111827">④ <strong>linker script</strong>: MCU의 Flash·SRAM 주소와 section 배치 규칙을 linker에 알려 주는 파일</span><br>
<span style="color:#dc2626">! <strong>변수 이름보다 저장 기간을 먼저 보면 어느 영역에 놓이는지 판단하기 쉬움</strong></span><br>
<br>
<span style="color:#1d4ed8">2) build부터 실행까지</span><br>
<span style="color:#111827">main.c → 컴파일·어셈블 → object file → 링크 → 실행 이미지</span><br>
<span style="color:#111827">실행 이미지 → loader 또는 MCU reset/startup → 실행 중 메모리</span><br>
<span style="color:#111827">① linker가 코드와 전역 데이터를 section으로 묶어 배치</span><br>
<span style="color:#111827">② 함수 호출 시 지역 변수와 호출 정보가 stack에 생김</span><br>
<span style="color:#111827">③ malloc을 호출한 경우에만 heap block이 생김</span><br>
<span style="color:#dc2626">! stack과 heap은 실행 파일의 고정 초기값이 아니라 <strong>실행 중 관리되는 영역</strong></span><br>
<br>
<span style="color:#1d4ed8">3) 메모리 레이아웃은 target별 모델</span><br>
<span style="color:#111827">① PC: 운영체제가 프로세스의 가상 주소 공간에 실행 파일을 mapping</span><br>
<span style="color:#111827">② MCU: linker script가 물리 Flash와 SRAM에 section을 배치</span><br>
<span style="color:#111827">③ 주소 높낮이와 heap·stack 성장 방향은 환경에 따라 달라질 수 있음</span><br>
<span style="color:#dc2626">! .text·.data·.bss·heap·stack의 정확한 주소 배치는 C 표준이 보장하지 않음</span><br>
<span style="color:#dc2626">★ 실제 배치는 <strong>map file·linker script·datasheet</strong>로 확인</span><br>
<br>
<span style="color:#1d4ed8">그림: 일반적인 메모리 레이아웃</span><br>
<span style="color:#111827">낮은 주소</span><br>
<span style="color:#111827">[.text / .rodata : 코드·상수]</span><br>
<span style="color:#111827">[.data : 초기값 있는 전역·static]</span><br>
<span style="color:#111827">[.bss : 초기값 없는 전역·static]</span><br>
<span style="color:#111827">[heap ↑        빈 공간        ↓ stack]</span><br>
<span style="color:#111827">높은 주소</span><br>
<span style="color:#dc2626">! 이 그림은 개념도이며 실제 주소와 성장 방향은 target에서 확인</span><br>
<br>
<span style="color:#1d4ed8">2. 고정 section — .text / .rodata / .data / .bss</span><br>
<span style="color:#1d4ed8">1) .text와 .rodata</span><br>
<span style="color:#111827">① <strong>.text</strong>: CPU가 실행할 기계어 명령어</span><br>
<span style="color:#111827">② <strong>.rodata</strong>: 문자열 literal·읽기 전용 상수 등이 놓일 수 있는 section</span><br>
<span style="color:#111827">③ MCU에서는 보통 Flash에 있고 CPU가 그곳에서 직접 실행·읽기</span><br>
<span style="color:#111827">④ PC에서는 실행 파일을 가상 메모리에 mapping하고 읽기 전용 code page를 공유할 수 있음</span><br>
<span style="color:#111827">ex) int add(int a, int b)의 실행 명령어 → 보통 .text</span><br>
<span style="color:#dc2626">! const 객체의 정확한 section은 toolchain·최적화·attribute에 따라 달라질 수 있음</span><br>
<br>
<span style="color:#1d4ed8">2) .data</span><br>
<span style="color:#111827">① 0이 아닌 초기값을 가진 전역·static 객체가 주로 배치됨</span><br>
<span style="color:#111827">② 프로그램 전체 수명 동안 존재</span><br>
<span style="color:#111827">③ MCU에서는 초기값을 Flash에 보관하고 reset 때 SRAM으로 복사</span><br>
<span style="color:#111827">ex) int configured_speed = 115200;</span><br>
<span style="color:#dc2626">! .data는 <strong>초기값 Flash 공간과 실행 중 SRAM 공간</strong>을 모두 사용할 수 있음</span><br>
<br>
<span style="color:#1d4ed8">3) .bss</span><br>
<span style="color:#111827">① 초기화하지 않았거나 0으로 초기화한 전역·static 객체가 주로 배치됨</span><br>
<span style="color:#111827">② 프로그램 전체 수명 동안 존재하고 startup code가 0으로 채움</span><br>
<span style="color:#111827">③ SRAM 사용량에는 포함되지만 0 초기값 전체를 Flash에 저장할 필요는 없음</span><br>
<span style="color:#111827">ex) static int sample_count; / static int enabled = 0;</span><br>
<span style="color:#dc2626">! <strong>.bss는 메모리를 사용하지 않는 영역이 아님</strong>: 실행 중 SRAM을 차지함</span><br>
<br>
<span style="color:#1d4ed8">4) MCU reset 직후 startup 흐름</span><br>
<span style="color:#111827">Flash의 .data 초기값 → SRAM의 .data로 복사</span><br>
<span style="color:#111827">SRAM의 .bss → 0으로 초기화</span><br>
<span style="color:#111827">초기화 완료 → main() 호출</span><br>
<span style="color:#dc2626">★ <strong>.data 복사 → .bss zero-fill → main 진입</strong> 흐름을 기억</span><br>
<br>
<span style="color:#1d4ed8">3. 실행 중 영역 — stack과 heap</span><br>
<span style="color:#1d4ed8">1) stack</span><br>
<span style="color:#111827">① 함수의 지역 변수·매개변수 전달 정보·복귀 주소 등 호출 상태를 관리</span><br>
<span style="color:#111827">② 함수가 호출되면 frame이 생기고 반환되면 자동으로 사라짐</span><br>
<span style="color:#111827">③ 지역 변수는 최적화와 ABI에 따라 CPU register에 놓일 수도 있음</span><br>
<span style="color:#111827">cf) stack frame = 한 번의 함수 호출에 필요한 상태를 묶은 저장 단위</span><br>
<span style="color:#111827">cf) ABI = 함수 호출·register 사용·데이터 배치 규칙을 정한 약속</span><br>
<span style="color:#dc2626">! 함수가 끝난 뒤 그 함수의 automatic 변수에 접근하면 안 됨</span><br>
<br>
<span style="color:#1d4ed8">2) stack overflow</span><br>
<span style="color:#111827">① 너무 깊은 재귀 호출은 stack frame을 계속 쌓음</span><br>
<span style="color:#111827">② 큰 지역 배열도 한 번에 많은 stack 공간을 사용</span><br>
<span style="color:#111827">③ MCU에서는 인접 RAM 훼손·HardFault·예측 불가능한 오동작으로 이어질 수 있음</span><br>
<span style="color:#dc2626">! 제한된 MCU RAM에서는 함수별 stack 사용량과 최악 호출 깊이를 확인</span><br>
<br>
<span style="color:#1d4ed8">3) heap</span><br>
<span style="color:#111827">① malloc·calloc·realloc이 요청한 동적 block을 제공하는 영역</span><br>
<span style="color:#111827">② block 수명은 함수 호출이 아니라 free할 때까지</span><br>
<span style="color:#111827">③ malloc 실패 시 NULL을 반환하므로 사용 전에 검사</span><br>
<span style="color:#111827">④ 책임을 다한 뒤 정확히 한 번 free</span><br>
<span style="color:#dc2626">! free하지 않으면 memory leak, free 뒤 다시 사용하면 dangling pointer</span><br>
<br>
<span style="color:#1d4ed8">4) 포인터 변수와 가리키는 block은 다른 곳에 있다</span><br>
<span style="color:#111827">void read_packet(void) 안의 unsigned char *packet</span><br>
<span style="color:#111827">① packet 변수 자체 → 함수의 지역 변수이므로 보통 stack</span><br>
<span style="color:#111827">② malloc(64)이 만든 64 byte block → heap</span><br>
<span style="color:#111827">③ packet에 저장된 값 → heap block의 시작 주소</span><br>
<span style="color:#111827">④ 함수가 끝나 packet만 사라져도 free하지 않은 heap block은 남음</span><br>
<span style="color:#dc2626">★ <strong>포인터가 있는 위치와 포인터가 가리키는 데이터의 위치를 분리해서 생각</strong></span><br>
<br>
<span style="color:#1d4ed8">4. 코드에서 저장 위치 추적하기</span><br>
<span style="color:#1d4ed8">1) 저장 기간으로 분류</span><br>
<span style="color:#111827">① 함수 밖 변수·함수 안 static → static storage duration → .data 또는 .bss</span><br>
<span style="color:#111827">② 일반 지역 변수·매개변수 → automatic storage duration → stack 또는 register</span><br>
<span style="color:#111827">③ malloc 반환 포인터가 가리키는 대상 → allocated storage duration → heap</span><br>
<span style="color:#111827">④ 함수 본문의 실행 명령어 → .text</span><br>
<span style="color:#dc2626">! 지역에 선언됐다는 이유만으로 모두 stack은 아님: <strong>함수 안 static은 .data/.bss</strong></span><br>
<br>
<span style="color:#1d4ed8">2) 한 코드 예시</span><br>
<span style="color:#111827">int global_ready = 1; → .data</span><br>
<span style="color:#111827">static int global_errors; → .bss</span><br>
<span style="color:#111827">void process(int input)의 명령어 → .text</span><br>
<span style="color:#111827">int local = input; → stack 또는 register</span><br>
<span style="color:#111827">static int runs = 1; → .data, 함수 반환 뒤에도 유지</span><br>
<span style="color:#111827">int *dynamic = malloc(...); → dynamic은 stack, 가리키는 block은 heap</span><br>
<span style="color:#dc2626">! 선언 위치만 보지 말고 <strong>static 여부·초기값·할당 방식·수명</strong>을 함께 확인</span><br>
<br>
<span style="color:#1d4ed8">5. MCU에서는 Flash와 SRAM 예산으로 본다</span><br>
<span style="color:#1d4ed8">1) 영역별 대표 비용</span><br>
<span style="color:#111827">① .text·.rodata → 대개 Flash</span><br>
<span style="color:#111827">② .data 초기값 → Flash, 실행 중 .data → SRAM</span><br>
<span style="color:#111827">③ .bss·stack·heap → 대개 실행 중 SRAM</span><br>
<span style="color:#111827">④ 정확한 배치는 MCU와 linker script에 따라 확인</span><br>
<span style="color:#dc2626">! .data는 Flash와 SRAM 양쪽 예산에 영향을 줄 수 있다는 점을 놓치지 않기</span><br>
<br>
<span style="color:#1d4ed8">2) build 뒤 점검 순서</span><br>
<span style="color:#111827">① map file에서 section별 시작 주소와 크기 확인</span><br>
<span style="color:#111827">② .text·.rodata·.data 초기값의 Flash 사용량 확인</span><br>
<span style="color:#111827">③ .data·.bss·stack·heap의 SRAM 사용량 확인</span><br>
<span style="color:#111827">④ stack/heap 예약 크기와 남은 SRAM 확인</span><br>
<span style="color:#111827">⑤ 큰 전역 배열·큰 지역 배열·동적 할당의 필요성 재검토</span><br>
<span style="color:#dc2626">★ MCU 메모리는 감으로 판단하지 말고 <strong>map file의 숫자로 검증</strong></span><br>
<br>
<span style="color:#1d4ed8">6. 핵심 3줄</span><br>
<span style="color:#111827">1) <strong>실행 명령어는 .text, 초기값 있는 전역·static은 .data, 초기값 없는 전역·static은 .bss에 주로 놓인다.</strong></span><br>
<span style="color:#111827">2) <strong>지역 변수와 호출 상태는 stack에서 자동 관리되고, malloc으로 얻은 heap block은 free할 때까지 직접 관리한다.</strong></span><br>
<span style="color:#111827">3) <strong>MCU에서는 map file로 각 section의 Flash·SRAM 사용량과 stack·heap 여유를 확인한다.</strong></span><br>
<br>
<span style="color:#1d4ed8">Q. .data와 .bss의 차이는?</span><br>
<span style="color:#111827">A. 둘 다 프로그램 전체 수명의 전역·static 객체를 담지만, .data는 초기값 이미지가 필요하고 .bss는 startup 때 0으로 채운다.</span><br>
<span style="color:#1d4ed8">Q. 함수 안에 선언한 static 변수는 왜 stack이 아닌가?</span><br>
<span style="color:#111827">A. 선언 위치와 관계없이 static storage duration을 가져 프로그램 전체 실행 동안 유지되기 때문이다.</span><br>
<span style="color:#1d4ed8">Q. 지역 포인터와 malloc block은 어디에 있는가?</span><br>
<span style="color:#111827">A. 지역 포인터 변수 자체는 보통 stack에 있고, 포인터가 가리키는 동적 block은 heap에 있다.</span><br>
<span style="color:#1d4ed8">Q. .bss가 실행 이미지에서 작아 보여도 SRAM을 사용하는 이유는?</span><br>
<span style="color:#111827">A. 0 초기값을 Flash에 모두 저장하지 않을 뿐, linker가 SRAM에 배치한 공간을 startup code가 실행 시 0으로 채우기 때문이다.</span><br>
<span style="color:#1d4ed8">Q. 실제 section 위치와 크기는 무엇으로 확인하는가?</span><br>
<span style="color:#111827">A. build 결과의 map file과 linker script를 확인하고 MCU의 datasheet 주소 범위와 대조한다.</span><br>
<br>
<span style="color:#1d4ed8">7. 30초 면접 답변</span><br>
<span style="color:#111827">C 프로그램의 메모리 레이아웃은 저장 기간과 용도에 따라 코드와 데이터를 나누는 모델입니다.</span><br>
<span style="color:#111827">실행 명령어는 보통 .text, 초기값 있는 전역·static 변수는 .data, 초기값 없는 전역·static 변수는 .bss에 들어갑니다.</span><br>
<span style="color:#111827">지역 변수와 함수 복귀 정보는 stack에 생겨 함수가 끝나면 사라지지만, malloc으로 얻은 heap block은 free할 때까지 남습니다.</span><br>
<span style="color:#dc2626">MCU에서는 map file로 이 영역들의 Flash·SRAM 사용량과 stack·heap 여유를 확인합니다.</span><br>
<br>
<span style="color:#1d4ed8">8. 지금 깊이 조절</span><br>
<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- .text / .data / .bss / stack / heap의 역할</span><br>
<span style="color:#111827">- static·automatic·allocated storage duration</span><br>
<span style="color:#111827">- 지역 포인터와 heap block의 위치 차이</span><br>
<span style="color:#111827">- .data 복사 → .bss zero-fill → main 흐름</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- .rodata, ABI, stack frame</span><br>
<span style="color:#111827">- map file, linker script</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- custom section attribute와 startup code</span><br>
<span style="color:#111827">- ELF section·symbol·relocation 구조</span><br>
<span style="color:#111827">- MPU·가상 메모리·target별 stack overflow 검출</span><br>
<span style="color:#dc2626">! 지금은 저장 기간으로 영역을 구분하고 Flash·SRAM 비용까지 연결한다</span><br>
<br>
<span style="color:#1d4ed8">9. 참고 자료</span><br>
<a style="color:#111827" href="../../10_주제별/c언어/020_C_프로그램_메모리_레이아웃.md">C 프로그램의 메모리 레이아웃 — 원본 학습노트</a><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=FlkNgJXEyrc">The Memory Layout of a C Program</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/070_전역변수와_static.md">전역 변수와 static 변수</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/030_sizeof와_포인터_메모리_크기.md">sizeof와 포인터 메모리 크기</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/100_실시간_시스템에서_malloc_사용_원칙.md">실시간 시스템에서 malloc 사용 원칙</a><br>
<a style="color:#111827" href="../../10_주제별/cs/임베디드수업/8_MCU_메모리맵과_MMIO.md">MCU Memory Map과 MMIO</a><br>
