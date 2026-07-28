# TI Precision Labs — CAN 물리 계층과 하드웨어

**주제:** 자동차 CAN network, CAN controller와 transceiver, differential bus, topology, termination, dominant/recessive, ISO 11898
**강의:** TI Precision Labs — Introduction to CAN Communication

---

## 1. CAN이 필요한 이유

**CAN(Controller Area Network)** 은 여러 전자 제어 장치가 하나의 공통 bus를 통해 message를 주고받는 비동기 직렬 통신 방식이다. 자동차에서는 중앙 body controller, power seat, door module, climate control unit, brake 관련 장치처럼 서로 멀리 떨어진 module들이 CAN bus를 공유한다.

예를 들어 climate control system이 power seat system에 seat heater 작동을 요청하거나, brake pedal 입력을 받은 control unit이 brake light를 켜도록 다른 module과 정보를 공유할 수 있다. 주변의 더 단순하고 낮은 속도의 장치는 LIN sub-bus로 확장할 수 있다.

CAN을 사용하는 핵심 이유는 **배선 절감**이다.

- 장치를 각각 point-to-point로 연결하면 배선 수와 무게가 크게 증가한다.
- 자동차 배선은 비싸고 무거우며 수작업 조립 비중도 높다.
- 여러 node가 하나의 bus를 공유하면 제조 비용과 차량 무게를 줄일 수 있다.
- 무게 감소는 연료 효율 개선에도 도움이 된다.

> CAN은 장치마다 일대일 배선을 연결하는 구조가 아니라, 여러 node가 같은 bus에서 **message identifier(ID)** 를 기준으로 정보를 공유하는 구조다.

### Classical CAN, CAN FD, LIN 비교

| 구분 | Classical CAN | CAN FD | LIN |
| --- | --- | --- | --- |
| 역할 | 자동차의 주요 shared bus | Classical CAN의 bandwidth 확장 | 저속 peripheral용 sub-bus |
| 배선 | differential 2-wire | differential 2-wire | 강의에서는 세부 물리 계층 생략 |
| 강의 기준 속도 | 최대 1 Mbit/s | 최대 5 Mbit/s | CAN보다 낮은 속도 |
| 한 frame의 data | 최대 8 byte | 최대 64 byte | 강의 범위 밖 |

---

## 2. CAN 표준이 다루는 범위

CAN 표준은 multipoint bus에서 사용하는 **asynchronous serial communication의 protocol과 physical layer**를 정의한다.

- **Protocol:** frame 형식, ID 기반 arbitration, CRC, ACK, error 처리 등을 규정한다.
- **Physical layer:** controller의 logic 신호를 `CANH`와 `CANL`의 differential voltage로 전달하는 방법과 전기적 요구사항을 규정한다.

각 CAN node는 크게 두 부분으로 구성된다.

```text
Application / MCU
       ↓
CAN controller(protocol engine)
       ↓ TXD / ↑ RXD
CAN transceiver
       ↓
CANH ───────── shared bus ───────── CANH
CANL ───────── shared bus ───────── CANL
```

- **CAN controller:** frame 생성·해석, ID arbitration, CRC, ACK, error counter 등 protocol 처리를 담당한다. 보통 MCU 내부에 있다.
- **CAN transceiver:** controller의 logic 신호를 `CANH`와 `CANL`의 differential electrical signal로 변환하고, bus 신호를 다시 logic 신호로 전달한다.

> MCU의 CAN controller와 외부 CAN transceiver는 같은 부품이 아니다. Controller는 protocol을 처리하고, transceiver는 실제 bus의 전기 신호를 구동하고 수신한다.

---

## 3. Network topology와 배선

CAN은 여러 node가 참여하는 **multipoint bus** 다. 물리 배선은 다음 원칙을 따른다.

- `CANH`와 `CANL`을 **twisted pair cable** 로 배선한다.
- 양 끝이 분명한 **bus topology** 로 구성한다.
- main bus에서 node까지 뻗는 **stub는 가능한 짧게** 만든다.
- bus 양 끝에는 network characteristic impedance와 일치하는 termination을 둔다.

