# TI Precision Labs — CAN Protocol과 CAN FD

**주제:** Classical CAN frame, message identifier, 비파괴 arbitration, bit stuffing, frame 유형, CAN FD, 호환성과 system 영향
**강의:** TI Precision Labs — CAN Protocol and CAN FD
**선행 노트:** [CAN 물리 계층과 하드웨어](./1_CAN_물리계층과_하드웨어.md)

---

## 1. Protocol 동작의 물리적 전제

CAN protocol은 bus의 **dominant/recessive** 성질을 이용한다.

| Bus state | Logic | 특징 |
| --- | --- | --- |
| Recessive | 1 | 어떤 node도 dominant를 구동하지 않을 때의 bus 상태 |
| Dominant | 0 | driver가 bus를 능동 구동하며 recessive를 덮어씀 |

여러 node가 동시에 서로 다른 bit를 보내면 dominant `0`이 recessive `1`보다 우선한다. 각 node는 자신이 보낸 값과 실제 bus 값을 동시에 비교할 수 있으므로, 충돌로 winning message를 파괴하지 않고 arbitration을 수행한다.

---

## 2. Classical CAN data frame 구조

bus가 idle일 때는 recessive 상태를 유지한다. 송신 node가 dominant `SOF`를 보내면서 frame 전송을 시작한다.

```text
SOF
 → Arbitration field: Identifier + RTR
 → Control field: IDE + reserved + DLC
 → Data field
 → CRC sequence + CRC delimiter
 → ACK slot + ACK delimiter
 → EOF
 → Interframe space
```

### 2.1 SOF(Start of Frame)

- 길이: **1 bit**
- 값: 항상 **dominant 0**
- 역할: idle 상태였던 bus에서 전송 시작을 알리고 node들의 bit timing 동기화를 시작한다.

### 2.2 Identifier와 RTR

- **Standard identifier:** 11 bit
- **Extended identifier:** 29 bit
- identifier는 message의 priority를 결정하고 message 의미 또는 대상을 구분하는 데 사용될 수 있다.
- **값이 작을수록 priority가 높다.** 전부 dominant `0`인 ID가 가능한 최고 priority다.

identifier 바로 다음의 `RTR(Remote Transmission Request)` bit는 frame의 목적을 구분한다.

| RTR | 의미 |
| --- | --- |
| dominant `0` | Data frame |
| recessive `1` | Remote frame, 다른 node에 data 요청 |

### 2.3 Control field와 DLC

강의의 standard frame 예에서 control field는 6 bit다.

- **IDE(Identifier Extension):** dominant이면 11-bit standard ID, recessive이면 29-bit extended format을 나타낸다.
- **Reserved bit:** 향후 표준 확장을 위해 예약된 bit다.
- **DLC(Data Length Code) 4 bit:** data field의 byte 수를 나타낸다.

Classical CAN data frame의 payload는 **0~8 byte**다. Remote frame에는 data field가 없다. Data byte는 **MSB(Most Significant Bit) first**로 전송되고, 여러 byte는 순서대로 이어진다.

### 2.4 CRC

- Classical CAN 강의 예의 CRC sequence는 **15 bit**다.
- 송신 node는 앞서 전송한 bit들을 바탕으로 CRC를 계산한다.
- 수신 node가 계산한 CRC와 수신 CRC가 다르면 error condition이다.
- CRC sequence 뒤에는 recessive **CRC delimiter**가 온다.

### 2.5 ACK

`ACK slot`에서 송신 node는 recessive를 전송한다. Frame을 오류 없이 받은 수신 node는 이 자리를 dominant로 덮어써 수신 성공을 알린다.

```text
Transmitter: recessive(1)
Receiver:    dominant(0)  ← 정상 수신 시
Bus:         dominant(0)  ← ACK 확인
```

ACK slot 뒤에는 recessive ACK delimiter가 온다. 송신 node가 ACK를 확인하지 못하면 message는 다시 arbitration을 거쳐 재전송될 수 있다.

