# Mutex

**주제:** Race condition이 발생하는 이유, critical section과 mutual exclusion의 의미, FreeRTOS mutex로 shared resource를 보호하는 방법.
**원본 강의:** [Introduction to RTOS Part 6 - Mutex | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch/I55auRpbiTs)

---

## 1. Race Condition이 왜 생기는가

Concurrent programming에서는 두 개 이상의 task가 같은 shared resource를 다룰 때 문제가 생길 수 있다.

대표적인 예가 global variable을 counter처럼 사용하는 경우다. 두 task가 같은 global variable을 읽고, 값을 수정하고, 다시 쓰는 작업을 동시에 수행하면 결과가 실행 순서에 따라 달라질 수 있다.

이런 문제를 **race condition**이라고 한다. Race condition은 electronics와 software에서 모두 쓰는 용어이며, system behavior가 우리가 통제할 수 없는 event timing에 의존할 때 발생한다.

예를 들어 `shared_var++`처럼 보이는 코드도 대부분의 architecture에서는 한 instruction cycle로 끝나지 않는다. 일반적으로 다음 단계가 필요하다.

1. Memory에서 shared variable 값을 읽는다.
2. Register, cache memory, local variable 같은 곳에 값을 임시로 저장한다.
3. 값을 increment한다.
4. 수정된 값을 다시 memory에 쓴다.

이 과정 중간에 context switch가 일어나면 다른 task가 아직 갱신되지 않은 값을 읽을 수 있다.

---

## 2. Increment 예제로 보는 Race Condition

Global variable이 처음에 `2`라고 하자.

Task A가 먼저 실행되어 global variable 값을 읽고 local로 보관한다. 아직 memory에 다시 쓰기 전이다. 이때 context switch가 발생해 Task B가 실행된다.

Task B도 global variable을 읽는다. Task A가 아직 write back을 하지 않았으므로 Task B도 값 `2`를 읽는다. Task B는 이를 `3`으로 increment하고 global variable에 `3`을 쓴다.

그 다음 Task A가 다시 실행된다. Task A는 자신이 local에 보관하고 있던 값 `2`를 `3`으로 increment한 뒤 global variable에 다시 `3`을 쓴다.

결과적으로 Task A와 Task B가 모두 실행되었지만 global variable은 `2`에서 `3`으로 한 번만 증가한다.

> 두 task가 각각 한 번씩 increment했는데 counter가 한 번만 증가했다면, 결과가 task instruction의 정확한 실행 순서에 의존한 것이다. 이것이 race condition이다.

---

## 3. Queue로 해결하기 어려운 Shared State

이전 강의에서 queue는 inter-task communication 방법으로 사용되었다. Queue를 사용하면 task 사이에 message를 전달하면서 shared resource 문제를 피할 수 있다.

하지만 모든 문제가 queue로 깔끔하게 해결되지는 않는다.

예를 들어 global variable을 flag나 counter로 계속 유지해야 하고, 여러 task가 그 값을 읽어야 한다면 queue만으로는 충분하지 않을 수 있다.

이때 shared resource에 접근하는 code section을 보호할 다른 kernel object가 필요하다. FreeRTOS에서는 semaphore와 mutex 같은 도구를 사용할 수 있다.

---

## 4. Critical Section과 Mutual Exclusion

Shared resource를 읽고, 수정하고, 다시 쓰는 code section을 **critical section**이라고 부른다.

Critical section은 한 task가 들어가면 끝까지 실행되어야 한다. 다른 task가 같은 critical section에 동시에 들어가면 shared resource 상태가 깨질 수 있다.

다른 task가 critical section에 들어오지 못하게 배제하는 개념을 **mutual exclusion**이라고 한다.

Mutual exclusion을 강제하는 방법은 여러 가지다.

- Queue를 이용한 locking/message system
- Lock
- Mutex
- Semaphore

FreeRTOS에서는 mutex와 semaphore가 내부적으로 queue 기반으로 구현된다. 그래서 FreeRTOS API에서는 mutex도 semaphore 계열 object로 일반화되어 다뤄진다.

---

