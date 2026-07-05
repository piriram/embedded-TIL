# STM32 베어메탈 #1 — 첫 프로젝트와 LED 블링크

**주제:** STM32F407에서 라이브러리·어셈블리 없이 순수 C만으로 최소 펌웨어를 만들고 LED를 깜빡이기
**타겟 MCU:** STM32F407 (Streamline F407 보드 + STLink 호환 프로그래머 + 백플레인)
**원본 강의:** [STM32 Bare Metal Tutorial #1 — Creating Your First Project & LED Blink (YouTube)](https://www.youtube.com/watch?v=m1C2LlFRwY4)

---

## 1. 베어메탈(Bare Metal)의 정의 — 강사의 입장

"베어메탈"이라는 용어를 두고 강사는 댓글에서 종종 공격을 받았다고 한다. 일반적으로는 **OS(RTOS 등)를 사용하지 않는 환경**을 베어메탈이라 부르고, 이 정의대로면 STM32에서 HAL 라이브러리를 써도 RTOS만 없으면 베어메탈로 간주된다.

> "I simply disagree. ... bare metal means having no abstraction layer between you and the hardware whether that's a task scheduler or operating system or whatever."

강사가 쓰는 정의는 더 엄격하다.

- **베어메탈 = 하드웨어와 코드 사이에 어떠한 추상화 계층(Abstraction Layer)도 없는 상태**
- HAL 같은 라이브러리도 일절 쓰지 않고, **레지스터 레벨에서 직접 하드웨어를 제어**
- 다른 사람들은 이를 **register level programming**이라고도 부름

강사 본인도 베어메탈은 처음이고 시리즈를 진행하며 배우는 중이라고 밝힘. 1980년대 중후반 Intel 8051 / 6502 이후로 베어메탈은 거의 안 했다고 함.

---

## 2. 하드웨어 & 개발 환경

### 하드웨어
- **MCU 보드:** Streamline F407 (STM32F407)
- **프로그래머/디버거:** STLink 호환 모듈
- **백플레인(Backplane):** 프로그래머와 MCU 보드를 슬롯에 꽂아 연결

### 소프트웨어 (강사는 Debian 환경 사용)
- **Make** (또는 CMake)
- **ARM C 컴파일러** (GNU)
- **디버거** (gdb)
- **STLink CLI** (`st-flash`)
- **OpenOCD** — MCU에 펌웨어 로드
- **IDE:** 강사는 VS Code 사용 (원래 CLion 쓰려 했으나 VS Code가 의도대로 동작해서 채택). Eclipse(STM32CubeIDE 말고 일반 Eclipse), NetBeans 등도 가능

명령행 비중이 큼. "터미널이 더 쉽다"는 이유.

---

## 3. 필수 문서 — 데이터시트와 레퍼런스 매뉴얼

베어메탈에서는 HAL 쓸 때보다 문서가 더 중요하다.

| 문서 | 분량 | 역할 |
| --- | --- | --- |
| **Datasheet (F407)** | 약 25페이지 | 칩 기본 스펙 |
| **Reference Manual** | **약 1,757페이지** | 레지스터 맵, 주변장치 동작 — 베어메탈의 바이블 |

> 끝까지 다 읽는 사람은 없다. 하지만 **목차를 훑어 구조를 익혀두는 건 의무**다. 일반적으로 앞부분은 CPU 전체, 뒤로 갈수록 주변장치(Peripheral)별 챕터다.

예: GPIO는 270페이지부터 약 20~30페이지에 걸쳐 설명 → 이것만 다 보면 GPIO는 마스터 가능.

---

## 4. STM32 부팅 메커니즘 — 무엇이 일어나는가

전원이 켜지면 MCU는 무엇을 하나?

1. CPU는 **주소 0**에서 실행을 시작한다.
2. 그런데 MCU는 내부적으로 주소 0을 **Flash 시작 주소(`0x0800 0000`)로 리매핑**한다. 즉 실제로는 Flash 첫 바이트부터 읽는다.
3. Flash의 **첫 4바이트(1 word)** = **스택 포인터(SP) 초기값**
4. 그 다음 4바이트 = **Reset 벡터(부팅 시 실행할 함수의 주소)**
5. 그 뒤로 인터럽트 벡터들이 이어진다.

벡터 테이블 구성:
- **Unmaskable 벡터 16개** (Reset, Fault 등) — 위 SP와 Reset 포함
- 그 뒤에 모듈별로 **최대 91개**의 인터럽트 벡터 (칩에 따라 다름)
- 합쳐서 **총 107개 × 4바이트 = 428바이트**가 벡터 테이블만으로 잡힘

### 일반적인 방식 vs 이 강의의 방식

| | 일반 (CubeMX 자동생성) | 이 강의 |
| --- | --- | --- |
| 부트스트랩 코드 | 어셈블리 파일(`.s`)이 부트스트랩 후 `main()` 호출 | **순수 C만으로 부트스트랩 + main 호출** |
| 영감 | — | Sajupa의 GitHub 페이지에서 100% 영감 (강사가 직접 언급) |

> "his examples he is not using a single line of assembler code and this idea is 100% inspired from him."

---

## 5. 실습 1 — 최소 프로젝트 (First Minimal): 단 3개 파일

목표: 펌웨어가 실제로 STM32에서 부팅·실행되는 최소 조건. **라이브러리 0, 어셈블리 0**.

폴더 구조:
```
first_minimal/
├── F407.ld     ← 링커 스크립트
├── main.c      ← 벡터 테이블 + Reset + main
└── Makefile    ← 빌드 자동화
```

### 5.1 링커 스크립트 (`F407.ld`)

**가장 하드웨어 종속적인 파일**. 그래서 칩 이름을 파일명에 박음(`F407.ld`). 약 32줄.

> 강사도 "링커 스크립트 문법의 전문가는 아니"라며 솔직하게 인정. 의도만 명확하면 됨.

구성 요소:

1. **Entry point** — 펌웨어 실행이 시작되는 심볼 정의
2. **메모리 영역 정의**
   - **Flash:** F407은 실제 1MB이고 기본적으로 2뱅크로 나뉘지만, 강의에서는 **512K**만 잡음. (16K만 잡아도 동작은 됨. 어차피 거의 안 씀.)
   - **RAM:** 총 약 128KB 중 앞쪽 92K가 일반 SRAM, 나머지 64K는 별도 주소 공간. **64K**만 잡아도 됨.
3. **`_estack` 정의**
   - 스택 포인터의 초기값 = **RAM의 끝 주소** = `RAM origin + RAM length`
   - 이유: **스택은 위(높은 주소)에서 아래로 자라고**, 힙·데이터는 아래에서 위로 자란다. 끝에서 시작해야 가장 멀리 떨어진다. **둘이 만나면 망함.**
4. **섹션 배치**
   - `vectors` 섹션 — 벡터 테이블 (Flash 맨 앞에 위치)
   - `.text` — 코드
   - `.data`, `.rodata` — 데이터, 읽기 전용 데이터
   - `.bss` 등

> 강사 노트: "이 링커 스크립트는 시리즈 후속 강의에서도 거의 그대로 쓸 것이다."

### 5.2 `main.c` — 순수 C 부트스트랩

핵심 아이디어 3가지:
1. **벡터 테이블을 C 배열로 정의**
2. **Reset 핸들러를 C 함수로 작성** (어셈블리 없음)
3. `main()` 호출

#### (1) 외부 심볼 `_estack` 가져오기

링커 스크립트에서 정의한 `_estack`을 C에서 `extern`으로 받음.

#### (2) 벡터 테이블 정의

```c
// 개념적 형태 (강의 코드의 의도)
void (*const vectors[])(void) __attribute__((section(".vectors"))) = {
    (void(*)(void))(&_estack),  // [0]  스택 포인터 초기값
    reset_handler,              // [1]  Reset 벡터 → reset() 호출
    // 나머지는 정의 안 하면 0으로 채워짐 → 인터럽트 동작 안 함 (지금은 OK)
};
```

- `vectors` 배열은 `.vectors` 섹션에 들어가고, 링커 스크립트가 이걸 **Flash 맨 앞**에 배치한다.
- 첫 원소가 **`_estack` 주소** (= 스택 포인터)인 것은 ARM Cortex-M의 부팅 규약.
- 두 번째 원소가 Reset 핸들러 함수 포인터.
- 나머지 105개 인터럽트 벡터는 정의 안 했으니 0. 인터럽트 발생하면 동작 안 함 — 지금은 LED만 깜빡일 거라 상관없음.

#### (3) Reset 핸들러

```c
void __attribute__((naked, noreturn)) reset_handler(void) {
    // .data 섹션 초기화 (Flash → RAM 복사)
    // .bss 영역 0으로 초기화
    main();
    for (;;) { }   // main이 끝나면 안 되지만 안전망
}
```

**왜 `__attribute__((naked))`인가?**
> "naked basically means the whole C push on stack and all that is avoided because we will never ever exit from this function."

일반 함수는 진입 시 레지스터를 스택에 push, 종료 시 pop 하는 prologue/epilogue가 자동 삽입된다. Reset 핸들러는 **절대 return 하지 않으니** 이 코드가 필요 없다. `naked`로 prologue/epilogue 제거 → 코드 크기·시작 동작이 깔끔.

**왜 끝에 무한 루프?**
- 안전망. `main()`이 절대 return 하면 안 되지만 혹시 모르니.
- 컴파일러가 "main도 무한 루프, return 없음"을 알면 이 부분을 **최적화로 삭제할 수도 있다**.

#### (4) `main()`

```c
int main(void) {
    volatile uint32_t count = 0;
    volatile uint32_t half  = 0;
    while (1) {
        count += 2;
        half   = count / 2;
        half  += 1;
    }
}
```

**왜 굳이 두 변수를 만들고 계산을 하나?**
> "if you don't use a variable anywhere the C compiler will normally just try to optimize that out of the way."

아무 일도 안 하는 `while(1)`이면 컴파일러가 통째로 최적화로 날릴 위험이 있다. 변수 두 개를 실제로 쓰는 계산을 넣어 코드가 살아남게 함. **`volatile`은 명시되지 않았지만 의도는 같은 맥락** — 컴파일러가 멋대로 못 지우게.

### 5.3 `Makefile`

핵심 옵션과 흐름.

- **`CFLAGS`에 `-O0`** — 최적화 끔 (지금은 디버깅·동작 확인이 우선)
  > "Normally I would use `-Og` which is optimized for debugging but for now let's not optimize anything."
- **`LDFLAGS`** — `F407.ld` 링커 스크립트 사용 (강의 중 강사가 처음 `F407.LN`으로 오타냈다가 `F407.LD`로 정정)
- **`-nostartfiles`** — 표준 스타트업 파일 안 씀
- **`-nostdlib`** + **nano specs** — 표준 라이브러리도 안 씀
- **Source는 `main.c` 하나뿐**

빌드 흐름:
```
make
 → .c 컴파일 + 링킹 한 번에 → firmware.elf 생성
 → firmware.elf에서 바이너리만 추출 → firmware.bin
```

`firmware.elf`(약 86KB) vs `firmware.bin`(**528바이트**)
- ELF는 디버깅용 심볼·메타데이터까지 다 들어있음
- BIN은 실제로 Flash에 쓰일 순수 바이너리만

**바이너리 크기 분석:**
- 벡터 테이블: 107개 × 4바이트 = **428바이트**
- 따라서 528 - 428 = **실제 코드는 약 100바이트**

> "100 bytes of code in this binary."

`make flash` 타겟으로 `st-flash`를 호출해 MCU에 굽는다.

### 5.4 실제로 동작하는지 증명 — 디버거로

LED도 없고 UART도 없으니 눈으로는 동작을 확인 못 한다. → **gdb로 step over**.

1. 디버거 실행
2. `count`, `half` 변수를 watch
3. `F10`(step over)을 누를 때마다:
   - 처음: `count`는 0, `half`는 **쓰레기 값** (스택의 이전 값)
   - 1스텝: `count = 2`
   - 2스텝: `half = 1` (= 2 / 2)
   - 3스텝: `half = 2` (= 1 + 1)

→ 코드가 실제로 STM32F407에서 실행 중임이 증명됨.

> 강사 말 한 마디: "I rest my case."

---

## 6. 실습 2 — LED 블링크 (Second Blink): 진짜 Hello World

목표: 보드의 **C13 핀에 연결된 파란 LED**를 깜빡임.

### 6.1 시작 전 알아야 할 두 가지

**(A) 모든 주변장치(Peripheral)의 클럭은 기본적으로 꺼져 있다.**
> "None of the peripherals are clocked. They're all just there. They're not doing anything."

- 전력 절감 목적
- GPIO 포트도 마찬가지 — **포트 C를 쓰려면 먼저 포트 C에 클럭을 공급**해야 함
- 클럭 공급은 **RCC (Reset and Clock Control)** 레지스터로

**(B) STM32F4는 부팅 직후 내부 RC 오실레이터로 16MHz**
- PLL(Phase-Locked Loop)을 켜면 훨씬 빠르게 돌릴 수 있지만 지금은 안 건드림
- 16MHz면 LED 깜빡임에는 차고 넘침

### 6.2 헬퍼 매크로 — `bit()`와 `PIN()`

```c
#define BIT(n)         (1U << (n))            // 비트 n에 1
#define PIN(bank, n)   ((((bank) - 'A') << 8) | (n))   // 핀 식별자 인코딩
```

- `BIT(7)` → `1`을 7번 왼쪽 시프트
- `PIN('C', 13)` → C13 핀
- 직접 손으로 매번 시프트 안 해도 되게 하는 편의 매크로

> "this is a slippery slope because this is where it's no longer completely bare metal — oh I'm just joking. But it is the beginning of a library that will eventually probably be a library."

— 강사 본인도 "이 매크로들이 결국 라이브러리의 시작점"이라고 농담 반 진담 반.

### 6.3 핵심 트릭 — 구조체로 레지스터 매핑

STM32에서는 **모든 것이 Peripheral, 모든 Peripheral은 Register**다.

#### RCC 구조체

레퍼런스 매뉴얼에 정의된 RCC 레지스터들(약 30개의 32비트 레지스터)을 그대로 C 구조체로 선언.

```c
struct rcc {
    volatile uint32_t CR;          // offset 0x00
    volatile uint32_t PLLCFGR;     // offset 0x04
    volatile uint32_t CFGR;
    // ...
    volatile uint32_t AHB1ENR;     // ← GPIO 포트 클럭 활성화에 쓸 레지스터
    // ...
};
```

그리고 RCC의 실제 메모리 주소(레퍼런스 매뉴얼 참조)를 **포인터로 강제 캐스팅**:

```c
#define RCC ((struct rcc *) 0x40023800)   // 주소는 RM 참조
```

이제 `RCC->AHB1ENR |= BIT(2);` 같은 코드로 메모리 매핑된 레지스터를 직접 만진다.

#### GPIO 구조체

GPIO 포트 하나당 레지스터 묶음(MODER, OTYPER, OSPEEDR, PUPDR, IDR, ODR, BSRR, LCKR, AFR[2])을 구조체로:

```c
struct gpio {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;     // Bit Set/Reset Register
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
};
```

- 포트는 A, B, C, ... 여러 개. 각 포트는 핀이 16개.
- 핀 식별자(`PIN('C', 13)`)에서 bank/pin을 디코딩해 해당 포트 구조체 포인터를 얻음.

### 6.4 GPIO 모드 enum

```c
enum gpio_mode {
    GPIO_MODE_INPUT  = 0,
    GPIO_MODE_OUTPUT = 1,
    GPIO_MODE_AF     = 2,   // Alternative Function
    GPIO_MODE_ANALOG = 3,
};
```

C enum은 명시 안 하면 0부터 자동 부여 — 0, 1, 2, 3 그대로 매뉴얼의 모드 인코딩과 일치.

### 6.5 헬퍼 함수 (`inline`)

#### `gpio_set_mode(pin, mode)`
- 핀의 bank → 해당 GPIO 구조체 포인터
- `MODER` 레지스터에서 해당 핀의 2비트를 `mode` 값으로 설정

#### `gpio_write(pin, value)` — BSRR을 이용한 비트 토글

**BSRR (Bit Set/Reset Register)** 의 디자인이 묘하다.

- **32비트 레지스터**, 그런데 핀은 16개뿐.
- **하위 16비트에 1을 쓰면 → 해당 핀 SET (High)**
- **상위 16비트에 1을 쓰면 → 해당 핀 RESET (Low)**

```c
static inline void gpio_write(uint16_t pin, bool val) {
    struct gpio *p = /* pin → port */;
    p->BSRR = (1U << PINNO(pin)) << (val ? 0 : 16);
}
```

이 설계의 장점: **하나의 write로 atomic하게 set 또는 reset**. read-modify-write가 아니라서 인터럽트 안전.

#### `spin(count)` — 무식한 딜레이

```c
static inline void spin(volatile uint32_t count) {
    while (count--) ;
}
```

- 16MHz에서 카운트다운하니 적당히 느림 → 눈에 보일 만한 깜빡임 주기 만들기 가능
- **강사 본인도 "100% 자랑스럽지는 않은 방법"**이라고 인정.
- 초기 시리즈에서도 이 방식으로 시작했다 다음 영상에서 **SysTick 타이머**로 개선할 예정이라고 예고.

### 6.6 `main()` — 완성

```c
int main(void) {
    uint16_t led = PIN('C', 13);            // 파란 LED

    RCC->AHB1ENR |= BIT(2);                 // GPIOC 클럭 ON (포트 C = AHB1의 bit 2)
    gpio_set_mode(led, GPIO_MODE_OUTPUT);   // C13을 출력 모드

    for (;;) {
        gpio_write(led, true);
        spin(999999);
        gpio_write(led, false);
        spin(999999);
    }
}
```

- `RCC->AHB1ENR` 비트 2 = 포트 C 클럭 활성화 (정확한 비트 위치는 RM 참조)
- 강사: "지금은 그냥 믿어. 나중에 자세히 다룬다."
- 빌드 → `make flash` → **파란 LED 깜빡임 확인**.

### 6.7 바이너리 크기

- **블링크 버전 바이너리: 784바이트** (최소 버전 528바이트보다 약 256바이트 큼)
- Makefile은 여전히 `-O0` (최적화 없음). 그래도 이 정도.

---

## 7. 최적화 챌린지 (강사가 예고한 대회)

> "I am sure that can be smaller. ... I expect down towards 100 to 150 bytes."

- 현재 784바이트 → **약 100~150바이트까지 줄일 수 있다**고 강사 추정
- 거의 **500바이트 이상 줄일 여지**가 있음
- 규칙 요약 (영상에서 강사가 미리 흘린 것):
  - LED가 **눈에 보일 속도로 깜빡이기만 하면 됨** (정확히 1Hz일 필요 없음)
  - "편법"(변수 미초기화, 일반적으로 나쁜 습관, "불법" 같은 짓) **다 허용**
  - 본인이 보드에 flash해서 깜빡임만 확인되면 OK
- 우승자에게 보드 1세트 (백플레인 + 프로그래머 + MCU 보드) 우편 발송

> "하드웨어의 극한을 이해하는 좋은 훈련."

---

## 8. 정리 — 무엇을 한 것인가

1. **링커 스크립트(`F407.ld`)** — 메모리 영역(Flash, RAM)과 스택 포인터(`_estack`), 섹션 배치 정의
2. **`main.c`** — 어셈블리 한 줄도 없이 순수 C로:
   - 벡터 테이블 정의 (배열의 첫 원소 = `_estack`, 두 번째 = Reset 핸들러)
   - `naked` 어트리뷰트의 Reset 함수 → `main()` 호출
   - `main()` 안에서 RCC 클럭 활성화, GPIO 모드 설정, BSRR로 핀 토글, spin 딜레이
3. **`Makefile`** — `-O0`, `-nostartfiles`, `-nostdlib`, nano specs로 최소 의존 빌드 → `firmware.bin` 생성 → `st-flash`로 굽기
4. **결과:** STM32F407에서 파란 LED가 깜빡임. 바이너리 784바이트.

핵심 인사이트:
- "베어메탈 = OS 없음"이 아니라 **"추상화 계층 없음"**
- 어셈블리 스타트업 없이도 **순수 C로 부트스트랩 가능** (Sajupa 영감)
- **메모리 주소를 구조체 포인터로 캐스팅**하는 기법이 레지스터 제어의 정수
- BSRR의 상위/하위 16비트 분할은 **atomic set/reset**을 위한 의도된 설계
- 초보적인 `spin()` 딜레이는 다음 영상에서 **SysTick 타이머**로 개선 예정

---

## 참고 자료

- [STM32 Bare Metal Tutorial #1 (YouTube)](https://www.youtube.com/watch?v=m1C2LlFRwY4)
- STM32 World Wiki — "STM32 Bare Metal Development" 페이지 (영상 설명란 링크)
- STM32 Fun Bare Metal — GitHub Repository (강사가 시리즈용으로 새로 만든 저장소, 영상 설명란 링크)
- Sajupa의 GitHub 페이지 — 어셈블리 없는 부트스트랩 기법의 원본 (STM32 Wiki에서 링크)
- **STM32F407 Datasheet** (약 25페이지)
- **STM32F4 Reference Manual (RM0090)** — 약 1,757페이지. GPIO는 p.270~

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** 베어메탈은 HAL이나 OS 같은 추상화 계층 없이 **레지스터 레벨에서 직접 하드웨어를 제어**하는 프로그래밍 방식이다.
- **왜 필요:** 코드 크기·실행 속도·전력 소모를 극한으로 최적화하고, 하드웨어 동작을 완전히 이해·제어해야 하는 임베디드 환경에서 필요.
- **동작:** STM32 부팅 시 CPU는 Flash 시작 주소(`0x0800 0000`)로 리매핑된 0번지부터 실행한다. 첫 4바이트는 스택 포인터(`_estack` = RAM의 끝), 다음 4바이트는 Reset 벡터다. 링커 스크립트로 메모리 영역과 섹션 배치를 정의하고, `main.c`에서 벡터 테이블을 C 배열로 정의해 `naked` 어트리뷰트의 Reset 함수가 `main()`을 호출하게 한다. 주변장치 제어는 RCC로 해당 페리퍼럴 클럭을 켠 뒤 레지스터 묶음을 C 구조체로 매핑해 직접 쓴다.
- **비교:** HAL 라이브러리 방식은 함수 호출 한 줄로 LED를 켜지만 추상화 오버헤드가 있고 내부 동작을 알기 어렵다. 베어메탈은 펌웨어가 500~800바이트 수준으로 작지만 레지스터·메모리 맵을 직접 다뤄야 해 Reference Manual 의존도가 높다.
- **30초 통합 답변:**
  > 베어메탈은 HAL이나 OS 같은 추상화 계층 없이 레지스터를 직접 제어하는 방식입니다. 링커 스크립트로 Flash와 RAM 영역, 스택 포인터를 정의하고, main.c에서 벡터 테이블 첫 원소를 스택 포인터, 두 번째를 Reset 핸들러로 둬서 어셈블리 없이도 순수 C만으로 부팅합니다. Reset 함수는 naked 어트리뷰트로 prologue/epilogue를 제거해 main을 호출하고, main에서는 RCC 레지스터로 GPIO 포트 클럭을 켠 뒤 MODER로 출력 모드를 설정하고 BSRR의 하위 16비트로 SET, 상위 16비트로 RESET을 atomic하게 토글합니다. HAL 방식과 달리 펌웨어가 800바이트 이하로 작고 하드웨어를 완전히 이해·제어할 수 있다는 장점이 있습니다.
