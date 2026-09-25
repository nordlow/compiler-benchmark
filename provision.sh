#!/usr/bin/env bash

# Unified Compiler Benchmark Installer
# Targets: Ubuntu (22.04+) and Arch Linux (Stable)

set -euo pipefail

show_help() {
    echo "Usage: $0 --languages=[LIST|all]"
    echo ""
    echo "Options:"
    echo "  --languages=all     Install all available languages and tools."
    echo "  --languages=LIST    Comma-separated list of specific languages to install."
    echo "  --help              Show this help message."
    echo ""
    echo "Available Language Keys:"
    echo "  gcc, llvm, repo, csharp, dmd, rust, nim, c3, vlang, zig, circle, swift, vox, cproc, cuik, pareas, crystal, fpc, ghc, fortran, hare, odin, scheme"
    echo ""
    echo "Examples:"
    echo "  $0 --languages=all"
    echo "  $0 --languages=zig,rust,pareas,cproc,crystal,odin,scheme"
    exit 0
}

INSTALL_ALL=false
declare -A SELECTED

if [ $# -eq 0 ]; then
    show_help
fi

for i in "$@"; do
    case $i in
        --languages=*)
			REQUESTED_LANGS="${i#*=}"
			if [ "$REQUESTED_LANGS" == "all" ]; then
				INSTALL_ALL=true
			else
				IFS=',' read -ra ADDR <<< "$REQUESTED_LANGS"
				for lang in "${ADDR[@]}"; do
					SELECTED[$(echo "$lang" | tr '[:upper:]' '[:lower:]')]=true
				done
			fi
			shift
			;;
        --help)
            show_help
            ;;
        *)
			;;
    esac
done

