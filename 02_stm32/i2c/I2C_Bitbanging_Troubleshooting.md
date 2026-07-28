# I2C Bit-banging 디버깅 트러블슈팅 (SDA 핀 0V 고정 문제)

## 📌 개요
STM32F103 (Blue Pill) 보드에서 I2C 통신을 하드웨어(I2C IP)가 아닌 **GPIO Bit-banging**으로 구현하여 MPU6050 센서와 통신할 때 발생한 문제를 디버깅한 기록입니다.

## 🐛 문제 현상
- `I2C_ReadByte(0)` 함수를 통해 MPU6050의 `WHO_AM_I` 레지스터(0x75)를 읽어왔으나, 정상적인 값(`0x68`)이 아닌 **`0x00`**이 읽힘.
- 코드는 정상적으로 실행(멈추지 않음)되나, 센서와의 실제 데이터 통신이 이루어지지 않는 상태.

## 🕵️‍♂️ 디버깅 과정

### 1. 디버거 변수 최적화 문제 해결 (`volatile` 활용)
초기에는 VSCode 디버거에서 변수 값이 `<optimized out>`으로 표시되어 값을 확인할 수 없었습니다.
- **해결 방안:** 컴파일러 최적화로 인해 변수가 사라지는 것을 막기 위해 `volatile uint8_t mpu_id = 0;` 처럼 `volatile` 키워드를 추가하여 실시간으로 값을 모니터링할 수 있도록 조치함.

### 2. printf 방식의 한계 (RAM Overflow)
UART나 USB CDC를 통한 `printf` 출력을 시도했으나 빌드 에러가 발생함.
- **원인:** STM32F103C8 칩은 RAM이 20KB로 매우 제한적. FreeRTOS와 USB 스택이 이미 메모리를 점유하고 있는 상황에서 `stdio.h`의 무거운 `printf` 라이브러리를 추가하자 **RAM Overflow** 발생.
- **결론:** 메모리가 부족한 소형 칩에서는 무리하게 `printf`를 추가하기보다는 **디버거(VSCode VARIABLES 창)를 적극적으로 활용**하는 것이 훨씬 효율적임.

### 3. I2C 주소 스캐너(Scanner) 및 ACK 확인 코드 도입
센서가 물리적으로 응답(ACK)을 하는지 확인하기 위해 아래와 같이 코드를 수정함.
1. `1 ~ 127`까지 모든 주소를 찔러보고 ACK가 떨어지는 주소를 `found_address`에 저장하는 스캐너 작성.
2. 각 통신 단계(`WriteByte`)마다 반환되는 ACK 값을 `volatile` 변수(`ack1`, `ack2`, `ack3`)에 저장하여 모니터링.

```c
// I2C 주소 스캐너
volatile uint8_t found_address = 0;
for (uint8_t addr = 1; addr < 128; addr++) {
    I2C_Start();
    uint8_t ack = I2C_WriteByte(addr << 1);
    I2C_Stop();
    if (ack == 0) {
        found_address = addr; // 센서 발견!
        break;
    }
    delay_us(100);
}
```

## 🔍 원인 분석 (결과 확인)
VSCode 디버거를 통해 확인한 결과는 다음과 같았습니다.
- `found_address = 1`
- `ack1 = 0`, `ack2 = 0`, `ack3 = 0`
- `mpu_id = 0`

**[분석 결과]**
- I2C 프로토콜에서 **ACK는 SDA 선이 LOW(0)**로 떨어질 때 인식됨.
- `found_address`가 존재할 수 없는 주소인 1번지에서 바로 발견(ACK=0)되었고, 모든 쓰기 작업의 ACK가 0으로 떨어짐.
- 심지어 데이터(`mpu_id`)를 읽을 때도 모든 비트가 0으로 읽혀 최종 값이 0이 나옴.
- **즉, SDA 선(PB9 핀)이 물리적으로 항상 0V (LOW) 상태로 강제 고정되어 있다는 뜻!**

## 💡 해결 및 교훈 (Lesson Learned)
SDA 선이 항상 0V라는 것은 소프트웨어 버그가 아닌 **하드웨어(물리적 핀 연결)의 합선(Short)이나 오결선**을 의미합니다.

* **체크리스트:**
  1. SDA 선이 `PB9` 핀이 아닌 그 옆의 `GND` 핀에 잘못 꽂혀 있는지 점검 (Blue Pill 보드 구조 상 핀 간격 착각 주의).
  2. 빵판(Breadboard) 내부에서 SDA 라인이 GND 라인과 접촉(합선)되지 않았는지 확인.

* **핵심 교훈:**
  I2C 통신 실패 시, 데이터 값만 보지 말고 **ACK 응답 비트**를 쪼개서 확인하면 문제의 원인(SDA Stuck Low / High)을 하드웨어 레벨에서 정확히 추론할 수 있다.

### 🚀 향후 계획
기존 빵판(Breadboard) 환경에서의 접촉 불량 및 오결선 한계를 극복하기 위해, **새로 구매하여 직접 납땜을 완료한 새 부품들로 하드웨어 환경을 싹 교체하여 처음부터 깔끔하게 다시 시작**하기로 결정함! (2026-07-24)
