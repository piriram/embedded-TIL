# Software Timer

**주제:** FreeRTOS software timer의 동작 구조, timer service task, one-shot/auto-reload timer, callback 주의사항, LCD backlight auto-dim 패턴.
**원본 강의:** [Introduction to RTOS Part 8 - Software Timer | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch/b1f1Iex0Tso)

---

## 1. Software Timer가 필요한 이유

Microcontroller program에서는 어떤 일을 일정 시간 뒤에 실행하거나 주기적으로 실행해야 하는 일이 많다.

예를 들면 다음과 같다.

- LED blinking
- LCD refresh
- Sensor polling
- Servo motor pulse generation
- 일정 시간 inactivity 후 backlight 끄기

가장 단순한 방법은 별도 task를 만들고 `vTaskDelay()`로 block state에 넣었다가 주기적으로 깨우는 것이다. 하지만 ESP32의 FreeRTOS task는 stack과 TCB 때문에 대략 1KB에 가까운 overhead가 생길 수 있다.

주기적 작업 하나를 위해 task를 매번 만드는 것은 부담이 클 수 있다. 이때 software timer를 사용할 수 있다.

---

## 2. 다른 방법들과의 비교

주기 실행을 구현하는 방법은 여러 가지다.

첫 번째는 별도 task를 만들고 `vTaskDelay()`를 사용하는 방식이다. 구현은 쉽지만 task overhead가 생긴다.

두 번째는 기존 task 안에서 `xTaskGetTickCount()`를 호출해 scheduler가 시작된 뒤 경과한 tick 수를 확인하는 방식이다. Arduino의 `millis()`와 비슷하게 timestamp를 비교해 실행 시점을 판단할 수 있다.

세 번째는 hardware timer를 쓰는 방식이다. 1 tick보다 더 높은 정밀도가 필요하면 hardware timer가 필요하다. 다만 microcontroller의 hardware timer 수는 제한되어 있고, timer 설정 코드는 architecture-specific이라 portable하지 않다.

네 번째가 FreeRTOS의 **software timer**다. Software timer는 operating system level에서 제공되며, timer가 expire되면 arbitrary callback function을 호출할 수 있다.

> **주의**
> FreeRTOS software timer는 tick timer에 의존한다. 기본 tick이 1ms라면 1ms보다 더 정밀한 software timer는 만들 수 없다.

---

## 3. Timer Service Task

FreeRTOS timer library를 사용하면 scheduler가 시작될 때 background에서 특별한 task가 생성된다.

이 task를 **timer service task** 또는 **timer daemon**이라고 부른다.

Timer service task의 역할은 다음과 같다.

- Timer list를 유지한다.
- 각 timer의 expire 시점을 관리한다.
- Timer가 expire되면 연결된 callback function을 호출한다.
- Timer create/start/stop/reset 같은 command를 queue를 통해 처리한다.

Timer service task는 계속 CPU를 점유하지 않는다. 자신이 관리하는 timer list를 보고 다음 expire 시점까지 block되었다가, tick timer가 해당 시점에 도달하면 깨어나 callback을 실행한다.

---

## 4. Timer Callback의 성격

Timer가 expire되면 호출되는 function을 **callback function**이라고 한다.

Callback은 timer 생성 시 argument로 전달되고, timer service task 안에서 실행된다. 따라서 callback은 timer service task와 같은 priority level에서 실행된다.

이 때문에 timer callback은 ISR처럼 다뤄야 한다.

- 빨리 끝내야 한다.
- Blocking하면 안 된다.
- `delay()`나 오래 걸리는 computation을 피해야 한다.
- Queue, mutex, semaphore를 사용할 때 block time을 주지 않아야 한다.

Callback이 오래 걸리거나 block되면 timer service task 자체가 막힌다. 그러면 다른 timer callback과 timer command 처리도 지연된다.

---

## 5. Timer Command Queue

우리는 timer service task를 직접 제어하지 않는다.

