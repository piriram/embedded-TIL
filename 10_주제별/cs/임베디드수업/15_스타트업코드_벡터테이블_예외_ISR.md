# Startup Code Part 3 — 벡터 테이블, 예외, 인터럽트 핸들러

**원본 강의:** [#15 Startup Code Part-3: Vector table initialization, exception handlers, interrupt handlers (YouTube)](https://www.youtube.com/watch?v=42HbCf5cz5A)

Cortex-M은 reset과 exception 발생 시 실행할 code를 추측하지 않는다. CPU는 정해진 위치의 **vector table**에서 초기 stack pointer와 handler 주소를 읽어 실행한다. 이 강의는 vector table을 linker symbol·function address로 초기화하고, 예외 handler의 failure policy와 fault injection까지 검증하는 startup code 완성 단계다.

---

## 1. vector table의 첫 두 항목

Cortex-M vector table의 가장 앞 두 word는 일반 ISR 주소 목록과 다르게 해석된다.

| offset | 내용 | CPU 동작 |
| --- | --- | --- |
| `0x00` | initial Main Stack Pointer(MSP) 값 | reset 직후 SP에 적재 |
| `0x04` | `Reset_Handler` 주소 | reset 직후 PC에 적재하여 실행 시작 |
| 이후 | NMI, HardFault, SysTick, peripheral IRQ handler 주소 | 대응 exception/IRQ 발생 시 해당 주소로 분기 |

따라서 첫 entry는 **함수 포인터가 아니라 stack의 최상단 주소**다. Cortex-M stack은 일반적으로 높은 SRAM 주소에서 낮은 주소 쪽으로 자라므로, startup vector에는 stack section의 끝(limit) 주소를 넣는다.

```text
reset
  ├─ vector[0] → MSP = stack top
  └─ vector[1] → PC  = Reset_Handler
                          └─ C runtime 초기화 → main()
```

---

## 2. linker symbol을 C에서 주소로 쓰기

stack top의 실제 주소는 linker가 section 배치가 끝난 뒤에 결정한다. source code에서 임의 숫자로 고정하면 linker script의 stack size와 어긋날 수 있다. 그래서 linker가 제공하는 section symbol을 `extern` declaration으로 compiler에 알리고 그 주소를 사용한다.

```c
extern unsigned char __StackTop;  /* linker가 정의한 symbol: 저장공간을 새로 만들지 않음 */

/* 실제 table 선언 방식은 startup file·compiler·linker script에 따른다. */
```

이 강의의 IAR 환경은 `CSTACK$$Limit` 같은 section limit symbol을 사용한다. `extern`은 “다른 translation unit 또는 linker가 정의한 symbol”을 선언할 뿐, 새 변수를 정의하지 않는다. type은 여기서 값을 읽기 위한 것이 아니라 **주소를 얻기 위한 표기**에 가깝다.

> **주의**
> object pointer와 function pointer를 정수 배열에 cast해 섞는 vector table 선언은 해당 embedded toolchain·ABI에 맞춘 startup code 기법이다. ISO C의 모든 구현에 그대로 portable한 일반 container로 간주하면 안 된다. vendor CMSIS startup template와 linker script를 기준으로 한다.

---

## 3. reset handler와 함수 주소

`Reset_Handler`는 reset 뒤 PC가 가리키는 startup entry point다. function name에 `()`를 붙이지 않으면 호출이 아니라 주소를 가리킨다.

```c
void Reset_Handler(void);

/* 개념적으로 vector entry에는 &Reset_Handler가 들어간다. */
```

`Reset_Handler`는 보통 `.data` 초기값 복사, `.bss` zero-initialization, C library 초기화 등을 거쳐 `main()`을 호출한다. 이 강의에서는 기존 IAR runtime startup entry(`__iar_program_start`)를 custom vector table의 reset entry로 재사용한다.

함수 포인터의 정확한 선언·callback 설계는 [함수 포인터와 콜백](../../c언어/함수포인터와_콜백.md)을 참고한다.

---

## 4. 예외와 IRQ: slot 순서는 ABI다

Reset 뒤에는 NMI, HardFault, MemManage, BusFault, UsageFault, SVC, PendSV, SysTick 같은 Cortex-M core exception entry가 있고, 이어서 MCU별 peripheral IRQ entry가 있다. datasheet와 CMSIS header의 표에 **reserved slot**도 포함된다.

vector table은 handler 이름을 찾는 dictionary가 아니라 index가 의미를 갖는 address array다. 항목 하나를 빼거나 reserved slot을 건너뛰면 이후 모든 handler 주소가 한 칸씩 밀려 전혀 다른 interrupt에서 잘못된 code가 실행된다.

```text
IRQ 발생 → CPU가 exception number로 slot 계산
        → vector table의 해당 word에서 handler 주소 읽기
        → 현재 실행을 exception stack frame으로 보존하고 handler 실행
        → exception return으로 선점 지점 복귀
```

이 “주소 table에서 handler를 dispatch한다”는 점은 callback과 닮았지만, IRQ 발생·stack frame 저장·복귀를 hardware가 수행한다는 점이 다르다.

---

## 5. fault handler와 unused handler의 역할 분리

HardFault 같은 fault는 memory corruption·invalid instruction·stack 문제처럼 계속 실행하면 위험한 상태를 뜻할 수 있다. 단순 `while (1)`은 debugger에는 편하지만, production device를 영구 정지 상태로 만들 수 있다.

강의의 방향은 모든 unrecoverable fault를 공통 `assert_failed()`로 모아 다음을 수행할 여지를 만드는 것이다.

- fault 종류·file·line·register snapshot을 가능한 범위에서 기록
- 안전 출력 끄기 등 damage control
- watchdog 또는 `NVIC_SystemReset()`으로 controlled reset

반면 SVC·PendSV·SysTick처럼 project에 따라 구현될 수도 있는 handler에는 **weak alias**를 둔다. user가 실제 handler를 정의하면 그 strong definition이 선택되고, 정의하지 않으면 `Unused_Handler` 같은 default handler가 선택된다. CMSIS가 정한 표준 handler 이름을 쓰는 이유도 RTOS·vendor library가 같은 symbol을 기대하기 때문이다.

---

## 6. 손상된 stack에서 fault를 처리할 때

stack overflow 때문에 fault가 난 경우, 일반 C function prologue가 stack에 register를 push하는 동작 자체가 또 fault를 낼 수 있다. 그러면 HardFault handler에 진입하자마자 다시 fault에 들어가 implicit infinite loop가 된다.

이 강의의 IAR 해법은 handler와 `assert_failed()`를 `__stackless`로 선언해 stack을 사용하지 않도록 만드는 것이다. 다른 compiler에서는 naked handler, assembly wrapper, dedicated emergency stack 등 다른 기법을 쓸 수 있다. 핵심 원칙은 같다.

> **예외**
> `naked`·`stackless` function은 compiler의 일반 calling convention을 깨기 쉬운 고급 기능이다. C code를 마음대로 넣지 말고 target compiler의 ABI·manual·vendor startup code에 맞춰 최소한으로 사용한다.

---

## 7. fault injection으로 startup code를 실제 검증한다

fault handler는 정상 동작 중 거의 실행되지 않으므로 “빌드됐다”는 사실만으로 충분하지 않다. 강의는 debugger에서 SP를 RAM 시작 주소 근처로 바꾼 뒤 function prologue의 push를 single-step하여 의도적으로 stack overflow/HardFault를 만든다.

검증할 항목은 다음과 같다.

1. 예상한 HardFault handler가 vector table slot에서 선택되는가?
2. handler 진입 자체가 stack push 때문에 재-fault하지 않는가?
3. common error handler가 기록·damage control·reset policy를 수행하는가?
4. reset 뒤 vector[0]의 stack top과 vector[1]의 reset entry가 올바르게 다시 동작하는가?
5. weak default 대신 project의 `SysTick_Handler`처럼 strong handler가 선택되는가?

드물게 실행되는 code일수록 의도적으로 오류를 주입해 test해야 한다는 점이 이 강의의 중요한 engineering lesson이다.

---

## 8. 전경-배경 구조와 이어 보기

vector table은 ISR이 **어디에서 시작하는지**를 정하고, 전경-배경 architecture는 ISR이 background를 **언제 선점하고 어떻게 복귀하는지**를 설명한다. ISR은 필요한 hardware event만 짧게 포착하고, 길거나 blocking인 처리는 flag·event를 통해 background 또는 RTOS task로 전달한다.

---

## 참고 자료

- [#15 Startup Code Part-3: Vector table initialization, exception handlers, interrupt handlers (YouTube)](https://www.youtube.com/watch?v=42HbCf5cz5A)
- [MCU Memory Map & Memory Mapped I/O](./8_MCU_메모리맵과_MMIO.md) — Reset vector·Flash aliasing 기초
- [인터럽트의 개념과 동작 원리](./16_인터럽트의_개념과_동작원리.md) — exception/IRQ 발생과 ISR 실행
- [ARM Cortex-M 인터럽트 진입과 복귀](./18_ARM_Cortex_M_인터럽트_진입과_복귀.md) — exception stack frame·`EXC_RETURN`
- [전경-배경 아키텍처](./21_전경_배경_아키텍처_슈퍼루프.md) — ISR과 main loop의 역할 분리

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Cortex-M vector table은 reset과 각 exception/IRQ에서 CPU가 읽을 초기 stack pointer와 handler 주소의 정해진 순서 배열이다.
- **왜 필요:** CPU는 reset 뒤 실행할 code와 interrupt마다 실행할 handler를 알아야 하며, slot 순서가 틀리면 잘못된 handler 실행·부팅 실패가 생긴다.
- **동작:** vector[0]의 stack top을 MSP에, vector[1]의 `Reset_Handler` 주소를 PC에 넣는다. 이후 exception number에 맞는 slot의 handler 주소로 hardware가 분기하고, handler 종료 뒤 원래 code로 복귀한다.
- **비교:** 일반 callback은 software가 함수 포인터를 호출하지만, ISR dispatch는 hardware가 vector table을 읽어 현재 실행을 선점한다. fault handler는 stack이 손상됐을 수 있어 일반 handler보다 보수적으로 설계해야 한다.
- **30초 통합 답변:**
  > Cortex-M의 vector table은 CPU가 reset과 interrupt에서 실행할 주소를 담은 고정 순서 table입니다. 첫 항목은 함수 주소가 아니라 initial stack pointer이고, 두 번째 항목은 Reset Handler 주소라서 reset 뒤 SP와 PC가 각각 설정됩니다. 이후 exception number에 맞는 slot에서 ISR 주소를 읽어 hardware가 handler로 분기하고, 끝나면 선점 지점으로 복귀합니다. reserved slot까지 정확히 유지해야 하며, HardFault처럼 stack 손상 가능성이 있는 handler는 무한 loop만 두기보다 기록과 controlled reset을 포함해 fault injection으로 검증해야 합니다.
