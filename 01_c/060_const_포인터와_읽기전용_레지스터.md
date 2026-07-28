# `const` 포인터와 읽기 전용 레지스터

**원본 강의:** [Const, const pointers, and pointers to const things (YouTube)](https://www.youtube.com/watch?v=HpElPprsR0I) — Jacob Sorber

`const`가 포인터 선언에 섞이면 무엇이 고정되는지 혼동하기 쉽다. 핵심은 `const`가 **포인터 자체**에 붙었는지, **포인터가 가리키는 대상**에 붙었는지를 `*`를 경계로 구분하는 것이다. 이 노트는 이를 MMIO의 읽기 전용 상태 레지스터까지 연결한다.

---

## 1. `const`의 기본 의미

```c
const int x = 42;
// x = 7;              // 컴파일 오류: x를 통해서는 수정할 수 없음
```

`const`는 값이 절대 변하지 않는다는 뜻보다, **이 식별자 또는 접근 경로를 통한 쓰기를 컴파일러가 거부한다**는 뜻에 가깝다. 실수로 값을 바꾸는 일을 컴파일 단계에서 잡고, 코드를 읽는 사람에게 변경하지 않겠다는 의도를 전달한다.

`const int x`와 `int const x`는 같은 타입이다. 전자는 `const`를 타입 왼쪽에, 후자는 타입 오른쪽에 둔 표기 차이일 뿐이다.

---

## 2. 포인터에서는 고정할 대상이 두 개다

포인터 선언에는 포인터 변수(주소)와 가리키는 객체(값)가 있다. 따라서 `const`도 어느 쪽에 붙이는지에 따라 의미가 달라진다.

| 선언 | 바꿀 수 없는 것 | 가능한 것 |
| --- | --- | --- |
| `const uint32_t *p` | `*p` (가리키는 값) | `p`를 다른 주소로 변경 |
| `uint32_t *const p` | `p` (포인터가 담은 주소) | `*p`의 값 변경 |
| `const uint32_t *const p` | `p`와 `*p` 모두 | 둘 다 변경 불가 |

```c
const uint32_t *p;        // p는 const uint32_t를 가리키는 포인터
uint32_t *const p = &x;   // p는 uint32_t를 가리키는 const 포인터
```

---

## 3. Pointer to const — 대상은 읽기 전용, 포인터는 이동 가능

```c
uint32_t a = 10;
uint32_t b = 20;
const uint32_t *p = &a;

// *p = 11;              // 오류: p를 통해 a를 수정할 수 없음
p = &b;                  // 가능: p 자체는 const가 아님
```

`const uint32_t *p`는 **pointer to const**다. `p`가 가리키는 값을 이 포인터를 통해 수정하지 못할 뿐, `p`가 다른 객체를 가리키도록 바꾸는 일은 가능하다. 함수 인자에서 가장 흔한 형태다.

```c
void uart_send(const uint8_t *buf, size_t len) {
    while (len-- > 0U) {
        uart_write_byte(*buf++);   // 포인터 이동과 읽기는 가능
    }
    // buf[0] = 0U;                // 호출자 버퍼 수정은 불가
}
```

이 선언은 호출자에게 “이 함수는 전달받은 버퍼의 내용을 바꾸지 않는다”는 계약을 준다.

---

## 4. Const pointer — 주소는 고정, 대상 값은 수정 가능

```c
uint32_t a = 10;
uint32_t b = 20;
uint32_t *const p = &a;

*p = 11;                // 가능: a의 값을 수정
// p = &b;              // 오류: p가 담은 주소는 바꿀 수 없음
```

`uint32_t *const p`는 **const pointer**다. 초기화할 때 지정한 주소를 계속 가리켜야 할 때 쓴다. `const`가 `*` 오른쪽에 있어 포인터 변수 `p` 자체를 수식한다.

```c
const uint32_t *const p = &a;
// *p = 11;             // 대상 수정 불가
// p = &b;              // 포인터 변경 불가
```

위 형태는 포인터 주소와 가리키는 대상 모두를 보호한다.

---

## 5. MMIO에 연결 — `const volatile`

MMIO 레지스터는 일반 변수처럼 주소로 접근하지만 실제로는 하드웨어 회로에 연결돼 있다. 상태 레지스터나 ADC 데이터 레지스터처럼 **소프트웨어는 읽기만 하고 하드웨어가 값을 갱신하는 레지스터**에는 두 속성이 동시에 필요하다.

```c
#define ADC_DR (*(const volatile uint32_t *)0x4001244CU)

uint32_t sample = ADC_DR;  // 가능: 하드웨어 상태를 매번 읽음
// ADC_DR = 0U;            // 오류: 소프트웨어 쓰기 금지
```

- `const`: 이 코드가 해당 레지스터에 쓰지 못하게 한다. 즉 소프트웨어 관점의 읽기 전용이다.
- `volatile`: 하드웨어가 프로그램 흐름 밖에서 값을 바꿀 수 있으므로 컴파일러가 읽기를 캐싱하거나 제거하지 못하게 한다.

> **주의**
> `const volatile`은 값이 안 변한다는 뜻이 아니다. 값은 하드웨어가 바꿀 수 있으므로 `volatile`이고, 소프트웨어가 쓰면 안 되므로 `const`다.

쓰기 가능한 출력 레지스터는 보통 `volatile`만 쓴다.

```c
#define GPIOD_ODR (*(volatile uint32_t *)0x40020C14U)
GPIOD_ODR |= (1U << 12);
```

실제 레지스터의 읽기·쓰기 가능 여부와 비트별 제약은 반드시 MCU reference manual을 기준으로 판단한다.

---

## 6. 빠른 판별법

1. 변수 이름에서 시작해 `*`를 기준으로 포인터와 대상을 분리한다.
2. `const`가 대상 타입에 붙으면 가리키는 대상이 const다.
3. `const`가 `*` 오른쪽이면 포인터 자체가 const다.

- `const T *p`: “`p`는 **const T를 가리킨다**.”
- `T *const p`: “`p`는 **고정된 포인터**다.”
- `const T *const p`: “`p`와 대상 모두 고정이다.”

---

## 참고 자료

- [Const, const pointers, and pointers to const things (YouTube)](https://www.youtube.com/watch?v=HpElPprsR0I)
- 관련 노트: [C Preprocessor와 volatile 키워드](./050_Preprocessor와_volatile.md)
- 관련 면접 카드: [`const` 키워드](../../20_면접대비/답변카드/const_키워드.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** `const`는 해당 접근 경로로 객체를 수정하지 못하게 하는 C 타입 한정자다.
- **왜 필요:** 포인터가 가리키는 버퍼를 함수가 바꾸지 않는다는 계약을 만들고, 읽기 전용 레지스터에 실수로 쓰는 일을 컴파일 단계에서 막는다.
- **동작:** `const uint32_t *p`는 `*p`를 수정할 수 없지만 `p`는 이동할 수 있다. `uint32_t *const p`는 포인터 주소는 고정이지만 `*p`는 수정할 수 있다.
- **비교:** `const`는 소프트웨어 쓰기를 제한하고, `volatile`은 외부 변화가 가능한 객체의 접근을 실제로 유지한다. 읽기 전용 MMIO 상태 레지스터는 `const volatile`로 표현한다.
- **30초 통합 답변:** `const`는 그 식별자나 포인터를 통한 쓰기를 컴파일러가 막아 의도를 코드에 명시하는 타입 한정자입니다. `const uint32_t *p`는 가리키는 값을 못 바꾸지만 포인터는 이동할 수 있고, `uint32_t *const p`는 포인터 주소는 고정이지만 대상 값은 바꿀 수 있습니다. 임베디드에서는 함수 입력 버퍼를 보호하고, 하드웨어가 값을 갱신하지만 소프트웨어는 쓰면 안 되는 상태 레지스터에는 `const volatile`을 써서 읽기 전용과 매 접근 보존을 함께 표현합니다.
