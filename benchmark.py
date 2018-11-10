#!/usr/bin/env python3


import os.path


def regenerate_sources(root_path='generated'):
    lang = "d"
    with open(os.path.join(root_path, lang, "foo." + lang), 'w') as f:
        f.write(
'''long foo0(long x)
{
    return x * 0;
}

void main(string[] args)
{
    long sum = 0;
    sum += foo0(42);
}
''')


if __name__ == '__main__':
    regenerate_sources()
