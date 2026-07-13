# C 프로그램의 메모리 레이아웃

**원본 강의:** [The Memory Layout of a C Program | Data Structures in Embedded Systems (YouTube)](https://www.youtube.com/watch?v=FlkNgJXEyrc)

C 소스 파일은 컴파일·어셈블·링크를 거쳐 실행 파일이 되고, 실행 시 코드와 데이터가 목적에 따라 나뉜 메모리 영역에 배치된다. 이 노트의 핵심은 **값 자체가 어디에 놓이는지**와 **포인터 변수와 그 포인터가 가리키는 동적 메모리가 서로 다른 영역에 놓일 수 있다**는 점이다.

> **주의**
> `.text`, `.data`, `.bss`, heap, stack은 C 언어 표준이 강제하는 메모리 주소 배치가 아니라 흔히 쓰는 실행 환경과 링커의 모델이다. PC 운영체제에서는 프로세스의 가상 주소 공간으로, MCU에서는 linker script가 정한 Flash·SRAM 영역으로 나타난다. 따라서 실제 주소와 방향은 target의 map file·linker script·datasheet로 확인한다.

---

## 1. 소스 코드에서 실행 중 메모리까지

```text
main.c ──컴파일/어셈블/링크──> 실행 이미지 ──로더 또는 reset──> 실행 중 메모리
```

링커는 여러 object file과 library를 결합하면서 코드와 전역 데이터를 section으로 나눈다. 프로그램이 실행되면 지역 변수와 함수 호출 정보는 실행 흐름에 따라 stack에 생기고, `malloc()`을 호출한 경우에만 heap 블록이 생긴다. 즉 **stack과 heap은 실행 파일에 들어 있는 고정 데이터 자체라기보다 실행 중 관리되는 영역**이다.

일반적인 개념도는 다음과 같다. 주소의 높고 낮음·성장 방향은 일반적인 설명일 뿐 절대 규칙이 아니다.

```text
낮은 주소
┌─────────────────────────────────────┐
│ .text / .rodata : 기계어 코드, 상수 │
├─────────────────────────────────────┤
│ .data           : 초기값 있는 전역·static │
├─────────────────────────────────────┤
│ .bss            : 초기값 없는 전역·static │
├─────────────────────────────────────┤
│ heap             : 동적 할당 블록   │  ↑ (흔한 배치)
│                 ...                 │
│ stack            : 호출 프레임      │  ↓ (흔한 배치)
└─────────────────────────────────────┘
높은 주소
```

---

## 2. `.text`와 읽기 전용 데이터

`.text`에는 CPU가 실행할 기계어 코드가 들어간다. PC의 운영체제 환경에서는 같은 프로그램을 여러 프로세스가 실행할 때 읽기 전용 코드 페이지를 공유할 수 있어 메모리를 절약하기도 한다.

문자열 리터럴이나 `const` 객체는 toolchain에 따라 `.rodata` 같은 읽기 전용 section에 들어갈 수 있다.

```c
const char banner[] = "READY";

int add(int a, int b)
{
    return a + b;  /* 함수의 명령어는 보통 .text */
}
```

MCU에서는 `.text`와 `.rodata`의 초기 이미지가 보통 Flash에 있고 CPU가 그곳에서 직접 실행한다. 반면 PC에서는 운영체제가 실행 파일을 가상 메모리에 매핑한다. 어느 쪽이든 “코드는 데이터와 달리 임의로 쓰면 안 되는 영역”이라는 구분이 중요하다.

---

## 3. `.data`와 `.bss` — 전역·`static` 객체의 두 갈래

파일 범위 전역 변수와 `static` 저장 기간을 가진 변수는 프로그램 전체 수명 동안 존재한다. 초기값 유무에 따라 보통 다음처럼 나뉜다.

```c
int configured_speed = 115200;  /* .data: 초기값이 있음 */
static int sample_count;        /* .bss: 초기값이 없지만 0으로 초기화 */
static int enabled = 0;         /* 보통 .bss: 0 초기값 */
```

| 영역 | 들어가는 대표 대상 | 시작할 때 해야 할 일 |
| --- | --- | --- |
| `.data` | 0이 아닌 초기값을 가진 전역·`static` 객체 | 초기값을 RAM에서 써야 함 |
| `.bss` | 초기화하지 않았거나 0으로 초기화한 전역·`static` 객체 | 0으로 채워야 함 |

임베디드 startup code는 reset 직후 Flash에 저장된 `.data`의 초기값을 SRAM으로 복사하고, `.bss`를 0으로 채운 다음 `main()`을 호출하는 경우가 일반적이다. 그래서 `.bss`의 크기는 SRAM 사용량에는 영향을 주지만, 초기값 바이트를 Flash에 따로 저장할 필요는 없다.

> **예외**
> `const`, 최적화, 특수 section attribute, zero-initialized object의 정확한 section 이름은 toolchain마다 달라질 수 있다. 최종 판단은 빌드 결과의 `.map` 파일이다.

---

## 4. stack — 함수 호출마다 생기는 자동 저장 공간

stack은 함수의 지역 변수, 매개변수 전달 정보, 복귀 주소처럼 **함수 호출에 묶인 상태**를 관리한다. 함수가 반환되면 해당 호출 프레임은 자동으로 사라진다.

```c
int sum(int left, int right)
{
    int result = left + right;
    return result;
}
```

위 함수에서 `left`, `right`, `result`는 보통 stack 또는 CPU 레지스터로 구현된다. 최적화 수준과 ABI에 따라 실제 배치는 달라질 수 있지만, C의 관점에서는 `sum()` 호출이 끝난 후 이 자동 변수에 접근하면 안 된다.

재귀가 너무 깊거나 큰 지역 배열을 만들면 stack을 넘칠 수 있다. MCU는 stack 크기가 작고 다른 RAM 영역과 경계를 공유하므로, stack overflow가 곧바로 메모리 훼손·HardFault·예측 불가능한 오동작으로 이어질 수 있다.

---

## 5. heap — 수명이 호출 범위를 넘어가는 동적 메모리

heap은 `malloc()`·`calloc()`·`realloc()` 같은 동적 할당 함수가 요청한 블록을 제공하는 영역이다. block의 수명은 함수 호출이 아니라 **`free()`를 호출할 때까지**다.

```c
void read_packet(void)
{
    size_t bytes = 64;
    unsigned char *packet = malloc(bytes);

    if (packet == NULL) {
        return;                 /* 할당 실패 처리 */
    }

    /* packet[0..63] 사용 */
    free(packet);               /* 책임을 다한 뒤 정확히 한 번 해제 */
}
```

`packet`이라는 **포인터 변수 자체**는 `read_packet()`의 지역 변수이므로 보통 stack에 있다. 반면 `packet`이 가리키는 64바이트 block은 heap에 있다. 포인터가 사라져도 `free()`하지 않으면 heap block은 남아 memory leak이 된다. 반대로 `free()` 뒤 포인터를 계속 쓰면 dangling pointer가 된다.

> **주의**
> heap과 stack이 서로 마주 보게 성장하는 그림은 이해를 돕는 전형적인 모델이다. 현대 OS의 가상 메모리와 MCU의 linker script는 이보다 복잡할 수 있다. “둘이 충돌하면 항상 segmentation fault가 난다”라고 단정하지 말고, target의 실제 메모리 보호·fault 동작을 확인한다.

---

## 6. 한 코드로 배치 추적하기

```c
int global_ready = 1;       /* .data */
static int global_errors;   /* .bss */

void process(int input)     /* 함수 명령어: .text */
{
    int local = input;      /* 자동 변수: stack 또는 레지스터 */
    static int runs = 1;    /* .data, 호출이 끝나도 유지 */
    int *dynamic = malloc(8 * sizeof *dynamic);

    if (dynamic != NULL) {
        dynamic[0] = local; /* dynamic가 가리키는 배열: heap */
        free(dynamic);
    }

    runs++;
}
```

이 코드를 읽을 때는 변수 이름이 아니라 **저장 기간(storage duration)**을 기준으로 판단한다.

- 함수 밖 변수와 함수 안 `static` 변수: static storage duration → `.data` 또는 `.bss`
- 일반 지역 변수와 매개변수: automatic storage duration → 호출 중 stack/레지스터
- `malloc()` 반환 포인터가 가리키는 대상: allocated storage duration → heap, `free()`까지 유지
- 함수 본문에서 실행할 명령어: `.text`

---

## 7. MCU에서 이어서 확인할 것

PC에서 배운 레이아웃을 MCU에 옮길 때는 “프로세스 하나의 가상 공간” 대신 **물리 Flash와 SRAM의 예산**으로 바꿔 생각한다.

- `.text`·`.rodata`·`.data`의 초기값은 대개 Flash 용량을 쓴다.
- 실행 중 `.data`·`.bss`·stack·heap은 대개 SRAM 용량을 쓴다.
- `.data`는 초기값을 Flash에 보관하면서 실행 중에는 SRAM에도 놓이는 경우가 많다.
- `uint32_t`처럼 폭이 고정된 타입을 사용하면 레지스터 폭과 통신 데이터 크기를 더 명확하게 표현할 수 있다.
- 빌드 뒤 map file에서 section 크기, stack/heap 예약 크기, 남은 SRAM을 확인한다.

heap이 정말 필요한지와 실시간 제약에서 어떻게 제한해야 하는지는 [실시간 시스템에서 `malloc` 사용 원칙](./실시간_시스템에서_malloc_사용_원칙.md)에서 이어서 다룬다.

---

## 참고 자료

- [The Memory Layout of a C Program | Data Structures in Embedded Systems (YouTube)](https://www.youtube.com/watch?v=FlkNgJXEyrc)
- [전역 변수와 static 변수](./전역변수와_static.md) — `.data`·`.bss`와 linkage 복습
- [`sizeof`와 포인터 메모리 크기](./sizeof와_포인터_메모리_크기.md) — 포인터 자체와 heap block의 크기 구분
- [MCU Memory Map & Memory Mapped I/O](../cs/임베디드수업/8_MCU_메모리맵과_MMIO.md) — MCU 주소 공간·Flash·SRAM 연결

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** C 프로그램 메모리 레이아웃은 코드·정적 데이터·동적 데이터·호출 상태를 수명과 용도에 따라 `.text`, `.data`, `.bss`, heap, stack으로 나누어 배치하는 모델이다.
- **왜 필요:** 변수의 수명과 RAM·Flash 사용량을 이해해야 memory leak, dangling pointer, stack overflow를 예방하고 MCU의 제한된 메모리를 예측할 수 있다.
- **동작:** 초기값 있는 전역·`static` 변수는 보통 `.data`, 초기값 없는 전역·`static` 변수는 `.bss`에 놓인다. 지역 변수와 함수 호출 정보는 stack에 자동으로 생기고, `malloc()`으로 잡은 block은 heap에 남아 `free()`할 때까지 유지된다.
- **비교:** stack은 함수 반환과 함께 자동으로 해제되지만 heap은 programmer가 직접 해제한다. `.data`와 `.bss`는 모두 프로그램 전체 수명을 가지지만 `.data`는 초기값 이미지가 필요하고 `.bss`는 시작 시 0으로 초기화된다.
- **30초 통합 답변:**
  > C 프로그램의 메모리 레이아웃은 저장 기간을 기준으로 코드와 데이터를 나누는 모델입니다. 실행 명령어는 보통 `.text`에, 초기값 있는 전역·static 변수는 `.data`에, 초기값 없는 전역·static 변수는 `.bss`에 들어갑니다. 지역 변수와 함수 복귀 정보는 stack에 자동으로 생기고 함수가 끝나면 사라집니다. 반면 `malloc`으로 얻은 heap block은 `free`할 때까지 남으므로 누수와 단편화를 관리해야 합니다. MCU에서는 map file로 이 영역들의 Flash·SRAM 사용량을 함께 확인합니다.