FreeRTOS는 timer service task와 통신하기 위한 queue와 API function을 제공한다. `xTimerStart()`, `xTimerStop()`, `xTimerReset()` 같은 API를 호출하면 command가 timer command queue에 들어간다.

Timer service task는 queue에서 command를 읽고 필요한 작업을 수행한다.

이 설계는 별도 task overhead를 만들지만, 하나의 timer service task가 여러 software timer를 관리할 수 있게 한다.

---

## 6. FreeRTOSConfig.h의 Timer 설정

Software timer를 쓰려면 `FreeRTOSConfig.h`에서 timer support가 켜져 있어야 한다.

```c
#define configUSE_TIMERS 1
```

ESP32 Arduino의 FreeRTOS는 timer support가 기본으로 포함되어 있어 보통 별도 수정이 필요 없다.

관련 설정에는 다음이 있다.

- Timer service task priority
- Timer command queue length
- Timer service task stack size

강의에서 확인한 ESP32 설정은 다음과 같다.

- Timer service task priority: **1**
- Command queue length: **10**
- Stack depth: **2KB**

Vanilla FreeRTOS에서는 stack depth 단위가 bytes가 아니라 words일 수 있다는 점을 주의해야 한다.

---

## 7. Software Timer API

FreeRTOS timer API는 timer 생성, 삭제, 시작, 정지, reset을 제공한다.

대표 함수는 다음과 같다.

- `xTimerCreate()`
- `xTimerStart()`
- `xTimerStop()`
- `xTimerReset()`
- `xTimerDelete()`
- `pvTimerGetTimerID()`
- `xTimerGetTimerDaemonTaskHandle()`

ISR 안에서 timer service task에 command를 보내야 한다면 `FromISR` variant를 사용해야 한다. ISR에서는 timer command queue가 full이어도 block할 수 없기 때문이다.

`xTimerGetTimerDaemonTaskHandle()`로 timer service task handle을 얻을 수 있지만, service task를 직접 조작하는 것은 권장되지 않는다. Priority를 바꾸고 싶다면 runtime에 handle로 조작하기보다 config file에서 설정하는 편이 낫다.

---

## 8. `xTimerCreate()` Parameter

Timer는 `xTimerCreate()`로 만든다.

```c
TimerHandle_t timer = xTimerCreate(
    "Timer Name",
    1000 / portTICK_PERIOD_MS,
    pdFALSE,
    (void *)0,
    callbackFunction
);
```

Parameter 의미는 다음과 같다.

- **Timer name:** debugging용 문자열
- **Period:** timer 길이, tick 단위
- **Auto reload:** `pdTRUE`면 반복 실행, `pdFALSE`면 one-shot
- **Timer ID:** callback에서 timer를 구분하거나 상태를 기억하는 데 쓰는 `void *`
- **Callback function:** timer expire 시 호출될 function

Timer 생성에는 heap memory가 필요하므로 실패할 수 있다. Return handle이 `NULL`인지 확인해야 한다.

---

## 9. One-Shot Timer

**One-shot timer**는 설정한 시간이 지난 뒤 callback을 한 번만 호출한다.

예를 들어 2초짜리 one-shot timer를 시작하면, 2초 뒤 callback이 실행되고 timer는 멈춘다. 다시 실행하려면 다른 task에서 timer를 다시 start하거나 reset해야 한다.

Timer callback function은 다음 형태다.

```c
void callbackFunction(TimerHandle_t xTimer)
{
    // timer expired
}
```

Parameter로 들어오는 timer handle을 사용하면 여러 timer가 같은 callback을 공유할 때 어느 timer가 expire되었는지 확인할 수 있다.

---

## 10. Auto-Reload Timer

**Auto-reload timer**는 expire될 때마다 callback을 호출하고, 자동으로 다시 시작된다.

`xTimerCreate()`의 auto reload parameter를 `pdTRUE`로 설정하면 된다.

One-shot timer와 auto-reload timer가 같은 callback을 사용할 수도 있다. 이때 timer ID를 다르게 설정하고, callback 안에서 `pvTimerGetTimerID()`로 ID를 읽어 구분한다.

