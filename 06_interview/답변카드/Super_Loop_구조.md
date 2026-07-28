# Super Loop 구조

> 출처: `10_주제별/cs/RTOS/1_RTOS란_무엇인가.md`
> 최종 갱신: 2026-05-21

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

Super loop는 setup function을 한 번 수행한 뒤, 무한 루프 안에서 여러 task를 round-robin 방식으로 반복 실행하는 구조입니다. Arduino를 포함한 많은 microcontroller 프로그램이 이 구조를 씁니다. 구현이 쉽고 CPU cycle과 memory를 적게 쓰며 debugging도 RTOS보다 훨씬 쉬워서, 단순한 project에는 오히려 더 나은 선택입니다. 여기에 interrupt를 함께 쓰면 button push 같은 외부 event나 timed interval 작업을 처리할 수 있습니다. strict timing deadline이 한두 개라면 RTOS보다 ISR이 더 적합한데, 경험적으로 1ms보다 짧은 deadline은 interrupt를 쓰는 게 낫고, 수백 ns보다 짧으면 FPGA 같은 hardware를 봐야 합니다. 그리고 RTOS를 써도 interrupt는 그대로 동작하며, interrupt priority가 task보다 높으면 task 실행을 멈추고 ISR을 처리한 뒤 복귀합니다.

---

## 한 줄 정의

Super loop는 setup 후 무한 루프 안에서 여러 task를 round-robin으로 반복 실행하는 구조다. 구현이 쉽고 overhead가 작다.

## 왜 필요한가

대부분의 단순한 microcontroller project는 해야 할 일이 몇 개뿐이고 각 일이 짧게 끝난다. 이런 경우 RTOS의 scheduling/synchronization overhead 없이도 동작하므로, 더 단순하고 가벼운 super loop가 적합하다.

## 동작 원리

프로그램 시작 시 setup function을 1회 수행하고, `while(forever)` 무한 루프 안에서 task를 순서대로(round-robin) 돈다. 각 task는 sensor 읽기, 계산, LED display 출력 등을 한다. interrupt를 추가하면 외부 event 발생 시 execution flow를 끊고 ISR을 실행한 뒤 원래 지점으로 복귀한다. 이 동작은 RTOS를 써도 동일하다 — interrupt priority가 task보다 높으면 모든 task를 멈추고 ISR을 처리한다.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** task 수가 적고 각 task가 짧게 끝나며 복잡한 동시성이 없을 때. strict deadline이 한두 개면 super loop + ISR
- **피하는 경우:** 여러 task를 진짜 concurrent하게 돌려야 하거나, 한 task가 길어 뒤 task가 밀리는 게 문제일 때

## 대표 예시

Arduino 기본 구조: `setup()` 1회 → `loop()` 안에서 sensor 읽고 계산하고 출력 반복. 1ms보다 짧은 정밀 작업은 ISR로 분리.

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| RTOS scheduler | 여러 task에 CPU 시간을 나누고 priority 적용. overhead·debugging 비용 큼 |
| Interrupt(ISR) | 짧고 정확한 timing 작업에 적합. 1ms 미만 deadline은 ISR이 유리 |
| FPGA / custom hardware | 수백 ns 미만 timing은 hardware 검토 대상 |

---

## 꼬리질문 예상

- **Q:** RTOS가 interrupt를 대체하나요?
  **A:** 아닙니다. RTOS를 써도 interrupt는 그대로 동작합니다. 아주 짧고 정확한 timing은 여전히 ISR이나 hardware가 더 알맞습니다.

- **Q:** 어느 정도 짧은 deadline부터 interrupt를 쓰나요?
  **A:** 경험적으로 1ms보다 짧으면 interrupt가 낫고, 수백 ns보다 짧으면 빠른 processor나 FPGA 같은 custom hardware를 봐야 합니다.

- **Q:** RTOS에서 interrupt와 task의 우선순위 관계는?
  **A:** interrupt priority가 task보다 높으면, interrupt는 모든 task 실행을 멈추고 ISR을 처리한 뒤 멈췄던 지점으로 복귀합니다.

---

## 자주 하는 오해

- **오해:** RTOS를 도입하면 super loop와 interrupt는 더 안 쓴다.
  - **정확히는:** interrupt는 RTOS 위에서도 동작하고, 단순 project에는 super loop가 여전히 더 나은 선택일 수 있다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| 무한 반복 | round-robin 방식으로 task 반복 실행 |
| 끼어들기 | interrupt가 execution flow를 끊고 ISR 실행 후 복귀 |
| 빠른 작업은 따로 | strict timing deadline 작업은 ISR로 분리 |

---

## 키워드

`super loop` `round-robin` `interrupt` `ISR` `timing deadline` `overhead`
