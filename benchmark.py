#!/usr/bin/env python3


import os.path


def generate_D(root_path='generated'):

    lang = "d"

    with open(os.path.join(root_path, lang, "foo." + lang), 'w') as f:
        f.write(
'''long f_0(long x)
{
    return x * 0;
}

void main(string[] args)
{
    long sum = 0;
    sum += f_0(42);
}
''')


if __name__ == '__main__':
    generate_D()
