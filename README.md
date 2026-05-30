# STM32F103 IMU-CAN Driver

STM32F103C8T6 (BluePill) bare-metal 펌웨어. MPU6050 IMU 센서를 I2C 레지스터 직접 제어로 읽고, CAN 버스로 자세 데이터를 송신합니다.

> 임베디드 SW 신입 포트폴리오. HAL 없이 레지스터 직접 제어로 구현해 MCU 동작 원리와 상태 플래그 흐름을 이해하는 것이 목표입니다.

<!-- TODO: 데모 GIF 또는 보드 사진 1장 첨부 -->
<!-- ![Demo](docs/validation/demo.gif) -->

## 1줄 요약

STM32F103 bare-metal firmware showing I2C register-level MPU6050 driver and CAN message transmission with UART logging.

## 보드 / MCU / 툴체인

- **MCU**: STM32F103C8T6 (BluePill) — ARM Cortex-M3, 72 MHz, 64 KB Flash, 20 KB SRAM
- **센서**: MPU6050 (AD0=GND, 7-bit addr `0x68`)
- **트랜시버**: TJA1050 (5V power, 3.3V logic compatible)
- **디버거**: ST-Link V2
- **UART 어댑터**: USB-TTL CP2102 (PA9 → RX, GND 공통)
- **툴체인**: STM32CubeIDE (arm-none-eabi-gcc)

## 핵심 주변장치

- I2C1 (PB6=SCL, PB7=SDA, 외부 4.7kΩ 풀업)
- bxCAN (PB8=RX, PB9=TX, 트랜시버 + 종단 120Ω)
- USART1 (PA9=TX, 115200 8N1, 로그용)
- SysTick (1 ms tick)

## 빌드와 플래시

### STM32CubeIDE
1. 본 repo 클론
2. CubeIDE에서 `File → Open Projects from File System` → 이 폴더 선택
3. `Build All`
4. ST-Link 연결 후 `Run`

### CLI (Make 기반은 백로그)

```bash
# 백로그: arm-none-eabi-gcc + st-flash 빌드 스크립트
./tools/flash.sh
```

## 검증 방법

이 펌웨어는 "동작했다"가 아니라 **검증 가능한 형태로** 확인했습니다.

- **UART 로그**: WHO_AM_I 응답값 + 가속도 raw 데이터 주기 출력 → `docs/validation/uart-log.md`
- **로직 분석기**: I2C START/ACK/STOP 시퀀스 캡처 → `docs/validation/logic-i2c.png`
- **CAN 송신**: candump 또는 PCAN으로 메시지 ID·payload 확인 → `docs/validation/can-trace.md`
- **재현 조건 표**: NACK, bus busy, 센서 전원 불안정, 클럭 설정 오류 케이스 → `docs/validation/failure-cases.md`

## 아키텍처 개요

```
+----------------+      I2C       +----------+
|  STM32F103     | <------------> |  MPU6050 |
|  (bare-metal)  |                +----------+
|                |      CAN
|                | <------------> CAN bus (TJA1050)
|                |      UART
|                | -------------> Host PC (CoolTerm)
+----------------+
```

자세한 구조: `docs/architecture.md`

## 회로 / 배선

- 핀맵: `hardware/pinmap.md`
- 배선 노트: `hardware/wiring-notes.md`
- (백로그) KiCad 회로도: `hardware/schematic/`

## Project Timeline

- **2026-05-22**: 프로젝트 시작 (트렌드 검증 후 임베디드 트랙 확정)
- **2026-05-27**: STM32F103 + bare-metal 진행 중. 산업장비 트랙 결정
- **진행 중**: I2C 레지스터 직접 read (MPU6050 WHO_AM_I 완료, 가속도 burst read 작업 중)
- **다음 마일스톤**: CAN 메시지 송신 통합 → bare-metal vs FreeRTOS 비교 데모

## 학습 진행 범위 (솔직 명시)

**완료**:
- I2C 레지스터 직접 제어 (START / ADDR / ACK 시퀀스, SR1+SR2 ADDR clear)
- MPU6050 WHO_AM_I 읽기 검증

**진행 중**:
- 가속도 6바이트 burst read
- CAN 메시지 ID·주기 설계 + 송신

**아직 안 함 (양산 코드 경험 없음)**:
- ASPICE / ISO 26262 절차 적용
- 양산 MCAL 또는 BSW 구조
- 회귀 테스트 자동화

## AI 도구 사용

학습 정리, 문서 초안, 코드 리뷰에 ChatGPT와 Claude를 사용했습니다. 최종 코드 작성·검증·설계 선택은 직접 수행했고, 동작은 실제 보드에서 확인했습니다.

## 한계와 다음 개선

- 현재는 polling 기반. 인터럽트·DMA 적용은 다음 단계
- 단일 보드 통신만. multi-node CAN arbitration 실험은 백로그
- FreeRTOS 비교 데모 → bare-metal vs RTOS task 분리 trade-off 검증 예정

## 연락

- Email: judyischicken@gmail.com
- GitHub: https://github.com/judymom

## 라이선스

MIT (`LICENSE` 참조)
