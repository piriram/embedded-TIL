# `restrict` 키워드

> 출처: 자체 작성
> 최종 갱신: 2026-05-30

---

## 30초 통합 답변

> 면접 직전 이것만 소리내어 읽는다.

`restrict`는 **C99에서 도입된 포인터 한정자로, "이 포인터가 가리키는 객체에 접근하는 유일한 경로가 이 포인터다"라고 컴파일러에게 약속하는 키워드**입니다. 핵심 효과는 **포인터 별칭(aliasing) 가능성을 배제해 컴파일러가 더 공격적으로 최적화할 수 있도록 허락하는 것**입니다. 같은 메모리에 두 포인터가 동시에 접근할 수 있다고 가정해야 하는 일반 포인터와 달리, `restrict`가 붙은 포인터는 그 가정을 풀어 컴파일러가 메모리 읽기를 캐싱하거나 명령을 재배치하거나 SIMD로 벡터화할 수 있게 합니다. 표준 라이브러리의 `memcpy(void *restrict dest, const void *restrict src, size_t n)` 시그니처가 대표 예입니다 — 두 버퍼가 겹치면 안 된다는 계약이 시그니처에 박혀 있습니다. 임베디드에서는 DSP 루프, 신호 처리 함수, 대량 데이터 복사 함수에 붙여 성능을 끌어올립니다. 단, 실제로 겹치는 포인터를 `restrict`로 넘기면 컴파일러는 못 잡고, 결과는 미정의 동작이 됩니다.

---

## 한 줄 정의

`restrict`는 **이 포인터가 가리키는 객체에 대한 모든 접근이 이 포인터(또는 이 포인터로부터 파생된 포인터)를 통해서만 일어난다고 약속하는 한정자**다.

핵심은 **별칭 가능성 배제 → 컴파일러 최적화 여지 확대**.

## 왜 필요한가 — 별칭 문제

C는 두 포인터가 같은 메모리를 가리킬 수 있다고 가정해야 한다. 이 가정 때문에 컴파일러는 다음 같은 최적화를 못 한다.

```c
void add(int *a, int *b, int *out, size_t n) {
    for (size_t i = 0; i < n; i++) {
        out[i] = a[i] + b[i];
    }
}
```

컴파일러 입장:
- `out`이 `a`나 `b`와 겹칠 수 있다.
- `out[0] = a[0] + b[0]`이 `a[1]`이나 `b[1]`을 바꿀 수 있다.
- 따라서 매 반복마다 `a[i]`, `b[i]`를 새로 읽어야 한다.
- 루프 언롤링, 벡터화(SIMD)에 제약이 생긴다.

```c
void add(int *restrict a, int *restrict b, int *restrict out, size_t n) {
    for (size_t i = 0; i < n; i++) {
        out[i] = a[i] + b[i];
    }
}
```

이제 컴파일러는:
- 세 포인터가 서로 겹치지 않는다고 가정 가능.
- `a[i]`, `b[i]`를 레지스터에 캐싱하거나 SIMD 명령으로 4개씩 한 번에 더할 수 있다.
- 루프 명령 수가 줄어든다.

## 동작 원리

`restrict`는 **프로그래머가 컴파일러에게 하는 약속**이다. 컴파일러는 그 약속을 검증하지 않고 믿는다.

표준 표현:
- `restrict` 포인터 `p`가 가리키는 객체에 대한 모든 읽기/쓰기는 `p` 또는 `p`에서 파생된 포인터(예: `p + 1`)를 통해서만 일어난다.
- 약속이 깨지면(같은 객체에 다른 경로로 접근하면) 미정의 동작.

검증이 없기 때문에 사용은 정직해야 한다.

## 표준 라이브러리에서 본 예

C99 표준은 `restrict`를 도입하면서 여러 라이브러리 함수 시그니처를 갱신했다.

```c
void *memcpy(void *restrict dest, const void *restrict src, size_t n);
```

→ `dest`와 `src`가 겹치면 미정의. 겹칠 수 있으면 `memmove`를 써야 한다.

```c
char *strcpy(char *restrict dest, const char *restrict src);
int printf(const char *restrict format, ...);
```

`memmove`는 일부러 `restrict`가 없다 — 겹쳐도 안전하게 동작하도록 구현되어 있기 때문.

## 임베디드에서 자주 쓰는 패턴

### 1. 신호 처리 / DSP 루프

```c
void fir_filter(const float *restrict input,
                const float *restrict coeffs,
                float *restrict output,
                size_t n, size_t taps) {
    for (size_t i = 0; i < n; i++) {
        float acc = 0;
        for (size_t k = 0; k < taps; k++) {
            acc += input[i + k] * coeffs[k];
        }
        output[i] = acc;
    }
}
```

ARM Cortex-M4F의 FPU나 Cortex-M55의 Helium 같은 SIMD를 컴파일러가 활용할 가능성이 올라간다.

