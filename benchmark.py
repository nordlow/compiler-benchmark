#!/usr/bin/env python3


import os.path
import timeit


def check_D_file(file_path):
    start = timeit.timeit()
    end = timeit.timeit()
    print("Check took of {} took {}".format(file_path, end - start))


def generate_D(function_count, root_path='generated'):

    LANG = "d"

    types = ["int", "double"]

    file_path = os.path.join(root_path, LANG, "foo." + LANG)
    with open(file_path, 'w') as f:
        for typ in types:
            for count in range(0, function_count):
                f.write('''${{TYPE}} add_${{TYPE}}_${{COUNT}}(${{TYPE}} x) { return x * (x + ${{COUNT}}); }
'''.replace("${{TYPE}}", typ).replace("${{COUNT}}", str(count)))
            f.write('\n')

        f.write('''int main(string[] args)
{
''')

        for typ in types:
            f.write('''    ${{TYPE}} ${{TYPE}}_sum = 0;
'''.replace("${{TYPE}}", typ))

            for count in range(0, function_count):
                f.write('''    ${{TYPE}}_sum += add_${{TYPE}}_${{COUNT}}(${{COUNT}});
'''.replace("${{TYPE}}", typ).replace("${{COUNT}}", str(count)))

        f.write('''    return int_sum;
}
''')

    print("Generated {} source file: {}".format(LANG.upper(), file_path))

    check_D_file(file_path)


if __name__ == '__main__':
    function_count = 10
    generate_D(function_count=function_count)
