#!/bin/bash

# C++ Circle Compiler
VERSION="141"
TDIR="${HOME}/.local/circle"
mkdir -p "$TDIR"
wget --quiet --show-progress --progress=bar:force -c "https://www.circle-lang.org/linux/build_${VERSION}.tgz" -O - | tar -xz -C "$TDIR"
