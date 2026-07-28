# Validation Evidence

이 폴더는 펌웨어가 **실제로 동작했다는 증거**를 모읍니다. README 메인에서 "검증 가능한 형태로 확인"을 주장하려면 이 폴더가 채워져야 합니다.

## 채울 항목

- [ ] `uart-log.md` — WHO_AM_I 응답값, 가속도 raw 출력 캡처 (5~15줄 인용)
- [ ] `logic-i2c.png` — 로직 분석기 I2C START / ACK / STOP 시퀀스 (Saleae 또는 nRF Connect)
- [ ] `logic-can.png` — CAN 메시지 ID + payload 캡처
- [ ] `can-trace.md` — candump 또는 PCAN 로그 텍스트
- [ ] `failure-cases.md` — 재현 조건 표 (NACK / bus busy / 센서 전원 불안정 / 클럭 설정 오류 / TRISE 미설정)
- [ ] `oscilloscope-sda-scl.png` — SDA/SCL rise time (선택, 풀업 검증용)

## 캡처 가이드

### UART 로그
- CoolTerm 또는 PuTTY, 115200 8N1
- 보드 부팅부터 1분 이내 캡처
- 정상 응답 + 의도적 실패 (예: 센서 분리) 두 케이스

### 로직 분석기
- 채널 2개 = SCL + SDA
- 샘플링 ≥ 4 MS/s (100 kHz I2C 기준)
- I2C 디코더 활성화 → START, addr+W, ACK, register, repeated START, addr+R, ACK, data, NACK, STOP 확인
- 9번째 클럭 ACK 위치 확인

### CAN 트레이스
- candump (`socketcan` 환경) 또는 PCAN-View
- 송신 ID + DLC + payload + 주기 확인
- 가능하면 bus load 측정

## 재현 조건 표 템플릿

| 케이스 | 입력 조건 | 기대 결과 | 실제 결과 | 비고 |
|--------|---------|---------|---------|------|
| 정상 read | 센서 정상 연결, 4.7kΩ 풀업 | WHO_AM_I = 0x68 | (캡처 첨부) | |
| NACK | 잘못된 주소 (0x69) | 함수 timeout 후 error | | |
| bus busy | START 전 BUSY 1 | timeout | | |
| 클럭 오류 | CR2.FREQ = 16 (잘못) | 통신 불안정 | | TRISE 함정 함께 |
| 풀업 누락 | 외부 풀업 제거 | SCL/SDA LOW에 갇힘 | | 회로 사진 |
