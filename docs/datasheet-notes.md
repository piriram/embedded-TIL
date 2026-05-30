# Datasheet Notes

펌웨어 작성 중 참고한 데이터시트 / 레퍼런스 매뉴얼 인용. 페이지·섹션·표·그림 번호까지 가능한 한 명시.

## STM32F103 RM0008 (Reference Manual)

- **§7 RCC**: 클럭 트리, HSE/PLL 설정, APB1/APB2 prescaler
- **§9 GPIO**: AF Open-drain 모드 (I2C용), AF Push-pull (UART TX)
- **§14 NVIC**: 인터럽트 우선순위 grouping
- **§24 USART**: BRR 계산, 8N1 프레임
- **§26 I2C**: 26.6.1 (Master mode), 26.6.7 (Status flags), 26.6.9 (TRISE)
  - **핵심 함정**: ADDR 클리어 = SR1 → SR2 순서 read (26.6.1 sequence diagram)
  - 1-byte read: ACK=0 + STOP 세팅을 ADDR 클리어 **직전**에
- **§24/Section "bxCAN"**: arbitration, mailbox, filter, error state

## MPU6050 Register Map (InvenSense)

- **WHO_AM_I (0x75)**: 기대값 `0x68`
- **PWR_MGMT_1 (0x6B)**: device reset, sleep, clock source
- **ACCEL_XOUT_H (0x3B)**: 가속도 X high. burst read 6바이트로 X/Y/Z 한 번에
- **GYRO_XOUT_H (0x43)**: 자이로 X high
- **SMPLRT_DIV (0x19)**: 샘플레이트 분주

## NXP I2C-bus Specification (UM10204)

- §3.1: SDA/SCL 양방향, open-drain, pull-up 또는 current source
- §3.1.5: Wired-AND 구조
- §6: I2C 표준 모드 100 kbit/s, Fast mode 400 kbit/s

## CAN 2.0A (Bosch)

- §3: Frame format (SOF, ID, RTR, IDE, r0, DLC, data, CRC, ACK, EOF)
- §7: Bit timing, sample point
- §8: Error handling (active, passive, bus-off)

## TJA1050 Datasheet

- Power: 5V Vcc (VIO 분리 없음 → 3.3V MCU 사용 시 일부 모듈 호환성 확인)
- Termination: 120Ω 양 끝
- TX/RX 신호 핀 매핑

## 참고: TI SPI 자료

(SPI는 이 프로젝트 범위 밖, 추후 확장 시 참조)
