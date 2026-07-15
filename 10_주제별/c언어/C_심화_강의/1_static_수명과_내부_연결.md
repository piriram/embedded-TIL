# `static`: 수명과 내부 연결

**원본 강의:** [The Static Keyword in C — Jacob Sorber (YouTube)](https://www.youtube.com/watch?v=3E-r4GfvWOI)

## 1. 같은 키워드, 두 문맥

`static`은 **scope**, **storage duration**, **linkage**를 구별해 읽어야 한다. 함수 안에서는 객체의 저장 기간을 정적으로 만들고, 파일 범위에서는 이름을 internal linkage로 만든다. scope 자체를 전역으로 바꾸는 키워드는 아니다.

```c
unsigned int next_id(void) {
    static unsigned int id;  // 프로그램 전체 수명, 함수 안에서만 이름 사용
    return ++id;
}
```

`id`는 호출마다 새 stack 객체가 생기지 않고 하나만 존재하며, 명시 초기화가 없으면 0으로 한 번 초기화된다.

---

## 2. 파일 범위에서는 내부 연결

```c
// motor.c
static unsigned int duty;
static void apply_pwm(unsigned int x) { duty = x; }
void motor_set_duty(unsigned int x) { apply_pwm(x); }
```

`duty`, `apply_pwm`은 `motor.c` 내부 심볼이다. 다른 파일의 `extern` 선언은 이 정의와 연결되지 않는다. 공개 API만 external linkage로 남겨 모듈 상태·헬퍼 함수를 숨기고 이름 충돌을 막는다.

> **주의**
> 함수 지역 `static`은 숨은 공유 상태다. ISR·스레드가 같은 함수를 재진입하면 안전하지 않을 수 있다.

## 참고 자료

- [원본 강의](https://www.youtube.com/watch?v=3E-r4GfvWOI)
- [전역 변수와 static 변수](../070_전역변수와_static.md)

---

## 면접 답변 (30초 분량)

- **한 줄 정의:** `static`은 함수 안에서는 정적 저장 기간, 파일 범위에서는 internal linkage를 만드는 키워드다.
- **왜 필요:** 호출 간 상태를 보존하고 모듈 내부 심볼을 외부에서 숨긴다.
- **동작:** 지역 `static`은 이름은 블록에, 객체는 프로그램 전체에 남는다. 파일 범위 `static`은 다른 번역 단위와 연결되지 않는다.
- **비교:** 일반 지역 변수는 반환 시 사라지고, 일반 파일 범위 변수는 `extern`으로 다른 파일에서 참조할 수 있다.
- **30초 통합 답변:**
  > `static`은 위치에 따라 두 의미가 있습니다. 함수 내부에서는 이름은 함수 안에만 두면서 객체를 프로그램 종료까지 유지해 호출 간 상태를 보존합니다. 파일 범위에서는 변수와 함수의 linkage를 internal로 만들어 해당 `.c`에서만 보이게 합니다. 따라서 드라이버 내부 상태와 헬퍼 함수는 `static`으로 숨기되, 지역 static은 재진입 안전성과 별도로 검토합니다.
