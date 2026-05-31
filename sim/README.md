# SIL Simulator — Phase 1

펌웨어 알고리즘을 PC에서 컴파일/실행해서 검증하는 Software-in-the-Loop 환경.

## 구성

```
sim/
├── algorithm.h    알고리즘 인터페이스 (펌웨어와 동일 사용)
├── algorithm.c    LPF + jerk + 상태머신 + 디바운스 구현
├── sim_main.c     PC 측 러너 (CSV 읽어 algo_step 호출)
├── sim.py         테스트 시나리오 5종 CSV 생성기
├── test_runner.py 자동 회귀 (cases/*.csv → expected/*.txt 비교)
├── Makefile       빌드와 테스트 진입점
├── cases/         생성된 CSV (gitignore 후보)
└── expected/      각 케이스의 기대 이벤트 시퀀스
```

## 빠른 실행

```bash
make test
```

내부 동작:
1. `algo_test` 바이너리 빌드
2. `sim.py` 실행 → `cases/` 에 5개 CSV
3. `test_runner.py` 실행 → 각 CSV 통과시켜 출력 이벤트와 `expected/` 비교
4. 전부 PASS 시 종료코드 0

## CSV 포맷

```
t_ms, ax, ay, az, gx, gy, gz
```

- 100 Hz (10ms 간격)
- raw int16
- 중력 baseline: az = 16384 (1g)

## 테스트 시나리오 5종

| 케이스 | 기대 이벤트 | 검증 항목 |
|---|---|---|
| idle | 0 | 정지 상태에서 오탐 없음 |
| hard_accel | HARD_ACCEL × 1 | 양의 jerk 임계 통과 |
| hard_brake | HARD_BRAKE × 1 | 음의 jerk 임계 통과 |
| sharp_turn | SHARP_TURN × 1 | 자이로 z 임계 통과 |
| noise | 0 | 작은 spike에 오탐 없음 (필터 검증) |

## 알고리즘 (Phase 1 범위)

- LPF: 이동평균 N=8
- jerk: LPF 출력의 1차 차분
- 임계: JERK_HIGH=600, GYRO_HIGH=15000
- 디바운스: MIN_DURATION_MS=50ms
- 쿨다운: COOLDOWN_MS=1000ms
- 상태머신: IDLE → DETECTING → EVENT → COOLDOWN

## 펌웨어와의 공유

`algorithm.c` / `algorithm.h` 는 STM32 펌웨어에서도 동일하게 컴파일된다.
- PC: `cc -O2 -std=c11 sim_main.c algorithm.c`
- MCU: STM32CubeIDE 프로젝트에 `algorithm.c` 추가, `int16_t` raw IMU 값을 `algo_step()` 에 전달

이 분리로 알고리즘 단위 검증이 HW 없이 가능하고, 펌웨어 변경 시 회귀 가능.

## 한계와 다음 단계

Phase 1 한계:
- 시뮬 노이즈 = 단순 패턴. 실센서 노이즈 분포와 다름
- 임계값 = 시뮬 데이터에 맞춰 튜닝. 실측 후 재조정 필요
- 가속도 회전 보정(중력 성분 재분배) 미적용
- 자이로 drift 미보정

다음 (Phase 2 이후):
- 실측 데이터 녹화 → 재생 CSV 추가
- 알고리즘 변경 시 회귀 PASS 유지
- CI (GitHub Actions) 통합
