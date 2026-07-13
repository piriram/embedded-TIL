# `inline`과 `static inline`

**원본 강의:** [The Inline Keyword in C — Jacob Sorber (YouTube)](https://www.youtube.com/watch?v=t6Jfrmdg5rk)

## 1. `inline`은 보장된 확장이 아니다

`inline`은 compiler에 호출을 본문으로 확장할 기회를 주지만 명령이 아니다. 최적화 수준, 함수 크기, 디버그 설정, compiler 판단에 따라 실제 함수 호출이 남을 수 있다. 따라서 인라인 여부와 무관하게 올바르게 동작해야 한다.

```c
static inline unsigned int square_u32(unsigned int x)
{
    return x * x;
}

unsigned int v = square_u32(i++); // 인수는 한 번 평가
```

---

## 2. 헤더 유틸리티는 `static inline`

`static inline` 정의를 헤더에 두면, 헤더를 포함한 각 translation unit가 internal linkage의 구현을 가진다. compiler가 인라인하지 않아도 외부 정의를 찾을 필요가 없으므로 작은 헤더 유틸리티에 적합하다.

반면 external `inline`의 C linkage 규칙은 표준·compiler mode에 따라 외부 정의가 필요한 경우가 있어 단순하다 보기 어렵다. 외부 API는 선언을 헤더에, 일반 정의를 `.c`에 두거나 프로젝트가 정한 규칙을 따른다.

> **주의**
> 성능은 assembly·profiler로 검증한다. 지나친 확장은 code size와 instruction cache에 불리할 수 있다.

## 참고 자료

- [원본 강의](https://www.youtube.com/watch?v=t6Jfrmdg5rk)
- [함수형 전처리기 매크로](./4_함수형_전처리기_매크로.md)

---

## 면접 답변 (30초 분량)

- **한 줄 정의:** `inline`은 실제 인라인 확장을 보장하지 않는 최적화 힌트다.
- **왜 필요:** 작은 연산에서 매크로보다 안전하게 호출 비용을 줄일 기회를 얻는다.
- **동작:** `static inline`은 타입 검사·함수 scope·한 번 평가를 가지며 헤더에서 내부 구현으로 쓸 수 있다.
- **비교:** 매크로는 텍스트가 항상 펼쳐지지만 타입 검사와 한 번 평가가 없고, external `inline`은 linkage 규칙이 더 복잡하다.
- **30초 통합 답변:**
  > `inline`은 함수 호출을 반드시 없애라는 명령이 아니라 compiler의 최적화 힌트입니다. 작은 연산은 `static inline`으로 만들면 매크로와 달리 타입 검사와 함수 scope, 인수 한 번 평가를 얻고 헤더에서 각 번역 단위의 내부 구현으로 쓸 수 있습니다. 다만 실제 확장과 성능은 보장되지 않고 code size가 늘 수 있어, 외부 연결 inline의 복잡한 규칙은 피하고 필요할 때 결과를 측정합니다.

