# C 언어 기초

C 언어 핵심 개념 정리. 메모리 모델·포인터·전처리기 등 면접 빈출 주제 중심.

---

## 문서 목록

| 제목 | 핵심 키워드 | 영상 |
|------|------------|------|
| [C언어 포인터 (Pointers)](./010_포인터.md) | 메모리 주소, Pass by Reference, 포인터 크기, void 포인터, 이중·함수 포인터 | - |
| [C 프로그램의 메모리 레이아웃](./020_C_프로그램_메모리_레이아웃.md) | `.text`, `.data`, `.bss`, stack, heap, 저장 기간, Flash·SRAM | [YouTube](https://www.youtube.com/watch?v=FlkNgJXEyrc) |
| [`sizeof`와 포인터 메모리 크기](./030_sizeof와_포인터_메모리_크기.md) | `sizeof`, pointer size, heap allocation, `malloc`, `memcpy`, 배열 decay | [YouTube](https://www.youtube.com/watch?v=P0k1C3F61xY) |
| [비트 연산자와 비트 마스크](./040_비트연산자.md) | AND, OR, XOR, NOT, `1U << n`, bit mask, field clear/set, RMW 주의 | [영상 4개](./040_비트연산자.md#참고-자료) |
| [C Preprocessor와 volatile 키워드](./050_Preprocessor와_volatile.md) | `#define` 매크로, Base+Offset, constant folding, 벤더 헤더, volatile, 컴파일러 최적화 | [YouTube](https://www.youtube.com/watch?v=5MzilJ2-MGY) |
| [`const` 포인터와 읽기 전용 레지스터](./060_const_포인터와_읽기전용_레지스터.md) | pointer to const, const pointer, `const volatile`, 읽기 전용 MMIO 레지스터 | [YouTube](https://www.youtube.com/watch?v=HpElPprsR0I) |
| [전역 변수와 static 변수](./070_전역변수와_static.md) | Data 영역, BSS 영역, 전역 정적 변수, 지역 정적 변수, 링키지 | - |
| [함수 포인터와 콜백](./080_함수포인터와_콜백.md) | function pointer, callback, indirect call, `qsort`, `const void *`, context | [YouTube](https://www.youtube.com/watch?v=sxTFSDAZM8s) |
| [고정폭 정수 타입과 `sizeof`](./090_고정폭_정수_타입과_sizeof.md) | `stdint.h`, `uint32_t`, exact-width integer, `size_t`, `INTn_MAX`, `PRIu32` | [YouTube](https://www.youtube.com/watch?v=vq7ghSMR2ts) |
| [실시간 시스템에서 `malloc` 사용 원칙](./100_실시간_시스템에서_malloc_사용_원칙.md) | dynamic allocation, leak, fragmentation, determinism, memory pool, startup allocation | [YouTube](https://www.youtube.com/watch?v=0DXU6pYKkEk) |
| [C11 `atomic`과 Race Condition](./110_C11_atomic과_Race_Condition.md) | `_Atomic`, `atomic_fetch_add`, read-modify-write, `volatile`과 atomic의 차이, critical section | [YouTube](https://www.youtube.com/watch?v=_xX25ThomIo) |
| [C 심화 강의 — 모듈·매크로·구조체](./C_심화_강의/README.md) | `static`·`extern`, 다중 파일, `inline`, macro, padding, bit-field, CMSIS | [8개 영상](./C_심화_강의/README.md) |

---

## 파일 네이밍 규칙

- `NNN_제목.md` 형식 — `010`부터 10단위로 번호를 부여해 중간 삽입 공간 확보
- 중간 문서는 앞뒤 번호 사이의 빈 번호를 사용한다. 예: `020`과 `030` 사이에 `025`
- 제목은 한국어, 단어 사이는 `_`로 구분
- 각 문서 하단에 `면접 답변 (30초 분량)` 섹션 — `/easy-quiz` 정답 카드로 사용

---

## 관련 폴더

- [`../cs/임베디드수업/`](../cs/임베디드수업/) — MCU·임베디드 시스템 강의 시리즈
- [`../stm32/베어메탈/`](../stm32/베어메탈/) — STM32 베어메탈 실습
