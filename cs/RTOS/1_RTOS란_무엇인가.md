# RTOS란 무엇인가

**주제:** Real-Time Operating System(RTOS)의 정의, 일반 목적 OS와의 차이, super loop와 interrupt 기반 구조의 한계, FreeRTOS를 쓰는 이유.
**원본 강의:** [Introduction to RTOS Part 1 - What is a Real-Time Operating System (RTOS)? | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch?v=F321087yYy4)

---

## 1. OS가 하는 일

운영체제(OS)는 컴퓨터나 microcontroller 위에서 실행되는 소프트웨어이며, 여러 중요한 기능을 맡는다. RTOS도 기본적으로 OS이기 때문에, 먼저 일반적인 OS의 역할을 이해해야 한다.

첫 번째 역할은 **background task와 user application의 scheduling**이다. 일반적인 컴퓨터나 스마트폰에서는 수십 개의 background process가 동시에 실행되고, 사용자는 여러 application을 열어 둔다. OS는 각 process에 CPU 시간을 조금씩 나눠 주어 모든 일이 동시에 일어나는 것처럼 보이게 만든다.

두 번째 역할은 **virtual resource 관리**다. 파일, library, folder 같은 자원을 application과 process가 필요할 때 접근할 수 있도록 관리한다.

세 번째 역할은 **device driver 관리 또는 제공**이다. OS가 driver를 통해 external disk를 읽고 쓰거나, keyboard와 mouse input에 반응하거나, monitor에 graphics를 그릴 수 있게 한다.

우리가 익숙한 Windows, macOS, Linux, iOS, Android는 모두 general purpose operating system에 속한다.

---

## 2. General Purpose OS와 RTOS의 차이

General purpose OS는 보통 **human interaction**을 가장 중요한 요구사항으로 두고 설계된다. 사용자가 클릭했을 때 반응하고, 화면이 자연스럽게 갱신되고, 여러 application이 무리 없이 돌아가는 것이 중요하다.

이런 OS의 scheduler는 사람이 느끼는 responsiveness를 우선한다. 그래서 어떤 timing deadline이 조금 밀리거나 놓쳐져도, 사람이 알아차리지 못하는 정도라면 받아들일 수 있다.

또한 general purpose OS의 scheduler는 흔히 **non-deterministic**하다. 즉, 어떤 task가 정확히 언제 실행되고 얼마 동안 실행될지 개발자가 미리 정확하게 알 수 없다.

RTOS(Real-Time Operating System)는 이 지점에서 목적이 다르다. RTOS는 general purpose OS와 비슷한 기능을 제공할 수 있지만, 핵심은 **scheduler가 task의 timing deadline을 만족하도록 설계된다**는 점이다.

예를 들어 medical device나 engine controller처럼 strict timing deadline이 필요한 장치에서는 deadline을 놓치는 것이 단순한 지연이 아니라 치명적인 문제가 될 수 있다. engine controller가 spark plug를 제때 점화하지 못하면 시스템 전체가 위험해질 수 있다.

> RTOS에서 "real-time"은 무조건 빠르다는 뜻이 아니라, **정해진 시간 안에 예측 가능하게 동작한다**는 뜻에 가깝다.

---

## 3. RTOS가 제공하는 범위

RTOS마다 제공하는 기능 범위는 다르다.

일부 RTOS는 high-level device driver를 제공하기도 한다. microcontroller 환경에서는 Wi-Fi stack, Bluetooth stack, simple LCD driver 같은 기능을 볼 수 있다.

반대로 아주 bare-bones한 RTOS는 scheduler만 제공하기도 한다. 이런 경우 filesystem이나 device driver는 우리가 직접 가져오거나 작성해야 한다.

중요한 점은 RTOS를 쓰는 이유가 timing deadline만은 아니라는 것이다. 여러 task를 동시에 실행하는 구조를 만들 수 있다는 점도 큰 장점이다.

---

## 4. Super Loop 구조

Arduino를 포함한 많은 microcontroller 프로그램은 다음과 같은 구조로 시작한다.

