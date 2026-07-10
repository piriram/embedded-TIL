# Mutex vs Semaphore

> 출처: `10_주제별/cs/RTOS/7_세마포어.md` (§6) + `10_주제별/cs/RTOS/6_Mutex.md` (§5)
> 최종 갱신: 2026-05-27

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다.

Mutex와 semaphore는 FreeRTOS에서 같은 API 계열로 다루지만 사용 목적이 다릅니다. Mutex는 ownership을 가져서 take한 task가 직접 give하며, shared resource의 critical section 보호에 적합합니다. Semaphore는 ownership이 없어 보통 한 task가 give하고 다른 task가 take하는 signaling, 즉 "event 발생", "resource 준비됨"을 알리는 용도에 적합합니다. 또 FreeRTOS에서는 mutex에만 priority inheritance가 있어, lock을 잡은 low-priority task의 우선순위를 임시로 올려 priority inversion을 완화합니다. Binary semaphore는 0/1만 count해서 겉으로 mutex와 비슷해 보이지만, ownership과 priority inheritance가 없어 resource 보호용으로는 mutex를 써야 합니다.

---

## 한 줄 정의

Mutex는 ownership과 priority inheritance를 갖는 resource 보호용 lock이고, semaphore는 ownership 없이 count로 task 간 event를 signal하는 synchronization object다.

## 왜 알아야 하는가

API가 비슷하다고 binary semaphore로 resource를 보호하면 priority inversion이 그대로 노출된다. 면접에서 "둘 다 가능한데 왜 mutex냐"는 후속 질문 단골.

## 핵심 차이 (표)

| 항목 | Mutex | Semaphore |
|------|-------|-----------|
| Ownership | 있음 (take 한 task만 give) | 없음 (다른 task가 give 가능) |
| 주 용도 | shared resource 보호 | event signaling, resource count |
| Priority inheritance | 있음 (FreeRTOS) | 없음 |
| Count 범위 | 0/1 개념 | 0 ~ max (counting), 0/1 (binary) |
| 비대칭 사용 | take/give 같은 task | give/take 다른 task 흔함 |
| ISR 사용 | 부적합 (block 위험) | binary semaphore가 적합 |

## 언제 무엇을 (의사결정)

- **공유 resource를 한 task만 수정해야 함** → Mutex
- **ISR → task event 통지** → Binary semaphore (`xSemaphoreGiveFromISR`)
- **Producer가 item 넣고 consumer가 꺼냄** → Counting semaphore (또는 queue)
- **동시 접근 수 N개로 제한** → Counting semaphore (max = N)
- **Task A 완료 후 Task B 시작** → Binary semaphore

## 대표 예시

- **Mutex:** `global_counter++` 보호 → take한 task가 read-modify-write 끝내고 give
- **Binary semaphore:** UART RX ISR이 byte 받으면 give → consumer task가 take해서 처리
- **Counting semaphore:** circular buffer의 filled slot 수 / empty slot 수 추적

## Binary Semaphore가 Mutex와 다른 이유

겉보기엔 0/1로 같지만:
1. **Ownership 없음:** Task A가 take했는데 Task B가 give 가능 → 의도치 않은 release
2. **Priority inheritance 없음:** Low-priority task가 잡고 있으면 high-priority task가 그대로 막힘

→ Resource 보호는 mutex, signaling은 binary semaphore.

---

## 꼬리질문 예상

- **Q:** Priority inheritance가 뭔가?
  **A:** Lock 잡은 low-priority task의 priority를 lock을 기다리는 high-priority task 수준으로 임시 상승. High가 lock 못 받아 medium에게 밀리는 priority inversion 완화.

- **Q:** Mutex로 signaling 하면 되지 않나?
  **A:** Ownership 때문에 give한 task와 take한 task가 같아야 자연스러움. 비대칭 signaling은 semaphore가 의미상 맞음.

- **Q:** Semaphore가 deadlock 만들 수 있나?
  **A:** 그렇다. 여러 semaphore를 다른 순서로 take하면 발생 가능. Mutex와 같은 deadlock 위험 있음.

- **Q:** FreeRTOS에서 mutex 만드는 API?
  **A:** `xSemaphoreCreateMutex()`. Binary semaphore는 `xSemaphoreCreateBinary()`, counting은 `xSemaphoreCreateCounting(max, initial)`.

---

## 자주 하는 오해

- **오해:** Semaphore는 mutex의 일반화일 뿐이다.
  - **정확히는:** Count 측면은 맞지만 ownership·priority inheritance가 빠져 resource 보호에는 부적합.

- **오해:** Binary semaphore == mutex.
  - **정확히는:** 동작 비슷, semantics 다름. ISR 신호는 binary semaphore, resource lock은 mutex.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| "둘 다 잠금" | "mutex는 ownership 기반 lock, semaphore는 ownership 없는 signaling" |
| "비슷한 거" | "FreeRTOS에서 API 계열은 같지만 semantics가 다름" |
| "priority 자동 조절" | "priority inheritance — mutex 한정" |

---

## 키워드

`ownership` `priority inheritance` `signaling vs protection` `binary semaphore` `xSemaphoreCreateMutex/Binary/Counting` `FromISR`
