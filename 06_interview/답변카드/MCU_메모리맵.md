# MCU 메모리맵

> 파생 학습노트: `10_주제별/cs/임베디드수업/8_MCU_메모리맵과_MMIO.md`
> 최종 갱신: 2026-05-20

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

MCU 메모리맵은 CPU가 접근할 수 있는 전체 주소 공간을 Flash, SRAM, System Memory, Peripheral Register 같은 영역으로 나눠 배치한 주소표입니다. 이 노트의 STM32 예시에서는 32비트 주소를 사용하므로 전체 주소 공간은 `2^32`바이트, 즉 4GB이고 주소 범위는 `0x00000000`부터 `0xFFFFFFFF`까지입니다. 대표적으로 Flash는 `0x08000000`, SRAM은 `0x20000000`, Peripheral Register 영역은 `0x40000000` 부근에 배치됩니다. Peripheral 하나가 실제로는 몇십 바이트의 레지스터만 써도 1024바이트 같은 큰 블록을 할당받을 수 있는데, 4GB 주소 공간이 넉넉하고 하드웨어 설계상 큰 구간 단위로 나누는 편이 쉽기 때문입니다. 다만 그 블록 안에 실제 레지스터가 없는 주소를 접근하면 유효한 값을 얻지 못하거나 Hard Fault가 발생할 수 있으므로, 반드시 데이터시트와 레퍼런스 매뉴얼의 메모리맵을 기준으로 접근해야 합니다.

---

## 한 줄 정의

**MCU 메모리맵은 MCU의 전체 주소 공간에서 Flash, SRAM, System Memory, Peripheral Register가 각각 어느 주소 범위에 배치되는지 나타낸 하드웨어 주소표다.**

핵심은 **주소값이 단순 숫자가 아니라, 하드웨어 안의 실제 연결 대상을 결정한다**는 점입니다.

---

## 왜 필요한가

CPU는 기본적으로 “어떤 주소에서 읽어라” 또는 “어떤 주소에 써라”는 요청만 내보냅니다.

하지만 MCU 내부에는 프로그램 코드가 들어 있는 Flash, 실행 중 데이터가 들어가는 SRAM, 제조사 내장 부트로더가 들어갈 수 있는 System Memory, GPIO·USART·SPI·ADC 같은 Peripheral Register가 함께 존재합니다.

따라서 주소 공간 안에서 어느 범위를 Flash로 볼지, 어느 범위를 SRAM으로 볼지, 어느 범위를 주변장치 레지스터로 볼지 정해 둔 표가 필요합니다. 이것이 MCU 메모리맵입니다.

---

## 동작 원리

이 노트의 STM32 예시에서는 MCU가 **32비트 주소**를 사용합니다.

계산은 다음과 같습니다.

```text
32비트 주소 공간 크기 = 2^32 bytes
                     = 4,294,967,296 bytes
                     = 4GB
```

따라서 주소 범위는 다음과 같습니다.

```text
최소 주소: 0x00000000
최대 주소: 0xFFFFFFFF
```

이 4GB 주소 공간 안에 Flash, System Memory, SRAM, Peripheral Register 영역이 나뉘어 배치됩니다. CPU가 특정 주소에 접근하면, MCU 내부 주소 디코더가 그 주소 범위를 보고 실제 요청 대상을 결정합니다.

---

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** Bare-metal firmware에서 Flash, SRAM, Peripheral Register, interrupt vector, linker script, startup code, MMIO 주소 접근을 이해하거나 디버깅할 때 사용합니다.
- **주의할 경우:** 메모리맵에 없는 주소나 실제 register가 없는 unassigned address를 접근하면 안 됩니다. 노트에서는 이런 접근이 유효한 값을 주지 않을 뿐 아니라 Hard Fault Interrupt를 발생시켜 시스템이 멈출 수 있다고 설명합니다.

---

## 대표 예시

### STM32 전체 메모리맵 예시

| 영역 | 시작 주소 | 설명 |
|------|-----------|------|
| Flash | `0x08000000` | 프로그램 코드 |
| System Memory | `0x1FFFF000` | 제조사가 넣어 둔 built-in software, 예: 부트로더 |
| SRAM | `0x20000000` | 실행 중 변수 등이 들어가는 실제 메모리 |
| Peripheral Registers | `0x40000000` 영역 | MMIO 대상인 주변장치 레지스터 |

이 표는 전체 4GB 주소 공간 중 주요 영역을 요약한 것입니다. 실제 세부 주소는 MCU 데이터시트나 레퍼런스 매뉴얼을 기준으로 확인해야 합니다.

---

## 헤프게 할당되는 이유

Peripheral Register는 실제 사용량보다 훨씬 큰 주소 블록을 할당받을 수 있습니다.

노트의 USART 예시는 다음과 같습니다.

```text
USART register 개수 = 7개
register 하나 크기 = 4바이트
실제 사용량 = 7 × 4바이트 = 28바이트

USART 하나에 할당된 블록 = 1024바이트
사용되지 않는 공간 = 1024 - 28 = 996바이트
```

즉, 실제 register는 28바이트뿐이지만 주소 공간은 1024바이트가 배정될 수 있습니다.

이유는 전체 주소 공간이 4GB로 넉넉하고, 하드웨어 설계에서는 peripheral마다 큰 블록을 통째로 잘라 할당하는 편이 더 단순하기 때문입니다.

