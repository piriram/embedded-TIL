# Hardware Interrupts

**주제:** RTOS에서 hardware interrupt와 task를 함께 쓰는 방법, ESP32 timer interrupt, ISR critical section, `FromISR` API, binary semaphore를 이용한 deferred interrupt.
**원본 강의:** [Introduction to RTOS Part 9 - Hardware Interrupts | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch/qsflCf6ahXU)

---

## 1. Hardware Interrupt가 필요한 이유

Embedded system에서는 hardware interrupt가 매우 중요하다. 많은 microcontroller peripheral은 CPU가 계속 polling하지 않아도 특정 event가 발생했을 때 interrupt를 만들 수 있다.

대표적인 예시는 다음과 같다.

- Timer가 expire되거나 특정 count에 도달함
- Push button이 눌려 pin voltage가 바뀜
- Serial receive buffer가 가득 차 CPU에 처리 시점을 알림
- Communication bus peripheral이 hardware에서 data send/receive를 처리한 뒤 event를 알림

이런 경우 electrical signal이 CPU로 전달되거나 register 값이 바뀐다. 어느 쪽이든 processor에게 asynchronous event가 발생했으니 현재 하던 일을 멈추고 처리하라고 알린다.

이것이 hardware interrupt다.

Hardware interrupt 사용법 자체는 architecture와 chip에 강하게 의존한다. 실제 peripheral 설정은 사용하는 chip의 datasheet나 API를 확인해야 한다.

---

## 2. RTOS Task보다 Interrupt가 우선한다

대부분의 RTOS, 특히 FreeRTOS에서는 hardware interrupt가 어떤 task보다 높은 priority를 가진다.

Task priority가 아무리 높아도 hardware interrupt가 발생하면 현재 task execution은 멈추고 processor는 해당 **ISR(Interrupt Service Routine)** 을 실행한다.

ISR이 끝나면 다시 task execution으로 돌아간다. 다만 반드시 interrupt 직전에 실행 중이던 task로 돌아가는 것은 아니다. ISR이 semaphore를 give하거나 더 높은 priority task를 깨우면 scheduler가 다른 task를 선택할 수 있다.

일부 microcontroller는 한 번에 하나의 hardware interrupt만 허용하고, 일부는 interrupt가 다른 interrupt를 interrupt하는 **nested interrupt**를 허용한다. 이 시리즈에서는 nested interrupt를 깊게 다루지 않는다.

Task 안에서 일부 또는 전체 interrupt를 disable할 수도 있다. 하지만 이는 critical shared resource를 보호해야 할 때 제한적으로 사용해야 한다.

> **주의**
> Interrupt를 오래 막으면 다른 event 처리 latency가 증가한다. RTOS task 설계보다 더 낮은 수준의 timing 문제로 이어질 수 있으므로 남용하면 안 된다.

---

## 3. ESP32 Hardware Timer 기본

강의에서는 ESP32의 hardware timer를 사용해 RTOS tick timer보다 더 정밀한 간격으로 analog value를 sample하는 예제를 만든다.

ESP32에는 timer가 4개 있다. 각 timer는 다음 구성을 가진다.

- **16-bit prescaler**
- **64-bit counter**
- Default base timer clock: **80 MHz**

Prescaler 또는 divider는 clock divider다. Timer base clock이 80 MHz이고 divider를 80으로 설정하면 timer는 다음 속도로 count한다.

```text
80 MHz / 80 = 1 MHz
```

즉 timer counter는 1초에 1,000,000번 증가한다.

1 Hz hardware interrupt driven blinky를 만들려면 timer가 1 MHz로 tick할 때 max count를 1,000,000으로 설정하면 된다.

Divider 값은 16-bit variable에 들어갈 수 있어야 하고, max count는 64-bit variable에 들어갈 수 있어야 한다.

---

## 4. Timer ISR Blinky

첫 예제는 hardware timer ISR로 LED를 toggle하는 단순한 blinky다.

ESP32 Arduino package library의 HAL timer를 사용한다.

핵심 흐름은 다음과 같다.

1. Built-in LED pin을 output으로 설정한다.
2. Timer handle을 만든다.
3. Timer number 0을 사용하고 divider를 설정한다.
4. Timer가 max value에 도달했을 때 호출할 ISR callback을 등록한다.
5. Timer가 interrupt 후 자동 reload되도록 설정한다.
6. Timer interrupt를 enable하고 실행한다.

ESP32에서는 ISR이 flash가 아니라 internal RAM에 있도록 `IRAM_ATTR` qualifier를 붙인다. 더 빠르게 접근하기 위해서다.

```c
void IRAM_ATTR onTimer()
{
    // ISR body
}
```

