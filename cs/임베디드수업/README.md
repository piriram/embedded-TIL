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

---

## 학습 흐름

1. **메모리 vs I/O** — 두 시나리오의 본질적 차이
2. **MMIO 추상화** — 주소 공간 통일, separate I/O space와의 비교
3. **Peripheral 구조** — Base Address + Offset, C 구조체 매칭
4. **메모리 맵 전체** — Flash, SRAM, Peripheral 영역 배치
5. **Reset Vector / Interrupt Vector Table** — 부팅 메커니즘

---

## 파일 네이밍 규칙

- `N_제목.md` 형식 (예: `8_MCU_메모리맵과_MMIO.md`)
- `N`은 Lesson 번호
- 제목은 한국어, 단어 사이는 `_`로 구분

---

## 관련 폴더

- [`../../stm32/베어메탈/`](../../stm32/베어메탈/) — STM32 베어메탈 실습 시리즈
- [`../../c언어/`](../../c언어/) — C 언어 기초 (Preprocessor·volatile, 포인터, static 등)