### 2. 대량 데이터 변환

```c
void rgb_to_gray(const uint8_t *restrict rgb,
                 uint8_t *restrict gray,
                 size_t pixels) {
    for (size_t i = 0; i < pixels; i++) {
        gray[i] = (rgb[i*3] * 30 + rgb[i*3+1] * 59 + rgb[i*3+2] * 11) / 100;
    }
}
```

### 3. MPU6050 raw → 가공 버퍼 변환

```c
void parse_imu(const uint8_t *restrict raw,
               int16_t *restrict out) {
    for (int i = 0; i < 3; i++) {
        out[i] = ((int16_t)raw[i*2] << 8) | raw[i*2 + 1];
    }
}
```

## 함정

### 1. 겹치는 포인터 전달 → 미정의 동작

```c
int buf[100];
add(buf, buf, buf, 100);   // restrict 약속 위반. 결과 미정의.
```

컴파일러는 못 잡는다. 런타임에 결과가 이상하게 나오면 디버깅 어렵다.

### 2. `restrict`는 C++ 표준이 아님

C++ 표준에는 `restrict`가 없다. GCC/Clang은 `__restrict__` 확장으로 지원하지만 표준 아니다. C 코드에만 쓴다.

### 3. 컴파일러가 항상 최적화하는 건 아님

`restrict`는 최적화 *허락*이지 *강제*가 아니다. -O0면 효과가 없을 수 있다. 측정 없이 효과를 가정하지 않는다.

### 4. const와 헷갈리지 않기

`const`는 그 포인터로 안 쓴다는 약속, `restrict`는 이 메모리에 다른 경로가 없다는 약속이다. 직교적으로 같이 쓸 수 있다.

```c
const int *restrict src   // 둘 다 가능
```

## 비교 / 대안

| 비교 대상 | 핵심 차이 |
|----------|-----------|
| 일반 포인터 | 별칭 가능 가정. 컴파일러가 보수적으로 최적화. |
| `restrict` 포인터 | 별칭 없음 약속. 컴파일러 최적화 여지 확대. |
| `const` 포인터/포인터-to-const | 쓰기 금지 약속. 별칭 가정과는 무관. |
| `volatile` 포인터 | 외부에서 값이 바뀜. 최적화 제한. restrict와 반대 방향. |
| `__attribute__((noalias))` | GCC 확장. 함수 전체에 적용. 비표준. |

## 꼬리질문 예상

- **Q:** `restrict`가 컴파일러에 약속하는 것은 무엇인가요?
  **A:** 이 포인터가 가리키는 객체에 대한 모든 접근이 이 포인터(또는 이로부터 파생된 포인터)만을 통해 일어난다는 것이다.

- **Q:** `restrict`로 어떤 최적화가 가능해지나요?
  **A:** 메모리 읽기 캐싱, 명령 재배치, SIMD 벡터화, 루프 언롤링 같은 최적화 여지가 늘어난다.

- **Q:** `restrict` 약속을 어기면 어떻게 되나요?
  **A:** 컴파일러는 검증하지 않으므로 컴파일은 통과한다. 런타임 결과는 미정의이고 보통 디버깅이 어렵다.

- **Q:** `memcpy`와 `memmove`의 차이는 무엇인가요?
  **A:** `memcpy`는 `restrict`가 붙어 두 버퍼가 안 겹친다고 가정한다. `memmove`는 겹쳐도 안전하게 동작하도록 만들어졌다.

- **Q:** `restrict`는 C++에서도 쓸 수 있나요?
  **A:** C++ 표준에는 없다. GCC/Clang의 `__restrict__` 확장은 있지만 비표준이다.

---

## 자주 하는 오해

- **오해:** `restrict`는 무조건 성능을 올린다.
  - **정확히는:** 컴파일러에 최적화 여지를 줄 뿐이다. 최적화 옵션, 타깃 아키텍처, 코드 형태에 따라 효과가 없을 수도 있다.

- **오해:** `restrict`가 별칭을 검사한다.
  - **정확히는:** 검사하지 않는다. 프로그래머가 보장해야 하는 약속이다.

- **오해:** `restrict`와 `const`는 같은 카테고리다.
  - **정확히는:** `const`는 쓰기 권한, `restrict`는 별칭 가정이다. 직교적이고 동시에 쓸 수 있다.

- **오해:** `restrict`는 임베디드에선 안 쓴다.
  - **정확히는:** DSP, 영상 처리, 대량 데이터 변환 루프에서 효과 있다. Cortex-M4F 이상에서 의미 있다.

---

## 키워드

`restrict` `C99` `pointer aliasing` `optimization hint` `SIMD vectorization` `memcpy vs memmove` `DSP loop` `loop unrolling` `register caching` `undefined behavior on overlap`
