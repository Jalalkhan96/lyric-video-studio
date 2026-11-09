#!/bin/sh
# Render a project with the kinetic engine. Usage:
#   scripts/render.sh projects/my-song [W H T0 T1 OUTFILE]
set -e
cd "$(dirname "$0")/.."
PROJ="$1"; shift
LVS_PROJECT="$PWD/$PROJ" .venv/bin/python engine/render_kinetic.py video "${@:-1080 1920 0 12 renders/out.mp4}"
