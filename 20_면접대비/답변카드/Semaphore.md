# Semaphore

> 출처: `10_학습자료/cs/RTOS/7_세마포어.md` (§1-3, 7)
> 최종 갱신: 2026-05-27

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다.

Semaphore는 RTOS에서 count 값을 통해 task 사이에 resource availability나 event 발생을 signal하는 synchronization object입니다. Producer-consumer 구조에서 producer가 buffer에 item을 넣고 `xSemaphoreGive()`로 count를 올리면, consumer는 `xSemaphoreTake()`로 count를 내리고 item을 소비합니다. Count가 0이면 consumer는 block되고, maximum count를 buffer capacity에 맞추면 producer가 용량을 넘지 못하게 제한할 수도 있습니다. Mutex와 달리 ownership이 없어 shared resource 보호보다는 signaling에 적합하고, buffer index 같은 critical section은 별도로 mutex로 보호해야 합니다. Binary semaphore는 0/1만 count하는 형태로 ISR에서 task로의 event 통지에 자주 씁니다.

---

## 한 줄 정의

Semaphore는 0 이상의 count를 가진 synchronization object로, give/take로 count를 조작해 task 사이에 resource 가용성·event 발생을 signal한다.

## 왜 필요한가

Producer-consumer 같은 구조에서 "읽을 item이 있는지", "빈 slot이 있는지"를 task 간에 알려야 한다. Semaphore는 이 상태를 count로 표현해 동기화한다.

## 동작 원리

- Count > 0 → `xSemaphoreTake()` 성공, count -1
- Count = 0 → take 실패, 호출 task는 block 또는 즉시 실패
- `xSemaphoreGive()` → count +1, 기다리던 task 깨움
- Take의 check-and-decrement는 **atomic**

Counting semaphore는 max 값까지 count, binary semaphore는 0/1로 제한.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** producer-consumer signaling / ISR → task event 통지(binary) / 제한된 동시 접근 수 제어
- **피하는 경우:** shared resource 자체 보호 (ownership 없으니 mutex 써라) / 단순 data 전달 (queue가 더 단순)

## 대표 예시

Producer-Consumer:
- Producer: buffer에 item write → `xSemaphoreGive(filled)` → count↑
- Consumer: `xSemaphoreTake(filled)` → count > 0이면 item read, 0이면 block

Circular buffer 풀세트: `mutex 1개` (buffer/index 보호) + `counting semaphore 2개` (filled / empty slot 수).

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| Mutex | ownership 있음, 같은 task가 take/give. semaphore는 give·take task가 다를 수 있음 |
| Queue | data + 동기화를 함께. semaphore보다 단순 |
| Binary semaphore | semaphore의 0/1 특화. ISR → task signaling에 자주 사용 |

---

## 꼬리질문 예상

- **Q:** Mutex 대신 binary semaphore로 resource 보호하면?
  **A:** 동작하지만 ownership·priority inheritance 없어 priority inversion 위험. 보호 목적이면 mutex.

- **Q:** Producer-consumer에 queue 있는데 왜 semaphore?
  **A:** Queue가 보통 더 단순. 단, buffer를 직접 관리하거나 단일 event signaling만 필요할 때 semaphore가 가볍다.

- **Q:** Count = 0에서 take하면?
  **A:** Timeout 인자에 따라 block (timeout tick 동안) 또는 즉시 `pdFALSE` 반환.

- **Q:** ISR에서는?
  **A:** `xSemaphoreGiveFromISR()` 사용. Binary semaphore로 task에 "data ready" 통지가 전형 패턴.

---

## 자주 하는 오해

- **오해:** Semaphore는 mutex의 일반화(count만 늘리면 끝).
  - **정확히는:** Technically 맞지만 실무에서는 signaling이 주 용도. Ownership·priority inheritance 차이로 resource 보호에는 mutex가 맞다.

- **오해:** Semaphore가 있으면 buffer 안전.
  - **정확히는:** Buffer index·data 수정은 여전히 critical section. Semaphore로 slot 수만 알리고, 실제 접근은 mutex로 보호.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| "신호 보낸다" | "give로 count를 올려 waiting task를 깨운다" |
| "락이랑 비슷" | "synchronization object지만 ownership 없음" |
| "POSIX에서 wait/post" | "FreeRTOS take/give = POSIX wait/post" |

---

## 키워드

`count` `signaling` `producer-consumer` `xSemaphoreGive/Take` `binary semaphore` `ownership 없음`
