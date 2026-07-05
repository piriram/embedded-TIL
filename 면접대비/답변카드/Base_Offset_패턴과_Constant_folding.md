# Base + Offset 패턴 + Constant folding

> 출처: `붙여넣은 마크다운(1)(7).md`
> 최종 갱신: 확인 불가

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

Base + Offset 패턴은 **하드웨어 레지스터 주소를 기준 주소인 base와 레지스터별 offset으로 나눠 표현하는 방식**입니다. 주로 MCU 데이터시트의 메모리 맵을 코드에 그대로 반영하기 위해 사용하며, 내부적으로는 `GPIOF_BASE + 0x3FC` 같은 상수식을 컴파일러가 컴파일 타임에 미리 계산하는 방식으로 동작합니다. 주소를 직접 하드코딩하는 방식과 비교하면 가독성과 유지보수성이 좋고, constant folding 덕분에 런타임 덧셈 비용이 없다는 점이 가장 중요합니다. 실제로는 `GPIO_PORTF_DATA`가 최종적으로 `0x400253FC` 주소 접근으로 접히고, 어셈블리에서 `ldr r0, =0x400253FC`처럼 완성된 주소가 바로 로드되는 것으로 확인할 수 있습니다.

---

## 한 줄 정의

Base + Offset 패턴은 **공통 base address를 한 번 정의하고, 각 레지스터를 base로부터의 offset으로 표현하는 주소 정의 방식**이다.

핵심 특성은 **가독성을 높이면서도 컴파일 타임 상수 계산으로 런타임 비용이 없다는 것**이다.

## 왜 필요한가

MCU 데이터시트의 레지스터 주소는 보통 다음 구조로 설명된다.

```text
Peripheral base address + Register offset
```

예를 들어 GPIO Port F의 기준 주소가 `0x40025000`이고, Data register의 offset이 `0x3FC`라면 최종 주소는 다음과 같다.

```text
0x40025000 + 0x3FC = 0x400253FC
```

주소를 매번 완성된 숫자로 직접 쓰면 다음 문제가 생긴다.

```c
#define GPIO_PORTF_DATA  (*((unsigned int *)0x400253FC))
#define GPIO_PORTF_DIR   (*((unsigned int *)0x40025400))
#define GPIO_PORTF_DEN   (*((unsigned int *)0x4002551C))
```

이 방식은 동작은 하지만, 코드만 봐서는 어떤 peripheral의 어떤 offset인지 파악하기 어렵다. 또한 base address가 바뀌거나 다른 포트로 옮길 때 수정 지점이 많아진다.

Base + Offset 패턴을 쓰면 데이터시트 구조가 코드에 그대로 드러난다.

```c
#define GPIOF_BASE       0x40025000

#define GPIO_PORTF_DIR   (*((unsigned int *)(GPIOF_BASE + 0x400)))
#define GPIO_PORTF_DEN   (*((unsigned int *)(GPIOF_BASE + 0x51C)))
#define GPIO_PORTF_DATA  (*((unsigned int *)(GPIOF_BASE + 0x3FC)))
```

## 동작 원리

`GPIOF_BASE`와 offset 값들은 모두 컴파일 타임에 알 수 있는 정수 상수다.

```c
#define GPIOF_BASE       0x40025000
#define GPIO_PORTF_DATA  (*((unsigned int *)(GPIOF_BASE + 0x3FC)))
```

사용 코드:

```c
GPIO_PORTF_DATA = 0x02;
```

전처리 후 개념적으로 다음 코드가 된다.

```c
(*((unsigned int *)(0x40025000 + 0x3FC))) = 0x02;
```

여기서 `0x40025000 + 0x3FC`는 런타임에 계산할 필요가 없다. 컴파일러가 컴파일 타임에 미리 계산할 수 있다.

계산 과정:

```text
0x40025000
+0x000003FC
-----------
 0x400253FC
```

따라서 최종적으로 컴파일러는 완성된 주소인 `0x400253FC`를 사용하는 기계어를 만들 수 있다.

강의 노트에서는 디버거에서 확인되는 증거로 다음 어셈블리 형태를 제시한다.

```asm
ldr r0, =0x400253FC
```

즉, CPU가 실행할 때 `0x40025000 + 0x3FC` 덧셈을 수행하는 것이 아니라, 이미 접힌 완성 주소 `0x400253FC`를 로드한다.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** MCU peripheral, MMIO register, SoC memory map처럼 주소가 `base + offset` 구조로 정의되는 하드웨어 레지스터를 코드로 옮길 때 사용한다.

```c
#define UART0_BASE       0x4000C000
#define UART0_DR         (*((unsigned int *)(UART0_BASE + 0x000)))
#define UART0_FR         (*((unsigned int *)(UART0_BASE + 0x018)))
```

- **피하는 경우:** base나 offset이 런타임에 바뀌는 일반 포인터 연산이라면 "컴파일 타임 constant folding으로 비용 0"이라고 말하면 안 된다. 이 주장은 base와 offset이 모두 컴파일 타임 상수일 때만 성립한다.

