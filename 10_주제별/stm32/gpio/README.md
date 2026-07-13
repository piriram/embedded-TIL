# STM32 GPIO

STM32F767 GPIO 학습 노트. 레지스터 직접 제어 방식.

- **타겟 MCU:** STM32F767VIT6
- **원본 강의:** [(210) STM32 입문 강의 몰아보기 (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)

---

## 진도 표

| # | 제목 | 핵심 키워드 | 상태 |
|---|------|------------|------|
| 1 | [GPIO 출력과 LED 제어](./1_GPIO출력과_LED제어.md) | MODER/OTYPER/OSPEEDR/ODR, RCC, 푸시풀, CubeIDE 디버깅 | 완료 |
| 2 | [GPIO 입력과 스위치](./2_GPIO입력과_스위치.md) | IDR, Schmitt Trigger, 풀업, FT 핀, AND 마스킹 | 완료 |
| 3 | [GPIO BSRR로 안전하게 출력하기](./3_GPIO_BSRR로_안전하게_출력하기.md) | BSRR, ODR, RMW, atomic set/reset, ISR 경쟁 조건 | 완료 |

---

## 관련 폴더

- [`../기초/`](../기초/) — ARM 구조·레지스터 접근·클럭·인터럽트 (강의 전체 진도표)
- [`../adc/`](../adc/), [`../timer/`](../timer/), [`../uart/`](../uart/)
