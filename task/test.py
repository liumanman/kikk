import sys
import os

path1 = sys.path[0]
path2 = os.path.normpath(os.path.join(path1, '../'))
path3 = os.path.realpath('../')

print(path3)

def test():
    p = join('/xx/xx/','yyy')
    print(p)

def init():
    from os.path import join

if __name__ == '__main__':
    # from os.path import join
    init()

    test()