# FreeRTOS Software Timer

**주제:** FreeRTOS software timer의 필요성, timer service task와 command queue, one-shot/auto-reload timer, callback 작성 원칙, LCD backlight auto-dim 패턴.

**원본 강의:** [Introduction to RTOS Part 8 - Software Timer | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch?v=b1f1Iex0Tso)

---

## 1. Software Timer가 필요한 이유

마이크로컨트롤러에서는 일정 시간 뒤에 동작하거나 주기적으로 반복해야 하는 일이 매우 많다.

- LED blinking
- LCD refresh
- Temperature sensor polling
- Servo motor pulse generation
- 마지막 입력 뒤 일정 시간 후 LCD backlight 끄기

가장 단순한 방법은 전용 task를 만들고 `vTaskDelay()`로 block 상태에 넣었다가 매 주기마다 깨우는 것이다. 하지만 ESP32의 FreeRTOS task 하나는 stack과 TCB(Task Control Block)를 포함해 약 1KB에 가까운 overhead가 들 수 있다. 작은 주기 작업 하나만을 위해 task를 추가하는 것은 과할 수 있다.

기존 task에서 `xTaskGetTickCount()`를 읽고, 이전 timestamp와 비교하는 방법도 있다. 이 값은 scheduler 시작 뒤 경과한 tick 수로, Arduino의 `millis()`와 비슷하다. 다만 실행 시점 판단 코드를 해당 task 안에 직접 관리해야 한다.

FreeRTOS의 **software timer**는 OS 수준에서 이 문제를 해결한다. Timer가 만료되면 지정한 callback function을 호출하므로, 여러 단순 시간 기반 작업을 전용 task를 추가하지 않고 관리할 수 있다.

> **주의**
> Software timer는 tick timer를 기반으로 한다. ESP32 예제의 기본 tick이 1ms라면 1ms보다 높은 정밀도는 낼 수 없다. 더 정밀한 timing이 필요하면 hardware timer를 사용해야 한다.

---

## 2. 구현 방법 선택 기준

| 방법 | 적합한 경우 | 장점 | 한계 |
| --- | --- | --- | --- |
| 전용 task + `vTaskDelay()` | 주기 작업 자체가 길거나 독립적인 흐름이 필요할 때 | 읽기 쉽고 block 처리 가능 | task마다 stack/TCB overhead |
| 기존 task + `xTaskGetTickCount()` | 이미 실행 중인 task 안에서 간단히 시점을 확인할 때 | task 추가 없음 | timestamp와 조건을 직접 관리 |
| Hardware timer | tick보다 높은 정밀도 또는 하드웨어 timing이 필요할 때 | 높은 정밀도 | 개수가 한정되고 MCU별 설정이 달라 portability가 낮음 |
| Software timer | 짧고 간단한 timeout·주기 callback이 여러 개 있을 때 | 하나의 service task가 다수 timer를 관리 | tick 정밀도에 묶이고 callback이 block되면 안 됨 |

Software timer는 software interrupt와 비슷해 보이지만 ISR context가 아니라 **task level**에서 동작한다. 따라서 ISR보다 제약은 적지만 timer service task를 막지 않도록 짧게 작성해야 한다.

---

## 3. Timer Service Task와 Command Queue

Timer 기능을 활성화하면 scheduler 시작 시 background에서 **timer service task**(timer daemon)가 실행된다. 이 task는 다음을 담당한다.

1. 활성 timer 목록과 각 만료 시점을 관리한다.
2. 다음으로 만료될 timer 시점까지 스스로 block한다.
3. tick timer가 해당 시점에 도달하면 깨어나 callback function을 호출한다.
4. create, start, stop, reset 같은 timer command를 queue에서 받아 처리한다.

우리가 timer service task를 직접 제어하는 방식은 아니다. `xTimerStart()`, `xTimerStop()`, `xTimerReset()` 같은 API를 호출하면 그 명령이 **timer command queue**에 들어가고, service task가 이를 읽어 실제 상태를 바꾼다.

