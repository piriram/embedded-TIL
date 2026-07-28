# Reset Vector와 벡터 테이블

> 파생 학습노트: `10_주제별/cs/임베디드수업/8_MCU_메모리맵과_MMIO.md`
> 최종 갱신: 2026-05-20

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다. 입에 붙을 때까지.

Reset Vector는 MCU가 전원 켜진 직후 가장 먼저 실행할 코드의 주소를 담고 있는 메모리 위치입니다. 이 노트의 STM32 예시에서는 Reset Vector가 `0x00000004`에 있고, 그 뒤에는 각 인터럽트가 발생했을 때 실행할 핸들러 주소들이 들어 있는 Interrupt Vector Table이 이어집니다. 여기서 vector는 “코드의 주소”, 즉 핸들러 함수로 점프하기 위한 포인터라고 보면 됩니다. 또한 이 MCU에서는 Flash가 원래 주소인 `0x08000000`뿐 아니라 부팅 시 필요한 낮은 주소 영역인 `0x00000000`에도 보이도록 aliasing될 수 있습니다. 따라서 부팅 직후 CPU는 주소 0 근처의 벡터 정보를 읽고, Reset Vector가 가리키는 초기화 코드로 이동해 프로그램 실행을 시작합니다.

---

## 한 줄 정의

**Reset Vector는 MCU가 리셋 직후 처음 실행할 코드의 주소를 담는 벡터이고, Interrupt Vector Table은 각 인터럽트 핸들러의 주소 목록이다.**

핵심은 **벡터가 코드 자체가 아니라 “실행할 코드의 주소”라는 점**입니다.

---

## 왜 필요한가

MCU가 전원이 켜졌을 때 바로 C 코드의 `main()`을 자동으로 알고 실행할 수 있는 것은 아닙니다.

리셋 직후 CPU는 정해진 메모리 위치에서 “어디로 점프해야 하는지”를 읽어야 합니다. 이때 필요한 시작점 정보가 Reset Vector입니다.

또한 실행 중 인터럽트가 발생하면, 인터럽트 종류마다 처리해야 할 코드가 다릅니다. 그래서 각 인터럽트별 핸들러 주소를 모아 둔 Interrupt Vector Table이 필요합니다. 인터럽트가 발생하면 MCU는 해당 슬롯의 주소를 읽고 그 핸들러로 점프합니다.

---

## 동작 원리

### Reset Vector

노트 기준으로 이 MCU의 Reset Vector는 주소 `0x00000004`에 저장됩니다.

```text
전원 켜짐 / 리셋 발생
        ↓
MCU가 정해진 벡터 위치를 읽음
        ↓
Reset Vector에서 시작 코드 주소를 얻음
        ↓
그 주소로 점프
        ↓
초기화 코드 실행
```

Reset Vector 자체는 실행 코드가 아니라, **처음 실행할 코드의 주소값**입니다.

### Interrupt Vector Table

Reset Vector 바로 다음에는 Interrupt Vector Table이 이어집니다.

```text
Interrupt Vector Table
- Reset Handler 주소
- Timer Interrupt Handler 주소
- USART Interrupt Handler 주소
- GPIO Interrupt Handler 주소
- ...
```

인터럽트가 발생하면 MCU는 그 인터럽트에 대응하는 슬롯을 찾아 핸들러 주소를 읽고, 해당 코드로 점프합니다.

---

## 언제 쓰는가 / 언제 피하는가

- **쓰는 경우:** MCU 부팅 과정, startup code, linker script, interrupt handler 등록, bare-metal firmware 구조를 설명할 때 필요합니다.
- **주의할 경우:** Reset Vector와 Interrupt Vector Table은 일반 변수 테이블이 아닙니다. CPU가 리셋과 인터럽트 처리에 직접 사용하는 주소 테이블이므로, 잘못 배치되거나 잘못된 주소를 담으면 부팅 실패나 잘못된 핸들러 실행으로 이어질 수 있습니다.

---

## 대표 예시

노트의 STM32 메모리 맵 설명에서는 Flash가 두 주소에서 보일 수 있다고 설명합니다.

| 주소 | 의미 |
|------|------|
| `0x00000000` | 부팅 시 벡터 테이블 접근을 위해 Flash가 보이는 alias 영역 |
| `0x00000004` | Reset Vector가 저장되는 위치 |
| `0x08000000` | Flash의 원래 주소 |
| Reset Vector 이후 | Interrupt Vector Table |

즉, 같은 Flash 메모리가 `0x00000000`과 `0x08000000` 두 주소 범위에서 접근될 수 있습니다. 이것이 aliasing입니다.

