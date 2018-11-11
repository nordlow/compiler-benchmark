#!/usr/bin/env python3


import subprocess
import os.path
from timeit import default_timer as timer
import shutil
from pprint import pprint


def compile_file(path, args, run_count=1):

    compiler = shutil.which(args[0])
    if compiler is None:
        print('Could not find compiler:', args[0])
        return None

    start = timer()
    # subprocess.call(args)
    for _ in range(0, run_count):
        with subprocess.Popen(args + [path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            results = proc.communicate()
            # print(results)
    end = timer()
    span = (end - start) / run_count  # time span
    print("- Checking of {} took {:1.3f} seconds (using \"{}\")".format(path, span, args[0]))
    return span


def generate_top(f_count, language, root_path='generated'):
    lang = language.lower()

    # types by language
    if lang in ["c", "c++", "d"]:
        types = ["int"]
    elif lang == "rust":
        types = ["i32"]
    elif lang == "go":
        types = ["int32"]

    # extensions by language
    if lang == "rust":
        ext = "rs"
    else:
        ext = lang

    dir_path = os.path.join(root_path, lang)
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, "foo." + ext)
    start = timer()
    with open(path, 'w') as f:
        if language == "Go":
            f.write('''package foo;

''')
        for typ in types:
            for n in range(0, f_count):
                if lang in ["c", "c++", "d"]:
                    f.write('''{{T}} add_{{T}}_{{N}}({{T}} x) { return x + {{N}}; }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
                elif lang == "rust":
                    f.write('''fn add_{{T}}_{{N}}(x: {{T}}) -> {{T}} { x + {{N}} }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
                elif lang == "go":
                    f.write('''func add_{{T}}_{{N}}(x {{T}}) {{T}} { return x + {{N}} }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
            f.write('\n')

        # MAIN HEADER
        if lang in ["c", "c++"]:
            f.write('''int main(__attribute__((unused)) int argc, __attribute__((unused)) char* argv[])
{
''')
        elif lang == "d":
            f.write('''int main(string[] args)
{
''')
        elif lang == "rust":
            f.write('''fn main() -> {{T}} {
'''.replace('{{T}}', types[0]))
        elif lang == "go":
            f.write('''func main() {{T}} {
'''.replace('{{T}}', types[0]))
        else:
            assert False

        # CALCULATE
        for typ in types:
            if lang in ["c", "c++", "d"]:
                f.write('''    {{T}} {{T}}_sum = 0;
'''.replace("{{T}}", typ))
            elif lang == "rust":
                f.write('''    let mut {{T}}_sum : {{T}} = 0;
'''.replace("{{T}}", typ))
            elif lang == "go":
                f.write('''    var {{T}}_sum {{T}} = 0;
'''.replace("{{T}}", typ))
            else:
                assert False

            for n in range(0, f_count):
                f.write('''    {{T}}_sum += add_{{T}}_{{N}}({{N}});
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))

        f.write('''    return {{T}}_sum;
}
'''.replace('{{T}}', types[0]))

    end = timer()
    span = (end - start) # time span
    print("Generating {} took {:1.3f} seconds ({})".format(path, span, language))

    # print("Generated {} source file: {}".format(language.upper(), path))

    return path  # "-betterC"


def print_speedup(from_lang, to_lang):
    if (from_lang in spans and to_lang in spans):
        print("- {} to {}: {:.2f}".format(from_lang, to_lang, spans[to_lang] / spans[from_lang]))


if __name__ == '__main__':
    f_count = 5000

    C_FLAGS = ['-fsyntax-only', '-Wall', '-Wextra']
    C_CLANG_FLAGS = C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option']

    CLANG_VERSIONS = [7, 8, 9, 10]
    GCC_VERSIONS = [4, 5, 6, 7, 8, 9, 10]

    languages = ["C", "C++", "D", "Rust", "Go"]

    gpaths = {}                 # generated paths
    spans = {}                  # time spans
    compilers = {}                  # compilers

    print("Code-generation:")
    for language in languages:
        gpaths[language] = generate_top(f_count=f_count, language=language)
    print()

    # Clang
    print("Clang:")
    for clang_version in CLANG_VERSIONS:
        language = "C"
        clang_ = shutil.which('clang-' + str(clang_version))
        if clang_ is not None:
            spans["Clang"] = compile_file(path=gpaths["C"], args=[clang_] + C_CLANG_FLAGS)
            spans[clang_] = spans["Clang"]

        language = "C++"
        clangxx_ = shutil.which('clang++-' + str(clang_version))
        if clangxx_ is not None:
            spans["Clang++"] = compile_file(path=gpaths["C++"], args=[clangxx_] + C_CLANG_FLAGS)
    print()

    # C GCC
    print("GCC:")
    for gcc_version in GCC_VERSIONS:
        language = "C"
        gcc_ = shutil.which('gcc-' + str(gcc_version))
        if gcc_ is not None:
            spans[gcc_] = compile_file(path=gpaths["C"], args=[gcc_] + C_FLAGS)
            spans["gcc-" + str(gcc_version)] = spans[gcc_]

        language = "C++"
        gxx_ = shutil.which('g++-' + str(gcc_version))
        if gxx_ is not None:
            spans[gxx_] = compile_file(path=gpaths["C++"], args=[gxx_] + C_FLAGS)
            spans["g++-" + str(gcc_version)] = spans[gxx_]
    print()

    # D
    language = "D"
    print(language + ":")
    # DMD
    dmd_ = shutil.which('dmd')
    if dmd_ is not None:
        if language not in compilers: compilers[language] = dmd_
        spans[language] = compile_file(path=gpaths["D"], args=[dmd_, '-o-'])
    # LDC
    ldc_ = shutil.which('ldmd2')
    if ldc_ is not None:
        if language not in compilers: compilers[language] = ldc_
        spans[language] = compile_file(path=gpaths["D"], args=[ldc_, '-o-'])
    print()

    # Go
    language = "Go"
    print(language + ":")
    gccgo_ = shutil.which('gccgo')
    if gccgo_ is not None:
        if language not in compilers: compilers[language] = gccgo_
        spans[language] = compile_file(path=gpaths[language], args=[gccgo_, '-fsyntax-only', '-c'])
        print()

    # Rust
    if False:
        language = "Rust"
        print(language + ":")
        rustc_ = shutil.which('rustc')
        if rustc_ is not None:
            if language not in compilers: compilers[language] = rustc_
            # See: https://stackoverflow.com/questions/53250631/does-rust-have-a-way-to-perform-syntax-and-semantic-analysis-without-generating/53250674#53250674
            # TODO try `rustc --emit=metadata -Z no-codegen`
            # TODO try `cargo check`
            spans[language] = compile_file(path=gpaths["Rust"], args=[rustc_, '--crate-type', 'lib', '--emit=mir', '-o', '/dev/null', '--test'])
            print()

    print("Speedups" + ":")

    # pprint(spans)

    print_speedup(from_lang="D", to_lang="gcc-8")
    print_speedup(from_lang="D", to_lang="g++-8")
    print_speedup(from_lang="D", to_lang="Clang")
    print_speedup(from_lang="D", to_lang="Clang++")
    print_speedup(from_lang="D", to_lang="Go")
    print_speedup(from_lang="D", to_lang="Rust")
