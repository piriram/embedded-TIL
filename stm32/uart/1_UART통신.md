# STM32 입문 #9 — UART 통신

**주제:** 직렬/병렬, 전이중/반이중, 동기/비동기 통신 분류, UART 프로토콜과 보레이트, PC와 문자 송수신 실습
**타겟 MCU:** STM32F767VIT6
**원본 강의:** [(210) STM32 입문 강의 몰아보기 | ARM, GPIO, ADC, UART (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)

---

## 1. 통신 분류

### 1.1 직렬 vs 병렬

- **직렬(Serial)** — 데이터를 **한 비트씩 순차** 전송. 배선 간단, 단거리·장거리 안정적, 간섭 적음. UART·SPI·I2C·USB·이더넷·CAN. **임베디드에서 훨씬 많이 쓰임.**
- **병렬(Parallel)** — 여러 비트(D0,D1,D2…)를 **동시** 전송. 고속이지만 배선 복잡, 거리 길수록 노이즈↑. 내부 버스·프린터 포트 등 고속 단거리.

### 1.2 전이중 vs 반이중

- **반이중(Half Duplex)** — 양방향 가능하지만 **동시 송수신 불가**. 예: 무전기("오바").
- **전이중(Full Duplex)** — 양방향 + **동시 송수신 가능**. 예: 전화.

### 1.3 동기 vs 비동기

- **동기(Synchronous)** — **클럭 신호에 동기**해 송수신. 예: I2C, SPI.
- **비동기(Asynchronous)** — 클럭 없이 **TX/RX가 통신 속도를 약속**해 송수신. 예: **UART**.

> **UART vs USART:** F767 데이터시트엔 USART(Universal **Synchronous** Asynchronous Receiver Transmitter)로 표기. Synchronous(동기)로도 설정 가능하지만, 이 강의는 **비동기 UART**로 쓴다. 발음 편의상 "유아트"라 부름.

---

## 2. UART 프로토콜

비동기라 TX(보내는 쪽)와 RX(받는 쪽)가 **약속(프로토콜)** 을 맞춰야 한다. 데이터 라인 한 줄로 통신.

```
[Idle High] → Start(Low) → Data bits(5~8) → [Parity] → Stop(High, 1~2bit)
```

- **Start bit** — 데이터 라인이 **Low로 떨어지면 시작**. (거의 모든 통신이 Low에서 시작.)
- **Data bits** — **5~8비트** 선택 가능.
- **Stop bit** — **High로 올리면 종료**. 1~2비트 선택.
- **Parity bit** — 오류 검출용. 이 강의·일반 UART에선 **미사용**.

> **약속이 맞아야 하는 것:** 데이터 비트 수, 통신 속도(보레이트), Stop 비트. **TX·RX 양쪽 설정이 반드시 같아야** 한다.

### 2.1 결선 — TX↔RX 교차

MCU1의 **TX는 상대 MCU2의 RX에**, MCU1의 RX는 MCU2의 TX에 연결한다.

> **주의:** TX끼리, RX끼리 연결하면 **통신 안 된다.** 반드시 **TX↔RX 교차**.

### 2.2 예시 — 문자 'A' 전송

'A'는 ASCII로 `01000001`(8비트). 데이터 비트를 8비트로 설정하고:
`Start(Low) → 0100 0001 → Stop(High)` 순으로 전송한다.

---

## 3. 보레이트(Baud Rate) 설정

**BPS(Bits Per Second)**, 즉 초당 비트 수를 TX·RX가 동일하게 맞춰야 한다. 흔히 쓰는 값: **9600**(느려도 됨), **115200**(빠르게).

F767의 UART2는 **APB1 클럭(54MHz)** 사용. 보레이트는 간단하다 — **클럭을 원하는 BPS로 나눈 값**을 **`USART_BRR`** 레지스터에 넣는다.

```c
// 9600 bps:    54MHz / 9600   = 5625
USART2->BRR = 5625;
// 115200 bps:  54MHz / 115200 = 468.75 → 반올림 469
USART2->BRR = 469;
```

> BPS가 커질수록 오차율이 조금씩 발생한다. (OVER8 비트 설정에 따라 계산식이 달라진다.)

---

## 4. 실습 — PC와 문자 송수신

### 4.1 하드웨어

MCU의 UART TX/RX를 PC에 바로 물려선 통신이 안 된다. **USB 변환 모듈**(키트 포함, 빨간 모듈)을 거쳐 USB로 변환해야 한다. PC에는 **Tera Term** 프로그램으로 모니터링.

> 전동 킥보드 개발 시 UART를 2개 사용: ① PC 연결용(USB 변환), ② **블루투스 모듈**(블루투스도 결국 UART). 폰으로 속도·온도·전류를 받아볼 예정.

### 4.2 설정 순서

1. **`init_MCU()`**.
2. **UART2 클럭 enable** — UART2는 **APB1**. `RCC_APB1ENR` 사용.
3. **GPIOD 클럭 enable** — **PD5=TX, PD6=RX** 사용(AHB 버스).
4. **PD5·PD6을 Alternate Function 모드(`10`)** — `GPIOD_MODER`에서 각 핀 2비트를 10으로. (TX/RX는 GPIO 특수기능.)
5. **`USART_CR1/CR2/CR3` 초기화(0)** — 일단 비활성화. (PLL처럼 끄고 내부 설정 후 켜는 패턴.)
6. **`USART_BRR`** 보레이트 설정(위 계산값).
7. **`USART_CR1`** 에서 비트 enable:
   - **UE(bit0)** — USART Enable.
   - **RE(bit2)** — Receiver Enable (Start bit 검색).
   - **TE(bit3)** — Transmitter Enable.

```c
RCC->APB1ENR |= (1 << 17);        // USART2 클럭 (예시 비트)
RCC->AHB1ENR |= (1 << 3);         // GPIOD 클럭
GPIOD->MODER |= (2 << (5*2));     // PD5 = AF(10)
GPIOD->MODER |= (2 << (6*2));     // PD6 = AF(10)
USART2->CR1 = 0; USART2->CR2 = 0; USART2->CR3 = 0;
USART2->BRR = 5625;               // 9600 bps
USART2->CR1 |= (1<<0)|(1<<2)|(1<<3);  // UE | RE | TE
```

> 매크로 활용: 16진수 대신 `(1 << 17)` 같은 시프트 표현이 가독성이 좋다. CubeIDE에서 매크로에 커서를 올리면 확장값을 볼 수 있다.

### 4.3 송수신 함수

**TX — 데이터 레지스터가 빌 때까지 대기 후 전송:**

```c
void uart_send_char(char c) {
    while (!(USART2->ISR & (1 << 7)));  // TXE: 송신 데이터 레지스터 빔 대기
    USART2->TDR = c;                    // 보낼 데이터 write → 자동 송신
}
```

- **ISR의 TXE(bit7)** — Transmit data register empty. 0이면 아직 못 비움(대기), 1이면 비어서 쓸 수 있음.
- 비었을 때 **`TDR`(Transmit Data Register)** 에 데이터를 쓰면 자동 송신.

**RX — 데이터 받을 때까지 대기 후 반환:**

```c
char uart_recv_char(void) {
    while (!(USART2->ISR & (1 << 5)));  // RXNE: 수신 데이터 있음 대기
    return USART2->RDR;                 // 받은 데이터 반환
}
```

- **ISR의 RXNE** — Read data register Not Empty. 받으면 1.
- **`RDR`(Receive Data Register)** 에서 읽어 반환.

### 4.4 테스트 — 받은 문자 +1 되돌리기

```c
init_MCU();
uart2_init();
while (1) {
    uint8_t received = uart_recv_char();  // PC → MCU
    received += 1;                        // 문자 +1
    uart_send_char(received);             // MCU → PC
}
```

PC에서 `a`를 보내면 MCU가 +1 한 `b`를 되돌려 보낸다.

> **실습:** Tera Term 다운로드 → Serial 선택 → UART USB 모듈의 COM 포트 지정 → Setup/Serial Port에서 Speed **9600** → New setting. `a`를 누르면 `+1`된 값이 PC로 송신되는 것을 확인.

---

## 참고 자료

- [(210) STM32 입문 강의 몰아보기 (YouTube)](https://www.youtube.com/watch?v=XOsyrZGZtR8)
- **STM32F767 레퍼런스 매뉴얼** — USART 챕터(CR1, BRR, ISR/TXE·RXNE, TDR, RDR)
- **Tera Term** — PC 시리얼 모니터링 프로그램
- 관련: [GPIO 출력과 LED 제어](../gpio/1_GPIO출력과_LED제어.md)(Alternate Function), [클럭과 PLL 설정](../기초/3_클럭과_PLL설정.md)(APB1 54MHz)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** UART는 클럭 없이 TX·RX가 보레이트를 약속해 데이터를 한 비트씩 주고받는 비동기 직렬·전이중 통신이다.
- **왜 필요:** 배선이 적고 안정적이라 MCU 디버깅·모듈 간 통신에 널리 쓰인다.
- **동작:** 데이터 라인이 Start(Low)→Data 5~8bit→Stop(High) 순으로 전송된다. 보레이트는 클럭/BPS 값을 BRR에 넣어 설정한다. TX는 TXE 플래그로 데이터 레지스터가 비길 기다려 TDR에 쓰고, RX는 RXNE로 수신을 기다려 RDR에서 읽는다. TX↔RX는 교차 결선한다.
- **비교:** I2C·SPI는 클럭 동기식이고 UART는 비동기다. 직렬은 배선이 적고 장거리 안정적, 병렬은 고속이나 단거리. UART는 양쪽 보레이트·데이터 비트·Stop 비트 설정이 같아야 한다.
- **30초 통합 답변:**
  > UART는 클럭 신호 없이 송수신 양쪽이 보레이트를 동일하게 약속해 데이터를 한 비트씩 주고받는 비동기 직렬 통신입니다. 데이터 라인이 평소 High였다가 Low로 떨어지면 Start, 5~8비트 데이터를 보낸 뒤 High로 올리면 Stop입니다. 보레이트는 사용하는 APB1 54MHz 클럭을 원하는 BPS로 나눈 값을 BRR 레지스터에 넣어 설정하고, 9600이면 5625가 됩니다. CR1에서 UE·RE·TE를 켜고, 송신은 TXE 플래그로 데이터 레지스터가 빌 때까지 기다려 TDR에 쓰며, 수신은 RXNE로 데이터가 들어올 때까지 기다려 RDR에서 읽습니다. 결선은 반드시 TX와 RX를 교차해야 하고, PC와 연결할 땐 USB 변환 모듈을 거쳐 Tera Term으로 모니터링했습니다.
