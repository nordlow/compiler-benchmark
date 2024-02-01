#!/bin/bash

set -e

GCC_VERSION=12
LLVM_VERSION=17

# TCC
sudo apt install tcc

# GCC
sudo apt install gcc-${GCC_VERSION}
sudo apt install g++-${GCC_VERSION}

# Install LLVM and Clang
./install_llvm

# Install faster linker
if ! type -f ld.lld &>/dev/null; then
    sudo apt install lld
fi

# Ada
sudo apt install gnat-${GCC_VERSION}

# D `dmd`
./install-dmd.sh

# D `gdc`
sudo apt install gdc gdc-${GCC_VERSION}

# Go: `gccgo`
./install-gccgo.sh

# Go: `go` `gotype`
./install-golang.sh

# Julia
sudo apt install julia

# C#
./install-mono.sh
./install-dotnet-sdk.sh

sudo apt install mono-mcs

# Java
sudo apt install openjdk-18-jdk

# Nim
./install-nim.sh

# OCaml
./install_ocaml.sh

# Zig: https://github.com/ziglang/zig/wiki/Install-Zig-from-a-Package-Manager
./install_zig-master
# snap install zig --classic --beta
# snap install zig --classic --edge

# Rust
./install_rust-nightly.sh
