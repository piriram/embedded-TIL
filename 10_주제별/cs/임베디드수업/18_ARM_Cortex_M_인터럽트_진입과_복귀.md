# ARM Cortex-M 인터럽트 진입과 복귀 — Interrupts Part 3

**원본 강의:** [#18 interrupts Part-3: How interrupts work on ARM Cortex-M? (YouTube)](https://www.youtube.com/watch?v=O0Z1D6p7J5A)

이 강의는 ARM Cortex-M에서 interrupt handler가 특별한 문법이나 별도의 `IRET` 명령 없이도 일반 C 함수처럼 작성될 수 있는 이유를 설명한다. 핵심은 Cortex-M의 **exception entry**가 일반 함수 호출 규약인 AAPCS(ARM Application Procedure Call Standard)와 역할을 나누어 register를 저장하고, 복귀할 때는 `LR`에 넣어 둔 특수 값(`EXC_RETURN`)을 `BX LR`로 실행한다는 점이다.

---

## 1. 이번 강의의 질문 — 왜 ISR이 일반 C 함수인가

이전 강의에서 본 MSP430은 일반 함수와 interrupt handler를 명확히 다르게 취급한다.

| 구분 | 일반 함수 | MSP430 interrupt handler |
| --- | --- | --- |
| 복귀 명령 | `RET` | `RETI` |
| 저장 register | 호출 규약이 요구하는 범위 | interrupt 복귀에 필요한 더 많은 범위 |

`RET`와 `RETI`는 stack에서 꺼내는 register 구성이 다르므로 서로 다른 machine instruction이다. 예를 들어 동일한 본문을 가진 일반 함수와 timer handler를 비교해도, MSP430 handler 쪽은 `R12`~`R15`를 추가로 저장해야 했다.

그렇다면 Cortex-M에서는 다음 두 요구를 어떻게 만족하면서 handler를 보통 C 함수로 만들 수 있을까?

1. Interrupt가 선점한 지점으로 정확히 돌아갈 수 있도록 충분한 CPU 상태를 저장해야 한다.
2. 일반 함수의 표준 return 동작만으로 interrupt 복귀를 수행해야 한다.

답은 **하드웨어가 exception entry에서 저장하는 register와, C 컴파일러가 AAPCS에 따라 handler 본문에서 저장하는 register가 서로 보완된다**는 데 있다.

---

## 2. 디버거로 SysTick interrupt를 원하는 instruction 뒤에 발생시키기

Exception stack frame을 관찰하려면 SysTick이 정확히 어느 instruction 뒤에서 CPU를 선점하는지 제어해야 한다. MSP430에서는 timer의 현재 counter를 limit보다 1 작은 값으로 바꿔 다음 clock cycle에 timeout을 만들 수 있었다. 그러나 Cortex-M SysTick의 `STCURRENT`는 **write-clear register**다. 어떤 값을 쓰더라도 counter만 clear하며 interrupt를 발생시키지 않는다.

대신 TivaC datasheet가 설명하는 `ICSR`(Interrupt Control and State Register)의 pending bit를 사용한다. `PENDSTSET`은 bit 26이며, 1로 설정하면 SysTick interrupt를 pending 상태로 만든다.

```text
ICSR.PENDSTSET = 1
        ↓
다음 interrupt 검사 시점에 SysTick interrupt request가 pending
        ↓
CPU가 현재 instruction을 끝낸 뒤 exception entry 또는 다음 일반 instruction 실행
```

실습 순서는 다음과 같다.

1. `while (1)` loop 첫 부분에 breakpoint를 걸고 실행을 멈춘다.
2. 바로 다음 `LDR.N` instruction에도 breakpoint를 건다.
3. `SysTick_Handler` 내부에도 breakpoint를 건다.
4. System Control Block의 `ICSR.PENDSTSET` bit를 1로 설정한다.
5. Single step이 아니라 프로그램을 free-run한다.

Single step을 쓰면 instruction마다 interrupt를 검사하는 정상적인 조건이 달라져 이 실험의 목적에 맞지 않는다. Free-run 결과 handler의 breakpoint에 도달하면, `MOVS`를 마친 직후 SysTick이 들어와 정상 흐름의 다음 `LDR.N` 대신 handler가 실행됐음을 확인할 수 있다.

> **주의**
> `PENDSTSET` 방식은 SysTick만을 위한 우회법이 아니다. Cortex-M은 각 interrupt source에 해당하는 pending bit를 제공하며, 대부분은 NVIC(Nested Vectored Interrupt Controller)에 있다. 디버거에서는 이를 이용해 특정 interrupt를 의도적으로 재현할 수 있다.

---

## 3. FPU 없는 기본 exception stack frame

먼저 project option에서 FPU를 `None`으로 설정하고 build한다. FPU가 있으면 floating-point state까지 stack에 저장되어 기본 원리를 보기 어려워진다.

Interrupt가 들어오기 전의 `SP`와 `SysTick_Handler` 안에서 멈춘 직후의 `SP`를 비교하면, FPU가 없는 경우 `SP`는 **4 byte word 8개만큼** 낮아진다. ARM stack은 낮은 주소 방향으로 자라므로, 이는 하드웨어가 exception entry에서 8-word stack frame을 자동으로 push했다는 뜻이다.

기본 exception frame에는 다음 상태가 저장된다.

| 저장 항목 | 의미 |
| --- | --- |
| `R0`~`R3` | 함수 인수와 caller-saved scratch register |
| `R12` | caller-saved scratch register |
| `LR` | 선점된 코드가 사용하던 link register 상태 |
| `PC` | interrupt가 끝난 뒤 돌아갈 instruction 주소 |
| `xPSR` | processor status 상태 |

예를 들어 PC slot에는 interrupt 이후 재개할 `while (1)` 안의 `LDR.N` 주소가 들어 있다. Datasheet의 exception stack frame 그림은 메모리를 높은 주소에서 낮은 주소 방향으로 표시할 수 있으므로, debugger의 memory view처럼 stack이 아래로 자라는 모습과 비교할 때는 방향을 뒤집어 읽어야 한다.

> **이미지 필요**
> FPU 없는 Cortex-M exception stack frame: `R0`~`R3`, `R12`, `LR`, `PC`, `xPSR`의 저장 순서와 interrupt 전후 `SP` 위치
> - 출처: TivaC datasheet의 “Exception Entry and Return”, 강의 05:39~07:33
> - 대체안: SysTick handler breakpoint에서 debugger의 Memory/Registers 창을 함께 캡처

---

## 4. AAPCS와 하드웨어 저장이 맞물리는 방식

Lesson 9에서 본 AAPCS는 함수 호출을 넘나들며 보존해야 하는 register를 정한 calling convention이다. 일반 C 함수는 자신이 `R4`~`R11`을 사용한다면 호출자에게 원래 값을 돌려주기 위해 stack에 저장했다가 복원한다.

Cortex-M의 exception entry는 그와 반대쪽 register group인 `R0`~`R3`, `R12`, `LR`, `PC`, `xPSR`을 하드웨어로 저장한다. 즉 일반 함수 호출에서 caller 측이 책임질 register 및 실행 재개 상태를 CPU가 자동으로 확보하고, handler를 컴파일한 C compiler는 평소와 동일하게 callee-saved register를 처리한다.

```text
Interrupt entry (Cortex-M hardware)
  R0~R3, R12, LR, PC, xPSR 저장
                 +
Handler 본문 (C compiler / AAPCS)
  필요할 때 R4~R11 저장·복원
                 ↓
선점 전 CPU 상태를 완성해 복원 가능
```

이것이 `void SysTick_Handler(void)` 같은 평범한 C 함수가 interrupt handler로 동작할 수 있는 이유다. AAPCS는 단순히 compiler별로 바꿀 수 있는 선택적 관례가 아니라, Cortex-M의 exception entry와 정확히 맞물려야 하므로 모든 compiler가 지켜야 하는 hard rule이 된다.

> 일반 C 함수는 caller/callee 사이의 약속으로 register를 보존한다. Cortex-M interrupt handler는 그 약속의 한쪽을 CPU hardware가 수행하기 때문에 같은 함수 규약을 그대로 사용할 수 있다.

---

## 5. `BX LR`가 interrupt return이 되는 원리 — `EXC_RETURN`

Handler를 instruction 단위로 따라가면, C 함수와 마찬가지로 끝에서 `BX LR`을 실행한다. 그런데 interrupt entry 직후 `LR`의 값은 일반 code address가 아니라 다음과 같은 특수 값이다.

```text
FPU 미사용 예: LR = 0xFFFFFFF9
```

`0xFFFFFFF9`는 code space의 유효한 일반 주소가 아니다. Cortex-M은 이 값을 PC에 load하는 상황을 특별히 해석한다. `BX LR`가 이 값으로 branch하려 하면, 하드웨어는 normal branch 대신 **exception return**을 수행한다.

```text
SysTick_Handler() 끝
        ↓
BX LR
        ↓  LR = 0xFFFFFFF9 (EXC_RETURN)
hardware가 exception return으로 해석
        ↓
stack frame pop, register 복원, preemption 지점의 PC로 복귀
```

그 결과 `SP`는 interrupt 직전 값으로 돌아가고, stack에 있던 register들도 선점 전 상태로 복원되며, `PC`는 원래 `while (1)` loop에서 중단했던 바로 다음 instruction으로 이동한다.

MSP430 같은 processor는 `IRET`/`RETI`처럼 **특별한 instruction**으로 interrupt return을 구분한다. Cortex-M은 `BX LR`이라는 표준 함수 return 경로에 `LR`의 **특별한 data 값**을 넣어 구분한다. Data 기반 방식은 여러 exception-return variant를 표현할 수 있어 더 유연하고 확장 가능하다.

> **주의**
> Handler 안에서 `LR`을 일반 함수의 return address처럼 해석하면 안 된다. Exception handler의 진입 직후 `LR`에는 code address가 아닌 `EXC_RETURN` 값이 들어 있으며, 이 값이 복원 방식과 복귀 context를 지정한다.

---

## 6. Handler mode, Thread mode, MSP와 PSP

Exception return 표에는 Cortex-M의 실행 상태와 stack pointer 관련 용어가 등장한다.

| 용어 | 의미 |
| --- | --- |
| Handler mode | interrupt나 fault 같은 exception을 처리하는 processor state |
| Thread mode | `main()`의 `while (1)`처럼 일반 code를 실행하는 state |
| MSP (Main Stack Pointer) | main stack을 가리키는 stack pointer |
| PSP (Process Stack Pointer) | process stack을 가리키는 stack pointer |
| Floating-point state | FPU가 활성화되어 FPU exception frame을 사용하는 상태 |

Cortex-M에는 `SP_main`과 `SP_process`라는 두 stack pointer가 있으며, CPU의 현재 내부 상태에 따라 `SP`로 보이는 register가 달라진다. 하나의 이름으로 보이는 register가 mode에 따라 서로 다른 실제 register를 가리키는 개념을 **register banking**이라고 한다.

지금은 기본 exception frame을 이해하는 데 MSP/PSP를 구별할 필요가 없지만, RTOS에서는 task마다 실행 context와 stack을 관리해야 하므로 이 구분이 중요해진다. `EXC_RETURN`의 여러 값은 Handler/Thread mode, MSP/PSP, FPU frame 사용 여부처럼 어떤 context로 어떤 stack frame을 복원할지 표현한다.

---

## 7. 8-byte stack alignment와 aligner word

Interrupt entry/exit은 register 여러 개를 빠르게 block transfer해야 하므로 stack frame의 시작 주소가 8-byte boundary에 맞는 것이 유리하다. Cortex-M은 exception entry 시 필요한 경우 **aligner word** 하나를 추가해 frame을 8-byte aligned 상태로 만든다.

강의 실험에서 정상적인 `SP`를 일부러 4 byte 낮춰 `0x3F4`로 만들면, 이 값은 8로 나누어떨어지지 않는다. Interrupt가 들어온 뒤 debugger memory view를 보면 8-register frame 외에 주소 `0x3F0`의 한 word가 건너뛰어져 있다. 이 slot이 aligner word다.

```text
interrupt 직전 SP = 0x3F4  (8-byte misaligned)
        ↓
aligner word 추가
        ↓
8-word 기본 exception frame 저장
        ↓
interrupt return 시 9-word 전체 제거
        ↓
SP = 0x3F4로 정확히 복귀
```

따라서 misaligned 상태에서는 총 9-word가 제거되지만, 원래 `SP`의 misalignment 자체도 보존된다. 실제 application code에서는 AAPCS가 **8-byte stack alignment**를 요구하고 compiler가 이를 보장하므로, 이런 상태는 정상적으로 발생해서는 안 된다.

> **예외**
> Aligner word는 항상 생기는 ninth register slot이 아니다. Exception entry 시 `SP` alignment가 필요한 조건에서만 하드웨어가 추가한다. RTOS처럼 stack을 직접 구성하는 코드에서는 이 규칙을 특히 신경 써야 한다.

---

## 8. FPU가 exception stack frame에 미치는 영향

FPU를 다시 활성화한 project를 build해 같은 실험을 하면 exception entry 직후 `SP` 변화가 훨씬 커진다.

```text
interrupt 직전 SP = 0x3F8
interrupt 진입 후 SP = 0x390
차이 = 0x68 byte = 104 byte = 26 words
```

기본 frame은 8개의 4-byte word이지만, FPU를 사용할 때는 floating-point storage를 포함한 **26-word FPU exception frame**이 사용된다. 즉 같은 exception 처리에서 stack에 필요한 frame 크기가 8 word에서 26 word로 커진다.

`LR`의 `EXC_RETURN` 값도 달라진다.

| 상태 | `LR`의 예 | 의미 |
| --- | --- | --- |
| FPU 미사용 | `0xFFFFFFF9` | 기본 exception frame을 사용한 복귀 |
| FPU 사용 | `0xFFFFFFE9` | FPU exception frame을 사용한 복귀 |

따라서 floating-point 연산을 쓰는 system은 ISR 자체가 FPU 계산을 하느냐와 별개로, FPU exception frame이 사용되는 조건을 고려하여 stack을 더 크게 잡아야 한다. 더 많은 상태를 push/pop해야 하므로 interrupt entry와 exit 시간도 길어진다.

> **주의**
> FPU 사용은 단지 계산 속도만의 문제가 아니다. Interrupt의 stack 사용량과 entry/exit latency까지 바꾼다. Stack sizing과 real-time 응답 시간을 산정할 때 FPU frame을 반드시 포함해야 한다.

---

## 9. Cortex-M interrupt entry/return 전체 흐름

```text
Thread mode의 일반 code 실행
        ↓
instruction 경계에서 pending interrupt 수락
        ↓
Hardware exception entry
  ├─ 기본 8-word frame 저장
  ├─ 필요하면 aligner word 추가
  ├─ FPU 사용 시 큰 FPU frame 사용
  └─ LR에 EXC_RETURN 기록
        ↓
Handler mode에서 일반 C handler 실행
  └─ compiler가 AAPCS에 따라 필요한 callee-saved register 관리
        ↓
handler의 표준 return: BX LR
        ↓
EXC_RETURN에 맞춰 hardware exception return
  ├─ frame pop
  ├─ register 및 SP 복원
  └─ 중단된 Thread mode instruction으로 재개
```

FPU가 없는 기본 case에서 Cortex-M의 interrupt entry와 exit은 각각 **12 clock cycles**가 걸린다. 8개 register를 push 또는 pop하는 일까지 포함한 시간으로, block transfer를 활용하는 hardware 설계 덕분에 빠르게 처리된다.

이 설계의 실무적 의미는 다음과 같다.

- ISR을 일반 C 함수로 작성할 수 있어 compiler와 source code가 단순해진다.
- Handler는 여전히 asynchronous하게 일반 code를 선점하므로, 다음 강의에서 다루는 race condition과 shared data 문제가 남는다.
- FPU 사용 여부, stack alignment, RTOS의 MSP/PSP 설정은 ISR의 stack 사용량과 latency에 직접 영향을 준다.

---

## 참고 자료

- [#18 interrupts Part-3: How interrupts work on ARM Cortex-M? (YouTube)](https://www.youtube.com/watch?v=O0Z1D6p7J5A)
- [state-machine.com/quickstart](https://state-machine.com/quickstart) — 강의 노트와 이전 lesson project 다운로드
- TivaC MCU Datasheet — “Exception Entry and Return”, `ICSR.PENDSTSET`, SysTick register 설명
- ARM Cortex-M documentation — exception stack frame, `EXC_RETURN`, MSP/PSP, FPU exception frame 설명
- 관련 노트: [16강 — 인터럽트의 개념과 동작 원리](./16_인터럽트의_개념과_동작원리.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Cortex-M interrupt는 exception entry hardware가 AAPCS의 caller-saved 상태와 복귀 정보를 stack에 저장하고, 일반 C handler가 표준 `BX LR` return으로 복귀할 수 있게 만든 메커니즘이다.
- **왜 필요:** Interrupt는 비동기적으로 일반 code를 선점하므로, 선점 전 register와 PC를 완전하게 보존해야 handler가 끝난 뒤 정확히 원래 instruction으로 돌아갈 수 있다.
- **동작:** FPU가 없으면 hardware가 `R0`~`R3`, `R12`, `LR`, `PC`, `xPSR`의 8-word frame을 저장한다. Handler는 AAPCS에 따라 필요한 `R4`~`R11`을 관리하고, `LR`의 `EXC_RETURN` 값을 대상으로 `BX LR`를 실행하면 hardware가 frame을 pop해 원래 context를 복원한다.
- **비교:** MSP430은 `RETI` 같은 전용 interrupt-return instruction을 쓰지만, Cortex-M은 `LR`의 특수 data 값으로 exception return을 선택하므로 handler가 일반 C 함수와 같은 return 경로를 사용한다.
- **30초 통합 답변:** Cortex-M에서는 interrupt entry hardware가 `R0`~`R3`, `R12`, `LR`, `PC`, `xPSR`을 자동 저장해 AAPCS가 요구하는 caller 쪽 보존을 맡습니다. Handler는 일반 C 함수처럼 필요한 callee-saved register만 compiler가 처리하고 마지막에 `BX LR`로 return합니다. 이때 LR의 `EXC_RETURN` 값이 일반 branch가 아니라 exception return을 지시해 stack frame을 복원하고 선점 지점으로 되돌아갑니다. MSP430의 `RETI`와 달리, Cortex-M은 특수 instruction 대신 특수 LR data를 사용한다는 차이가 있습니다.
