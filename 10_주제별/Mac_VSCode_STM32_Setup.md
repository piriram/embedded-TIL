# Mac + VSCode 환경에서 STM32 (CMake) 개발 및 디버깅 완벽 세팅하기

STM32CubeMX에서 `CMake` 기반으로 프로젝트를 생성했을 때, Mac 환경의 VSCode에서 빌드부터 디버깅까지 한 번에 진행하기 위한 세팅 과정 문서입니다.

## 1. 필수 빌드 툴 설치 (Terminal)

Mac에서는 Homebrew를 사용하여 필요한 툴체인들을 설치합니다.

```bash
# 1. CMake 빌드 시스템 설치
brew install cmake

# 2. ARM 공식 컴파일러 설치 (중요)
# (단순 arm-none-eabi-gcc 패키지는 stdint.h 등 표준 라이브러리가 누락될 수 있으므로 cask로 설치)
brew install --cask gcc-arm-embedded

# 3. 디버깅을 위한 OpenOCD 설치
brew install openocd
```

## 2. VSCode 확장 프로그램 (Extensions)

VSCode 좌측 확장 탭에서 다음 항목들을 필수로 설치합니다.
1. **C/C++** (Microsoft)
2. **CMake Tools** (Microsoft)
3. **Cortex-Debug** (marus25)
4. (선택) **clangd**

> **🚨 주의사항 (IntelliSense 충돌 해결)**
> `clangd` 확장과 Microsoft의 `C/C++` 확장이 동시에 켜져 있으면 자동 완성 충돌이 발생합니다.
> `.vscode/settings.json` 파일에 다음 설정을 추가하여 Microsoft 확장의 자동완성을 끄는 것을 권장합니다.
> ```json
> {
>     "C_Cpp.intelliSenseEngine": "disabled"
> }
> ```

## 3. 빌드 (Compile)

VSCode 터미널에서 다음 명령어로 직접 빌드하거나, VSCode 하단의 상태 표시줄에서 `Build` 버튼을 누릅니다.

```bash
# 빌드 폴더 생성 및 설정
cmake -B build
# 빌드 실행
cmake --build build
```
빌드가 성공하면 `build/` 폴더 내에 `.elf`, `.hex`, `.bin` 파일이 생성됩니다.

## 4. 디버깅 (Debugging) 환경 구성

디버깅을 버튼 하나로 실행하기 위해 `.vscode/launch.json` 파일을 생성하고 아래와 같이 작성합니다. (STM32F103 시리즈 + ST-Link 기준)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "STM32 Debug (OpenOCD)",
            "cwd": "${workspaceFolder}",
            "executable": "${workspaceFolder}/build/STM32F103C8T6-CMake-Template.elf",
            "request": "launch",
            "type": "cortex-debug",
            "servertype": "openocd",
            "configFiles": [
                "interface/stlink.cfg",
                "target/stm32f1x.cfg"
            ],
            "runToEntryPoint": "main",
            "showDevDebugOutput": "none"
        }
    ]
}
```

## 5. 자주 발생하는 에러 및 팁

### 🔴 에러: `OpenOCD: GDB Server Quit Unexpectedly`
* **원인**: 이전 디버깅 세션이 비정상적으로 종료되어 백그라운드에 `openocd` 프로세스가 살아남아 USB 포트를 점유하고 있는 현상.
* **해결법**: 터미널에 `pkill openocd` 를 입력하여 좀비 프로세스를 강제 종료한 뒤 다시 디버깅을 시작하면 해결됨.

### 🔴 에러: `fatal error: stdint.h: No such file or directory`
* **원인**: Homebrew의 기본 `arm-none-eabi-gcc` 포뮬러를 설치했을 때 C 표준 라이브러리(newlib)가 포함되지 않은 문제.
* **해결법**: 기존 패키지를 지우고(`brew uninstall arm-none-eabi-gcc`), 반드시 공식 릴리즈 버전인 `brew install --cask gcc-arm-embedded` 로 설치해야 함.

### 💡 팁: 맥북에서의 F5 키 (디버깅 단축키)
* 맥북은 기본적으로 F1~F12가 미디어 키로 작동하므로, 디버깅을 시작하려면 **`fn + F5`** 를 눌러야 함.
* 또는 엉뚱한 Quick Run 창이 뜰 경우, 좌측 **'Run and Debug(벌레 모양 아이콘)'** 탭에 직접 들어가서 드롭다운에서 `STM32 Debug (OpenOCD)` 를 선택하고 재생(▶️) 버튼을 마우스로 클릭하는 것이 가장 확실함.
