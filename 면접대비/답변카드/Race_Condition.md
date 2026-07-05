# Race Condition

> 출처: `cs/RTOS/6_Mutex.md` (§1-2)
> 최종 갱신: 2026-05-27

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다.

Race condition은 두 개 이상의 task가 같은 shared resource를 동시에 다룰 때, system 결과가 task instruction의 실행 순서에 의존하게 되는 문제입니다. 예를 들어 두 task가 같은 global counter를 `읽고 → 수정 → 쓰기` 하는데, 한 task가 읽고 아직 write back하기 전에 context switch가 일어나면 다른 task는 갱신되지 않은 값을 읽습니다. 결국 두 task가 각각 한 번씩 increment했는데 counter는 한 번만 증가하는 update 유실이 발생합니다. `shared_var++` 같은 한 줄짜리 연산도 대부분 architecture에서 read-modify-write 여러 instruction으로 쪼개지기 때문에 atomic하지 않은 게 원인입니다.

---

## 한 줄 정의

Race condition은 system behavior가 통제할 수 없는 event timing(task 실행 순서)에 의존하게 되는 concurrency bug다.

## 왜 필요한가 (왜 알아야 하는가)

Concurrent 환경에서 shared resource를 보호하지 않으면 update가 조용히 유실되어, 재현 어려운 버그가 production에서 터진다. Mutex/semaphore가 왜 필요한지 설명하려면 race condition이 출발점이다.

## 동작 원리

`shared_var++` 같은 연산은 일반적으로 (1) memory에서 값 읽기 (2) register/local에 보관 (3) increment (4) memory write back 4단계로 나뉜다. 중간 어디서든 context switch가 일어나면 다른 task가 stale value를 보고 같은 update를 덮어쓸 수 있다.

## 언제 쓰는가 / 언제 피하는가

- **발생 조건:** 2개 이상 task + shared mutable state + non-atomic 접근
- **회피:** critical section을 mutex로 보호 / queue로 message passing / atomic instruction 사용

## 대표 예시

Global counter 초기값 `2`. Task A가 `2` 읽고 local 보관 → context switch → Task B가 `2` 읽어 `3`으로 write → Task A 재개해서 local의 `2`를 `3`으로 만들어 write. 두 번 increment했지만 counter는 `3`. 한 번만 증가.

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| Deadlock | race는 timing 의존 결과 오류, deadlock은 서로 lock 기다리며 멈춤 |
| Priority inversion | race는 보호 안 함이 원인, inversion은 lock 보호는 했지만 우선순위가 역전됨 |

---

## 꼬리질문 예상

- **Q:** `shared_var++`는 한 줄인데 왜 atomic 아닌가?
  **A:** Source는 한 줄이지만 대부분 architecture에서 load/modify/store 여러 instruction으로 compile된다. 사이에 context switch 가능.

- **Q:** 어떻게 막나?
  **A:** Critical section을 mutex로 감싸 read-modify-write 전체를 한 task가 끝낼 때까지 다른 task 진입 차단. Queue로 shared state 자체를 없애는 것도 방법.

- **Q:** Single-core에서도 발생하나?
  **A:** 발생. Preemptive scheduler가 instruction 사이에 context switch하므로 core 1개라도 충분.

---

## 자주 하는 오해

- **오해:** Race condition은 multi-core에서만 발생한다.
  - **정확히는:** Single-core preemptive RTOS에서도 발생. Context switch가 instruction 단위가 아니라 임의 시점에 일어나기 때문.

- **오해:** `++` 같은 단일 연산자는 안전하다.
  - **정확히는:** 대부분 architecture에서 load-modify-store로 쪼개진다. `volatile`도 atomicity는 보장 안 함.

---

## 키워드

`shared resource` `context switch` `read-modify-write` `atomic` `critical section` `update lost`