---

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| **Memory Map** | MCU 전체 주소 공간에서 Flash, SRAM, Peripheral 영역이 어디 있는지 보여준다. |
| **Register Map** | 특정 peripheral 내부 register들이 base address 기준 어떤 offset에 있는지 보여준다. |
| **Flash** | 프로그램 코드가 저장되는 영역이다. |
| **SRAM** | 실행 중 변수와 데이터가 저장되는 실제 메모리 영역이다. |
| **Peripheral Register 영역** | GPIO, USART 같은 하드웨어 레지스터가 주소 공간에 매핑된 영역이다. |
| **Unassigned Address** | 주소 블록 안에 있어도 실제 register가 연결되지 않은 주소다. 접근 시 Hard Fault가 날 수 있다. |

---

## 꼬리질문 예상

- **Q:** MCU 메모리맵은 무엇인가요?
  **A:** CPU가 접근할 수 있는 전체 주소 공간에서 Flash, SRAM, System Memory, Peripheral Register가 각각 어느 주소 범위에 배치되어 있는지 보여주는 주소표입니다.

- **Q:** STM32 예시에서 전체 주소 공간이 왜 4GB인가요?
  **A:** 32비트 주소를 사용하기 때문입니다. 가능한 주소 개수는 `2^32`개이고, 바이트 단위 주소라면 전체 크기는 `2^32`바이트, 즉 4GB입니다.

- **Q:** `0xFFFFFFFF`는 무슨 의미인가요?
  **A:** 32비트 주소 공간에서 표현 가능한 최대 주소입니다. 노트에서는 이를 “eight Fs”라고 설명합니다.

- **Q:** Peripheral 영역은 왜 `0x40000000` 부근에 있나요?
  **A:** 이 STM32 메모리맵에서 Peripheral Registers 영역이 그 주소대에 배치되어 있기 때문입니다. 이런 배치는 개발자가 정하는 것이 아니라 MCU 제조사가 하드웨어 설계와 문서에서 정해 둔 것입니다.

- **Q:** Peripheral 하나가 실제로 28바이트만 쓰는데 왜 1024바이트를 할당하나요?
  **A:** 4GB 주소 공간이 넉넉하고, 하드웨어 설계에서는 peripheral마다 큰 블록을 통째로 배정하는 편이 더 쉽기 때문입니다. 노트의 USART 예시에서는 7개 register × 4바이트 = 28바이트만 실제 사용하지만, USART 하나에 1024바이트가 할당된다고 설명합니다.

- **Q:** 할당된 1024바이트 안이면 아무 주소나 접근해도 되나요?
  **A:** 아닙니다. 그 블록 안에서도 실제 register가 없는 unassigned address가 있을 수 있습니다. 노트에서는 이런 주소에 접근하면 유효한 값을 얻지 못할 뿐 아니라 Hard Fault Interrupt가 발생할 수 있다고 설명합니다.

- **Q:** Memory Map과 Register Map은 어떻게 다른가요?
  **A:** Memory Map은 MCU 전체 주소 공간 배치표이고, Register Map은 특정 peripheral 내부 register들의 offset 배치표입니다. 노트에서는 Register Map을 메모리맵의 미니 버전처럼 보면 된다고 설명합니다.

---

## 자주 하는 오해

- **오해:** 32비트 MCU는 실제 RAM이 4GB 있다는 뜻이다.
  - **정확히는:** 32비트 주소 공간이 4GB라는 뜻입니다. 실제 Flash나 SRAM 용량이 4GB라는 뜻은 아닙니다. 이 노트에서는 32비트 주소로 메모리맵 전체가 4GB 크기라고 설명합니다.

- **오해:** 메모리맵의 모든 주소에 실제 메모리가 있다.
  - **정확히는:** 일부 주소는 Flash, 일부는 SRAM, 일부는 Peripheral Register에 연결되고, 일부는 실제 대상이 없을 수 있습니다.

- **오해:** Peripheral 블록에 할당된 주소는 전부 안전하게 접근 가능하다.
  - **정확히는:** 블록 안에서도 실제 register가 없는 unassigned address는 접근하면 안 됩니다. Hard Fault가 발생할 수 있습니다.

- **오해:** Peripheral 주소는 개발자가 코드에서 정한다.
  - **정확히는:** GPIO, USART 같은 주변장치 주소는 MCU 제조사가 하드웨어 설계로 고정해 둡니다. 개발자는 데이터시트나 레퍼런스 매뉴얼에 나온 주소표를 보고 사용합니다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-------------|
| 메모리 주소표 | Memory Map |
| 전체 주소 범위 | Address Space |
| 프로그램 코드 영역 | Flash |
| 실행 중 변수 영역 | SRAM |
| 제조사 내장 코드 영역 | System Memory |
| 장치 레지스터 영역 | Peripheral Registers |
| 주변장치 내부 주소표 | Register Map |
| 실제 레지스터 없는 주소 | Unassigned Address |
| 잘못된 주소 접근으로 멈춤 | Hard Fault |
| 시작 주소 | Base Address |
| 기준 주소에서 떨어진 거리 | Offset |

---

## 키워드

`MCU Memory Map` `Address Space` `32-bit address` `4GB` `0xFFFFFFFF` `Flash` `SRAM` `System Memory` `Peripheral Registers` `Register Map` `Unassigned Address` `Hard Fault`
