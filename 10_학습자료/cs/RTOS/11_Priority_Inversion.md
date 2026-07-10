# Priority Inversion

**주제:** Priority inversion의 원인, bounded/unbounded priority inversion, Mars Pathfinder 사례, priority ceiling과 priority inheritance, service task 패턴.
**원본 강의:** [Introduction to RTOS Part 11 - Priority Inversion | DigiKey (YouTube)](https://www.youtube.com/watch/C2xKhxROmhA)

> **예외**
> 제공된 transcript는 자동 자막이 심하게 깨져 원문 기반 정리가 불가능했다. 이 노트는 영상 제목과 DigiKey 공식 Part 11 자료를 근거로 보강해 작성했다.

---

## 1. Priority Inversion이란

**Priority inversion**은 낮은 priority task 때문에 높은 priority task가 간접적으로 실행되지 못하는 concurrency bug다.

RTOS에서는 high priority task가 ready 상태라면 low priority task보다 먼저 실행되는 것이 정상이다. 하지만 shared resource와 mutex가 얽히면 이 구조가 뒤집힐 수 있다.

대표적인 흐름은 다음과 같다.

1. Low priority task가 mutex를 얻고 shared resource를 사용한다.
2. High priority task가 같은 mutex를 얻으려고 한다.
3. Mutex는 low priority task가 들고 있으므로 high priority task는 block된다.
4. High priority task가 low priority task를 기다리는 상태가 된다.

이때 priority 구조가 사실상 뒤집힌다.

---

## 2. Bounded Priority Inversion

High priority task가 low priority task의 critical section이 끝날 때까지만 기다리는 경우를 **bounded priority inversion**이라고 한다.

Inversion 시간이 low priority task가 mutex를 들고 있는 시간으로 제한되기 때문이다.

Shared resource를 lock으로 보호하면 bounded inversion 자체는 생길 수 있다. 중요한 것은 critical section을 짧게 유지해 지연 시간을 system requirement 안에 넣는 것이다.

---

## 3. Unbounded Priority Inversion

더 위험한 경우는 **unbounded priority inversion**이다.

1. Low priority task가 mutex를 들고 있다.
2. High priority task가 그 mutex를 기다리며 block된다.
3. Medium priority task가 ready 상태가 되어 low priority task를 preempt한다.
4. Medium priority task는 mutex와 직접 관련이 없지만 계속 CPU를 사용할 수 있다.
5. Low priority task는 mutex를 release할 기회를 얻지 못한다.
6. High priority task는 계속 기다린다.

High priority task가 직접 관련 없는 medium priority task 때문에 계속 지연되는 것이 문제다. Medium task 실행 시간이 제한되지 않으면 high task의 대기 시간도 제한되지 않는다.

> **주의**
> Unbounded priority inversion은 real-time deadline을 깨뜨릴 수 있다. 원인이 high priority task의 코드가 아니라 lock을 들고 있는 low priority task와 그 사이에 끼어든 medium priority task일 수 있어 디버깅도 어렵다.

---

## 4. Mars Pathfinder 사례

Priority inversion의 유명한 실제 사례는 **1997년 NASA Mars Pathfinder mission**이다.

Pathfinder lander는 임무 중 random reset을 겪었다. 원인은 intermittent priority inversion bug였고, watchdog timer가 system restart를 trigger했다.

Engineers는 문제를 분석한 뒤 lander에 patch를 전송해 해결했다.

이 사례는 priority inversion이 단순한 이론 문제가 아니라 실제 mission failure로 이어질 수 있는 RTOS 설계 문제임을 보여준다.

---

## 5. Priority Ceiling

**Priority ceiling protocol**은 resource 또는 lock에 ceiling priority를 부여하는 방식이다.

Ceiling은 그 resource를 사용할 수 있는 task 중 가장 높은 priority를 기준으로 정한다. 어떤 task가 그 resource를 lock하면, lock을 들고 있는 동안 priority가 ceiling priority로 올라간다.

예를 들어 ceiling이 `3`인 mutex를 low priority task가 얻으면, 그 task는 critical section 동안 priority `3`처럼 동작한다.

그러면 medium priority task가 low priority task를 preempt하지 못하고, low priority task가 빨리 mutex를 release할 수 있다.

---

## 6. Priority Inheritance

**Priority inheritance**는 high priority task가 mutex를 기다릴 때 lock holder의 priority를 일시적으로 올리는 방식이다.

흐름은 다음과 같다.

1. Low priority task가 mutex를 얻는다.
2. High priority task가 같은 mutex를 기다린다.
3. Mutex mechanism이 low priority task의 priority를 high priority task 수준으로 boost한다.
4. Medium priority task는 boost된 low priority task를 preempt하지 못한다.
5. Low priority task가 mutex를 release하면 priority가 원래 값으로 돌아간다.
6. High priority task가 mutex를 얻고 실행된다.

Priority ceiling은 resource를 잡는 순간 미리 올리는 방식이고, priority inheritance는 실제 high priority waiter가 생겼을 때 올리는 방식이다.

---

## 7. FreeRTOS에서의 선택

FreeRTOS mutex는 priority inheritance를 지원한다. 그래서 shared resource 보호에는 binary semaphore보다 mutex가 적합할 수 있다.

도구 선택은 목적에 따라 달라진다.

- **Mutex:** shared resource 보호, mutual exclusion, priority inheritance
- **Binary semaphore:** event signaling, ISR-to-task notification
- **Queue:** data/message ownership 전달
- **Direct-to-task notification:** 특정 task 하나를 빠르게 깨우기
- **Service task:** shared resource 접근을 한 task로 집중

---

## 8. Service Task 패턴

Priority inversion을 줄이는 한 방법은 shared resource를 여러 task가 직접 만지지 않게 하는 것이다.

예를 들어 serial port를 여러 task가 직접 쓰면 mutex가 필요하다. 대신 serial service task를 만들고, 다른 task는 queue로 출력 요청만 보낸다.

이렇게 하면 serial port ownership이 service task 하나로 모인다. Lock 수가 줄어들고, race condition, deadlock, priority inversion 위험도 줄어든다.

---

## 9. 실천 규칙

Priority inversion을 완화하려면 다음을 지켜야 한다.

- Critical section을 짧게 유지한다.
- Lock을 잡은 상태에서 `delay`, blocking I/O, long computation을 하지 않는다.
- High priority task가 기다릴 수 있는 lock의 worst-case hold time을 계산한다.
- Shared resource 접근을 queue나 service task로 직렬화한다.
- Mutex가 필요한 곳에는 binary semaphore 대신 mutex를 사용한다.
- 여러 lock을 쓴다면 lock 획득 순서를 일관되게 만든다.

---

## 참고 자료

- [Introduction to RTOS Part 11 - Priority Inversion | DigiKey](https://www.digikey.com/en/videos/d/digi-key-electronics/introduction-to-rtos-part-11-priority-inversion-digi-key-electronics)
- [Introduction to RTOS - Solution to Part 11 (Priority Inversion)](https://www.digikey.com/en/maker/projects/introduction-to-rtos-solution-to-part-11-priority-inversion/abf4b8f7cd4a4c70bece35678d178321)
- [What really happened on Mars rover Pathfinder](http://www.cs.cornell.edu/courses/cs614/1999sp/papers/pathfinder.html)
- [FreeRTOS Mutexes](https://www.freertos.org/Real-time-embedded-RTOS-mutexes.html)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Priority inversion은 low priority task가 가진 lock 때문에 high priority task가 실행되지 못하고 priority 구조가 뒤집히는 현상이다.
- **왜 필요:** RTOS에서는 high priority task가 deadline을 지켜야 하지만, shared resource와 mutex 때문에 low 또는 medium priority task가 이를 간접적으로 막을 수 있다.
- **동작:** Low priority task가 mutex를 들고 high priority task가 기다리면 bounded inversion이 생긴다. 여기에 medium priority task가 low priority task를 preempt하면 high priority task의 대기 시간이 제한되지 않는 unbounded inversion이 된다.
- **비교:** Priority ceiling은 lock을 잡는 순간 priority를 올리고, priority inheritance는 high priority task가 실제로 기다릴 때 lock holder의 priority를 올린다.
- **30초 통합 답변:**
  > Priority inversion은 낮은 priority task가 mutex 같은 lock을 들고 있어서 높은 priority task가 실행되지 못하는 상황입니다. Low task가 critical section을 끝낼 때까지만 기다리면 bounded inversion이고, medium priority task가 low task를 preempt해 lock release를 계속 늦추면 unbounded inversion이 됩니다. 이를 줄이기 위해 priority ceiling은 resource를 잡는 순간 priority를 올리고, priority inheritance는 high priority task가 기다릴 때 lock holder의 priority를 일시적으로 올립니다. 그래도 critical section은 짧게 유지하고, 가능하면 queue나 service task로 shared resource 접근을 단순화해야 합니다.
