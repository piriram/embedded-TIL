# FreeRTOS 시작하기

**주제:** FreeRTOS를 프로젝트에 포함하는 방법, ESP32의 FreeRTOS 구조, Arduino IDE 설정, `xTaskCreatePinnedToCore()`로 첫 task를 만드는 흐름.
**원본 강의:** [Introduction to RTOS Part 2 - Getting Started with FreeRTOS | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch?v=JIr7Xm_riRs)

---

## 1. 이번 강의의 목표

이 시리즈는 일반적인 RTOS 개념을 설명하면서, 그 개념을 **ESP32에서 FreeRTOS로 구현하는 방법**까지 함께 보여준다.

실습은 Arduino IDE를 사용한다. Arduino를 쓰면 board package 설치와 upload 흐름이 단순해져서 RTOS 개념 자체에 집중할 수 있다.

다만 Arduino를 쓰지 않는 프로젝트에서도 FreeRTOS를 사용할 수 있어야 하므로, 먼저 FreeRTOS source code를 다운로드하고 non-Arduino project에 포함하는 방법을 살펴본다.

---

## 2. FreeRTOS 소스와 문서 확인

FreeRTOS source code는 `FreeRTOS.org`에서 받을 수 있다.

강의에서 권장하는 흐름은 다음과 같다.

1. `FreeRTOS.org`에 접속한다.
2. **Download FreeRTOS**를 선택해 source code를 다운로드한다.
3. 문서에서 **Kernel > Getting Started**를 확인한다.
4. source code에 포함된 demo application을 build하고 실행하는 절차를 따라간다.
5. 자신의 board가 지원되지 않으면 **Create your own FreeRTOS project** 문서를 확인한다.

FreeRTOS를 프로젝트에 포함하는 과정은 비교적 단순하다. 최소한 필요한 것은 다음이다.

- FreeRTOS kernel의 C source file
- 필요한 header file
- heap management file
- RTOS tick timer로 사용할 microcontroller timer 설정
- `FreeRTOSConfig.h` 같은 configuration file

> **주의**
> FreeRTOS를 붙일 때는 microcontroller의 hardware timer 중 하나를 **RTOS tick timer**로 할당해야 한다. 어떤 timer를 어떻게 쓰는지는 port와 board에 따라 달라지므로, 관련 문서를 반드시 읽어야 한다.

---

## 3. FreeRTOS 참고 문서

FreeRTOS를 공부하거나 막혔을 때 강사가 특히 추천하는 자료는 두 가지다.

- **Mastering the FreeRTOS Real-Time Kernel**
- **FreeRTOS Reference Manual**

둘 다 FreeRTOS를 탐색할 때 매우 유용한 문서다. API 이름만 외우기보다, scheduler, task, queue, semaphore, memory management가 어떤 전제 위에서 동작하는지 확인할 때 참고한다.

---

## 4. FreeRTOS와 FreeRTOS Plus

다운로드한 zip file을 extract하면 FreeRTOS directory 안에서 크게 두 성격의 library를 볼 수 있다.

**FreeRTOS library**는 기본적으로 scheduler다. 우리가 이미 device driver와 file driver를 갖고 있다면 kernel scheduler만 가져와도 된다.

**FreeRTOS Plus library**는 scheduler에 몇 가지 driver와 middleware를 더한 묶음이다. 대표적으로 TCP, UDP 같은 networking 관련 기능이 포함된다.

Non-Arduino project에서는 자신의 build system에서 필요한 source file을 copy하거나 link하도록 구성한다.

Demo folder에는 여러 example project가 들어 있다. GCC example 같은 프로젝트를 열어 보면, 대부분 중요한 변수를 정의하는 config file을 갖고 있다. 자신의 project에도 이와 비슷한 configuration file이 필요하다.

`main.c`를 보면 여러 library file이 어떤 방식으로 include되는지 확인할 수 있다.

---

## 5. ESP32는 Vanilla FreeRTOS가 아니다

ESP32는 **Vanilla FreeRTOS**를 그대로 실행하지 않는다. ESP32는 Espressif의 **ESP-IDF framework** 안에서 수정된 FreeRTOS를 실행한다.

대부분의 ESP32는 dual-core processor를 갖고 있고, **SMP(Symmetric Multiprocessing)** architecture를 사용한다. SMP는 두 개 이상의 core가 memory와 다른 resource를 공유하는 구조다.

현대 desktop이나 laptop microprocessor도 multi-core 지원을 위해 SMP architecture를 많이 사용한다. Espressif는 ESP32의 SMP architecture를 지원하기 위해 FreeRTOS를 수정했다.