> **주의**
> ACK는 “application이 data 의미를 정상 처리했다”는 응답이 아니라, 수신 node가 CAN frame을 protocol 관점에서 오류 없이 받았다는 신호다.

### 2.6 EOF와 interframe space

- `EOF(End of Frame)`: **7개의 연속 recessive bit**
- EOF 뒤에는 다른 frame을 시작하기 전 interframe space가 필요하다.

> **주의 — 트랜스크립트 수치 교정**
> 강의 트랜스크립트에는 `7-bit interframe spacing`이라고 적혀 있지만, Classical CAN에서 고정된 7 recessive bit는 **EOF**다. 정상 data/remote frame 뒤의 최소 **Intermission은 3개의 recessive bit**이며, 그 뒤 bus idle이 이어진다.

---

## 3. ID 기반 비파괴 arbitration

여러 node가 idle bus에서 동시에 전송을 시작할 수 있다. 각 node는 자신의 ID bit를 보내는 동시에 실제 bus 상태를 읽는다.

- 자신이 dominant `0`을 보냈고 bus도 `0`이면 계속 전송한다.
- 자신이 recessive `1`을 보냈는데 bus에서 dominant `0`을 읽으면 더 높은 priority ID가 있음을 알 수 있다.
- 이 node는 즉시 전송을 중단하므로, winning frame의 bit는 손상되지 않는다.
- arbitration에서 진 node는 winning frame과 interframe space가 끝난 뒤 다시 전송을 시도한다.

### 두 node의 priority 예시

- Node A ID: `1199`
- Node B ID: `1530`
- `1199 < 1530`이므로 Node A의 priority가 더 높고 arbitration에서 이긴다.

### 세 node의 bit 단위 예시

```text
               비교 중인 한 bit
Node A:            0 dominant  ─┐
Node B:            1 recessive  ├─ Bus = 0 dominant
Node C:            0 dominant  ─┘

Node B: "1을 보냈는데 0을 읽음" → arbitration loss → 즉시 중단
```

강의 예에서는 Node B가 3번째 ID bit에서 먼저 탈락하고, Node C가 7번째 bit에서 탈락한다. Node A는 전체 identifier 동안 보낸 값과 bus 값이 일치하여 가장 낮은 binary ID로 arbitration을 이긴다.

> arbitration이 정확하려면 송신한 signal이 bus를 돌아 수신 경로로 들어오는 **loop time**과 cable의 **propagation delay**가 bit timing 안에 들어와야 한다. Cable 길이, node 수, isolation, loading이 증가하면 가능한 data rate가 낮아질 수 있다.

---

## 4. Bit stuffing

CAN은 frame 안에 같은 polarity가 지나치게 오래 이어지지 않도록 **bit stuffing**을 사용한다.

1. 같은 값이 **5 bit 연속** 나타나면,
2. 송신 node가 반대 polarity의 stuff bit 1개를 삽입하고,
3. 수신 node가 이를 자동으로 제거(destuffing)한다.

```text
원본:  1 1 1 1 1 1 ...
전송:  1 1 1 1 1 [0] 1 ...
                    ↑ stuff bit

원본:  0 0 0 0 0 0 ...
전송:  0 0 0 0 0 [1] 0 ...
                    ↑ stuff bit
```

stuff bit도 연속 bit 판정에 포함된다. 따라서 다섯 dominant bit 뒤에 삽입한 recessive stuff bit가 뒤의 네 recessive data bit와 연결되면, 다시 dominant stuff bit가 필요할 수 있다.

강의의 sample frame에서는 identifier의 마지막 bit부터 dominant가 6개 연속되므로, 5번째 dominant 뒤에 recessive stuff bit가 삽입된다.

- bit stuffing 적용 구간은 강의 기준 **SOF부터 CRC sequence의 마지막 bit까지**다.
- `CRC delimiter`, `ACK slot`, 각 delimiter, `EOF`처럼 고정 형식인 구간에는 적용하지 않는다.
- stuffing 적용 구간에서 stuff rule을 위반해 같은 bit가 6개 연속 관찰되면 error condition이 된다.
- destuffing 후의 logical data는 stuffing 전 원본과 같다.

