# Ch.11 STM32 Boot and Startup - Empty Check Mechanism 한글판

용도: Ch.10 이후 STM32 MOOC 기반 한글 손필기 노트

규칙:

- A4 세로 반 접기 2열 손필기
- 들여쓰기 없음
- 파랑: 제목, 번호, 핵심 키워드
- 검정: 설명, 예시, cf
- 빨강: 면접 주의, 헷갈리는 점
- 영어판과 같은 구조를 유지하되 한국어로 개념을 먼저 고정

## 1페이지: Empty Check Mechanism이란

<span style="color:#1d4ed8">주제: STM32 Empty Check Mechanism</span><br>
<span style="color:#1d4ed8">1. 핵심 개념</span><br>
<span style="color:#111827">a. Empty check mechanism은 일부 STM32 MCU에 있는 부팅 동작이다.</span><br>
<span style="color:#111827">b. Flash 첫 주소가 비어 있으면 MCU가 system bootloader로 부팅한다.</span><br>
<span style="color:#111827">c. BOOT 핀을 따로 조작하지 않아도 빈 장치를 프로그래밍할 수 있게 해준다.</span><br>
<span style="color:#111827">d. 처음 프로그래밍하는 새 MCU에서 유용하다.</span><br>
<span style="color:#111827">cf) virgin device = 아직 한 번도 프로그래밍되지 않은 새 MCU</span><br>
<span style="color:#dc2626">※ 프로그래밍에는 편하지만 이미 조립된 보드에서는 위험할 수 있음</span><br>
<br>
<span style="color:#1d4ed8">2. 주요 부팅 경로</span><br>
<span style="color:#111827">a. 일반 경우: Flash에 사용자 펌웨어가 있으면 user application을 실행한다.</span><br>
<span style="color:#111827">b. Empty 경우: Flash가 비어 있으면 system memory bootloader로 들어간다.</span><br>
<span style="color:#111827">c. System bootloader는 STM32 내부에 기본으로 들어 있는 부트로더다.</span><br>
<span style="color:#111827">d. 지원되는 bootloader interface를 통해 펌웨어를 쓸 수 있게 해준다.</span><br>
<span style="color:#111827">- 예: UART bootloader interface</span><br>
<span style="color:#dc2626">※ system bootloader와 user application boot code를 혼동하지 않기</span><br>
<br>
<span style="color:#1d4ed8">3. ST가 이 기능을 넣은 이유</span><br>
<span style="color:#111827">a. 빈 MCU는 펌웨어를 받을 방법이 필요하다.</span><br>
<span style="color:#111827">b. Empty check가 없으면 사용자가 BOOT 핀을 특정 레벨로 강제해야 할 수 있다.</span><br>
<span style="color:#111827">c. Empty check가 있으면 MCU가 자동으로 system bootloader에 들어갈 수 있다.</span><br>
<span style="color:#111827">d. 생산 또는 프로토타입 단계의 최초 프로그래밍을 단순하게 만든다.</span><br>
<span style="color:#dc2626">※ 면접 포인트: 장점과 위험을 같이 설명하기</span><br>

## 2페이지: 왜 문제가 될 수 있나

<span style="color:#1d4ed8">4. GPIO 부작용</span><br>
<span style="color:#111827">a. System bootloader가 실행되면 여러 GPIO를 output으로 설정할 수 있다.</span><br>
<span style="color:#111827">b. 그 핀들이 조립된 PCB의 외부 회로와 연결되어 있을 수 있다.</span><br>
<span style="color:#111827">c. Output 핀이 GND 또는 VDD에 직접 묶여 있으면 short circuit이 생길 수 있다.</span><br>
<span style="color:#111827">d. 최악의 경우 MCU나 외부 부품이 손상될 수 있다.</span><br>
<span style="color:#111827">cf) assembled PCB = 부품이 이미 실장된 보드</span><br>
<span style="color:#dc2626">※ 부팅 동작은 펌웨어 문제가 아니라 하드웨어 안전 문제이기도 함</span><br>
<br>
<span style="color:#1d4ed8">5. 프로그래밍 후 reset 문제</span><br>
<span style="color:#111827">a. 프로그래밍이 끝나면 Flash는 더 이상 비어 있지 않다.</span><br>
<span style="color:#111827">b. 그런데 reset 후에도 MCU가 system bootloader로 다시 들어갈 수 있다.</span><br>
<span style="color:#111827">c. Empty check bit가 아직 clear되지 않았기 때문이다.</span><br>
<span style="color:#111827">d. Reset pin을 통한 단순 reset만으로는 충분하지 않을 수 있다.</span><br>
<span style="color:#dc2626">※ 코드를 Flash했다고 empty check 조건이 자동으로 사라진다고 단정하지 않기</span><br>
<br>
<span style="color:#1d4ed8">6. 영상에서 언급한 STM32 계열</span><br>
<span style="color:#111827">a. 이 기능은 모든 STM32G0와 STM32WB part number에 존재한다.</span><br>
<span style="color:#111827">b. 일부 STM32L0, STM32L4, STM32F0에도 존재한다.</span><br>
<span style="color:#111827">c. 영상은 STM32 system memory boot mode 문서로 AN2606을 가리킨다.</span><br>
<span style="color:#111827">d. 정확한 동작은 선택한 device 기준으로 다시 확인해야 한다.</span><br>
<span style="color:#dc2626">※ 한 STM32 family 동작을 모든 STM32에 일반화하지 않기</span><br>

