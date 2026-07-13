# C11 `atomic`과 Race Condition

**원본 강의:** [Making variables atomic in C (YouTube)](https://www.youtube.com/watch?v=_xX25ThomIo) — Jacob Sorber

`volatile`은 하드웨어 레지스터나 ISR 공유 플래그에 필요한 키워드지만, 여러 실행 주체가 같은 값을 **읽고 → 계산하고 → 쓰는** 일을 하나로 묶어 주지는 않는다. 이 노트는 race condition의 원인과 C11의 `_Atomic`, mutex, 임계구역의 역할 경계를 정리한다.

---

## 1. 일반 카운터가 틀린 값을 만드는 이유

두 thread가 하나의 공유 카운터를 동시에 증가시킨다고 하자.

```c
uint64_t counter = 0U;

// thread A와 thread B가 둘 다 실행
counter += value;
```

소스에서는 한 줄이지만 일반적인 증가·더하기는 개념적으로 다음 단계다.

```text
1. counter 읽기
2. 레지스터에서 value를 더하기
3. 결과를 counter에 쓰기
```

실행이 끼어들면 한 갱신이 사라진다.

```text
counter = 10
A: 10 읽음
B: 10 읽음
A: 10 + 1을 계산해 11 기록
B: 10 + 1을 계산해 11 기록
결과: 두 번 증가했지만 counter는 11
```

이처럼 결과가 thread 또는 ISR의 실행 타이밍에 따라 달라지는 문제가 **race condition**이다. 멀티코어뿐 아니라 single-core MCU에서도 ISR이 main loop를 중간에 선점하면 같은 문제가 생길 수 있다.

---

## 2. `volatile`은 왜 해결책이 아닌가

```c
volatile uint32_t counter = 0U;
counter++;                         // 여전히 read-modify-write 복합 연산
```

`volatile`은 컴파일러가 `counter` 접근을 캐싱하거나 없애지 않도록 한다. 그래서 MMIO 레지스터, ISR/DMA가 바꿀 수 있는 플래그에는 필요하다. 그러나 `counter++`의 여러 단계를 **서로 끼어들 수 없게 만들지는 않는다.**

| 필요한 성질 | `volatile` | `atomic` | mutex / 임계구역 |
| --- | --- | --- | --- |
| 컴파일러가 접근을 생략·캐싱하지 못하게 함 | 가능 | 목적이 다름 | 목적이 다름 |
| 단일 read-modify-write를 하나의 연산으로 수행 | 불가 | 가능 | 가능 |
| 여러 변수·여러 문장으로 된 불변식 보호 | 불가 | 보통 불충분 | 가능 |
| ISR과 main의 짧은 공유 구간 보호 | 불가 | 플랫폼·구현 검토 필요 | interrupt disable 등으로 가능 |

> **주의**
> `volatile`은 atomic, mutual exclusion, thread-safe의 동의어가 아니다. “접근을 실제로 발생시킨다”와 “경쟁 없이 올바른 순서로 갱신한다”는 별개의 문제다.

---

## 3. C11 atomic — 공유 객체의 원자적 접근

C11은 `<stdatomic.h>`에 atomic 타입과 연산을 제공한다. 다음처럼 `_Atomic`으로 객체를 선언할 수 있다.

```c
#include <stdatomic.h>
#include <stdint.h>

_Atomic uint64_t counter = 0U;
```

두 thread가 이 카운터에 더할 때는 atomic read-modify-write 연산을 사용한다.

```c
void count(uint64_t value) {
    atomic_fetch_add(&counter, value);
}
```

`atomic_fetch_add()`는 현재 값을 읽고 더한 뒤 기록하는 것을 하나의 atomic operation으로 수행한다. 반환값으로는 더하기 전 값이 돌아온다.

강의에서 보인 `counter += value`나 `counter++` 같은 atomic 객체의 compound assignment도 atomic read-modify-write로 정의된다. 다만 `atomic_fetch_add()`처럼 의도가 드러나는 API를 쓰면 검토하기 쉽다.

---

## 4. 비슷해 보이지만 다른 두 표현

다음 코드는 일반 변수라면 결과가 같지만, atomicity 관점에서는 다르다.

```c
counter += value;                  // atomic 객체의 compound assignment: atomic RMW
counter = counter + value;         // load + add + store가 분리될 수 있음
```

두 번째 줄은 `counter`를 읽는 atomic load와 결과를 쓰는 atomic store 사이에 다른 실행 주체가 들어올 수 있다. 따라서 전체 더하기는 atomic하지 않으며 update lost가 다시 발생한다.

**교훈:** atomic 타입을 선언한 사실만으로 임의의 여러 문장 또는 임의의 표현 전체가 자동으로 하나의 transaction이 되지는 않는다. atomic read-modify-write 연산 또는 필요한 범위의 lock을 선택해야 한다.

---

## 5. mutex와 atomic의 선택 기준

강의는 mutex로 같은 카운터를 보호하는 방법과 atomic을 비교한다.

```c
pthread_mutex_lock(&counter_lock);
counter += value;
pthread_mutex_unlock(&counter_lock);
```

| 상황 | 적합한 선택 | 이유 |
| --- | --- | --- |
| 단일 카운터·플래그·포인터의 단순 갱신 | atomic | 짧은 단일 객체 연산을 명확하게 보호 |
| 여러 변수의 관계를 함께 유지 | mutex / 임계구역 | 전체 읽기·검증·수정 범위를 하나로 보호 |
| ISR과 main이 공유하는 값 | 매우 짧은 critical section 또는 MCU가 보장하는 atomic 접근 | RTOS mutex는 ISR에서 보통 쓸 수 없음 |
| 하드웨어 MMIO 레지스터 | 데이터시트에 맞는 `volatile` 접근 및 전용 set/clear 레지스터 | C atomic이 하드웨어 레지스터의 부작용·비트 규칙을 해결하지 않음 |

atomic 구현은 CPU가 제공하는 atomic instruction을 사용할 수 있어 mutex보다 가벼울 수 있다. 하지만 지원되지 않는 크기나 아키텍처에서는 라이브러리 호출 또는 내부 lock으로 구현될 수 있으므로, **atomic을 쓴다고 항상 더 빠른 것은 아니다.**

---

## 6. 지원 여부와 코드 의도 확인

atomic은 C11 기능이므로 컴파일러 언어 표준과 target 지원을 확인해야 한다.

```c
#if !defined(__STDC_VERSION__) || (__STDC_VERSION__ < 201112L) \\
    || defined(__STDC_NO_ATOMICS__)
#error "C11 atomics are not supported by this toolchain"
#endif
```

- `__STDC_VERSION__ >= 201112L`: C11 이상인지 확인한다.
- `__STDC_NO_ATOMICS__`: 구현이 atomic을 제공하지 않음을 알리는 선택적 매크로다.
- 특정 타입 크기의 연산이 lock-free인지까지 필요하면 `atomic_is_lock_free()`로 확인한다.

```c
if (!atomic_is_lock_free(&counter)) {
    // 성능 또는 ISR 안전성 요구가 있다면 이 경로를 별도로 설계한다.
}
```

> **주의**
> `atomic_is_lock_free()`가 false라고 correctness가 사라지는 것은 아니다. 내부 lock·라이브러리 호출이 필요할 수 있으므로 성능, ISR 사용 가능성, 의존성을 다시 검토해야 한다.

---

## 7. 메모리 순서와 이 강의의 범위

C11 atomic에는 `memory_order_relaxed`, `memory_order_acquire`, `memory_order_release` 같은 memory order도 있다. 이들은 다른 메모리 읽기·쓰기가 관측되는 순서를 제어한다.

이 강의의 카운터 예제처럼 **값 하나를 잃지 않게 누적**하는 데는 atomic RMW라는 사실이 핵심이다. 여러 데이터의 publish/consume 순서까지 보장해야 한다면 memory order를 별도 설계해야 하며, 기본 `atomic_fetch_add()`는 가장 보수적인 `memory_order_seq_cst`를 사용한다.

> `volatile`은 최적화 제어이고, atomic은 한 객체 연산의 원자성과 메모리 순서를 위한 도구다. ISR과 main이 공유하는 복합 상태나 여러 변수의 일관성은 atomic 하나만으로 해결되지 않을 수 있으므로, MCU와 RTOS 제약에 맞춰 짧은 임계구역이나 적절한 동기화 도구를 선택한다.

---

## 참고 자료

- [Making variables atomic in C (YouTube)](https://www.youtube.com/watch?v=_xX25ThomIo)
- [C Preprocessor와 volatile 키워드](./Preprocessor와_volatile.md)
- 관련 면접 카드: [Race Condition](../../20_면접대비/답변카드/Race_Condition.md), [Critical Section](../../20_면접대비/답변카드/Critical_Section.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** C11 atomic은 공유 객체의 load, store, read-modify-write를 중간에 끼어들 수 없는 원자적 연산으로 표현하는 기능이다.
- **왜 필요:** `counter++`와 `counter = counter + value`는 읽기·계산·쓰기 단계로 나뉘므로 thread나 ISR이 끼면 갱신이 유실되는 race condition이 생긴다.
- **동작:** `_Atomic uint64_t counter`를 선언하고 `atomic_fetch_add(&counter, value)`처럼 atomic RMW 연산을 사용하면 한 카운터 갱신을 원자적으로 수행한다.
- **비교:** `volatile`은 접근 생략·캐싱을 막을 뿐 atomicity를 보장하지 않는다. 여러 변수의 상태를 함께 보호해야 하면 atomic 하나보다 mutex 또는 짧은 critical section이 맞다.
- **30초 통합 답변:** C11 atomic은 여러 실행 주체가 공유하는 객체의 연산을 원자적으로 수행하도록 하는 기능입니다. 일반적인 `counter++`는 읽기·수정·쓰기 단계로 나뉘므로 thread나 ISR이 중간에 끼면 update가 유실될 수 있습니다. 이때 `_Atomic` 타입과 `atomic_fetch_add()`를 쓰면 한 카운터의 read-modify-write를 안전하게 처리할 수 있습니다. 다만 `volatile`은 최적화 제어일 뿐 원자성을 보장하지 않고, 여러 변수의 일관성이나 긴 처리 구간은 mutex나 임계구역으로 보호해야 합니다.
