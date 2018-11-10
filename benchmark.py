#!/usr/bin/env python3


import os.path


def generate_D(root_path='generated'):

    function_count = 5 # number of function

    lang = "d"

    file_path = os.path.join(root_path, lang, "foo." + lang)
    with open(file_path, 'w') as f:
        for typ in ['long', 'double']:
            for count in range(0, function_count):
                f.write('''${{TYPE}} add_${{TYPE}}_${{COUNT}}(${{TYPE}} x) { return x * ${{COUNT}}; }
'''.replace("${{TYPE}}", typ).replace("${{COUNT}}", str(count)))
            f.write('\n')

        f.write('''int main(string[] args)
{
''')

        for typ in ['long', 'double']:
            f.write('''    ${{TYPE}} ${{TYPE}}_sum = 0;
'''.replace("${{TYPE}}", typ))

            for count in range(0, function_count):
                f.write('''    ${{TYPE}}_sum += add_${{TYPE}}_0(42);
'''.replace("${{TYPE}}", typ))

        f.write('''}
''')

    print("Generated D source file: ", file_path)


if __name__ == '__main__':
    generate_D()
