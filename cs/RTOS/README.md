# RTOS 시리즈

Real-Time Operating System(RTOS)와 FreeRTOS 기초 개념을 정리하는 학습 노트 모음.

- **원본 강의:** Digi-Key Electronics RTOS / FreeRTOS YouTube 시리즈
- **실습 맥락:** ESP32, Arduino package, FreeRTOS

---

## 진도 표

| # | 제목 | 핵심 키워드 | 영상 | 상태 |
|---|------|------------|------|------|
| 1 | [RTOS란 무엇인가](./1_RTOS란_무엇인가.md) | RTOS, scheduler, deterministic timing, super loop, interrupt, task/thread/process, FreeRTOS, ESP32 | [YouTube](https://www.youtube.com/watch?v=F321087yYy4) | 완료 |
| 2 | [FreeRTOS 시작하기](./2_FreeRTOS_시작하기.md) | FreeRTOS source, FreeRTOSConfig.h, ESP-IDF, SMP, tick timer, vTaskDelay, xTaskCreatePinnedToCore, stack size, priority | [YouTube](https://www.youtube.com/watch?v=JIr7Xm_riRs) | 완료 |
| 3 | [Task Scheduling](./3_태스크_스케줄링.md) | tick, time slicing, priority, preemptive scheduling, round-robin, task state, context switching, ISR | [YouTube](https://www.youtube.com/watch?v=95yUbClyf3E) | 완료 |
| 4 | [RTOS 메모리 관리](./4_메모리_관리.md) | static allocation, stack, heap, TCB, stack canary, heap_1~heap_5, pvPortMalloc, vPortFree, memory leak | [YouTube](https://www.youtube.com/watch?v=Qske3yZRW5I) | 완료 |
| 6 | [Mutex](./6_Mutex.md) | race condition, shared resource, critical section, mutual exclusion, mutex, semaphore, xSemaphoreTake, xSemaphoreGive, task parameter lifetime | [YouTube](https://www.youtube.com/watch?v=I55auRpbiTs) | 완료 |
| 7 | [Semaphore](./7_세마포어.md) | semaphore, binary semaphore, counting semaphore, producer-consumer, mutex, priority inheritance, ISR, circular buffer | [YouTube](https://www.youtube.com/watch?v=5JcMtbA9QEE) | 완료 |
| 8 | [Software Timer](./8_Software_Timer.md) | software timer, timer service task, callback, command queue, one-shot timer, auto-reload timer, xTimerCreate, xTimerStart | [YouTube](https://www.youtube.com/watch?v=b1f1Iex0Tso) | 완료 |
| 9 | [Hardware Interrupts](./9_Hardware_Interrupts.md) | hardware interrupt, ISR, ESP32 timer, volatile, spin lock, critical section, FromISR API, binary semaphore, deferred interrupt, direct-to-task notification | [YouTube](https://www.youtube.com/watch?v=qsflCf6ahXU) | 완료 |
| 10 | [Deadlock and Starvation](./10_데드락과_스타베이션.md) | dining philosophers, starvation, aging, deadlock, timeout, livelock, lock hierarchy, arbitrator | [YouTube](https://www.youtube.com/watch?v=hRsWi4HIENc) | 완료 |
| 11 | [Priority Inversion](./11_Priority_Inversion.md) | priority inversion, bounded inversion, unbounded inversion, Mars Pathfinder, priority ceiling, priority inheritance, service task | [YouTube](https://www.youtube.com/watch?v=C2xKhxROmhA) | 완료 |
| 12 | [Multicore Systems](./12_멀티코어_시스템.md) | AMP, SMP, ESP32 dual-core, task affinity, core pinning, cache miss, multicore interrupt, spin lock, critical section | [YouTube](https://www.youtube.com/watch?v=LPSHUcH5aQc) | 완료 |

---

## 학습 흐름

1. **RTOS 도입 기준** — general purpose OS, super loop, interrupt, RTOS의 차이
2. **Task 생성과 실행** — FreeRTOS task, stack, scheduler 기본 사용법
3. **Scheduling과 priority** — time slicing, task priority, deadline 사고방식
4. **Resource management** — shared resource, semaphore, mutex
5. **Inter-task communication** — queue, event, task notification

---

## 파일 네이밍 규칙

- `N_제목.md` 형식 (예: `1_RTOS란_무엇인가.md`)
- `N`은 강의 회차 번호
- 제목은 한국어, 단어 사이는 `_`로 구분

---

## 관련 폴더

- [`../임베디드수업/`](../임베디드수업/) — MCU·MMIO·레지스터 기반 임베디드 기초
- [`../../stm32/베어메탈/`](../../stm32/베어메탈/) — STM32 베어메탈 실습 시리즈
- [`../../c언어/`](../../c언어/) — C 언어 기초