---

## 5. 네 가지 CAN frame

### 5.1 Data frame

- 가장 일반적인 frame이다.
- Classical CAN에서는 최대 8 byte의 실제 정보를 전달한다.
- `RTR = dominant 0`이다.

### 5.2 Remote frame

- 다른 node에 특정 ID의 data 전송을 요청한다.
- `RTR = recessive 1`로 표시한다.
- data field가 없다.
- 요청 대상 node는 data frame으로 응답할 수 있다.

### 5.3 Error frame

송수신 중 protocol error를 감지한 node가 전송한다. 강의는 **error-active node**가 보내는 active error flag를 중심으로 설명한다.

- active error flag는 정상 stuffing rule을 의도적으로 깨는 **최소 6개의 연속 dominant bit**를 사용한다.
- bus의 다른 node도 error를 감지하여 error frame 전송에 참여한다.
- 기존 송신 node는 원래 message를 자동 재전송한다.
- CAN controller의 error counter가 반복 오류 node의 bus 점유를 제한한다.

> **예외**
> 모든 error frame이 항상 dominant 6 bit인 것은 아니다. 강의의 설명은 error-active 상태의 active error flag를 단순화한 것이다. Error-passive node는 bus를 강제로 지배하지 않는 passive error flag를 사용한다.

### 5.4 Overload frame

- 형식은 error frame과 비슷하지만 frame 전송 도중이 아니라 **frame 사이 또는 interframe space**에서 발생한다.
- 처리할 시간이 더 필요한 node가 다음 message까지 추가 지연을 만들기 위해 사용한다.

---

## 6. CAN FD의 확장 방식과 장점

**CAN FD(CAN with Flexible Data Rate)** 는 Classical CAN frame을 확장하여 payload와 usable bandwidth를 늘린 protocol이다.

### 한 frame 안에서 data rate 변경

CAN FD는 arbitration 등 일부 구간은 기존 CAN 속도로 전송하고, **data field와 CRC 구간은 더 높은 data rate**로 전송할 수 있다.

```text
Arbitration 구간     Data + CRC 구간       나머지 구간
기존 CAN 속도   →    더 빠른 속도     →    protocol에 맞는 속도
```

강의 기준 CAN FD의 usable bandwidth는 최대 **5 Mbit/s**다. 같은 양의 data를 더 짧은 시간에 보내거나, 같은 시간 동안 더 많은 data를 보낼 수 있다.

### 주요 장점

- 한 frame의 payload가 Classical CAN의 8 byte에서 **최대 64 byte**로 증가한다.
- 기존 network를 FlexRay나 Ethernet으로 전면 교체하는 것보다 작은 추가 비용과 복잡도로 bandwidth를 늘릴 수 있다.
- module과 ECU의 end-of-line flash programming 시간을 줄여 제조 비용 절감에 도움을 준다.

### 호환성

- **CAN FD controller → Classical CAN frame:** 지원 가능하므로 backward compatible이다.
- **Classical CAN controller → CAN FD frame:** 해석할 수 없으므로 forward compatible하지 않다.

> **주의**
> “CAN FD가 backward compatible”하다는 말은 CAN FD controller가 Classical CAN 통신을 할 수 있다는 뜻이다. Classical CAN node가 CAN FD frame까지 그대로 수신할 수 있다는 뜻은 아니다.

---

## 7. CAN FD 도입 시 바뀌는 구성 요소

CAN FD를 도입할 때는 protocol engine부터 application까지 영향을 확인해야 한다.

| 구성 요소 | 확인할 변경점 |
| --- | --- |
| MCU의 CAN controller | CAN FD frame format과 더 긴 payload를 지원하는 controller 필요 |
| CAN transceiver | 1 Mbit/s 이하만 사용하면 기존 요구사항을 만족하는 transceiver를 재사용할 수 있음. 1 Mbit/s 초과 시 성능 재검토 |
| Cable·connector·protection | 1 Mbit/s 이하에서는 기존 CAN 부품 재사용 가능. 더 빠르면 signal integrity와 hardware 변경 가능성 검토 |
| Low-level driver | 새 controller register map과 최대 64-byte payload 처리에 맞게 수정 |
| Application software | 더 긴 data payload와 새로운 message 구성을 처리하도록 수정 |

