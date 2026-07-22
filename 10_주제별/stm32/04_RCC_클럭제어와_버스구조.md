# RCC (Reset and Clock Control) 클럭 제어와 버스 아키텍처

## 1. 전력 최적화를 위한 STM32의 설계 철학
아두이노(AVR 기반) 등 교육용 마이크로컨트롤러와 달리, STM32 같은 산업용 MCU는 전력 소모를 최소화하도록 설계되어 있습니다.
- 초기 부팅 시 MCU의 코어(CPU)를 제외한 **모든 주변장치(Peripheral)의 전원과 클럭(Clock)이 꺼져 있습니다.**
- 만약 클럭을 켜지 않고 해당 주변장치의 레지스터(MMIO)에 접근하려 하면 시스템 오류(Hard Fault)가 발생하거나 값이 무시됩니다.

## 2. RCC (Reset and Clock Control)
따라서 특정 주변장치(GPIO, I2C, SPI 등)를 사용하려면 가장 먼저 **RCC 레지스터**를 제어하여 해당 주변장치가 연결된 내부 버스(Bus)의 클럭 스위치를 켜주어야 합니다.

## 3. 버스(Bus) 아키텍처 (AHB, APB)
STM32 내부는 데이터를 실어 나르는 여러 개의 고속도로(Bus)로 나뉘어 있습니다. 장치의 속도 요구사항에 따라 연결된 버스가 다릅니다.
- **AHB (Advanced High-performance Bus)**: 가장 빠른 버스. DMA, 메모리 등 고속 장치가 연결됨.
- **APB (Advanced Peripheral Bus)**:
  - `APB1`: 저속 주변장치 (I2C1, 일반 타이머 등)
  - `APB2`: 고속 주변장치 (GPIO 전체, ADC, 통신 모듈 일부 등)

## 4. 실전 예시 (오늘의 학습)
베어메탈(Bare-metal) 코드 `main.c` 작성 시, 다음 작업을 최우선으로 수행했습니다.
1. PC13 핀에 연결된 내장 LED를 켜기 위해 `APB2` 버스의 `GPIOC` 클럭 활성화.
2. MPU6050 센서 통신(I2C1)을 위해 `APB2`의 `GPIOB` 및 `AFIO`(Alternate Function) 클럭과 `APB1`의 `I2C1` 클럭 활성화.
