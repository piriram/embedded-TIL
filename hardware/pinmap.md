# Pin Map

STM32F103C8T6 (BluePill) 핀 할당.

## 사용 핀

| 핀 | 기능 | 모드 | 연결 |
|----|------|------|------|
| PA9 | USART1 TX | AF Push-Pull | USB-TTL 어댑터 RX |
| PA10 | USART1 RX | Input (선택) | USB-TTL 어댑터 TX (옵션) |
| PB6 | I2C1 SCL | AF Open-Drain | MPU6050 SCL + 4.7kΩ → 3.3V |
| PB7 | I2C1 SDA | AF Open-Drain | MPU6050 SDA + 4.7kΩ → 3.3V |
| PB8 | CAN RX | Input + AF remap | TJA1050 RXD |
| PB9 | CAN TX | AF Push-Pull + remap | TJA1050 TXD |
| PC13 | LED (내장) | Output Push-Pull | BluePill 내장 LED (Low active) |

## 클럭 / 디버거

| 핀 | 용도 |
|----|------|
| PA13 | SWDIO (ST-Link) |
| PA14 | SWCLK (ST-Link) |
| OSC_IN | HSE 8 MHz crystal (BluePill 보드 내장) |

## 전원

| 핀 | 전압 |
|----|------|
| 3V3 | MPU6050 VCC, I2C 풀업 |
| 5V | TJA1050 VCC |
| GND | 공통 그라운드 (USB-TTL, 센서, 트랜시버 다 연결) |

## AFIO Remap

bxCAN 기본 핀 = PA11/PA12. 본 프로젝트는 USB 충돌 회피 위해 **PB8/PB9로 remap** 사용 → `AFIO_MAPR` `CAN_REMAP[1:0] = 10`.

## 주의

- BluePill 보드에 따라 USB 신호선이 PA11/PA12에 연결돼 있으므로 CAN 기본 매핑과 충돌. 반드시 PB8/PB9 remap.
- I2C 외부 풀업 필수. 보드 내부 풀업만으로는 100 kHz도 불안정.
- TJA1050은 5V 전원 필요. BluePill 5V 핀 사용. 신호선 3.3V/5V 호환성은 모듈 데이터시트 확인.