Timer가 max count에 도달할 때마다 ISR이 호출되고 LED가 toggle된다. Max count를 1,000,000으로 두면 LED는 1초 켜지고 1초 꺼지는 패턴을 반복한다.

> **주의**
> 다른 microcontroller나 IDE에서는 timer interrupt 설정과 ISR attribute가 달라진다. 이 강의에서 중요한 것은 ESP32 API 자체보다 ISR과 FreeRTOS task를 어떻게 동기화하느냐다.

---

## 5. ISR과 Shared Counter

다음 예제에서는 ISR과 task가 같은 global counter를 공유한다.

Timer divider를 8로 바꾸면 timer count 속도는 다음과 같다.

```text
80 MHz / 8 = 10 MHz
```

Timer max count를 조정하면 ISR을 **100 millisecond**마다 실행할 수 있다.

Global counter는 ISR 안에서 바뀔 수 있으므로 `volatile` qualifier를 붙인다.

```c
volatile int isr_counter = 0;
```

`volatile`은 compiler에게 이 variable이 현재 실행 중인 task scope 밖에서 바뀔 수 있다고 알려준다. 여기서는 ISR이 값을 바꾼다.

`volatile`이 없으면 compiler는 variable이 사용되지 않는다고 판단하거나, 반복해서 memory에서 다시 읽을 필요가 없다고 최적화할 수 있다.

> **주의**
> `volatile`은 race condition을 해결하지 않는다. 단지 compiler optimization에 대한 가시성 문제를 줄일 뿐이다. Shared data의 atomicity와 synchronization은 별도로 설계해야 한다.

---

## 6. ESP-IDF FreeRTOS의 Spin Lock과 Critical Section

ESP-IDF version의 FreeRTOS에서는 다른 core의 task가 critical section에 들어오지 못하게 막기 위해 **spin lock**을 사용한다.

Spin lock은 mutex처럼 shared resource 접근을 제한하지만, lock을 얻으려는 task가 lock이 available해질 때까지 loop를 돌며 기다린다.

그래서 일반 mutex처럼 아무 곳에나 쓰면 안 된다. Current core가 spin lock에서 오래 기다리면 system responsiveness가 나빠질 수 있다.

ESP-IDF에서는 special critical section function과 함께 spin lock을 사용한다.

ISR 안에서 critical section에 들어가면 다음 효과가 생긴다.

- 다른 core의 task가 같은 spin lock으로 보호되는 critical section에 들어가지 못한다.
- Current core의 interrupt가 disable된다.
- Nested interrupt를 쉽게 막을 수 있다.

하지만 critical section 중에 다른 interrupt가 발생하면 처리 지연이 생길 수 있다. 경우에 따라 interrupt를 놓치는 것처럼 보일 수도 있다.

따라서 ISR은 짧아야 하고, ISR 안의 critical section은 더 짧아야 한다.

> **주의**
> FreeRTOS documentation은 critical section 안에서 다른 FreeRTOS API function을 호출하지 말라고 명시한다. Critical section 안에서는 shared variable increment처럼 아주 짧은 작업만 수행해야 한다.

---

## 7. Task 쪽 Critical Section

예제 task는 `printValues`라는 이름으로 global counter를 1씩 decrement하고, 각 값을 print한다.

ISR은 counter를 increment하고 task는 counter를 decrement하므로, 둘 다 같은 shared variable을 접근한다. 따라서 task 쪽 decrement도 critical section으로 보호해야 한다.

이때 일반 mutex는 적합하지 않다. Interrupt는 task처럼 block될 수 없고, ISR을 spin하게 만드는 것도 바람직하지 않다.

Task context에서는 non-ISR critical section function을 사용해 current core에서 interrupt와 context switch를 막고, spin lock으로 other core 접근을 막는다.

Vanilla FreeRTOS의 critical section은 ESP-IDF보다 단순하다. Vanilla FreeRTOS에서는 spin lock이 포함되지 않는다.

Hardware interrupt가 task critical section 중에 발생하면 interrupt가 사라지는 것은 아니다. ISR은 current execution이 critical section을 나가고 interrupt가 re-enable된 뒤 trigger된다.

---

## 8. ISR 실행과 Task 출력 관찰

예제에서는 task가 2초마다 실행되도록 delay를 둔다. 그 사이 ISR은 100ms마다 여러 번 실행되어 global counter를 증가시킨다.

Serial terminal에서는 counter가 2초마다 `19`부터 countdown되는 것을 볼 수 있다. 중간에 어떤 숫자가 반복되는 경우도 있다. 이는 serial print statement 사이에 interrupt가 trigger되어 ISR이 실행되었기 때문이다.

