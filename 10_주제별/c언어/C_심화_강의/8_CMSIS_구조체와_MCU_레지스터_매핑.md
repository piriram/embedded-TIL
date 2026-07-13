# CMSIS 구조체와 MCU 레지스터 매핑

**원본 강의:** [#12 Structures in C and CMSIS — Quantum Leaps (YouTube)](https://www.youtube.com/watch?v=A0r3O2TxtiU)

## 1. register block을 구조체로 표현하기

```c
typedef struct {
    volatile uint32_t MODER;    // 0x00
    volatile uint32_t OTYPER;   // 0x04
    volatile uint32_t OSPEEDR;  // 0x08
    volatile uint32_t PUPDR;    // 0x0C
    volatile uint32_t IDR;      // 0x10
    volatile uint32_t ODR;      // 0x14
    volatile uint32_t BSRR;     // 0x18
} GPIO_TypeDef;
#define GPIOA ((GPIO_TypeDef *)0x48000000UL)
```

`GPIOA->ODR`은 base address와 `ODR` offset에 접근한다는 뜻이다. 구조체 멤버와 reserved 배열은 데이터시트 register map의 offset과 정확히 맞아야 한다.

---

## 2. CMSIS를 직접 재작성하지 않는 이유

레지스터는 하드웨어나 외부 이벤트로 바뀌고 read/write가 부작용을 가질 수 있으므로 보통 `volatile uint32_t`다. CMSIS는 `__I`, `__O`, `__IO` 같은 접근 의도 표기도 제공한다. 벤더 device header를 사용하면 reserved field와 offset 검증을 다시 만들 필요가 없다.

```c
GPIOA->BSRR = (1U << 5);  // set 전용 register 예
```

`volatile`은 접근 제거를 막을 뿐 atomicity를 보장하지 않는다. `ODR |= mask` 같은 RMW 대신 MCU가 제공하는 `BSRR`/SET/CLR alias를 우선한다.

> **주의**
> 구조체는 register word의 offset을 표현하는 데 쓰고, 개별 bit는 layout이 구현 의존적인 bit-field 대신 mask/shift와 벤더 macro로 조작한다.

## 참고 자료

- [원본 강의](https://www.youtube.com/watch?v=A0r3O2TxtiU)
- [구조체 padding과 alignment](./6_구조체_padding과_alignment.md)
- [bit-field와 mask/shift](./7_bit_field와_mask_shift.md)

---

## 면접 답변 (30초 분량)

- **한 줄 정의:** CMSIS register 구조체는 peripheral base address의 register offset을 `volatile` 멤버로 표현하는 인터페이스다.
- **왜 필요:** 숫자 주소 대신 `GPIOA->ODR`처럼 데이터시트와 대응되는 읽기 쉬운 코드가 된다.
- **동작:** base address를 register-block 구조체 포인터로 보고, 멤버 순서와 reserved 배열로 offset을 맞춘다.
- **비교:** 구조체는 word offset을 나타내고 개별 bit는 mask/shift가 더 이식성 있다.
- **30초 통합 답변:**
  > CMSIS의 레지스터 구조체는 peripheral base address를 `volatile` 구조체 포인터로 보고 데이터시트의 register offset을 멤버로 표현합니다. 그래서 `GPIOA->ODR`처럼 읽기 쉬워지지만 멤버 순서와 reserved 영역이 하드웨어 map과 정확히 맞아야 하므로 벤더 header를 사용합니다. `volatile`은 원자성을 보장하지 않으며, 개별 bit는 bit-field보다 mask/shift와 BSRR 같은 전용 set/clear register를 우선합니다.

