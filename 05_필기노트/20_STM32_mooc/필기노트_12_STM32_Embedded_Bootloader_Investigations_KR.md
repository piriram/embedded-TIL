# Ch.12 STM32 Embedded Bootloader Investigations 한글판

용도: STM32 bootloader debugging용 MOOC 기반 한글 손필기 노트

규칙:

- A4 세로 반 접기 2열 손필기
- 들여쓰기 없음
- 파랑: 제목, 번호, 핵심 키워드
- 검정: 설명, 예시, cf
- 빨강: 면접 주의, 헷갈리는 점
- Boot mode, AN2606, option byte, pin, communication interface를 연결해서 이해

## 1페이지: STM32 Embedded Bootloader란

<span style="color:#1d4ed8">주제: Embedded bootloader investigation</span><br>
<span style="color:#1d4ed8">1. 핵심 개념</span><br>
<span style="color:#111827">a. 모든 STM32 MCU는 system memory 안에 embedded bootloader를 가진다.</span><br>
<span style="color:#111827">b. 이 bootloader는 지원되는 interface를 통해 firmware programming을 가능하게 한다.</span><br>
<span style="color:#111827">c. Boot mode는 MCU가 user Flash, SRAM, system memory 중 어디서 시작할지 결정한다.</span><br>
<span style="color:#111827">- 예: USART, I2C, SPI, USB, CAN interface</span><br>
<span style="color:#dc2626">※ Bootloader 동작은 device-specific이므로 정확한 MCU 문서를 확인해야 함</span><br>
<br>
<span style="color:#1d4ed8">2. 확인해야 할 문서</span><br>
<span style="color:#111827">a. Reference manual은 선택한 MCU의 boot mode 설정을 설명한다.</span><br>
<span style="color:#111827">b. AN2606은 bootloader activation pattern과 지원 interface를 정리한다.</span><br>
<span style="color:#111827">c. Board user manual은 BOOT0와 connector pin 위치를 보여준다.</span><br>
<span style="color:#111827">d. 이 세 문서를 함께 봐야 한다.</span><br>
<span style="color:#dc2626">※ 다른 보드 기준으로 BOOT0나 bootloader pin을 추측하지 않기</span><br>
<br>
<span style="color:#1d4ed8">3. Boot mode가 의존할 수 있는 것</span><br>
<span style="color:#111827">a. BOOT0 pin level.</span><br>
<span style="color:#111827">b. Option byte 값.</span><br>
<span style="color:#111827">c. Empty Flash check mechanism.</span><br>
<span style="color:#111827">d. MCU에 따른 software boot configuration.</span><br>
<span style="color:#dc2626">※ Boot mode는 한 가지 요소만으로 결정된다고 보면 안 됨</span><br>

## 2페이지: Bootloader 활성화

<span style="color:#1d4ed8">4. 예시 target</span><br>
<span style="color:#111827">a. 영상은 STM32G474 Nucleo 보드를 사용한다.</span><br>
<span style="color:#111827">b. 같은 조사 원리는 다른 STM32 family에도 적용할 수 있다.</span><br>
<span style="color:#111827">c. 다만 정확한 activation pattern과 interface 목록은 달라질 수 있다.</span><br>
<span style="color:#dc2626">※ 예시는 방법으로만 보고 universal pin map으로 보지 않기</span><br>
<br>
<span style="color:#1d4ed8">5. Activation pattern 예시</span><br>
<span style="color:#111827">a. 발표자는 AN2606에서 target MCU의 activation pattern을 확인한다.</span><br>
<span style="color:#111827">b. 이 보드에서 선택한 pattern은 여러 조건을 요구한다.</span><br>
<span style="color:#111827">c. BOOT_LOCK option bit가 boot path를 잠그면 안 된다.</span><br>
<span style="color:#111827">d. nBOOT1 option bit가 요구 값으로 설정되어야 한다.</span><br>
<span style="color:#111827">e. BOOT0 pin은 high로 설정되어야 한다.</span><br>
<span style="color:#111827">f. nSWBOOT0 option bit도 요구 설정과 맞아야 한다.</span><br>
<span style="color:#dc2626">※ 흔한 실수: BOOT0만 맞추고 option byte를 무시함</span><br>
<br>
<span style="color:#1d4ed8">6. CubeProgrammer에서 option byte 확인</span><br>
<span style="color:#111827">a. STM32CubeProgrammer를 연다.</span><br>
<span style="color:#111827">b. ST-LINK를 통해 보드에 연결한다.</span><br>
<span style="color:#111827">c. Option Bytes tab을 연다.</span><br>
<span style="color:#111827">d. Security 관련 boot lock 설정을 확인한다.</span><br>
<span style="color:#111827">e. nBOOT1, nSWBOOT0 같은 user configuration 값을 확인한다.</span><br>
<span style="color:#111827">f. Board manual에 따라 물리 BOOT0 pin level을 설정한다.</span><br>
<span style="color:#dc2626">※ Option byte는 보안 설정만이 아니라 boot configuration의 일부</span><br>

