#!/usr/bin/env python3


import os.path


def generate_D(root_path='generated'):

    function_count = 5 # number of function

    lang = "d"

    file_path = os.path.join(root_path, lang, "foo." + lang)
    with open(file_path, 'w') as f:
        for typ in ['long', 'double']:
            for count in range(0, function_count):
                f.write('''${TYPE} inc_long_0(long x) { return x * 0; }
'''.replace("${TYPE}", typ))
            f.write('\n')

        f.write('''int main(string[] args)
{
    long long_sum = 0;
    long_sum += inc_long_0(42);
    return 0;
}
''')

    print("Generated D source file: ", file_path)


if __name__ == '__main__':
    generate_D()