이 강의 시리즈에서는 multi-core support를 깊게 다루지 않는다. RTOS 입문 범위를 넘기 때문이다. Demo application에서는 ESP32의 task를 **한 core에서만 실행되도록 제한**한다.

> **예외**
> ESP32의 `xTaskCreatePinnedToCore()`는 ESP-IDF 계열에서 제공되는 함수이며 Vanilla FreeRTOS에는 없다. Vanilla FreeRTOS에서는 일반적으로 `xTaskCreate()`를 사용한다.

---

## 6. ESP32와 Arduino IDE 설정

강의에서는 Adafruit Feather HUZZAH32를 사용하지만, 거의 모든 ESP32 board가 동작할 수 있다. Arduino에서 지원되는 board라면 보통 ESP-IDF를 기반으로 동작한다.

Arduino IDE 설정 흐름은 다음과 같다.

1. Arduino IDE를 설치한다.
2. **File > Preferences**로 이동한다.
3. **Additional Boards Manager URLs** 옆의 URL list button을 누른다.
4. 새 줄에 다음 URL을 추가한다.

```text
https://dl.espressif.com/dl/package_esp32_index.json
```

5. **Tools > Board > Boards Manager**로 이동한다.
6. `ESP32`를 검색한다.
7. **Espressif Systems ESP32 package**를 찾는다.
8. 가장 최신 version을 선택해 install한다.
9. 사용할 ESP32 Arduino board를 선택하고 upload한다.

---

## 7. ESP32의 FreeRTOSConfig.h 확인

ESP32도 Vanilla demo example처럼 FreeRTOS config file의 설정에 의존한다.

Arduino board package 안에서 `FreeRTOSConfig.h`를 찾을 수 있다. Windows 기준 예시는 다음 경로다.

```text
<username>/AppData/Local/Arduino15/packages/ESP32/hardware/ESP32/<package-version>/tools/sdk/include/FreeRTOS/FreeRTOS/FreeRTOSConfig.h
```

이 파일을 찾는 경로는 꽤 깊지만, ESP32에서 FreeRTOS가 어떻게 설정되어 있는지 확인할 때 유용하다.

강의에서 확인한 예시는 다음과 같다.

- 사용할 수 있는 priority level은 최대 **25개**다.
- 설정 가능한 smallest task stack size는 **768 bytes**다.
- stack overflow check 같은 define은 여러 가능한 값을 가질 수 있다.

어떤 define이 실제로 무엇으로 설정되어 있는지 궁금하면 serial terminal에 print해서 확인할 수도 있다.

---

## 8. 실습 코드의 기본 상수

실습에서는 학습을 단순하게 만들기 위해 ESP32의 task를 한 core에만 묶는다.

보통 실전에서는 ESP32의 dual-core 성능을 모두 쓰는 편이 좋다. 하지만 RTOS 개념을 처음 배울 때 second core가 동시에 개입하면 scheduler와 task 동작을 해석하기 어려워질 수 있다.

그래서 먼저 **ESP32를 한 core만 쓰는 것처럼 제한**하고, 기본 Blinky task를 만든다.

LED pin은 Arduino에서 정의한 built-in LED pin을 사용할 수 있다. 원하면 외부 LED를 연결한 pin으로 바꿔도 된다.

---

## 9. FreeRTOS Task 함수 형태

FreeRTOS에서 task는 scheduler가 실행할 수 있도록 등록되는 function이다. `setup()` 안에서 만들 수도 있고, 다른 task에서 만들 수도 있다.

FreeRTOS task function은 다음 형태를 갖는다.

```c
void taskFunction(void *parameter)
{
    while (true) {
        // task body
    }
}
```

반환값은 없고, parameter는 `void *` 하나를 받는다. 이 parameter를 통해 task에 argument를 전달할 수 있다.

다만 argument를 넘길 때는 memory lifetime에 주의해야 한다. `setup()`이나 calling task의 local variable 주소를 넘겼는데 그 scope가 끝나면, task가 가리키는 memory가 더 이상 유효하지 않을 수 있다.

이번 실습에서는 단순하게 argument를 넘기지 않고 `NULL`을 사용한다.

---

## 10. `vTaskDelay()`와 Tick Timer

Arduino Blinky에서는 보통 `delay(500)`으로 LED를 500ms 켜고 끈다.

ESP32 Arduino의 `delay()`는 non-blocking wait처럼 동작한다고 알려져 있지만, FreeRTOS를 배울 때는 `delay()`에 의존하는 습관을 들이지 않는 편이 좋다.

FreeRTOS에서는 대신 `vTaskDelay()`를 사용한다.