if [ "$INSTALL_ALL" = false ] && [ ${#SELECTED[@]} -eq 0 ]; then
    echo "Error: No languages specified."
    show_help
fi

should_install() {
    [[ "$INSTALL_ALL" == "true" ]] && return 0
    [[ -n "${SELECTED[$1]:-}" ]] && return 0
    return 1
}

INSTALL_DIR="${HOME}/.local"
BIN_DIR="${INSTALL_DIR}/bin"
mkdir -p "$BIN_DIR"

export PATH="${BIN_DIR}:${HOME}/.cargo/bin:${HOME}/.nimble/bin:${PATH}"

if [ -f /etc/arch-release ]; then
    OS="arch"
    echo ">> System: Arch Linux detected."
elif [ -f /etc/lsb-release ] || [ -f /etc/debian_version ]; then
    OS="ubuntu"
    echo ">> System: Ubuntu/Debian detected."
else
    echo "Unsupported OS. Script optimized for Arch and Ubuntu."
    exit 1
fi

# Install only packages that are not yet installed on the system
pkg_install() {
    local to_install=()
    if [ "$OS" == "arch" ]; then
        for pkg in "$@"; do
            if ! pacman -Q "$pkg" &>/dev/null && ! pacman -Qg "$pkg" &>/dev/null; then
                to_install+=("$pkg")
            fi
        done
        if [ ${#to_install[@]} -gt 0 ]; then
            echo ">> Installing missing package(s) on Arch: ${to_install[*]}"
            sudo pacman -S --noconfirm --needed "${to_install[@]}"
        fi
    elif [ "$OS" == "ubuntu" ]; then
        for pkg in "$@"; do
            if ! dpkg -s "$pkg" 2>/dev/null | grep -q "^Status:.*installed"; then
                to_install+=("$pkg")
            fi
        done
        if [ ${#to_install[@]} -gt 0 ]; then
            echo ">> Installing missing package(s) on Ubuntu: ${to_install[*]}"
            sudo apt-get install -y "${to_install[@]}"
        fi
    fi
}

echo ">> Checking Base Build Tools..."
if [ "$OS" == "arch" ]; then
    pkg_install base-devel git curl wget unzip tar xz lld
else
    pkg_install build-essential git curl wget unzip tar xz-utils software-properties-common lld
fi

# GCC Suite (C, C++, Go, Ada, D)
if should_install "gcc"; then
    echo ">> Checking GCC Suite..."
    if [ "$OS" == "arch" ]; then
        pkg_install gcc gcc-ada gcc-d gcc-go gcc-fortran
    else
        pkg_install gcc g++ gnat gdc gccgo gfortran
    fi
fi

# LLVM / Clang
if should_install "llvm"; then
    echo ">> Checking LLVM/Clang..."
    if [ "$OS" == "arch" ]; then
        pkg_install clang lld llvm
    else
        pkg_install clang lld
    fi
fi

# Repository Languages (Java, Julia, OCaml, Python, PyPy3, TCC)
if should_install "repo"; then
    echo ">> Checking Repository Languages..."
    if [ "$OS" == "arch" ]; then
        pkg_install jdk-openjdk julia ocaml python-psutil tcc go pypy3
    else
        pkg_install openjdk-21-jdk julia ocaml python3-psutil tcc golang-go pypy3
    fi
fi

# C# (Mono & .NET SDK)
if should_install "csharp"; then
    echo ">> Checking C# environment..."
    if [ "$OS" == "arch" ]; then
        pkg_install mono dotnet-sdk
    else
        if ! dpkg -s mono-devel 2>/dev/null | grep -q "^Status:.*installed"; then
            sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF || true
            echo "deb https://download.mono-project.com/repo/ubuntu stable-focal main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
            sudo apt update
            pkg_install mono-devel
        fi
        if ! command -v dotnet &>/dev/null; then
            sudo snap install --classic dotnet-sdk || echo "Skipping dotnet snap"
        fi
    fi
fi

# D
if should_install "dmd"; then
    echo ">> Checking DMD..."
    if [ "$OS" == "arch" ]; then
        pkg_install dmd
    else
        if ! command -v dmd &>/dev/null; then
            DMD_VER=$(wget -q -O - "https://dlang.org/download.html" | grep -oP 'releases/2.x/\K\d+\.\d+\.\d+(?=/dmd_)' | head -n 1)
            ARCH_S=$( [ "$(uname -m)" == "x86_64" ] && echo "amd64" || echo "i386" )
            wget -q --show-progress "http://downloads.dlang.org/releases/2.x/${DMD_VER}/dmd_${DMD_VER}-0_${ARCH_S}.deb" -O /tmp/dmd.deb
            sudo dpkg -i /tmp/dmd.deb || sudo apt-get install -f -y
            rm -f /tmp/dmd.deb
        fi
    fi
fi

# Nim
if should_install "nim"; then
    echo ">> Checking Nim..."
    if [ "$OS" == "arch" ]; then
        pkg_install nim
    else
        if ! command -v nim &>/dev/null; then
            curl https://nim-lang.org/choosenim/init.sh -sSf | sh -s -- -y
        fi
    fi
fi

# Rust
if should_install "rust"; then
    echo ">> Checking Rust..."
    if ! command -v rustc &>/dev/null; then
        curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain nightly
    fi
fi

# C3
if should_install "c3"; then
    echo ">> Checking C3..."
    if ! command -v c3c &>/dev/null; then
        curl -fsSL https://raw.githubusercontent.com/c3lang/c3c/refs/heads/master/install/install.sh | C3_VERSION=0.8.1 bash
    fi
fi

# V
if should_install "vlang"; then
    echo ">> Checking Vlang..."
    if ! command -v v &>/dev/null && [ ! -f "$BIN_DIR/v" ]; then
        V_ZIP=$(mktemp /tmp/vlang.XXXXXX.zip)
        curl -s -L -o "$V_ZIP" "https://github.com/vlang/v/releases/latest/download/v_linux.zip"
        unzip -o -qq "$V_ZIP" -d "$INSTALL_DIR"
        ln -sf "$INSTALL_DIR/v/v" "$BIN_DIR/v"
        rm "$V_ZIP"
    fi
fi

# Zig
if should_install "zig"; then
    echo ">> Checking Zig..."
    if [ "$OS" == "arch" ]; then
        pkg_install zig
    else
        if ! command -v zig &>/dev/null; then
            ZIG_URL=$(curl -s https://ziglang.org/download/index.json | grep -oP '"tarball":\s*"\Khttps://ziglang.org/builds/zig-linux-x86_64-[^"]+' | head -n 1)
            wget -q --show-progress -c "$ZIG_URL" -O - | tar -xJ -C "$INSTALL_DIR"
        fi
    fi
fi

# Odin
if should_install "odin"; then
    echo ">> Checking Odin..."
    if [ "$OS" == "arch" ]; then
        pkg_install odin
    else
        if ! command -v odin &>/dev/null && [ ! -f "$BIN_DIR/odin" ]; then
            ODIN_ARCH=$( [ "$(uname -m)" == "x86_64" ] && echo "amd64" || echo "arm64" )
            ODIN_URL=$(curl -sL https://api.github.com/repos/odin-lang/Odin/releases/latest | grep -oP '"browser_download_url":\s*"\Khttps://github.com/odin-lang/Odin/releases/download/[^"]+linux-'"${ODIN_ARCH}"'[^"]+\.tar\.gz' | head -n 1 || true)
            if [ -z "$ODIN_URL" ]; then
                ODIN_URL=$(curl -sL "https://github.com/odin-lang/Odin/releases/latest" | grep -oP 'href="\K/odin-lang/Odin/releases/download/[^"]+linux-'"${ODIN_ARCH}"'[^"]+\.tar\.gz' | head -n 1 | sed 's|^|https://github.com|')
            fi

            if [ -n "$ODIN_URL" ]; then
                ODIN_TMP=$(mktemp -d)
                wget -q --show-progress -c "$ODIN_URL" -O "$ODIN_TMP/odin.tar.gz"
                tar -xzf "$ODIN_TMP/odin.tar.gz" -C "$ODIN_TMP"
                EXTRACTED_DIR=$(find "$ODIN_TMP" -maxdepth 2 -type f -name "odin" -exec dirname {} \; | head -n 1)
                if [ -n "$EXTRACTED_DIR" ]; then
                    rm -rf "$INSTALL_DIR/odin"
                    mv "$EXTRACTED_DIR" "$INSTALL_DIR/odin"
                    ln -sf "$INSTALL_DIR/odin/odin" "$BIN_DIR/odin"
                fi
                rm -rf "$ODIN_TMP"
            else
                echo "Error: Failed to fetch Odin release URL." >&2
                exit 1
            fi
        fi
    fi
fi

# Circle / Swift
if should_install "circle"; then
    echo ">> Checking Circle..."
    if ! command -v circle &>/dev/null; then
        CIRCLE_VER=$(wget -q -O - "https://www.circle-lang.org/linux/" | grep -oP 'build_\K\d+(?=\.tgz)' | sort -nr | head -n 1)
        wget -q --show-progress -c "https://www.circle-lang.org/linux/build_${CIRCLE_VER}.tgz" -O - | tar -xz -C "${INSTALL_DIR}"
    fi
fi

if should_install "swift"; then
    echo ">> Checking Swift..."
    if [ "$OS" == "arch" ]; then
		if command -v yay &> /dev/null; then
            yay -S --noconfirm --needed swift-bin
        elif command -v paru &> /dev/null; then
            paru -S --noconfirm --needed swift-bin
		else
			pkg_install swift
		fi
    else
        if ! command -v swift &>/dev/null; then
            SWIFT_URL=https://download.swift.org/swiftly/linux/swiftly-$(uname -m).tar.gz
            wget -q --show-progress -c "$SWIFT_URL" -O - | tar -xz -C "$INSTALL_DIR" && \
                "$INSTALL_DIR/swiftly" init --quiet-shell-followup && \
                . "${SWIFTLY_HOME_DIR:-$HOME/.local/share/swiftly}/env.sh" && \
                hash -r
        fi
    fi
fi

# Vox
if should_install "vox"; then
    echo ">> Checking Vox..."
    if [ "$OS" == "arch" ]; then pkg_install ldc; else pkg_install ldc; fi
    if [ ! -f "$BIN_DIR/vox" ]; then
        VOX_TMP=$(mktemp -d)
        git clone --depth 1 https://github.com/MrSmith33/vox "$VOX_TMP"
        pushd "$VOX_TMP/source"
        ldc2 -d-version=cli -m64 -O3 -release -boundscheck=off -enable-inlining -flto=full -i main.d -of=vox.out
        cp vox.out "$BIN_DIR/vox"
        popd
        rm -rf "$VOX_TMP"
    fi
fi

# CProc
if should_install "cproc"; then
    echo ">> Checking cproc..."
    if [ "$OS" == "arch" ]; then
        pkg_install qbe
    else
        if ! command -v qbe &> /dev/null; then
            pkg_install qbe || echo "QBE build needed"
        fi
    fi
    if [ ! -f "$BIN_DIR/cproc" ]; then
        CPROC_TMP=$(mktemp -d)
        git clone --depth 1 https://github.com/michaelforney/cproc "$CPROC_TMP"
        pushd "$CPROC_TMP"
        ./configure --prefix="$INSTALL_DIR"
        make && make install
        popd
        rm -rf "$CPROC_TMP"
    fi
fi

# Cuik
if should_install "cuik"; then
    echo ">> Checking Cuik..."
    if [ "$OS" == "arch" ]; then
        pkg_install luajit ninja
    else
        pkg_install luajit ninja-build
    fi
    if [ ! -f "$BIN_DIR/cuik" ]; then
        CUIK_TMP=$(mktemp -d)
        # --recurse-submodules is required for mimalloc and tb
        git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/RealNeGate/Cuik/ "$CUIK_TMP"
        pushd "$CUIK_TMP"
        sed -i 's/-Werror//g' build.lua
        find . -type f \( -name "*.c" -o -name "*.h" \) -exec sed -i 's/__debugbreak/__builtin_trap/g' {} +
        sed -i '1i #include <ctype.h>' common/common.c || true
        CFLAGS="-D__debugbreak=__builtin_trap -include ctype.h" luajit build.lua -x64 -driver -cuik -tb
		install -m 755 bin/cuik "$BIN_DIR/cuik"
        popd
        rm -rf "$CUIK_TMP"
    fi
fi

# Pareas
if should_install "pareas"; then
    echo ">> Checking Pareas and Dependencies..."
    if [ "$OS" == "arch" ]; then
        pkg_install meson ninja python-pip
    else
        pkg_install meson ninja-build python3-pip
    fi

    if ! command -v futhark &> /dev/null; then
        echo ">> Downloading Futhark compiler binary..."
        F_VER="0.25.15"
        F_URL="https://github.com/diku-dk/futhark/releases/download/v${F_VER}/futhark-${F_VER}-linux-x86_64.tar.xz"
        wget -q --show-progress "$F_URL" -O /tmp/futhark.tar.xz
        tar -xJf /tmp/futhark.tar.xz --strip-components=1 -C "$INSTALL_DIR"
        rm /tmp/futhark.tar.xz
    fi

    if [ ! -f "$BIN_DIR/pareas" ]; then
        PAREAS_TMP=$(mktemp -d)
        git clone --recursive https://github.com/Snektron/pareas "$PAREAS_TMP"
        pushd "$PAREAS_TMP"
        meson setup build -Dfuthark-backend=multicore --prefix="$INSTALL_DIR" --buildtype=release
        ninja -C build
        cp build/pareas "$BIN_DIR/pareas"
        popd
        rm -rf "$PAREAS_TMP"
    fi
fi

# Crystal
if should_install "crystal"; then
    echo ">> Checking Crystal..."
    if [ "$OS" == "arch" ]; then
        pkg_install crystal shards
    else
        if ! command -v crystal &>/dev/null; then
            curl -fsSL https://crystal-lang.org/install.sh | sudo bash
        fi
    fi
fi

# Free Pascal (FPC)
if should_install "fpc" || should_install "pascal"; then
    echo ">> Checking Free Pascal (FPC)..."
    if [ "$OS" == "arch" ]; then
        pkg_install fpc
    else
        if ! dpkg -s fpc 2>/dev/null | grep -q "^Status:.*installed"; then
            sudo add-apt-repository -y universe || true
            pkg_install fpc
        fi
    fi
fi

# Haskell (GHC)
if should_install "ghc" || should_install "haskell"; then
    echo ">> Checking Haskell (GHC)..."
    if [ "$OS" == "arch" ]; then
        pkg_install ghc ghc-static
    else
        if ! dpkg -s ghc 2>/dev/null | grep -q "^Status:.*installed"; then
            sudo add-apt-repository -y universe || true
            pkg_install ghc
        fi
    fi
fi

# Fortran (gfortran)
if should_install "fortran" || should_install "gfortran"; then
    echo ">> Checking GNU Fortran..."
    if [ "$OS" == "arch" ]; then
        pkg_install gcc-fortran
    else
        pkg_install gfortran
    fi
fi

# Hare
if should_install "hare"; then
    echo ">> Checking Hare..."
    if [ "$OS" == "arch" ]; then
        pkg_install hare qbe harec
    else
        if ! command -v qbe &> /dev/null; then
            pkg_install qbe || {
                QBE_TMP=$(mktemp -d)
                git clone --depth 1 git://c9x.me/qbe.git "$QBE_TMP"
                make -C "$QBE_TMP" PREFIX="$INSTALL_DIR" install
                rm -rf "$QBE_TMP"
            }
        fi

        if ! dpkg -s hare 2>/dev/null | grep -q "^Status:.*installed"; then
            HAREC_TMP=$(mktemp -d)
            git clone --depth 1 https://git.sr.ht/~sircmpwn/harec "$HAREC_TMP"
            pushd "$HAREC_TMP"
            cp configs/linux.mk config.mk
            make
            make install PREFIX="$INSTALL_DIR"
            popd
            rm -rf "$HAREC_TMP"

            HARE_TMP=$(mktemp -d)
            git clone --depth 1 https://git.sr.ht/~sircmpwn/hare "$HARE_TMP"
            pushd "$HARE_TMP"
            cp configs/linux.mk config.mk
            make
            make install PREFIX="$INSTALL_DIR"
            popd
            rm -rf "$HARE_TMP"
        fi
    fi
fi

# Scheme (Chez Scheme)
if should_install "scheme" || should_install "chezscheme" || should_install "chez-scheme"; then
    echo ">> Checking Chez Scheme..."
    if [ "$OS" == "arch" ]; then
        if ! pacman -Q chez-scheme &>/dev/null && ! pacman -Q chez-scheme-git &>/dev/null; then
            if command -v yay &> /dev/null; then
                yay -S --noconfirm --needed chez-scheme
            elif command -v paru &> /dev/null; then
                paru -S --noconfirm --needed chez-scheme
            else
                echo ">> Neither yay nor paru found; building chez-scheme from AUR using makepkg..."
                AUR_TMP=$(mktemp -d)
                git clone --depth 1 https://aur.archlinux.org/chez-scheme.git "$AUR_TMP"
                pushd "$AUR_TMP"
                makepkg -si --noconfirm
                popd
                rm -rf "$AUR_TMP"
            fi
        fi
    else
        pkg_install chezscheme
    fi

    if ! command -v scheme &> /dev/null; then
        for alt in chezscheme chez-scheme chez; do
            if command -v "$alt" &> /dev/null; then
                ln -sf "$(command -v "$alt")" "$BIN_DIR/scheme"
                break
            fi
        done
    fi
fi

echo "--------------------------------------------------------"
echo "✅ Requested installations complete for $OS!"
echo "--------------------------------------------------------"
echo "IMPORTANT: Ensure your PATH includes these directories:"
echo 'export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nimble/bin:$PATH"'