1. 프로그램 시작 시 setup function을 수행한다.
2. `while (forever)` 형태의 무한 루프 안에서 여러 task를 round-robin 방식으로 실행한다.
3. task는 sensor 값을 읽고, 계산을 수행하고, LED display 같은 장치에 결과를 표시한다.

이런 구조를 **super loop**라고 부른다.

Super loop는 구현이 매우 쉽고 overhead가 작다. CPU cycle과 memory를 적게 쓰며, RTOS보다 debugging도 훨씬 쉽다. 그래서 단순한 microcontroller project 대부분에서는 super loop가 더 나은 선택일 수 있다.

예를 들어 해야 할 일이 몇 개뿐이고, 각 일이 짧게 끝나며, 복잡한 동시성이 필요 없다면 굳이 RTOS를 도입할 이유가 없다.

---

## 5. Interrupt로 해결할 수 있는 경우

Super loop 구조에서도 interrupt를 함께 사용할 수 있다. 외부 button push 같은 event가 발생했을 때 execution flow를 끊고 처리하거나, 특정 timed interval마다 어떤 작업을 실행할 수 있다.

strict timing deadline이 필요한 task가 한두 개라면 RTOS보다 interrupt service routine(ISR)이 더 적합할 수 있다.

강사는 경험적으로 **1 millisecond보다 짧은 timing deadline**을 맞춰야 한다면 interrupt를 쓰는 편이 낫다고 설명한다. 만약 interval이 **수백 nanosecond보다 짧은 수준**이라면 매우 빠른 processor가 필요하거나, FPGA 같은 custom hardware를 검토해야 한다.

> **주의**
> RTOS는 interrupt를 대체하는 도구가 아니다. 아주 짧고 정확한 timing이 필요한 작업은 여전히 interrupt나 hardware가 더 알맞을 수 있다.

---

## 6. Super Loop의 한계와 Concurrent Task

Super loop의 문제는 task를 실제로 동시에 실행할 수 없다는 점이다.

예를 들어 task 2가 오래 걸리기 시작하면, 그 뒤에 있는 task 3의 display update가 늦어진다. 그러면 사용자는 화면 lag를 경험할 수 있다.

또 serial terminal에서 user input을 polling하거나 sensor data를 읽는 구조라면, 다른 task가 너무 오래 걸리는 동안 입력이나 데이터를 놓칠 수 있다.

Multi-core processor에서는 여러 task를 물리적으로 동시에 실행할 수 있다. 하지만 많은 microcontroller는 single-core이므로, CPU 시간을 여러 task 사이에 나누어 써야 한다.

RTOS는 이때 task별로 CPU 시간을 나누고, 필요하면 특정 task에 더 높은 priority를 줄 수 있다. 예를 들어 user input task의 priority를 높이면 사용자는 lag를 덜 느낀다. 대신 background task는 더 늦게 끝날 수 있다.

> **이미지 필요**
> Super loop에서 task 2가 길어져 task 3 display update가 지연되는 흐름과, RTOS scheduler가 task time slice를 나누는 흐름 비교
> - 출처: 강의 04:35~05:30 구간
> - 대체안: 직접 작성한 super loop vs RTOS scheduling 다이어그램

---

## 7. Task, Thread, Process 용어

RTOS와 OS를 이해할 때 task, thread, process 용어가 자주 섞인다.

- **Task:** 코드에서 끝내야 하는 어떤 작업 단위다.
- **Thread:** own program counter와 memory set을 가진 CPU utilization 단위다.
- **Process:** 실행 중인 computer program의 instance다. 보통 process는 task를 수행하기 위해 하나 이상의 thread를 가진다.

일반적인 OS에서 한 process 안의 thread들은 heap memory 같은 resource를 공유하고, 서로 resource를 전달할 수 있다.

많은 RTOS는 하나의 process만 다룰 수 있는 구조에 가깝고, general purpose OS는 여러 process를 동시에 실행할 수 있다.

