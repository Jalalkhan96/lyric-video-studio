#!/bin/sh
# Word-sync a project: Demucs vocals + MMS_FA alignment -> assets/words.json
# Usage: scripts/sync.sh projects/my-song   (expects lyrics.txt + assets/song.mp3 inside)
set -e
cd "$(dirname "$0")/.."
PROJ="$1"; [ -d "$PROJ" ] || { echo "project dir not found: $PROJ"; exit 1; }
SYNC_PY=~/workspace/qarara-rasha-lyric-video/work/venv/bin/python
mkdir -p "$PROJ/work"
LVS_PROJECT="$PWD/$PROJ" "$SYNC_PY" -m demucs --two-stems vocals -o "$PROJ/work/demucs" "$PROJ/assets/song.mp3"
# demucs names its output after the input stem: assets/song.mp3 -> htdemucs/song/vocals.wav,
# which is exactly where engine/align_words.py looks first. No copying needed.
LVS_PROJECT="$PWD/$PROJ" "$SYNC_PY" engine/align_words.py
