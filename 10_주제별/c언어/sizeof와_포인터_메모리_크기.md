# `sizeof`와 포인터 — 메모리 블록 크기를 알 수 없는 이유

**원본 강의:** [A common pitfall when using sizeof() with pointers in C. (YouTube)](https://www.youtube.com/watch?v=P0k1C3F61xY)

`sizeof`는 C에서 타입 또는 객체가 차지하는 바이트 수를 구하는 **연산자**다. 그러나 `malloc()`으로 확보한 메모리를 포인터로 가리킬 때 `sizeof(pointer)`를 쓰면, 확보한 블록의 크기가 아니라 **주소를 담는 포인터 변수의 크기**만 나온다. 이 차이를 놓치면 `memcpy()`가 데이터 일부만 복사하거나, 반대로 잘못된 길이 계산으로 메모리 오류를 낼 수 있다.

---

## 1. `sizeof`가 알려 주는 것

`sizeof`는 피연산자의 타입이 차지하는 크기를 `size_t`로 반환한다. 배열이나 구조체처럼 컴파일 시점에 크기를 아는 객체에는 매우 유용하다.

```c
int values[50];
size_t bytes = sizeof values;       /* 배열 전체의 바이트 수 */
size_t count = sizeof values / sizeof values[0];  /* 원소 개수: 50 */
```

배열 `values` 자체에 `sizeof`를 적용했으므로 배열 전체 크기를 얻는다. 반면 포인터 변수는 메모리 주소 하나를 저장하는 별도 객체다.

> 기억할 문장: `sizeof`는 “가리키는 대상의 크기”가 아니라 “식의 타입이 차지하는 크기”를 구한다.

---

## 2. 핵심 함정 — `sizeof(pointer)`는 힙 블록 크기가 아니다

다음처럼 구조체를 힙에 할당했다고 하자.

```c
struct Packet *src = malloc(200);
struct Packet *dst = malloc(200);

memcpy(dst, src, sizeof src);   /* 잘못된 코드 */
```

`src`의 타입은 `struct Packet *`다. 따라서 `sizeof src`는 `src`가 보관한 **주소의 크기**다. 64비트 환경에서는 흔히 8바이트, 32비트 환경에서는 흔히 4바이트지만, 정확한 값은 target ABI와 아키텍처에 따라 달라진다. 어느 경우든 이 값은 `malloc(200)`으로 확보한 200바이트라는 사실을 알려 주지 않는다.

즉 위 코드는 200바이트를 복사하려는 의도와 달리 보통 8바이트 또는 4바이트만 복사한다. 컴파일러나 C 런타임은 일반적인 포인터만 보고 그 주소가 가리키는 동적 할당 블록의 길이를 추적해 주지 않는다.

> **주의**
> 배열은 함수 인자로 전달되는 순간 대개 포인터로 변환(decay)된다. 따라서 함수 안에서 `sizeof(arr)`를 계산해도 전체 배열 크기가 아니라 포인터 크기가 나오는 경우가 많다. 배열 길이가 필요한 API는 길이를 별도 인자로 받아야 한다.

---

## 3. 올바른 해결 — 크기를 함께 보관하고 전달하기

동적 메모리를 확보할 때는 **할당 크기를 함께 기록**하고, 복사·전송·해제 정책에서 그 값을 사용한다.

```c
size_t packet_size = 200;
struct Packet *src = malloc(packet_size);
struct Packet *dst = malloc(packet_size);

if (src != NULL && dst != NULL) {
    memcpy(dst, src, packet_size);  /* 의도한 200바이트 복사 */
}

free(dst);
free(src);
```

크기와 포인터를 따로 들고 다니기 어렵다면, 데이터 구조에 길이를 명시적으로 넣을 수 있다.

```c
struct Buffer {
    size_t length;
    unsigned char data[];  /* flexible array member */
};
```

가변 길이 블록을 다룰 때 앞부분에 길이를 기록해 두면, 블록을 받는 쪽이 빠르게 길이를 확인할 수 있다. 다만 이 설계에서는 메타데이터 바이트, 정렬, 범위 검증, 할당·해제 책임을 함께 정해야 한다.

> **예외**
> 고정 크기 구조체라면 `sizeof *ptr` 또는 `sizeof(struct Packet)`으로 **구조체 한 개의 크기**를 구할 수 있다. 이는 포인터가 가리키는 객체의 타입 크기를 계산하는 것이며, `malloc()`이 실제로 확보한 임의 길이 블록을 알아내는 기능은 아니다.

---

## 4. 임베디드·면접에서 점검할 것

- `memcpy`, DMA 전송, 통신 프레임 처리처럼 길이가 필요한 함수에 포인터만 넘기지 않는다. 길이도 `size_t` 등으로 함께 전달한다.
- 길이는 **할당한 크기**, **실제로 유효한 데이터 길이**, **목적지 용량**으로 나뉠 수 있다. 복사 길이는 이 셋을 구분해 결정한다.
- MCU에서는 포인터 크기가 PC와 다를 수 있다. 예를 들어 32비트 Cortex-M에서는 보통 포인터가 4바이트이므로, PC에서 우연히 보인 값이나 `sizeof` 결과를 target에 그대로 가정하면 안 된다.
- C 표준에서 `malloc()` 반환 포인터만으로 portable하게 할당 크기를 역산하는 방법은 없다. 할당 시점에 보관한 길이가 정답이다.

---

## 참고 자료

- [A common pitfall when using sizeof() with pointers in C. (YouTube)](https://www.youtube.com/watch?v=P0k1C3F61xY)
- [C 언어 포인터](./포인터.md) — 주소, 포인터 크기, 포인터 연산 복습
- [RTOS 메모리 관리](../cs/RTOS/4_메모리_관리.md) — task stack·heap·동적 할당의 실제 사용

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** `sizeof(pointer)`는 포인터가 가리키는 메모리 블록이 아니라 주소를 저장하는 포인터 변수의 크기를 반환한다.
- **왜 필요:** 힙 메모리의 길이를 `sizeof(pointer)`로 계산해 `memcpy` 등에 전달하면 일부 데이터만 복사하거나 메모리 범위를 잘못 다룰 수 있다.
- **동작:** `malloc(200)`의 반환값을 `p`에 저장해도 `p`의 타입은 포인터다. 그래서 `sizeof p`는 target의 포인터 크기만 반환한다. 할당 크기는 `malloc` 시점에 `size_t length`로 보관해 API에 함께 전달해야 한다.
- **비교:** `sizeof array`는 배열 객체 전체의 크기를 구하지만, 배열이 함수 인자에서 포인터로 변환된 뒤의 `sizeof arr`은 포인터 크기를 구한다. `sizeof *p`는 가리키는 타입의 한 객체 크기일 뿐 동적 블록의 길이는 아니다.
- **30초 통합 답변:**
  > `sizeof`는 가리키는 힙 블록의 크기가 아니라 식의 타입 크기를 구합니다. 따라서 `malloc(200)`의 반환 포인터 `p`에 `sizeof p`를 적용하면 200이 아니라 target의 주소 크기, 예를 들어 32비트 MCU에서는 보통 4바이트가 나옵니다. 이 값을 `memcpy` 길이로 쓰면 데이터 일부만 복사하게 됩니다. 동적 메모리는 할당할 때 `size_t`로 길이를 별도 보관하고 포인터와 함께 전달해야 하며, 고정 크기 구조체 한 개의 크기가 필요할 때만 `sizeof *p`를 사용합니다.