---

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| **Reset Vector** | 리셋 직후 처음 실행할 코드의 주소를 담는다. |
| **Interrupt Vector Table** | 각 인터럽트가 발생했을 때 실행할 핸들러 주소들을 담는다. |
| **Reset Handler** | Reset Vector가 가리키는 실제 초기화 코드다. |
| **Interrupt Handler** | 특정 인터럽트를 처리하는 실제 코드다. |
| **Flash Aliasing** | 같은 Flash가 `0x08000000`뿐 아니라 `0x00000000` 같은 다른 주소에서도 보이게 하는 하드웨어 매핑이다. |

---

## 꼬리질문 예상

- **Q:** Vector는 정확히 무엇인가요?
  **A:** 이 노트에서는 vector를 “어떤 코드의 주소”라고 설명합니다. 즉 실행할 코드 자체가 아니라, 그 코드로 점프하기 위한 주소값입니다.

- **Q:** Reset Vector에는 코드가 들어 있나요?
  **A:** 코드 자체가 아니라, 리셋 직후 실행할 코드의 주소가 들어 있습니다.

- **Q:** 이 노트의 예시에서 Reset Vector는 어디에 있나요?
  **A:** 주소 `0x00000004`에 저장된다고 설명되어 있습니다.

- **Q:** Interrupt Vector Table은 왜 필요한가요?
  **A:** 인터럽트 종류마다 실행할 핸들러가 다르기 때문에, 각 인터럽트에 대응하는 핸들러 주소를 테이블로 저장해 두어야 합니다. 인터럽트가 발생하면 MCU는 해당 슬롯의 주소를 가져와 그 핸들러로 점프합니다.

- **Q:** 왜 Flash가 `0x00000000`에도 보이나요?
  **A:** 부팅 시 CPU가 낮은 주소 영역에서 벡터 정보를 읽어야 하기 때문입니다. 이 MCU는 같은 Flash를 `0x08000000`뿐 아니라 `0x00000000`에서도 접근할 수 있게 aliasing할 수 있다고 설명됩니다.

- **Q:** Flash aliasing은 Flash가 두 개 있다는 뜻인가요?
  **A:** 아닙니다. 같은 Flash 메모리가 두 주소 범위에서 보이는 것입니다. 노트에서는 어떤 주소 범위를 사용하든 같은 Flash memory가 접근된다고 설명합니다.

---

## 자주 하는 오해

- **오해:** Reset Vector는 리셋 직후 실행되는 코드 그 자체다.
  - **정확히는:** Reset Vector는 실행할 코드의 주소입니다. 실제 코드는 그 주소가 가리키는 Reset Handler입니다.

- **오해:** Interrupt Vector Table에는 인터럽트 처리 코드가 직접 들어 있다.
  - **정확히는:** 각 인터럽트 핸들러의 주소가 들어 있습니다. 인터럽트 발생 시 MCU가 그 주소로 점프합니다.

- **오해:** Flash가 `0x00000000`과 `0x08000000`에 보이면 Flash가 두 개다.
  - **정확히는:** 같은 Flash가 두 주소 범위에서 보이도록 하드웨어가 alias를 만든 것입니다.

- **오해:** CPU가 전원을 켜면 바로 `main()`을 실행한다.
  - **정확히는:** CPU는 먼저 벡터 정보를 통해 시작 주소를 얻고, Reset Handler 같은 초기화 코드를 거친 뒤 일반적으로 `main()`으로 진입합니다. 이 마지막 `main()` 진입 과정은 일반적인 MCU startup flow 설명이며, 업로드 노트에는 Reset Vector와 인터럽트 벡터 테이블 중심으로 설명되어 있습니다.

---

## 자주 놓치는 정확 표현

| 모호한 말 | 정확한 용어 |
|----------|-------------|
| 시작 코드 | Reset Handler |
| 시작 코드 주소 | Reset Vector |
| 인터럽트 목록 | Interrupt Vector Table |
| 인터럽트 함수 주소 | Interrupt Handler Address |
| 코드 주소 | Vector |
| 주소 0에 Flash가 보임 | Flash Aliasing |
| 같은 메모리가 다른 주소에 보임 | Memory Aliasing |
| 부팅 시 읽는 표 | Vector Table |

---

## 키워드

`Reset Vector` `Interrupt Vector Table` `Vector` `Reset Handler` `Interrupt Handler` `Flash Aliasing` `0x00000004` `0x00000000` `0x08000000` `Boot Sequence`
