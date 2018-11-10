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
            # print(results)
    end = timer()
    span = (end - start) / count
    print("Checking of {} took {:1.3f} seconds ({})".format(path, span, args[0]))
    return span


def generate(f_count, language, args, root_path='generated'):

    types = ["int", "long", "float", "double"]

    path = os.path.join(root_path, language.lower(), "foo." + language.lower())
    with open(path, 'w') as f:
        for typ in types:
            for n in range(0, f_count):
                f.write('''{{T}} add_{{T}}_{{N}}({{T}} x) { return x * (x + {{N}}); }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
            f.write('\n')

        if language.upper() == "C":
            f.write('''int main(int argc, char* argv[])
{
''')
        elif language.upper() == "D":
            f.write('''int main(string[] args)
{
''')

        for typ in types:
            f.write('''    {{T}} {{T}}_sum = 0;
'''.replace("{{T}}", typ))

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

    C_FLAGS = ['-fsyntax-only']
    C_CLANG_FLAGS = C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option']

    span_C_Clang_7 = generate(f_count=f_count, language="C", args=['clang-7'] + C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option'])
    span_C_GCC_8 = generate(f_count=f_count, language="C", args=['gcc-8'] + C_FLAGS)
    span_C_GCC_7 = generate(f_count=f_count, language="C", args=['gcc-7'] + C_FLAGS)
    span_C_GCC_6 = generate(f_count=f_count, language="C", args=['gcc-6'] + C_FLAGS)
    span_C_GCC_5 = generate(f_count=f_count, language="C", args=['gcc-5'] + C_FLAGS)

    span_D_DMD = generate(f_count=f_count, language="D", args=['dmd', '-o-'])
    span_D_LDC = generate(f_count=f_count, language="D", args=['ldmd2', '-o-'])

    print("D/C speed:", span_C_GCC_8 / span_D_LDC)
