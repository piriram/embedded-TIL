# RTOS 선택 기준

> 출처: `10_주제별/cs/RTOS/1_RTOS란_무엇인가.md`
> 최종 갱신: 2026-05-21

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

RTOS는 모든 firmware 문제의 정답은 아니고, 상황에 따라 골라야 합니다. RTOS가 좋은 경우는 여러 task를 concurrent하게 실행해야 하거나, user input·storage·hardware control·network stack 같은 기능을 분리하고 싶을 때, timing deadline을 맞춰야 할 때, Wi-Fi나 Bluetooth처럼 빠른 event response와 많은 resource가 필요한 library를 쓸 때, 그리고 팀 프로젝트에서 기능을 task 단위로 나눠 개발할 때입니다. 반대로 2KB RAM 수준의 작은 8/16-bit MCU는 task switching의 memory·CPU overhead 때문에 application에 쓸 resource가 거의 안 남아서 super loop가 현실적입니다. task가 적고 짧거나, deadline 작업이 한두 개라 ISR로 해결되거나, RTOS의 scheduling·synchronization·debugging overhead가 더 부담이면 super loop나 interrupt로 충분합니다. ESP32처럼 clock과 memory 여유가 있는 MCU로 올라가면 RTOS가 현실적인 선택이 됩니다.

---

## 한 줄 정의

RTOS 선택은 task 수, 동시성 요구, timing deadline, resource 여유, 팀 개발 여부를 따져 정하는 trade-off다. 항상 정답은 아니다.

## 왜 필요한가

RTOS는 concurrent 실행과 deadline 보장을 주지만, task switching overhead와 scheduling/synchronization/debugging 비용도 같이 온다. 자원이 빠듯한 MCU에서 무턱대고 RTOS를 쓰면 application에 남는 resource가 거의 없어 오히려 손해다.

## 동작 원리

RTOS는 task switching 때 context를 저장·복원하므로 memory와 CPU overhead가 든다. 2KB RAM짜리 8/16-bit MCU에서는 이 overhead가 가용 resource의 큰 비중을 먹어 application 여지가 줄어든다. 반대로 ESP32는 clock cycle과 memory 여유가 있어 scheduler overhead를 감당하고, 애초에 그런 MCU를 고른 이유가 concurrent task를 돌리기 위해서인 경우가 많다.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** 여러 task concurrent 실행 / 기능 분리(input·storage·hardware·network) / timing deadline 만족 / Wi-Fi·BT 같은 무거운 stack / 팀 단위 task 분담
- **피하는 경우:** task가 적고 짧음 / CPU·RAM이 매우 제한적(2KB RAM급) / deadline 작업이 한두 개라 ISR로 해결 / RTOS overhead가 더 큰 부담

## 대표 예시

ESP32 — user input, SD card read/write, hardware control, number crunching을 동시에 수행하고 Wi-Fi/Bluetooth stack을 돌릴 때 RTOS가 큰 도움. 반대로 Arduino Uno(2KB RAM)는 FreeRTOS porting 사례는 있어도 overhead 때문에 super loop가 현실적.

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| RTOS | concurrent 실행·deadline·기능 분리 제공, 단 switching overhead와 debugging 비용 |
| Super loop | 단순·저overhead, task 적고 짧을 때 적합 |
| Interrupt(ISR) | deadline 작업이 한두 개일 때 RTOS 없이 해결 |

---

## 꼬리질문 예상

- **Q:** RAM이 작은 MCU에서 RTOS가 부적합한 이유는?
  **A:** task switching의 memory·CPU overhead 때문입니다. 2KB RAM 수준이면 overhead가 자원을 많이 먹어 application에 쓸 resource가 거의 안 남습니다.

- **Q:** FreeRTOS를 고르는 이유는?
  **A:** IoT device에서 인기가 많고 free·open source라 실습이 쉽습니다. 2017년부터 Amazon이 maintenance를 맡고 있고, ESP32는 modified FreeRTOS를 기본 탑재해 task 생성 setup이 거의 필요 없습니다.

- **Q:** RTOS를 쓰면 생기는 비용은?
  **A:** task 간 resource 관리, priority 설계, synchronization 문제를 확인해야 하고 debugging이 어려워집니다.

---

## 자주 하는 오해

- **오해:** RTOS는 firmware 문제의 정답이라 가능하면 항상 쓰는 게 좋다.
  - **정확히는:** RTOS는 trade-off다. task가 적거나 자원이 빠듯하면 super loop·ISR이 더 낫다. bare-metal super loop도 많은 문제에 충분히 좋은 해결책이다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| 메모리가 작아서 안 됨 | task switching의 memory·CPU overhead 부담 |
| 기능을 나눔 | 기능을 task 단위로 분리 |
| RTOS 쓰면 복잡해짐 | priority 설계·synchronization·debugging overhead 증가 |

---

## 키워드

`task switching overhead` `concurrent` `trade-off` `FreeRTOS` `ESP32` `super loop`