## 3페이지: 안전한 프로그래밍 절차

<span style="color:#1d4ed8">7. 절차의 목표</span><br>
<span style="color:#111827">a. 목표는 system bootloader가 실행되기 전에 빈 STM32를 프로그래밍하는 것이다.</span><br>
<span style="color:#111827">b. MCU가 이미 PCB에 납땜되어 있을 때 특히 유용하다.</span><br>
<span style="color:#111827">c. 원치 않는 GPIO output 상태로 인한 위험을 줄인다.</span><br>
<span style="color:#dc2626">※ 핵심 아이디어: debugger를 연결하는 동안 MCU를 reset 상태로 잡아두기</span><br>
<br>
<span style="color:#1d4ed8">8. 단계별 흐름</span><br>
<span style="color:#111827">a. 전원 인가 전후로 MCU를 reset 상태에 둔다.</span><br>
<span style="color:#111827">b. Debug pin을 제외한 GPIO는 analog 또는 high-impedance 상태에 머문다.</span><br>
<span style="color:#111827">c. Connect under reset 방식으로 debugger를 연결한다.</span><br>
<span style="color:#111827">d. Core가 어떤 instruction도 실행하기 전에 멈춰 있게 한다.</span><br>
<span style="color:#111827">e. User application을 Flash에 프로그래밍한다.</span><br>
<span style="color:#111827">f. 다음 정상 부팅 전에 empty check bit를 clear한다.</span><br>
<span style="color:#111827">cf) high impedance = 핀이 HIGH나 LOW를 강하게 구동하지 않는 상태</span><br>
<span style="color:#dc2626">※ bit를 clear하지 않으면 MCU가 system memory로 다시 부팅할 수 있음</span><br>
<br>
<span style="color:#1d4ed8">9. Empty check bit를 clear하는 방법</span><br>
<span style="color:#111827">a. 보드 전원을 완전히 껐다 켠다.</span><br>
<span style="color:#111827">b. Option byte launch를 수행한다.</span><br>
<span style="color:#111827">c. Flash configuration register에서 empty bit를 직접 clear한다.</span><br>
<span style="color:#111827">d. 직접 register clear 방식은 STM32G0와 STM32WB에서만 가능하다.</span><br>
<span style="color:#dc2626">※ 배터리가 이미 조립된 제품에서는 power cycle이 어려울 수 있음</span><br>

## 4페이지: CubeProgrammer 실습 요약

<span style="color:#1d4ed8">10. 데모 구성</span><br>
<span style="color:#111827">a. 데모는 내부 Flash가 비어 있는 STM32G0 Nucleo 보드를 사용한다.</span><br>
<span style="color:#111827">b. 외부 노란색 LED를 PA9에 연결한다.</span><br>
<span style="color:#111827">c. PA9는 system bootloader에서 UART1 transmit으로 사용된다.</span><br>
<span style="color:#111827">d. Bootloader가 실행되면 PA9가 output이 되고 노란색 LED가 켜진다.</span><br>
<span style="color:#111827">e. User application은 Nucleo 보드의 초록색 LED를 깜빡이는 코드다.</span><br>
<br>
<span style="color:#1d4ed8">11. CubeProgrammer 순서</span><br>
<span style="color:#111827">a. STM32CubeProgrammer를 연다.</span><br>
<span style="color:#111827">b. ST-LINK mode를 선택한다.</span><br>
<span style="color:#111827">c. Normal이나 hot plug가 아니라 connect under reset을 선택한다.</span><br>
<span style="color:#111827">d. 물리 reset button을 누른 상태에서 ST-LINK로 연결한다.</span><br>
<span style="color:#111827">e. Debugger가 연결된 뒤 reset button을 놓는다.</span><br>
<span style="color:#111827">f. Application hex file을 프로그래밍한다.</span><br>
<span style="color:#111827">g. Option byte launch로 empty check condition을 clear한다.</span><br>
<span style="color:#111827">h. 연결을 끊고 user application이 실행되는지 확인한다.</span><br>
<span style="color:#dc2626">※ 확인 증거: 노란 LED는 꺼져 있고 초록 LED가 깜빡임</span><br>
<br>
<span style="color:#1d4ed8">12. 데모가 증명하는 것</span><br>
<span style="color:#111827">a. Bootloader 실행을 막은 상태에서도 MCU를 프로그래밍할 수 있다.</span><br>
<span style="color:#111827">b. Connect under reset은 user code나 bootloader code 실행 전에 debugger 제어권을 준다.</span><br>
<span style="color:#111827">c. Option byte launch는 MCU가 empty check state를 다시 샘플링하게 만든다.</span><br>
<span style="color:#111827">d. 조건이 clear되면 MCU는 user Flash로 부팅한다.</span><br>
<span style="color:#dc2626">※ 이건 이론이 아니라 생산 프로그래밍과 연결되는 실무 개념</span><br>