이 구조는 service task 하나의 overhead를 갖지만, 여러 timer가 각각 task를 갖지 않아도 되게 한다.

> **이미지 필요**
> Application task가 timer command queue로 명령을 보내고, timer service task가 timer list를 관리한 뒤 callback을 실행하는 흐름도.
> - 출처: 강의 02:23~03:59
> - 대체안: 해당 구간의 강의 화면을 캡처하거나 직접 block diagram 작성

---

## 4. Callback은 ISR처럼 짧고 Non-blocking으로 작성한다

Timer가 만료될 때 호출되는 함수를 **callback function**이라고 한다. Callback은 별도의 실행 문맥이 아니라 timer service task 안에서 실행되며, service task와 같은 priority를 갖는다.

따라서 callback이 길어지거나 block되면 다른 timer의 만료 처리와 timer command 처리까지 늦어진다. ISR처럼 다음 원칙을 적용한다.

- 필요한 동작만 빠르게 수행한다.
- `delay()`나 긴 계산을 넣지 않는다.
- Queue, mutex, semaphore를 쓰더라도 block time을 두지 않는다.
- 시간이 오래 걸리는 일은 callback에서 notification·queue·event 등을 통해 별도 task에 넘기는 방식으로 설계한다.

> **주의**
> Callback은 ISR은 아니지만, timer service task 전체를 멈추게 할 수 있다. “task context이므로 마음대로 기다려도 된다”는 생각이 가장 흔한 실수다.

---

## 5. Timer 기능 설정과 주요 API

Software timer를 사용하려면 `FreeRTOSConfig.h`에서 timer 지원이 켜져 있어야 한다.

```c
#define configUSE_TIMERS 1
```

ESP32 Arduino의 FreeRTOS는 기본으로 timer support를 포함하므로 보통 별도 수정이 필요 없다. 강의에서 확인한 ESP32 설정값은 timer service task priority `1`, command queue length `10`, stack depth `2KB`다. Vanilla FreeRTOS에서는 stack depth가 byte가 아니라 word 단위일 수 있다.

대표 API는 다음과 같다.

- `xTimerCreate()` / `xTimerDelete()` — timer 생성·삭제
- `xTimerStart()` / `xTimerStop()` / `xTimerReset()` — 실행 상태 제어
- `pvTimerGetTimerID()` — callback 안에서 timer ID 조회
- `xTimerGetTimerDaemonTaskHandle()` — service task handle 조회
- `...FromISR()` — ISR에서 timer service task로 command를 보낼 때 사용하는 non-blocking variant

ISR에서는 command queue가 가득 차도 기다릴 수 없으므로, 가능한 경우 반드시 `FromISR` API를 쓴다. `xTimerGetTimerDaemonTaskHandle()`로 service task priority를 runtime에 바꾸는 것은 권장되지 않는다. Priority가 필요하면 설정 파일에서 정하는 편이 낫고, ESP32 port에서는 이 handle 조회 기능이 기본으로 비활성화되어 있을 수 있다.

---

## 6. `xTimerCreate()`로 Timer 만들기

Timer는 `xTimerCreate()`로 만든다.

```c
TimerHandle_t oneShotTimer = xTimerCreate(
    "One-shot timer",                   // debugging용 이름
    2000 / portTICK_PERIOD_MS,           // period: tick 단위
    pdFALSE,                             // auto reload 여부
    (void *)0,                           // timer ID
    timerCallback                        // 만료 시 호출할 함수
);
```

각 parameter의 의미는 다음과 같다.

