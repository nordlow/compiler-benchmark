#!/bin/bash

set -e

# Install faster linker
if ! type -f ld.lld &>/dev/null; then
    sudo apt install lld
fi

# TCC
sudo apt install tcc

# GCC
./install_gcc

# Install LLVM and Clang
./install_llvm

# D `dmd`
./install-dmd.sh

# Go: `go` `gotype`
./install-golang.sh

# Julia
./install-julia

# C#
./install-mono.sh
./install-dotnet-sdk.sh

./install-mono-mcs

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
