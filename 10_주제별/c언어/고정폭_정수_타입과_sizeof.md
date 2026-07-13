# 고정폭 정수 타입과 `sizeof`

**원본 강의:** [How to Find Memory Size & Limits of C Data Types | Microcontrollers (Video 08) (YouTube)](https://www.youtube.com/watch?v=vq7ghSMR2ts)

임베디드 코드에서 `char`, `short`, `int`, `long`의 크기를 당연하게 가정하면 PC와 MCU, 또는 MCU끼리도 이식성이 깨질 수 있다. 이 영상은 `stdint.h`의 고정폭 정수 타입, `sizeof`, 그리고 최솟값·최댓값 macro를 사용해 target에서 실제 폭과 범위를 확인하는 방법을 보여 준다.

---

## 1. C 기본 정수 타입의 크기는 구현이 정한다

C는 `char`, `short`, `int`, `long`, `long long` 사이의 최소 관계를 정하지만, `int`와 `long`이 반드시 몇 비트인지는 정하지 않는다. 예를 들어 `int`는 16비트일 수도 32비트일 수도 있다. 따라서 레지스터, CAN/UART frame, binary protocol처럼 **정확한 비트 폭이 인터페이스의 일부**인 코드에는 기본 타입보다 고정폭 타입을 우선한다.

```c
#include <stdint.h>

uint8_t  status;
int16_t  temperature_delta;
uint32_t peripheral_value;
int64_t  timestamp;
```

`uint32_t`는 “정확히 32비트 부호 없는 정수 타입을 이 구현이 제공한다”는 뜻이다. 이름의 `u`는 unsigned, 끝의 `_t`는 typedef로 정의한 타입이라는 관례를 나타낸다.

> **예외**
> 정확히 해당 폭을 표현할 수 없는 구현은 `uint32_t` 같은 exact-width typedef를 제공하지 않을 수 있다. 대부분의 현대 MCU toolchain에서는 제공하지만, portable library라면 `stdint.h`에 그 타입이 실제로 있는지와 API 요구 폭을 함께 확인한다.

---

## 2. `sizeof`로 target의 실제 크기 확인하기

`sizeof`는 타입 또는 객체가 차지하는 크기를 **바이트 단위**로 반환한다. 반환 타입은 `size_t`이며, 1바이트가 몇 비트인지는 `CHAR_BIT`으로 확인한다. 일반적인 MCU에서 `CHAR_BIT`는 8이지만 C 표준은 8비트만을 보장한다.

```c
#include <limits.h>
#include <stdint.h>
#include <stdio.h>

uint32_t value = 0;

printf("uint32_t: %zu bytes\n", sizeof value);
printf("byte width: %d bits\n", CHAR_BIT);
```

`sizeof`의 결과는 `size_t`이므로 `printf`에서는 `%zu`를 쓴다. `%llu`는 `unsigned long long` 전용이므로, `sizeof` 결과에 무조건 쓰는 형식 지정자가 아니다. compiler warning은 바로잡아야 할 타입 불일치 신호다.

---

## 3. 표현 가능한 범위는 `limits.h`와 `stdint.h`에서 읽는다

고정폭 타입의 범위 macro는 `stdint.h`에 있다. 예를 들어 `UINT8_MAX`는 8비트 unsigned 정수의 최댓값, `INT16_MIN`은 16비트 signed 정수의 최솟값이다.

```c
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

int16_t signed_value = INT16_MIN;
uint32_t unsigned_value = UINT32_MAX;

printf("int16_t minimum: %" PRId16 "\n", signed_value);
printf("uint32_t maximum: %" PRIu32 "\n", unsigned_value);
```

| 타입 | 범위 | 대표 용도 |
| --- | --- | --- |
| `uint8_t` | 0 ~ 255 | byte 단위 data, small flag |
| `int8_t` | -128 ~ 127 | 작은 signed offset |
| `uint16_t` | 0 ~ 65,535 | ADC raw value, protocol field |
| `int16_t` | -32,768 ~ 32,767 | signed sensor delta |
| `uint32_t` | 0 ~ 4,294,967,295 | 32-bit register value, tick counter |
| `int32_t` | -2,147,483,648 ~ 2,147,483,647 | signed 32-bit calculation |

format macro `PRId16`, `PRIu32`도 구현이 올바른 `printf` 형식 지정자를 선택하도록 돕는다. 단순한 firmware에서 debugger로 값을 볼 때는 덜 보일 수 있지만, log와 diagnostic code가 여러 toolchain에서 빌드된다면 유용하다.

---

## 4. “레지스터 폭 = C 기본 타입”이라는 가정을 피한다

STM32 같은 32비트 MCU에서 주변장치 register가 32비트로 정의되는 경우가 많아도, `long`이 32비트라는 보장은 C 언어 자체에 없다. 레지스터 interface에는 벤더 CMSIS 헤더가 선언한 타입을 쓰거나 `uint32_t`처럼 폭이 드러나는 타입을 쓴다.

```c
volatile uint32_t * const gpio_moder =
    (volatile uint32_t *)0x48000000U;
```

여기서 중요한 것은 `uint32_t`가 32비트 **데이터 폭**을 표현하고, `volatile`이 하드웨어가 값을 바꿀 수 있음을 compiler에 알린다는 점이다. 주소 상수의 정확성, 정렬, read/write 권한, register의 실제 폭은 반드시 데이터시트와 벤더 헤더로 확인한다.

---

## 5. 실습 절차

1. `stdint.h`, `limits.h`, `inttypes.h`를 include한다.
2. `int8_t`부터 `uint64_t`까지 필요한 타입의 `sizeof`를 `%zu`로 출력한다.
3. `INTn_MIN`, `INTn_MAX`, `UINTn_MAX`를 출력하거나 debugger에서 확인한다.
4. 같은 코드를 PC와 target MCU에서 빌드해 결과가 달라지는 기본 타입이 있는지 확인한다.
5. protocol·register·저장 format에는 의도한 폭이 드러나는 typedef로 바꾼다.

`sizeof(pointer)`는 포인터가 가리키는 heap block의 크기가 아니라 주소를 저장하는 포인터 객체의 크기라는 점도 함께 구분해야 한다.

---

## 참고 자료

- [How to Find Memory Size & Limits of C Data Types | Microcontrollers (Video 08) (YouTube)](https://www.youtube.com/watch?v=vq7ghSMR2ts)
- [`sizeof`와 포인터 메모리 크기](./sizeof와_포인터_메모리_크기.md) — `sizeof`와 배열 decay·heap block 크기
- [컴퓨터는 어떻게 숫자를 세는가](../cs/임베디드수업/1_컴퓨터는_어떻게_숫자를_센다.md) — signed/unsigned와 2의 보수
- [레지스터 직접 접근(메모리 맵)](../stm32/기초/2_레지스터_직접접근_메모리맵.md) — fixed-width type과 `volatile`을 쓰는 MMIO 맥락

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** `uint32_t` 같은 고정폭 정수 타입은 target이 지원할 때 정확한 비트 폭을 코드에 명시하는 `stdint.h` typedef다.
- **왜 필요:** `int`와 `long`의 크기는 플랫폼마다 다를 수 있어, 레지스터·통신 protocol·파일 format처럼 폭이 중요한 임베디드 interface에 기본 타입을 쓰면 이식성 문제가 생긴다.
- **동작:** `sizeof`는 타입 또는 객체의 바이트 수를 `size_t`로 반환하고, `INT32_MAX`·`UINT32_MAX` 같은 macro는 표현 범위를 제공한다. 출력할 때는 `sizeof`에 `%zu`, 고정폭 정수에는 `PRIu32` 같은 macro를 사용한다.
- **비교:** 기본 타입은 구현 의존 폭이고, exact-width type은 폭이 명시적이다. 단, 정확한 폭을 구현할 수 없으면 해당 `uintN_t` typedef가 없을 수 있다.
- **30초 통합 답변:**
  > 임베디드에서는 `int`나 `long`의 크기가 플랫폼마다 달라질 수 있으므로, 32비트 레지스터나 통신 field에는 `uint32_t`처럼 폭이 고정된 타입을 우선합니다. `sizeof`는 실제 바이트 수를 `size_t`로 반환하므로 `%zu`로 출력하고, 범위는 `UINT32_MAX` 같은 `stdint.h` macro로 확인합니다. 다만 `uintN_t`는 target이 정확히 그 폭을 지원할 때만 제공되므로, 빌드 환경과 벤더 헤더를 함께 확인합니다.