## 3페이지: Bootloader 활성화 확인법

<span style="color:#1d4ed8">7. 핵심 확인 방법</span><br>
<span style="color:#111827">a. Program Counter 값을 확인한다.</span><br>
<span style="color:#111827">b. Bootloader가 활성화되면 Program Counter가 system memory range에 있어야 한다.</span><br>
<span style="color:#111827">c. User application이 활성화되면 Program Counter가 Flash range에 있어야 한다.</span><br>
<span style="color:#111827">d. 주소 range는 reference manual에 설명되어 있다.</span><br>
<span style="color:#dc2626">※ “bootloader가 실행된 것 같다”보다 주소 range 확인이 더 강한 증거</span><br>
<br>
<span style="color:#1d4ed8">8. 예시 해석</span><br>
<span style="color:#111827">a. BOOT0 high + 요구 option bytes + reset = Program Counter가 system memory에 위치.</span><br>
<span style="color:#111827">b. BOOT0 low + reset = Program Counter가 user Flash에 위치.</span><br>
<span style="color:#111827">c. 이것으로 boot mode selection이 동작함을 확인할 수 있다.</span><br>
<span style="color:#111827">d. Debugger를 조사 도구로 쓸 수 있음도 보여준다.</span><br>
<span style="color:#dc2626">※ Boot mode는 추측이 아니라 address range로 확인</span><br>
<br>
<span style="color:#1d4ed8">9. 핵심 영어 문장</span><br>
<span style="color:#111827">a. I verified bootloader activation by checking the Program Counter.</span><br>
<span style="color:#111827">b. When it was in system memory range, the embedded bootloader was active.</span><br>
<span style="color:#111827">c. When BOOT0 was low, the Program Counter moved to user Flash range after reset.</span><br>
<span style="color:#dc2626">※ 이 문장은 영어 면접 대비용으로 소리 내어 연습</span><br>

## 4페이지: Bootloader 통신 interface

<span style="color:#1d4ed8">10. 지원되는 interface</span><br>
<span style="color:#111827">a. AN2606은 STM32 device별 지원 bootloader interface를 나열한다.</span><br>
<span style="color:#111827">b. 예시 G4 device에서는 USART, I2C, SPI, USB 등을 지원한다.</span><br>
<span style="color:#111827">c. 각 interface는 특정 pin을 가진다.</span><br>
<span style="color:#111827">d. 보드 설계에서 기대하는 pin이 올바르게 routing되어 있어야 한다.</span><br>
<span style="color:#dc2626">※ pin이 틀리면 bootloader는 active여도 접근할 수 없을 수 있음</span><br>
<br>
<span style="color:#1d4ed8">11. 첫 번째 디버깅 조언</span><br>
<span style="color:#111827">a. Bootloader 통신이 실패하면 먼저 같은 hardware path를 테스트한다.</span><br>
<span style="color:#111827">b. 해당 interface로 간단한 user application을 만든다.</span><br>
<span style="color:#111827">c. 예를 들어 bootloader를 의심하기 전에 USART 통신을 먼저 검증한다.</span><br>
<span style="color:#111827">d. 이것은 board routing, connector, pin이 맞는지 확인한다.</span><br>
<span style="color:#111827">e. Hardware path 문제와 bootloader state 문제를 분리한다.</span><br>
<span style="color:#dc2626">※ 좋은 디버깅은 failure domain을 분리하는 것부터 시작</span><br>
<br>
<span style="color:#1d4ed8">12. Interface scanning 동작</span><br>
<span style="color:#111827">a. Embedded bootloader는 활성화 후 지원되는 interface들을 scan한다.</span><br>
<span style="color:#111827">b. 한 interface에서 activity를 감지하면 다른 interface scan을 멈춘다.</span><br>
<span style="color:#111827">c. 그 뒤 감지된 interface를 기다리는 loop에 들어간다.</span><br>
<span style="color:#111827">d. 이 때문에 사용자가 원한 interface 통신이 막힐 수 있다.</span><br>
<span style="color:#dc2626">※ 이 영상의 핵심 교훈</span><br>

