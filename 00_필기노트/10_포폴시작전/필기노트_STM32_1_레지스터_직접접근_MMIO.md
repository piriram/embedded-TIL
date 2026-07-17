<span style="color:#1d4ed8">I. STM32 실전 1 — 레지스터 직접 접근과 MMIO</span><br>
<br>
<span style="color:#1d4ed8">1. 주소로 주변장치를 제어한다</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>Memory Map</strong>: MCU 주소 공간의 어디에 무엇이 있는지 정한 주소 지도</span><br>
<span style="color:#111827">② <strong>MMIO(Memory-Mapped I/O)</strong>: 주변장치 레지스터를 메모리 주소에 배치해 읽고 쓰는 방식</span><br>
<span style="color:#111827">③ <strong>Peripheral</strong>: GPIO·UART·Timer처럼 CPU 밖에서 입출력 기능을 담당하는 주변장치</span><br>
<span style="color:#111827">④ <strong>register</strong>: 주변장치의 설정값·상태값을 담는 하드웨어 저장 공간</span><br>
<span style="color:#dc2626">★ <strong>STM32 하드웨어 제어는 결국 특정 주소의 레지스터를 읽고 쓰는 일</strong></span><br>
<br>
<span style="color:#1d4ed8">2) STM32F767 주소 공간</span><br>
<span style="color:#111827">① 전체 주소 공간: 0x0000_0000 ~ 0xFFFF_FFFF</span><br>
<span style="color:#111827">② Peripheral 영역 시작: 0x4000_0000</span><br>
<span style="color:#111827">③ Peripheral 영역은 APB1·APB2·AHB 버스별 주소 구역으로 나뉨</span><br>
<span style="color:#111827">④ 각 주변장치는 자신에게 할당된 주소의 register block을 가짐</span><br>
<span style="color:#111827">cf) APB/AHB = CPU와 주변장치·메모리를 연결하는 MCU 내부 bus</span><br>
<span style="color:#dc2626">! 주소값은 MCU마다 다르므로 <strong>대상 MCU의 reference manual</strong>로 확인</span><br>
<br>
<span style="color:#1d4ed8">그림: 레지스터 직접 접근 흐름</span><br>
<span style="color:#111827">C 코드</span><br>
<span style="color:#111827">→ Memory Map에서 Peripheral 주소 확인</span><br>
<span style="color:#111827">→ base + offset으로 register 주소 계산</span><br>
<span style="color:#111827">→ pointer cast + dereference</span><br>
<span style="color:#111827">→ register bit 변경</span><br>
<span style="color:#111827">→ GPIO 등 실제 하드웨어 동작</span><br>
<span style="color:#dc2626">! <strong>주소 찾기 → 값 접근 → bit 변경</strong> 순서로 이해</span><br>
<br>
<span style="color:#1d4ed8">2. base address와 offset으로 주소를 계산한다</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>base address</strong>: 한 주변장치 register block이 시작하는 주소</span><br>
<span style="color:#111827">② <strong>offset</strong>: base address에서 특정 register까지 떨어진 byte 거리</span><br>
<span style="color:#111827">③ <strong>register address</strong>: base address + offset</span><br>
<span style="color:#dc2626">★ <strong>레지스터 실제 주소 = 주변장치 base address + register offset</strong></span><br>
<br>
<span style="color:#1d4ed8">2) STM32F767 GPIOD와 RCC</span><br>
<span style="color:#111827">① GPIOD_BASE = 0x40020C00</span><br>
<span style="color:#111827">② RCC_BASE = 0x40023800</span><br>
<span style="color:#111827">③ 같은 GPIOD 안의 register는 base가 같고 offset만 다름</span><br>
<span style="color:#dc2626">! GPIOD와 RCC는 서로 다른 peripheral이므로 base address도 다름</span><br>
<br>
<span style="color:#1d4ed8">3) GPIO register offset</span><br>
<span style="color:#111827">① MODER = +0x00: GPIO pin mode 설정</span><br>
<span style="color:#111827">② OTYPER = +0x04: 출력 type 설정</span><br>
<span style="color:#111827">③ OSPEEDR = +0x08: 출력 speed 설정</span><br>
<span style="color:#111827">④ PUPDR = +0x0C: pull-up / pull-down 설정</span><br>
<span style="color:#111827">⑤ IDR = +0x10: 입력값 읽기</span><br>
<span style="color:#111827">⑥ ODR = +0x14: 출력값 읽기·쓰기</span><br>
<span style="color:#111827">⑦ RCC AHB1ENR = RCC_BASE + 0x30</span><br>
<span style="color:#111827">cf) 32-bit register 한 개 = 4 byte이므로 연속 register offset이 보통 0x04씩 증가</span><br>
<span style="color:#dc2626">! register 순서·간격·reserved 영역은 반드시 register map 표를 기준으로 함</span><br>
<br>
<span style="color:#1d4ed8">ex) GPIOD ODR 주소 계산</span><br>
<span style="color:#111827">GPIOD_BASE + ODR_OFFSET</span><br>
<span style="color:#111827">= 0x40020C00 + 0x14</span><br>
<span style="color:#111827">= 0x40020C14</span><br>
<span style="color:#dc2626">! 계산 뒤 reference manual의 register address와 다시 대조</span><br>
<br>
<span style="color:#1d4ed8">3. pointer cast와 dereference로 값에 접근한다</span><br>
<span style="color:#1d4ed8">1) 용어 설명</span><br>
<span style="color:#111827">① <strong>pointer cast</strong>: 숫자로 된 주소를 특정 타입을 가리키는 pointer로 변환</span><br>
<span style="color:#111827">② <strong>dereference(*)</strong>: pointer가 가리키는 주소의 실제 값에 접근</span><br>
<span style="color:#111827">③ <strong>volatile</strong>: 코드 밖 하드웨어가 값을 바꿀 수 있으므로 매 접근을 실제로 수행하도록 compiler에 알림</span><br>
<span style="color:#dc2626">! 주소 숫자만으로는 register 값을 읽고 쓸 수 없고 <strong>pointer 변환과 역참조</strong>가 필요</span><br>
<br>
<span style="color:#1d4ed8">2) macro 해석</span><br>
<span style="color:#111827">#define GPIOD_MODER (*(volatile unsigned long *)(GPIOD_BASE + 0x00))</span><br>
<span style="color:#111827">#define GPIOD_ODR   (*(volatile unsigned long *)(GPIOD_BASE + 0x14))</span><br>
<span style="color:#111827">① GPIOD_BASE + offset → register 주소를 숫자로 계산</span><br>
<span style="color:#111827">② (volatile unsigned long *) → volatile register pointer로 변환</span><br>
<span style="color:#111827">③ 맨 앞 * → 주소를 역참조해 register 값으로 사용</span><br>
<span style="color:#dc2626">★ <strong>base + offset → pointer cast → dereference → register 값</strong></span><br>
<br>
<span style="color:#1d4ed8">3) bit를 바꿔 GPIO를 제어</span><br>
<span style="color:#111827">GPIOD_MODER |= (1U &lt;&lt; 6); → MODER bit 6 SET</span><br>
<span style="color:#111827">GPIOD_ODR   |= (1U &lt;&lt; 3); → PD3 High</span><br>
<span style="color:#111827">cf) 1U &lt;&lt; n = 1을 n번 왼쪽으로 옮겨 n번 bit mask 생성</span><br>
<span style="color:#111827">cf) |= = 기존 값은 유지하면서 mask에 해당하는 bit를 1로 설정</span><br>
<span style="color:#dc2626">! MODER가 초기값 0이라는 전제에서 bit 6 SET은 PD3의 2-bit field를 01로 만듦</span><br>
<span style="color:#dc2626">! volatile은 접근을 유지하지만 bit 연산의 정확성이나 동시성 안전까지 보장하지 않음</span><br>
<br>
<span style="color:#1d4ed8">4. 구조체로 register block을 mapping한다</span><br>
<span style="color:#1d4ed8">1) 개별 pointer macro의 한계</span><br>
<span style="color:#111827">① register마다 base + offset cast를 반복해야 함</span><br>
<span style="color:#111827">② 주소·offset 복사 과정에서 실수하기 쉬움</span><br>
<span style="color:#111827">③ 주변장치 register 수가 많아지면 코드가 지저분해짐</span><br>
<span style="color:#dc2626">! 직접 macro 방식은 원리 학습용이며 실제 프로젝트는 CMSIS header를 우선</span><br>
<br>
<span style="color:#1d4ed8">2) 구조체 mapping 원리</span><br>
<span style="color:#111827">① register map 순서대로 32-bit member를 선언</span><br>
<span style="color:#111827">② member 주소 차이가 register offset과 일치</span><br>
<span style="color:#111827">③ 구조체 pointer가 peripheral base address를 가리키게 함</span><br>
<span style="color:#111827">④ member 이름으로 register에 접근</span><br>
<span style="color:#dc2626">★ <strong>구조체 member 순서·크기·reserved 공간이 hardware register map과 정확히 같아야 함</strong></span><br>
<br>
<span style="color:#1d4ed8">3) GPIO_TypeDef 흐름</span><br>
<span style="color:#111827">MODER +0x00 → OTYPER +0x04 → OSPEEDR +0x08 → PUPDR +0x0C</span><br>
<span style="color:#111827">→ IDR +0x10 → ODR +0x14</span><br>
<span style="color:#111827">#define GPIOD ((GPIO_TypeDef *)GPIOD_BASE)</span><br>
<span style="color:#111827">GPIOD-&gt;MODER → base + 0x00의 값</span><br>
<span style="color:#111827">GPIOD-&gt;ODR → base + 0x14의 값</span><br>
<span style="color:#111827">cf) ptr-&gt;member = (*ptr).member</span><br>
<span style="color:#dc2626">! 구조체가 register를 새로 만드는 것이 아니라 <strong>이미 존재하는 주소 배치를 C 타입으로 표현</strong></span><br>
<br>
<span style="color:#1d4ed8">그림: 구조체와 register map 대응</span><br>
<span style="color:#111827">GPIOD base 0x40020C00</span><br>
<span style="color:#111827">→ MODER member  +0x00</span><br>
<span style="color:#111827">→ OTYPER member +0x04</span><br>
<span style="color:#111827">→ OSPEEDR member +0x08</span><br>
<span style="color:#111827">→ ...</span><br>
<span style="color:#111827">→ ODR member    +0x14</span><br>
<span style="color:#dc2626">! member 위치와 manual의 offset이 1:1로 맞아야 함</span><br>
<br>
<span style="color:#1d4ed8">5. CMSIS header가 이 작업을 대신한다</span><br>
<span style="color:#1d4ed8">1) CMSIS에서 이미 정의한 것</span><br>
<span style="color:#111827">① peripheral base address</span><br>
<span style="color:#111827">② register offset에 맞춘 GPIO_TypeDef·RCC_TypeDef 구조체</span><br>
<span style="color:#111827">③ GPIOD·RCC 같은 peripheral pointer macro</span><br>
<span style="color:#111827">④ target header: stm32f767xx.h</span><br>
<span style="color:#dc2626">! 실습에서 직접 재정의하지 말고 vendor CMSIS device header를 사용</span><br>
<br>
<span style="color:#1d4ed8">2) 원리를 알아야 하는 이유</span><br>
<span style="color:#111827">① GPIOD-&gt;MODER 문법이 실제 어느 주소를 쓰는지 추적 가능</span><br>
<span style="color:#111827">② register 값이 바뀌지 않을 때 base·offset·clock·bit 설정을 점검 가능</span><br>
<span style="color:#111827">③ HAL·LL API 아래에서 일어나는 register 접근을 이해 가능</span><br>
<span style="color:#111827">④ debugger와 reference manual을 연결해 문제를 좁힐 수 있음</span><br>
<span style="color:#dc2626">★ CMSIS를 쓰더라도 <strong>memory map → register address → bit 동작</strong> 연결을 설명할 수 있어야 함</span><br>
<br>
<span style="color:#1d4ed8">6. 직접 접근 코드 점검 순서</span><br>
<span style="color:#111827">① 대상 MCU와 reference manual이 일치하는가?</span><br>
<span style="color:#111827">② peripheral base address가 맞는가?</span><br>
<span style="color:#111827">③ register offset과 access 권한이 맞는가?</span><br>
<span style="color:#111827">④ register 폭에 맞는 volatile pointer인가?</span><br>
<span style="color:#111827">⑤ 필요한 peripheral clock을 RCC에서 켰는가?</span><br>
<span style="color:#111827">⑥ bit 위치·field 폭·초기값을 확인했는가?</span><br>
<span style="color:#111827">⑦ debugger에서 실제 register 값과 pin 동작을 확인했는가?</span><br>
<span style="color:#dc2626">! 주소만 맞아도 끝이 아님: <strong>clock·access 권한·field 값</strong>까지 맞아야 동작</span><br>
<br>
<span style="color:#1d4ed8">7. 핵심 3줄</span><br>
<span style="color:#111827">1) <strong>STM32의 주변장치 register는 MMIO 주소 공간에 있으며 실제 주소는 peripheral base + register offset으로 구한다.</strong></span><br>
<span style="color:#111827">2) <strong>계산한 주소를 volatile pointer로 cast하고 dereference하면 register 값을 읽고 쓸 수 있다.</strong></span><br>
<span style="color:#111827">3) <strong>CMSIS는 register map과 같은 구조체를 base address에 mapping해 GPIOD-&gt;MODER 같은 접근을 제공한다.</strong></span><br>
<br>
<span style="color:#1d4ed8">Q. register 주소는 어떻게 구하는가?</span><br>
<span style="color:#111827">A. reference manual에서 peripheral base address와 register offset을 찾아 더한다.</span><br>
<span style="color:#1d4ed8">Q. register pointer에 volatile이 필요한 이유는?</span><br>
<span style="color:#111827">A. hardware가 코드 흐름과 무관하게 값을 바꿀 수 있으므로 compiler가 register 접근을 생략하거나 저장값으로 대체하지 않게 하기 위해서다.</span><br>
<span style="color:#1d4ed8">Q. GPIOD-&gt;ODR은 실제로 무엇을 의미하는가?</span><br>
<span style="color:#111827">A. GPIOD base를 가리키는 GPIO_TypeDef pointer에서 +0x14 위치의 ODR member에 접근한다는 뜻이다.</span><br>
<span style="color:#1d4ed8">Q. 구조체 mapping이 개별 pointer macro보다 나은 점은?</span><br>
<span style="color:#111827">A. register 순서와 offset을 구조체 member로 한 번 표현해 반복 cast와 주소 복사 실수를 줄인다.</span><br>
<span style="color:#1d4ed8">Q. CMSIS header를 쓰는데 직접 접근 원리를 왜 알아야 하는가?</span><br>
<span style="color:#111827">A. header와 HAL 아래의 실제 주소·register·bit 동작을 추적해 설정 오류를 디버깅하기 위해서다.</span><br>
<br>
<span style="color:#1d4ed8">8. 30초 면접 답변</span><br>
<span style="color:#111827">STM32의 주변장치 register는 Memory-Mapped I/O 방식으로 주소 공간에 배치됩니다.</span><br>
<span style="color:#111827">Reference manual에서 peripheral base address와 register offset을 더해 실제 주소를 구하고, 이를 volatile pointer로 cast한 뒤 dereference하면 register를 읽고 쓸 수 있습니다.</span><br>
<span style="color:#111827">개별 register마다 cast하면 실수하기 쉬우므로 register map과 같은 순서의 구조체를 base address에 mapping해 GPIOD-&gt;MODER처럼 접근합니다.</span><br>
<span style="color:#dc2626">CMSIS device header가 이 base address와 구조체 mapping을 이미 제공하므로 실제 프로젝트에서는 header를 사용하고, 직접 접근 원리는 디버깅에 활용합니다.</span><br>
<br>
<span style="color:#1d4ed8">9. 지금 깊이 조절</span><br>
<span style="color:#111827">지금 꼭 이해</span><br>
<span style="color:#111827">- MMIO와 register의 관계</span><br>
<span style="color:#111827">- register address = base + offset</span><br>
<span style="color:#111827">- pointer cast → dereference → bit 변경</span><br>
<span style="color:#111827">- volatile의 역할</span><br>
<span style="color:#111827">- 구조체 mapping과 GPIOD-&gt;MODER</span><br>
<br>
<span style="color:#111827">지금은 이름만</span><br>
<span style="color:#111827">- APB1 / APB2 / AHB</span><br>
<span style="color:#111827">- CMSIS device header, GPIO_TypeDef</span><br>
<br>
<span style="color:#111827">나중에 깊게</span><br>
<span style="color:#111827">- bus matrix와 address decoder</span><br>
<span style="color:#111827">- 구조체 padding·alignment·reserved member 검증</span><br>
<span style="color:#111827">- register access type과 read-modify-write 경쟁</span><br>
<span style="color:#dc2626">! 지금은 base + offset 계산과 구조체 mapping을 직접 설명할 수 있게 한다</span><br>
<br>
<span style="color:#1d4ed8">10. 참고 자료</span><br>
<a style="color:#111827" href="../../10_주제별/stm32/기초/2_레지스터_직접접근_메모리맵.md">레지스터 직접 접근 — 원본 학습노트</a><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=XOsyrZGZtR8">STM32 입문 강의 몰아보기</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/010_포인터.md">C언어 포인터</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/040_비트연산자.md">비트 연산자와 bit mask</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/050_Preprocessor와_volatile.md">Preprocessor와 volatile</a><br>
<a style="color:#111827" href="../../10_주제별/c언어/C_심화_강의/8_CMSIS_구조체와_MCU_레지스터_매핑.md">CMSIS 구조체와 MCU register mapping</a><br>
