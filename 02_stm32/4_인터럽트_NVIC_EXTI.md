# STM32 입문 #6 — 인터럽트 (NVIC · EXTI)

**주제:** 폴링 vs 인터럽트, NVIC와 벡터 테이블, EXTI 외부 인터럽트로 스위치 누름마다 LED 토글하기
**타겟 MCU:** STM32F767VIT6
**원본 강의:** [(210) STM32 입문 강의 몰아보기 | ARM, GPIO, ADC, UART (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)

> 인터럽트는 MCU의 핵심 기능이다. 전동 킥보드 구동 시 **홀센서 신호를 인터럽트로 받아 삼상 인버터를 구동**하므로 매우 중요하다.

---

## 1. 폴링 vs 인터럽트 — 치킨 배달 비유

**폴링(Polling):** 치킨을 시키고 **문 앞에서 올 때까지 계속 기다림**. 다른 일(설거지·공부·운동)을 아무것도 못 한다.

```c
while (1) {
    if (치킨_도착) break;   // 올 때까지 이것만 확인
}
```

**인터럽트(Interrupt):** 치킨 시키고 **하던 공부를 계속함**. 초인종(인터럽트)이 울리면 그때만 잠깐 멈추고 치킨을 받은 뒤 다시 공부로 복귀.

> **주의 — 폴링이 무조건 나쁜 게 아니다.**
> 어떤 값이 **무조건, 매우 빠르게** 들어온다는 게 보장되면 폴링도 괜찮다. 폴링은 구현이 더 간단하다. 인터럽트는 핸들러·우선순위 관리가 필요해 상대적으로 복잡하다. **시스템을 명확히 이해하고 골라야 한다.**

---

## 2. 인터럽트 개념과 NVIC

코어는 주변 장치와 연결돼 있고, 주변 장치가 **인터럽트를 발생**시킬 수 있다(GPIO 입력, ADC 완료, 통신 수신 등). 발생하면 **현재 작업을 잠시 멈추고 인터럽트를 처리**한 뒤 원래 루틴으로 복귀한다.

**NVIC(Nested Vectored Interrupt Controller):** Cortex-M 시리즈가 공통으로 쓰는 ARM의 인터럽트 컨트롤러. 인터럽트를 우선순위 기반으로 처리한다.

- 인터럽트 발생 → **ISR(Interrupt Service Routine)** 함수 호출.
- ISR의 시작 번지들을 **우선순위에 따라 저장**해 둔 것이 **인터럽트 벡터 테이블(Interrupt Vector Table)**.
- 인터럽트가 동시에 두 개 발생하면 미리 정한 우선순위로 처리한다.

---

## 3. 벡터 테이블 — 우선순위와 주소

레퍼런스 매뉴얼 NVIC 챕터의 벡터 테이블에는 Position, Priority, Type of priority, Address, Description이 있다.

- **−1, −2, −3 (Reset, NMI, HardFault):** Priority가 **Fixed** — ARM이 고정, 우리가 못 바꾼다.
- **0번부터:** 우선순위 변경 가능. 표의 값은 **디폴트**다.
- **Address:** 인터럽트 발생 시 호출될 **ISR 함수가 저장된 주소**. 그 번지로 점프해 코드를 실행한다.

예: EXTI0 인터럽트 발생 → 해당 함수가 저장된 메모리 주소로 점프.

---

## 4. EXTI — 외부 인터럽트 컨트롤러

**EXTI(Extended Interrupt and Event Controller):** GPIO 핀으로 들어오는 외부 신호를 인터럽트로 만든다. **CPU 코어가 아니라 주변 장치**라는 점이 중요하다. 외부/내부 신호를 인식해 **NVIC에 전달**한다.

### 4.1 EXTI 라인 구조

- GPIO 각 핀(포트 A~)에서 들어오는 외부 인터럽트는 **EXTI0 ~ EXTI15**.
- 같은 번호 핀들(모든 포트의 0번 핀 등)이 **하나의 EXTI 라인으로 묶임**.
- **벡터:** EXTI0~EXTI4는 각각 개별 벡터(5개). **EXTI5~9는 하나로**, **EXTI10~15도 하나로** 묶여 벡터를 공유한다.

### 4.2 EXTI 동작 흐름

1. **Input Line** — 외부 신호 입력.
2. **엣지 검출** — Falling edge는 **FTSR**, Rising edge는 **RTSR** 레지스터로 선택.
3. **마스크** — Interrupt Mask Register(IMR)로 허용/금지. 마스크 = "가린다" = 사용 안 함. **인터럽트를 쓰려면 마스킹을 해제**(비트=1)해야 한다.
4. 마스크 해제 시 → **Pending Request Register(PR)** 의 대기 비트가 1로 세팅 → 신호가 **NVIC로 입력** → 우선순위 기반 처리.

> **이미지 필요**
> EXTI 블록도 — Input Line → 엣지 검출(FTSR/RTSR) → IMR 마스크 → Pending(PR) → NVIC
> - 출처: STM32F767 레퍼런스 매뉴얼 EXTI 챕터, 강의 1:46~1:48
> - 대체안: 레퍼런스 매뉴얼 "External interrupt/event controller block diagram"

---

## 5. 실습 — PD4 스위치로 LED 토글

PD4 스위치를 EXTI4에 연결해, **Falling edge(스위치 ON)마다** LED를 토글한다.

### 5.1 설정 순서

1. **GPIO·LED·스위치 클럭/모드 설정** (앞 편들과 동일). LED 초기값 OFF.
2. **SYSCFG 클럭 enable** — EXTI는 **APB2**에 연결. `RCC_APB2ENR`로 SYSCFG enable.
3. **`SYSCFG_EXTICR2`** — EXTI4의 소스를 **포트 D**로 지정. (EXTICR2가 EXTI4~7 담당.) 초기값 클리어 후 PD4 선택값(`0x3` = `0011`) 설정.
4. **`EXTI_IMR`** — 4번 비트=1로 마스킹 해제(인터럽트 사용).
5. **`EXTI_FTSR`** — 4번 비트=1로 Falling edge 트리거 선택.
6. **`EXTI_PR`** — 4번 비트=1을 써서 Pending 클리어. (1을 쓰면 0으로 클리어됨. 초기 쓰레기 값 제거.)
7. **`NVIC_EnableIRQ(EXTI4_IRQn)`** — CMSIS 인라인 함수로 EXTI4 인터럽트 enable. 인자는 헤더에 정의된 IRQ 번호.

```c
RCC->APB2ENR |= (1 << 14);          // SYSCFG 클럭 (예시 비트)
SYSCFG->EXTICR[1] &= ~(0xF << 0);   // EXTI4 클리어
SYSCFG->EXTICR[1] |=  (0x3 << 0);   // EXTI4 = 포트 D
EXTI->IMR  |= (1 << 4);             // 마스크 해제
EXTI->FTSR |= (1 << 4);             // Falling edge
EXTI->PR   |= (1 << 4);             // Pending 클리어
NVIC_EnableIRQ(EXTI4_IRQn);         // NVIC enable
```

### 5.2 ISR — 인터럽트 핸들러

스위치 ON(Falling edge)마다 핸들러가 실행돼 LED를 토글한다.

```c
void EXTI4_IRQHandler(void) {
    if (EXTI->PR & (1 << 4)) {       // 정말 EXTI4가 발생했나 확인
        EXTI->PR |= (1 << 4);        // 1을 써서 Pending 클리어
        GPIOD->ODR ^= (1 << 3);      // LED 토글(반전)
    }
}
```

- 핸들러 진입 시 **PR 비트로 발생 여부 확인** → 1이면 처리.
- **PR에 1을 다시 써서 클리어** — 안 하면 다음 인터럽트를 구분 못 한다.
- `^=`(XOR)로 LED 반전 → 누를 때마다 ON/OFF 반복.

> **주의 — 핸들러 안에서 긴 delay 금지.**
> ISR 안에 1초짜리 delay를 넣으면, 그 1초 동안 다른 인터럽트가 발생해도 처리가 꼬인다. 특히 우선순위가 더 높은 인터럽트가 대기 중이면 문제다. **ISR은 짧게** 끝내야 한다. (인버터 펌웨어에서는 SysTick으로 task를 만들어 이를 해결할 예정.)

---

## 참고 자료

- [(210) STM32 입문 강의 몰아보기 (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)
- **STM32F767 레퍼런스 매뉴얼** — NVIC 벡터 테이블, EXTI(IMR/FTSR/RTSR/PR), SYSCFG_EXTICR
- CMSIS `stm32f767xx.h` — IRQ 번호 정의, `NVIC_EnableIRQ`
- 관련: [GPIO 입력과 스위치](../gpio/2_GPIO입력과_스위치.md), [cs/RTOS/9_Hardware_Interrupts](../../cs/RTOS/9_Hardware_Interrupts.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** 인터럽트는 이벤트 발생 시에만 현재 작업을 멈추고 ISR을 실행하는 방식이고, NVIC가 우선순위로 관리한다.
- **왜 필요:** 폴링은 한 신호만 계속 기다려 다른 일을 못 한다. 인터럽트는 평소 다른 작업을 하다 이벤트 시에만 처리해 효율적이다.
- **동작:** 주변 장치(EXTI 등)가 인터럽트를 NVIC에 전달하면, 벡터 테이블에서 ISR 주소로 점프한다. EXTI는 GPIO 외부 신호를 FTSR/RTSR로 엣지 검출하고 IMR로 마스크 해제 후 PR을 세팅해 NVIC로 보낸다. EXTI0~4는 개별 벡터, 5~9·10~15는 묶여 공유한다.
- **비교:** 폴링은 구현이 간단하고 신호가 빠르게 보장될 때 유리하지만 CPU를 점유한다. 인터럽트는 효율적이나 핸들러·우선순위 관리가 필요하고, ISR 안에서 긴 delay는 금물이다.
- **30초 통합 답변:**
  > 폴링은 신호가 올 때까지 while로 계속 기다려서 다른 일을 못 하는 방식이고, 인터럽트는 평소 메인 작업을 하다가 이벤트가 발생한 순간에만 ISR로 처리하는 방식입니다. STM32에선 NVIC가 인터럽트를 우선순위 기반으로 관리하고, 발생 시 벡터 테이블의 ISR 주소로 점프합니다. GPIO 외부 신호는 EXTI가 담당하는데, FTSR이나 RTSR로 falling/rising 엣지를 고르고 IMR로 마스크를 해제한 뒤 Pending 레지스터를 세팅해 NVIC로 전달합니다. 제 실습에선 PD4 스위치를 EXTI4에 연결하고 SYSCFG로 포트 D를 지정, falling edge마다 핸들러에서 ODR을 XOR로 토글해 LED를 켜고 껐습니다. 핸들러에선 PR로 발생을 확인하고 1을 써서 클리어해야 하며, 다른 인터럽트가 꼬이지 않도록 ISR 안에서 긴 delay는 절대 넣지 않습니다.
