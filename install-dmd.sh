#!/usr/bin/env bash

MAJOR_VERSION="2.096.1-beta1"
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

# get it
wget -O "${PPATH}" "http://downloads.dlang.org/releases/2.x/${MAJOR_VERSION}/${PNAME}" && \
    exec sudo dpkg -i "${PPATH}"
