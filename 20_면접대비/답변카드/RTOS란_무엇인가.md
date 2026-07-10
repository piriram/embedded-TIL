# RTOS란 무엇인가

> 출처: `10_학습자료/cs/RTOS/1_RTOS란_무엇인가.md`
> 최종 갱신: 2026-05-21

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

RTOS는 task의 timing deadline을 예측 가능하게 만족하도록 설계된 운영체제입니다. RTOS도 기본적으로는 OS라서 task scheduling, resource 관리, device driver 같은 기능을 제공하지만, general purpose OS와 목적이 다릅니다. Windows나 macOS 같은 general purpose OS는 human responsiveness를 우선해서 scheduler가 non-deterministic하게 동작하고, deadline이 조금 밀려도 사람이 못 느끼면 허용합니다. 반면 RTOS는 scheduler가 정해진 시간 안에 task를 끝내도록 설계됩니다. 그래서 engine controller나 medical device처럼 deadline을 놓치면 치명적인 시스템에 적합합니다. 여기서 real-time은 무조건 빠르다는 뜻이 아니라, 정해진 시간 안에 예측 가능하게 동작한다는 뜻입니다.

---

## 한 줄 정의

RTOS는 task의 timing deadline을 예측 가능하게 만족하도록 설계된 real-time operating system이다. 핵심은 속도가 아니라 timing의 예측 가능성(determinism)이다.

## 왜 필요한가

General purpose OS의 scheduler는 non-deterministic해서 task가 정확히 언제 실행될지 보장하지 못한다. engine controller가 spark plug를 제때 점화하지 못하는 식으로 deadline을 놓치면 치명적인 시스템에서는, deadline을 보장하는 scheduler가 필요하다.

## 동작 원리

RTOS도 OS이므로 task scheduling, virtual resource 관리, device driver 제공을 한다. 다만 scheduler가 task의 timing deadline을 만족하도록 설계된다는 점이 다르다. RTOS마다 제공 범위는 다르며, Wi-Fi/Bluetooth stack 같은 high-level driver까지 주는 것도 있고, scheduler만 주는 bare-bones한 것도 있다.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** strict timing deadline을 만족해야 하거나, 여러 task를 concurrent하게 실행해야 할 때
- **피하는 경우:** 단순 MCU 작업처럼 super loop나 ISR로 충분할 때

## 대표 예시

medical device, engine controller — deadline 위반이 단순 지연이 아니라 시스템 전체 위험으로 이어지는 장치.

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| General purpose OS | human responsiveness 우선, non-deterministic scheduling, deadline 다소 밀려도 허용 |
| RTOS | timing deadline 만족이 목적, deterministic, 예측 가능성이 핵심 |

---

## 꼬리질문 예상

- **Q:** RTOS의 "real-time"이 빠르다는 뜻인가요?
  **A:** 아닙니다. 정해진 시간 안에 예측 가능하게(deterministic) 동작한다는 뜻입니다. 절대 속도가 아니라 timing 보장이 핵심입니다.

- **Q:** RTOS를 쓰는 이유가 timing deadline 때문만인가요?
  **A:** 아닙니다. 여러 task를 concurrent하게 실행하는 구조를 만들 수 있다는 점도 큰 이유입니다.

- **Q:** RTOS는 항상 filesystem이나 driver를 제공하나요?
  **A:** 아닙니다. RTOS마다 범위가 다릅니다. bare-bones한 RTOS는 scheduler만 주고, filesystem이나 driver는 직접 작성해야 합니다.

---

## 자주 하는 오해

- **오해:** RTOS는 일반 OS보다 빠르다.
  - **정확히는:** RTOS는 빠른 게 아니라 timing이 예측 가능한 것이다. determinism이 핵심이지 throughput이 아니다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| 실시간이라 빠름 | 정해진 시간 안에 예측 가능하게 동작 (deterministic) |
| 일반 OS는 느림 | non-deterministic scheduling, human responsiveness 우선 |
| 제때 못 함 | timing deadline을 놓침 (miss the deadline) |

---

## 키워드

`timing deadline` `deterministic` `scheduler` `non-deterministic` `general purpose OS`