## 5. Lock, Mutex, Semaphore의 차이

Concurrent programming에서 **lock**은 한 번에 하나의 thread만 특정 code section에 들어갈 수 있도록 하는 system이다.

**Mutex**는 mutual exclusion의 줄임말이다. 넓은 OS 문맥에서는 system의 여러 process에 걸쳐 동작하는 lock처럼 설명할 수 있다.

FreeRTOS 환경에서는 보통 하나의 process만 실행한다고 볼 수 있으므로, lock과 mutex를 거의 같은 의미로 이해해도 된다.

**Semaphore**는 mutex와 비슷하지만 counter를 가진다. 이 counter를 통해 제한된 수의 thread가 동시에 critical section에 들어가도록 만들 수 있다.

실무에서는 semaphore가 단순 mutual exclusion보다 **다른 thread/task에 signal을 보내는 수단**으로 자주 쓰인다. 강의에서는 semaphore를 다음 lecture에서 다룬다고 설명한다.

> **주의**
> Mutex는 shared resource를 한 번에 하나의 task만 쓰게 하는 데 적합하고, semaphore는 event signaling이나 제한된 resource count를 표현하는 데 더 자연스러운 경우가 많다.

---

## 6. Mutex를 열쇠로 이해하기

강의에서는 작은 coffee shop의 restroom key로 mutex를 설명한다.

Restroom은 shared resource다. 한 번에 한 사람만 사용할 수 있다. Counter 위 basket에 restroom key가 놓여 있고, restroom을 쓰려는 사람은 key를 가져간다.

Key를 가진 사람만 restroom을 사용할 수 있다. 사용이 끝나면 key를 다시 basket에 돌려놓는다. 다른 사람이 restroom을 쓰고 싶어도 key가 없으면 기다려야 한다.

이때 restroom key가 mutex와 같다.

- Shared resource: restroom 또는 global variable
- Mutex: shared resource에 접근할 수 있는 key
- Take: key를 가져감
- Give: key를 돌려줌
- Waiting task: key가 돌아올 때까지 기다리거나 다른 일을 함

이 모델은 global variable 같은 shared resource에 한 번에 하나의 thread만 접근하도록 제한하는 방식을 직관적으로 보여준다.

---

## 7. Mutex 동작 흐름

Mutex는 `0` 또는 `1` 같은 boolean value로 단순화해 생각할 수 있다.

Task A가 critical section에 들어가기 전에 mutex가 available한지 확인하고, available하다면 mutex를 take한다. 이 check-and-take 동작은 반드시 **atomic**해야 한다.

Atomic하다는 것은 mutex를 확인하고 가져가는 중간에 다른 task가 끼어들 수 없다는 뜻이다. 일부 processor architecture는 이를 위해 test-and-set 같은 special assembly instruction을 제공한다.

Task A가 mutex를 take하면 mutex는 unavailable 상태가 된다. Task A는 critical section을 실행한다.

이때 Task B가 preempt되어 실행되더라도, Task B는 같은 critical section에 들어가기 전에 mutex를 확인해야 한다. Mutex가 unavailable하므로 Task B는 실패하고 yield하거나 다른 일을 해야 한다.

Task A가 critical section을 끝내면 mutex를 give한다. 그러면 mutex가 available 상태가 되고, Task B가 다음에 실행될 때 mutex를 take한 뒤 critical section에 들어갈 수 있다.

결과적으로 다른 task가 interrupt할 수는 있어도, 같은 shared resource를 보호하는 critical section에는 동시에 들어갈 수 없다.

> **이미지 필요**
> Task A가 mutex를 take한 뒤 critical section을 실행하고, Task B가 대기했다가 mutex 반환 후 진입하는 순서도
> - 출처: 강의 07:36~09:32 구간
> - 대체안: restroom key analogy와 task timeline을 결합한 직접 작성 다이어그램

---

## 8. FreeRTOS에서 Mutex 만들기

Vanilla FreeRTOS에서 semaphore와 mutex를 사용하려면 보통 semaphore header를 include해야 한다.

```c
#include "semphr.h"
```