- **이름:** debugger나 trace에서 timer를 식별하기 위한 문자열
- **period:** timer 기간이며 tick 단위다. 밀리초 값은 `portTICK_PERIOD_MS`로 나누어 변환한다.
- **auto reload:** `pdFALSE`면 one-shot, `pdTRUE`면 auto-reload다.
- **timer ID:** `void *` 형태의 사용자 데이터다. callback에서 timer 구분 또는 callback 사이의 상태 보관에 쓸 수 있다.
- **callback:** `void`를 반환하고 `TimerHandle_t` 하나를 인자로 받는 함수다.

Timer control block은 heap memory를 사용하므로 생성이 실패할 수 있다. 반환 handle이 `NULL`인지 확인한 뒤 시작해야 한다.

```c
if (oneShotTimer == NULL) {
    Serial.println("Failed to create timer");
    return;
}
```

Callback의 기본 형태는 다음과 같다.

```c
void timerCallback(TimerHandle_t xTimer)
{
    // 짧고 non-blocking인 작업만 수행한다.
}
```

---

## 7. One-shot과 Auto-reload Timer

**One-shot timer**는 설정한 period가 지난 뒤 callback을 한 번 호출하고 멈춘다. 다시 사용하려면 다른 task에서 다시 start하거나 reset해야 한다. Inactivity timeout처럼 “마지막 이벤트 뒤 한 번만 실행”해야 할 때 적합하다.

**Auto-reload timer**는 만료될 때마다 callback을 실행한 뒤 자동으로 다시 시작된다. 일정 주기의 상태 확인이나 갱신에 적합하다.

두 timer가 callback 하나를 공유할 수도 있다. 생성할 때 서로 다른 timer ID를 지정하고, callback에서 `pvTimerGetTimerID()`로 구분한다.

```c
void timerCallback(TimerHandle_t xTimer)
{
    uint32_t timerId = (uint32_t)pvTimerGetTimerID(xTimer);

    if (timerId == 0) {
        Serial.println("One-shot timer expired");
    } else if (timerId == 1) {
        Serial.println("Auto-reload timer expired");
    }
}
```

강의 예제에서 auto-reload timer는 1초마다 계속 callback을 호출하고, one-shot timer는 한 번 호출한 뒤 멈춘다.

---

## 8. `xTimerStart()`의 Queue Wait와 Restart 성질

Timer 시작 명령도 service task의 command queue를 거친다.

```c
xTimerStart(oneShotTimer, portMAX_DELAY);
```

두 번째 인자는 command queue가 가득 찼을 때 기다릴 최대 시간이다. `portMAX_DELAY`는 task context에서 큐에 넣을 수 있을 때까지 사실상 무한히 기다리라는 뜻이다. ISR에서는 block하면 안 되므로 이 방식이 아니라 `FromISR` API를 사용한다.

강의의 중요한 힌트는, 아직 만료되지 않은 timer에 `xTimerStart()`를 다시 호출하면 counter가 다시 시작된다는 점이다. 매 입력마다 one-shot timer를 다시 start하면, timer는 마지막 입력 이후의 period가 지나야 만료된다.

---

## 9. 실습: LCD Backlight Auto-Dim

ESP32의 LED를 LCD backlight라고 가정한다. 별도 input task가 serial terminal의 문자를 읽어 echo하고, 입력 중에는 LED를 켠다. 마지막 입력 뒤 5초 동안 아무 입력이 없으면 one-shot software timer callback이 LED를 끈다.

동작 순서는 다음과 같다.

1. 5초짜리 one-shot timer를 생성한다.
2. input task가 문자를 하나 읽으면 echo하고 LED를 켠다.
3. 입력마다 `xTimerStart()`를 호출한다.
4. 새 입력이 5초 안에 오면 counter가 다시 5초부터 시작한다.
5. 5초 동안 입력이 없으면 callback이 실행되어 LED를 끈다.

