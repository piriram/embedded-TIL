# STM32 Phase 1: 시작하기 및 첫 LED 깜빡이 (MVP)

이 문서는 새 STM32F103C8T6 (C타입) 보드와 MPU6050 센서 모듈(모두 핀납땜 완제품)을 사용하여 임베디드 포트폴리오의 1단계(생존 신고)를 달성하기 위한 구체적인 가이드입니다.

## 1. 하드웨어 물리적 연결 (ST-Link & 타겟 보드)

코드를 굽기 위한 ST-Link 디버거와 터미널 로그를 확인하기 위한 USB 연결 과정입니다.

### 1.1 준비물
* ST-Link V2 동글
* STM32F103C8T6 보드 (C타입, 정품 ST칩, 핀납땜 완료)
* F/F (암-암) 점퍼선 3가닥 (검정, 노랑, 파랑 추천)
* C타입 USB 케이블 (PC와 연결용)

### 1.2 핀 연결 매핑
ST-Link 본체 겉면의 핀맵 번호/이름과 보드의 핀헤더 이름을 확인하여 F/F 점퍼선으로 연결합니다.

| ST-Link 핀 번호/이름 | 색상 추천 | STM32 보드 핀 | 비고 |
| :--- | :--- | :--- | :--- |
| **5번 또는 6번 (GND)** | 🖤 검정 | **GND** | 그라운드 기준점 통일 |
| **2번 (SWCLK)** | 💛 노랑 | **CLK** (또는 SWCLK) | 디버깅 클럭 |
| **4번 (SWDIO)** | 💙 파랑 | **DIO** (또는 SWDIO) | 디버깅 데이터 |
| **7번 또는 8번 (3.3V)** | ❤️ 빨강 | **(연결 안 함)** | ⚠️ 보드를 USB(C타입)로 전원 공급할 경우 충돌 방지를 위해 3.3V 핀은 빼둡니다. |

> **주의:** C타입 케이블을 보드에 꽂아 전원(빨간색 LED)이 들어오면 ST-Link의 3.3V 전원선은 연결할 필요가 없습니다.

---

## 2. STM32CubeIDE 프로젝트 생성

### 2.1 새 프로젝트 만들기
1. STM32CubeIDE 실행 후 `File` ➔ `New` ➔ `STM32 Project` 선택.
2. Target Selection 창의 좌측 상단 검색창(Part Number)에 `STM32F103C8` 입력.
3. 리스트에서 `STM32F103C8Tx` 선택 후 `Next`.
4. Project Name에 `01_gpio_uart_blink` 입력 후 `Finish` 클릭 (이후 팝업은 기본값 Yes).

---

## 3. 칩 설정 (CubeMX 핀맵 세팅)

프로젝트가 생성되면 자동으로 열리는 칩 뷰(`*.ioc` 파일)에서 하드웨어 설정을 진행합니다.

1. **디버그 포트 활성화 (가장 중요 ⭐️)**
   * 좌측 메뉴 `System Core` ➔ `SYS` 클릭.
   * `Debug` 항목을 **Serial Wire** 로 변경.
   * *(이 설정을 누락하면 칩셋의 SWD 핀이 막혀버려 이후 ST-Link로 다운로드가 불가한 벽돌 현상이 발생할 수 있습니다.)*

2. **클럭 설정 (HSE)**
   * 좌측 메뉴 `System Core` ➔ `RCC` 클릭.
   * `High Speed Clock (HSE)` 항목을 **Crystal/Ceramic Resonator** 로 변경 (보드의 외부 크리스탈 활용).

3. **LED 핀 설정 (출력 모드)**
   * 칩 그림에서 **PC13** 핀(STM32F103 보드의 기본 내장 LED)을 좌클릭.
   * **GPIO_Output** 선택 (해당 핀이 초록색으로 변함).

4. **UART 핀 설정 (비동기 통신)**
   * 좌측 메뉴 `Connectivity` ➔ `USART1` 클릭.
   * `Mode`를 **Asynchronous** 로 변경 (PA9, PA10 핀이 초록색으로 변함).

5. **저장 및 코드 생성**
   * 단축키 `Cmd + S`를 눌러 설정 저장.
   * "Generate Code?" 알럿이 뜨면 **Yes** 클릭.

---

## 4. 5초 깜빡이 코드 작성 및 빌드

생성된 C 코드에 진입하여 직접 로직을 작성합니다.

1. 좌측 `Project Explorer`에서 `Core/Src/main.c` 더블클릭.
2. `int main(void)` 함수 내부의 무한 루프 `while (1)` 블록 탐색.
3. `while (1)` 안에 아래와 같이 LED 토글(Toggle)과 지연(Delay) 함수를 작성합니다.

```c
  /* USER CODE BEGIN WHILE */
  while (1)
  {
      HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13); // PC13 핀의 상태 반전 (ON/OFF)
      HAL_Delay(5000);                        // 5000ms(5초) 대기

    /* USER CODE END WHILE */
```

### 4.1 빌드 및 다운로드
1. 상단 툴바의 **망치 아이콘(Build)** 클릭 ➔ 에러/경고 0개 확인.
2. 상단 툴바의 **재생 버튼(Run)** 또는 **벌레 아이콘(Debug)** 클릭.
3. `Edit Configuration` ➔ `Debugger` 탭 ➔ **ST-LINK** 확인 후 `OK`.
4. 다운로드가 완료되면 보드의 User LED(보통 초록 또는 파란색)가 5초 간격으로 점멸하는 것을 확인합니다.
