#!/bin/bash

set -e

URL=https://download.swift.org/swift-5.7.1-release/ubuntu2204/swift-5.7.1-RELEASE/swift-5.7.1-RELEASE-ubuntu22.04.tar.gz
TDIR="${HOME}/.local/swift"
mkdir -p "$TDIR"
exec wget --quiet --show-progress --progress=bar:force -c "$URL" -O - | tar -xz -C "$TDIR"
