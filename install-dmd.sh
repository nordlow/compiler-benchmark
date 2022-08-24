#!/usr/bin/env bash

set -e

MAJOR_VERSION="2.096.0"
VERSION="${MAJOR_VERSION}"

UNAME=$(uname -i)
if [[ "${UNAME}" == "i386" ]]; then
    ARCH=x86
elif [[ "${UNAME}" == "x86_64" ]]; then
    ARCH=amd64
else
    echo "Unsupported architecture ${UNAME}"
    exit 1
fi

PNAME="dmd_${VERSION}-0_${ARCH}.deb"
TDIR=/tmp
PPATH="${TDIR}/${PNAME}"

on_exit() {
    rm -f ${PPATH}
}
trap on_exit EXIT

# Install faster linker
if ! type -f ld.lld &>/dev/null; then
    sudo apt install lld
fi

# get it
wget -O "${PPATH}" "http://downloads.dlang.org/releases/2.x/${MAJOR_VERSION}/${PNAME}" && \
    exec sudo dpkg -i "${PPATH}"
