#!/usr/bin/env python3


import subprocess
import os.path
from timeit import default_timer as timer

def do_file(path, args):

    start = timer()
    # subprocess.call(args)
    with subprocess.Popen(args + [path],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as proc:
        results = proc.communicate()
        print(results)
    end = timer()
    print("Checking of {} took {:1.3f} seconds ({})".format(path, end - start, args[0]))


def generate(f_count, language, args, root_path='generated'):

    types = ["int", "long", "float", "double"]

    path = os.path.join(root_path, language, "foo." + language.lower())
    with open(path, 'w') as f:
        for typ in types:
            for n in range(0, f_count):
                f.write('''{{T}} add_{{T}}_{{N}}({{T}} x) { return x * (x + {{N}}); }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
            f.write('\n')

        if language == "c":
            f.write('''int main(int argc, char* argv[])
{
''')
        elif language == "d":
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

    do_file(path, args=args)  # "-betterC"


if __name__ == '__main__':
    f_count = 50000
    C_FLAGS = ['-fsyntax-only']
    C_CLANG_FLAGS = C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option']
    generate(f_count=f_count, language="c", args=['clang-7'] + C_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option'])
    generate(f_count=f_count, language="c", args=['gcc-8'] + C_FLAGS)
    generate(f_count=f_count, language="d", args=['dmd', '-o-'])
