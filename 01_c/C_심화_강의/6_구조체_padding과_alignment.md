# 구조체 padding과 alignment

**원본 강의:** [Structure Padding in C — Neso Academy (YouTube)](https://www.youtube.com/watch?v=aROgtACPjjg)

## 1. `sizeof`가 합계보다 큰 이유

```c
struct sample {
    char tag;       // offset 0
    int value;      // 흔히 4-byte alignment 필요
    short code;
};
```

일반적인 32-bit ABI에서는 `value`를 4의 배수 주소에 두려고 `tag` 뒤에 3바이트 padding이 들어간다. 배열 원소도 정렬돼야 하므로 끝에 tail padding이 추가될 수 있다. 위 구조체는 멤버 합이 7바이트지만 흔히 12바이트다.

---

## 2. 확인과 설계

```c
#include <stddef.h>
sizeof(struct sample);
offsetof(struct sample, value);
```

정확한 크기·alignment는 CPU, ABI, compiler option에 의존하므로 target에서 확인한다. 많은 인스턴스를 저장한다면 큰 alignment 멤버부터 배치해 내부 padding을 줄일 수 있지만, 공개 ABI·파일 형식·프로토콜 구조체의 순서는 바꾸면 안 된다.

padding 값은 의미 없을 수 있어 구조체 전체 `memcmp` 비교나 raw 전송은 위험하다. 필드를 개별 비교·직렬화한다.

---

## 3. packed는 만능 해결책이 아니다

`__attribute__((packed))` 같은 compiler 확장은 padding을 없앨 수 있지만 `int`가 unaligned address에 놓일 수 있다. target에 따라 성능 저하·fault·분해된 접근이 생긴다. 정확한 wire layout 경계에서만 CPU와 compiler 규칙을 확인해 쓴다.

> **주의**
> padding과 실제 주소 배치는 C 표준이 고정하지 않는다. `packed` 역시 이식 가능한 표준 C 문법이 아니다.

## 참고 자료

- [원본 강의](https://www.youtube.com/watch?v=aROgtACPjjg)
- [CMSIS 구조체와 MCU 레지스터 매핑](./8_CMSIS_구조체와_MCU_레지스터_매핑.md)

---

## 면접 답변 (30초 분량)

- **한 줄 정의:** 구조체 padding은 CPU alignment와 ABI를 맞추려고 멤버 사이·끝에 compiler가 넣는 여분 바이트다.
- **왜 필요:** 정렬된 접근을 보장해 CPU가 안전하고 효율적으로 멤버를 읽는다.
- **동작:** 큰 alignment 멤버 앞과 배열의 다음 원소를 맞추기 위한 끝에 padding이 생긴다.
- **비교:** 멤버 순서 조정은 공간을 줄일 수 있지만 packed 구조체는 unaligned access 위험이 있다.
- **30초 통합 답변:**
  > 구조체 padding은 alignment를 맞추기 위해 compiler가 넣는 여분 바이트입니다. 그래서 `char` 뒤의 `int` 앞에 padding이 생기고, 구조체 배열의 모든 원소를 정렬하려고 tail padding도 생겨 `sizeof`가 멤버 합과 다를 수 있습니다. 실제 layout은 target의 ABI에 따르므로 `offsetof`로 확인합니다. packed는 padding을 없애지만 unaligned access 문제를 만들 수 있어 일반 해결책이 아닙니다.

