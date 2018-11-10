#!/usr/bin/env python3


import subprocess
import os.path
from timeit import default_timer as timer

def check_D_file(path):

    args = ['/usr/bin/dmd', '-o-', path]

    start = timer()
    subprocess.call(args)
    # with subprocess.Popen(args,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.PIPE) as proc:
    #     print(proc.communicate())
    end = timer()
    print("Checking of {} took {:1.3f} seconds".format(path, end - start))


def generate(f_count, language, root_path='generated'):

    types = ["int", "long", "float", "double"]

    path = os.path.join(root_path, language, "foo." + language.lower())
    with open(path, 'w') as f:
        for typ in types:
            for n in range(0, f_count):
                f.write('''{{T}} add_{{T}}_{{N}}({{T}} x) { return x * (x + {{N}}); }
'''.replace("{{T}}", typ).replace("{{N}}", str(n)))
            f.write('\n')

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

    print("Generated {} source file: {}".format(language.upper(), path))

    check_D_file(path)


if __name__ == '__main__':
    generate(f_count=50000, language="d")
