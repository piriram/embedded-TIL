# C 언어 기초

C 언어 핵심 개념 정리. 메모리 모델·포인터·전처리기 등 면접 빈출 주제 중심.

---

## 문서 목록

| 제목 | 핵심 키워드 | 영상 |
|------|------------|------|
| [C언어 포인터 (Pointers)](./포인터.md) | 메모리 주소, Pass by Reference, 포인터 크기, void 포인터, 이중·함수 포인터 | - |
| [전역 변수와 static 변수](./전역변수와_static.md) | Data 영역, BSS 영역, 전역 정적 변수, 지역 정적 변수, 링키지 | - |
| [C Preprocessor와 volatile 키워드](./Preprocessor와_volatile.md) | `#define` 매크로, Base+Offset, constant folding, 벤더 헤더, volatile, 컴파일러 최적화 | [YouTube](https://www.youtube.com/watch?v=5MzilJ2-MGY) |
| [비트 연산자 (Bitwise Operators)](./비트연산자.md) | AND, OR, XOR, NOT, shift, 플래그 압축, 레지스터 마스킹 | [YouTube](https://www.youtube.com/watch?v=igIjGxF2J-w) |

---

## 파일 네이밍 규칙

- `제목.md` 형식 — 강의 번호 prefix 없음 (주제별 분류)
- 제목은 한국어, 단어 사이는 `_`로 구분
- 각 문서 하단에 `면접 답변 (30초 분량)` 섹션 — `/easy-quiz` 정답 카드로 사용

---

## 관련 폴더

- [`../cs/임베디드수업/`](../cs/임베디드수업/) — MCU·임베디드 시스템 강의 시리즈
- [`../stm32/베어메탈/`](../stm32/베어메탈/) — STM32 베어메탈 실습
