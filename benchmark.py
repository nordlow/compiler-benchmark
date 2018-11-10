#!/usr/bin/env python3


import os.path


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

    print("Generated D source file: ", file_path)


if __name__ == '__main__':
    function_count = 100000
    generate_D(function_count=function_count)
