# 임베디드 면접 Q&A 추천 자료

임베디드 소프트웨어 기술 면접에서 자주 나오는 개념 질문, 예시 답변, 해설, 코딩 문제와 꼬리질문을 연습하기 위한 자료 모음이다.

## 1. GitHub 영어 자료

### 추천 우선순위

| 순위 | 저장소 | 주요 범위 | 추천 용도 |
|---|---|---|---|
| 1 | [Bassel20/Embedded-Systems-Interview-Questions-Answers](https://github.com/Bassel20/Embedded-Systems-Interview-Questions-Answers) | C, 임베디드 개념, UART/SPI/I2C, RTOS, 코딩, 이력서 기반 질문 | 면접 답변 뼈대 작성 |
| 2 | [circuits-and-code/circuits-and-code-book](https://github.com/circuits-and-code/circuits-and-code-book) | 펌웨어, MCU, 하드웨어, 회로 | MCU·회로 연계 질문 대비 |
| 3 | [nhtranngoc/embedded-interview-questions](https://github.com/nhtranngoc/embedded-interview-questions) | endianness, ISR, `volatile`, UART/SPI/I2C, DMA, ARM, 메모리, CAN | 핵심 개념 빠른 점검 |
| 4 | [vishnumotghare/Embedded-Systems-and-Linux-Interview-Questions](https://github.com/vishnumotghare/Embedded-Systems-and-Linux-Interview-Questions) | Embedded C, Linux BSP/Kernel, ARM | C 포인터·배열 및 Linux 영역 복습 |
| 5 | [srnvl/Embedded_SWE_Prep](https://github.com/srnvl/Embedded_SWE_Prep) | 부트 시퀀스, 인터럽트, priority inversion, RTOS vs bare-metal, SPI/UART/I2C, 코딩 | 꼬리질문과 문제은행 보완 |

### 자료별 특징

### 1. Bassel20/Embedded-Systems-Interview-Questions-Answers

- 질문과 답변이 주제별로 분류되어 있어 말하기 연습에 바로 활용하기 좋다.
- C, 임베디드 기본 개념, 통신 프로토콜, RTOS, 코딩뿐 아니라 이력서 기반 질문도 포함한다.
- 다섯 자료 중 **면접 답변 연습용 1순위**로 사용한다.

### 2. circuits-and-code/circuits-and-code-book

- 펌웨어·하드웨어 면접 핵심 문항 약 20개를 책처럼 해설한다.
- 소프트웨어 개념만이 아니라 MCU와 회로를 함께 묻는 면접을 준비할 때 유용하다.
- 개념의 원리와 하드웨어 동작을 연결해 설명하는 연습에 활용한다.

### 3. nhtranngoc/embedded-interview-questions

- 주요 질문과 일부 답변을 한 페이지에서 빠르게 확인할 수 있다.
- endianness, ISR, `volatile`, UART/SPI/I2C, DMA, ARM, 메모리, CAN 등 빈출 주제가 폭넓게 포함되어 있다.
- 면접 직전 체크리스트나 빠진 개념을 찾는 용도로 적합하다.

### 4. vishnumotghare/Embedded-Systems-and-Linux-Interview-Questions

- Embedded C부터 Linux BSP/Kernel, ARM까지 비교적 넓은 범위를 다룬다.
- 특히 C 포인터와 배열 관련 문제를 다시 풀어보는 데 유용하다.
- Linux 기반 임베디드 직무를 지원할 때 보충 자료로 사용한다.

### 5. srnvl/Embedded_SWE_Prep

- 완성된 답변집보다는 문제은행과 코딩 대비 자료에 가깝다.
- 부트 시퀀스, 인터럽트, priority inversion, RTOS와 bare-metal 비교, SPI/UART/I2C 등 꼬리질문으로 이어지기 좋은 주제가 정리되어 있다.
- 1번 자료로 기본 답변을 만든 뒤 빈틈을 찾고 난도를 높이는 용도로 사용한다.

## 2. 영어권 답변·해설 자료

GitHub 문제은행 외에 질문별 예시 답변이나 면접관의 의도를 함께 볼 수 있는 웹 자료다.

### InterviewPrep — 30 Embedded Firmware Engineer Q&A

- 링크: [30 Embedded Firmware Engineer Interview Questions and Answers](https://interviewprep.org/embedded-firmware-engineer-interview-questions/)
- 기술 질문마다 면접관의 의도와 예시 답변이 있어 말하기 연습에 적합하다.
- C/C++, MCU, debugging, communication protocol, RTOS 중심으로 답변 구조를 익힐 때 사용한다.

### Indeed — Firmware Engineer Interview Questions

- 링크: [Firmware Engineer Interview Questions](https://www.indeed.com/career-advice/interviewing/firmware-engineer-interview-questions)
- 기술, 경험, 인성 질문과 예시 답변을 함께 제공한다.
- 특히 전력 최적화와 임베디드 target debugging 경험을 구조화하는 방식을 참고하기 좋다.

### Rezumi — Firmware Engineer Interview Questions

- 링크: [Firmware Engineer Interview Questions](https://www.rezumi.ai/resources/en/firmware-engineer-interview-questions)
- `volatile`/`const`, memory-mapped I/O, RTOS, MCU 등 질문마다 출제 의도와 답변 frame을 제시한다.
- 개념을 단순 정의로 끝내지 않고 면접관이 확인하려는 역량까지 연결할 때 활용한다.

### Circuits & Code Book

- 링크: [circuits-and-code/circuits-and-code-book](https://github.com/circuits-and-code/circuits-and-code-book)
- firmware·hardware intern 면접용 핵심 질문 약 20개를 해설하며 저장소에서 PDF도 제공한다.
- GitHub 추천 자료 2번과 동일한 자료로, MCU·회로 연계 질문을 준비할 때 우선 확인한다.

### Embedded C Interview Questions & Answers

- 링크: [Embedded C Interview Questions & Answers](https://wordsatease.com/embedded-c-interview-questions-answers/)
- Embedded C 핵심 질문 15개를 답변 중심으로 정리했다.
- C 언어의 기초 개념을 짧고 명확하게 말하는 연습에 활용한다.

영어권 자료 중에서는 [Bassel20 Q&A 저장소](https://github.com/Bassel20/Embedded-Systems-Interview-Questions-Answers)가 질문 분류와 답변 구성이 잘 되어 있어, iOS 면접 질문 저장소처럼 주제별 Q&A를 반복 연습하는 방식에 가장 가깝다.

## 3. 한국어 질문·답변 자료

한국어 자료는 공개 GitHub 저장소보다 웹 기반 질문·답변과 실제 면접 후기가 많다.

### 트리업 — 임베디드 엔지니어 면접 질문 9선

- 링크: [임베디드 엔지니어 면접 질문 9선](https://treeup.io/interview-questions/embedded-engineer)
- C/C++와 임베디드 경험을 연결해 말하는 답변 구조를 제시한다.
- `개념 → 경험 → trade-off` 순서로 답변을 구성하는 연습에 적합하다.

### interviews.chat — 임베디드 C/C++ 개발자 면접 질문 및 답변

- 링크: [임베디드 C/C++ 개발자 면접 질문 및 답변](https://www.interviews.chat/ko/questions/embedded-cc-developer)
- debugging, SPI/I2C, GPIO timing, logic analyzer 활용 등 질문별 답변 예시를 제공한다.
- 도구를 사용해 문제를 관찰하고 원인을 좁히는 과정을 설명하는 연습에 유용하다.

### 우문현답 — LG이노텍 SW·시스템 R&D 임베디드 경험 질문

- 링크: [LG이노텍 SW·시스템 R&D 면접 질문](https://www.woomunhyundap.com/companies/lg_10/rnd_software/9b9ce777-6cc9-4c5d-9971-8b9f902905d9)
- 임베디드 시스템 사용 경험을 구체화하고 예상 꼬리질문에 대비하는 데 초점을 둔다.
- 프로젝트에서 맡은 역할, 사용 기술, 문제 해결과 확인 결과를 구체화할 때 참고한다.

### 잘봐요 — 현대모비스 제어·임베디드·품질 면접 질문 55선

- 링크: [현대모비스 제어·임베디드·품질 면접 질문 55선](https://welldone-interview.co.kr/interview/hyundai-mobis-embedded-interview)
- 자동차 제어, 임베디드 SW, 검증·품질 질문을 한 번에 확인할 수 있다.
- 자동차·전장 또는 산업장비 회사 지원 전 예상 질문 범위를 점검할 때 활용한다.

### 만도 1차 면접 후기

- 링크: [만도 1차 면접 후기](https://researcher-ming.tistory.com/5)
- 실제 면접에서 받은 임베디드 경험, 사용 언어, PID와 feedback control 관련 질문을 확인할 수 있다.
- 개념 문제뿐 아니라 실제 면접의 질문 흐름과 깊이를 가늠하는 사례 자료로 사용한다.

### STM32 공식 한국어 문서

- 링크: [STM32 공식 한국어 페이지](https://www.st.com/ko/stm32/stm32.html)
- STM32Cube, HAL, Cortex-M, debugging 관련 답변의 기술 정확도를 검증하는 근거로 사용한다.
- 면접 질문 모음이 아니라, 커뮤니티 답변을 공식 정보와 대조하기 위한 검증 자료다.

## 4. 권장 활용 순서

### 기본 조합: GitHub 1번 + 5번

현재 면접 준비 방향에는 GitHub 자료의 **1번 + 5번 조합**을 우선 추천한다.

1. 1번 저장소에서 질문 하나를 고른다.
2. 답변을 그대로 외우지 말고 `정의 → 필요한 이유 → 동작 방식 → 실제 확인 방법` 구조로 다시 쓴다.
3. 30초 기본 답변과 1분 심화 답변을 각각 만든다.
4. 5번 저장소에서 같은 주제의 꼬리질문이나 코딩 문제를 찾아 푼다.
5. 답하지 못한 내용은 학습 노트 또는 `_오답노트.md`에 남긴다.

### 한국어 보완 순서

1. 트리업에서 `개념 → 경험 → trade-off` 답변 구조를 익힌다.
2. interviews.chat에서 peripheral과 debugging 질문의 한국어 답변 예시를 확인한다.
3. 내 STM32 프로젝트 경험을 같은 구조로 다시 말한다.
4. STM32 공식 문서와 reference manual에서 기술 내용을 검증한다.
5. 우문현답, 잘봐요, 실제 면접 후기로 회사·산업별 꼬리질문을 보완한다.

### 답변 연습 예시

`volatile`을 연습한다면 다음 순서로 확장한다.

- 기본 질문: `volatile`은 무엇인가?
- 이유 질문: 임베디드에서 왜 필요한가?
- 적용 질문: MMIO 또는 ISR 공유 변수에 어떻게 사용하는가?
- 한계 질문: `volatile`이 atomicity나 thread safety까지 보장하는가?
- 검증 질문: 생성된 assembly, debugger, datasheet에서 무엇을 확인할 것인가?

## 주의사항

오픈소스 면접 자료의 답변은 작성자의 환경과 관점에 따라 부정확하거나 지나치게 단순할 수 있다. 특히 다음 주제는 답변을 그대로 암기하지 말고 공식 문서로 한 번 더 검증한다.

- C 언어의 `volatile`, pointer, undefined behavior: 사용 중인 C 표준과 compiler 문서
- ISR, interrupt priority, DMA, memory model: MCU reference manual과 ARM 문서
- UART, SPI, I2C, CAN: 해당 MCU reference manual, peripheral datasheet, protocol specification
- RTOS scheduling, ISR API, priority inversion: 사용 중인 RTOS의 공식 문서
- Linux BSP/Kernel: Linux kernel 공식 문서

면접에서는 저장소의 표현을 재현하는 것보다, **내 프로젝트에서 어디에 적용했고 무엇으로 확인했는지**까지 연결해 설명하는 것을 최종 목표로 한다.
