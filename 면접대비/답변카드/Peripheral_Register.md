# Peripheral Register

> 파생 학습노트: `cs/임베디드수업/8_MCU_메모리맵과_MMIO.md`
> 최종 갱신: 2026-05-20

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

Peripheral Register는 GPIO, UART, Timer 같은 주변장치를 제어하거나 상태를 읽기 위해 MCU 주소 공간에 배치된 하드웨어 레지스터입니다. MMIO 방식에서는 이 레지스터들이 일반 메모리 주소처럼 보이지만, 실제 RAM이 아니라 하드웨어 회로에 연결된 제어 지점입니다. 각 peripheral은 고유한 Base Address를 가지고, 내부 레지스터들은 그 기준 주소에서 Offset만큼 떨어진 위치에 배치됩니다. 예를 들어 USART의 Status Register는 수신 준비, 송신 가능 여부, 에러 상태를 알려주고, Data Register는 읽으면 수신 데이터를 가져오고 쓰면 송신 데이터를 내보냅니다. 따라서 Peripheral Register는 “값을 저장하는 변수”라기보다 “하드웨어를 제어하고 상태를 관찰하는 주소화된 인터페이스”라고 말하는 것이 정확합니다.

---

## 한 줄 정의

**Peripheral Register는 MCU 주변장치의 설정, 상태 확인, 데이터 입출력을 위해 메모리 주소에 매핑된 하드웨어 레지스터다.**

핵심은 **RAM처럼 주소로 접근하지만 실제로는 주변장치 하드웨어에 연결되어 있다**는 점입니다.

---

## 왜 필요한가

CPU가 GPIO, USART, Timer, ADC 같은 주변장치를 직접 “객체”처럼 인식하는 것이 아니기 때문에, 주변장치를 제어할 수 있는 표준화된 접점이 필요합니다.

Peripheral Register는 그 접점 역할을 합니다. CPU는 특정 주소에 read/write 요청을 보내고, MCU 내부 버스와 주소 디코더가 그 요청을 해당 주변장치 레지스터로 연결합니다. 즉, 소프트웨어는 주소 접근만으로 하드웨어 설정 변경, 상태 확인, 데이터 송수신을 할 수 있습니다.

---

## 동작 원리

Peripheral마다 시작 주소인 **Base Address**가 정해져 있고, 그 안의 각 register는 base에서 일정한 **Offset**만큼 떨어진 위치에 배치됩니다.

```text
특정 Peripheral Register 주소 = Base Address + Offset
```

예를 들어 어떤 USART의 Base Address가 정해져 있다면, Status Register, Data Register, Control Register는 각각 base에서 몇 바이트 떨어진 위치에 놓입니다. 노트에서는 32비트 레지스터 기준으로 register 하나가 4바이트이기 때문에 offset이 `0, 4, 8, 12, ...`처럼 4의 배수로 증가한다고 설명합니다.

---

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** GPIO 핀 방향 설정, 핀 출력 값 변경, 버튼 입력 읽기, USART 송수신, Timer 설정, ADC 상태 확인처럼 주변장치를 직접 제어할 때 사용합니다.
- **주의할 경우:** 데이터시트나 레퍼런스 매뉴얼에 정의되지 않은 주소, reserved bit, 실제 register가 없는 unassigned address는 함부로 접근하면 안 됩니다. 노트에 따르면 실제 register가 없는 주소에 접근하면 유효한 값을 얻지 못할 뿐 아니라 Hard Fault가 발생할 수 있습니다.

---

## 대표 예시

### USART Register

| Register | 역할 |
|----------|------|
| `USART_SR` | Status Register. USART 내부 상태를 알려준다. |
| `USART_DR` | Data Register. 읽으면 수신 데이터를 가져오고, 쓰면 송신 데이터를 내보낸다. |

`USART_SR`은 수신된 바이트가 준비되었는지, 송신용 공간이 있는지, 에러가 발생했는지 같은 상태를 알려줍니다. `USART_DR`은 읽기와 쓰기의 의미가 다릅니다. 읽으면 receive line에 들어온 문자를 가져오고, 쓰면 transmit line으로 데이터를 내보냅니다.

### GPIO Register

GPIO Port A의 시작 주소는 노트에서 `0x40020000`으로 설명됩니다. GPIO register에는 핀 매핑, pull-up / pull-down 같은 전기적 설정, 실제 GPIO 핀 값 읽기/쓰기용 register가 포함됩니다.