FreeRTOS에서는 **task**라는 용어를 thread에 가까운 의미로 사용한다. 그래서 FreeRTOS ecosystem에서는 task와 thread라는 말이 혼용될 수 있다. 이 노트에서도 FreeRTOS 문맥에서는 CPU utilization 단위를 가리킬 때 **task**라고 부른다.

---

## 8. RTOS에서도 Interrupt는 동작한다

RTOS를 사용해도 interrupt는 여전히 동작한다.

Interrupt priority가 task보다 높다면, interrupt는 모든 task의 code execution을 멈추고 interrupt service routine을 실행한 뒤, 멈췄던 지점으로 돌아간다.

Interrupt는 여러 개 둘 수 있지만, nested interrupt 처리는 복잡해질 수 있다. 강의에서는 nested interrupt handling까지는 다루지 않는다.

---

## 9. 작은 MCU에서 RTOS가 부적합할 수 있는 이유

단순한 8-bit 또는 16-bit microcontroller에 **2KB RAM** 정도만 있다면, super loop 접근이 더 현실적일 가능성이 높다.

이런 controller에서도 간단한 scheduler를 돌릴 수는 있다. 실제로 FreeRTOS를 Arduino Uno에 porting한 사례도 있다. 하지만 task switching에 드는 memory와 CPU overhead 때문에 실제 application에 남는 resource가 많지 않다.

이런 환경에서는 값싼 controller가 잘할 수 있는 몇 가지 task만 맡기고, 구조를 단순하게 유지하는 편이 낫다.

반대로 ESP32처럼 더 강력한 microcontroller로 올라가면 RTOS가 훨씬 현실적인 선택이 된다. clock cycle과 memory 여유가 있어 scheduler overhead를 감당할 수 있고, 애초에 그런 성능의 MCU를 선택한 이유가 여러 concurrent task를 돌리기 위해서인 경우가 많다.

---

## 10. RTOS를 쓰고 싶은 대표 상황

RTOS를 쓰는 가장 대표적인 이유는 **여러 일을 concurrent하게 처리해야 할 때**다.

ESP32 같은 장치는 user input 처리, SD card read/write, hardware control, number crunching을 동시에 수행할 수 있다. 특히 wireless stack은 RTOS가 큰 도움이 되는 영역이다.

Wi-Fi나 Bluetooth stack 같은 library는 많은 RAM과 processing power를 요구한다. 또한 network event에 짧은 시간 안에 반응해야 한다. 이런 기능을 application logic과 같은 super loop 안에서 안정적으로 섞기 어렵다면, RTOS가 feature를 개별 task로 나누는 데 도움을 준다.

팀으로 큰 firmware project를 진행할 때도 RTOS가 유리할 수 있다. 기능을 task 단위로 나누어 각 팀원이 맡고, 각 task가 concurrent하게 실행된다는 전제 위에서 작업할 수 있다.

다만 RTOS를 쓰면 overhead와 debugging 비용도 생긴다. task 간 resource 관리, priority 설계, synchronization 문제를 확인해야 한다.

---

## 11. FreeRTOS와 ESP32를 선택한 이유

강의 시리즈는 FreeRTOS와 ESP32를 사용한다.

FreeRTOS는 IoT device에서 매우 인기 있는 RTOS다. 강의에서는 Eclipse Foundation의 2018 survey를 근거로 FreeRTOS가 많이 쓰인다고 설명한다.

Linux와 Windows도 IoT device에서 많이 쓰이지만, RT Linux 같은 예외를 제외하면 이들은 general purpose OS다. Bare-metal super loop architecture도 여전히 많이 쓰이며, 많은 문제에 대해 충분히 좋은 해결책이다.

FreeRTOS는 free and open source라서 실습하기 쉽다. 2017년부터는 Amazon이 FreeRTOS project maintenance를 맡았다.

강사는 Zephyr project도 지켜볼 만하다고 언급한다. Zephyr는 Linux Foundation이 지원하는 비교적 새로운 RTOS project다.

ESP32는 기능이 풍부한 강력한 IoT microcontroller이고, 저렴한 ESP32 development board를 쉽게 구할 수 있다. 이 시리즈에서는 Arduino package가 있는 ESP32 board라면 대부분 사용할 수 있다.

