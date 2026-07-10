# 외부 세계를 어떻게 통제할까 — LED 블링크

**원본 강의:** [#4 외부 세계를 어떻게 통제할 수 있을까? (YouTube)](https://www.youtube.com/watch?v=1Kjh0CAgnl4)

이 강의는 "Modern Embedded Systems Programming" 코스의 4강이다. Stellaris LaunchPad 보드의 RGB LED를 깜빡이게 만든다. 단순한 "Hello World"처럼 보이지만, 실제로는 보드 매뉴얼·schematic으로 하드웨어 연결을 추적하고, 1200쪽짜리 datasheet에서 memory map을 찾고, clock gating으로 꺼진 주변장치를 깨우고, GPIO 레지스터들을 설정한 뒤, 1강의 pointer hack으로 그 모든 주소에 값을 쓰는 과정을 전부 거친다. 이 노트만 읽어도 강의를 따로 볼 필요 없도록 모든 주소·비트·절차를 담았다.

> 강사 코멘트: 별것 아닌 것처럼 보여도 LED를 깜빡이게 만든 것은 임베디드 커리어에서 매우 중요한 이정표(milestone)다.

---

## 1. 강의 목표와 LED 하드웨어 연결 구조

목표는 Stellaris LaunchPad 보드의 LED를 깜빡이는 것이다. 이 강의에서는 보드의 **User Manual**을 다운로드할 것을 강하게 권한다(클래스 노트 링크 참조). 보드가 없으면 시뮬레이터로 따라 할 수 있지만 디버거 뷰가 조금 다르고, 당연히 LED가 깜빡이는 것은 못 본다.

오늘 관심사는 보드 오른쪽 가장자리에 있는 **Red-Green-Blue User LED**다. 매뉴얼은 보드의 부품들이 마이크로컨트롤러에 어떻게 연결되는지 설명하는데, User LED는 **GPIO(General Purpose Input-Output, 범용 입출력)**에 연결돼 있다.

매뉴얼 끝에는 보드의 schematic(회로도)이 있다.

> **이미지 필요**
> 보드 schematic 발췌 — RGB User LED의 R/G/B 부품이 트랜지스터로 구동되고, 트랜지스터가 LED_R / LED_G / LED_B 출력으로 제어되며, 그 출력이 MCU 핀 F1 / F2 / F3에 연결되는 모습.
> - 출처: Stellaris LaunchPad User Manual schematic 1페이지 (강의 00:53~01:25)
> - 대체안: 강의 해당 구간 스크린샷 캡처, `cs/임베디드수업/images/4_led_schematic.png`로 저장

schematic에서 읽어낼 연결 구조:

- User LED의 R, G, B 부품은 각각 **트랜지스터(transistor)**로 전원을 받는다.
- 그 트랜지스터들은 출력 신호 **LED_R, LED_G, LED_B**로 각각 제어된다.
- 이 출력들은 회로도 위쪽에서 마이크로컨트롤러 핀 **F1, F2, F3**에 연결된다.
- 핀 이름의 문자 **F는 GPIO-F**를 뜻한다. 즉 LED는 GPIO-F 포트로 제어한다.

---

## 2. 프로젝트 준비

평소처럼 이전 3강 프로젝트를 복사해 `lesson4`로 이름을 바꾼다. (3강 프로젝트가 없으면 state-machine.com/quickstart에서 받는다.) `lesson4` 디렉터리 안의 workspace 파일을 더블클릭해 IAR 툴셋을 연다.

보드가 있다면 지금 PC에 연결하고 다음을 확인한다.

- 디버거가 **TI Stellaris 인터페이스**로 구성돼 있을 것.
- Download 탭에 **"Use flash loader"** 옵션이 체크돼 있을 것.
- **TI Stellaris 메뉴**에서 **"Reset will do system reset"** 옵션을 체크 — 보드가 항상 깨끗한 리셋 상태에서 시작하도록.

보드가 없으면 디버거를 Simulator로 구성하고 따라 한다.

> **주의**
> 프로젝트를 **전체 다시 빌드(rebuild entirely)**한다. 그렇게 하지 않으면 IAR이 이전 3강 프로젝트의 `main.c` 파일을 끌어다 쓸 수 있다.

---

## 3. 주소 공간 복습 — Flash와 RAM

디버거에서 프로세서가 여러 주소를 어떻게 쓰는지 빠르게 복습한다.

- **0부터 시작하는 낮은 주소**에는 machine instruction이 있다. 이건 우리 프로그램의 컴파일된 코드이고, 마이크로컨트롤러 안에 **영구적으로** 저장된다. → 즉 **0부터 시작하는 낮은 주소는 Flash 메모리에 매핑**된다.
- **`0x2`로 시작하는 주소**는 `counter` 같은 변수에 쓰인다. → 즉 **`0x20000000`이 RAM(Random Access Memory)의 시작**을 표시한다.
- RAM 시작 바로 앞 주소들에는 "구멍(hole)"이 보인다 — 디버거가 그 주소에서 아무것도 못 읽었다는 뜻이고, 십중팔구 사용되지 않는 영역이라서다.
- 더 탐색하면 주소 **`0x20008000`**에서 RAM이 끝난다 → RAM은 **`0x8000`개의 주소만큼 뻗은 "섬(island)"**이며, `0x8000`은 10진수로 **32KB**다. → 이 마이크로컨트롤러는 **32KB RAM**을 갖는다.

이 정도가 현재 주소에 대해 아는 전부다. LED를 깜빡이려면 주소 공간의 모든 "대륙과 섬"의 지도 — 즉 **memory map**을 알아야 한다.

---

## 4. datasheet과 memory map 읽는 법

마이크로컨트롤러의 memory map을 (그리고 그 외 많은 것을 끔찍하게 상세히) 기술한 문서를 **datasheet(데이터시트)**라 한다. LaunchPad 보드의 특정 LM4F 마이크로컨트롤러 datasheet를 다운로드할 것을 강하게 권한다.

> 미리 경고: datasheet는 거대한 경향이 있다. 이 LM4F datasheet는 **1200쪽이 넘는데**, datasheet 치고는 그래도 상대적으로 짧은 편이다. 다행히 이런 문서는 처음부터 끝까지 통독하라고 만든 게 아니다. **사실 임베디드 시스템 엔지니어 일의 큰 부분은 datasheet 안에서 길을 찾아 필요한 정보를 빠르게 찾아내는 법을 아는 것이다.**

memory map을 찾으려면 datasheet에서 문자열 **"memory map"**을 검색하면 된다.

> **이미지 필요**
> LM4F 마이크로컨트롤러의 memory map — on-chip flash, bit-banded on-chip SRAM, Peripherals 영역(GPIO 포트 포함)이 0~0xFFFFFFFF의 선형 주소 공간에 배치된 그림.
> - 출처: LM4F datasheet "memory map" 섹션 (강의 05:16~06:30)
> - 대체안: 강의 해당 구간 스크린샷 캡처, `cs/임베디드수업/images/4_memory_map.png`로 저장

memory map에서 읽어낼 것:

- 전형적인 현대 ARM Cortex-M 마이크로컨트롤러의 memory map은 segment나 memory bank가 전혀 없는 **아주 깔끔하고 단순한 선형(linear) 주소 공간**이다. (옛날 8비트 마이크로컨트롤러를 다뤄봤다면 이 **선형 32비트 주소 공간**의 단순함을 고맙게 느낄 것이다.)
- 첫 "섬"은 **on-chip flash** — 주소 **0부터 `0x3FFFF`**까지로 **256KB flash 메모리**에 해당한다.
- RAM 섬은 **`0x20000000`**에서 시작하며 여기서는 **"Bit-banded on-chip S-RAM"**이라 명명돼 있다. S-RAM은 **Static-RAM**의 약자다.
- **Peripherals(주변장치) "대륙"**에는 **GPIO 포트**들이 있다. LED를 제어하려면 **"GPIO Port F"**를 찾는다. memory map을 따라 내려가면 GPIO Port-F가 나온다 — 그 시작 주소를 복사한다.

---

## 5. clock gating — GPIO-F가 꺼져 있는 이유

GPIO-F의 시작 주소를 IAR 디버거의 memory 뷰에 붙여넣고 무엇이 뜨는지 본다. 그런데 datasheet가 광고한 GPIO-F의 주소 범위가 **비어 있는 것처럼 보인다.**

이런 일이 생겨도 절망하지 말 것. **전형적인 이유는 그 하드웨어 블록이 전력 절약을 위해 기본적으로 꺼져 있기 때문**이다.

> **clock gating(클럭 게이팅):** 칩의 특정 부분으로 가는 **클럭 신호를 차단하는 기법**. 현대 마이크로컨트롤러에서 매우 흔한 관행이다. 회로는 클럭이 공급돼야 동작하므로, 클럭을 끊으면 그 블록은 전력을 거의 쓰지 않고 잠든 상태가 된다.

따라서 먼저 GPIO-F 블록을 **켜는 법**을 알아내야 하고, 그러려면 datasheet로 돌아가야 한다.

---

## 6. clock-gating 레지스터로 GPIO-F 깨우기

datasheet 처음으로 돌아가 문자열 **"clock gating"**을 검색한다. 그 섹션 안에서 다시 **"GPIO"**를 검색하면 **GPIO Clock Gating Control 레지스터**가 나온다.

이 레지스터 설명을 자세히 본다 — datasheet에서 흔히 쓰는 매우 전형적인 형식이기 때문이다.

> **이미지 필요**
> datasheet의 레지스터 설명 형식 — 0번부터 번호가 매겨진 비트 블록 그림, 각 비트의 타입(RO/RW/WO) 표시, 그 아래 MSB부터 나열된 비트 그룹 설명. bit 5가 GPIO Port F 클럭 활성화임을 강조.
> - 출처: LM4F datasheet GPIO Clock Gating Control 레지스터 섹션 (강의 07:27~08:23)
> - 대체안: 강의 해당 구간 스크린샷 캡처, `cs/임베디드수업/images/4_register_description.png`로 저장

datasheet 레지스터 설명 형식 읽는 법:

- 레지스터는 **비트 블록**으로 그려지며, 비트는 **항상 0번부터** 번호가 매겨진다.
- 각 비트의 **타입**이 표시된다 — **RO = Read-Only**(읽기 전용), **R/W = Read-Write**(읽기·쓰기), **WO = Write-Only**(쓰기 전용).
- 논리적으로 관련된 비트 그룹은 레지스터 블록 그림 **아래에 MSB(최상위 비트)부터** 문서화된다.
- 우리에게 가장 흥미로운 것은 **bit 5의 설명** — 이 비트가 **GPIO Port F로 가는 클럭을 활성화**한다. 우리가 찾던 레지스터가 맞다.

레지스터의 **base address**를 복사하되, 완전한 레지스터 주소를 얻으려면 추가 **offset `0x608`**을 base에 더해야 한다는 점에 유의한다. (LM4F 시스템 컨트롤 base `0x400FE000` + offset `0x608` = `0x400FE608`.)

디버거에서 **Symbolic Memory**라는 추가 메모리 뷰를 열고, datasheet의 clock-gating 레지스터 base address를 붙여넣은 뒤 offset `0x608`을 더한다. 강조 표시된 clock-gating 레지스터 값을 편집해 **bit 5를 set**한다. 1강(숫자 세기)에서 배운 대로 bit 5만 켜진 값은 16진수 **`0x20`**이다. 엔터를 치면 — **GPIO-F 하드웨어 블록이 깨어난다.** (원래 memory 뷰에서 GPIO-F 시작 주소가 깨어나는 것을 동시에 지켜볼 수 있다.)

---

## 7. GPIO-F 핀 설정 — direction과 digital function

GPIO-F 블록을 깨웠지만 아직 LED를 깜빡일 수는 없다. datasheet의 GPIO 섹션을 읽어보면, **GPIO-F의 bit 1, 2, 3을 디지털 출력(digital output)으로 설정**해야 한다. 이 비트들이 각각 핀 F1, F2, F3 — 즉 LED의 세 색을 구동한다.

두 개의 레지스터를 설정한다(주소는 모두 GPIO-F 주소 블록 안에 있다).

1. **핀 방향(direction) 레지스터 — `0x40025400`:** bit 1, 2, 3을 1로 set → 핀을 출력으로. bit 1,2,3이 1이고 bit 0이 0이면 2진수 **`1110`**, 16진수 **`E`**다.
2. **디지털 기능(digital function) 레지스터 — `0x4002551C`:** 다시 bit 1, 2, 3을 1로 set → 핀의 기능을 디지털 출력으로.

---

## 8. LED 제어 — Data register에 값 쓰기

이제 LED를 제어할 수 있다. 제어는 **`0x400253FC`에 있는 GPIO-F Data 레지스터**를 통해 한다. 비트는 항상 0번부터 센다는 점을 기억하면서 실험한다.

- **bit 1만 set** — 최하위 nibble에 16진수 **`2`** 쓰기 → **빨강(red) LED가 켜진다.**
- **`0` 쓰기** → LED가 꺼진다.
- **bit 2 set** — 16진수 **`4`** 쓰기 → LED가 **파랑(blue)**으로 바뀐다.
- **bit 3 set** — 16진수 **`8`** 쓰기 → 세 번째 색도 제어된다.

> 핵심 통찰: **LED를 제어하는 일의 전부는 결국 특정 메모리 주소에 숫자를 쓰는 것**으로 귀결된다. 그리고 특정 주소에 숫자를 쓰는 법은 **pointer(포인터)**로 이미 알고 있다. 힘든 일(heavy-lifting)은 사실상 끝났고, 이걸 C로 코딩하는 것은 식은 죽 먹기다.

---

## 9. C 코드로 옮기기 — pointer hack

3강 끝에서 보여준 **pointer hack**을 쓴다. 이 기법은 우리가 고른 **어떤 메모리 주소에든 어떤 숫자든 쓸 수 있게** 해 준다.

- 코드를 정리해 pointer 관련 부분만 남긴다. 사실 **별도의 pointer 변수조차 필요 없다** — pointer-cast를 곧바로 역참조(de-reference)할 수 있기 때문이다.
- 3강에서는 `int`에 대한 포인터를 썼다. 하지만 **ARM 레지스터는 unsigned**이므로 포인터 타입을 **`unsigned int`**로 바꾼다.
- 3강의 지어낸(fabricated) 주소를, GPIO-F 블록을 켤 때 쓴 clock-gating 시스템 레지스터의 주소로 교체한다.
- pointer cast 전체를 괄호로 감싼다. 이 전체가 **`unsigned int`에 대한 포인터**다. 그렇다면 별표(`*`) 연산자로 이 포인터를 **역참조**할 수 있다.
- 이제 포인터에 값을 쓴다. 디버거 실험에서 봤듯 이 레지스터에는 **bit 5, 즉 16진수 `0x20`**을 set해야 한다. 값이 unsigned임은 **`U` 접미사**로 표시한다.
- 더 이상 안 쓰는 `p_int` 포인터는 제거하고, F7로 컴파일러가 코드를 받아들이는지 확인한다.

```c
int main() {
    /* clock-gating 레지스터(base + offset 0x608)에 bit 5 set → GPIO-F 블록 켜기 */
    *((unsigned int *)0x400FE608U) = 0x20U;

    /* GPIO-F 핀 방향 레지스터: bit 1,2,3을 출력으로 → 0xE */
    *((unsigned int *)0x40025400U) = 0xEU;

    /* GPIO-F 디지털 기능 레지스터: bit 1,2,3 활성화 */
    *((unsigned int *)0x4002551CU) = 0xEU;

    while (1) {  /* 조건 자리에 상수 1 → 항상 참 → 영원히 반복 */
        /* 빨강 LED 켜기: data register의 bit 1 set */
        *((unsigned int *)0x400253FCU) = 0x2U;
        /* 빨강 LED 끄기: bit 1 clear */
        *((unsigned int *)0x400253FCU) = 0x0U;
    }
    return 0;  /* 끝없는 while 아래라 도달 불가 — 컴파일러 warning */
}
```

같은 방식으로 나머지 레지스터도 처리한다 — GPIO-F 핀 방향 레지스터에 bit 1,2,3 set(`0xE` 쓰기), 디지털 기능 레지스터에도 bit 1,2,3 set. 이게 끝나면 GPIO-F data 레지스터의 **bit 1을 set/clear**해서 빨강 LED를 켜고 끌 수 있다.

---

## 10. 무한 루프와 delay — LED를 실제로 깜빡이기

LED를 한 번 켜고 끄는 것으로는 "깜빡임"이 아니다. 정말 깜빡이려면 이걸 **영원히** 반복해야 한다. LED를 켜고 끄는 코드를 `while` 루프로 감싼다. **조건 자리에 상수 `1`을 두면 조건이 항상 참**이므로 루프가 영원히 돈다.

이 코드를 컴파일하면 **끝없는 `while` 아래의 `return` 문이 도달 불가능(unreachable)하다는 warning**이 뜬다 — 맞는 말이다.

보드에서 테스트하면: clock-gating 레지스터 설정이 GPIO-F 블록을 깨우고, 빨강 LED가 켜졌다 꺼지고, 끝없는 루프도 동작하는 듯하다. 그런데 **Go 버튼으로 전속력(full speed) 실행**하면 — **LED가 계속 켜진 채로 있다.**

Break 버튼으로 코드에 끼어들어 다시 single-step 하면 멀쩡하다. 전속력으로 돌리면 깜빡임이 멈추는 이유는?

> 정답: **프로그램이 사람 눈으로 LED의 빠른 깜빡임을 알아챌 수 없을 만큼 너무 빨리 돈다.** 프로그램을 느리게 만들어야 한다.

이를 위해 2강에서 배운 **카운팅 `while` 루프**를 delay로 쓴다. 이런 루프는 CPU 사이클을 많이 낭비하지만, **`while` 조건의 상한값을 설정해 지연 시간을 제어**할 수 있다. **LED를 켠 뒤와 끈 뒤 양쪽 모두에 delay**가 필요하다.

```c
unsigned int counter;

while (1) {
    *((unsigned int *)0x400253FCU) = 0x2U;   /* LED 켜기 */
    counter = 0;                              /* 켠 뒤 delay */
    while (counter < 500000U) { ++counter; }

    *((unsigned int *)0x400253FCU) = 0x0U;   /* LED 끄기 */
    counter = 0;                              /* 끈 뒤 delay */
    while (counter < 500000U) { ++counter; }
}
```

> 다음 강의에서는 이 blinky 프로그램을 **C preprocessor**와 **`volatile` 키워드**로 개선하는 법을 배운다.

---

## 참고 자료

- [#4 외부 세계를 어떻게 통제할 수 있을까? (YouTube)](https://www.youtube.com/watch?v=1Kjh0CAgnl4)
- [state-machine.com/quickstart](https://state-machine.com/quickstart) — 클래스 노트, 보드 User Manual, datasheet, 프로젝트 파일 다운로드
- Stellaris LaunchPad User Manual — 보드 부품 연결, schematic
- LM4F 마이크로컨트롤러 datasheet (1200쪽+) — memory map, clock-gating 레지스터, GPIO 레지스터
- 관련 노트: [1강 — 16진법](./1_컴퓨터는_어떻게_숫자를_센다.md), [2강 — 카운팅 while 루프](./2_제어흐름_바꾸기_loop와_if.md), [8강 — MCU 메모리 맵과 MMIO](./8_MCU_메모리맵과_MMIO.md)

**주요 주소 정리**

| 레지스터 | 주소 | 설정 값 | 역할 |
|----------|------|---------|------|
| Clock Gating Control | `0x400FE608` (base + offset `0x608`) | `0x20` (bit 5) | GPIO-F 클럭 켜기 |
| GPIO-F 핀 방향(direction) | `0x40025400` | `0xE` (bit 1,2,3) | 핀을 출력으로 |
| GPIO-F 디지털 기능 | `0x4002551C` | `0xE` (bit 1,2,3) | 디지털 출력 기능 활성화 |
| GPIO-F Data | `0x400253FC` | `0x2`/`0x4`/`0x8` | LED 색 켜고 끄기 |

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

주제: **clock gating — 주변장치가 처음엔 비어 있는 이유**

- **한 줄 정의:** clock gating은 칩의 특정 블록으로 가는 클럭 신호를 차단해 그 블록을 잠재우는 전력 절약 기법이다.
- **왜 필요:** 마이크로컨트롤러는 GPIO·타이머·통신 등 많은 주변장치를 갖지만, 어떤 응용이든 그중 일부만 쓴다. 안 쓰는 블록에 클럭을 계속 공급하면 전력만 낭비된다. 그래서 대부분의 주변장치는 기본적으로 클럭이 꺼진 채 부팅된다.
- **동작:** 디지털 회로는 클럭이 토글돼야 상태가 바뀌므로, 클럭을 끊으면 그 블록은 거의 전력을 쓰지 않고 멈춘다. datasheet의 clock-gating 제어 레지스터에서 해당 블록의 enable 비트를 set 하면 클럭이 공급되어 블록이 깨어난다. 깨우기 전에는 그 주변장치의 레지스터를 읽어도 비어 있는 것처럼 보인다.
- **비교:** 일반 메모리(Flash·RAM)는 주소만 알면 바로 접근되지만, 주변장치는 datasheet에 광고된 주소에 있더라도 clock gating으로 꺼져 있어 먼저 클럭을 켜야 접근된다. GPIO를 쓰려면 클럭 enable → 핀 방향 설정 → 디지털 기능 활성화 → data 레지스터 쓰기 순서를 거쳐야 한다.
- **30초 통합 답변:**
  > clock gating은 칩의 특정 블록으로 가는 클럭 신호를 차단해서 그 블록을 잠재우는 전력 절약 기법입니다. 마이크로컨트롤러는 GPIO, 타이머, 통신 같은 주변장치를 잔뜩 갖고 있지만 어떤 응용이든 그중 일부만 쓰기 때문에, 안 쓰는 블록에 클럭을 계속 주면 전력만 낭비됩니다. 그래서 대부분의 주변장치는 기본적으로 클럭이 꺼진 채 부팅됩니다. 디지털 회로는 클럭이 토글돼야 동작하므로 클럭을 끊으면 거의 전력을 안 쓰고 멈추는데, datasheet의 clock-gating 제어 레지스터에서 그 블록의 enable 비트를 set 하면 클럭이 다시 공급되어 깨어납니다. 그래서 GPIO를 처음 들여다보면 datasheet에 적힌 주소인데도 레지스터가 비어 보이고, 클럭을 켜야 비로소 접근됩니다. GPIO를 실제로 쓰려면 클럭 enable, 핀 방향 출력 설정, 디지털 기능 활성화, 그리고 data 레지스터 쓰기 순서를 모두 거쳐야 합니다.
