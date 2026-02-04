#!/bin/bash

SET_DPI=0 # I have set it to 192 for my 4k desktop monitor
USE_GAMEMODE=0 # use gamemoderun
RUN_INSTALLER=0 # set place Vortex-setup.exe to drive_c, set to 1 and run once. Dont forget to set back to 0
VORTEX_REL_PATH="drive_c/Program Files/Black Tree Gaming Ltd/Vortex" # in case you modified the default install path

export LD_LIBRARY_PATH="$LUTRIS_RUNNER/files/lib:/usr/lib/x86_64-linux-gnu:/app/lib/i386-linux-gnu:/app/lib:/app/lib32:/usr/lib/x86_64-linux-gnu/GL/default/lib:/app/lib/i386-linux-gnu/GL/default/lib:/app/lib/ffmpeg/.:/app/lib32/ffmpeg/.:/usr/lib/x86_64-linux-gnu/openh264/extra:/lib:/lib64:/usr/lib:/usr/lib64:/lib/i386-linux-gnu:/lib/x86_64-linux-gnu:/usr/lib/i386-linux-gnu:$LUTRIS_PATH/runtime/Ubuntu-18.04-i686:$LUTRIS_RUNTIME_STEAM/i386/lib/i386-linux-gnu:$LUTRIS_RUNTIME_STEAM/i386/lib:$LUTRIS_RUNTIME_STEAM/i386/usr/lib/i386-linux-gnu:$LUTRIS_RUNTIME_STEAM/i386/usr/lib:$LUTRIS_PATH/runtime/Ubuntu-18.04-x86_64:$LUTRIS_RUNTIME_STEAM/amd64/lib/x86_64-linux-gnu:$LUTRIS_RUNTIME_STEAM/amd64/lib:$LUTRIS_RUNTIME_STEAM/amd64/usr/lib/x86_64-linux-gnu:$LUTRIS_RUNTIME_STEAM/amd64/usr/lib:/usr/lib/extensions/vulkan/gamescope/lib"

echo "Executed on $(date) with args: $@" >> vortex.log

LUTRIS_PATH="$HOME/.var/app/net.lutris.Lutris/data/lutris"
LUTRIS_RUNTIME_STEAM="$LUTRIS_PATH/runtime/steam"
LUTRIS_RUNTIME_UMU="$LUTRIS_PATH/runtime/umu"
LUTRIS_RUNNER="$LUTRIS_PATH/runners/proton/GE-Proton10-29"

# Environment variables
export LC_ALL=""
export WINEDEBUG="-all"
export DXVK_LOG_LEVEL="error"
export UMU_LOG="1"
export WINEARCH="win64"
export WINE="$LUTRIS_RUNNER/files/bin/wine"
export WINE_MONO_CACHE_DIR="$LUTRIS_RUNNER/files/mono"
export WINE_GECKO_CACHE_DIR="$LUTRIS_RUNNER/files/gecko"
export WINEESYNC="1"
export WINEFSYNC="1"
export WINE_FULLSCREEN_FSR="1"
export DXVK_NVAPIHACK="0"
export DXVK_ENABLE_NVAPI="1"
export PROTON_DXVK_D3D8="1"
export WINEDLLOVERRIDES="winemenubuilder="
export WINE_LARGE_ADDRESS_AWARE="1"
export TERM="xterm"
export PROTON_VERB=runinprefix
export WINEPREFIX="$HOME/.local/share/Steam/steamapps/compatdata/264710/pfx"

if [ 0 -eq 1 ]; then
    cd "$WINEPREFIX/drive_c/"
    "$LUTRIS_RUNTIME_UMU/umu-run" Vortex-setup.exe
    exit 0
fi

# Working Directory
VORTEX_DIR="$WINEPREFIX/$VORTEX_REL_PATH"
WORK_DIR="$VORTEX_DIR"
cd "$WORK_DIR"

# Set DPI
if [ $SET_DPI -gt 0 ]; then
"$WINE" reg add \
"HKCU\\Control Panel\\Desktop" \
/v LogPixels \
/t REG_DWORD \
/d $SET_DPI \
/f
fi

# Command
if [ $USE_GAMEMODE -gt 0 ]; then
    gamemoderun "$LUTRIS_RUNTIME_UMU/umu-run" "$WORK_DIR/Vortex.exe" "$@"
else
    "$LUTRIS_RUNTIME_UMU/umu-run" "$WORK_DIR/Vortex.exe" "$@"
fi
