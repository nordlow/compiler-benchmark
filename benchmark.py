#!/usr/bin/env python3


import subprocess
import os.path
from timeit import default_timer as timer

def do_file(path, args):

    start = timer()
    # subprocess.call(args)
    count = 5                   # number run counts
    for _ in range(1, count):
        with subprocess.Popen(args + [path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            results = proc.communicate()
            print(results)
    end = timer()
    span = (end - start) / count  # time span
    print("Checking of {} took {:1.3f} seconds ({})".format(path, span, args[0]))
    return span


def generate(f_count, language, args, root_path='generated'):
    lang = language.lower()

    if lang in ["c", "c++", "d"]:
        types = ["int", "long", "float", "double"]
    elif lang == "rust":
        types = ["i32", "i64", "f32", "f64"]

    if lang == "rust":
        ext = "rs"
    else:
        ext = lang
    path = os.path.join(root_path, lang, "foo." + ext)
    with open(path, 'w') as f:
        for typ in types:
            for n in range(0, f_count):
                if lang in ["c", "c++", "d"]:
                    f.write('''{{T}} add_{{T}}_{{N}}({{T}} x) { return x * (x + {{N}}); }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
                elif lang == "rust":
                    f.write('''{{T}} add_{{T}}_{{N}}({{T}} x) { return x * (x + {{N}}); }
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
            f.write('''fn main() {
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

        f.write('''    return int_sum;
}
''')

    # print("Generated {} source file: {}".format(language.upper(), path))

    return do_file(path, args=args)  # "-betterC"


if __name__ == '__main__':
    f_count = 5000

    span_Rust = generate(f_count=f_count, language="Rust", args=['rustc', '--crate-type', 'lib', '--emit=mir', '-o', '/dev/null', '--test'])

    C_FLAGS = ['-fsyntax-only', '-Wall', '-Wextra']
    C_CLANG_FLAGS = C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option']

    span_C_Clang_7 = generate(f_count=f_count, language="C", args=['clang-7'] + C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option'])
    span_C_GCC_8 = generate(f_count=f_count, language="C", args=['gcc-8'] + C_FLAGS)
    span_C_GCC_7 = generate(f_count=f_count, language="C", args=['gcc-7'] + C_FLAGS)
    span_C_GCC_6 = generate(f_count=f_count, language="C", args=['gcc-6'] + C_FLAGS)
    span_C_GCC_5 = generate(f_count=f_count, language="C", args=['gcc-5'] + C_FLAGS)

    span_D_DMD = generate(f_count=f_count, language="D", args=['dmd', '-o-'])
    span_D_LDC = generate(f_count=f_count, language="D", args=['ldmd2', '-o-'])

    print("D/C speedup:", span_C_GCC_8 / span_D_LDC)
    print("D/Rust speedup:", span_C_GCC_8 / span_Rust)
