# 코드의 제어 흐름 바꾸기 — loop와 if

**원본 강의:** [#2 How to change the flow of control through your code (YouTube)](https://www.youtube.com/watch?v=cZj284kfuE8)

이 강의는 "Modern Embedded Systems Programming" 코스의 2강이다. 1강에서 만든 "위에서 아래로 흐르는" 선형 코드를, `while` 루프와 `if` 문으로 **비선형 제어 흐름**으로 바꾼다. 단순히 문법을 익히는 게 아니라, 컴파일러가 `while` 한 줄을 어떤 machine instruction 묶음으로 바꾸는지, branch 명령어가 어떻게 PC를 조작하는지, 그리고 비선형 흐름이 왜 성능을 깎아먹는지(instruction pipeline)를 머신 레벨로 파고든다. 이 노트만 읽어도 강의를 따로 볼 필요 없도록 절차·숫자·원리를 모두 담았다.

---

## 1. 강의 목표와 프로젝트 백업의 황금률

먼저 1강 프로젝트를 복사해 `lesson 2`로 이름을 바꾼다. (1강 프로젝트가 없으면 state-machine.com/quickstart에서 받을 수 있다.) `lesson 2` 디렉터리 안으로 들어가 workspace 파일을 더블클릭하면 IAR 툴셋이 열린다.

> 강사가 강하게 권하는 습관: **작동하는 프로젝트를 자주 백업 복사하라.** 소프트웨어 개발의 황금률(golden rule)은 **항상 소프트웨어가 작동하는 상태를 유지하면서, 작고 점진적인(small incremental) 변경만 가하는 것**이다. 무언가가 작동하면 저장하라. 어떤 단계에서 망쳤을 때, 깨진 코드를 고치려 애쓰는 것보다 작동하던 버전으로 되돌아가는 편이 보통 훨씬 쉽다.

---

## 2. 선형 제어 흐름은 명령어에 하드와이어돼 있다

모든 C 프로그램이 그렇듯 이 프로그램도 `main` 함수에서 실행을 시작한다. `main` 안의 코드는 **제어가 위에서 아래로 흐르는** 아주 단순한 선형 코드다.

디버거(시뮬레이터)에서 이 가장 단순한 흐름을 확인한다. 디버그 모드의 뷰를 다시 정리하면:

- **Disassembly** 창 — machine instruction을 보여준다.
- **Register** 뷰 — ARM Cortex-M 레지스터 상태를 보여준다.
- 오늘 가장 중요한 것은 **PC(program counter) 레지스터** — 현재 명령어의 주소를 담으며, 그 명령어는 Disassembly 뷰에서 강조 표시된다.

한 번에 machine instruction 하나씩 single step 하면서 PC가 매 스텝 어떻게 바뀌는지 본다. 여기서 핵심: 우리가 실행하는 것은 **R1 레지스터를 증가시키는 명령어뿐**이고, **PC를 증가시키는 전용 명령어는 따로 없다.** 그 대신 **모든 명령어가 부수 효과(side effect)로 PC를 증가시킨다.**

즉, **위에서 아래로 흐르는 가장 단순한 선형 제어 흐름은 명령어 자체에 하드와이어(hardwire)돼 있다.** 이 강의에서는 이 하드와이어된 흐름을 바꿔서, 프로그램이 루프를 돌거나 코드의 일부를 조건적으로 건너뛰게 만든다. 이런 제어 흐름 변경 덕분에 **반복을 피하고, 런타임에 결정(decision)을 내릴 수 있다.**

---

## 3. while 루프 — 가장 단순한 반복

C에서 가장 단순한 루프는 `while` 루프다. **`while` 키워드 → 괄호 안의 조건(condition) → 루프 본문(body)** 순서로 작성한다.

동작: 조건을 검사 → 참(true)이면 본문 실행 → 다시 조건 검사로 돌아감. **조건이 거짓(false)일 때만 루프를 빠져나간다.**

1강 코드에는 `counter` 증가가 21번 있었다. 같은 횟수만큼 증가시키려면 조건을 `counter < 21`로 둔다.

```c
counter = 0;
while (counter < 21) {   /* 조건이 참인 동안 body 반복 */
    ++counter;
}
```

---

## 4. 컴파일된 루프 해부 — B, CMP, APSR, BLT 명령어

이 코드를 시뮬레이터에서 컴파일·실행하면, 컴파일러가 만든 명령어 흐름은 대략 이렇다.

```
        MOV   R0, #0      ; counter를 R0 레지스터에 0으로 대입
        B     test        ; 무조건(unconditional) 분기 — 명령어 몇 개를 건너뜀
body:   ADD   R0, #1      ; ++counter
test:   CMP   R0, #21     ; R0와 21 비교 (21은 명령어 안에 0x15로 인코딩됨)
        BLT   body        ; 조건 분기 — 조건 충족 시 body로 역방향 점프
```

각 명령어가 하는 일:

- **첫 명령어**는 0을 **R0 레지스터**로 옮긴다. R0가 이제 `counter` 변수를 담는다.
- **`B` 명령어 (Branch, 분기)** — 매우 흥미로운 명령어다. **PC를 직접 수정**해서 명령어 몇 개를 건너뛴다.
- **`CMP` 명령어 (Compare, 비교)** — R0를 숫자 21과 비교한다. 21은 명령어 자체에 16진수 **`0x15`**로 인코딩돼 있는 것을 실제로 볼 수 있다.
- `CMP`의 흥미로운 부수 효과: **APSR 레지스터를 수정**한다. **APSR은 Application Program Status Register**의 약자다. 구체적으로 `CMP`는 비교를 `R0 - 21`이라는 **뺄셈**으로 수행하는데, 그 결과가 음수가 나오므로 APSR의 **N 비트(Negative)를 세트**한다.
- **`BLT` 명령어** — 앞서 본 `B`(branch)의 한 변종이지만, 이건 **조건부(conditional)**다. `BLT`는 **APSR의 N 비트가 세트돼 있을 때만 PC를 수정**한다. 그렇지 않으면 `BLT`는 그냥 다음 명령어로 흘러내려간다(fall through).

> 즉 루프의 "조건 검사 → 분기"는 `CMP`(상태 비트 갱신)와 `BLT`(상태 비트를 보고 분기) 두 명령어가 협력해 구현한다. C의 `<` 같은 비교는 이렇게 상태 레지스터(APSR)를 거쳐 동작한다.

---

## 5. Branch 명령어는 어디로 점프할지 어떻게 아는가

좋은 질문: branch 명령어는 어디로 점프할지를 어떻게 알까? 답은 **그 정보가 명령어 자체에 인코딩(encode)돼 있다**는 것이다.

ARM Architecture Reference Manual의 한 페이지가 모든 `B` 명령어 변종의 인코딩을 설명한다. 우리의 `BLT` 명령어를 해부하면:

> **이미지 필요**
> ARM Architecture Reference Manual의 B 명령어 인코딩 표 — `BLT` 명령어 16비트를 nibble 단위로 쪼개 encoding T1 / condition / offset 영역으로 나눈 그림.
> - 출처: ARM Architecture Reference Manual, B instruction encodings 페이지 (강의 04:40 부근)
> - 대체안: 강의 해당 구간 스크린샷 캡처, `cs/임베디드수업/images/2_b_instruction_encoding.png`로 저장

- 명령어가 16진수 **`D`**로 시작한다 → **encoding T1**을 사용한다는 뜻.
- 다음 nibble은 **조건(condition)**을 나타낸다 → 16진수 **`B`**는 **LT(Less Than) 조건**을 뜻한다.
- 마지막 바이트 **`FC`**는 **PC를 얼마나 바꿀지를 인코딩**한다. 이 양을 **offset(오프셋)**이라 부른다.

여기서 1강 내용이 다시 등장한다. offset은 **부호 있는(signed) 값**이고, signed 숫자는 **2의 보수(two's complement) 표현**을 쓴다. 따라서 바이트 `0xFC`는 **-4**를 나타낸다.

이제 새 PC 값을 계산할 수 있다 — **현재 PC인 `0x7E`에서 4를 빼면 `0x7A`**다. 이게 우리가 점프하길 기대하는 지점이다. `BLT` 명령어를 실제로 실행해 보면 PC가 정말 `0x7A`로 **뒤로(backwards) 점프**한다. 뒤로 점프하므로 루프가 된다 — 코드를 단계별로 밟아가며 확인할 수 있다.

> 강사 코멘트: 명령어 해부는 여기까지만 한다. 하지만 `BLT` 명령어를 뜯어본 것은 ARM Cortex-M 프로세서의 내부 동작을 엿보게 해 줬다는 점에서 매우 교육적이었다.

---

## 6. 컴파일러는 똑똑하다 — 다른 흐름, 같은 결과

디스어셈블된 코드가 우리가 `while` 루프로 설명한 것과 **다른 제어 흐름**을 구현했다는 점을 눈치챘을 것이다.

- **원래 설명한 `while`:** 먼저 조건을 검사하고, 조건이 참이 아니면 루프 본문을 건너뛴다.
- **컴파일된 코드:** **무조건 분기(unconditional branch)로 시작**하고, **루프 본문과 조건 검사의 순서를 뒤집는다.**

생각해 보면 이 두 흐름은 **동등(equivalent)**하다. 다만 생성된 쪽이 **더 빠르다** — 루프 바닥에 **조건 분기가 단 하나**뿐이기 때문이다. (조건을 위에서 검사하면 위쪽 조건 분기 + 아래쪽 무조건 분기로 매 반복마다 분기가 2번 필요하다.)

이 예가 보여주는 두 가지 중요한 점:

1. **`while` 같은 단일 C 문장 하나가 여러 개의 machine instruction을 생성**할 수 있으며, 그 명령어들이 한 곳에 모여 있지조차 않을 수 있다.
2. **컴파일러는 꽤나 똑똑하고, 프로세서를 우리보다 더 잘 안다.**

---

## 7. 비선형 흐름의 성능 비용 — loop overhead와 pipeline stall

비선형 제어 흐름은 프로세서가 코드를 얼마나 빨리 실행하는지에 **상당한 영향**을 준다. 임베디드 시스템 프로그래머라면 이를 알아야 한다.

- 첫째, **loop overhead** — 루프를 처리하기 위한 추가적인 테스트와 점프를 이제 실행해야 한다.
- 둘째, 더 나쁜 것 — 점프는 **pipeline stall** 때문에 추가적인 실행 지연을 일으킨다.

### instruction pipeline이란

ARM Cortex-M을 포함한 모든 현대 프로세서는 처리량(throughput)을 높이려고 **instruction pipeline**을 사용한다.

> **이미지 필요**
> instruction pipeline을 조립 라인(assembly line)에 비유한 그림 — 여러 명령어가 fetch / decode / execute 단계에 각각 걸쳐 동시에 처리되는 모습, 그리고 branch 발생 시 부분 처리된 명령어가 버려지는 모습.
> - 출처: 강의 07:30~08:10 부근 pipeline 다이어그램
> - 대체안: 강의 해당 구간 스크린샷 캡처, `cs/임베디드수업/images/2_instruction_pipeline.png`로 저장

- pipeline은 **조립 라인**과 같다 — 프로세서가 여러 명령어를 각기 다른 완성 단계에 두고 동시에 작업한다. 이렇게 하면 주어진 시간에 처리할 수 있는 명령어 수가 늘어난다.
- 각 명령어는 **독립적인 단계들의 연속**으로 쪼개진다 — 메모리에서 **fetch(인출)**, **decode(해독)**, **execute(실행)** 등. 각 단계는 완료에 **한 클럭 사이클**이 걸린다.
- pipeline은 명령어가 **순서대로** 실행될 때 최대 용량(full capacity)으로 작동한다.
- 그런데 **branch 명령어가 이 순서를 깨뜨리면**, pipeline은 **부분적으로 처리된 명령어들을 버리고(discard)** 새 명령어에서 다시 시작해야 한다. 이게 **pipeline이 몇 사이클 동안 stall(정지)**한다는 뜻이다.

> **주의**
> 강사는 "루프를 쓰지 말라"고 말하는 게 **아니다.** 방금 논한 효과들은 **인터럽트 처리 같은 시간 임계(time-critical) 코드에서만** 정말 중요하고, 대부분의 다른 경우에는 무관(irrelevant)하다.

---

## 8. loop unrolling — 정말 빠르게 해야 할 때

정말로 속도를 높여야 할 때 무엇을 할 수 있는지 이제 안다 — **루프를 풀어(unroll)** 버리면 된다. 전부 풀거나, 필요한 만큼만 풀 수 있다.

예를 들어 `while` 루프를 이렇게 바꾼다 — **한 번 통과(single pass)당 `counter` 증가 횟수를 늘리고, 루프 카운터를 그에 맞춰 조정**한다.

```c
counter = 0;
while (counter < 21) {   /* 한 번 통과에 3번 증가 → 테스트·분기 빈도 1/3 */
    ++counter;
    ++counter;
    ++counter;
}
```

이렇게 실행하면 **테스트와 분기가 덜 자주** 일어나지만, 증가 횟수는 여전히 똑같은 **21번**이다. 테스트·분기 횟수가 줄어든 만큼 loop overhead와 pipeline stall이 줄어든다.

---

## 9. if 문 — 런타임에 의사결정하기

마지막으로, 제어 흐름을 이용해 **런타임에 결정을 내리는** 법을 본다. 예를 들어 `counter` 값이 **홀수(odd)**가 될 때마다 특별한 무언가를 하고 싶다고 하자.

`if` 문은 **`if` 키워드 → 괄호 안의 조건 → 조건이 참일 때 실행할 코드** 순서로 작성한다.

```c
if ((counter & 1) != 0) {   /* counter의 최하위 비트가 1 → 홀수 */
    /* 홀수일 때 실행할 코드 */
}
else {
    /* 조건이 거짓(짝수)일 때 실행 */
}
```

홀수인지 검사하는 조건식에는 설명이 필요하다.

- **`&`는 bitwise AND 연산자**다. `counter`의 **모든 비트**와 두 번째 피연산자(여기서는 `1`) 사이에서 AND 연산을 수행한다.
- 두 번째 피연산자 `1`은 `counter`의 **최하위 비트(LSB, least significant bit)**를 검사한다. LSB는 `counter`가 **짝수면 0, 홀수면 1**이다. 따라서 `counter & 1`의 결과가 곧 짝/홀 판정이 된다.
- **`!=`는 "같지 않다(not equal)"** 연산자다. 따라서 `(counter & 1) != 0`은 "LSB가 0이 아니다 = 홀수다"라는 뜻.

`if`에는 선택적인 **`else` 분기**를 붙일 수 있으며, `else`는 **조건이 거짓일 때만** 실행된다.

---

## 10. 제어 흐름문은 중첩된다

C의 제어 흐름문(control flow statement)들은 **중첩(nest)**될 수 있다. 즉 `while` 안에 `if`를 둘 수 있고, 그런 식으로 계속 조합할 수 있다.

다음 강의에서는 변수와 포인터(pointer)에 대해 좀 더 다룬다.

---

## 참고 자료

- [#2 How to change the flow of control through your code (YouTube)](https://www.youtube.com/watch?v=cZj284kfuE8)
- [state-machine.com/quickstart](https://state-machine.com/quickstart) — 클래스 노트와 프로젝트 파일 다운로드
- ARM Architecture Reference Manual — `B` 명령어 변종들의 인코딩(encoding T1, condition, offset)
- 관련 노트: [1강 — 2의 보수](./1_컴퓨터는_어떻게_숫자를_센다.md) (offset이 signed 값이라 2의 보수로 해석)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

주제: **instruction pipeline과 branch에 의한 pipeline stall**

- **한 줄 정의:** instruction pipeline은 명령어를 fetch·decode·execute 단계로 쪼개 여러 명령어를 조립 라인처럼 겹쳐 처리하는 구조로, 프로세서 처리량을 높인다.
- **왜 필요:** 명령어 하나를 끝까지 처리하고 다음을 시작하면 각 단계의 하드웨어가 놀게 된다. 단계를 겹쳐 실행하면 같은 시간에 더 많은 명령어를 처리할 수 있다.
- **동작:** 각 단계는 한 클럭 사이클이 걸리고, 명령어가 순서대로 실행될 때 pipeline은 최대 용량으로 작동한다. 그런데 branch 명령어가 PC를 바꿔 실행 순서를 깨뜨리면, 미리 fetch·decode 해 둔 부분 처리 명령어들이 무효가 되어 버려지고, 새 주소에서 다시 채워야 한다. 이 동안 pipeline이 몇 사이클 stall 한다.
- **비교:** 선형 코드는 명령어가 순서대로 흘러 pipeline이 꽉 차지만, 루프·`if` 같은 비선형 흐름은 branch마다 loop overhead와 pipeline stall을 유발한다. 그래서 인터럽트 처리 같은 시간 임계 코드에서는 loop unrolling으로 분기 빈도를 줄인다.
- **30초 통합 답변:**
  > instruction pipeline은 명령어를 fetch, decode, execute 같은 단계로 쪼개서 조립 라인처럼 여러 명령어를 겹쳐 처리하는 구조입니다. 명령어 하나를 끝까지 처리하고 다음을 시작하면 각 단계 하드웨어가 노는데, 단계를 겹치면 같은 시간에 더 많은 명령어를 처리할 수 있어서 throughput이 올라갑니다. 각 단계가 한 클럭 사이클씩 걸리고, 명령어가 순서대로 실행될 때 pipeline이 최대 용량으로 동작합니다. 문제는 branch 명령어인데, branch가 PC를 바꿔 실행 순서를 깨면 미리 fetch·decode 해 둔 명령어들이 무효가 돼서 버려지고 새 주소에서 다시 채워야 합니다. 이때 pipeline이 몇 사이클 stall 합니다. 그래서 루프나 if 같은 비선형 흐름은 loop overhead에 더해 분기마다 pipeline stall 비용이 듭니다. 평소엔 무시해도 되지만 인터럽트 처리 같은 시간 임계 코드에서는 loop unrolling으로 분기 빈도를 줄여 이 비용을 깎습니다.
