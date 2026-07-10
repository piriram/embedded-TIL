# Mutex

> 출처: `10_주제별/cs/RTOS/6_Mutex.md` (§5-9)
> 최종 갱신: 2026-05-27

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다.

Mutex는 shared resource의 critical section에 한 번에 하나의 task만 들어가도록 보장하는 mutual exclusion 도구입니다. 두 task가 같은 global counter를 read-modify-write하면 중간 context switch 때문에 update가 유실되는 race condition이 생기는데, mutex로 read-modify-write 전체를 감싸면 한 task가 끝낼 때까지 다른 task는 진입할 수 없습니다. FreeRTOS에서는 mutex도 semaphore 계열 API로 다루고, task가 `xSemaphoreTake()`로 mutex를 얻은 뒤 critical section을 실행하고 끝나면 반드시 `xSemaphoreGive()`로 반환합니다. Queue가 message passing으로 공유 자체를 줄인다면, mutex는 반드시 공유해야 하는 resource를 보호하는 도구입니다.

---

## 한 줄 정의

Mutex(mutual exclusion)는 한 task가 take하면 give할 때까지 다른 task의 critical section 진입을 막는 ownership 기반 lock이다.

## 왜 필요한가

여러 task가 같은 global state를 read-modify-write할 때 context switch 순서에 따라 update가 유실된다(race condition). Mutex가 read-modify-write 전체를 한 task에 묶어 일관성을 보장한다.

## 동작 원리

- Mutex는 boolean(0/1)으로 단순화 가능. Available/unavailable 상태.
- `xSemaphoreTake()`는 mutex 확인 → take를 한 instruction에 묶는 **atomic** 동작 (test-and-set류 instruction 활용).
- Take 성공 → critical section 실행 → `xSemaphoreGive()`로 반환.
- 다른 task가 preempt돼도 mutex unavailable이면 진입 실패 → yield 또는 block.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** 반드시 공유해야 하는 mutable resource(global counter, buffer index, peripheral register) 보호
- **피하는 경우:** ISR 안 (block될 수 있어 ISR-safe API 또는 binary semaphore 사용) / task 간 단순 신호 전달(semaphore가 맞음)

## 대표 예시

```c
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

if (xSemaphoreTake(mutex, 0) == pdTRUE) {
    // critical section: read-modify-write
    xSemaphoreGive(mutex);
} else {
    // 다른 일 수행
}
```
두 번째 parameter `0` = non-blocking (즉시 실패 시 `pdFALSE`).

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| Semaphore | ownership 없음, counter 기반, signaling용. mutex는 ownership 있음 + priority inheritance |
| Queue | data 전달 + 동기화를 함께 제공. shared state 자체를 줄임 |
| Binary semaphore | 0/1만 count, 겉은 mutex 비슷하지만 ownership·priority inheritance 없음 |

---

## 꼬리질문 예상

- **Q:** Take 동작이 왜 atomic이어야 하나?
  **A:** Check와 take 사이에 다른 task가 끼면 두 task가 동시에 mutex를 가져간다고 판단할 수 있다. test-and-set 같은 single instruction으로 보장.

- **Q:** `xSemaphoreTake` 두 번째 인자?
  **A:** Timeout tick. `0`이면 non-blocking, `portMAX_DELAY`면 무한 대기.

- **Q:** Critical section 안에서 return하면?
  **A:** Give 누락되어 다른 task가 영원히 진입 불가. 모든 경로에서 give 보장 필요(또는 RAII/cleanup pattern).

- **Q:** ISR에서 mutex 써도 되나?
  **A:** 안 됨. ISR은 block 불가. 신호 전달이 목적이면 `xSemaphoreGiveFromISR()`로 binary semaphore 사용.

---

## 자주 하는 오해

- **오해:** Mutex와 binary semaphore는 같다.
  - **정확히는:** 동작은 비슷해도 mutex만 ownership과 priority inheritance를 가진다. Resource 보호는 mutex, signaling은 binary semaphore.

- **오해:** Mutex만 있으면 priority inversion 없다.
  - **정확히는:** Mutex가 priority inheritance를 제공해 inversion을 완화할 뿐, 근본 회피는 아님.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| "잠근다" | "take해서 ownership 획득" |
| "막아준다" | "다른 task의 critical section 진입을 차단" |
| "락" | "mutual exclusion lock (mutex)" |

---

## 키워드

`mutual exclusion` `ownership` `xSemaphoreTake/Give` `atomic test-and-set` `priority inheritance` `critical section`
