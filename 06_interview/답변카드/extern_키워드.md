# `extern` 키워드

> 출처: 자체 작성
> 최종 갱신: 2026-05-30

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다.

`extern`은 **변수나 함수가 다른 어딘가에 정의되어 있다고 컴파일러에게 알리는 선언 키워드**입니다. 핵심은 **선언(declaration)과 정의(definition)를 분리하는 장치**라는 점입니다. 같은 변수를 여러 파일에서 쓰고 싶을 때, 정의는 `.c` 파일에 한 번만 두고 다른 파일들은 헤더에 `extern` 선언만 포함시켜 같은 심볼을 참조합니다. 이 분리가 없으면 헤더를 여러 파일이 include할 때 변수가 중복 정의되어 링커 에러가 납니다. 함수에는 사실 `extern`이 기본값이라 생략 가능하지만, 변수는 명시적으로 `extern`을 붙여야 선언으로 취급됩니다. 임베디드에서는 인터럽트 핸들러와 main loop가 공유하는 플래그 변수, HAL 핸들 구조체, 전역 상태 변수에 많이 쓰입니다.

---

## 한 줄 정의

`extern`은 **이 식별자의 정의는 다른 어딘가(다른 파일이나 같은 파일의 다른 위치)에 있다고 알리는 외부 연결 선언**이다.

핵심은 **"정의가 아니라 선언만 한다"는 표시**.

## 왜 필요한가

C의 컴파일 모델은 파일 단위(translation unit)다. 각 `.c` 파일은 독립적으로 컴파일되어 오브젝트 파일이 되고, 마지막에 링커가 합친다.

문제:
- 컴파일러는 한 `.c` 파일을 컴파일할 때 다른 파일에 뭐가 있는지 모른다.
- 어떤 변수나 함수의 이름과 타입만 알면 컴파일은 가능하지만, 그 실체는 링커가 다른 오브젝트 파일에서 찾아 연결해줘야 한다.

`extern`이 하는 일:
- "이 이름은 존재한다. 타입은 이렇다. 실체는 내가 정의하지 않는다."
- 컴파일러는 이 정보로 코드를 생성할 수 있다.
- 링커가 실체를 다른 오브젝트 파일에서 찾아 연결한다.

만약 `extern` 없이 헤더에 `int g_counter;`를 적고 여러 파일이 그 헤더를 include하면:
- 각 `.c` 파일마다 `g_counter`가 정의된다.
- 링커가 중복 정의 에러를 낸다.

## 선언 vs 정의

```c
extern int g_counter;   // 선언 (declaration). 메모리 할당 X.
int g_counter;          // 정의 (definition). 메모리 할당 O. 0으로 초기화.
int g_counter = 5;      // 정의 + 초기화.
```

규칙:
- 정의는 **정확히 한 번**, 어느 하나의 `.c` 파일에 있어야 한다(One Definition Rule).
- 선언은 **여러 번** 있어도 된다(보통 헤더에 둠).

## 동작 원리 — 전형적인 패턴

### 헤더와 소스 분리

```c
// shared.h
#ifndef SHARED_H
#define SHARED_H

extern volatile uint32_t g_tick;     // 선언만
void inc_tick(void);                 // 함수 선언 (extern 생략됨)

#endif
```

```c
// shared.c
#include "shared.h"

volatile uint32_t g_tick = 0;        // 정의 (실체)

void inc_tick(void) { g_tick++; }    // 정의
```

```c
// main.c
#include "shared.h"

int main(void) {
    inc_tick();
    if (g_tick > 1000) { /* ... */ }
}
```

- `main.c`는 `g_tick`의 선언만 보고 컴파일된다.
- 링커가 `shared.c`의 정의와 연결한다.

### 함수에는 사실 `extern`이 기본

```c
void foo(void);            // 사실 extern void foo(void); 와 동일
extern void foo(void);     // 명시. 의미 같음.
```

함수 선언은 본문이 없으면 자동으로 선언으로 취급되어 `extern`은 보통 생략한다. 변수는 다르다 — 초기화 없는 `int x;`도 파일 범위에서는 정의로 취급되므로 `extern`을 명시해야 선언이 된다.

## 임베디드에서 자주 쓰는 패턴

### 1. 인터럽트 ↔ main loop 공유 플래그