FreeRTOS는 semaphore와 mutex를 비슷한 방식으로 구현하므로, mutex handle도 semaphore type으로 다룬다.

Global mutex handle은 다음처럼 선언할 수 있다.

```c
SemaphoreHandle_t mutex;
```

`setup()`에서 task를 만들기 전에 mutex를 생성한다.

```c
mutex = xSemaphoreCreateMutex();
```

`xSemaphoreCreateMutex()`의 return value를 global mutex handle에 저장하면 mutex 생성은 끝난다.

---

## 9. `xSemaphoreTake()`와 `xSemaphoreGive()`

Task function에서는 critical section에 들어가기 전에 `xSemaphoreTake()`로 mutex를 얻으려고 시도한다.

```c
if (xSemaphoreTake(mutex, 0) == pdTRUE) {
    // critical section
    xSemaphoreGive(mutex);
} else {
    // mutex를 얻지 못했을 때 다른 작업
}
```

`xSemaphoreTake()`의 첫 번째 parameter는 mutex handle이다. 두 번째 parameter는 timeout tick 수다.

두 번째 parameter를 `0`으로 두면 non-blocking 동작이 된다. Mutex를 즉시 얻을 수 없으면 기다리지 않고 바로 `pdFALSE`를 return한다.

Mutex를 얻으면 `pdTRUE`를 return하고 critical section을 실행할 수 있다. Critical section이 끝나면 반드시 `xSemaphoreGive()`로 mutex를 반환해야 한다.

`else` block에는 mutex를 얻지 못했을 때 수행할 다른 작업을 넣을 수 있다. 이렇게 하면 task가 mutex를 기다리는 동안에도 완전히 멈춰 있지 않고 유용한 일을 할 수 있다.

> **주의**
> Mutex를 take한 뒤 모든 코드 경로에서 반드시 give해야 한다. 중간 return, error path, exception-like 흐름에서 give를 빠뜨리면 다른 task가 영원히 critical section에 들어가지 못할 수 있다.

---

## 10. Race Condition Demo에 Mutex 적용하기

강의의 demo program은 두 task가 같은 `incTask` function을 실행한다.

문제를 관찰하기 쉽게 하기 위해 단순한 `shared_var++` 대신 일부러 나쁜 increment section을 만든다.

1. Global variable을 local variable로 copy한다.
2. Local value를 increment한다.
3. Random하게 **100~500 millisecond** 기다린다.
4. Local value를 global variable에 write back한다.
5. Global variable 값을 print한다.

Mutex 없이 실행하면 counter가 정상적으로 증가하다가도 같은 값이 반복될 수 있다. 이는 두 task가 같은 old value를 읽고 각각 write back했기 때문이다.

Mutex를 적용하면 read-modify-write 전체가 critical section으로 보호된다. 그러면 한 task가 global variable을 읽고 수정해 write back하는 동안 다른 task는 같은 code section에 들어가지 못한다.

Serial monitor에서는 counter가 더 이상 같은 값으로 반복되지 않고 의도대로 증가하는 것을 확인할 수 있다.

---

## 11. ISR에서 Mutex와 Semaphore를 다룰 때

Queue에서와 마찬가지로, interrupt service routine 안에서 일반 mutex/semaphore API를 그대로 사용하면 안 된다.

기본 함수인 `xSemaphoreTake()`나 `xSemaphoreGive()`를 ISR에서 직접 사용하는 대신, ISR용 API를 사용해야 한다.

FreeRTOS에서는 이런 목적으로 `FromISR` suffix가 붙은 함수들이 제공된다.

> **주의**
> ISR에서는 blocking 동작을 할 수 없고 scheduler와의 상호작용도 task context와 다르다. Mutex와 semaphore를 ISR에서 다뤄야 한다면 반드시 ISR용 API와 해당 제약을 확인해야 한다.

---

## 12. Task Parameter와 Local Stack Memory 문제

강의 마지막 challenge는 task parameter 전달 문제를 mutex로 우회해 보는 것이다.

FreeRTOS documentation은 task를 만들 때 local stack memory에 있는 argument를 넘기지 말라고 강하게 경고한다.