이 동작은 예상된 것이다. ISR은 task와 별도로 asynchronous하게 실행되어야 한다.

---

## 9. ISR에서 FreeRTOS API를 부를 때의 규칙

ISR 안에서는 일반 FreeRTOS API를 그대로 호출하면 안 된다.

ISR context에서는 block할 수 없다. ISR은 task가 아니기 때문에 mutex나 semaphore를 기다리며 block 상태로 들어갈 수 없다.

따라서 ISR에서 사용할 수 있도록 별도로 제공되는 API를 사용해야 한다. FreeRTOS에서는 보통 함수 이름 끝에 `FromISR`이 붙는다.

예시는 다음과 같다.

- `xSemaphoreGiveFromISR()`
- `xQueueSendFromISR()`
- `portYIELD_FROM_ISR()` 또는 ESP-IDF의 yield-from-ISR 방식

`FromISR` 함수는 block하지 않는다. Mutex나 semaphore를 take하려 했는데 unavailable하다면 기다리는 대신 다른 방식으로 처리해야 한다.

---

## 10. Binary Semaphore로 Deferred Interrupt 만들기

ISR은 가능한 짧아야 한다. Heavy processing은 ISR 안에서 직접 하지 않고 task로 미루는 것이 좋다.

이 구조를 **deferred interrupt**라고 볼 수 있다.

흐름은 다음과 같다.

1. Task B는 binary semaphore를 기다리며 blocked state에 있다.
2. Task A 또는 idle task가 실행 중이다.
3. Hardware interrupt가 발생하고 ISR이 실행된다.
4. ISR은 shared resource를 갱신하거나 buffer에 data를 넣는다.
5. ISR은 `xSemaphoreGiveFromISR()`로 binary semaphore를 give한다.
6. 더 높은 priority task가 unblock되었다면 ISR 종료 직후 scheduler가 실행된다.
7. Scheduler는 방금 깨어난 Task B를 선택할 수 있다.
8. Task B가 ISR이 준비한 data를 처리한다.

이렇게 하면 ISR은 data 준비와 signal만 담당하고, 실제 계산은 task에서 수행한다.

예를 들어 FFT(Fast Fourier Transform) 같은 heavy calculation은 ISR에서 수행하지 않고 task에서 처리해야 한다. 그래야 다른 task에게도 실행 기회가 생긴다.

> **이미지 필요**
> Hardware interrupt가 binary semaphore를 give하고, blocked high-priority task가 깨어나 ISR 이후 바로 실행되는 timing chart
> - 출처: 강의 08:36~10:08 구간
> - 대체안: Task A, Task B, ISR, semaphore 상태를 포함한 직접 작성 타임라인

---

## 11. ADC Sampling 예제

다음 demo에서는 timer ISR이 **1초마다** 실행되도록 divider와 max count를 조정한다.

ISR 안에서는 ADC(analog-to-digital converter)를 읽고, 결과를 global variable에 저장한다. 그리고 binary semaphore로 reading task에게 새 ADC value가 준비되었음을 알린다.

ISR 안에서는 semaphore를 give할 때 반드시 ISR용 함수를 사용한다.

```c
xSemaphoreGiveFromISR(binary_sem, &task_woken);
```

많은 `FromISR` 함수는 `task_woken` 같은 special parameter를 가진다. 이 값은 semaphore give 때문에 더 높은 priority task가 unblock되었는지 기록한다.

더 높은 priority task가 unblock되었다면 ISR이 끝나자마자 scheduler가 그 task를 실행할 수 있도록 yield-from-ISR API를 호출해야 한다.

ESP-IDF version은 이 yield function에 parameter를 직접 넘기지 않으므로, `if` statement로 같은 효과를 만든다고 설명한다.

Task 쪽에서는 binary semaphore를 forever wait한다.

```c
xSemaphoreTake(binary_sem, portMAX_DELAY);
```

Semaphore가 ISR에 의해 available해지면 task가 깨어나 ADC value를 serial terminal에 출력한다.

Setup에서는 binary semaphore를 만들고, creation result가 `NULL`이 아닌지 확인하는 것이 좋다. Demo에서는 `printValues` task를 priority **2**로 실행한다. 이는 ESP32 Arduino의 setup/loop task priority보다 높다.

실행하면 serial terminal에 ADC value가 1초에 한 번씩 출력된다.

---

## 12. Direct-to-Task Notification

Newer FreeRTOS version에는 **direct-to-task notification**이 있다.

어떤 task가 특정 data를 기다리고 있는지 정확히 알고 있다면 semaphore 대신 task notification을 사용할 수 있다.

Task notification의 장점은 semaphore보다 빠르고 효율적이라는 점이다.

