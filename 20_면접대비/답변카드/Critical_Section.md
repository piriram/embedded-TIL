# Critical Section과 Mutual Exclusion

> 출처: `10_주제별/cs/RTOS/6_Mutex.md` (§4)
> 최종 갱신: 2026-05-27

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다.

Critical section은 shared resource를 읽고·수정하고·다시 쓰는 code 영역으로, 한 task가 들어가면 중간에 다른 task가 같은 영역에 진입하지 못하도록 보호해야 하는 구간입니다. 다른 task의 동시 진입을 막는 개념을 mutual exclusion이라고 하고, 이를 강제하는 도구로 lock, mutex, semaphore, 또는 queue 기반 message passing이 사용됩니다. FreeRTOS에서는 mutex와 semaphore가 모두 queue 위에 구현되어 있어 API가 비슷합니다. Critical section을 잘못 잡으면 race condition이 발생하고, 너무 길게 잡으면 다른 task의 응답성이 떨어집니다.

---

## 한 줄 정의

Critical section은 shared resource를 다루는 atomic하게 실행돼야 할 code 영역이고, mutual exclusion은 그 영역에 한 번에 한 task만 들어가게 강제하는 원칙이다.

## 왜 필요한가

Shared resource를 보호하지 않으면 race condition으로 update가 유실된다. Critical section이라는 경계를 명확히 정의해야 어떤 코드를 어떤 동기화 도구로 감쌀지 설계할 수 있다.

## 동작 원리

진입 전 lock 획득 시도 → 성공 시 critical section 실행 → 종료 시 lock 해제. 획득/해제 동작 자체가 atomic해야 한다(test-and-set 같은 special instruction 또는 scheduler 차원의 protection).

## 언제 쓰는가 / 언제 피하는가

- **반드시 보호:** shared mutable state(global var, buffer, hardware register, peripheral)
- **짧게 유지:** critical section이 길수록 다른 task latency↑, priority inversion 위험↑
- **피할 수 있으면:** queue로 shared state 자체를 없애는 설계가 더 단순

## 대표 예시

Global `counter`를 두 task가 increment. `xSemaphoreTake(mutex) → counter++ → xSemaphoreGive(mutex)`로 감싼 4줄이 critical section.

## 비교 / 대안 (Mutual Exclusion 구현 도구)

| 도구 | 특징 |
|------|------|
| Lock/Mutex | ownership 있음. 같은 task가 take→give |
| Semaphore | ownership 없음. counter 기반, signaling에 적합 |
| Queue | message passing으로 공유 자체를 제거 |
| Disable interrupts | 짧은 구간에 한정. ISR과의 race 차단용 |

---

## 꼬리질문 예상

- **Q:** Critical section이 너무 길면 뭐가 문제?
  **A:** Lock 잡은 동안 다른 task가 막혀 응답성·실시간성 저하. Priority inversion 가능성↑.

- **Q:** Mutual exclusion을 mutex 없이 구현 가능?
  **A:** Short critical section은 ISR disable로도 가능. 또는 lock-free 자료구조나 atomic CAS instruction 사용.

- **Q:** Mutex가 critical section을 어떻게 보장?
  **A:** Take/give 동작 자체가 atomic이어서 두 task가 동시에 mutex를 가져갈 수 없다. 못 가져간 task는 block/yield.

---

## 자주 하는 오해

- **오해:** Critical section = 함수 전체
  - **정확히는:** 정확히 shared resource를 건드리는 최소 범위. 넓을수록 손해.

---

## 키워드

`shared resource` `mutual exclusion` `atomic` `lock` `mutex` `짧게 유지`