```text
120 Ω                                      120 Ω
  │                                           │
CANH ─────┬──────────┬──────────┬──────────── CANH
CANL ─────┴──────────┴──────────┴──────────── CANL
          │          │          │
        Node A     Node B     Node C
        짧은 stub  짧은 stub  짧은 stub
```

stub가 길거나 star처럼 branch가 많아지면 propagation delay와 reflection이 커진다. 특히 data rate가 높을수록 signal integrity와 arbitration margin이 나빠질 수 있다.

---

## 4. 종단 저항과 signal integrity

CAN twisted pair의 characteristic impedance는 보통 **120 Ω** 이다. 따라서 bus의 **양 끝에 각각 120 Ω termination** 을 배치한다.

```text
             CAN bus
CANH ──┬──────────────────────────┬── CANH
       │                          │
      120 Ω                      120 Ω
       │                          │
CANL ──┴──────────────────────────┴── CANL
        bus의 한쪽 끝              bus의 반대쪽 끝
```

termination은 전송파가 cable 끝에서 반사되는 것을 줄여 waveform을 안정화한다. node를 탈착할 수 있는 network라면 node 제거와 함께 bus 끝의 termination까지 사라지지 않도록 배치 위치를 신중하게 정해야 한다.

### Standard termination

- bus 양 끝에서 `CANH`와 `CANL` 사이에 각각 하나의 120 Ω resistor를 둔다.
- 가장 단순한 구성이다.

### Split termination

하나의 120 Ω을 두 개의 저항으로 나누고 중앙점을 capacitor 등을 통해 안정화하는 방식이다.

- signal integrity와 electromagnetic emission 특성을 개선할 수 있다.
- bus의 common-mode voltage 변동을 줄이는 데 도움이 된다.
- differential signal 변화는 유지하면서 common-mode noise를 억제한다.

> **주의**
> termination resistor의 정격 전력은 정상 통신만 보고 정하면 안 된다. `CANH` 또는 `CANL`이 `VCC`나 ground에 short될 수 있으므로, network transceiver의 short-circuit overcurrent protection 조건까지 고려해야 한다.

---

## 5. Differential signal과 dominant/recessive

CAN은 두 선의 절대 전압보다 두 선 사이의 차이를 이용한다.

```text
VD = VCANH - VCANL
```

| Bus state | Logic | Differential voltage `VD` | 구동 방식 |
| --- | --- | --- | --- |
| **Recessive** | 1 | 낮음 | 어떤 node도 dominant를 구동하지 않을 때 termination을 통해 수동 복귀 |
| **Dominant** | 0 | 높음 | driver가 bus를 능동적으로 구동 |

여러 node가 동시에 서로 다른 값을 내보내면 **dominant(0)가 recessive(1)를 덮어쓴다.** 즉 CAN bus는 wired-AND와 유사하게 동작한다.

```text
Node A: recessive(1)
Node B: dominant(0)
Bus:    dominant(0)
```

driver는 bus를 dominant 상태로 능동 구동할 수 있다. 반대로 어떤 driver도 dominant를 구동하지 않으면 bus는 termination resistor를 통한 에너지 소산으로 recessive 상태에 수동 복귀한다.

이 전기적 성질 덕분에 node는 전송 중 bus를 관찰하여 data를 파괴하지 않고 priority arbitration을 수행할 수 있다. Arbitration의 상세 동작은 [CAN protocol과 CAN FD](./2_CAN_프로토콜과_CAN_FD.md)에서 다룬다.

---

## 6. ISO 11898과 CAN 명칭

자동차 CAN interface는 **ISO 11898** 계열 표준을 따른다. 강의에서 다룬 part는 다음과 같다.

| 표준 | 강의에서 설명한 범위 |
| --- | --- |
| `ISO 11898-2` | High-speed CAN physical layer |
| `ISO 11898-3` | Low-speed fault-tolerant CAN(LSFT CAN), 최대 125 kbit/s |
| `ISO 11898-5` | Part 2에 low-power mode 요구사항 추가 |
| `ISO 11898-6` | Selective wake-up을 위한 partial networking 요구사항 |

자동차 제조사가 말하는 low speed, medium speed, high speed는 **제조사 내부 data-rate 구분**일 수 있다. ISO 표준의 `LSFT CAN`, `HS CAN` 명칭과 비슷하지만 뜻이 항상 같지는 않다.