> **예외**
> Binary semaphore는 ISR과 task 동기화의 좋은 학습 도구이지만, 실제 설계에서 단일 task만 깨우면 되는 구조라면 direct-to-task notification이 더 적합할 수 있다.

---

## 13. Challenge: ADC 평균 계산과 Serial Command

이번 challenge는 앞선 여러 강의의 개념을 종합하는 final project에 가깝다.

요구사항은 다음과 같다.

1. Hardware timer가 ISR을 실행한다.
2. ISR은 ADC를 **초당 10번** sample한다.
3. ADC value는 buffer에 저장한다.
4. **1초 동안 10개 sample**이 모이면 ISR은 Task A를 깨운다.
5. Task A는 10개 sample의 average를 계산한다.
6. Average는 floating point value로 global variable에 저장한다.
7. Task B는 serial terminal을 담당한다.
8. Task B는 들어오는 character를 echo back한다.
9. User가 `avg` command를 입력하면 global average value를 출력한다.

강사는 double buffer 또는 circular buffer 사용을 권장한다. ISR이 buffer 한쪽을 계속 채우는 동안 Task A가 다른 쪽을 읽을 수 있게 하기 위해서다.

또 buffer overrun도 고려해야 한다. Buffer overrun은 ISR이 Task A가 아직 읽지 않은 element에 새 data를 쓰려고 할 때 발생한다.

Average는 floating point global variable이고, 이 값은 single instruction cycle 안에서 read/write된다고 가정할 수 없다. 따라서 Task A가 average를 쓰고 Task B가 average를 읽는 부분도 synchronization이 필요하다.

이 구조는 RTOS에서 흔한 design pattern이다.

- ISR: sampling처럼 timing이 중요한 짧은 작업
- Task A: incoming data에 대한 complex calculation
- Task B: user input/output

16 kHz audio data를 다루고 real-time FFT를 계산하며 console에 결과를 표시하는 구조도 이 pattern으로 확장할 수 있다. 이상적으로는 DMA(Direct Memory Access) controller가 sampling을 도와주면 좋지만, ISR과 task synchronization 원리는 비슷하다.

---

## 참고 자료

- [Introduction to RTOS Part 9 - Hardware Interrupts | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch/qsflCf6ahXU)
- [FreeRTOS Interrupt Management](https://www.freertos.org/RTOS-Cortex-M3-M4.html)
- [FreeRTOS `xSemaphoreGiveFromISR()`](https://www.freertos.org/a00124.html)
- [FreeRTOS Direct-to-Task Notifications](https://www.freertos.org/RTOS-task-notifications.html)
- [ESP-IDF FreeRTOS Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/freertos.html)
- [ESP-IDF Heap and System API Reference](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/index.html)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** RTOS에서 hardware interrupt는 task보다 높은 priority로 실행되는 asynchronous event 처리 메커니즘이며, ISR은 짧게 끝내고 무거운 처리는 task로 defer해야 한다.
- **왜 필요:** Timer, GPIO, ADC, serial buffer 같은 peripheral event는 RTOS tick보다 더 정확하거나 즉각적인 처리가 필요할 수 있다. 하지만 ISR에서 오래 작업하면 다른 interrupt와 task scheduling을 지연시킨다.
- **동작:** ISR은 shared data를 짧게 갱신하고 `xSemaphoreGiveFromISR()` 같은 `FromISR` API로 task를 깨운다. 더 높은 priority task가 unblock되면 yield-from-ISR을 통해 ISR 직후 scheduler가 그 task를 실행하게 할 수 있다.
- **비교:** 일반 mutex/semaphore API는 task context용이라 ISR에서 block할 수 없고, ISR에서는 `FromISR` API를 써야 한다. 단일 task를 깨우는 구조에서는 binary semaphore보다 direct-to-task notification이 더 빠르고 효율적일 수 있다.
- **30초 통합 답변:**
  > RTOS에서 hardware interrupt는 어떤 task보다 높은 priority로 실행되는 asynchronous event 처리 방식입니다. Timer나 ADC 같은 peripheral event는 ISR에서 즉시 감지하되, ISR은 shared data 저장이나 semaphore give처럼 짧은 일만 하고 무거운 계산은 task로 넘기는 것이 좋습니다. FreeRTOS에서는 ISR 안에서 일반 API를 쓰지 않고 `xSemaphoreGiveFromISR()` 같은 `FromISR` API를 사용해야 하며, 더 높은 priority task가 깨어났다면 yield-from-ISR로 ISR 직후 바로 실행되게 할 수 있습니다. 단일 task만 깨우는 경우에는 binary semaphore보다 direct-to-task notification이 더 효율적일 수 있습니다.
