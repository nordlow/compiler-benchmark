#!/bin/bash

set -e

# Install faster linker
if ! type -f ld.lld &>/dev/null; then
    sudo apt install lld
fi

# C
sudo apt install tcc
sudo apt install gcc-12
sudo apt install clang-14

# C++
sudo apt install g++-12
sudo apt install clang-14

# Ada
sudo apt install gnat-12

# D `dmd`
./install-dmd.sh

# D `gdc`
sudo apt install gdc gdc-12

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
sudo apt install ocaml-nox

# Zig: https://github.com/ziglang/zig/wiki/Install-Zig-from-a-Package-Manager
# snap install zig --classic --beta
snap install zig --classic --edge

# Rust
./install_rust-nightly.sh
