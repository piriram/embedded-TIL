# Task, Thread, Process 용어

> 출처: `10_학습자료/cs/RTOS/1_RTOS란_무엇인가.md`
> 최종 갱신: 2026-05-21

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

task, thread, process는 자주 섞이는 용어입니다. task는 코드에서 끝내야 하는 작업 단위이고, thread는 자기 program counter와 memory set을 가진 CPU utilization 단위입니다. process는 실행 중인 프로그램의 instance이며, 보통 task를 수행하기 위해 하나 이상의 thread를 가집니다. 일반 OS에서 한 process 안의 thread들은 heap 같은 resource를 공유하고 서로 자원을 전달할 수 있습니다. 차이를 보면, 많은 RTOS는 하나의 process만 다루는 구조에 가깝고 general purpose OS는 여러 process를 동시에 돌립니다. 그리고 FreeRTOS에서는 task라는 용어를 thread에 가까운 의미, 즉 CPU utilization 단위로 씁니다. 그래서 FreeRTOS 문맥에서는 task와 thread가 혼용됩니다.

---

## 한 줄 정의

task는 끝내야 하는 작업 단위, thread는 자기 program counter와 memory set을 가진 CPU utilization 단위, process는 실행 중인 프로그램의 instance다.

## 왜 필요한가

RTOS와 OS를 설명할 때 이 세 용어가 자주 섞인다. 특히 FreeRTOS는 task를 thread 의미로 쓰기 때문에, 용어의 원래 정의와 FreeRTOS 관용을 구분하지 못하면 답변이 흔들린다.

## 동작 원리

process는 thread를 하나 이상 담는 컨테이너다. 한 process 안의 thread들은 heap memory 같은 resource를 공유하고 서로 전달할 수 있다. 각 thread는 own program counter와 memory set을 가져 독립적으로 CPU를 점유한다. task는 추상적인 "할 일" 단위로, thread가 수행하는 대상이다.

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** FreeRTOS 문맥에서는 CPU utilization 단위를 가리킬 때 "task"라고 부른다 (thread와 사실상 동일 의미)
- **피하는 경우:** 일반 OS 이론을 말할 때는 task(작업 단위)와 thread(실행 단위)를 구분해서 써야 한다

## 대표 예시

일반 OS: 브라우저 = process, 그 안의 탭 렌더링 = thread, "이미지 디코딩" = task.
FreeRTOS: `xTaskCreate`로 만든 task = 사실상 thread(CPU utilization 단위).

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| Task | 끝내야 하는 작업 단위 (추상적). FreeRTOS에서는 thread 의미로 전용 |
| Thread | own program counter + memory set을 가진 CPU utilization 단위 |
| Process | 실행 중인 프로그램 instance. thread 1개 이상 보유, RTOS는 보통 1 process |

---

## 꼬리질문 예상

- **Q:** FreeRTOS의 task는 OS 이론의 task와 같은 뜻인가요?
  **A:** 아닙니다. FreeRTOS는 task를 thread에 가까운 CPU utilization 단위로 씁니다. 이론상의 "작업 단위"와는 다릅니다.

- **Q:** RTOS와 general purpose OS의 process 처리 차이는?
  **A:** 많은 RTOS는 하나의 process만 다루는 구조에 가깝고, general purpose OS는 여러 process를 동시에 실행할 수 있습니다.

- **Q:** 한 process 안 thread들은 무엇을 공유하나요?
  **A:** heap memory 같은 resource를 공유하고 서로 자원을 전달할 수 있습니다. program counter와 memory set은 thread마다 따로 가집니다.

---

## 자주 하는 오해

- **오해:** task와 thread는 항상 다른 것이다.
  - **정확히는:** 일반 OS 이론에서는 다르지만, FreeRTOS에서는 task를 thread 의미로 써서 두 용어가 혼용된다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-----------|
| 프로그램 | 실행 중인 instance = process |
| 동시에 도는 거 | CPU utilization 단위 = thread |
| 할 일 | 작업 단위 = task |

---

## 키워드

`task` `thread` `process` `program counter` `CPU utilization` `FreeRTOS`
