#!/bin/bash

VERSION="0.10.0"
URL=https://ziglang.org/builds/zig-linux-x86_64-${VERSION}-dev.3659+e5e6eb983.tar.xz
TDIR="${HOME}/.local"

echo "Downloading and extracting ${URL} to ${TDIR}..."
exec wget --quiet --show-progress --progress=bar:force -c "${URL}" -O - | tar -xJ -C "${TDIR}"