## 기술 용어

<span style="color:#1d4ed8">empty check mechanism</span><br>
<span style="color:#111827">a. 첫 Flash 주소가 비어 있는지 확인하는 하드웨어/부팅 시점 메커니즘.</span><br>
<br>
<span style="color:#1d4ed8">system bootloader</span><br>
<span style="color:#111827">a. ST가 system memory에 넣어둔 내장 bootloader.</span><br>
<br>
<span style="color:#1d4ed8">virgin device</span><br>
<span style="color:#111827">a. 아직 프로그래밍되지 않은 새 MCU.</span><br>
<br>
<span style="color:#1d4ed8">assembled PCB</span><br>
<span style="color:#111827">a. 부품이 이미 실장된 인쇄회로기판.</span><br>
<br>
<span style="color:#1d4ed8">connect under reset</span><br>
<span style="color:#111827">a. MCU를 reset 상태로 잡아둔 채 debugger를 연결하는 debug connection mode.</span><br>
<br>
<span style="color:#1d4ed8">option byte launch</span><br>
<span style="color:#111827">a. Option byte 설정을 다시 로드하고 system reset을 발생시키는 절차.</span><br>
<br>
<span style="color:#1d4ed8">high impedance</span><br>
<span style="color:#111827">a. 핀이 HIGH 또는 LOW를 강하게 밀지 않는 상태.</span><br>

## 30초 한글 설명

<span style="color:#1d4ed8">면접 답변</span><br>
<span style="color:#111827">a. Empty check mechanism은 Flash 첫 주소가 비어 있는지 확인하는 STM32의 부팅 동작입니다.</span><br>
<span style="color:#111827">b. 비어 있으면 MCU는 user Flash가 아니라 내장 system bootloader로 부팅합니다.</span><br>
<span style="color:#111827">c. 이 기능은 빈 장치를 처음 프로그래밍할 때 유용합니다.</span><br>
<span style="color:#111827">d. 하지만 조립된 PCB에서는 bootloader가 GPIO를 output으로 설정할 수 있어 위험할 수 있습니다.</span><br>
<span style="color:#111827">e. 이를 피하려면 connect under reset으로 debugger를 연결하고, application을 flash한 뒤 empty check condition을 clear해야 합니다.</span><br>
<span style="color:#dc2626">※ 마무리: 이 개념은 boot flow 문제이면서 board safety 문제이기도 하다고 이해했습니다</span><br>

## 꼬리질문

<span style="color:#1d4ed8">Q1. 빈 STM32가 system memory로 부팅하는 이유는?</span><br>
<span style="color:#111827">a. Empty check mechanism이 첫 Flash 주소가 비어 있다고 판단하기 때문이다.</span><br>
<br>
<span style="color:#1d4ed8">Q2. 조립된 PCB에서 왜 위험할 수 있나?</span><br>
<span style="color:#111827">a. System bootloader가 GPIO를 output으로 설정할 수 있기 때문이다.</span><br>
<span style="color:#111827">b. 그 핀들이 외부 회로와 연결되어 있을 수 있다.</span><br>
<br>
<span style="color:#1d4ed8">Q3. Connect under reset은 무슨 뜻인가?</span><br>
<span style="color:#111827">a. MCU를 reset 상태로 잡아둔 채 debugger를 연결한다는 뜻이다.</span><br>
<span style="color:#111827">b. Core가 instruction을 실행하기 전에 멈춰 있게 된다.</span><br>
<br>
<span style="color:#1d4ed8">Q4. 프로그래밍만으로 항상 충분하지 않은 이유는?</span><br>
<span style="color:#111827">a. 다음 reset 전에 empty check bit를 clear해야 할 수 있기 때문이다.</span><br>
<br>
<span style="color:#1d4ed8">Q5. STM32 bootloader 동작은 어떤 문서를 봐야 하나?</span><br>
<span style="color:#111827">a. AN2606, STM32 system memory boot mode application note를 확인한다.</span><br>

## 참고 자료

<span style="color:#1d4ed8">원본 영상</span><br>
<span style="color:#111827">STM32 boot and startup tips - Empty check mechanism</span><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=mBU9xHqw264">https://www.youtube.com/watch?v=mBU9xHqw264</a><br>
<br>
<span style="color:#1d4ed8">관련 문서</span><br>
<span style="color:#111827">AN2606 - STM32 microcontroller system memory boot mode</span><br>
<span style="color:#dc2626">※ STM32 family별 정확한 bootloader 동작은 AN2606에서 다시 확인</span><br>
