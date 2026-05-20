# Lesson 8 — MCU Memory Map & Memory Mapped I/O

**주제:** MCU 메모리 맵 구조와 Memory Mapped I/O 개념. 주변장치 레지스터가 어떻게 메모리 주소로 매핑되어 제어되는지.
**원본 강의:** [Lesson 8. The MCU Memory Map and Memory Mapped I/O (YouTube)](https://www.youtube.com/watch?v=bWMsBXNAOAE)

---

## 1. 메모리 vs I/O — 두 가지 시나리오

컴퓨터 안에서 데이터를 읽고 쓸 때 시나리오는 크게 둘로 나뉜다.

**시나리오 1 — 메모리 (데이터 저장용):**
- 프로그램 실행 중 Flash에서 명령어를 읽거나, RAM에 변수 값을 썼다가 나중에 다시 읽는다.
- 핵심: **이전에 저장한 값을 그대로 다시 가져온다.**

**시나리오 2 — I/O (물리적 동작):**
- LED를 켜고 끄거나, UART로 시리얼 라인에 데이터를 보내고 받는다.
- 핵심: **값을 저장하는 게 아니라 무언가 물리적인 동작을 일으키거나 외부 상태를 읽는다.**
- I/O를 *write*한다는 건 값을 기억시키려는 게 아니라 "동작을 시키는 것"이고, *read*한다는 건 "외부 상태(예: 버튼이 눌렸는지)를 가져오는 것"이다.
- 어떤 I/O는 한쪽만 의미가 있다 — 키보드에 값을 *write*하는 건 말이 안 된다.

---

## 2. I/O 주소를 어떻게 지정할 것인가 — 두 접근법

이 둘을 어떻게 다룰지에 대한 설계 철학이 갈린다.

### 접근법 1: 메모리와 I/O를 완전히 분리

- 메모리 주소 공간과 I/O 주소 공간이 **별도**로 존재한다 (서로 다른 address space).
- 따라서 I/O 전용 어셈블리 명령어가 따로 필요하다 (예: `IN`, `OUT`).
- **예시:** 강사가 커리어 초기에 썼던 **Intel 8085**, 그리고 오늘날의 **x86 CPU**도 여전히 이 방식을 지원한다.

### 접근법 2: Memory Mapped I/O (MMIO)

- 메모리와 I/O를 **똑같이 취급**한다. 둘 다 "데이터 읽기/쓰기 + 주소 지정"이라는 점에서 비슷하니, I/O도 메모리 주소를 갖게 한다.
- 주소 `X`는 실제 RAM, 주소 `Y`는 LED 제어용 — 이런 식으로 동일한 주소 공간 안에 섞어 배치한다.
- 강사 표현: **"powerful abstraction"** — 메모리와 I/O의 세계를 통일해 소프트웨어 설계를 단순하게 만든다.

> **주의**
> Separate I/O address space를 지원하는 시스템에서도 MMIO를 동시에 쓸 수 있다. 강사가 언급한 **8085 시스템도 실제로는 MMIO를 사용했다.** 둘은 양자택일이 아니다.

---

## 3. Memory Mapped I/O와 "Register" 용어

MMIO를 쓰면 용어가 살짝 혼란스러워진다.
- I/O 장치가 "메모리 주소"를 갖고 "메모리 맵" 안에 들어있다고 말하지만, 실제로는 RAM이 아니다.
- 그것은 타이머·UART 같은 **하드웨어**일 뿐, 단지 프로그래머가 접근하기 편하도록 메모리 주소라는 껍데기를 씌운 것이다.
- 강사 표현: **"but it's okay we know what we mean and we get used to it."**

이 혼란을 줄이려고 I/O 쪽에 **Register**라는 용어를 따로 쓴다.
- 예: UART는 여러 개의 register를 가진다.
- 한 register에 *write*해서 보레이트를 설정하고, 다른 register를 *read*해서 시리얼로 수신된 데이터를 가져온다.

---

## 4. Peripheral 레지스터 구조 — Base Address + Offset

MCU 내부에서 peripheral(타이머·UART 등)이 어떻게 생겼는지.

> **이미지 필요**
> Peripheral 추상 다이어그램 — 시스템 버스 연결, pinmux로 내려가는 I/O 신호, 인터럽트 컨트롤러로 가는 인터럽트 출력, 내부에 register 묶음.
> - 출처: 강의 5분 30초~ 슬라이드
> - 대체안: ARM Cortex-M 시스템 아키텍처 그림

**구조:**
- Peripheral마다 시작점인 **Base Address**가 정해져 있다.
- 그 안의 각 register는 base에서 일정한 **Offset**만큼 떨어진 곳에 위치한다.
- 특정 register 주소 = `Base Address + Offset`.

**왜 offset이 4의 배수인가:**
- 모든 register가 **32비트 = 4바이트**라고 가정한다.
- 그래서 register 사이 offset이 4바이트씩 증가한다 → `0, 4, 8, 12, ...` 모두 4의 배수.

**왜 C 배열/구조체와 매칭되는가:**
- 강사 표현: **"if you know the c language well you might notice that the set of registers looks like an array or maybe you think of it as a data structure — and you would be right."**
- 그래서 실제 코딩에서 register 묶음을 C **배열** 또는 **구조체**로 모델링한다.
- 다음 강의들에서 더 다룰 예정.

---

## 5. 구체 예시 — USART 레지스터 맵

> **이미지 필요**
> USART register map 표 — bit 0~31, offset 컬럼, 각 비트 의미, 사용 안 하는 bit는 회색 처리.
> - 출처: STM32F4 Reference Manual (RM0090) USART 챕터, 강의 7분 30초~ 슬라이드
> - 대체안: 데이터시트의 register map 페이지 스크린샷

이 그림은 MCU reference manual에서 가져온 것이고, 이걸 **register map**이라 부른다 — 메모리 맵의 미니 버전이라고 생각하면 된다.

**핵심 관찰:**
- 비트 번호 0 → 31까지 표시 → **32비트 레지스터**임을 의미.
- 32비트 = 4바이트라서 offset 컬럼이 모두 4의 배수.
- 회색 처리된 비트들은 사용하지 않음 (reserved).

**대표 레지스터 두 개:**

### USART_SR (Status Register)
- 약자 SR = Status Register.
- USART 내부에서 지금 무슨 일이 벌어지는지 알려준다 (10비트 사용).
- 비트들이 가리키는 정보:
  - 시리얼 라인에서 수신된 바이트가 읽을 준비 됐는지
  - 전송용 라인에 바이트 쓸 공간이 있는지
  - USART가 어떤 에러를 감지했는지

### USART_DR (Data Register)
- **읽으면:** USART receive 라인에 들어온 문자를 가져온다.
- **쓰면:** USART transmit 라인으로 데이터를 내보낸다.
- "수신 데이터가 있는지", "송신 준비가 됐는지"는 SR로 확인하고 DR을 만진다.

나머지 register들은 USART 설정용 — 보레이트, 문자당 비트 수 등.

### Base Address — MCU에 USART 여러 개

이 register들을 코드로 다루려면 한 가지 더 필요하다: **각 USART의 Base Address**.
- MCU에 USART가 여러 개라서 각각의 base가 다르다.
- 보통 MCU **data sheet** 또는 **reference manual**에서 찾을 수 있다 (강사 표현으로는 이 MCU의 경우 양쪽 다 있음).

> **주의**
> 이 MCU의 USART 번호가 **1, 2, 6**으로 좀 이상하다.
> 강사 표현: **"the numbering of these usarts is sort of odd — one, two, and six."** 같은 family의 다른 MCU들까지 보면 말이 될 수도 있지만, 어쨌든 이 MCU에는 그 세 개가 있다.

---

## 6. STM32 전체 메모리 맵 (4GB)

> **이미지 필요**
> Memory map 전체 다이어그램 — 3컬럼 구조. 왼쪽: 전체 4GB 주소 공간, 가운데: 일부 확대, 오른쪽: peripheral register 영역 상세.
> - 출처: STM32F4 데이터시트의 memory map 페이지, 강의 10분 30초~ 슬라이드
> - 대체안: RM0090 Figure 17 (Memory map)

강사 표현: **"this diagram which comes from the data sheet is a little intimidating so we'll take it a piece at a time."** 압도되지 말고 조각으로 나눠 본다.

### 주소 공간 크기

- MCU는 **32비트 주소**를 쓴다.
- 따라서 메모리 맵 전체 크기 = `2^32` 바이트 = **4 GB**.
- 16진수로 최대 주소 = `0xFFFFFFFF` ("eight Fs").
- 메모리 맵은 `0x00000000`에서 시작해 `0xFFFFFFFF`까지.

### 주요 영역 (두 번째 컬럼 — 확대 부분)

| 영역 | 시작 주소 | 설명 |
| --- | --- | --- |
| **Flash** | `0x0800 0000` | 프로그램 코드 |
| **System Memory** | `0x1FFF F000` | MCU 제조사가 구워놓은 built-in software. 예: 시리얼 링크로 Flash를 프로그래밍할 수 있게 해주는 부트로더. (강사가 써본 SoC 중 절반 정도가 이런 built-in software를 가지고 있었다고 함. 이 강의에서는 다루지 않음.) |
| **SRAM** | `0x2000 0000` | 실행 중 변수 등이 들어가는 실제 메모리 |
| **Peripheral Registers** | `0x4000 0000` 영역 | MMIO 대상인 주변장치 레지스터 (3번째 컬럼 큰 흰색 블록들) |

---

## 7. Reset Vector & 인터럽트 벡터 테이블

메모리 맵에서 가장 특별한 영역.

### Vector라는 용어
- **vector = "어떤 코드의 주소"의 fancy한 이름.** 그 코드를 가리키는 포인터라고 보면 된다.

### Reset Vector
- **MCU가 전원 켜진 직후 가장 먼저 실행할 코드의 주소**를 담는 메모리 위치.
- 이 MCU의 경우 Reset Vector는 **주소 `0x00000004`**에 저장된다 (메모리 맵 거의 바닥).

### Interrupt Vector Table
- Reset Vector 바로 다음에 위치.
- **모든 인터럽트 종류마다 그 인터럽트를 처리할 코드(핸들러)의 주소가 들어있다.**
- 인터럽트가 발생하면 MCU는 해당 슬롯의 주소를 가져와 그 핸들러로 점프한다.

### 주소 `0x0`에 Flash가 보이는 이유 — Aliasing

- 이 MCU에는 "주소 0에 어떤 메모리를 보이게 할지" 결정하는 **advanced feature**가 있다 (강의에서는 다루지 않음).
- **이 강의에서는 단순히 Flash가 주소 0에 나타난다고 가정**한다.
- 그래서 Flash가 두 주소에서 동시에 보인다:
  - `0x00000000` (Reset Vector가 여기 있어서 부팅 시 접근)
  - `0x08000000` (Flash의 "원래" 주소)
- 강사 표현: **"don't worry — this is an easy thing to do in hardware design. The same flash memory is accessed regardless of which address range you are using."** 즉 *같은* Flash가 두 주소 범위 모두에서 동일하게 접근된다 (하드웨어가 alias를 만들어줌).

---

## 8. Peripheral 주소 상세와 Hard Fault 주의

> **이미지 필요**
> 메모리 맵 3번째 컬럼 확대 — GPIO 포트들, DMA, 타이머, SPI 버스, ADC, USART들의 주소.
> - 출처: 강의 13분 30초~ 슬라이드, RM0090 peripheral memory map
> - 대체안: 데이터시트의 Table — Memory map and register boundary addresses

### GPIO Port A 예시
- 시작 주소 `0x4002 0000`.
- 들어있는 register 종류:
  - **핀 매핑용:** 각 핀이 무엇에 연결될지 설정 (alternate function 등)
  - **전기적 설정용:** pull-up / pull-down 저항 삽입 여부
  - **읽기/쓰기용:** 실제 GPIO로 쓸 핀의 값을 0/1로 읽거나 쓰기

이어서 DMA, 타이머, SPI 버스, ADC, USART들이 차례로 배치된다.

### 주소 공간이 헤프게 할당되는 이유

USART 예시로 직접 계산:
- USART register는 **7개**, 각 **4바이트** → 실제 사용 = **28 바이트**.
- 그런데 이 표에서는 USART 하나당 **1024 바이트**가 할당돼 있다.
- 즉 1024 − 28 = **996 바이트가 사용되지 않음**.

**왜 이렇게 헤프게?**
- 강사 표현: **"there's plenty of address space — 4 gigabytes — and it is easier in hardware design to allocate larger blocks to peripherals."**
- 4GB 주소 공간이 워낙 넉넉하니, 하드웨어 설계 편의상 큰 블록을 통째로 잘라 주는 게 낫다.

### 할당되지 않은 주소를 건드리면? → Hard Fault

> **예외**
> 헤프게 할당된 영역 안에서 **실제 register가 없는 주소(unassigned address)에 접근하면 위험**하다.
> - 유효한 값을 얻지 못할 뿐 아니라,
> - **Hard Fault Interrupt가 발생해서 시스템이 뻗을 수 있다.**
> - 강사 마지막 경고: **"so be careful."**

---

## 참고 자료

- [Lesson 8. The MCU Memory Map and Memory Mapped I/O (YouTube)](https://www.youtube.com/watch?v=bWMsBXNAOAE)
- STM32F4 Reference Manual (RM0090) — Memory map 챕터, USART 챕터
- STM32F4 데이터시트 — Memory map 및 register boundary addresses 테이블
- Wikipedia — *Address space* (강사가 사전 지식 부족할 경우 추천)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Memory Mapped I/O는 **주변장치 레지스터를 일반 메모리 주소처럼 매핑**해서, 메모리 접근 명령(load/store)만으로 I/O를 제어하는 방식이다.
- **왜 필요:** 메모리와 I/O를 통일된 주소 공간으로 다루면 전용 I/O 명령어(`IN`/`OUT`)를 따로 익힐 필요 없이 C 포인터·구조체로 직관적으로 하드웨어를 제어할 수 있다. 소프트웨어 설계가 단순해지는 "강력한 추상화"다.
- **동작:** STM32 같은 32비트 MCU는 `2^32` = 4GB 주소 공간을 Flash(`0x0800 0000`), SRAM(`0x2000 0000`), Peripheral(`0x4000 0000` 영역)으로 분할한다. Peripheral은 Base Address + 4의 배수 Offset으로 register를 가리키고, 이 구조가 C 구조체와 일대일로 매칭되어 포인터 캐스팅만으로 다룰 수 있다. Reset Vector는 주소 `0x0000 0004`에, 인터럽트 벡터 테이블은 그 뒤에 위치한다.
- **비교:** Intel 8085·x86이 지원하는 **separate I/O address space** 방식은 메모리와 I/O 주소가 완전히 분리돼 전용 명령어가 필요하다. 단, 그런 시스템에서도 MMIO를 함께 쓸 수 있다 — 양자택일이 아니다.
- **30초 통합 답변:**
  > Memory Mapped I/O는 주변장치 레지스터를 메모리 주소처럼 매핑해서 메모리 접근 명령만으로 I/O를 제어하는 방식입니다. STM32 같은 32비트 MCU는 4GB 주소 공간을 Flash, SRAM, Peripheral 영역으로 나누고, 주변장치는 Base Address에 4바이트 단위 Offset을 더해 레지스터에 접근합니다. 이 구조가 C 구조체와 정확히 매칭되어 포인터 캐스팅으로 직접 제어할 수 있고, 결과적으로 x86처럼 별도 I/O 명령어 없이 직관적인 코딩이 가능합니다. 다만 데이터시트상 한 주변장치에 1024바이트가 할당되어도 실제 사용은 28바이트뿐인 경우가 많고, 비어있는 주소를 건드리면 Hard Fault가 발생할 수 있어 주의해야 합니다.
