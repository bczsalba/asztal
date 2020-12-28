#!/usr/bin/env python3
# https://stackoverflow.com/a/27165165

import sys,os

lines = []
c = 0
linelen = min(os.get_terminal_size()[0]//5,16)
if len(sys.argv) == 1:
    for n in range(256//linelen):
        line = []
        for i in range(linelen):
            c += 1
            pad = (3-len(str(c)))*' '
            line.append(f'\033[38;5;{c}m {pad}{c}')
        lines.append(' '.join(line))
    
    for l in lines:
        print(l)
else:
    if sys.argv[1] == '-i':
        while True:
            colors = input('\n')
            line = []
            blockline = []
            for n in colors.split(' '):
                pad = (4-len(str(n)))*' '

                line.append(f'\033[38;5;{n}m'+str(n)+pad)
                blockline.append(f'\033[38;5;{n}m'+'█'*(4))

            print('\033[1A\033[K'+''.join(line)+'\033[0m')
            print('\033[K'+''.join(blockline)+'\033[0m')
