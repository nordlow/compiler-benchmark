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
    echo "  gcc, llvm, repo, csharp, dmd, rust, nim, c3, vlang, zig, circle, swift, vox, cproc, cuik, pareas, crystal, fpc, ghc, fortran, hare, odin"
    echo ""
    echo "Examples:"
    echo "  $0 --languages=all"
    echo "  $0 --languages=zig,rust,pareas,cproc,crystal,odin"
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
    PKG_MAN="sudo pacman -S --noconfirm --needed"
    echo ">> System: Arch Linux detected."
elif [ -f /etc/lsb-release ] || [ -f /etc/debian_version ]; then
    OS="ubuntu"
    PKG_MAN="sudo apt-get install -y"
    echo ">> System: Ubuntu/Debian detected."
else
    echo "Unsupported OS. Script optimized for Arch and Ubuntu."
    exit 1
fi

echo ">> Installing Base Build Tools..."
if [ "$OS" == "arch" ]; then
    ${PKG_MAN} base-devel git curl wget unzip tar xz lld
else
    ${PKG_MAN} build-essential git curl wget unzip tar xz-utils software-properties-common lld
fi

# GCC Suite (C, C++, Go, Ada, D)
if should_install "gcc"; then
    echo ">> Installing GCC Suite..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} gcc gcc-ada gcc-d gcc-go gcc-fortran
    else
        ${PKG_MAN} gcc g++ gnat gdc gccgo gfortran
    fi
fi

# LLVM / Clang
if should_install "llvm"; then
    echo ">> Installing LLVM/Clang..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} clang lld llvm
    else
        ${PKG_MAN} clang lld
    fi
fi

# Repository Languages (Java, Julia, OCaml, Python, Scheme, TCC)
if should_install "repo"; then
    echo ">> Installing Repository Languages..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} jdk-openjdk julia ocaml python-psutil chezscheme tcc go
    else
        ${PKG_MAN} openjdk-21-jdk julia ocaml python3-psutil chezscheme tcc golang-go
    fi
fi

# C# (Mono & .NET SDK) ---
if should_install "csharp"; then
    echo ">> Installing C# environment..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} mono dotnet-sdk
    else
        sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
        echo "deb https://download.mono-project.com/repo/ubuntu stable-focal main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
        sudo apt update
        ${PKG_MAN} mono-devel
        sudo snap install --classic dotnet-sdk || echo "Skipping dotnet snap"
    fi
fi

# D
if should_install "dmd"; then
    echo ">> Installing DMD..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} dmd
    else
        DMD_VER=$(wget -q -O - "https://dlang.org/download.html" | grep -oP 'releases/2.x/\K\d+\.\d+\.\d+(?=/dmd_)' | head -n 1)
        ARCH_S=$( [ "$(uname -m)" == "x86_64" ] && echo "amd64" || echo "i386" )
        wget -q --show-progress "http://downloads.dlang.org/releases/2.x/${DMD_VER}/dmd_${DMD_VER}-0_${ARCH_S}.deb" -O /tmp/dmd.deb
        sudo dpkg -i /tmp/dmd.deb || sudo apt-get install -f -y
    fi
fi

# Nim
if should_install "nim"; then
    echo ">> Installing Nim..."
    if [ "$OS" == "arch" ]; then ${PKG_MAN} nim; else curl https://nim-lang.org/choosenim/init.sh -sSf | sh -s -- -y; fi
fi

# Rust
if should_install "rust"; then
    echo ">> Installing Rust..."
    curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain nightly
fi

# C3
if should_install "c3"; then
    echo ">> Installing C3..."
    curl -fsSL https://raw.githubusercontent.com/c3lang/c3c/refs/heads/master/install/install.sh | C3_VERSION=0.8.1 bash
fi

# V
if should_install "vlang"; then
    echo ">> Installing Vlang..."
    V_ZIP=$(mktemp /tmp/vlang.XXXXXX.zip)
    curl -s -L -o "$V_ZIP" "https://github.com/vlang/v/releases/latest/download/v_linux.zip"
    unzip -o -qq "$V_ZIP" -d "$INSTALL_DIR"
    ln -sf "$INSTALL_DIR/v/v" "$BIN_DIR/v"
    rm "$V_ZIP"
fi