CAN FD도 cable이 길어지고 node 수, isolation, loading이 증가하면 가능한 최고 data rate가 낮아진다. **1 Mbit/s를 넘는 CAN FD**를 사용할 때는 controller만 교체하면 된다고 가정하지 말고 physical layer와 hardware design을 함께 검증해야 한다.

---

## 8. 한 번에 연결해서 기억하기

```text
bus idle은 recessive
→ dominant SOF로 frame 시작
→ ID가 낮을수록 arbitration priority가 높음
→ Control/DLC 뒤에 data 전송
→ CRC로 오류 검출, ACK로 frame 수신 확인
→ EOF 뒤 interframe space 후 다음 frame 가능
→ 5개의 같은 bit 뒤 opposite stuff bit 삽입
→ CAN FD는 data/CRC 구간을 빠르게 하고 payload를 64 byte로 확장
```

### 이해 점검 질문

- CAN ID의 숫자가 작을수록 priority가 높은 이유는 무엇인가?
- 송신 node가 recessive를 보냈는데 dominant를 읽으면 어떻게 동작하는가?
- ACK는 application-level 응답과 무엇이 다른가?
- bit stuffing은 어느 구간에 적용되는가?
- Data, Remote, Error, Overload frame은 각각 언제 사용되는가?
- CAN FD controller와 Classical CAN controller의 호환성은 어느 방향으로 성립하는가?
- 1 Mbit/s를 넘는 CAN FD에서 physical layer를 다시 검토해야 하는 이유는 무엇인가?

---

## 참고 자료

- [TI CAN & CAN FD technical resources](https://www.ti.com/CAN)
- **ISO 11898 series** — CAN data link layer 및 physical layer 표준
- 선행 노트: [CAN 물리 계층과 하드웨어](./1_CAN_물리계층과_하드웨어.md)
- 관련 프로젝트 자료: [STM32F103·CAN 2.0A·TJA1050 데이터시트 노트](../../../30_프로젝트/docs/datasheet-notes.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** CAN protocol은 dominant 0이 recessive 1을 덮어쓰는 bus 특성을 이용해 낮은 message ID에 우선권을 주고, frame 단위로 data와 오류 정보를 전달한다.
- **왜 필요:** 여러 ECU가 하나의 bus를 공유할 때 충돌로 message를 손상시키지 않고 real-time priority에 따라 통신하며 오류를 검출하기 위해 필요하다.
- **동작:** Frame은 SOF, ID/RTR, control/DLC, data, CRC, ACK, EOF 순서다. 여러 node가 동시에 전송하면 recessive를 보냈지만 dominant를 읽은 node가 중단하여 가장 낮은 ID가 arbitration을 이긴다.
- **비교:** Classical CAN은 최대 1 Mbit/s와 frame당 8 byte를 지원하고, CAN FD는 data·CRC 구간의 속도를 높여 강의 기준 최대 5 Mbit/s와 frame당 64 byte까지 지원한다.
- **30초 통합 답변:**
  > CAN frame은 dominant SOF로 시작해 ID와 RTR, control과 DLC, 최대 8 byte data, CRC, ACK, EOF 순서로 전송됩니다. 여러 node가 동시에 송신하면 dominant 0이 recessive 1을 덮어쓰므로, recessive를 보냈지만 dominant를 읽은 node가 전송을 멈추고 가장 낮은 message ID가 비파괴 arbitration을 이깁니다. CRC와 bit stuffing으로 오류를 감지하고 ACK slot에서 frame 수신을 확인합니다. CAN FD는 data와 CRC 구간을 더 빠르게 전송하고 payload를 최대 64 byte로 늘린 확장 방식입니다.