문제는 다음 순서로 발생한다.

1. `setup()` 또는 calling function에서 local variable을 만든다.
2. 그 local variable의 address를 task parameter로 넘긴다.
3. 새 task가 실행되어 parameter를 copy하기 전에 calling function이 끝난다.
4. Local variable은 scope를 벗어나 사라진다.
5. 새 task가 dereference한 값은 이미 유효하지 않거나 default처럼 보이는 값이 된다.

강의 예제에서는 user가 serial terminal에 입력한 number를 `delay_arg` pointer로 task에 넘긴다. 이 값은 `setup()`/`loop()` task의 stack memory에 있다.

`blinkLED` task가 parameter pointer를 dereference해서 local variable에 저장하기 전에 `setup()`이 끝나면, 전달한 값은 더 이상 안전하지 않다. 실행 결과 `num`이 기대한 값이 아니라 `0`으로 설정될 수 있다.

---

## 13. Challenge: Mutex로 Parameter Copy를 기다리기

Challenge는 mutex를 사용해 `setup()`이 parameter variable을 가진 상태로 너무 빨리 종료되지 않게 만드는 것이다.

목표는 `blinkLED` task가 parameter pointer를 dereference하고 값을 자기 local variable에 copy할 때까지 `setup()`이 빠져나가지 않도록 조정하는 것이다.

강사는 이것이 올바른 mutex 사용법은 아니라고 분명히 말한다. 실제로는 mutex라기보다 task 간 signal에 가깝고, 다음 강의의 semaphore가 더 자연스러운 도구다.

> **예외**
> 이 challenge는 학습을 위한 hack이다. Local stack memory의 주소를 task parameter로 넘기는 방식 자체가 위험하므로, 실제 firmware에서는 static/global storage, heap allocation, queue, semaphore 같은 더 명확한 lifetime 관리 방식을 선택해야 한다.

---

## 참고 자료

- [Introduction to RTOS Part 6 - Mutex | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch/I55auRpbiTs)
- [FreeRTOS Semaphore / Mutex API](https://www.freertos.org/a00113.html)
- [FreeRTOS `xSemaphoreCreateMutex()`](https://www.freertos.org/CreateMutex.html)
- [FreeRTOS `xSemaphoreTake()`](https://www.freertos.org/a00122.html)
- [FreeRTOS `xSemaphoreGive()`](https://www.freertos.org/a00123.html)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Mutex는 shared resource의 critical section에 한 번에 하나의 task만 들어가도록 보장하는 mutual exclusion 도구다.
- **왜 필요:** 여러 task가 global counter 같은 shared resource를 read-modify-write하면 context switch 순서에 따라 update가 유실되는 race condition이 생길 수 있다.
- **동작:** Task는 critical section에 들어가기 전에 `xSemaphoreTake()`로 mutex를 얻고, 작업이 끝나면 `xSemaphoreGive()`로 반환한다. Mutex를 얻지 못한 task는 기다리거나 다른 작업을 수행한다.
- **비교:** Queue는 message passing으로 shared resource 접근 자체를 줄이는 데 유용하고, mutex는 반드시 공유해야 하는 resource를 보호한다. Semaphore는 mutex와 비슷하지만 counter와 signaling 용도로 더 자주 쓰인다.
- **30초 통합 답변:**
  > Mutex는 shared resource를 다루는 critical section에 한 번에 하나의 task만 들어가게 하는 mutual exclusion 도구입니다. 예를 들어 두 task가 같은 global counter를 읽고 증가시킨 뒤 다시 쓰면, 중간 context switch 때문에 두 task가 실행됐는데 counter는 한 번만 증가하는 race condition이 생길 수 있습니다. FreeRTOS에서는 mutex도 semaphore 계열 API로 다루며, task가 `xSemaphoreTake()`로 mutex를 얻은 뒤 critical section을 실행하고 끝나면 `xSemaphoreGive()`로 반환합니다. Queue가 message passing으로 공유를 줄이는 방법이라면, mutex는 반드시 공유해야 하는 resource를 보호하는 방법입니다.
