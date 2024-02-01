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
./install_dmd-stable

# Go: `go` `gotype`
./install-golang.sh

# C#
./install-mono.sh
./install-dotnet-sdk.sh
./install-mono-mcs

# Java
./install_java

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

# Julia
./install_julia