## 5페이지: 잘못된 interface 감지 문제

<span style="color:#1d4ed8">13. 실패 시나리오</span><br>
<span style="color:#111827">a. 사용자는 USART2로 bootloader와 통신하려고 한다.</span><br>
<span style="color:#111827">b. USART2 통신이 시작되기 전에 다른 pin이 toggle된다.</span><br>
<span style="color:#111827">c. Bootloader는 그 activity를 USART1 activity로 해석한다.</span><br>
<span style="color:#111827">d. Bootloader는 USART1에서 기다리게 된다.</span><br>
<span style="color:#111827">e. 다음 reset 전까지 USART2 통신은 실패한다.</span><br>
<span style="color:#dc2626">※ Power-up 중 임의의 pin transition이 wrong bootloader interface를 선택할 수 있음</span><br>
<br>
<span style="color:#1d4ed8">14. 제품 설계에서 중요한 이유</span><br>
<span style="color:#111827">a. 보드 power-up 중 외부 신호가 예기치 않게 toggle될 수 있다.</span><br>
<span style="color:#111827">b. 그 pin이 bootloader-supported interface라면 bootloader가 잘못된 interface를 선택할 수 있다.</span><br>
<span style="color:#111827">c. 이 문제는 생산 프로그래밍이나 현장 복구를 불안정하게 만든다.</span><br>
<span style="color:#111827">d. Embedded bootloader는 ST가 제공한 것이므로 사용자가 수정할 수 없다.</span><br>
<span style="color:#dc2626">※ Bootloader interface 동작은 제품 정의 단계에서 고려해야 함</span><br>
<br>
<span style="color:#1d4ed8">15. 실무 설계 의미</span><br>
<span style="color:#111827">a. Reset과 startup 동안 bootloader interface pin의 원치 않는 activity를 피해야 한다.</span><br>
<span style="color:#111827">b. Pull-up, pull-down, external device, connector state를 확인한다.</span><br>
<span style="color:#111827">c. 의도한 bootloader interface는 통신 전까지 접근 가능하고 조용해야 한다.</span><br>
<span style="color:#dc2626">※ Bootloader access는 firmware 설계만이 아니라 board-level design의 일부</span><br>

## 6페이지: 어떤 interface가 활성화됐는지 조사

