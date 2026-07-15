# C 심화 강의 — 모듈·매크로·구조체

| # | 노트 | 핵심 | 영상 | 상태 |
|---|---|---|---|---|
| 1 | [`static`: 수명과 내부 연결](./1_static_수명과_내부_연결.md) | storage duration, internal linkage | [YouTube](https://www.youtube.com/watch?v=3E-r4GfvWOI) | 완료 |
| 2 | [여러 C 파일 컴파일과 모듈화](./2_여러_C_파일_컴파일과_모듈화.md) | header, translation unit, linker | [YouTube](https://www.youtube.com/watch?v=2YfM-HxQd_8) | 완료 |
| 3 | [`extern`과 전역 심볼](./3_extern과_전역_심볼.md) | declaration, definition | [YouTube](https://www.youtube.com/watch?v=ySY_FlA7EvA) | 완료 |
| 4 | [함수형 전처리기 매크로](./4_함수형_전처리기_매크로.md) | parenthesis, side effect | [YouTube](https://www.youtube.com/watch?v=w3iXBUbq4NY) | 완료 |
| 5 | [`inline`과 `static inline`](./5_inline과_static_inline.md) | type safety, linkage | [YouTube](https://www.youtube.com/watch?v=t6Jfrmdg5rk) | 완료 |
| 6 | [구조체 padding과 alignment](./6_구조체_padding과_alignment.md) | ABI, tail padding | [YouTube](https://www.youtube.com/watch?v=aROgtACPjjg) | 완료 |
| 7 | [bit-field와 mask/shift](./7_bit_field와_mask_shift.md) | implementation-defined layout | [YouTube](https://www.youtube.com/watch?v=aMAM5vL7wTs) | 완료 |
| 8 | [CMSIS 구조체와 MCU 레지스터 매핑](./8_CMSIS_구조체와_MCU_레지스터_매핑.md) | register block, `volatile` | [YouTube](https://www.youtube.com/watch?v=A0r3O2TxtiU) | 선택 심화 |

학습 순서는 **linkage → 모듈 경계 → 안전한 추상화 → 메모리 배치 → 레지스터 접근**이다. 기존 [전역 변수와 static 변수](../070_전역변수와_static.md), [전처리기와 volatile](../050_Preprocessor와_volatile.md), [비트 연산자](../040_비트연산자.md)와 함께 본다.
