# TIL — Embedded SW

임베디드 SW 학습 기록. 학습 순서대로 번호를 붙여 구성했다.

## 구조

```
embedded-TIL/
├── 01_c/           C 언어 핵심 (포인터, 비트연산, volatile, 구조체 등)
├── 02_stm32/       STM32F103 주제별 (GPIO·UART·I2C·CAN·ADC·Timer)
├── 03_cs/          임베디드 CS 이론 (임베디드수업 MOOC, RTOS)
├── 04_hardware/    하드웨어 실습 (납땜, Breadboard, 핀맵, 결선)
├── 05_필기노트/    시리즈 강의 필기노트 (포폴시작전, STM32 MOOC)
├── 06_interview/   면접 답변카드, 오답노트
├── 07_project/     IMU-CAN 드라이버 프로젝트 문서·시뮬레이터·도구
└── 90_templates/   학습노트·답변카드 템플릿
```

## 학습 순서

```
01_c → 02_stm32 (GPIO → UART → I2C → CAN) → 03_cs (RTOS) → 07_project
```

## Quick Links

### C 언어
- [포인터](./01_c/010_포인터.md) · [비트연산](./01_c/040_비트연산자.md) · [volatile & Preprocessor](./01_c/050_Preprocessor와_volatile.md)
- [C 심화 강의](./01_c/C_심화_강의/)

### STM32
- [GPIO](./02_stm32/gpio/) · [UART](./02_stm32/uart/) · [I2C](./02_stm32/i2c/) · [CAN](./02_stm32/can/) · [ADC](./02_stm32/adc/) · [Timer](./02_stm32/timer/)
- [베어메탈 & MMIO](./02_stm32/01_베어메탈과_MMIO.md) · [RCC 클럭](./02_stm32/04_RCC_클럭제어와_버스구조.md)

### CS / RTOS
- [임베디드수업](./03_cs/임베디드수업/) · [RTOS](./03_cs/RTOS/)

### 프로젝트
- [아키텍처](./07_project/docs/architecture.md)
- [SIL 시뮬레이터](./07_project/sim/)
- [검증 자료](./07_project/docs/validation/)

### 면접
- [답변카드](./06_interview/답변카드/) · [오답노트](./06_interview/_오답노트.md)

## License

MIT ([LICENSE](./LICENSE))