- 제조사가 low/medium/high speed라고 부르는 network도 실제 physical layer는 `ISO 11898-2` 계열 **HS CAN** 일 수 있다.
- HS CAN의 동작 범위는 LSFT CAN의 속도 범위와 겹친다.
- CAN transceiver의 저속 한계는 강의 기준 약 **10~40 kbit/s**이며, `TXD/RXD timeout` 조건의 영향을 받는다.

ISO 11898 위에는 항공, 농업, embedded control, industrial automation, military, marine, safety-critical 분야별 higher-layer protocol과 별도의 EMC·ESD 시험 표준이 추가될 수 있다.

---

## 7. 한 번에 연결해서 기억하기

```text
자동차 배선 비용과 무게를 줄여야 함
→ 여러 node가 하나의 CAN bus를 공유
→ MCU의 controller는 protocol, transceiver는 전기 신호 담당
→ CANH/CANL twisted pair와 짧은 stub로 배선
→ 양 끝 120 Ω termination으로 reflection 억제
→ dominant(0)가 recessive(1)를 덮어쓰는 differential bus 형성
→ 이 물리적 성질을 protocol의 arbitration에 활용
```

### 이해 점검 질문

- CAN controller와 CAN transceiver는 각각 무엇을 담당하는가?
- twisted pair와 differential signaling을 사용하는 이유는 무엇인가?
- 왜 CAN bus 양 끝에 각각 120 Ω termination을 두는가?
- standard termination과 split termination은 무엇이 다른가?
- dominant `0`과 recessive `1`이 동시에 구동되면 bus는 어떤 상태가 되는가?
- 제조사의 low-speed CAN이라는 이름만 보고 ISO 11898-3이라고 단정하면 안 되는 이유는 무엇인가?

---

## 참고 자료

- [TI CAN & CAN FD technical resources](https://www.ti.com/CAN)
- **ISO 11898 series** — CAN data link layer 및 physical layer 표준
- **ISO 11898-2** — High-speed CAN physical layer
- **ISO 11898-3** — Low-speed fault-tolerant CAN
- **ISO 11898-5** — High-speed CAN low-power mode
- **ISO 11898-6** — High-speed CAN selective wake-up / partial networking
- 관련 프로젝트 자료: [STM32F103·CAN 2.0A·TJA1050 데이터시트 노트](../../../30_프로젝트/docs/datasheet-notes.md)
- 다음 강의: [CAN protocol과 CAN FD](./2_CAN_프로토콜과_CAN_FD.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** CAN은 여러 ECU가 `CANH/CANL` differential 2-wire bus를 공유하는 자동차용 serial network다.
- **왜 필요:** 자동차 module을 point-to-point로 모두 연결하면 배선 비용과 무게가 커지므로, 하나의 shared bus로 배선을 줄이면서 멀리 떨어진 장치끼리 통신하기 위해 사용한다.
- **동작:** MCU 내부 CAN controller가 frame과 protocol을 처리하고 transceiver가 logic 신호를 CANH/CANL 전압으로 변환한다. Bus는 twisted pair로 구성하고 양 끝을 각각 120 Ω으로 종단하며, dominant 0이 recessive 1을 덮어쓴다.
- **비교:** Standard termination은 양 끝에 120 Ω 하나씩을 사용하고, split termination은 저항을 나눠 common-mode voltage 변동과 electromagnetic emission을 줄이는 데 도움을 준다.
- **30초 통합 답변:**
  > CAN은 여러 ECU가 CANH와 CANL의 differential 2-wire bus를 공유하는 자동차용 통신 방식입니다. Point-to-point 방식보다 배선 비용과 무게를 줄일 수 있습니다. MCU 내부 CAN controller는 frame과 arbitration 같은 protocol을 처리하고, transceiver는 logic 신호를 실제 bus 전압으로 변환합니다. CANH와 CANL은 twisted pair로 배선하고 reflection을 줄이기 위해 bus 양 끝에 각각 120 Ω 종단 저항을 둡니다. Bus에서는 dominant 0이 recessive 1을 덮어쓰며, 이 성질이 ID arbitration의 기반이 됩니다.