# Zig
if should_install "zig"; then
    echo ">> Installing Zig..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} zig
    else
        ZIG_URL=$(curl -s https://ziglang.org/download/index.json | grep -oP '"tarball":\s*"\Khttps://ziglang.org/builds/zig-linux-x86_64-[^"]+' | head -n 1)
        wget -q --show-progress -c "$ZIG_URL" -O - | tar -xJ -C "$INSTALL_DIR"
    fi
fi

# ODin
if should_install "odin"; then
    echo ">> Installing Odin..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} odin
    else
        ODIN_ARCH=$( [ "$(uname -m)" == "x86_64" ] && echo "amd64" || echo "arm64" )
        # Query GitHub API with a scrape fallback in case of rate limits
        ODIN_URL=$(curl -sL https://api.github.com/repos/odin-lang/Odin/releases/latest | grep -oP '"browser_download_url":\s*"\Khttps://github.com/odin-lang/Odin/releases/download/[^"]+linux-'"${ODIN_ARCH}"'[^"]+\.tar\.gz' | head -n 1 || true)
        if [ -z "$ODIN_URL" ]; then
            ODIN_URL=$(curl -sL "https://github.com/odin-lang/Odin/releases/latest" | grep -oP 'href="\K/odin-lang/Odin/releases/download/[^"]+linux-'"${ODIN_ARCH}"'[^"]+\.tar\.gz' | head -n 1 | sed 's|^|https://github.com|')
        fi

        if [ -n "$ODIN_URL" ]; then
            ODIN_TMP=$(mktemp -d)
            wget -q --show-progress -c "$ODIN_URL" -O "$ODIN_TMP/odin.tar.gz"
            tar -xzf "$ODIN_TMP/odin.tar.gz" -C "$ODIN_TMP"
            # Locate the extracted directory containing the binary, core, and base libs
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

# Swift
if should_install "circle"; then
    echo ">> Installing Circle..."
    CIRCLE_VER=$(wget -q -O - "https://www.circle-lang.org/linux/" | grep -oP 'build_\K\d+(?=\.tgz)' | sort -nr | head -n 1)
    wget -q --show-progress -c "https://www.circle-lang.org/linux/build_${CIRCLE_VER}.tgz" -O - | tar -xz -C "${INSTALL_DIR}"
fi
if should_install "swift"; then
    echo ">> Installing Swift..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} swift-bin
    else
        SWIFT_URL=https://download.swift.org/swiftly/linux/swiftly-$(uname -m).tar.gz
        wget -q --show-progress -c "$SWIFT_URL" -O - | tar -xz -C "$INSTALL_DIR" && \
            "$INSTALL_DIR/swiftly" init --quiet-shell-followup && \
            . "${SWIFTLY_HOME_DIR:-$HOME/.local/share/swiftly}/env.sh" && \
            hash -r
    fi
fi

# Vox
if should_install "vox"; then
    echo ">> Building Vox..."
    if [ "$OS" == "arch" ]; then ${PKG_MAN} ldc; else ${PKG_MAN} ldc; fi
    VOX_TMP=$(mktemp -d)
    git clone --depth 1 https://github.com/MrSmith33/vox "$VOX_TMP"
    pushd "$VOX_TMP/source"
    ldc2 -d-version=cli -m64 -O3 -release -boundscheck=off -enable-inlining -flto=full -i main.d -of=vox.out
    cp vox.out "$BIN_DIR/vox"
    popd
    rm -rf "$VOX_TMP"
fi

# CProc
if should_install "cproc"; then
    echo ">> Building cproc..."
    if [ "$OS" == "arch" ]; then ${PKG_MAN} qbe; else ${PKG_MAN} qbe || echo "QBE build needed"; fi
    CPROC_TMP=$(mktemp -d)
    git clone --depth 1 https://github.com/michaelforney/cproc "$CPROC_TMP"
    pushd "$CPROC_TMP"
    ./configure --prefix="$INSTALL_DIR"
    make && make install
    popd
    rm -rf "$CPROC_TMP"
fi

# Cuik
if should_install "cuik"; then
    echo ">> Building Cuik..."
    if [ "$OS" == "arch" ]; then ${PKG_MAN} luajit; else ${PKG_MAN} luajit; fi
    CUIK_TMP=$(mktemp -d)
    git clone --depth 1 https://github.com/RealNeGate/Cuik/ "$CUIK_TMP"
    pushd "$CUIK_TMP"
    sed -i 's/-Werror//g' build.lua
    find . -type f \( -name "*.c" -o -name "*.h" \) -exec sed -i 's/__debugbreak/__builtin_trap/g' {} +
    sed -i '1i #include <ctype.h>' common/common.c
    CFLAGS="-D__debugbreak=__builtin_trap -include ctype.h" luajit build.lua -x64 -driver -cuik -tb
    cp cuik "$BIN_DIR/cuik"
    popd
    rm -rf "$CUIK_TMP"
fi

# Pareas
if should_install "pareas"; then
    echo ">> Installing Pareas and Dependencies..."

    # 1. System Dependencies (C++20, Meson, Ninja, Python)
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} meson ninja python-pip
    else
        ${PKG_MAN} meson ninja-build python3-pip
    fi

    # 2. Futhark Compiler (Required for Pareas)
    if ! command -v futhark &> /dev/null; then
        echo ">> Downloading Futhark compiler binary..."
        F_VER="0.25.15" # Latest known stable
        F_URL="https://github.com/diku-dk/futhark/releases/download/v${F_VER}/futhark-${F_VER}-linux-x86_64.tar.xz"
        wget -q --show-progress "$F_URL" -O /tmp/futhark.tar.xz
        tar -xJf /tmp/futhark.tar.xz --strip-components=1 -C "$INSTALL_DIR"
        rm /tmp/futhark.tar.xz
    fi

    # 3. Clone and Build Pareas
    PAREAS_TMP=$(mktemp -d)
    # Note: --recursive is critical for {fmt} and other submodules
    git clone --recursive https://github.com/Snektron/pareas "$PAREAS_TMP"
    pushd "$PAREAS_TMP"

    # We use the multicore backend as it is the most compatible for CPU benchmarking
    # without requiring specific NVIDIA/OpenCL drivers installed.
    meson setup build -Dfuthark-backend=multicore --prefix="$INSTALL_DIR" --buildtype=release
    ninja -C build

    # Install the resulting binary
    cp build/pareas "$BIN_DIR/pareas"
    popd
    rm -rf "$PAREAS_TMP"
fi

# Crystal
if should_install "crystal"; then
    echo ">> Installing Crystal..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} crystal shards
    else
        curl -fsSL https://crystal-lang.org/install.sh | sudo bash
    fi
fi

# Free Pascal (FPC)
if should_install "fpc" || should_install "pascal"; then
    echo ">> Installing Free Pascal (FPC)..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} fpc
    else
        sudo add-apt-repository -y universe || true
        ${PKG_MAN} fpc
    fi
fi

# Haskell (GHC)
if should_install "ghc" || should_install "haskell"; then
    echo ">> Installing Haskell (GHC)..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} ghc ghc-static
    else
        sudo add-apt-repository -y universe || true
        ${PKG_MAN} ghc
    fi
fi

# Fortran (gfortran)
if should_install "fortran" || should_install "gfortran"; then
    echo ">> Installing GNU Fortran..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} gcc-fortran
    else
        ${PKG_MAN} gfortran
    fi
fi

# Hare
if should_install "hare"; then
    echo ">> Installing Hare..."
    if [ "$OS" == "arch" ]; then
        ${PKG_MAN} hare qbe harec
    else
        # Ensure QBE backend is present
        if ! command -v qbe &> /dev/null; then
            ${PKG_MAN} qbe 2>/dev/null || {
                QBE_TMP=$(mktemp -d)
                git clone --depth 1 git://c9x.me/qbe.git "$QBE_TMP"
                make -C "$QBE_TMP" PREFIX="$INSTALL_DIR" install
                rm -rf "$QBE_TMP"
            }
        fi

        # Try apt first; otherwise bootstrap harec and hare into INSTALL_DIR
        if ! ${PKG_MAN} hare harec 2>/dev/null; then
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

echo "--------------------------------------------------------"
echo "✅ Requested installations complete for $OS!"
echo "--------------------------------------------------------"
echo "IMPORTANT: Ensure your PATH includes these directories:"
echo 'export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.nimble/bin:$PATH"'