```c
TimerHandle_t backlightTimer;

void backlightOffCallback(TimerHandle_t xTimer)
{
    digitalWrite(LED_BUILTIN, LOW);
}

void serialInputTask(void *pvParameters)
{
    for (;;) {
        if (Serial.available() > 0) {
            char c = Serial.read();
            Serial.write(c);                         // 입력 문자 echo
            digitalWrite(LED_BUILTIN, HIGH);         // backlight on

            if (xTimerStart(backlightTimer, portMAX_DELAY) != pdPASS) {
                Serial.println("Failed to start timer");
            }
        }

        vTaskDelay(1);                               // input task가 CPU를 양보
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    backlightTimer = xTimerCreate(
        "Backlight off",
        5000 / portTICK_PERIOD_MS,
        pdFALSE,
        (void *)0,
        backlightOffCallback
    );

    if (backlightTimer == NULL) {
        Serial.println("Failed to create timer");
        return;
    }

    xTaskCreate(serialInputTask, "Serial input", 2048, NULL, 1, NULL);
}

void loop()
{
}
```

이 패턴의 핵심은 “마지막 입력부터 5초”를 별도의 timestamp 계산으로 관리하지 않고, 입력마다 one-shot timer를 restart해 표현하는 것이다.

> **주의**
> 예제의 callback은 `digitalWrite()`처럼 짧은 동작만 한다. 실제로 LED를 끈 뒤 파일 저장·통신·화면 갱신처럼 오래 걸리는 일을 해야 한다면 callback에서 직접 실행하지 말고 별도 task에 전달한다.

---

## 10. 핵심 정리

- Software timer는 FreeRTOS tick에 기반한 OS-level timer다.
- 하나의 timer service task가 timer list와 command queue를 관리하므로 여러 timer를 효율적으로 다룬다.
- Callback은 timer service task context에서 실행되므로 짧고 non-blocking이어야 한다.
- `pdFALSE`는 one-shot, `pdTRUE`는 auto-reload다.
- Software timer 정밀도는 1 tick을 넘을 수 없다. 더 높은 정밀도는 hardware timer의 영역이다.
- 마지막 이벤트 이후 timeout을 만들 때는 one-shot timer를 이벤트마다 restart하는 방식이 깔끔하다.

---

## 참고 자료

- [Introduction to RTOS Part 8 - Software Timer | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch?v=b1f1Iex0Tso)
- [FreeRTOS Software Timers](https://www.freertos.org/RTOS-software-timer.html)
- [FreeRTOS Timer API](https://www.freertos.org/FreeRTOS-Software-Timer-API-Functions.html)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** FreeRTOS software timer는 tick timer를 기반으로 일정 시간 뒤 또는 주기적으로 callback을 실행하는 OS-level timer다.
- **왜 필요:** 단순 주기 작업마다 task를 만들면 stack과 TCB overhead가 생기고, hardware timer는 개수가 제한되며 MCU별 설정이 달라진다.
- **동작:** Timer service task가 timer list와 command queue를 관리하다가 timer가 만료되면 callback을 실행한다. Callback은 service task context에서 실행되므로 ISR처럼 빠르고 non-blocking으로 작성한다.
- **비교:** One-shot timer는 한 번 만료된 뒤 멈추고 auto-reload timer는 자동으로 다시 시작된다. 1 tick보다 높은 정밀도가 필요하면 software timer가 아니라 hardware timer를 사용한다.
- **30초 통합 답변:**
  > FreeRTOS software timer는 OS tick을 기준으로 특정 시간 뒤 또는 주기적으로 callback을 실행하는 기능입니다. 단순한 timeout이나 주기 작업마다 별도 task를 만들면 stack과 TCB overhead가 생기고 hardware timer도 한정되어 있으므로, 하나의 timer service task가 여러 software timer를 관리하게 하면 효율적입니다. 다만 callback은 timer service task에서 실행되므로 ISR처럼 짧고 block 없이 작성해야 합니다. One-shot은 한 번만 실행되고 auto-reload는 반복 실행되며, tick보다 정밀한 timing에는 hardware timer를 선택합니다.
