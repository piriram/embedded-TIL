# STM32 입문 #2 — GPIO 출력과 LED 제어

**주제:** GPIO 포트/핀 구조를 이해하고, 레지스터를 직접 설정해 LED를 켜고 끄기. STM32CubeIDE에서 CMSIS 헤더로 코딩·빌드·디버깅하기
**타겟 MCU:** STM32F767VIT6
**원본 강의:** [(210) STM32 입문 강의 몰아보기 | ARM, GPIO, ADC, UART (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)

> **실습 회로:** 포트 D의 3번 핀(PD3)에 Fault LED가 연결돼 있다. LED의 애노드는 3.3V, 캐소드가 PD3에 물려 있다.

---

## 1. 포트와 핀 — GPIO의 기본 단위

STM32F767도 패키지(다리 핀 개수·형태)에 따라 포트 수가 다르다. 핀이 100개인 패키지, 다른 형태 등 여러 가지가 있다.

- **포트(Port)** 는 A, B, C, D… 로 구분된다.
- **각 포트는 최대 16개의 핀**을 가진다. 포트 A면 PA0 ~ PA15, 포트 B면 PB0 ~ PB15.

> **주의**
> 실제 핀 개수와 포트 구성은 **패키지마다 다르다.** 회로도와 데이터시트를 항상 확인해야 한다.

---

## 2. LED 켜기 — 전류 방향과 전위차

PD3에는 Fault LED의 **캐소드**가 연결돼 있고, 애노드는 3.3V에 묶여 있다. LED가 켜지려면 전류가 애노드 → 캐소드로 흘러야 한다. 즉 애노드(+) 쪽이 3.3V, 캐소드(−) 쪽이 0V여야 양단에 전위차가 생긴다.

- **PD3 = High(3.3V)** → 애노드도 3.3V, 캐소드도 3.3V → **전위차 없음 → LED OFF**
- **PD3 = Low(0V)** → 애노드 3.3V, 캐소드 0V → **전위차 발생 → LED ON**

| PD3 출력 | LED |
| --- | --- |
| High (3.3V) | OFF |
| Low (0V) | ON |

STM32F767은 3.3V로 동작하므로 High 신호 = 3.3V 출력이다. 포트 내부 출력 구조는 **푸시풀(Push-Pull)** 형태로 되어 있다.

---

## 3. 레지스터 3분류 — Control / Status / Data

MCU의 주변 기능을 쓰려면 **레지스터를 설정**해야 한다. 레지스터 종류가 매우 많은데, 세 가지 기준으로 보면 정리가 쉽다.

- **Control Register** — 통신 속도, 클럭 속도, 인터럽트 사용 여부, 포트를 출력/입력으로 쓸지, 푸시풀 사용 여부 등 **모듈을 설정**하는 레지스터.
- **Status Register** — "통신 완료", "클럭 설정 완료", "인터럽트 발생" 등 **모듈의 상태를 읽는** 레지스터. 어떤 비트가 1로 세팅되며 상태를 알려준다.
- **Data Register** — ADC 변환 결과나 통신으로 받은 데이터가 **저장되는 공간**. 여기서 값을 읽어낸다.

> 이 분류는 MCU마다 딱 나뉘어 있지 않은 경우도 있지만, 기준을 갖고 보면 설정이 한결 수월해진다.

---

## 4. 레지스터는 32비트 — 비트마다 의미가 있다

F767은 32비트 MCU라서 레지스터도 **32비트**다. 0번 비트부터 31번 비트까지 있고, 제조사가 **비트마다(또는 비트 묶음마다) 의미를 부여**해 둔다.

레지스터 설명에는 보통 다음이 따라온다.
- **Address offset** — 베이스 주소에서 떨어진 거리 (레지스터 직접 접근 편에서 활용)
- **Reset value** — 리셋 직후의 초기값

---

## 5. GPIO 출력에 필요한 레지스터들

PD3를 출력으로 쓰려면 RCC로 클럭을 켠 뒤, GPIO 레지스터 4개를 차례로 설정한다.

### 5.1 RCC — 포트 클럭 활성화 (가장 먼저!)

> **주의**
> 모든 주변 장치는 클럭이 공급돼야 동작한다. **주변 장치를 쓸 때 가장 먼저 해야 할 일은 클럭 활성화다.**

GPIO는 AHB1 버스에 물려 있으므로 **RCC AHB1 Peripheral Clock Enable 레지스터(`RCC_AHB1ENR`)** 에서 GPIO D에 해당하는 비트를 1로 설정한다.

```c
RCC->AHB1ENR |= 0x8;   // GPIOD 클럭 enable (bit 3)
```

- `0x8` = `1000`(2진수) → 3번 비트만 1.
- `|=`(OR 연산)을 쓰는 이유: 기존 비트들은 그대로 두고 **원하는 비트만 1로 세팅**하기 위해서. (비트 연산은 별도로 공부할 것.)

### 5.2 GPIOx_MODER — 핀의 모드 결정

`GPIOx_MODER`(Mode Register)는 핀을 어떤 모드로 쓸지 정한다. 핀 하나당 **2비트**를 차지한다.

| 2비트 값 | 모드 |
| --- | --- |
| `00` | Input |
| `01` | **General Purpose Output** (LED 출력에 사용) |
| `10` | Alternate Function (타이머·SPI 등 핀의 특수 기능) |
| `11` | Analog (ADC 등) |

PD3는 6번·7번 비트를 `01`로 설정해 **출력 모드**로 만든다.

```c
GPIOD->MODER |= (1 << 6);   // PD3을 출력 모드(01)로
```

> **참고 — Alternate Function / Analog:**
> 각 핀은 단순 온/오프 외에 데이터시트에 정의된 특수 기능을 가진다. 예를 들어 PA6은 핀 타입이 IO이고 `FT`로 표시돼 있으면 **5V 입력까지 견디는 핀**이다(F767 자체는 3.3V 동작). Alternate Function을 켜면 타이머나 SPI 통신 기능을, Additional Function(Analog)으로는 ADC를 쓸 수 있다.

### 5.3 GPIOx_OTYPER — 출력 타입 (푸시풀/오픈드레인)

`GPIOx_OTYPER`(Output Type Register)로 출력 형태를 정한다. 핀 하나당 **1비트**.

- `0` = **Push-Pull** (리셋 초기값. PD3는 이걸로)
- `1` = Open-Drain

```c
// reset value가 0이라 별도 설정 불필요하지만 명시 가능
```

### 5.4 GPIOx_OSPEEDR — 출력 속도

`GPIOx_OSPEEDR`(Output Speed Register)로 온/오프 출력 속도를 정한다. PD3는 Medium으로 설정.

> **주의 — 빠를수록 좋은 게 아니다.**
> 출력 속도가 빠르다는 건 스위칭 주파수가 높다는 뜻이고, **EMI(전자파 간섭) 문제**가 생긴다. 설계는 항상 요구사항이 있으므로, 오버스펙으로 무작정 빠르게 하지 말고 **요구사항을 만족하는 선에서 적당히** 맞춰야 한다. (예: 고장 신호처럼 급한 건 빠르게, 중요도 낮은 신호는 적당히.)

### 5.5 GPIOx_ODR — 실제 출력 (Output Data Register)

설정이 끝나면 `GPIOx_ODR`(Output Data Register)의 해당 비트로 실제 High/Low를 낸다.

- ODR 비트 = `1` → High(3.3V) 출력 → LED OFF
- ODR 비트 = `0` → Low(0V) 출력 → LED ON

```c
GPIOD->ODR &= ~(1 << 3);   // PD3 = 0 → LED ON
GPIOD->ODR |=  (1 << 3);   // PD3 = 1 → LED OFF
```

위 `ODR`의 `&=`/`|=`는 비트 마스크를 배우기 위한 전형적인 RMW(read-modify-write) 표기다. 실전에서 ISR이나 다른 실행 흐름이 같은 ODR을 갱신할 수 있다면, STM32의 `BSRR`에 한 번 write하는 방식이 더 안전하다. 자세한 이유와 코드는 [GPIO BSRR로 안전하게 출력하기](./3_GPIO_BSRR로_안전하게_출력하기.md)를 참고한다.

---

## 6. 무한 루프와 전역 변수로 제어

임베디드 시스템은 `main`에서 레지스터를 한 번 설정한 뒤 **`while(1)` 무한 루프** 안에서 계속 동작한다.

문제: 루프 안에서 LED를 그냥 켜고 끄면 너무 빨라 눈으로 확인이 안 된다. 그래서 **전역 변수**를 하나 만들어 디버거로 실시간 조작한다.

```c
uint8_t test;   // 전역 변수 (unsigned 8bit)

while (1) {
    if (test == 0) {
        GPIOD->ODR |= (1 << 3);    // LED OFF
    } else {
        GPIOD->ODR &= ~(1 << 3);   // LED ON
    }
}
```

`uint8_t`는 unsigned 8비트 정수의 typedef다.

---

## 7. STM32CubeIDE 실습 흐름

1. **File → New → STM32 Project**
2. **Target Selection**에서 `STM32F767VIT6` 검색 후 선택 → Next
3. 프로젝트 이름 지정(예: `LED_onoff`)

> **주의 — 경로에 한글 금지.**
> 프로젝트 경로에 한글이 있으면 오류가 난다. **컴퓨터 사용자 이름이 한글이면 영어로 변경**해야 한다. 강사도 이 문제를 겪었다.

4. 프로젝트 생성 후 뜨는 그래픽 설정 창(HAL 드라이버 방식)은 **X로 닫는다.** 이 강의는 그래픽 설정 대신 **레지스터에 직접 접근**한다.
5. `Core/Src/main.c`를 열고 자동 생성된 코드를 **Ctrl+A로 전부 지운 뒤** 직접 작성.
6. CMSIS 디바이스 헤더(`stm32f767xx.h`)를 포함한다. 이 헤더 안에 `RCC`, `GPIOD`, `RCC_AHB1ENR` 등 **모든 레지스터가 미리 선언**돼 있어 편하게 접근할 수 있다.
   - 위치: 프로젝트 탐색기 → Drivers → CMSIS → Device → ST → Include 안의 F767 헤더. 프로젝트 생성 시 ST가 제공.

> 글자 크기 조절: Window → Preferences → General → Appearance → Colors and Fonts → C/C++ → Editor 항목 더블클릭.

---

## 8. 빌드 & 디버깅 — 동작 확인

1. **Ctrl+B**로 빌드. 콘솔에 에러·워닝 없는지 확인.
2. 벌레 모양 **Debug 아이콘** 클릭 → OK → Switch → 디버그 화면 진입.
3. **Live Expressions** 창에 전역 변수 `test`를 추가하면 실시간 모니터링·값 변경 가능.
4. **Resume(▶)** 으로 실행. `test = 1` 입력하고 엔터 → `else` 분기로 들어가 LED ON.

유용한 디버깅 기능:
- **Breakpoint** — 코드 줄을 더블클릭하면 점이 생긴다. 그 줄에 도달하면 멈춰 한 줄씩 디버깅 가능.
- **Step Into / Step Over** — 한 줄씩 실행하며 흐름 추적. Step Over는 함수를 한 단위로 넘긴다.
- **SFRS 창** — GPIO D를 펼치면 실제 레지스터 값(MODER, OSPEEDR 등)이 보인다. `01`로 잘 설정됐는지 비트 단위로 확인 가능. (Error reading value가 뜨면 잠깐 멈췄다 다시 실행.)

> CMSIS 헤더의 정체: `GPIOD->MODER`에서 `MODER`를 Ctrl+클릭으로 따라가면 `stm32f767xx.h`로 들어간다. RCC·GPIO 레지스터들이 전부 구조체로 선언돼 있어, 우리는 메모리 주소를 직접 계산하지 않고도 레지스터에 접근할 수 있다. (구조체가 어떻게 만들어졌는지는 다음 편 "레지스터 직접 접근"에서 다룬다.)

---

## 참고 자료

- [(210) STM32 입문 강의 몰아보기 (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)
- **STM32F767 레퍼런스 매뉴얼** — GPIO 챕터 (MODER/OTYPER/OSPEEDR/ODR 레지스터 맵)
- **STM32F767 데이터시트** — 핀별 Alternate/Additional Function 표
- 관련: [레지스터 직접 접근(메모리 맵)](../기초/2_레지스터_직접접근_메모리맵.md)
- 심화: [GPIO BSRR로 안전하게 출력하기](./3_GPIO_BSRR로_안전하게_출력하기.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** GPIO 출력 제어는 RCC로 포트 클럭을 켠 뒤 MODER·OTYPER·OSPEEDR로 핀을 설정하고 ODR로 High/Low를 출력하는 과정이다.
- **왜 필요:** LED 점등 같은 디지털 출력을 내려면 해당 핀을 출력 모드로 설정하고 전압을 제어해야 한다.
- **동작:** ① RCC_AHB1ENR로 GPIOD 클럭 enable → ② MODER 2비트를 01로 출력 모드 → ③ OTYPER로 푸시풀 → ④ OSPEEDR로 속도 → ⑤ ODR 비트로 0(Low)/1(High) 출력. PD3에 LED 캐소드가 물려 있어 PD3=0이면 전위차가 생겨 LED가 켜진다.
- **비교:** Input 모드는 신호를 받고, Output은 내보낸다. Alternate Function은 타이머·SPI 같은 특수 기능, Analog는 ADC용이다. 출력 속도는 빠를수록 EMI가 늘어 요구사항에 맞게 적당히 정해야 한다.
- **30초 통합 답변:**
  > STM32에서 GPIO 출력을 쓰려면 먼저 RCC의 AHB1ENR 레지스터로 해당 포트 클럭을 켜야 합니다. 모든 주변 장치는 클럭이 없으면 동작하지 않기 때문입니다. 그다음 MODER 레지스터에서 핀당 2비트를 01로 설정해 출력 모드로 만들고, OTYPER로 푸시풀, OSPEEDR로 속도를 정합니다. 실제 출력은 ODR 비트에 0이나 1을 써서 Low/High를 냅니다. 제 실습에서는 PD3에 LED 캐소드가 연결돼 있어서 PD3을 0으로 만들면 애노드 3.3V와 전위차가 생겨 LED가 켜졌습니다. 레지스터 설정은 OR·AND 연산으로 원하는 비트만 건드리고, CubeIDE의 Live Expressions와 SFRS 창으로 변수와 레지스터를 실시간 확인하며 디버깅했습니다.