---

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| **RAM Cell** | 값을 저장하고 나중에 같은 값을 다시 읽기 위한 메모리 공간이다. |
| **Peripheral Register** | 값을 저장하기 위한 일반 메모리가 아니라, 주변장치 제어와 상태 확인을 위한 하드웨어 접점이다. |
| **Memory Map** | MCU 전체 주소 공간에서 Flash, SRAM, Peripheral 영역이 어디에 있는지 보여준다. |
| **Register Map** | 특정 peripheral 내부의 register들이 base address 기준 어떤 offset에 있는지 보여준다. |

노트에서는 register map을 “메모리 맵의 미니 버전”처럼 보면 된다고 설명합니다.

---

## 꼬리질문 예상

- **Q:** Peripheral Register는 RAM인가요?
  **A:** 아니다. 메모리 주소처럼 접근하지만 실제 RAM이 아니라 UART, GPIO, Timer 같은 하드웨어에 연결된 레지스터다.

- **Q:** Peripheral Register 주소는 어떻게 계산하나요?
  **A:** `Base Address + Offset`으로 계산한다. Peripheral마다 시작 주소가 있고, 내부 register는 그 기준에서 일정한 offset만큼 떨어져 있다.

- **Q:** 왜 offset이 보통 4의 배수인가요?
  **A:** 노트 기준으로 register가 32비트, 즉 4바이트라고 가정하기 때문이다. 그래서 다음 register가 `0, 4, 8, 12, ...`처럼 4바이트 간격으로 배치된다.

- **Q:** `USART_DR`은 읽기와 쓰기가 같은 의미인가요?
  **A:** 아니다. 읽으면 수신된 문자를 가져오고, 쓰면 송신 라인으로 데이터를 내보낸다. 같은 register 주소라도 read와 write의 하드웨어 의미가 다를 수 있다.

- **Q:** Peripheral Register를 C 구조체로 표현할 수 있는 이유는 무엇인가요?
  **A:** register들이 base address 기준으로 일정한 offset에 순서대로 배치되기 때문이다. 노트에서는 이 구조가 C 배열이나 구조체처럼 보이며, 실제 코딩에서도 register 묶음을 C 배열 또는 구조체로 모델링한다고 설명한다.

- **Q:** 실제 register가 없는 주소를 읽으면 어떻게 되나요?
  **A:** 단순히 0이 나온다고 단정하면 안 된다. 노트에 따르면 unassigned address에 접근하면 유효한 값을 얻지 못할 뿐 아니라 Hard Fault가 발생할 수 있다.

---

## 자주 하는 오해

- **오해:** Peripheral Register는 일반 변수처럼 값을 저장하는 공간이다.
  - **정확히는:** 일부 값이 유지될 수는 있지만, 본질은 주변장치 제어와 상태 확인을 위한 하드웨어 인터페이스다.

- **오해:** Peripheral Register 주소는 개발자가 코드에서 정한다.
  - **정확히는:** 주소는 MCU 제조사가 하드웨어 설계와 문서에서 정해 둔다. 개발자는 데이터시트나 레퍼런스 매뉴얼의 주소를 보고 사용한다.

- **오해:** 메모리 주소처럼 접근하므로 실제 메모리다.
  - **정확히는:** MMIO에서는 주소라는 형태만 메모리처럼 보일 뿐, 해당 주소는 GPIO나 USART 같은 하드웨어 회로에 연결된다.

- **오해:** Reserved bit나 빈 주소를 읽고 써도 안전하다.
  - **정확히는:** 문서에 정의되지 않은 bit나 address는 접근하지 않는 것이 원칙이며, unassigned address 접근은 Hard Fault를 유발할 수 있다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-------------|
| 장치 안의 변수 | Peripheral Register |
| 장치 주소 | Peripheral Register Address |
| 시작 주소 | Base Address |
| 떨어진 위치 | Offset |
| 레지스터 목록 | Register Map |
| 상태 보는 레지스터 | Status Register |
| 데이터 주고받는 레지스터 | Data Register |
| 설정용 레지스터 | Control Register |
| 쓰면 안 되는 비트 | Reserved Bit |
| 실제 레지스터가 없는 주소 | Unassigned Address |

---

## 키워드

`Peripheral Register` `MMIO` `Base Address` `Offset` `Register Map` `Status Register` `Data Register` `Control Register` `Reserved Bit` `Hard Fault`