Arduino를 사용하는 이유는 level playing field를 만들기 위해서다. 많은 embedded programmer와 electronics tinkerer가 Arduino 경험이 있고, 경험이 없더라도 배우기 쉽다. FreeRTOS를 가르치면서 vendor tool이나 chip-specific library까지 동시에 가르치지 않아도 된다.

ESP32는 modified version of FreeRTOS를 기본적으로 실행하므로, Arduino 환경에서도 task 생성에 필요한 setup이 거의 없다. Task management, semaphore, mutex 같은 예제도 나중에 자신의 build system으로 옮기기 쉽다.

> **예외**
> ESP32의 RTOS는 vanilla FreeRTOS와 완전히 같지는 않다. 강의에서는 ESP RTOS가 vanilla FreeRTOS와 다른 지점을 필요할 때 짚겠다고 한다.

---

## 12. RTOS 선택 기준 정리

RTOS는 모든 firmware 문제의 정답이 아니다. 하지만 다음 조건에서는 좋은 도구가 될 수 있다.

- 여러 task를 concurrent하게 실행해야 한다.
- user input, storage, hardware control, network stack처럼 서로 다른 기능을 분리하고 싶다.
- timing deadline을 만족해야 한다.
- wireless stack처럼 빠른 event response와 많은 resource가 필요한 library를 사용한다.
- 팀 프로젝트에서 기능을 task 단위로 나누어 개발하고 싶다.

반대로 다음 조건에서는 super loop나 interrupt만으로도 충분할 수 있다.

- task 수가 적고 각 task가 짧게 끝난다.
- CPU와 RAM이 매우 제한적이다.
- timing deadline이 필요한 작업이 한두 개이고 ISR로 해결 가능하다.
- RTOS의 scheduling, synchronization, debugging overhead가 더 큰 부담이다.

---

## 참고 자료

- [Introduction to RTOS Part 1 - What is a Real-Time Operating System (RTOS)? | Digi-Key Electronics (YouTube)](https://www.youtube.com/watch?v=F321087yYy4)
- [FreeRTOS](https://www.freertos.org/)
- [Zephyr Project](https://www.zephyrproject.org/)
- [Eclipse Foundation IoT Developer Survey 2018](https://iot.eclipse.org/community/resources/iot-surveys/)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** RTOS는 task의 timing deadline을 예측 가능하게 만족하도록 설계된 real-time operating system이다.
- **왜 필요:** Super loop는 구현이 단순하지만 한 task가 오래 걸리면 뒤의 작업이 밀리고, polling 중 입력이나 sensor data를 놓칠 수 있다. 여러 기능을 concurrent하게 처리하거나 strict timing deadline을 맞춰야 할 때 RTOS가 도움이 된다.
- **동작:** RTOS scheduler는 여러 task에 CPU 시간을 나누어 주고, priority를 통해 중요한 task가 먼저 실행되도록 제어한다. FreeRTOS에서는 task라는 용어가 thread에 가까운 CPU utilization 단위로 쓰인다.
- **비교:** General purpose OS는 human responsiveness를 우선해 non-deterministic scheduling을 허용하지만, RTOS는 deadline을 만족하는 예측 가능성이 핵심이다. 단순 MCU 작업에서는 super loop나 ISR이 더 적합할 수 있다.
- **30초 통합 답변:**
  > RTOS는 여러 task를 동시에 실행하는 것처럼 관리하면서, 각 task의 timing deadline을 예측 가능하게 만족하도록 설계된 운영체제입니다. Super loop는 단순하고 overhead가 작지만, 한 작업이 오래 걸리면 display update나 sensor polling 같은 뒤의 작업이 밀릴 수 있습니다. RTOS scheduler는 task에 CPU 시간을 나누고 priority를 적용해 중요한 작업을 먼저 처리하게 합니다. 다만 2KB RAM 수준의 작은 MCU나 1ms보다 짧은 정밀 timing 작업은 RTOS보다 super loop와 interrupt가 더 적합할 수 있습니다.
