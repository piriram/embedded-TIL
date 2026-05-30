# Wiring Notes

## 부품 (BOM)

| 부품 | 수량 | 비고 |
|------|------|------|
| STM32F103C8T6 BluePill | 1 | 알리 2~3천 원 |
| MPU6050 모듈 | 1 | GY-521 호환, 0x68 (AD0=GND) |
| TJA1050 CAN 트랜시버 모듈 | 1 또는 2 | loopback 또는 multi-node |
| USB-TTL 어댑터 (CP2102) | 1 | UART 로그용 |
| ST-Link V2 | 1 | 디버그/플래시 |
| 4.7kΩ 저항 | 2 | I2C SDA/SCL 풀업 |
| 120Ω 저항 | 2 | CAN 종단 |
| 브레드보드 + 점퍼선 | | |

## 배선 절차

1. **전원 먼저**: BluePill 3V3 → 브레드보드 전원 레일. GND 공통.
2. **I2C 풀업**: SDA·SCL 각각 4.7kΩ → 3.3V. **풀업 없으면 통신 안 됨**.
3. **MPU6050**: VCC=3V3, GND, SCL=PB6, SDA=PB7, AD0=GND.
4. **TJA1050**: VCC=5V (BluePill 5V 핀), GND, TXD=PB9, RXD=PB8.
5. **CAN 종단**: CAN_H ↔ CAN_L 사이 120Ω. 양 끝 노드에 각각.
6. **UART 어댑터**: USB-TTL RX ↔ BluePill PA9, GND 공통.
7. **ST-Link**: SWDIO=PA13, SWCLK=PA14, GND, 3V3 (전원 옵션).

## 사진

`hardware/wiring-photo-1.jpg`, `wiring-photo-2.jpg` 자리.

면접관 신뢰도 ↑ 위해 보드·풀업·트랜시버 분리해서 2~3장 권장.

## 트러블슈팅 메모

| 증상 | 원인 후보 | 확인 |
|------|---------|------|
| WHO_AM_I 응답 없음 | 풀업 누락 | 멀티미터로 SDA/SCL HIGH 확인 |
| WHO_AM_I = 0xFF | ADDR 클리어 미스 | SR1 → SR2 순서 확인 |
| CAN 송신 실패 | bus-off, 종단 없음 | 120Ω 확인, ESR/TEC 카운터 |
| UART 깨짐 | baud mismatch, GND | 양쪽 baud 확인, GND 공통 |
