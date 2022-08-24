#!/bin/bash

set -e

# See: https://github.com/vlang/v#installing-v---from-source-preferred-method

REPOS=~/.cache/repos

mkdir -p "${REPOS}"
pushd "${REPOS}"
git clone --recurse-submodules https://github.com/vlang/v.git
pushd v
make
cp -rf v vlib ~/.local/bin/
popd
popd
