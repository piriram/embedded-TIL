# Architecture

## 시스템 블록도

```
                     +---------------------+
                     |    STM32F103C8T6    |
                     |    (bare-metal)     |
                     |                     |
  +-------------+    |  +--------------+   |    +-------------+
  |  MPU6050    |<-->|  | I2C1 driver  |   |    |  CoolTerm   |
  |  (0x68)     |I2C |  |  (register   |   |UART|  (Host PC)  |
  +-------------+    |  |   direct)    |   |--->|             |
                     |  +--------------+   |    +-------------+
                     |         |           |
                     |         v           |
                     |  +--------------+   |
                     |  | App layer    |   |
                     |  |  - sensor    |   |
                     |  |    read loop |   |
                     |  |  - CAN tx    |   |
                     |  +--------------+   |
                     |         |           |
                     |         v           |
                     |  +--------------+   |    +-------------+
                     |  | bxCAN driver |   |CAN |  TJA1050    |
                     |  +--------------+   |--->|  + bus      |
                     +---------------------+    +-------------+
```

## 디렉토리 구조

- `30_프로젝트/docs/`: 설계 문서 + 검증 자료
- `30_프로젝트/sim/`: SIL 시뮬레이터
- `30_프로젝트/tools/`: 빌드/플래시 스크립트
- `10_주제별/hardware/`: 회로·배선 자료

## bare-metal 구조 선택 이유

이 프로젝트는 HAL을 사용하지 않고 레지스터 직접 제어로 구현합니다. 학습·검증 목적이 핵심입니다:

- I2C 상태 플래그 (SB / ADDR / TXE / BTF / RXNE) 흐름 손에 익히기
- ADDR 클리어 시퀀스 (SR1 → SR2 순서) 같은 RM0008 26.6 절 함정 직접 만져보기
- CAN arbitration·error frame·bus-off 같은 상태를 데이터시트 레벨에서 이해

실무에서는 HAL/LL이 더 적절할 수 있다는 점을 인지하고 있습니다.

## 클럭 트리

- HSE 8 MHz → PLL ×9 → SYSCLK 72 MHz
- AHB 72 MHz (HCLK)
- APB1 36 MHz (I2C1, CAN, USART2)
- APB2 72 MHz (USART1)
- SysTick: 72 MHz / 8 = 9 MHz → 1 ms tick = reload 8999

자세한 RCC 설정은 `Core/Src/main.c` `SystemClock_Config()` 참조.

## 메모리 맵 (요약)

| 영역 | 시작 주소 | 크기 |
|------|---------|------|
| Flash | `0x08000000` | 64 KB |
| SRAM | `0x20000000` | 20 KB |
| Peripheral | `0x40000000` | (RM0008 표 1 참조) |

## 백로그

- 인터럽트 기반 I2C
- DMA 활성화
- FreeRTOS 3-task 비교 데모 (별도 폴더 또는 별도 repo)
- micro-ROS (F103 SRAM 제약으로 지원 보드 변경 후 실험)
