# `extern`과 전역 심볼

**원본 강의:** [Understanding the Extern Keyword in C — Jacob Sorber (YouTube)](https://www.youtube.com/watch?v=ySY_FlA7EvA)

## 1. 선언은 공유하고 정의는 한 번만

```c
// system.h
extern unsigned int system_ticks;  // 선언: storage 없음

// system.c
unsigned int system_ticks = 0U;    // 정의: 실제 객체 하나
```

`extern`은 “다른 번역 단위에 정의된 external linkage 심볼을 사용한다”는 선언이다. 헤더의 선언은 여러 `.c`에서 포함해도 괜찮지만, 정의는 한 `.c`에만 둔다. 함수는 기본적으로 external linkage이므로 `extern void f(void);` 대신 보통 `void f(void);`라고 선언한다.

---

## 2. 놓치기 쉬운 규칙

```c
extern int status;       // 선언
extern int status = 1;   // 초기화가 있으므로 정의
```

초기화된 `extern`은 객체를 만들므로 헤더에 두면 multiple definition이 된다. 파일 범위 `int x;`의 tentative definition 규칙도 혼동하기 쉬우므로, 공유 전역은 항상 `extern` 선언을 헤더에 두고 하나의 `.c`에서 초기화하여 정의한다.

파일 범위 `static int state;`는 internal linkage다. 다른 파일에 `extern int state;`라고 써도 연결할 외부 심볼이 없다. 외부에는 변수 대신 API를 공개하는 편이 안전하다.

> **주의**
> `extern`은 자동 링크가 아니다. 선언과 정의의 타입은 반드시 같은 헤더를 통해 일치시킨다.

## 참고 자료

- [원본 강의](https://www.youtube.com/watch?v=ySY_FlA7EvA)
- [여러 C 파일 컴파일과 모듈화](./2_여러_C_파일_컴파일과_모듈화.md)

---

## 면접 답변 (30초 분량)

- **한 줄 정의:** `extern`은 다른 번역 단위의 external linkage 심볼을 참조하는 선언이다.
- **왜 필요:** 여러 `.c`가 하나의 전역 객체나 외부 함수를 타입 일관성 있게 사용한다.
- **동작:** 헤더의 `extern int x;`는 객체를 만들지 않고, 한 `.c`의 `int x = 0;`가 실제 정의가 된다.
- **비교:** 파일 범위 `static`은 internal linkage라 `extern`으로 참조할 수 없고, 초기화된 `extern`은 정의다.
- **30초 통합 답변:**
  > `extern`은 다른 번역 단위에 정의된 external linkage 심볼을 이 파일에서 쓰겠다는 선언입니다. 보통 헤더에 `extern` 선언을 두고, 실제 전역 변수 정의는 초기화와 함께 한 `.c`에만 둡니다. 헤더에 정의를 두면 multiple definition이 나며, `static` 심볼은 internal linkage이므로 `extern`으로 가져올 수 없습니다.

