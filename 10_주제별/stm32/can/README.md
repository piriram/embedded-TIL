# STM32 CAN 학습노트

TI Precision Labs와 STM32 프로젝트 자료를 바탕으로 CAN의 물리 계층부터 protocol과 CAN FD까지 학습한다.

## 진도표

| 번호 | 제목 | 핵심 키워드 | 원본 | 상태 |
| --- | --- | --- | --- | --- |
| 1 | [CAN 물리 계층과 하드웨어](./1_CAN_물리계층과_하드웨어.md) | controller, transceiver, differential bus, topology, 120 Ω, ISO 11898 | TI Precision Labs — Introduction to CAN Communication | 완료 |
| 2 | [CAN Protocol과 CAN FD](./2_CAN_프로토콜과_CAN_FD.md) | frame, arbitration, CRC, ACK, bit stuffing, CAN FD | TI Precision Labs — CAN Protocol and CAN FD | 완료 |

## 학습 흐름

1. 1강: 자동차에서 shared bus가 필요한 이유
2. 1강: CAN controller와 transceiver의 역할
3. 1강: `CANH/CANL`, twisted pair, 120 Ω termination
4. 1강: dominant/recessive와 ISO 11898 physical layer
5. 2강: Classical CAN frame과 ID arbitration
6. 2강: CRC, ACK, bit stuffing과 네 가지 frame
7. 2강: CAN FD의 data rate, payload, 호환성과 hardware 영향

## 파일명 규칙

- `N_제목.md`
- 원리 노트를 먼저 만들고, MCU 구현 노트는 이후 번호로 추가한다.

## 관련 폴더

- [STM32 주제별 노트](../)
- [프로젝트 데이터시트 노트](../../../30_프로젝트/docs/datasheet-notes.md)
- [포트폴리오 시작 전 필기노트](../../../00_필기노트/10_포폴시작전/)
