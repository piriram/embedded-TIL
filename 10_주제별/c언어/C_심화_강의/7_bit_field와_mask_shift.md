# bit-field와 mask/shift

**원본 강의:** [Bit Fields in C — Jacob Sorber (YouTube)](https://www.youtube.com/watch?v=aMAM5vL7wTs)

## 1. bit-field 문법

```c
struct flags {
    unsigned int ready : 1;
    unsigned int mode  : 2;
    unsigned int       : 1;  // 이름 없는 padding
    unsigned int error : 1;
};
```

폭은 멤버의 비트 수다. 작은 내부 상태를 읽기 좋게 압축할 수 있지만 bit-field 멤버의 주소는 일반적으로 취할 수 없다.

---

## 2. binary layout의 함정

allocation unit 크기, bit 배치 방향(LSB/MSB), padding, `int` field의 signedness, `sizeof`는 compiler·ABI에 의존할 수 있다. 따라서 같은 소스가 다른 target에서 동일한 통신 바이트열이나 레지스터 bit를 뜻한다고 보장할 수 없다.

```c
#define CTRL_ENABLE_MASK  (1U << 0)
#define CTRL_SPEED_SHIFT  1U
#define CTRL_SPEED_MASK   (0x7U << CTRL_SPEED_SHIFT)

ctrl = (ctrl & ~CTRL_SPEED_MASK) | ((speed & 0x7U) << CTRL_SPEED_SHIFT);
```

mask/shift는 데이터시트의 bit number가 코드에 드러나므로 레지스터와 패킷에 더 이식성 있다. byte order도 별도로 명시해 직렬화한다.

> **주의**
> 위 read-modify-write는 동시성 안전을 보장하지 않는다. ISR·DMA와 공유하는 레지스터는 set/clear alias나 임계 구역을 사용한다.

## 참고 자료

- [원본 강의](https://www.youtube.com/watch?v=aMAM5vL7wTs)
- [비트 연산자](../비트연산자.md)

---

## 면접 답변 (30초 분량)

- **한 줄 정의:** bit-field는 구조체 멤버에 비트 폭을 지정하는 문법이다.
- **왜 필요:** 내부 플래그와 작은 필드를 읽기 쉽게 압축한다.
- **동작:** 폭을 선언하지만 저장 단위·비트 순서·padding·signedness는 구현 의존적일 수 있다.
- **비교:** mask/shift는 정확한 bit 위치를 명시해 레지스터·통신 패킷에 더 안전하다.
- **30초 통합 답변:**
  > bit-field는 구조체 멤버의 폭을 비트로 지정해 내부 상태를 압축하는 문법입니다. 다만 bit가 어느 방향으로 배치되는지, 저장 단위와 padding, signedness는 compiler와 ABI에 의존할 수 있습니다. 그래서 정확한 binary layout이 필요한 레지스터나 통신 패킷에는 bit-field보다 데이터시트 bit 번호를 직접 표현하는 mask/shift를 우선합니다.