`vTaskDelay()`는 scheduler에게 다음 의미를 전달한다.

> 이 task는 지정한 delay 시간이 끝날 때까지 쉬어도 된다. 그동안 다른 task를 실행해라.

거의 모든 RTOS는 **tick timer**를 기반으로 한다. Tick timer는 microcontroller의 hardware timer 중 하나를 사용해 processor에 일정한 간격으로 interrupt를 거는 장치다.

이 interrupt period를 **tick**이라고 부른다. Scheduler는 매 tick마다 어떤 task를 실행해야 할지 판단할 기회를 얻는다.

FreeRTOS의 기본 tick period는 **1 millisecond**이고, `portTICK_PERIOD_MS`가 `1`로 define된다.

중요한 점은 `vTaskDelay()`가 millisecond가 아니라 **tick 개수**를 인자로 받는다는 것이다. 그래서 원하는 millisecond 값을 tick period로 나누어 전달해야 한다.

```c
vTaskDelay(500 / portTICK_PERIOD_MS);
```

이 코드는 500ms에 해당하는 tick 수만큼 현재 task를 delay한다.

> **주의**
> `vTaskDelay()`는 CPU를 멈춰 세우는 blocking delay가 아니라, 현재 task를 일정 tick 동안 대기 상태로 보내고 scheduler가 다른 task를 실행할 수 있게 한다.

---

## 11. `xTaskCreatePinnedToCore()`로 Task 만들기

ESP32 실습에서는 `setup()`에서 LED pin을 output으로 설정한 뒤, `xTaskCreatePinnedToCore()`를 호출해 task를 만든다.

이 함수는 ESP32의 특정 CPU core에서 task를 실행하도록 scheduler에 요청한다.

Vanilla FreeRTOS에는 이 함수가 없고, `xTaskCreate()`를 사용한다. ESP-IDF에서도 `xTaskCreate()`는 동작하지만, 그러면 scheduler가 어떤 core에서 task를 실행할지 자유롭게 정할 수 있다.

`xTaskCreatePinnedToCore()`의 주요 parameter는 다음과 같다.

- **Task function:** 실행할 task function의 이름
- **Task name:** debugging과 식별에 사용할 문자열
- **Stack size:** task stack 크기
- **Parameter:** task function에 전달할 `void *` argument
- **Priority:** task priority
- **Task handle:** 다른 task나 main loop에서 task를 관리할 때 사용할 handle pointer
- **Core ID:** task를 실행할 CPU core

강의에서는 task를 ESP32의 **core 1**에서 실행하도록 설정한다.

---

## 12. Stack Size와 Priority

ESP32 Arduino 환경의 `xTaskCreatePinnedToCore()`에서 stack size는 **bytes** 단위다.

Vanilla FreeRTOS의 `xTaskCreate()`에서는 stack size가 **word 수**로 해석된다. 이 차이를 혼동하면 stack 크기를 예상과 다르게 잡을 수 있다.

ESP32 config file 기준으로 empty task를 실행하고 scheduler overhead를 감당하는 데 필요한 최소 stack size는 **768 bytes**다. 강의에서는 basic task이므로 이를 조금 늘려 **1KB**를 사용한다.

Priority는 숫자가 높을수록 높다. `configMAX_PRIORITIES` 설정은 config file에서 확인할 수 있고, 강의 기준 기본값은 **25**다. 따라서 task priority는 **0부터 24까지** 줄 수 있으며, `0`이 가장 낮다.

Task handle을 저장하면 다른 task나 main execution loop에서 해당 task의 상태를 확인하거나, memory usage를 보거나, 필요하면 task를 끝낼 수 있다.

---

## 13. Arduino의 `setup()`과 `loop()`도 Task다

ESP32 Arduino framework에서는 `setup()`과 `loop()`가 main program entry point에서 직접 호출되는 단순 함수가 아니다. 이 둘은 별도의 task 안에서 실행된다.

그래서 `setup()`에서 `xTaskCreate()` 또는 `xTaskCreatePinnedToCore()`를 호출하는 순간 새 task가 생성되어 실행될 수 있다.

다른 FreeRTOS system에서는 보통 `vTaskStartScheduler()`를 호출해야 scheduler가 시작되고 task들이 실행된다. 하지만 ESP32 Arduino 환경에서는 `setup()` 전에 이미 `vTaskStartScheduler()`가 호출되어 있으므로 우리가 직접 호출할 필요가 없다.

이번 실습에서는 `loop()`를 비워 둔다.

> **주의**
> ESP32 Arduino의 `setup()`과 `loop()`는 core 1에서 priority 1인 task로 실행된다. 우리가 만든 task의 priority를 이보다 낮게 설정하면 `setup()`/`loop()` task가 다른 task에 영향을 줄 수 있다.