예를 들어 다음은 런타임 계산이 필요할 수 있다.

```c
unsigned int *base = get_base_address();
unsigned int offset = get_offset();

reg = *(base + offset);
```

여기서는 컴파일러가 최종 주소를 미리 하나의 상수로 접을 수 없다.

## 대표 예시

GPIO Port F 레지스터 정의:

```c
#define GPIOF_BASE       0x40025000

#define GPIO_PORTF_DIR   (*((unsigned int *)(GPIOF_BASE + 0x400)))
#define GPIO_PORTF_DEN   (*((unsigned int *)(GPIOF_BASE + 0x51C)))
#define GPIO_PORTF_DATA  (*((unsigned int *)(GPIOF_BASE + 0x3FC)))
```

`GPIO_PORTF_DATA`의 최종 주소 계산:

```text
GPIOF_BASE + 0x3FC
= 0x40025000 + 0x3FC
= 0x400253FC
```

사용 코드:

```c
GPIO_PORTF_DATA = 0x02;
```

전처리 후 개념적 형태:

```c
(*((unsigned int *)(0x40025000 + 0x3FC))) = 0x02;
```

컴파일러의 constant folding 후 개념적 형태:

```c
(*((unsigned int *)0x400253FC)) = 0x02;
```

어셈블리에서 확인되는 증거:

```asm
ldr r0, =0x400253FC
```

이 증거는 주소 덧셈이 실행 시간에 수행되지 않고, 컴파일 타임에 완성 주소로 접혔다는 뜻이다.

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| 완성 주소 직접 하드코딩 | 런타임 비용은 없지만, base와 offset 구조가 코드에 드러나지 않아 가독성과 유지보수성이 낮다. |
| Base + Offset 매크로 | 데이터시트 구조를 그대로 반영하면서도 컴파일 타임에 완성 주소로 접혀 런타임 비용이 없다. |
| 런타임 포인터 계산 | base나 offset이 변수이면 실행 중 덧셈이 필요할 수 있다. |
| 벤더 헤더 파일 | 보통 동일한 base + offset 구조를 이미 매크로로 제공하므로 직접 정의할 필요가 줄어든다. |

---

## 꼬리질문 예상

- **Q:** `GPIOF_BASE + 0x3FC`는 CPU가 매번 더하나요?
  **A:** 아니다. 둘 다 컴파일 타임 상수라면 컴파일러가 미리 `0x400253FC`로 계산한다. 이를 constant folding이라고 한다.

- **Q:** 런타임 비용 0이라고 말할 수 있는 조건은 무엇인가요?
  **A:** base와 offset이 모두 컴파일 타임에 결정되는 상수여야 한다. 런타임 변수라면 비용 0이라고 단정할 수 없다.

- **Q:** `ldr r0, =0x400253FC`는 무엇을 보여주나요?
  **A:** 완성된 주소 `0x400253FC`가 어셈블리 코드에 직접 들어갔다는 것을 보여준다. 즉 `0x40025000 + 0x3FC` 덧셈이 런타임 명령으로 남지 않았다는 증거다.

- **Q:** Base + Offset 패턴의 장점은 성능인가요?
  **A:** 주된 장점은 가독성과 유지보수성이다. 성능은 직접 완성 주소를 쓴 것과 같고, constant folding 덕분에 추가 런타임 비용이 없다.

---

## 자주 하는 오해

- **오해:** `GPIOF_BASE + 0x3FC`처럼 쓰면 CPU가 매번 덧셈하므로 느려진다.
  - **정확히는:** 둘 다 상수이면 컴파일러가 컴파일 타임에 `0x400253FC`로 미리 계산한다. 런타임 덧셈 비용은 없다.

- **오해:** Base + Offset은 단순히 보기 좋게 쓰는 스타일이다.
  - **정확히는:** 데이터시트의 메모리 맵 구조를 코드에 반영하는 방식이다. 어떤 peripheral의 어느 register offset인지 추적하기 쉬워진다.

- **오해:** 모든 포인터 주소 계산은 constant folding된다.
  - **정확히는:** 컴파일 타임에 값이 확정되는 상수식만 접힌다. 런타임에 결정되는 변수 기반 주소 계산은 접을 수 없다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-------------|
| 컴파일러가 알아서 최적화한다 | 컴파일 타임 상수식을 constant folding한다 |
| 주소를 더한다 | base address와 register offset을 더해 absolute address를 만든다 |
| 런타임 비용이 없다 | 상수식이 컴파일 타임에 접혀 실행 중 덧셈 명령이 남지 않는다 |
| `ldr`이 계산한다 | `ldr r0, =0x400253FC`는 이미 완성된 주소를 로드한다 |
| base를 쓰면 빠르다 | base + offset은 가독성 패턴이고, 성능은 constant folding 때문에 직접 주소 사용과 동일하다 |

---

## 키워드

`Base + Offset` `constant folding` `compile-time constant` `MMIO` `register offset` `base address` `absolute address` `GPIOF_BASE` `0x400253FC` `ldr r0, =0x400253FC`
