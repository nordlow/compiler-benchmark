#!/usr/bin/env python3


import subprocess
import os.path
from timeit import default_timer as timer


def compile_file(path, args):

    start = timer()
    # subprocess.call(args)
    count = 5                   # number run counts
    for _ in range(1, count):
        with subprocess.Popen(args + [path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            results = proc.communicate()
            # print(results)
    end = timer()
    span = (end - start) / count  # time span
    print("Checking of {} took {:1.3f} seconds ({})".format(path, span, args[0]))
    return span


def generate_top(f_count, language, root_path='generated'):
    lang = language.lower()

    # types by language
    if lang in ["c", "c++", "d"]:
        types = ["int"]
    elif lang == "rust":
        types = ["i32"]

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
        for typ in types:
            for n in range(0, f_count):
                if lang in ["c", "c++", "d"]:
                    f.write('''{{T}} add_{{T}}_{{N}}({{T}} x) { return x + {{N}}; }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
                elif lang == "rust":
                    f.write('''fn add_{{T}}_{{N}}(x: {{T}}) -> {{T}} { x + {{N}} }
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
            f.write('''fn main() -> i32 {
''')
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
    print("Generating {} took {:1.3f} seconds".format(path, span))

    # print("Generated {} source file: {}".format(language.upper(), path))

    return path  # "-betterC"


if __name__ == '__main__':
    f_count = 5000

    C_FLAGS = ['-fsyntax-only', '-Wall', '-Wextra']
    C_CLANG_FLAGS = C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option']

    # TODO don't regenerate sources

    # C
    path_C = generate_top(f_count=f_count, language="C")
    span_C_Clang_7 = compile_file(path=path_C, args=['clang-7'] + C_CLANG_FLAGS)
    span_C_GCC_8 = compile_file(path=path_C, args=['gcc-8'] + C_FLAGS)
    span_C_GCC_7 = compile_file(path=path_C, args=['gcc-7'] + C_FLAGS)
    span_C_GCC_6 = compile_file(path=path_C, args=['gcc-6'] + C_FLAGS)
    span_C_GCC_5 = compile_file(path=path_C, args=['gcc-5'] + C_FLAGS)

    # # C++
    # span_Cxx_GCC_5 = generate_top(f_count=f_count, language="C++", args=['g++-8'] + C_FLAGS)
    # span_Cxx_Clang_7 = generate_top(f_count=f_count, language="C++", args=['clang++-7'] + C_CLANG_FLAGS)

    # # D
    # span_D_DMD = generate_top(f_count=f_count, language="D", args=['dmd', '-o-'])
    # span_D_LDC = generate_top(f_count=f_count, language="D", args=['ldmd2', '-o-'])

    # # Rust
    # span_Rust = generate_top(f_count=f_count, language="Rust", args=['rustc', '--crate-type', 'lib', '--emit=mir', '-o', '/dev/null', '--test'])

    # print("D/C speedup:", span_C_GCC_8 / span_D_LDC)
    # print("D/C++ speedup:", span_Cxx_GCC_5 / span_D_LDC)
    # print("D/Rust speedup:", span_Rust / span_D_LDC)
