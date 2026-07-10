# Super Loop의 한계

> 출처: `10_학습자료/cs/RTOS/1_RTOS란_무엇인가.md`
> 최종 갱신: 2026-05-21

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

Super loop의 핵심 한계는 task를 실제로 동시에 실행할 수 없다는 점입니다. task를 순서대로 돌기 때문에, 앞쪽 task가 오래 걸리기 시작하면 뒤 task의 display update가 늦어져 사용자가 화면 lag를 느낍니다. 또 serial terminal에서 user input을 polling하거나 sensor data를 읽는 구조라면, 다른 task가 길게 도는 동안 입력이나 데이터를 놓칠 수 있습니다. multi-core processor라면 물리적으로 동시 실행이 가능하지만 많은 microcontroller는 single-core라서 CPU 시간을 task끼리 나눠 써야 합니다. RTOS는 이때 task별로 CPU 시간을 나누고 priority를 줄 수 있어서, 예를 들어 user input task의 priority를 높이면 사용자가 lag를 덜 느끼게 됩니다. 대신 background task는 더 늦게 끝납니다.

---

## 한 줄 정의

Super loop는 task를 round-robin으로 순차 실행하므로 진짜 concurrent 실행이 불가능하다. 한 task가 길어지면 뒤 task가 그만큼 밀린다.

## 왜 필요한가

한 task의 지연이 그대로 뒤 task로 전파되면, display lag나 input/data 유실이 생긴다. 여러 기능을 안정적으로 동시 처리하려면 CPU 시간을 task 사이에 나눌 수단이 필요하다 — RTOS scheduler가 그 역할을 한다.

## 동작 원리

Super loop는 task를 한 줄로 세워 순서대로 돈다. task 2가 길어지면 그 뒤의 task 3 display update가 늦어진다. polling 기반 input/sensor 읽기는 다른 task가 도는 동안 event를 놓친다. single-core MCU는 물리적 동시 실행이 불가능하므로 CPU 시간을 나눠 써야 하는데, RTOS scheduler는 task에 time slice를 배분하고 priority로 중요한 task를 먼저 실행시킨다.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우(RTOS 도입):** 한 task의 지연이 다른 task에 영향을 주면 안 될 때, user input 같은 task에 priority가 필요할 때
- **피하는 경우:** task가 모두 짧아 지연 전파가 문제되지 않을 때는 super loop로 충분

## 대표 예시

task 2(긴 계산) → task 3(display update) 순서일 때, task 2가 길어지면 화면 갱신이 눈에 띄게 lag. user input task의 priority를 높이면 입력 반응은 빨라지지만 background task는 늦게 끝남.

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| Super loop | 순차 실행. 앞 task 지연이 뒤 task로 전파, priority 개념 없음 |
| RTOS scheduler | task에 time slice 배분 + priority. 중요한 task 먼저, 단 overhead 발생 |
| Multi-core | 물리적 동시 실행 가능. 단 많은 MCU는 single-core |

---

## 꼬리질문 예상

- **Q:** Super loop에서 한 task가 오래 걸리면 무슨 문제가 생기나요?
  **A:** 뒤 task의 display update가 밀려 화면 lag가 생기고, polling 중인 input이나 sensor data를 놓칠 수 있습니다.

- **Q:** RTOS에서 priority를 높이면 다 좋아지나요?
  **A:** 아닙니다. 높인 task는 빨라지지만 그만큼 background task는 늦게 끝납니다. priority는 trade-off입니다.

- **Q:** Single-core MCU에서도 RTOS가 의미 있나요?
  **A:** 네. 물리적 동시 실행은 안 되지만, CPU 시간을 task끼리 나눠 동시에 도는 것처럼 만들고 priority로 제어할 수 있습니다.

---

## 자주 하는 오해

- **오해:** RTOS를 쓰면 task가 진짜 동시에 실행된다.
  - **정확히는:** single-core에서는 CPU 시간을 잘게 나눠 동시 실행처럼 보이게 할 뿐이다. 물리적 동시 실행은 multi-core에서만 가능하다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| 화면이 버벅임 | display update 지연으로 인한 lag |
| 입력을 놓침 | polling 중 다른 task가 길어 event 유실 |
| 동시에 돌림 | time slice 배분으로 concurrent 실행처럼 보이게 함 |

---

## 키워드

`concurrent` `time slice` `priority` `single-core` `display lag` `polling`
