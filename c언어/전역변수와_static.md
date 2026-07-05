# 전역 변수와 static 변수

전역 변수와 정적(static) 변수를 구분하려면 두 가지 기준을 기억해야 합니다.

> 변수의 **수명**은 "얼마나 오래 살아있는가"이고, **유효 범위/가시성**은 "어디서 이 변수를 볼 수 있는가"입니다.

- **수명:** 변수가 메모리에 존재하는 기간
- **유효 범위(Scope):** 코드에서 변수 이름으로 접근할 수 있는 범위
- **가시성(Visibility):** 다른 파일이나 함수에서 해당 변수를 볼 수 있는지 여부

---

## 1. Data 영역과 BSS 영역

전역 변수와 정적 변수는 프로그램이 실행되는 동안 계속 살아 있어야 하므로 보통 Data 영역 또는 BSS 영역에 저장됩니다. 반면 일반 지역 변수는 Stack 영역에 저장됩니다.

> 초기값이 있는 전역/정적 변수는 Data 영역에 저장되고, 초기값이 없거나 0으로 초기화된 전역/정적 변수는 BSS 영역에 저장됩니다.

- **Data 영역:** 초기값이 있는 전역 변수와 정적 변수가 저장되는 영역
- **BSS 영역:** 초기값이 없거나 0으로 초기화된 전역 변수와 정적 변수가 저장되는 영역. BSS는 Block Started by Symbol의 약자입니다.
- **특징:** BSS 영역의 변수는 프로그램 시작 시 자동으로 0으로 초기화됩니다.

### 예제

```c
int global_a = 10;        // Data 영역
int global_b;             // BSS 영역
static int global_c = 0;  // BSS 영역

void func(void)
{
    static int count;     // BSS 영역
    int local = 10;       // Stack 영역
}
```

- `global_a`: 10이라는 초기값이 있으므로 Data 영역
- `global_b`: 초기값이 없지만 전역 변수라서 자동으로 0이 되므로 BSS 영역
- `global_c`: 0으로 초기화된 정적 변수이므로 BSS 영역
- `count`: 함수 안에 있어도 `static`이므로 BSS 영역
- `local`: 일반 지역 변수이므로 Stack 영역

> **주의**
> 전역 변수와 정적 변수는 초기값을 주지 않아도 0으로 초기화되지만, 일반 지역 변수는 초기화하지 않으면 쓰레기값을 가질 수 있습니다.

---

## 2. 일반 전역 변수

> **전역 변수:** 함수 밖에 선언돼 프로그램 종료까지 살아있고, 선언된 파일 전체(+`extern` 시 다른 파일)에서 접근 가능한 변수.

함수 바깥에 아무 키워드 없이 선언한 변수입니다.

- **수명:** 프로그램 시작부터 끝까지 (Data/BSS 영역)
- **유효 범위:** 프로그램 전체 (다른 파일 포함)
- **특징:** `main.c`에서 선언했더라도, `helper.c` 같은 다른 파일에서 `extern` 키워드를 사용하면 이 변수를 읽고 쓸 수 있습니다.
- **단점:** 파일이 많은 큰 프로젝트에서 다른 개발자가 같은 변수 이름을 사용하면 충돌(Linker Error)이 날 수 있고, 변수 값을 누가 어디서 바꿨는지 추적하기 어렵습니다.

### 예제

```c
// main.c
int count = 10;
```

```c
// helper.c
#include <stdio.h>

extern int count;

void print_count(void)
{
    printf("%d\n", count);
}
```

`count`는 일반 전역 변수이므로, 다른 파일인 `helper.c`에서도 `extern`으로 가져와 사용할 수 있습니다.

---

## 3. 전역 정적 변수

함수 바깥에 선언하되, 앞에 `static`을 붙인 변수입니다.

> 전역 정적 변수는 수명은 전역 변수처럼 길지만, 접근 범위는 자신이 선언된 `.c` 파일 내부로 제한됩니다.

- **수명:** 프로그램 시작부터 끝까지 (Data/BSS 영역)
- **유효 범위:** 오직 자신이 선언된 파일(`.c`) 내부
- **특징:** 다른 파일에서 `extern`으로 가져가려고 해도 접근할 수 없습니다.
- **장점:** 변수 이름 충돌을 막고, 코드를 안전하게 캡슐화(정보 은닉)할 수 있습니다.

> **주의**
> 실무에서 전역 변수를 써야 한다면, 가능한 한 파일 내부에서만 보이도록 `static` 전역 변수로 제한하는 방식이 권장됩니다.

### 예제

```c
// main.c
static int count = 10;
```

```c
// helper.c
extern int count;  // 접근 불가

void change_count(void)
{
    count = 20;
}
```

`count`는 `main.c` 내부에서만 보이는 전역 정적 변수입니다. 따라서 `helper.c`에서 `extern`으로 가져오려고 해도 접근할 수 없습니다.

---

## 4. 지역 정적 변수

함수 안쪽에 `static`을 붙여 선언한 변수입니다.

> 지역 정적 변수는 함수 안에서만 보이지만, 함수가 끝나도 값이 사라지지 않습니다.

- **수명:** 프로그램 시작부터 끝까지 (Data/BSS 영역)
- **유효 범위:** 오직 자신이 선언된 함수 `{ }` 내부
- **특징:** 함수 밖에서는 볼 수 없지만, 함수 호출이 끝나도 값이 유지됩니다.

### 예제

```c
#include <stdio.h>

void counter(void)
{
    static int count = 0;

    count++;
    printf("%d\n", count);
}

int main(void)
{
    counter();  // 1
    counter();  // 2
    counter();  // 3

    return 0;
}
```

`count`는 `counter` 함수 안에서만 접근할 수 있지만, 함수 호출이 끝나도 값이 유지됩니다.

---

## 5. 비교 정리

| 구분 | 선언 위치 | 수명 | 유효 범위 |
| --- | --- | --- | --- |
| 일반 전역 변수 | 함수 밖 | 프로그램 시작부터 끝까지 | 다른 파일에서도 접근 가능 |
| 전역 정적 변수 | 함수 밖 + `static` | 프로그램 시작부터 끝까지 | 선언된 `.c` 파일 내부 |
| 지역 정적 변수 | 함수 안 + `static` | 프로그램 시작부터 끝까지 | 선언된 함수 내부 |

---

## 6. 요약

- **전역 변수:** 이 프로그램 안의 모든 파일에서 이 변수를 같이 쓰자는 의미입니다.
- **정적(static) 변수:** 수명은 길지만, 내가 선언된 구역(파일 또는 함수) 밖으로는 나가지 않겠다는 의미입니다.

> `static`은 변수의 수명을 길게 만들기도 하지만, 특히 파일 범위에서는 외부 접근을 막는 접근 제한 역할이 중요합니다.

### 한 번에 비교하는 예제

```c
// file_scope.c
#include <stdio.h>

int global_count = 10;
static int file_count = 20;

void test(void)
{
    static int local_count = 0;

    local_count++;

    printf("global_count = %d\n", global_count);
    printf("file_count = %d\n", file_count);
    printf("local_count = %d\n", local_count);
}
```

```c
// other.c
extern int global_count;
extern int file_count;  // 접근 불가

void update(void)
{
    global_count = 100;
    file_count = 200;  // 오류
}
```

- `global_count`: 다른 파일에서 `extern`으로 접근 가능
- `file_count`: 같은 파일 안에서만 접근 가능
- `local_count`: `test` 함수 안에서만 접근 가능하지만, 호출 사이에 값 유지

---

## 참고 자료

- 없음