```c
// shared.h
extern volatile uint8_t btn_flag;

// main.c
volatile uint8_t btn_flag = 0;

void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == GPIO_PIN_0) btn_flag = 1;
}

while (1) {
    if (btn_flag) { btn_flag = 0; /* handle */ }
}
```

### 2. HAL 핸들 공유

```c
// main.h
extern I2C_HandleTypeDef hi2c1;

// main.c (CubeMX 자동 생성)
I2C_HandleTypeDef hi2c1;

// mpu6050.c
#include "main.h"
void mpu6050_read(void) {
    HAL_I2C_Master_Receive(&hi2c1, /* ... */);
}
```

### 3. 다른 파일의 함수 호출 (관습상 생략하지만 명시할 수도)

```c
extern void uart_send_string(const char *s);
```

## 함정

### `extern` + 초기화 = 정의

```c
extern int x = 10;   // 초기화가 있으면 선언 아니라 정의!
```

대부분 컴파일러가 경고만 하고 정의로 취급한다. 의도가 헷갈리므로 피한다.

### 헤더에 변수 정의

```c
// bad_header.h
int g_counter = 0;   // 헤더에 정의 — 여러 파일이 include하면 중복 정의
```

이 헤더를 여러 파일에서 include하면 링커 에러. 헤더에는 `extern` 선언만, 정의는 `.c`에.

### `static` vs `extern`

`static` 파일 범위 변수는 내부 연결이라 `extern`으로 끌어올 수 없다. 정반대 방향.

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| `static` (파일 범위) | 내부 연결. 다른 파일에서 못 봄. `extern`의 반대. |
| `extern` 없는 변수 (파일 범위) | 외부 연결 + 정의. 다른 파일에서 `extern` 선언으로 끌어 쓸 수 있음. |
| `extern` 선언 | 외부 연결만. 메모리 할당 안 함. |
| 함수 선언 | 기본이 `extern`. 명시는 보통 생략. |
| 매크로 (`#define`) | 전처리기에서 치환. 심볼 아님. 링커 무관. |

## 꼬리질문 예상

- **Q:** `extern`을 붙이면 무엇이 달라지나요?
  **A:** 변수 선언으로 취급되어 메모리 할당이 일어나지 않고, 컴파일러가 실체를 다른 오브젝트 파일에서 찾도록 링커에 위임한다.

- **Q:** 헤더 파일에 변수를 정의하면 무슨 문제가 생기나요?
  **A:** 여러 `.c` 파일이 그 헤더를 include하면 변수가 여러 번 정의되어 링커에서 중복 정의 에러가 난다.

- **Q:** 함수 선언에 `extern`을 생략해도 되는 이유는?
  **A:** 함수는 본문이 없으면 자동으로 선언으로 취급되어 `extern`이 기본값이기 때문이다.

- **Q:** `extern` 선언이 정의와 타입이 다르면 어떻게 되나요?
  **A:** 표준상 미정의 동작이다. 컴파일러는 못 잡고, 링커는 이름만 매칭한다. 런타임에 잘못된 메모리를 잘못된 타입으로 접근해 깨진다.

- **Q:** `extern`과 `static`을 같이 쓸 수 있나요?
  **A:** 의미가 충돌해서 안 된다. `static`은 내부 연결, `extern`은 외부 연결을 의미한다.

---

## 자주 하는 오해

- **오해:** `extern`은 변수를 만든다.
  - **정확히는:** 변수를 만들지 않고, 다른 곳에 있는 변수의 이름과 타입만 컴파일러에 알린다.

- **오해:** 헤더에 `extern int x;`라고 쓰면 변수가 생긴다.
  - **정확히는:** 헤더에서는 선언만 한다. 실체는 어느 `.c` 파일에 `int x;`로 정의해야 한다.

- **오해:** 함수에 `extern`을 안 붙이면 내부 연결이 된다.
  - **정확히는:** 함수는 명시하지 않아도 기본이 외부 연결이다. 내부 연결로 만들려면 `static`을 붙인다.

- **오해:** `extern int x = 10;`은 다른 곳의 x에 10을 대입한다.
  - **정확히는:** 초기화가 있으면 정의로 취급된다. 다른 곳에서 또 정의되어 있으면 중복 정의 에러.

---

## 키워드

`extern` `declaration` `definition` `external linkage` `translation unit` `linker` `One Definition Rule` `header guard` `forward declaration` `shared global state`
