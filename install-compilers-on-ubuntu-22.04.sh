#!/bin/bash

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
sudo apt install gccgo-12

# Go: `go` `gotype`
sudo add-apt-repository ppa:longsleep/golang-backports
sudo apt update
sudo apt install golang-go golang-golang-x-tools

# Julia
sudo apt install julia

# C#
./install-mono.sh
sudo snap install --classic dotnet-sdk

sudo apt install mono-mcs

# Java
sudo apt install openjdk-18-jdk

# Nim
curl https://nim-lang.org/choosenim/init.sh -sSf | sh

# OCaml
sudo apt install ocaml-nox
