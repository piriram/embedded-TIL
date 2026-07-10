# STM32 입문 — 기초 개념

STM32F767 입문 강의 중 **공통 기초 개념**(ARM 코어·버스, 레지스터 직접 접근, 클럭, 인터럽트) 학습 노트 모음.

- **타겟 MCU:** STM32F767VIT6 (ARM Cortex-M7)
- **환경:** STM32CubeIDE + CMSIS 헤더, 레지스터 직접 제어 (HAL 그래픽 설정 미사용)
- **원본 강의:** [(210) STM32 입문 강의 몰아보기 | ARM, GPIO, ADC, UART (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)
- **최종 목표:** 전동 킥보드 삼상 인버터로 BLDC 모터 제어

> 같은 강의에서 갈라진 주제별 노트는 [`../gpio/`](../gpio/), [`../adc/`](../adc/), [`../timer/`](../timer/), [`../uart/`](../uart/)에 있다.

---

## 진도 표 (이 강의 전체)

| # | 제목 | 핵심 키워드 | 폴더 | 상태 |
|---|------|------------|------|------|
| 1 | [ARM 코어와 MCU 버스 구조](./1_ARM코어와_MCU버스구조.md) | Cortex-M7, AHB/APB, 클럭 동기, 데이터시트 | 기초 | 완료 |
| 2 | [GPIO 출력과 LED 제어](../gpio/1_GPIO출력과_LED제어.md) | MODER/OTYPER/OSPEEDR/ODR, RCC, CubeIDE | gpio | 완료 |
| 3 | [레지스터 직접 접근(메모리 맵)](./2_레지스터_직접접근_메모리맵.md) | 베이스+오프셋, 포인터 캐스팅, 구조체 | 기초 | 완료 |
| 4 | [GPIO 입력과 스위치](../gpio/2_GPIO입력과_스위치.md) | IDR, Schmitt Trigger, FT 핀, AND 마스킹 | gpio | 완료 |
| 5 | [클럭과 PLL 설정](./3_클럭과_PLL설정.md) | HSE/HSI/LSE/LSI, PLL, 오버드라이브, init_MCU | 기초 | 완료 |
| 6 | [인터럽트 NVIC/EXTI](./4_인터럽트_NVIC_EXTI.md) | 폴링vs인터럽트, 벡터 테이블, ISR, 토글 | 기초 | 완료 |
| 7 | [ADC 원리와 실습](../adc/1_ADC원리와_실습.md) | 샘플링/양자화, 분해능, SAR, 레귤러/인젝티드 | adc | 완료 |
| 8 | [타이머/카운터와 PWM](../timer/1_타이머카운터와_PWM.md) | ARR/CCR, 센터얼라인, 상보출력, 데드타임 | timer | 완료 |
| 9 | [UART 통신](../uart/1_UART통신.md) | 비동기 직렬, 보레이트, TXE/RXNE, TX↔RX | uart | 완료 |

---

## 학습 흐름

1. **MCU 구조 이해** — ARM 코어 + 주변 장치 + 버스, 클럭 동기
2. **GPIO 출력** — 레지스터로 LED 제어, CubeIDE 디버깅
3. **레지스터 직접 접근** — 메모리 맵, 포인터, 구조체 (CMSIS 헤더 원리)
4. **GPIO 입력** — 스위치 읽기
5. **클럭/PLL** — 216MHz 만들기, `init_MCU`
6. **인터럽트** — NVIC/EXTI
7. **ADC** → 8. **타이머/PWM** → 9. **UART**

---

## 파일 네이밍 규칙

- `N_제목.md` 형식 (N = 강의 회차)
- 제목은 한국어, 단어 사이는 `_`

---

## 관련 폴더

- [`../gpio/`](../gpio/), [`../adc/`](../adc/), [`../timer/`](../timer/), [`../uart/`](../uart/)
- [`../베어메탈/`](../베어메탈/) — **별개 시리즈** (STM32F407, 영어 강의, 순수 C 부트스트랩)