---

## 14. 첫 Blinky Task 예시

강의의 핵심 코드는 다음 구조로 이해하면 된다.

```c
#if CONFIG_FREERTOS_UNICORE
static const BaseType_t app_cpu = 0;
#else
static const BaseType_t app_cpu = 1;
#endif

static const int led_pin = LED_BUILTIN;

void toggleLED(void *parameter)
{
    while (true) {
        digitalWrite(led_pin, HIGH);
        vTaskDelay(500 / portTICK_PERIOD_MS);
        digitalWrite(led_pin, LOW);
        vTaskDelay(500 / portTICK_PERIOD_MS);
    }
}

void setup()
{
    pinMode(led_pin, OUTPUT);

    xTaskCreatePinnedToCore(
        toggleLED,
        "Toggle LED",
        1024,
        NULL,
        1,
        NULL,
        app_cpu
    );
}

void loop()
{
}
```

이 코드는 LED를 500ms 켜고 500ms 끄므로, LED는 1초 주기로 깜빡인다.

중요한 학습 포인트는 LED toggle 자체가 아니라, 이 동작이 `loop()`가 아니라 FreeRTOS task로 실행된다는 점이다.

---

## 15. 실습 과제

이번 강의의 challenge는 같은 LED를 서로 다른 rate로 blink하게 만드는 것이다.

즉, 이미 만든 task와 비슷한 task를 하나 더 만들고, delay 값을 다르게 설정한다. 그러면 두 task가 같은 LED를 서로 다른 주기로 제어하면서 불규칙해 보이는 blink pattern이 만들어진다.

이 실습은 task가 여러 개 있을 때 scheduler가 각 task를 번갈아 실행한다는 점을 눈으로 확인하는 데 도움이 된다.

> **주의**
> 여러 task가 같은 LED pin이라는 shared resource를 동시에 제어한다. 이번 예제에서는 시각적 효과를 보기 위한 단순 실습이지만, 실제 firmware에서는 shared resource 접근을 명확히 설계해야 한다.

---

## 참고 자료

- [Introduction to RTOS Part 2 - Getting Started with FreeRTOS | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch?v=JIr7Xm_riRs)
- [FreeRTOS](https://www.freertos.org/)
- [FreeRTOS Kernel Getting Started](https://www.freertos.org/FreeRTOS-quick-start-guide.html)
- [Mastering the FreeRTOS Real-Time Kernel](https://www.freertos.org/Documentation/RTOS_book.html)
- [ESP-IDF FreeRTOS Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/freertos.html)
- [Arduino ESP32 package index](https://dl.espressif.com/dl/package_esp32_index.json)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** FreeRTOS task는 scheduler에 등록되어 tick timer 기준으로 실행 기회를 받는 함수형 실행 단위다.
- **왜 필요:** Super loop에서는 한 작업이 delay되는 동안 다른 작업이 밀릴 수 있지만, FreeRTOS task는 `vTaskDelay()`로 자신을 대기 상태로 보내고 scheduler가 다른 task를 실행하게 할 수 있다.
- **동작:** Task function은 `void (*)(void *)` 형태이며 보통 내부에 무한 루프를 가진다. `xTaskCreate()`나 ESP32의 `xTaskCreatePinnedToCore()`로 function, stack size, priority, argument, handle, core 정보를 scheduler에 등록한다.
- **비교:** Vanilla FreeRTOS에서는 `xTaskCreate()`와 `vTaskStartScheduler()` 흐름을 직접 다루는 경우가 많지만, ESP32 Arduino에서는 ESP-IDF 기반 FreeRTOS가 이미 scheduler를 시작해 두고 `setup()`과 `loop()`도 task로 실행한다.
- **30초 통합 답변:**
  > FreeRTOS에서 task는 scheduler가 실행할 수 있도록 등록하는 함수형 실행 단위입니다. Task 함수는 반환값 없이 `void *` parameter를 받고, 보통 내부에서 무한 루프를 돌며 `vTaskDelay()`로 일정 tick 동안 대기합니다. `vTaskDelay()`는 CPU를 막는 delay가 아니라 현재 task를 쉬게 하고 다른 task가 실행될 수 있게 합니다. ESP32 Arduino에서는 `xTaskCreatePinnedToCore()`로 task를 특정 core에 묶을 수 있지만, Vanilla FreeRTOS에서는 보통 `xTaskCreate()`를 사용하며 stack size 단위도 환경에 따라 bytes와 words 차이가 날 수 있습니다.
