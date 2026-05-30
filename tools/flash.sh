#!/usr/bin/env bash
#
# STM32F103 펌웨어 플래시 스크립트 (백로그)
#
# 현재는 STM32CubeIDE GUI 사용. CLI 빌드/플래시는 다음 단계.
#
# 백로그 예시:
#   1. Makefile + arm-none-eabi-gcc 빌드
#   2. st-flash 또는 openocd로 플래시
#
# Usage (백로그 완료 후):
#   ./tools/flash.sh

set -euo pipefail

FIRMWARE="build/firmware.bin"

if [ ! -f "$FIRMWARE" ]; then
    echo "Error: $FIRMWARE not found"
    echo "Build first: make all"
    exit 1
fi

echo "Flashing $FIRMWARE to STM32F103..."
st-flash write "$FIRMWARE" 0x8000000
echo "Done. Press reset on board."