```c
uint32_t timer_id = (uint32_t)pvTimerGetTimerID(xTimer);
```

강의 예제에서는 timer ID `0`은 one-shot timer, timer ID `1`은 auto-reload timer로 구분한다.

실행하면 auto-reload timer는 1초마다 계속 callback을 호출하고, one-shot timer는 한 번 callback을 호출한 뒤 멈춘다.

---

## 11. `xTimerStart()`와 Command Queue Wait

Timer를 시작하려면 `xTimerStart()`를 호출한다.

```c
xTimerStart(timer, portMAX_DELAY);
```

두 번째 parameter는 timer command queue가 full일 때 얼마나 기다릴지 정하는 block time이다.

`portMAX_DELAY`를 주면 queue가 full인 경우 사실상 계속 기다리라는 뜻이다. Task context에서는 가능하지만, ISR context에서는 이런 blocking wait를 하면 안 된다.

`xTimerStart()`는 이미 실행 중인 timer에 대해 호출되면 timer counter를 restart할 수 있다. 이 성질은 inactivity timeout을 구현할 때 유용하다.

---

## 12. Challenge: LCD Backlight Auto-Dim

강의 challenge는 ESP32 LED를 LCD backlight라고 가정하고 auto-dim 기능을 만드는 것이다.

요구사항은 다음과 같다.

1. 새 task에서 serial terminal character를 읽는다.
2. 들어온 character를 serial terminal에 echo한다.
3. Character가 입력되면 LED를 켠다.
4. 마지막 character 입력 후 **5초** 동안 inactivity가 있으면 LED를 끈다.
5. LED off는 software timer callback에서 수행한다.

핵심 힌트는 `xTimerStart()`다. Timer가 expire되기 전에 `xTimerStart()`를 다시 호출하면 counter가 restart된다.

즉 serial input이 들어올 때마다 one-shot timer를 5초로 다시 시작하면, 마지막 입력으로부터 5초가 지난 뒤에만 callback이 실행되어 LED를 끌 수 있다.

---

## 참고 자료

- [Introduction to RTOS Part 8 - Software Timer | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch/b1f1Iex0Tso)
- [FreeRTOS Software Timers](https://www.freertos.org/RTOS-software-timer.html)
- [FreeRTOS Timer API](https://www.freertos.org/FreeRTOS-Software-Timer-API-Functions.html)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** FreeRTOS software timer는 tick timer를 기반으로 일정 시간 뒤 또는 주기적으로 callback을 실행하는 OS-level timer다.
- **왜 필요:** 단순 주기 작업마다 task를 만들면 stack과 TCB overhead가 크고, hardware timer는 개수가 제한되며 architecture-specific이다.
- **동작:** Timer service task가 timer list와 command queue를 관리하고, timer가 expire되면 callback을 실행한다. Callback은 timer service task context에서 실행되므로 빠르게 끝나야 하고 block하면 안 된다.
- **비교:** One-shot timer는 한 번 expire된 뒤 멈추고, auto-reload timer는 expire 후 자동으로 다시 시작된다. 1 tick보다 높은 정밀도가 필요하면 software timer가 아니라 hardware timer를 써야 한다.
- **30초 통합 답변:**
  > FreeRTOS software timer는 OS의 tick timer를 기반으로 특정 시간 뒤 또는 주기적으로 callback을 실행하는 기능입니다. 별도 task를 만들면 stack과 TCB overhead가 생기고, hardware timer는 수가 제한되어 있으므로 가벼운 주기 작업에는 software timer가 유용합니다. Timer service task가 timer list와 command queue를 관리하며, callback은 이 task context에서 실행되므로 ISR처럼 짧고 non-blocking으로 작성해야 합니다. One-shot timer는 한 번만 실행되고 auto-reload timer는 반복 실행되며, tick보다 더 정밀한 timing은 hardware timer가 필요합니다.
