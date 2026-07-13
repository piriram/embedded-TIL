# 이벤트 주도 프로그래밍 — GUI, 이벤트 루프, Run-to-Completion, 비차단

**원본 강의:** [#33 Event-Driven Programming Part-1: GUI example, events, event-loop, run-to-completion, no-blocking (YouTube)](https://www.youtube.com/watch?v=rfb2JI1GGIc)

이 강의는 GUI가 왜 전통적인 순차 프로그램과 다른 프로그래밍 패러다임을 요구했는지 Win32 `HelloWin` 예제로 설명한다. 핵심은 입력을 기다리는 **event loop**, producer와 consumer를 분리하는 **비동기 event queue**, 한 event를 끝까지 처리하는 **Run-to-Completion(RTC)**, 그리고 application-level code에서의 **no-blocking**이다. 다음 강의들에서 이 원리를 TivaC LaunchPad 같은 real-time embedded system에 적용한다.

---

## 1. GUI가 순차 프로그래밍만으로 어려운 이유

명령줄(command-line) 프로그램은 보통 keyboard 하나에서 입력을 받고, 화면 맨 아래에 결과를 출력한다. 따라서 다음처럼 순차 흐름으로 작성할 수 있다.

```text
키 입력을 기다린다 → 문자를 출력한다 → 키를 처리한다 → 추가 결과를 출력한다
```

GUI에서는 조건이 근본적으로 달라진다.

- 입력원이 keyboard와 mouse처럼 여러 개다. Keyboard를 blocking wait하는 동안에는 mouse에 반응하지 못하고, 그 반대도 마찬가지다.
- Keyboard 입력은 어느 window/object가 keyboard focus를 갖는지 알아야 올바른 대상에 전달할 수 있다.
- Mouse 입력은 `(x, y)` 좌표와 button 상태만으로 충분하지 않다. GUI system은 현재 좌표에 있는 object를 찾아 click, scrollbar 이동, icon 선택 같은 의미 있는 입력으로 해석해야 한다.
- Window는 겹치고 이동·크기 조절·최소화·복원된다. 출력 위치와 대상이 고정되어 있지 않다.

따라서 GUI application은 "먼저 어떤 입력을 기다릴 것인가"를 application code가 직접 결정하는 방식에서 벗어나야 한다. **입력 사건(event/message)이 application을 구동**하도록 관점을 뒤집는 것이 event-driven programming이다.

> Event는 key press, mouse move처럼 외부에서 발생한 입력뿐 아니라 button, desktop icon, scrollbar, timer처럼 GUI object와 system이 만들어 내는 사건도 포함한다.

---

## 2. Win32 `HelloWin`의 기본 구성

Win32 API의 C 예제는 event-driven programming의 구조를 직접 드러낸다.

1. `WinMain()`에서 window class의 style, cursor, class name 같은 attribute를 준비한다.
2. 해당 class가 처리할 virtual function인 `WNDPROC`(window procedure)를 attribute structure에 등록한다.
3. `RegisterClass()`로 class를 Windows에 등록하고, `CreateWindow()`로 window object를 만든다.
4. Window를 보이고 갱신한 뒤 `WinMain()`은 event loop에 들어간다.

`WNDPROC`는 특정 window class의 virtual member function처럼 동작한다. Win32는 attribute structure 안에 virtual-function pointer를 직접 넣는 방식으로 이를 구현한다. Window를 만들고 보여 주는 초기화는 한 번만 수행하지만, 실제 application의 지속적인 일은 event loop와 `WNDPROC` 호출에서 일어난다.

---

## 3. Event loop — 여러 입력을 한 곳에서 기다리고 전달하기

Win32 message loop의 핵심 형태는 다음과 같다.

```c
MSG msg;

for (;;) {
    if (GetMessage(&msg, 0, 0, 0) == 0) {
        break;
    }
    DispatchMessage(&msg);
}
```

- `GetMessage()`는 keyboard, mouse, screen 등 application에 관심 있는 **어떤 입력이든** 기다린다.
- Event가 발생하면 Windows system은 event를 `MSG` message object로 기록하여 application의 message queue에 넣는다.
- `GetMessage()`는 queue에서 message를 `msg`로 복사하고 return한다. `0` return은 application 종료를 뜻한다.
- `DispatchMessage()`는 현재 window에 등록된 `WNDPROC`를 호출하여 message를 application code로 전달한다.

```text
Keyboard / Mouse / Window system / Timer
                 ↓
      Windows가 MSG로 기록하여 queue에 저장
                 ↓
 GetMessage() ──→ DispatchMessage()
                         ↓
                    WNDPROC()
                         ↓
                 event 처리 후 return
                         └──────────────→ 다음 event를 위해 loop로 복귀
```

Message object는 event의 **기록과 전달만** 담당한다. Queue에 보관할 수 있으므로 event loop가 event를 기다릴 때뿐 아니라 이전 event를 처리하느라 바쁠 때도 새 event를 받을 수 있다.

---

## 4. Event-driven system의 세 가지 성질

### 비동기 event delivery

Windows는 event가 생기면 message를 queue에 넣을 뿐, application이 그 event 처리를 끝낼 때까지 기다리지 않는다. 이처럼 event producer(Windows system)와 event consumer(application)가 서로 독립적으로 동작하는 delivery를 **asynchronous**라고 한다.

Queue는 producer와 consumer의 속도 차이를 흡수한다. 그러나 consumer인 application이 계속 늦으면 queue에 event가 쌓이며 결국 사용자는 application이 멈춘 것처럼 느끼게 된다.

### Run-to-Completion(RTC)

`DispatchMessage()`가 `WNDPROC`를 호출하면, 그 호출은 **반드시 끝나서 event loop로 return한 뒤에야** 다음 event를 처리할 수 있다. 즉 event 하나의 처리는 다른 event가 끼어들지 않는 하나의 RTC step이다.

- Event handler는 현재 event를 끝까지 처리하고 return한다.
- 다음 event는 handler가 return한 뒤에만 dispatch된다.
- 이 규칙은 handler 내부에서 다음 event가 중첩 실행되는 상황을 막아 reasoning을 단순하게 만든다.

### Inversion of control

RTOS 기반의 전통적 code에서는 application이 RTOS service를 호출한다. Event-driven system에서는 event loop가 **application의 `WNDPROC`를 호출한다.** 즉 제어권의 주도권이 framework/system에 있고 application은 callback/handler로 참여한다.

이 **inversion of control**이 "events drive the application"의 정확한 의미이며 event-driven programming의 핵심 특성이다.

> **주의**
> RTC는 handler가 짧게 끝난다는 의미가 아니라, handler가 return할 때까지 다음 event dispatch가 진행되지 않는다는 실행 규칙이다. 따라서 handler가 길어질수록 모든 종류의 event가 함께 지연된다.

---

## 5. `WNDPROC`가 message를 처리하는 방식

`MSG` structure의 앞 네 field가 `WNDPROC` parameter와 대응한다.

| `WNDPROC` parameter | 역할 |
| --- | --- |
| `HWND me` | message를 받을 window handle. 강의에서는 member function의 receiver라는 뜻으로 `me`라고 부른다. |
| `UINT sig` | event 종류를 나타내는 signal. Win32의 원래 이름은 `message`다. |
| `WPARAM wParam` | signal별 추가 event parameter |
| `LPARAM lParam` | signal별 추가 event parameter |

Handler는 `sig`를 기준으로 `switch`를 수행한다.

```c
LRESULT CALLBACK WndProc(HWND me, UINT sig,
                         WPARAM wParam, LPARAM lParam) {
    switch (sig) {
        case WM_CREATE:
            /* window 생성 처리 */
            return 0;

        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;

        /* WM_PAINT, WM_KEYDOWN, WM_MOUSEMOVE 등 */

        default:
            return DefWindowProc(me, sig, wParam, lParam);
    }
}
```

- `WM_CREATE`는 window가 생성될 때 전달된다.
- `WM_DESTROY`에서는 `PostQuitMessage()`가 `WM_QUIT` message를 queue에 넣는다. 다음 `GetMessage()`가 `0`을 return하여 event loop가 종료된다.
- `WM_PAINT`는 Windows가 window의 일부 또는 전체를 다시 그려야 한다고 판단할 때 전달된다.
- `WM_KEYDOWN`, `WM_MOUSEMOVE`는 keyboard와 mouse 입력을 처리한다.

`PostQuitMessage()` 사례는 application도 자신에게 event를 **비동기적으로 post**할 수 있음을 보여 준다. Handler는 처리 결과 status를 Windows에 return하므로 Windows → application의 event 전달과 application → Windows의 처리 결과 보고라는 양방향 통신이 성립한다.

### Handler 호출 사이에 상태를 보존하기

`WM_PAINT`에서 key press와 mouse move 횟수를 화면에 표시하려면 counter가 `WNDPROC`의 여러 호출을 넘어 살아 있어야 한다. 그러므로 예제의 counter와 LED text pointer는 `static` variable로 둔다.

```c
case WM_KEYDOWN:
    ++key_down_count;
    InvalidateRect(me, 0, TRUE);
    return 0;
```

Automatic local variable은 handler가 return할 때마다 scope를 벗어나므로 이런 상태에 쓸 수 없다. `InvalidateRect()`는 window가 다시 그려져야 한다고 Windows에 알린다. 실제 갱신은 `WNDPROC`가 return한 뒤 Windows가 `WM_PAINT`를 보내야 일어난다.

---

## 6. Default window procedure — Ultimate Hook과 Programming by Difference

`HelloWin` 예제에서 programmer가 직접 구현한 것은 key press와 mouse move counting뿐이다. 그런데도 window는 이동, 크기 조절, 최소화, 복원, 최대화 같은 일반 Windows application의 look and feel을 가진다.

그 이유는 직접 처리하지 않은 message를 `DefWindowProc()`에 넘기기 때문이다. Win32에 정의된 수많은 `WM_*` message 중 application이 필요한 일부만 가로채고 나머지는 default window procedure가 처리한다.

```text
모든 event → application의 WNDPROC가 먼저 받음
                  ├─ 직접 처리할 event → application 동작
                  └─ 처리하지 않을 event → DefWindowProc()
                                               ↓
                                      Windows 기본 동작 수행
```

이 구조의 두 이름은 다음과 같다.

- **Ultimate Hook:** 모든 event에 application code를 붙이기 쉽다는 관점이다.
- **Programming by Difference:** 기본 동작 전체를 다시 작성하지 않고, 기본 동작과 다른 부분만 구현한다는 관점이다.

OOP 관점에서는 Windows system을 수백 개의 virtual function을 가진 base class, 각 Windows application을 선택한 function만 override하는 subclass로 볼 수 있다. `WNDPROC`는 그 override 지점을 한 함수와 `switch`로 표현한 것이다.

---

## 7. Blocking `Sleep()`이 event loop를 망가뜨리는 이유

Key를 누르면 화면의 LED text를 잠깐 `RED`로 보였다가 `OFF`로 바꾸고 싶다고 하자. 순차 code처럼 `WM_KEYDOWN` 안에서 다음을 작성하면 문제가 생긴다.

```c
case WM_KEYDOWN:
    led_text = "RED";
    InvalidateRect(me, 0, TRUE);
    Sleep(200);                 /* 200 ms blocking */
    led_text = "OFF";
    InvalidateRect(me, 0, TRUE);
    return 0;
```

### 첫 번째 문제: responsiveness 상실

`Sleep(200)` 동안 `WNDPROC`는 return하지 못한다. 그 시간에 들어오는 key와 mouse message는 queue에 축적된다. Key를 빠르게 여러 번 누르면 각 `WM_KEYDOWN`마다 200 ms씩 막히며, mouse move를 포함한 모든 event의 counter와 화면 갱신이 한동안 멈춘다. 마지막 delay를 처리한 뒤 queue를 비우면서 counter가 큰 폭으로 한꺼번에 증가한다.

Windows programmer는 이런 반응 없는 application을 **pig**라고 부른다. Windows의 오래된 rule of thumb은 100 ms 이상 걸리는 작업이라면 event로 쪼개라는 것이다.

### 두 번째 문제: RTC semantics 위반과 paint 실패

`InvalidateRect()`는 repaint 필요성을 표시할 뿐 즉시 그리지 않는다. `led_text = "RED"` 뒤에 `Sleep()`을 호출하면 `WNDPROC`가 Windows로 return하지 않으므로 Windows는 `WM_PAINT`를 dispatch할 기회를 얻지 못한다. 200 ms 후에는 LED text가 이미 `OFF`가 되어 있어 `RED` 상태를 화면에서 볼 수 없다.

Event-driven 관점에서 blocking call은 "어떤 event가 발생할 때까지 기다린다"는 뜻이다. 그런데 그 event는 현재 `WM_KEYDOWN` 처리의 중간에 도착하는 셈이므로, 한 event를 끝까지 처리한다는 RTC 가정을 깨뜨린다.

> **주의**
> Application-level handler 안에서의 blocking은 현재 event만 늦추지 않는다. 단일 event loop를 공유하는 keyboard, mouse, paint, timer 등 모든 event의 responsiveness를 떨어뜨리고 RTC를 위반한다.

---

## 8. Timer event로 LED blink를 구현하기

순차 `Sleep()` 대신 Windows timer를 사용하면 "200 ms 뒤"를 새 event로 표현할 수 있다.

```c
case WM_KEYDOWN:
    led_text = "RED";
    InvalidateRect(me, 0, TRUE);
    SetTimer(me, TIMER_ID, 200, 0);
    return 0;

case WM_TIMER:
    if (wParam == TIMER_ID) {
        led_text = "OFF";
        InvalidateRect(me, 0, TRUE);
        KillTimer(me, TIMER_ID);
    }
    return 0;
```

동작 순서는 다음과 같다.

1. `WM_KEYDOWN`은 LED text를 `RED`로 바꾸고 repaint를 요청한 뒤 곧바로 return한다.
2. Event loop는 `WM_PAINT`, mouse move, 다음 key press 등 다른 event를 계속 처리한다.
3. 200 ms 뒤 timer가 `WM_TIMER` event를 발생시킨다.
4. `WM_TIMER` handler는 `wParam`의 timer ID로 자신이 설정한 timer인지 확인하고 LED text를 `OFF`로 바꾼다.
5. `KillTimer()`를 호출해 periodic timer가 계속 만료되는 것을 막는다.

Timer는 기다림 자체를 handler 안에 두지 않고, **미래의 event를 예약**한다. 그래서 key press가 연속으로 들어오고 mouse를 움직여도 event counters가 계속 갱신되며 application은 responsive하게 남는다.

---

## 9. 임베디드 시스템으로 가져갈 원칙

GUI와 embedded system의 주변장치는 다르지만, event-driven 구조의 원칙은 같다.

| GUI 예 | Embedded system의 대응 예 | 공통 원칙 |
| --- | --- | --- |
| `WM_KEYDOWN`, `WM_MOUSEMOVE` | GPIO interrupt, UART receive, ADC conversion complete | 외부 사건을 event로 처리한다. |
| Windows message queue | event queue | producer와 consumer를 비동기로 분리한다. |
| `WNDPROC` | event handler / active object dispatch | event 하나를 RTC로 처리하고 return한다. |
| `WM_TIMER` | hardware timer timeout event | delay로 block하지 말고 시간이 지난 사실을 event로 받는다. |

이번 강의의 결론은 단순하다. **순차 programming과 event-driven programming은 다른 패러다임이며 섞이지 않는다.** Event-driven application-level code에서는 blocking을 피하고, 시간이 걸리는 동작도 timer·state·후속 event로 나누어 표현해야 한다.

---

## 10. 복습 체크리스트

- Event가 발생하면 누가 `MSG`를 만들고 queue에 넣는가?
- `GetMessage()`와 `DispatchMessage()`의 역할은 각각 무엇인가?
- 비동기 event delivery에서 producer와 consumer가 독립적이라는 말은 무엇을 뜻하는가?
- RTC가 보장하는 처리 순서는 무엇이며, `Sleep()`은 왜 이를 깨는가?
- `InvalidateRect()` 뒤 LED `RED`가 보이지 않는 이유는 무엇인가?
- 200 ms delay를 `WM_TIMER` event로 바꾸면 어떤 event들이 계속 responsive하게 처리되는가?
- Default window procedure가 제공하는 "Programming by Difference"의 이점은 무엇인가?

---

## 참고 자료

- [#33 Event-Driven Programming Part-1: GUI example, events, event-loop, run-to-completion, no-blocking (YouTube)](https://www.youtube.com/watch?v=rfb2JI1GGIc)
- [state-machine.com/quickstart](https://www.state-machine.com/quickstart) — 강의 노트와 `lesson33` HelloWin project 다운로드
- Charles Petzold, *Programming Windows* (1988) — 강의의 Hello-Windows 예제 원전
- 관련 노트: [16강 — 인터럽트의 개념과 동작 원리](./16_인터럽트의_개념과_동작원리.md), [18강 — ARM Cortex-M 인터럽트 진입과 복귀](./18_ARM_Cortex_M_인터럽트_진입과_복귀.md)

---

## 면접 답변 (30초 분량)

> `/easy-quiz` 실행 시 이 섹션이 정답 카드로 사용됩니다.

- **한 줄 정의:** Event-driven programming은 event queue와 event loop가 외부 사건을 전달하고 application handler가 각 event를 Run-to-Completion으로 처리하는 제어 역전 방식의 프로그래밍이다.
- **왜 필요:** GUI처럼 keyboard, mouse, timer 등 여러 입력에 동시에 반응해야 할 때, 한 입력을 기다리는 순차 code는 다른 입력을 놓치거나 application을 멈춘 것처럼 만들 수 있다.
- **동작:** System은 event를 message object로 queue에 넣고, event loop가 이를 꺼내 handler로 dispatch한다. Handler는 짧게 처리하고 return하며, 시간이 필요한 일은 `Sleep()`으로 block하지 않고 timer 같은 후속 event로 나눈다.
- **비교:** 순차 programming은 application이 제어 흐름과 blocking wait를 직접 주도하지만, event-driven programming은 framework의 event loop가 application code를 호출하며 각 event는 RTC로 처리된다.
- **30초 통합 답변:**
  > Event-driven programming은 system이 event를 queue에 넣고 event loop가 application handler로 전달하는 제어 역전 방식입니다. GUI처럼 keyboard, mouse, timer가 동시에 들어오는 환경에서는 순차 code로 하나를 blocking wait하면 나머지 입력에도 반응하지 못합니다. 그래서 handler는 하나의 event를 Run-to-Completion으로 짧게 끝내고 return해야 하며, 200 ms 뒤의 처리처럼 시간이 필요한 일은 `Sleep()`이 아니라 timer event로 나눕니다. 이 원칙은 GUI뿐 아니라 interrupt와 event queue를 쓰는 embedded system에도 그대로 적용됩니다.