<span style="color:#1d4ed8">16. 조사 전략</span><br>
<span style="color:#111827">a. 통신이 실패하면 어떤 bootloader interface가 초기화됐는지 확인한다.</span><br>
<span style="color:#111827">b. AN2606으로 가능한 bootloader interface 목록을 만든다.</span><br>
<span style="color:#111827">c. Reference manual에서 각 peripheral base address와 register size를 찾는다.</span><br>
<span style="color:#111827">d. Debug link를 통해 peripheral register 값을 dump한다.</span><br>
<span style="color:#111827">e. 통신 시도 전후 register 값을 비교한다.</span><br>
<span style="color:#dc2626">※ Bootloader state를 register level에서 디버깅하는 방식</span><br>
<br>
<span style="color:#1d4ed8">17. Command line이 유용한 이유</span><br>
<span style="color:#111827">a. 영상은 STM32CubeProgrammer command line 사용을 추천한다.</span><br>
<span style="color:#111827">b. Command line은 여러 interface의 register content를 dump할 수 있다.</span><br>
<span style="color:#111827">c. USART, I2C, SPI, USB register state를 비교하기 쉽다.</span><br>
<span style="color:#111827">d. 현재 bootloader state를 보존해야 하면 debug connection이 board를 reset하면 안 된다.</span><br>
<span style="color:#dc2626">※ 너무 빨리 reset하면 증거를 없앨 수 있음</span><br>
<br>
<span style="color:#1d4ed8">18. Register 변화에서 얻는 증거</span><br>
<span style="color:#111827">a. USART2가 사용되면 USART2 register에 통신 관련 변화가 보인다.</span><br>
<span style="color:#111827">b. USART1 pin이 toggle되면 USART1 register에 통신 시도 흔적이 보인다.</span><br>
<span style="color:#111827">c. USB가 연결되면 USB register에 connection activity가 보인다.</span><br>
<span style="color:#111827">d. 이런 변화로 bootloader가 선택한 interface를 알 수 있다.</span><br>
<span style="color:#dc2626">※ 선택된 interface가 내가 기대한 interface가 아닐 수 있음</span><br>

## 7페이지: 우회 방법과 설계 선택

<span style="color:#1d4ed8">19. 우회 방법 1</span><br>
<span style="color:#111827">a. User application에서 embedded bootloader로 jump한다.</span><br>
<span style="color:#111827">b. Application이 언제 bootloader로 들어갈지 제어할 수 있다.</span><br>
<span style="color:#111827">c. 의도한 interface pin만 active하도록 보장하는 데도 도움이 된다.</span><br>
<span style="color:#111827">d. 이 방법은 지원 device에 대해 AN2606에 설명되어 있다.</span><br>
<span style="color:#dc2626">※ 모든 STM32 chip에서 가능하거나 동일한 방식은 아님</span><br>
<br>
<span style="color:#1d4ed8">20. 우회 방법 2</span><br>
<span style="color:#111827">a. Custom bootloader를 구현한다.</span><br>
<span style="color:#111827">b. Custom bootloader는 사용할 interface와 protocol을 직접 정의할 수 있다.</span><br>
<span style="color:#111827">c. 일부 device에 대해 ST Cube firmware package에 bootloader 예제가 있다.</span><br>
<span style="color:#111827">d. 제어권은 커지지만 firmware 복잡도도 증가한다.</span><br>
<span style="color:#dc2626">※ Custom bootloader는 safety, recovery, update failure 처리를 함께 설계해야 함</span><br>
<br>
<span style="color:#1d4ed8">21. 관련 protocol 문서</span><br>
<span style="color:#111827">a. AN2606은 system memory boot mode와 activation pattern을 설명한다.</span><br>
<span style="color:#111827">b. 다른 ST application note들은 bootloader communication protocol을 설명한다.</span><br>
<span style="color:#111827">c. 필요한 protocol 문서는 선택한 interface에 따라 달라진다.</span><br>
<span style="color:#111827">d. USART, I2C, SPI, USB DFU, CAN은 protocol detail이 다르다.</span><br>
<span style="color:#dc2626">※ Boot activation rule과 communication protocol rule을 섞지 않기</span><br>

## 기술 용어

<span style="color:#1d4ed8">embedded bootloader</span><br>
<span style="color:#111827">a. System memory에 저장된 ST 내장 bootloader.</span><br>
<br>
<span style="color:#1d4ed8">activation pattern</span><br>
<span style="color:#111827">a. MCU를 system memory로 부팅시키는 데 필요한 pin과 option byte 조합.</span><br>
<br>
<span style="color:#1d4ed8">option byte</span><br>
<span style="color:#111827">a. Boot configuration이나 protection 같은 device behavior를 제어하는 비휘발성 설정값.</span><br>
<br>
<span style="color:#1d4ed8">Program Counter</span><br>
<span style="color:#111827">a. 현재 실행 중이거나 곧 실행할 instruction 주소를 담는 CPU register.</span><br>
<br>
<span style="color:#1d4ed8">system memory</span><br>
<span style="color:#111827">a. Embedded bootloader가 들어 있는 보호된 memory 영역.</span><br>
<br>
<span style="color:#1d4ed8">user Flash</span><br>
<span style="color:#111827">a. User application firmware가 저장되는 Flash memory.</span><br>
<br>
<span style="color:#1d4ed8">DFU</span><br>
<span style="color:#111827">a. Device Firmware Upgrade. USB firmware update mode에서 자주 쓰임.</span><br>
<br>
<span style="color:#1d4ed8">register dump</span><br>
<span style="color:#111827">a. Hardware 또는 firmware state를 보기 위해 peripheral register raw 값을 읽는 것.</span><br>

