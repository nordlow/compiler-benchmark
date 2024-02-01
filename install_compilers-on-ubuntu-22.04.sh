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
./install_golang

# C#
./install_mono
./install_dotnet-sdk.sh
./install_mono-mcs

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
