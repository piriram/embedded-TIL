# 실시간 시스템에서 `malloc` 사용 원칙

**원본 강의:** [Why you Should NEVER Use Malloc in Real-Time Systems (YouTube)](https://www.youtube.com/watch?v=0DXU6pYKkEk)

제목의 “NEVER”는 경계심을 주기 위한 표현이다. 실무의 정확한 원칙은 **실시간 경로에서 일반적인 동적 할당을 무심코 사용하지 말고, 필요하다면 할당 시점·최대 사용량·실패 처리·실행 시간을 통제하라**이다. 특히 장시간 꺼지지 않는 임베디드 시스템에서는 한 번의 누수나 단편화가 나중의 할당 실패로 나타날 수 있다.

---

## 1. `malloc()`이 제공하는 것과 실시간 코드의 요구

`malloc(size)`은 heap에서 최소 `size`바이트를 연속으로 쓸 수 있는 block을 찾아 그 시작 주소를 반환한다. 실패하면 `NULL`을 반환한다. C 언어 차원에서 `malloc()`은 편리하지만, 아래 항목을 실시간 deadline에 맞춰 보장해 주지는 않는다.

- 정확히 얼마나 오래 걸리는가
- 어느 주소의 block을 선택하는가
- 장시간 실행 뒤에도 큰 연속 block이 남아 있는가
- 실패했을 때 시스템이 안전한 상태로 계속 동작하는가

real-time은 단순히 “빠른” 것이 아니라 **정해진 시간 안에 끝난다는 예측 가능성(determinism)**이 핵심이다. ISR이나 deadline이 촘촘한 control loop에서 할당기 내부 탐색·lock·cache miss에 걸리는 시간까지 deadline 예산에 넣기 어렵다면, 그 경로에서는 `malloc()`을 피하는 편이 안전하다.

---

## 2. 장시간 실행에서 생기는 세 가지 위험

### memory leak

할당한 block의 마지막 소유자가 `free()`하지 않으면 그 block은 다시 쓸 수 없다. 누수는 짧은 테스트에서 보이지 않다가 장시간 동작 후 heap을 소진해 allocation failure로 나타난다.

```c
uint8_t *buffer = malloc(128);

if (buffer == NULL) {
    return ERROR_NO_MEMORY;
}

/* buffer 사용 */
free(buffer);      /* 모든 정상·오류 경로에서 해제 책임을 분명히 한다 */
```

“마지막에 free한다”만으로는 충분하지 않다. 소유권이 task·함수·queue 사이를 이동한다면 **누가, 어떤 완료·오류·취소 경로에서, 정확히 한 번 해제하는지**를 API 계약에 적어야 한다.

### fragmentation

다양한 크기의 block을 할당·해제하면 free space가 작은 조각으로 흩어질 수 있다. 전체 여유 RAM의 합은 충분해도 요청한 크기의 **연속된 block**이 없으면 `malloc()`은 `NULL`을 반환한다.

```text
처음:    [사용 32][사용 64][사용 32]
해제 후: [사용 32][빈칸 64][사용 32]
요청:    80 bytes  → 전체 여유가 있어도 연속 80 bytes가 없어 실패 가능
```

모든 block을 성실히 `free()`하더라도 fragmentation은 생길 수 있다. 따라서 leak을 고쳤다는 사실이 heap 위험을 모두 없애지는 않는다.

### 비결정적 실행 시간과 캐시 효과

일반 allocator는 적합한 free block을 찾고 metadata를 갱신하며, multi-thread 환경에서는 내부 동기화를 할 수도 있다. heap 상태에 따라 실행 시간이 달라질 수 있고, 선택된 주소가 cache locality에도 영향을 준다. 영상은 hardware별 cache line과 access time이 다르므로, 성능이 아주 민감하면 allocator까지 target 특성에 맞춰야 한다고 설명한다.

> **주의**
> cache를 의식한 custom allocator가 항상 더 빠르거나 더 안전한 것은 아니다. 직접 만든 allocator도 경계 검사, 동시성, 정렬, 누수, failure policy를 검증해야 한다. 요구사항 없이 일반 `malloc`을 custom code로 바꾸는 것은 해결책이 아니다.

---

## 3. 피해야 할 위치와 허용할 수 있는 위치

| 위치 | 권장 판단 | 이유 |
| --- | --- | --- |
| ISR | 사용하지 않음 | 지연 시간이 길어질 수 있고, allocator의 thread/interrupt safety를 보장하기 어렵다. |
| 주기 제어 loop·hard deadline 경로 | 기본적으로 사용하지 않음 | 실행 시간과 실패가 deadline을 깨거나 기능을 멈출 수 있다. |
| 시스템 초기화 단계 | 조건부 허용 | 실행 전 한 번만 할당하고 최대량·실패 처리를 검증할 수 있다. |
| non-real-time task | 조건부 허용 | heap budget, 최대 block 크기, failure 대응, 동시성 정책을 명시한다. |

초기화 단계에서 필요한 buffer를 모두 할당한 뒤, 운용 단계에서는 추가 할당과 해제를 하지 않는 방식은 runtime fragmentation 위험을 크게 줄인다. 다만 초기화 실패 시의 안전 동작과 전체 RAM 예산은 여전히 검증해야 한다.

---

## 4. 통제 가능한 대안

### 정적 할당

크기와 개수가 고정이면 가장 단순하다. 배열을 정적으로 확보하고 사용 중에는 주소만 빌려 준다.

```c
enum { RX_BUFFER_COUNT = 4, RX_BUFFER_SIZE = 128 };
static uint8_t rx_buffers[RX_BUFFER_COUNT][RX_BUFFER_SIZE];
```

장점은 메모리 사용량과 주소가 빌드 시점에 보인다는 점이다. 단점은 실제 사용량보다 크게 예약하면 RAM이 낭비되고, 더 큰 요청을 처리할 유연성이 없다는 점이다.

### 고정 크기 memory pool

동일 크기의 message·packet·event를 자주 만들면 block 크기와 개수를 정한 pool을 사용한다. 할당은 빈 block 하나를 꺼내고, 반납은 그 block을 다시 넣는 동작이므로 일반 heap보다 시간 상한과 fragmentation을 관리하기 쉽다.

pool 설계에서 반드시 정할 항목은 다음과 같다.

- block 크기와 총 개수, 최악 동시 사용량
- pool이 비었을 때의 정책: drop, back-pressure, 재시도, safe state
- task/ISR 동시 접근 보호 방식
- double free·반납하지 않은 block을 찾는 debug 방법

### arena 또는 startup-only allocation

초기화 때만 여러 객체를 만들고 운용 중 개별 해제가 필요 없다면, 큰 고정 buffer에서 앞쪽부터만 떼어 쓰는 arena를 사용할 수 있다. reset 또는 subsystem 재초기화 때 전체를 한꺼번에 되돌리는 방식이라 fragmentation을 만들지 않는다. 반대로 객체별 수명이 제각각이면 arena는 맞지 않는다.

---

## 5. FreeRTOS와 연결하기

FreeRTOS에서 task, queue, semaphore 같은 kernel object도 heap을 사용할 수 있다. `heap_1`부터 `heap_5`까지의 scheme은 해제 가능 여부와 fragmentation 처리 방식이 다르며, static allocation도 선택할 수 있다.

- 일반 C `malloc/free` 대신 RTOS가 제공하는 allocation API를 사용할지 정한다.
- allocation 반환값을 항상 확인한다.
- task stack 여유와 전체 free heap을 측정한다.
- critical application에서는 dynamic allocation을 금지하거나 초기화 단계·고정 pool로 한정한다.

구체적인 FreeRTOS API와 `heap_1`~`heap_5`, stack watermark는 [RTOS 메모리 관리](../cs/RTOS/4_메모리_관리.md)를 참고한다.

---

## 6. 코드 리뷰 체크리스트

- `malloc/calloc/realloc/free` 호출이 ISR, callback, deadline 경로에 있는가?
- 모든 allocation failure에 `NULL` 검사와 안전한 대응이 있는가?
- 소유권과 정확히 한 번의 `free()`가 정상·오류·취소 경로 모두에서 명확한가?
- block 크기와 동시 최대 개수로 worst-case heap budget을 계산했는가?
- 장시간 soak test로 leak·fragmentation·high-water mark를 관찰했는가?
- 고정 크기 pool 또는 static allocation으로 바꿀 수 있는가?

이 질문들에 답하지 못한다면 “`malloc`을 썼다”는 사실보다 **메모리 수명과 실패 정책이 설계되지 않았다**는 점이 문제다.

---

## 참고 자료

- [Why you Should NEVER Use Malloc in Real-Time Systems (YouTube)](https://www.youtube.com/watch?v=0DXU6pYKkEk)
- [C 프로그램의 메모리 레이아웃](./020_C_프로그램_메모리_레이아웃.md) — stack·heap·저장 기간의 기초
- [RTOS 메모리 관리](../cs/RTOS/4_메모리_관리.md) — FreeRTOS static allocation, heap scheme, stack watermark
- [`sizeof`와 포인터 메모리 크기](./030_sizeof와_포인터_메모리_크기.md) — 동적 block 길이를 별도로 보관해야 하는 이유

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** 실시간 시스템에서 `malloc`은 금지 주문이 아니라, runtime의 실행 시간·실패·단편화를 예측하고 통제할 수 있을 때만 제한적으로 쓰는 대상이다.
- **왜 필요:** 장시간 동작하는 MCU에서 memory leak이나 fragmentation은 한참 뒤의 allocation failure를 만들고, allocator의 비결정적 시간은 ISR과 control loop의 deadline을 깨뜨릴 수 있다.
- **동작:** `malloc`은 heap에서 연속 block을 찾고 실패하면 `NULL`을 반환한다. 매번 할당·해제를 반복하면 free block이 흩어질 수 있으므로, 소유권·정확히 한 번의 해제·최대 사용량·실패 정책을 관리해야 한다.
- **비교:** stack과 static allocation은 수명과 크기가 더 예측 가능하다. 고정 크기 pool은 일반 heap보다 fragmentation과 시간 상한을 통제하기 쉽지만, block 수가 고정되어 exhaustion 정책이 필요하다.
- **30초 통합 답변:**
  > 실시간 시스템에서 `malloc`을 무조건 금지해야 한다기보다, 실행 중 동적 할당을 통제해야 합니다. 일반 heap은 누수와 fragmentation으로 장시간 뒤에 `NULL`을 반환할 수 있고, 적합한 block을 찾는 시간도 일정하지 않아 ISR이나 주기 제어 loop에 넣기 부적절합니다. 그래서 필요한 buffer는 초기화 때 미리 할당하거나 static array·고정 크기 memory pool을 사용합니다. 꼭 동적 할당한다면 최대 사용량, `NULL` 처리, 소유권과 정확히 한 번의 해제, 장시간 테스트를 설계에 포함합니다.
