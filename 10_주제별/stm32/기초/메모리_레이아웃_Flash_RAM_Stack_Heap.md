# STM32 메모리 레이아웃 — Flash, RAM, stack, heap

**원본 강의:** [Memory Layout in Embedded Systems | Flash, RAM, Stack, Heap Explained with STM32 (YouTube)](https://www.youtube.com/watch?v=UdkuoHSp_0s)

MCU firmware는 전원이 꺼져도 남아야 하는 프로그램 이미지와, 실행 중에만 필요한 RAM을 분리해 쓴다. 이 영상은 STM32를 예로 Flash, RAM, `.data`, `.bss`, heap, stack의 역할과 stack–heap 충돌이 만드는 reset·memory corruption을 정리한다.

---

## 1. Flash와 RAM의 역할

| 메모리 | 성질 | 대표 내용 |
| --- | --- | --- |
| Flash | non-volatile, 전원 꺼져도 보존 | 기계어 코드, 읽기 전용 상수, `.data` 초기값 이미지 |
| SRAM | volatile, reset/전원 차단 시 내용 소실 | 실행 중 전역 변수, stack, heap |

STM32의 Flash·SRAM 시작 주소와 크기는 제품군마다 다르다. 영상의 주소 예시는 특정 controller를 위한 참고값일 뿐이므로, 실제 project에서는 target datasheet와 linker script를 기준으로 한다.

---

## 2. reset 뒤 `main()` 전까지: startup code의 일

링커는 section을 Flash와 SRAM에 배치하고, startup code는 `main()` 전에 초기 RAM 상태를 만든다.

```text
Flash: [.text / .rodata] [.data 초기값 이미지]
                    │
                    ├─ .data 초기값을 SRAM으로 복사
                    └─ .bss 영역을 0으로 초기화

SRAM:  [.data] [.bss] [heap ... stack]
```

- `.text`: CPU가 실행할 코드. MCU에서는 대개 Flash에서 실행한다.
- `.data`: 0이 아닌 초기값을 가진 전역·`static` 객체의 실행 중 RAM 영역. 초기값은 Flash에도 저장된다.
- `.bss`: 초기화하지 않은 전역·`static` 객체와 보통 0으로 초기화한 객체. startup code가 SRAM에서 0으로 채운다.

```c
int baudrate = 115200;  /* .data: Flash 초기값 + SRAM 실행 공간 */
static int error_count; /* .bss: SRAM에서 0으로 초기화 */
static int ready = 0;   /* 보통 .bss */
```

> **주의**
> “`= 0`을 적었으니 반드시 `.data`다”는 설명은 일반적으로 맞지 않는다. C에서 static storage duration 객체의 기본 초기값은 0이며, toolchain은 보통 zero-initialized object를 `.bss`에 넣어 Flash 이미지를 절약한다. section 이름과 최종 배치는 implementation·linker script에 따라 달라지므로 map file이 기준이다.

---

## 3. stack과 heap이 충돌하면 왜 위험한가

stack은 함수의 지역 변수, 복귀 주소, 호출 상태를 담는다. Cortex-M firmware에서는 MSP 또는 PSP가 stack을 가리키며, 일반적인 linker layout에서는 SRAM의 높은 주소에서 낮은 주소 방향으로 자란다.

heap은 `malloc()` 같은 동적 할당을 위해 예약한 영역이며 흔한 배치에서는 낮은 주소에서 높은 주소 방향으로 자란다. stack의 큰 지역 배열·깊은 호출·RTOS task stack 사용량이 늘거나, heap 사용량이 늘면 두 영역의 여유 공간이 줄어든다.

```text
SRAM 높은 주소
┌─────────────────────┐
│ stack               │ ↓
│         여유         │
│ heap                │ ↑
├─────────────────────┤
│ .bss / .data        │
└─────────────────────┘
SRAM 낮은 주소
```

충돌하거나 경계를 넘으면 다른 변수·제어 정보를 덮어써 data corruption, 이상 동작, HardFault, reset처럼 재현하기 어려운 증상이 나타날 수 있다. MCU에 memory protection이 없거나 제한적이면 PC처럼 즉시 친절한 오류가 나오지 않을 수 있다.

---

## 4. Flash와 SRAM 예산을 함께 본다

초기값 있는 전역 변수 하나는 보통 두 예산을 모두 쓴다.

- Flash: 초기값을 저장
- SRAM: 실행 중 읽고 쓸 객체 공간

반면 큰 zero-initialized buffer는 SRAM은 쓰지만, 보통 Flash에 같은 크기의 0 바이트를 저장하지 않는다. 그래서 build log의 Flash 사용량만 보고 RAM이 충분하다고 판단하면 안 된다.

```c
static uint8_t rx_buffer[1024];          /* SRAM 약 1 KiB, 보통 .bss */
static uint8_t calibration[1024] = {1};  /* SRAM + Flash 초기값 이미지 */
```

정확한 숫자는 build 뒤 map file에서 `.text`, `.rodata`, `.data`, `.bss`, heap/stack 예약량을 확인한다. RTOS를 쓴다면 각 task stack과 TCB·queue의 RAM도 합산한다.

---

## 5. 디버깅과 설계 습관

- 큰 자동 배열은 stack 대신 static buffer 또는 명시적 buffer pool이 적합한지 검토한다.
- `malloc()`을 runtime hot path와 ISR에서 피하고, 필요 시 초기화 단계 또는 고정 크기 pool로 제한한다.
- linker script의 `_estack`, `_sdata`, `_edata`, `_sbss`, `_ebss` 같은 symbol과 map file로 경계를 확인한다.
- RTOS task마다 high-water mark를 측정하고, stack overflow hook·assert를 켠다.
- firmware update 뒤 RAM 요구량이 늘었다면 stack/heap 여유와 `.bss` 증가를 먼저 비교한다.

---

## 참고 자료

- [Memory Layout in Embedded Systems | Flash, RAM, Stack, Heap Explained with STM32 (YouTube)](https://www.youtube.com/watch?v=UdkuoHSp_0s)
- [C 프로그램의 메모리 레이아웃](../../c언어/C_프로그램_메모리_레이아웃.md) — 일반 C 모델과 저장 기간
- [레지스터 직접 접근(메모리 맵)](./2_레지스터_직접접근_메모리맵.md) — STM32 주변장치 주소 공간
- [RTOS 메모리 관리](../../cs/RTOS/4_메모리_관리.md) — task stack·heap·stack watermark

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** STM32 메모리 레이아웃은 non-volatile Flash의 firmware 이미지와 volatile SRAM의 `.data`, `.bss`, stack, heap을 linker와 startup code가 역할별로 배치하는 구조다.
- **왜 필요:** Flash와 SRAM 예산을 따로 관리하고 stack–heap 충돌을 예방해야 firmware update 뒤의 reset·memory corruption을 빠르게 진단할 수 있다.
- **동작:** reset 뒤 startup code가 Flash의 `.data` 초기값을 SRAM으로 복사하고 `.bss`를 0으로 만든 다음 `main()`을 호출한다. 함수 호출은 stack을 쓰고, 동적 할당은 heap을 쓰므로 두 영역의 최악 사용량을 관리해야 한다.
- **비교:** Flash는 전원 차단 후에도 남지만 SRAM은 휘발성이다. `.data`는 초기값 때문에 Flash와 SRAM을 모두 쓰고, `.bss`는 보통 SRAM만 쓰며 startup 때 0으로 초기화된다.
- **30초 통합 답변:**
  > STM32에서는 코드와 상수, 그리고 `.data`의 초기값이 Flash에 있고, 실행 중 전역 데이터와 stack·heap은 SRAM에 있습니다. reset 뒤 startup code가 `.data`를 Flash에서 SRAM으로 복사하고 `.bss`를 0으로 초기화한 뒤 `main`을 실행합니다. 그래서 초기값 있는 전역 변수는 Flash와 SRAM을 모두 쓰고, 큰 지역 배열이나 RTOS task stack은 SRAM을 빠르게 소진할 수 있습니다. map file과 stack high-water mark로 stack–heap 충돌 여유를 확인하는 습관이 중요합니다.
