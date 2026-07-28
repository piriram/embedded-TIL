# 임베디드 수업 시리즈

MCU·임베디드 시스템 기초 개념 강의 정리. Lesson 단위로 순차 학습.

- **원본 강의:** Modern Embedded Systems Programming (Miro Samek, YouTube 시리즈)

---

## 진도 표

| # | 제목 | 핵심 키워드 | 영상 | 상태 |
|---|------|------------|------|------|
| 0 | [시작하기 — 개발 환경 세팅](./0_시작하기_개발환경_세팅.md) | ARM Cortex-M, TivaC/NUCLEO, 하드웨어 디버거, IAR/KEIL MDK, Device Family Pack | [YouTube](https://www.youtube.com/watch?v=hnj-7XwTYRI) | 완료 |
| 1 | [컴퓨터는 어떻게 숫자를 세는가](./1_컴퓨터는_어떻게_숫자를_센다.md) | 변수, machine instruction, CPU 레지스터(R0~R15), PC, 16진법/nibble, 2의 보수, signed overflow | [YouTube](https://www.youtube.com/watch?v=gQOv8o5lS2k) | 완료 |
| 2 | [코드의 제어 흐름 바꾸기 — loop와 if](./2_제어흐름_바꾸기_loop와_if.md) | while 루프, B/CMP/BLT 명령어, APSR, branch 인코딩, instruction pipeline, pipeline stall, loop unrolling, if/bitwise AND | [YouTube](https://www.youtube.com/watch?v=cZj284kfuE8) | 완료 |
| 4 | [외부 세계를 어떻게 통제할까 — LED 블링크](./4_외부세계_통제하기_LED_블링크.md) | GPIO, datasheet/memory map, clock gating, 레지스터 비트(RO/RW/WO), pointer hack, 무한 루프, delay 루프 | [YouTube](https://www.youtube.com/watch?v=1Kjh0CAgnl4) | 완료 |
| 8 | [MCU Memory Map & Memory Mapped I/O](./8_MCU_메모리맵과_MMIO.md) | MMIO, Peripheral register, Base+Offset, Vector table, Hard Fault | [YouTube](https://www.youtube.com/watch?v=bWMsBXNAOAE) | 완료 |
| 15 | [Startup Code — 벡터 테이블, 예외, 인터럽트 핸들러](./15_스타트업코드_벡터테이블_예외_ISR.md) | initial MSP, Reset Handler, vector table, weak alias, fault injection, stackless handler | [YouTube](https://www.youtube.com/watch?v=42HbCf5cz5A) | 완료 |
| 16 | [인터럽트의 개념과 동작 원리 — Part 1](./16_인터럽트의_개념과_동작원리.md) | Interrupt, polling, SysTick, preemption, asynchronous, ISR, PRIMASK | [YouTube](https://www.youtube.com/watch?v=jP1JymlHUtc) | 완료 |
| 18 | [ARM Cortex-M 인터럽트 진입과 복귀 — Part 3](./18_ARM_Cortex_M_인터럽트_진입과_복귀.md) | exception entry, stack frame, AAPCS, EXC_RETURN, MSP/PSP, FPU, stack alignment | [YouTube](https://www.youtube.com/watch?v=O0Z1D6p7J5A) | 완료 |
| 33 | [이벤트 주도 프로그래밍 — GUI, 이벤트 루프, Run-to-Completion, 비차단](./33_이벤트_주도_프로그래밍_GUI_이벤트루프와_비차단.md) | event, message queue, event loop, asynchronous, RTC, inversion of control, `WM_TIMER`, no-blocking | [YouTube](https://www.youtube.com/watch?v=rfb2JI1GGIc) | 완료 |
| 21 | [전경-배경 아키텍처 — Super Loop와 Main+Interrupts](./21_전경_배경_아키텍처_슈퍼루프.md) | foreground/background, super loop, main+ISRs, BSP, volatile, critical section, blocking, event-driven state machine | [YouTube](https://www.youtube.com/watch?v=AoLLKbvEY8Q) | 완료 |

---

## 학습 흐름

1. **메모리 vs I/O** — 두 시나리오의 본질적 차이
2. **MMIO 추상화** — 주소 공간 통일, separate I/O space와의 비교
3. **Peripheral 구조** — Base Address + Offset, C 구조체 매칭
4. **메모리 맵 전체** — Flash, SRAM, Peripheral 영역 배치
5. **Reset Vector / Interrupt Vector Table** — 부팅 메커니즘
6. **Polling에서 interrupt로** — SysTick이 시간을 세고 CPU 실행 흐름을 선점하는 과정
7. **Interrupt 활성화 조건** — Peripheral 설정, vector table, ISR, PRIMASK의 협력
8. **Cortex-M exception entry/return** — AAPCS와 8-word stack frame, `EXC_RETURN`, stack alignment, FPU frame
10. **Event-driven programming** — GUI의 event queue·event loop, asynchronous delivery, RTC, timer 기반 no-blocking
9. **전경-배경 아키텍처** — super loop와 ISR의 역할, 공유 변수 보호, blocking·non-blocking event-driven 상태기계, BSP 분리

---

## 파일 네이밍 규칙

- `N_제목.md` 형식 (예: `8_MCU_메모리맵과_MMIO.md`)
- `N`은 Lesson 번호
- 제목은 한국어, 단어 사이는 `_`로 구분

---

## 관련 폴더

- [`../../stm32/베어메탈/`](../../stm32/베어메탈/) — STM32 베어메탈 실습 시리즈
- [`../../c언어/`](../../c언어/) — C 언어 기초 (Preprocessor·volatile, 포인터, static 등)