## 30초 한글 설명

<span style="color:#1d4ed8">면접 답변</span><br>
<span style="color:#111827">a. STM32 MCU에는 system memory 안에 embedded bootloader가 들어 있습니다.</span><br>
<span style="color:#111827">b. 이를 정확히 활성화하려면 reference manual과 AN2606을 확인해야 합니다.</span><br>
<span style="color:#111827">c. 필요한 pin과 option-byte pattern은 device마다 다릅니다.</span><br>
<span style="color:#111827">d. 활성화 여부는 Program Counter가 system memory range에 있는지 확인해서 검증할 수 있습니다.</span><br>
<span style="color:#111827">e. 통신이 실패하면 의도치 않은 pin activity 때문에 다른 interface가 선택됐을 수 있습니다.</span><br>
<span style="color:#111827">f. 이 경우 peripheral register를 dump해서 어떤 interface가 초기화됐는지 확인할 수 있습니다.</span><br>
<span style="color:#dc2626">※ 마무리: bootloader debugging은 firmware와 board-level thinking이 모두 필요합니다</span><br>

## 꼬리질문

<span style="color:#1d4ed8">Q1. STM32 embedded bootloader는 어디에 있는가?</span><br>
<span style="color:#111827">a. STM32 device 내부의 system memory에 있다.</span><br>
<br>
<span style="color:#1d4ed8">Q2. Bootloader activation을 위해 어떤 문서를 확인해야 하나?</span><br>
<span style="color:#111827">a. MCU reference manual.</span><br>
<span style="color:#111827">b. AN2606.</span><br>
<span style="color:#111827">c. Board user manual.</span><br>
<br>
<span style="color:#1d4ed8">Q3. Bootloader가 active인지 어떻게 확인하나?</span><br>
<span style="color:#111827">a. Program Counter가 system memory address range에 있는지 확인한다.</span><br>
<br>
<span style="color:#1d4ed8">Q4. 기대한 interface로 통신이 실패하는 이유는?</span><br>
<span style="color:#111827">a. Bootloader가 다른 interface의 activity를 먼저 감지했을 수 있다.</span><br>
<span style="color:#111827">b. 그 뒤 scan을 멈추고 해당 interface에서 기다리기 때문이다.</span><br>
<br>
<span style="color:#1d4ed8">Q5. 선택된 interface를 어떻게 조사하나?</span><br>
<span style="color:#111827">a. AN2606에서 가능한 interface 목록을 만든다.</span><br>
<span style="color:#111827">b. Reference manual에서 register address를 찾는다.</span><br>
<span style="color:#111827">c. Peripheral register를 dump하고 값을 비교한다.</span><br>
<br>
<span style="color:#1d4ed8">Q6. 제품 설계에서 왜 중요한가?</span><br>
<span style="color:#111827">a. Startup 중 의도치 않은 pin activity가 wrong interface를 선택할 수 있기 때문이다.</span><br>
<span style="color:#111827">b. 이로 인해 bootloader recovery나 production programming이 불안정해질 수 있다.</span><br>

## 참고 자료

<span style="color:#1d4ed8">원본 영상</span><br>
<span style="color:#111827">STM32 boot and startup tips - Embedded bootloader investigations</span><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=kTMjjED8ErA">https://www.youtube.com/watch?v=kTMjjED8ErA</a><br>
<br>
<span style="color:#1d4ed8">관련 문서</span><br>
<span style="color:#111827">AN2606 - STM32 microcontroller system memory boot mode</span><br>
<span style="color:#dc2626">※ STM32 family별 activation pattern과 bootloader interface는 AN2606에서 다시 확인</span><br>
