# 임베디드 수업 시리즈

MCU·임베디드 시스템 기초 개념 강의 정리. Lesson 단위로 순차 학습.

- **원본 강의:** YouTube embedded systems 강의 시리즈

---

## 진도 표

| # | 제목 | 핵심 키워드 | 영상 | 상태 |
|---|------|------------|------|------|
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
