# STM32 GPIO BSRR — RMW 없이 핀 Set/Reset하기

**주제:** `GPIOx_ODR`의 read-modify-write(RMW) 위험을 이해하고, STM32 `GPIOx_BSRR`로 개별 핀을 atomic하게 set/reset하기
**적용 MCU:** STM32F767 계열을 기준으로 설명. 실제 bit 정의와 지원 여부는 사용하는 MCU의 reference manual·CMSIS 헤더를 확인한다.
**원본 강의:** [Blink LED using GPIO BSRR Register | STM32 Bare Metal Programming Explained — YouTube](https://www.youtube.com/watch?v=yVE-KrwpL7I)

---

## 1. ODR의 `|=`와 `&= ~`는 한 번의 동작이 아니다

다음 코드는 보기에 "PD3의 bit만 set/clear"하는 것 같지만, C 대입 연산은 보통 세 단계로 전개된다.

```c
GPIOD->ODR |=  LED_MASK;    // read → OR → write
GPIOD->ODR &= ~LED_MASK;    // read → AND → write
```

`ODR`은 read/write 레지스터다. 따라서 CPU는 먼저 ODR의 현재값을 **읽고**, RAM/레지스터에서 mask 연산을 한 뒤, 계산 결과를 ODR에 **다시 쓴다**. 이것을 RMW(read-modify-write)라고 한다.

문제는 read와 write 사이에 인터럽트(ISR), 다른 태스크 또는 하드웨어가 같은 ODR의 다른 비트를 바꾸면 발생한다. CPU가 먼저 읽어 둔 오래된 값으로 마지막 write를 하면, 그 사이의 갱신이 사라질 수 있다.

```text
초기 ODR = 0b0000
main: ODR 읽음                  → 0b0000
ISR:  bit 1 set 완료            → ODR = 0b0010
main: bit 3을 set한 옛값을 씀   → ODR = 0b1000  (ISR의 bit 1 갱신 유실)
```

> **주의**
> `volatile`은 컴파일러가 레지스터 access를 생략·합치지 못하게 할 뿐, read와 write 사이를 잠그지 않는다. 따라서 `volatile`만으로 RMW 경쟁 조건은 해결되지 않는다.

---

## 2. BSRR의 32비트 write 명령 형식

STM32F767의 `GPIOx_BSRR`(bit set/reset register)은 ODR의 각 bit를 명령식으로 바꾸는 write-only 레지스터다. BSRR에 **0을 쓰는 bit는 아무 일도 하지 않고**, 1을 쓰는 위치만 ODR에 반영된다.

| BSRR bit 위치 | 이름 | 1을 write했을 때 |
| --- | --- | --- |
| `[15:0]` | `BSy` (bit set) | 해당 `ODRy`를 1로 set |
| `[31:16]` | `BRy` (bit reset) | 해당 `ODRy`를 0으로 reset |

예를 들어 핀 번호가 `3`이면 lower half의 bit 3은 "ODR3을 1로", upper half의 bit 19(= 3 + 16)는 "ODR3을 0으로" 만든다.

```c
#define LED_PIN   3U
#define LED_MASK  (1U << LED_PIN)

GPIOD->BSRR = LED_MASK;            // ODR bit 3 set: GPIO 출력 High
GPIOD->BSRR = (LED_MASK << 16U);   // ODR bit 3 reset: GPIO 출력 Low
```

여기서 `=`가 핵심이다. BSRR 자체를 읽어 현재 상태와 합치지 않고, 원하는 동작을 **한 번 write**한다. 그 write가 ODR의 해당 bit만 바꾸므로 다른 bit의 값은 보존된다.

> **주의**
> `GPIOx_BSRR |= mask` 또는 `&= ~mask`는 쓰지 않는다. BSRR은 상태 저장소가 아니라 명령 레지스터이며, 읽어 수정할 이유가 없다. `GPIOx_BSRR = mask`처럼 write만 한다.

---

## 3. active-low LED 예제

이 프로젝트의 F767 보드처럼 LED 애노드가 3.3 V, 캐소드가 GPIO 핀에 연결된 active-low 구성에서는 핀 Low가 LED ON이다. 따라서 PD3을 BSRR로 제어하면 다음과 같다.

```c
#define FAULT_LED_PIN   3U
#define FAULT_LED_MASK  (1U << FAULT_LED_PIN)

static inline void fault_led_on(void)
{
    GPIOD->BSRR = FAULT_LED_MASK << 16U;  // PD3 = Low → LED ON
}

static inline void fault_led_off(void)
{
    GPIOD->BSRR = FAULT_LED_MASK;         // PD3 = High → LED OFF
}
```

LED가 active-high인지 active-low인지는 MCU가 아니라 **회로 연결**이 정한다. 회로도에서 LED의 애노드/캐소드와 GPIO 연결을 확인한 뒤 함수 이름과 실제 BSRR 동작을 맞춘다.

---

## 4. 여러 핀을 같은 순간에 갱신하기

BSRR 한 번의 32-bit write에는 set할 핀과 reset할 핀을 함께 넣을 수 있다. 예를 들어 PA0·PA2를 High로, PA1을 Low로 바꾸려면 다음처럼 쓴다.

```c
#define SET_MASK    ((1U << 0U) | (1U << 2U))
#define RESET_MASK  (1U << 1U)

GPIOA->BSRR = SET_MASK | (RESET_MASK << 16U);
```

여러 ODR bit를 각각 RMW하는 것보다 pin 사이의 갱신 간격이 없고, 인터럽트가 중간 상태를 끼워 넣을 수 없다. 같은 pin을 set와 reset mask 양쪽에 동시에 넣는 것은 피한다. F767 reference manual에서는 같은 bit의 set와 reset이 동시에 요청되면 set가 우선한다고 설명하지만, 의도를 숨기는 코드가 되므로 mask가 서로 겹치지 않게 만드는 편이 낫다.

---

## 5. BSRR이 보장하는 범위와 보장하지 않는 범위

BSRR은 **GPIO ODR bit update 하나**를 RMW 없이 atomic하게 만든다. 그래서 ISR이 다른 GPIO bit를 바꾸는 상황에서 출력 latch 갱신이 유실되는 문제를 해결한다. 하지만 다음까지 자동으로 해결하지는 않는다.

- 두 태스크가 **같은 pin의 의미**를 서로 다르게 제어하면 마지막 write가 이긴다. pin 소유권을 한 모듈로 정하거나 동기화해야 한다.
- pin의 **현재 상태를 읽어서 반전(toggle)** 하는 작업은 BSRR만으로 할 수 없다. `ODR ^= mask`는 다시 RMW다. 필요하면 소프트웨어 상태를 단일 소유자가 관리하거나, timer hardware toggle 기능을 사용한다.
- 여러 레지스터 설정(`MODER`, `PUPDR`, clock enable 등)을 하나의 일관된 transaction으로 묶어 주지는 않는다. 초기화 순서와 필요시 critical section은 별도로 설계한다.

즉 BSRR은 "출력 상태 변경"에는 기본 선택지지만, 동시성 설계 전체를 대신하는 만능 lock은 아니다.

---

## 6. ODR와 BSRR 선택 기준

| 목적 | 권장 접근 | 이유 |
| --- | --- | --- |
| 출력 latch 전체 값을 의도적으로 교체 | `GPIOx->ODR = value` | 전체값 write가 목적일 때 명확 |
| 한 pin 또는 여러 선택 pin을 set/reset | `GPIOx->BSRR = mask` | RMW 없이 atomic bit update |
| 출력 상태 확인 | `GPIOx->ODR` read | BSRR은 상태를 보관하지 않는 write-only 명령 레지스터 |
| pin toggle | 단일 소유 상태 관리 또는 timer toggle | `ODR ^= mask`의 RMW 위험을 인지해야 함 |

> **예외**
> STM32 제품군과 오래된 CMSIS 헤더에는 `BSRRL`/`BSRRH` 또는 별도 `BRR`처럼 표기된 variant가 있을 수 있다. 이 노트의 `GPIOx->BSRR` 32-bit 방식은 STM32F767 reference manual 기준이다. 다른 칩으로 코드를 복사할 때는 해당 칩의 register map과 device header를 먼저 확인한다.

---

## 참고 자료

- [Blink LED using GPIO BSRR Register | STM32 Bare Metal Programming Explained — YouTube](https://www.youtube.com/watch?v=yVE-KrwpL7I)
- [STM32F765xx/F767xx/F768Ax/F769xx Reference Manual (RM0390) — STMicroelectronics](https://www.st.com/resource/en/reference_manual/dm00135183-stm32f765xx-stm32f767xx-stm32f768ax-and-stm32f769xx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) — General-purpose I/Os, `GPIOx_BSRR`
- 관련: [GPIO 출력과 LED 제어](./1_GPIO출력과_LED제어.md), [비트 연산자와 비트 마스크](../../c언어/040_비트연산자.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** STM32 `GPIOx_BSRR`은 ODR의 선택 bit를 한 번의 write로 set 또는 reset하는 atomic bit set/reset 레지스터다.
- **왜 필요:** `ODR |= mask`, `ODR &= ~mask`는 read-modify-write이므로 read와 write 사이에 ISR 등이 ODR을 바꾸면 그 갱신이 유실될 수 있다.
- **동작:** BSRR 하위 16비트의 1은 대응 ODR bit를 set하고, 상위 16비트의 1은 대응 ODR bit를 reset한다. 그래서 `GPIOx->BSRR = 1U << pin`으로 High, `GPIOx->BSRR = 1U << (pin + 16U)`으로 Low를 만든다.
- **비교:** ODR은 현재 출력 latch 값을 읽고 전체값을 쓸 수 있는 상태 레지스터이고, BSRR은 읽어 수정하지 않고 선택 bit 변경을 명령하는 write-only 레지스터다.
- **30초 통합 답변:**
  > STM32 GPIO에서 `ODR |= mask`나 `ODR &= ~mask`는 레지스터를 읽고 수정한 뒤 다시 쓰는 RMW라서, 그 사이 ISR이 다른 bit를 갱신하면 마지막 write가 그 변경을 덮어쓸 수 있습니다. 그래서 한두 핀을 변경할 때는 BSRR을 사용합니다. BSRR의 하위 16비트에 1을 쓰면 해당 ODR bit가 set되고, 상위 16비트에 1을 쓰면 reset됩니다. 즉 `GPIOx->BSRR = 1U << pin`은 High, `GPIOx->BSRR = 1U << (pin + 16U)`은 Low를 한 번의 write로 처리합니다. 다만 BSRR은 같은 pin을 여러 태스크가 제어하는 정책 문제나 toggle의 상태 읽기 문제까지 해결하지는 않으므로 pin 소유권도 함께 설계해야 합니다.
